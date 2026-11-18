#!/usr/bin/env python3
"""Offline hybrids: combine the graphs of two tools edge-wise (no new analysis, no LLM).

    .venv/bin/python -I eval/combine.py pycg-2026 nscg

writes results/tools/union(pycg-2026,nscg) and results/tools/inter(pycg-2026,nscg) (the
directory names are filesystem-safe: union--pycg-2026--nscg, inter--pycg-2026--nscg).
"""

import json
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "results" / "tools"


def load(p):
    return json.loads(p.read_text()) if p.exists() else None


def combine(a, b):
    for op in ("union", "inter"):
        out = TOOLS / f"{op}--{a}--{b}"
        for ga_path in (TOOLS / a).rglob("*.json"):
            if ga_path.name == "runs.json":
                continue
            rel = ga_path.relative_to(TOOLS / a)
            ga, gb = load(ga_path), load(TOOLS / b / rel)
            if gb is None:
                continue
            g = {}
            for k in set(ga) | set(gb):
                sa, sb = set(ga.get(k, [])), set(gb.get(k, []))
                g[k] = sorted(sa | sb if op == "union" else sa & sb)
            dst = out / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(json.dumps(g, indent=1))
        print("wrote", out)


if __name__ == "__main__":
    combine(sys.argv[1], sys.argv[2])
