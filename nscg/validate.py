"""Symbolic validation of the LLM's answers (the last stage of NSCG).

For every site the model's callee names are checked against the definition index:
* a package name that is a node is kept;
* a package class name is replaced by what instantiating it runs (MRO rule);
* `pkg.C.m` for a method that `C` inherits is mapped through the MRO to the defining class;
* a package-looking name that names nothing is repaired when exactly one node has the same
  last two components (e.g. a wrong module path), otherwise it is rejected (hallucination);
* an outside name whose head is a local import alias is expanded (`np.x` -> `numpy.x`);
* implicit sites keep only package callees;
* optionally (the "symbolic floor"), certain symbolic resolutions are always kept.
Every decision is counted, so the report can quantify what validation changes.
"""

from __future__ import annotations

import builtins
from collections import Counter

BUILTINS = frozenset(dir(builtins))

EXPLICIT = ("call", "decorator", "raise", "class")


def clean(name):
    return name.strip().strip("`'\" ").replace("()", "")


class Validator:
    def __init__(self, program, floor=True, repair=True, v21=False):
        self.p = program
        self.floor = floor
        self.repair = repair
        self.v21 = v21
        self.stats = Counter()
        self.suffix_index = {}
        for q in program.funcs:
            parts = q.split(".")
            self.suffix_index.setdefault(".".join(parts[-2:]), []).append(q)
        self.rejected = []

    def _imported_tops(self, ms):
        tops = set()
        for bs in ms.bindings.values():
            for b in bs:
                if b[0] == "module":
                    tops.add(b[1].split(".")[0])
                elif b[0] == "from":
                    tops.add(b[1].split(".")[0])
        return tops

    def _alias(self, name, module):
        head, _, rest = name.partition(".")
        if self.v21 and head == "builtins" and rest.split(".")[0] in BUILTINS:
            self.stats["builtins->builtin"] += 1
            return "<builtin>." + rest
        ms = self.p.module_scopes.get(module)
        if ms is None or head not in ms.bindings:
            return name
        if self.v21 and head in self._imported_tops(ms):
            return name  # `invoke.X` with `from invoke import __version__ as invoke`: a module path
        for b in ms.bindings[head]:
            if self.v21 and b[0] == "from":
                target = f"{b[1]}.{b[2]}"
                if name == target or name.startswith(target + "."):
                    return name  # already the full path (`time.time` for `from time import time`)
            if b[0] == "module" and b[1] != head:
                return b[1] + ("." + rest if rest else "")
            if b[0] == "from" and not self.p.in_package(b[1]):
                return f"{b[1]}.{b[2]}" + ("." + rest if rest else "")
        return name

    def internal(self, name):
        """Map a package name to node names ([] if it names nothing)."""
        p = self.p
        if name in p.funcs and p.funcs[name].kind != "module":
            return [name]
        if name in p.classes:
            self.stats["class->constructor"] += 1
            return [t for t in p.constructor_targets(name) if t in p.funcs] or []
        owner, _, attr = name.rpartition(".")
        if owner in p.classes and attr:
            vals = p.lookup_attr(owner, attr)
            fs = [v[1] for v in vals if v[0] == "func"]
            if fs:
                self.stats["inherited->definer"] += 1
                return fs
            if attr == "__init__":
                self.stats["init->constructor"] += 1
                return [t for t in p.constructor_targets(owner) if t in p.funcs]
        if self.repair:
            parts = name.split(".")
            hits = self.suffix_index.get(".".join(parts[-2:]), [])
            if len(hits) == 1:
                self.stats["repaired-path"] += 1
                return hits
        return []

    def site(self, site, answer):
        out = []
        for raw in answer or []:
            name = clean(raw)
            if not name:
                continue
            name = self._alias(name, site.module)
            if self.p.in_package(name) or name in self.p.funcs:
                mapped = self.internal(name)
                if not mapped:
                    self.stats["rejected-unknown-internal"] += 1
                    self.rejected.append((site.sid, site.caller, name))
                    continue
                self.stats["kept-internal"] += 1
                out += mapped
            else:
                if site.kind not in EXPLICIT:
                    self.stats["rejected-external-at-implicit"] += 1
                    continue
                if name.startswith("<builtin>.") and name.count(".") == 1 and name[10:] in ("object",):
                    continue
                self.stats["kept-external"] += 1
                out.append(name)
        if self.floor and site.certain:
            for r in site.resolved:
                if r not in out:
                    self.stats["floor-added"] += 1
                    out.append(r)
        return list(dict.fromkeys(out))


def raw_site(site, answer):
    """No validation at all: the model's names as written."""
    return [clean(a) for a in (answer or []) if clean(a)]
