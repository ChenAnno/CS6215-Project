#!/usr/bin/env python3
"""Memorisation probe: consistently rename the package-defined functions and classes of the
micro-benchmark cases, rewrite the ground truth accordingly, and keep only the cases whose
renamed ground truth the benchmark's own dynamic validator still accepts.

    .venv/bin/python -I eval/perturb.py            # writes results/perturbed/micro/<cat>/<case>/
    .venv/bin/python -I eval/perturb.py --validate # + runs PyCG's micro-benchmark/validate.py on them

A name is renamed (to `q<hash>_<n>`) only when it is safe to do so syntactically: it is the
name of a `def` or `class` of the case, not a dunder, not a builtin, not the name of a module of
the case, not a component of any outside callee in the ground truth (an override such as `run`
of `threading.Thread` keeps its name), and it occurs in no string literal (no `getattr(x, "f")`).
Every NAME token equal to a renamed name is replaced (identifiers, attributes, keywords).
"""

import argparse
import builtins
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tokenize
import ast
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
sys.path.insert(0, str(HERE))
import subjects  # noqa: E402

OUT = PROJECT / "results" / "perturbed" / "micro"
VALIDATE = subjects.EVAL_REPO / "PyCG" / "micro-benchmark" / "validate.py"


def defined_names(trees):
    names = set()
    for t in trees:
        for n in ast.walk(t):
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                names.add(n.name)
    return names


def string_text(trees):
    out = []
    for t in trees:
        for n in ast.walk(t):
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                out.append(n.value)
    return "\n".join(out)


def rename_source(src, mapping):
    toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    out = []
    for t in toks:
        if t.type == tokenize.NAME and t.string in mapping:
            t = t._replace(string=mapping[t.string])
        out.append(t)
    return tokenize.untokenize(out)


def rename_dotted(name, mapping, modules):
    parts = name.split(".")
    if parts[0] not in modules:
        return name
    return ".".join(mapping.get(p, p) for p in parts)


def perturb_case(case_dir, dst):
    files = sorted(case_dir.rglob("*.py"))
    trees = [ast.parse(f.read_text()) for f in files]
    modules = {f.relative_to(case_dir).parts[0].removesuffix(".py") for f in files}
    truth = json.loads((case_dir / "callgraph.json").read_text())
    outside_parts = {p for k, vs in truth.items() for n in [k, *vs] if n.split(".")[0] not in modules
                     for p in n.split(".")}
    strings = string_text(trees)
    safe = sorted(n for n in defined_names(trees)
                  if not (n.startswith("__") and n.endswith("__")) and n not in dir(builtins)
                  and n not in modules and n not in outside_parts and n not in strings and n != "main")
    salt = hashlib.sha256(str(case_dir.relative_to(subjects.SNIPPETS)).encode()).hexdigest()[:4]
    mapping = {n: f"q{salt}_{i}" for i, n in enumerate(safe)}
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(case_dir, dst)
    for f in files:
        rel = f.relative_to(case_dir)
        (dst / rel).write_text(rename_source(f.read_text(), mapping))
    new_truth = {rename_dotted(k, mapping, modules): sorted(rename_dotted(v, mapping, modules) for v in vs)
                 for k, vs in truth.items()}
    (dst / "callgraph.json").write_text(json.dumps(new_truth, indent=4))
    (dst / "renaming.json").write_text(json.dumps(mapping, indent=1))
    return mapping


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    a = ap.parse_args(argv)
    keys = sorted(subjects.micro_cases())
    renamed = {}
    for k in keys:
        mapping = perturb_case(subjects.SNIPPETS / k, OUT / k)
        renamed[k] = len(mapping)
    stats = {"cases": len(keys), "cases_with_renaming": sum(1 for v in renamed.values() if v),
             "renamed_names": sum(renamed.values())}
    print(stats)
    if a.validate:
        cases = [str(OUT / k) for k in keys if renamed[k]]
        p = subprocess.run([sys.executable, "-I", str(VALIDATE), *cases], capture_output=True, text=True)
        failed = sorted({line.split(":")[0] for line in p.stdout.splitlines() if line.endswith(": FAIL")})
        failed = [str(Path(f).relative_to(OUT)) if f.startswith(str(OUT)) else f for f in failed]
        stats["validator_failed"] = failed
        stats["validator_tail"] = p.stdout.splitlines()[-1:] if p.stdout else p.stderr[-300:]
        # The cohort of the probe: renamed and still valid.
        stats["cohort"] = sorted(k for k in keys if renamed[k] and k not in failed)
        print(len(failed), "failed validation;", len(stats["cohort"]), "cases in the probe cohort")
        print(stats["validator_tail"])
    (OUT.parent / "micro-perturbation.json").write_text(json.dumps(stats, indent=1))


if __name__ == "__main__":
    main()
