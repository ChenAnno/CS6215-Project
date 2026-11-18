#!/usr/bin/env python3
"""Run NSCG (or one of its variants) on the micro- and/or macro-benchmark subjects.

    .venv/bin/python -m nscg.run --variant nscg --benchmark micro macro [--model haiku] [--jobs 12]

Variants (see README.md, "Variants"):
  sym        symbolic front-end only (no LLM): the pre-resolved callees of every site
  llm-only   V0: the LLM reads the source and writes the call graph (no symbolic help)
  nohints    V1: symbolic call sites, no per-site symbolic information
  nscg       V2: symbolic sites + pre-resolution + name candidates + callbacks + attribute facts,
             then symbolic validation (the full design)
  hybrid     V3: V2 plus the PyCG-2026 callees of each caller as evidence

Writes results/tools/<tool>/{micro/<cat>/<case>.json, macro/<project>.json} (scored by
eval/score_all.py), results/raw/<tool>/... (the LLM's answers per site, for offline
ablations), and results/runs/<tool>-<benchmark>.json (time, tokens, cost, failures).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from . import llm, prompts
from .frontend import load_macro_project, load_micro_case
from .validate import Validator, raw_site

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT / "eval"))
import subjects  # noqa: E402

RESULTS = PROJECT / "results"
MAX_SITES_PER_UNIT = 45
MAX_FULL_MODULE_LINES = 700


def load_projects_module():
    path = subjects.MACRO / "projects.py"
    spec = importlib.util.spec_from_file_location("macro_projects", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def tool_name(variant, model):
    base = {"sym": "nscg-sym", "llm-only": "llm-only", "nohints": "nscg-nohints", "nscg": "nscg",
            "hybrid": "nscg-hybrid", "nscg21": "nscg-v21", "hybrid21": "nscg-hybrid-v21"}[variant]
    name = base if model == "haiku" or variant == "sym" else f"{base}@{model}"
    name += f"-r{os.environ['NSCG_REPEAT']}" if os.environ.get("NSCG_REPEAT") else ""
    return name + ("+renamed" if subjects.RENAMED else "")


# ----------------------------------------------------------------------------- units
class Unit:
    """One LLM request: a micro case, or a chunk of the sites of one module of a package."""

    def __init__(self, key, program, sites, desc, sources, callers, outline, facts, pycg_hints=None):
        self.key, self.program, self.sites, self.desc = key, program, sites, desc
        self.sources, self.callers, self.outline, self.facts = sources, callers, outline, facts
        self.pycg_hints = pycg_hints


V21 = ("nscg21", "hybrid21")


def micro_units(case_key, variant="nscg"):
    d = subjects.SNIPPETS / case_key
    p = load_micro_case(d, library_hooks=variant in V21)
    srcs = []
    for mod in sorted(p.modules):
        rel = p.modules[mod]["path"].relative_to(d)
        srcs.append(f"### file {rel} (module `{mod}`)\n" + p.numbered_source(mod))
    callers = p.nodes()
    attrs = sorted({s.text.split("(")[0].rsplit(".", 1)[-1] for s in p.sites if s.kind == "call" and "." in s.text.split("(")[0]})
    return p, [Unit(case_key, p, p.sites, f"a small program; `main.py` is run as the script `main`",
                    "\n\n".join(srcs), callers, None, p.attr_fact_text(attrs))]


def macro_units(project, pycg_graph=None, variant="nscg"):
    p = load_macro_project(project, library_hooks=variant in V21)
    outline = p.outline(max_lines=450)
    units = []
    for mod in sorted(p.modules):
        msites = [s for s in p.sites if s.module == mod]
        mcallers = [q for q, f in sorted(p.funcs.items()) if f.module == mod]
        nlines = len(p.modules[mod]["lines"])
        chunks = [msites[i:i + MAX_SITES_PER_UNIT] for i in range(0, len(msites), MAX_SITES_PER_UNIT)] or [[]]
        for ci, chunk in enumerate(chunks):
            callers = sorted({s.caller for s in chunk}) if len(chunks) > 1 else mcallers
            if nlines <= MAX_FULL_MODULE_LINES or not chunk:
                src = p.numbered_source(mod)
            else:
                lo = min(p.funcs[c].lineno for c in callers if c in p.funcs)
                hi = max(p.funcs[c].end_lineno for c in callers if c in p.funcs)
                lo = min(lo, min(s.line for s in chunk))
                hi = max(hi, max(s.line for s in chunk))
                if hi - lo > MAX_FULL_MODULE_LINES:  # module-level code: window around the sites
                    lo, hi = min(s.line for s in chunk) - 40, max(s.line for s in chunk) + 40
                header = p.numbered_source(mod, 1, min(40, lo - 1)) if lo > 1 else ""
                src = (header + "\n   ...\n" if header else "") + p.numbered_source(mod, lo, hi)
            attrs = sorted({s.text.split("(")[0].rsplit(".", 1)[-1] for s in chunk
                            if s.kind == "call" and "." in s.text.split("(")[0]})
            hints = None
            if pycg_graph is not None:
                hints = "\n".join(f"{c}: [{', '.join(sorted(pycg_graph.get(c, [])))}]" for c in sorted({s.caller for s in chunk}))
            units.append(Unit(f"{project.name}/{mod}#{ci}", p, chunk,
                              f"module `{mod}` of package `{project.name}`" + (f", part {ci + 1}/{len(chunks)}" if len(chunks) > 1 else ""),
                              src, callers, outline, p.attr_fact_text(attrs), hints))
    return p, units


# ----------------------------------------------------------------------------- solving
def solve_unit(unit, variant, model):
    """Returns (answers {sid: [names]} or {caller: [names]} for llm-only, record or None, error)."""
    if variant == "sym":
        return {s.sid: list(s.resolved) for s in unit.sites}, None, None
    if variant == "llm-only":
        prompt = prompts.llm_only_prompt(unit.desc, unit.sources, unit.callers, unit.outline)
        out, rec = llm.ask(prompt, prompts.EDGE_SCHEMA, prompts.SYSTEM, model=model)
        ans = {}
        for e in out.get("edges", []):
            ans.setdefault(str(e.get("caller", "")).strip(), []).extend(e.get("callees") or [])
        return ans, rec, None
    if not unit.sites:
        return {}, None, None
    hints = variant != "nohints"
    prompt = prompts.site_prompt(unit.desc, unit.sources, unit.sites, unit.outline, unit.facts, hints=hints,
                                 pycg_hints=unit.pycg_hints if variant in ("hybrid", "hybrid21") else None)
    out, rec = llm.ask(prompt, prompts.SITE_SCHEMA, prompts.SYSTEM, model=model)
    ans = {}
    for e in out.get("sites", []):
        ans[str(e.get("id", "")).strip()] = e.get("callees") or []
    return ans, rec, None


def build_graph(program, units_answers, variant, validate=True, floor=True):
    """Graph {node: sorted callees} from the per-unit answers."""
    graph = {n: set() for n in program.nodes()}
    v = Validator(program, floor=floor, v21=variant in V21)
    missing = 0
    for unit, ans in units_answers:
        if variant == "llm-only":
            for caller, callees in ans.items():
                graph.setdefault(caller, set()).update(c.strip() for c in callees if c.strip())
            continue
        for s in unit.sites:
            if s.sid not in ans:
                missing += 1
                a = list(s.resolved)  # fallback: the symbolic resolution
            else:
                a = ans[s.sid]
            callees = v.site(s, a) if validate else raw_site(s, a)
            graph.setdefault(s.caller, set()).update(callees)
    return {k: sorted(x) for k, x in graph.items()}, v.stats, missing, v.rejected


def run(variant, benchmarks, model, jobs, limit=None, only=None, validate=True, floor=True):
    tool = tool_name(variant, model) + ("" if validate else "-novalidate") + ("" if floor or not validate else "-nofloor")
    tdir = RESULTS / "tools" / tool
    rdir = RESULTS / "raw" / tool
    for benchmark in benchmarks:
        t0 = time.time()
        before = dict(llm.STATS)
        programs = {}
        units = []
        if benchmark == "micro":
            keys = sorted(subjects.micro_cases())
            if only:
                keys = [k for k in keys if any(k.startswith(o) for o in only)]
            keys = keys[:limit] if limit else keys
            for k in keys:
                p, us = micro_units(k, variant)
                programs[k] = p
                units += [(k, u) for u in us]
        else:
            projs = load_projects_module().load_projects()
            names = [n for n in subjects.MACRO_PROJECTS if not only or n in only]
            for name in names:
                pycg = None
                if variant in ("hybrid", "hybrid21"):
                    pycg = json.loads((RESULTS / "tools" / "pycg-2026" / "macro" / f"{name}.json").read_text())
                p, us = macro_units(projs[name], pycg, variant)
                programs[name] = p
                units += [(name, u) for u in us]
        print(f"[{tool}/{benchmark}] {len(programs)} programs, {len(units)} units, "
              f"{sum(len(u.sites) for _, u in units)} sites", flush=True)
        answers = {k: [] for k in programs}
        errors = []
        records = {}

        def work(item):
            key, unit = item
            try:
                ans, rec, _ = solve_unit(unit, variant, model)
                return key, unit, ans, rec, None
            except Exception as e:  # noqa: BLE001 - recorded, the unit falls back to symbolic
                return key, unit, {}, None, f"{type(e).__name__}: {e}"

        done = 0
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            futs = [ex.submit(work, it) for it in units]
            for f in as_completed(futs):
                key, unit, ans, rec, err = f.result()
                answers[key].append((unit, ans))
                if err:
                    errors.append({"unit": unit.key, "error": err})
                if rec:
                    records[unit.key] = {"cache_key": rec["key"], "cost_usd": rec.get("cost_usd"),
                                         "seconds": rec.get("seconds"), "usage": rec.get("usage")}
                done += 1
                if done % 25 == 0 or done == len(units):
                    print(f"  {done}/{len(units)} units, cost so far ${llm.STATS['cost_usd'] - before['cost_usd']:.3f}, "
                          f"errors {len(errors)}", flush=True)
        stats_total = {}
        for key, p in programs.items():
            ua = sorted(answers[key], key=lambda x: x[0].key)
            graph, vstats, missing, rejected = build_graph(p, ua, variant, validate=validate, floor=floor)
            out = tdir / benchmark / (f"{key}.json")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(graph, indent=1))
            raw = {"units": [{"unit": u.key, "answers": a,
                              "sites": [{"id": s.sid, "caller": s.caller, "line": s.line, "col": s.col, "kind": s.kind,
                                         "text": s.text, "resolved": s.resolved, "candidates": s.candidates,
                                         "callbacks": s.callbacks, "certain": s.certain,
                                         "hooks": s.hooks} for s in u.sites]}
                             for u, a in ua],
                   "validation": dict(vstats), "missing_answers": missing, "rejected": rejected}
            rp = rdir / benchmark / f"{key}.json"
            rp.parent.mkdir(parents=True, exist_ok=True)
            rp.write_text(json.dumps(raw))
            for k2, v2 in vstats.items():
                stats_total[k2] = stats_total.get(k2, 0) + v2
            stats_total["missing_answers"] = stats_total.get("missing_answers", 0) + missing
        delta = {k: (llm.STATS[k] - before[k]) for k in llm.STATS}
        run_rec = {"tool": tool, "variant": variant, "model": model, "benchmark": benchmark,
                   "programs": len(programs), "units": len(units), "sites": sum(len(u.sites) for _, u in units),
                   "wall_seconds": round(time.time() - t0, 1), "llm": delta, "validation": stats_total,
                   "errors": errors, "per_unit": records}
        rr = RESULTS / "runs" / f"{tool}-{benchmark}.json"
        rr.parent.mkdir(parents=True, exist_ok=True)
        rr.write_text(json.dumps(run_rec, indent=1))
        print(f"[{tool}/{benchmark}] done in {run_rec['wall_seconds']} s; requests {delta['requests']}, cache hits "
              f"{delta['cache_hits']}, cost ${delta['cost_usd']:.3f}, errors {len(errors)}; validation {stats_total}",
              flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", required=True,
                    choices=["sym", "llm-only", "nohints", "nscg", "hybrid", "nscg21", "hybrid21"])
    ap.add_argument("--benchmark", nargs="+", default=["micro", "macro"], choices=["micro", "macro"])
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--jobs", type=int, default=12)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--no-validate", action="store_true", help="ablation: the LLM's names as written")
    ap.add_argument("--no-floor", action="store_true", help="ablation: validation without the symbolic floor")
    a = ap.parse_args(argv)
    run(a.variant, a.benchmark, a.model, a.jobs, a.limit, a.only, validate=not a.no_validate, floor=not a.no_floor)


if __name__ == "__main__":
    main()
