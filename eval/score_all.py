#!/usr/bin/env python3
"""Score every tool directory under results/tools with the official PyCG-evaluation scorer.

    .venv/bin/python -I eval/score_all.py [--tools pycg-2026 nscg-v2 ...] [--projects a b c d]
        [--micro-cases eval/micro_cases.txt]

A tool directory has the layout of pycg-evaluation's run.py:
    results/tools/<tool>/micro/<category>/<case>.json
    results/tools/<tool>/macro/<project>.json
(and optionally runs.json). Scores are computed with
third_party/pycg-evaluation/evaluation/common/score.py (raw mode, the headline
mode of the PyCG evaluation), so baselines and our analyzers are scored identically.

Writes results/scores/<tool>.json (per case / per project counts, FP and FN lists)
and results/scores/summary.json (aggregates restricted to the selected subjects).
"""

import argparse
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
EVAL_REPO = PROJECT / "third_party" / "pycg-evaluation"
TOOLS = PROJECT / "results" / "tools"
SCORES = PROJECT / "results" / "scores"

sys.path.insert(0, str(HERE))
import subjects  # noqa: E402


def load_scorer():
    path = EVAL_REPO / "evaluation" / "common" / "score.py"
    spec = importlib.util.spec_from_file_location("pycg_eval_score", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def counts_json(c):
    return c.to_json()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tools", nargs="*")
    ap.add_argument("--mode", default="raw", choices=["raw", "normalised"])
    args = ap.parse_args(argv)
    score = load_scorer()
    SCORES.mkdir(parents=True, exist_ok=True)
    tools = args.tools or sorted(p.name for p in TOOLS.iterdir() if p.is_dir())
    micro_keys = subjects.micro_cases()
    projects = subjects.MACRO_PROJECTS
    summary = {}
    for tool in tools:
        tdir = TOOLS / tool
        out = {"tool": tool, "mode": args.mode}
        row = {}
        if (tdir / "micro").is_dir():
            cases = score.score_micro(tdir, snippets=subjects.SNIPPETS)
            sel = {k: v for k, v in cases.items() if k in micro_keys}
            cats = score.micro_categories(sel, args.mode)
            total = score.micro_total(cats)
            out["micro"] = {
                "cases": {
                    k: (
                        {"status": v["status"]}
                        if v["status"] == "skipped"
                        else {
                            "status": v["status"],
                            "complete": v[args.mode]["complete"],
                            "sound": v[args.mode]["sound"],
                            "exact": v[args.mode]["exact"],
                            **{e: counts_json(v[args.mode]["counts"][e]) for e in score.EDGE_SETS},
                        }
                    )
                    for k, v in sel.items()
                },
                "categories": {
                    c: {**{f: r[f] for f in ("cases", "skipped", "failed", "complete", "sound", "exact")},
                        **{e: counts_json(r["counts"][e]) for e in score.EDGE_SETS}}
                    for c, r in cats.items()
                },
                "total": {**{f: total[f] for f in ("cases", "skipped", "failed", "complete", "sound", "exact")},
                          **{e: counts_json(total["counts"][e]) for e in score.EDGE_SETS}},
            }
            row["micro"] = out["micro"]["total"]
        if (tdir / "macro").is_dir():
            per = score.score_macro(tdir)
            out["macro"] = {}
            agg = {e: score.ZERO for e in score.EDGE_SETS}
            for name in projects:
                r = per[name]
                m = r[args.mode]
                out["macro"][name] = {
                    "status": r["status"],
                    **{e: counts_json(m[e]) for e in score.EDGE_SETS},
                    "false_positives": m["false_positives"],
                    "false_negatives": m["false_negatives"],
                }
                for e in score.EDGE_SETS:
                    agg[e] = agg[e] + m[e]
            out["macro_total"] = {e: counts_json(agg[e]) for e in score.EDGE_SETS}
            row["macro"] = out["macro_total"]
            row["macro_projects"] = {n: {e: out["macro"][n][e] for e in ("inside", "outside", "all")}
                                     | {"status": out["macro"][n]["status"]} for n in projects}
        if subjects.RENAMED:
            out["micro_cohort"] = "renamed probe (eval/perturb.py)"
        (SCORES / f"{tool}.json").write_text(json.dumps(out, indent=1))
        summary[tool] = row
        print(f"== {tool}")
        if "micro" in row:
            t = row["micro"]
            print(f"  micro ({t['cases']} cases, {t['exact']} exact): inside P={t['inside']['precision']} R={t['inside']['recall']} "
                  f"| outside P={t['outside']['precision']} R={t['outside']['recall']} | all F1={t['all']['f1']}")
        if "macro" in row:
            for n, v in row["macro_projects"].items():
                print(f"  {n:16s} [{v['status']}] inside P={v['inside']['precision']} R={v['inside']['recall']} "
                      f"(tp {v['inside']['tp']}/fp {v['inside']['fp']}/fn {v['inside']['fn']}) | outside P={v['outside']['precision']} R={v['outside']['recall']}")
            t = row["macro"]
            print(f"  {'TOTAL':16s} inside P={t['inside']['precision']} R={t['inside']['recall']} F1={t['inside']['f1']} "
                  f"| outside P={t['outside']['precision']} R={t['outside']['recall']} F1={t['outside']['f1']}")
    old = json.loads((SCORES / "summary.json").read_text()) if (SCORES / "summary.json").exists() else {}
    old.update(summary)
    (SCORES / "summary.json").write_text(json.dumps(old, indent=1))


if __name__ == "__main__":
    main()
