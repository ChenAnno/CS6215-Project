#!/usr/bin/env python3
"""Error taxonomy of a site-based NSCG variant against the ground truth, and overlap with a baseline.

    .venv/bin/python -I eval/errors.py nscg [--baseline pycg-2026] [--benchmark macro|micro]

Reads results/scores/<tool>.json (FP/FN lists from the official scorer, macro) or recomputes
edge sets (micro), and results/raw/<tool>/... (what the front-end proposed at each site and
what the LLM answered). Every false negative / false positive edge gets one label:

FN, callee inside the package
  fn-no-evidence     no site of the caller proposed the callee (front-end gave no hint)
  fn-rejected        a site proposed it (resolution / name candidate / callback) but the LLM dropped it
FN, callee outside
  fn-ext-misnamed    the tool has an outside callee of the same caller with the same last name part
  fn-ext-omitted     otherwise
FP, callee inside
  fp-accepted-hint   the callee was proposed at a site of the caller and the LLM kept it wrongly
  fp-llm-added       the LLM added a package callee that the front-end did not propose
FP, callee outside
  fp-ext-misnamed    the truth has an outside callee of that caller with the same last name part
  fp-ext-spurious    otherwise
Writes results/errors/<tool>-<benchmark>.json and prints a summary.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
sys.path.insert(0, str(HERE))
import subjects  # noqa: E402

RES = PROJECT / "results"


def last(name):
    return name.rsplit(".", 1)[-1]


def label(tool, bench, key, fps, fns, packages, raw):
    proposed = {}
    for u in raw["units"]:
        for s in u["sites"]:
            proposed.setdefault(s["caller"], set()).update(s["resolved"] + s["candidates"] + s["callbacks"]
                                                           + s.get("hooks", []))
    mine = json.loads((RES / "tools" / tool / bench / f"{key}.json").read_text())
    truth_path = (subjects.SNIPPETS / key / "callgraph.json") if bench == "micro" else (
        subjects.MACRO / "ground-truth" / f"{key}.json")
    truth = json.loads(truth_path.read_text())

    def inside(n):
        return any(n == p or n.startswith(p + ".") for p in packages)

    out = []
    for a, b in fns:
        if inside(b):
            lab = "fn-rejected" if b in proposed.get(a, ()) else "fn-no-evidence"
        else:
            lab = "fn-ext-misnamed" if any(last(c) == last(b) and not inside(c) for c in mine.get(a, [])) else "fn-ext-omitted"
        out.append({"edge": [a, b], "label": lab, "program": key})
    for a, b in fps:
        if inside(b):
            lab = "fp-accepted-hint" if b in proposed.get(a, ()) else "fp-llm-added"
        else:
            lab = "fp-ext-misnamed" if any(last(c) == last(b) and not inside(c) for c in truth.get(a, [])) else "fp-ext-spurious"
        out.append({"edge": [a, b], "label": lab, "program": key})
    return out


def micro_sets(tool, key, packages):
    truth = json.loads((subjects.SNIPPETS / key / "callgraph.json").read_text())
    p = RES / "tools" / tool / "micro" / f"{key}.json"
    mine = json.loads(p.read_text()) if p.exists() else {}
    te = {(a, b) for a, bs in truth.items() for b in bs}
    me = {(a, b) for a, bs in mine.items() for b in bs}
    return sorted(me - te), sorted(te - me), te, me


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("tool")
    ap.add_argument("--baseline", default="pycg-2026")
    ap.add_argument("--benchmark", default="macro", choices=["macro", "micro"])
    a = ap.parse_args(argv)
    labels = []
    overlap = Counter()
    if a.benchmark == "macro":
        sc = json.loads((RES / "scores" / f"{a.tool}.json").read_text())["macro"]
        base = json.loads((RES / "scores" / f"{a.baseline}.json").read_text())["macro"]
        projs = {}
        import importlib.util
        spec = importlib.util.spec_from_file_location("mp", subjects.MACRO / "projects.py")
        mp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mp)
        projs = mp.load_projects()
        for key, r in sc.items():
            packages = projs[key].package_names
            raw = json.loads((RES / "raw" / a.tool / "macro" / f"{key}.json").read_text())
            fps = [tuple(e) for e in r["false_positives"]]
            fns = [tuple(e) for e in r["false_negatives"]]
            labels += label(a.tool, "macro", key, fps, fns, packages, raw)
            bfp = {tuple(e) for e in base[key]["false_positives"]}
            bfn = {tuple(e) for e in base[key]["false_negatives"]}
            for e in fns:
                overlap["fn-also-baseline" if e in bfn else "fn-only-tool"] += 1
            for e in bfn:
                if e not in set(fns):
                    overlap["fn-only-baseline"] += 1
            for e in fps:
                overlap["fp-also-baseline" if e in bfp else "fp-only-tool"] += 1
            for e in bfp:
                if e not in set(fps):
                    overlap["fp-only-baseline"] += 1
    else:
        for key in sorted(subjects.micro_cases()):
            rawp = RES / "raw" / a.tool / "micro" / f"{key}.json"
            if not rawp.exists():
                continue
            d = subjects.SNIPPETS / key
            packages = sorted({p.relative_to(d).parts[0].removesuffix(".py") for p in d.rglob("*.py")})
            fps, fns, te, me = micro_sets(a.tool, key, packages)
            labels += label(a.tool, "micro", key, fps, fns, packages, json.loads(rawp.read_text()))
            bfps, bfns, _, _ = micro_sets(a.baseline, key, packages)
            for e in fns:
                overlap["fn-also-baseline" if e in set(bfns) else "fn-only-tool"] += 1
            overlap["fn-only-baseline"] += len(set(bfns) - set(fns))
            for e in fps:
                overlap["fp-also-baseline" if e in set(bfps) else "fp-only-tool"] += 1
            overlap["fp-only-baseline"] += len(set(bfps) - set(fps))
    c = Counter(x["label"] for x in labels)
    out = RES / "errors" / f"{a.tool}-{a.benchmark}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"summary": dict(c), "overlap_with_" + a.baseline: dict(overlap), "edges": labels},
                              indent=1))
    print(a.tool, a.benchmark, dict(sorted(c.items())))
    print("overlap with", a.baseline, dict(sorted(overlap.items())))


if __name__ == "__main__":
    main()
