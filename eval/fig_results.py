#!/usr/bin/env python3
"""Result figures of the report.

report/figures/pr_macro.pdf   precision vs recall (inside edges) of every tool, four packages and micro
report/figures/categories.pdf all-edge F1 per micro category, the categories where the tools differ most
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
RES = PROJECT / "results"
OUT = PROJECT / "report" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# Reference categorical palette (light mode), first three slots: validated all-pairs.
C_BASE, C_NS, C_HYB = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.size": 7, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False})

TOOLS = [
    ("pycg-2021", "PyCG-2021", C_BASE, "s"), ("pycg-2026", "PyCG-2026", C_BASE, "s"),
    ("nscg-sym", "S1 only", C_NS, "o"), ("llm-only", "V0", C_NS, "o"), ("nscg-nohints", "V1", C_NS, "o"),
    ("nscg", "V2", C_NS, "o"), ("nscg-v21", "V2.1", C_NS, "o"),
    ("nscg-hybrid-v21", "V3", C_HYB, "D"), ("union--pycg-2026--nscg-v21", "∪", C_HYB, "D"),
    ("inter--pycg-2026--nscg-v21", "∩", C_HYB, "D"),
]


def pr(c):
    return (c["tp"] / c["tool"] if c["tool"] else 0), (c["tp"] / c["truth"] if c["truth"] else 0)


def load(t):
    p = RES / "scores" / f"{t}.json"
    return json.loads(p.read_text()) if p.exists() else None


OFFSETS = {
    "micro": {"V0": (4, 3), "V1": (-11, 4), "V2": (-12, -8), "V2.1": (4, -8), "∪": (4, -3), "∩": (4, 1),
              "PyCG-2026": (4, 2), "PyCG-2021": (4, 2), "S1 only": (4, 2)},
    "macro": {"V0": (4, -6), "V1": (4, 1), "V2": (-12, 3), "V2.1": (4, -8), "V3": (4, 1), "∪": (4, -2),
              "∩": (-12, 2), "PyCG-2026": (4, -2), "PyCG-2021": (4, 2), "S1 only": (4, 2)},
}


def scatter():
    import numpy as np

    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.5), gridspec_kw={"wspace": 0.28})
    for ax, key, title in ((axes[0], "micro", "Micro-benchmark, inside edges"),
                           (axes[1], "macro", "Four packages, inside edges")):
        pts = []
        for t, label, color, marker in TOOLS:
            s = load(t)
            if s is None:
                continue
            c = s["micro"]["total"]["inside"] if key == "micro" and "micro" in s else (
                s["macro_total"]["inside"] if key == "macro" and "macro_total" in s else None)
            if c is None:
                continue
            p, r = pr(c)
            pts.append((r, p, label, color, marker))
        rs = [x[0] for x in pts]
        ps = [x[1] for x in pts]
        x0, x1 = max(0.0, min(rs) - 0.05), min(1.0, max(rs) + 0.06)
        y0, y1 = max(0.0, min(ps) - 0.03), min(1.005, max(ps) + 0.02)
        ax.set_xlim(x0, x1)
        ax.set_ylim(y0, y1)
        for f in (0.5, 0.6, 0.7, 0.8, 0.9, 0.95):
            rr = np.linspace(max(f / (2 - f) + 1e-3, x0), x1, 200)
            pp = f * rr / (2 * rr - f)
            ok = (pp >= y0) & (pp <= y1)
            if ok.sum() < 2:
                continue
            ax.plot(rr[ok], pp[ok], color=GRID, lw=0.8, zorder=0)
            i = np.where(ok)[0][0]
            ax.text(rr[i], pp[i], f" F1={f}", fontsize=5.2, color=MUTED, ha="left", va="top", clip_on=True)
        for r, p, label, color, marker in pts:
            ax.scatter([r], [p], s=24, color=color, marker=marker, edgecolor="white", linewidth=0.8, zorder=3)
            dx, dy = OFFSETS[key].get(label, (4, 2))
            ax.annotate(label, (r, p), xytext=(dx, dy), textcoords="offset points", fontsize=6, color=INK)
        ax.set_xlabel("recall")
        ax.set_ylabel("precision")
        ax.set_title(title, fontsize=7.5, color=INK)
        ax.grid(True, color=GRID, lw=0.5)
    from matplotlib.lines import Line2D

    handles = [Line2D([], [], marker="s", ls="", color=C_BASE, label="symbolic baselines"),
               Line2D([], [], marker="o", ls="", color=C_NS, label="NSCG variants (ours)"),
               Line2D([], [], marker="D", ls="", color=C_HYB, label="hybrids with PyCG-2026")]
    fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False, fontsize=6.5, bbox_to_anchor=(0.5, 1.04))
    fig.savefig(OUT / "pr.pdf", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(OUT / "pr.png", dpi=200, bbox_inches="tight", pad_inches=0.02)


def categories():
    p = RES / "micro_categories.json"
    if not p.exists():
        return
    d = json.loads(p.read_text())
    tools = d["tools"]
    keep = [tools.index(t) for t in ("PyCG-26", "V0", "V2.1")]
    rows = d["rows"]
    spread = {c: max(v[i] for i in keep if v[i] is not None) - min(v[i] for i in keep if v[i] is not None) for c, v in rows.items()}
    cats = sorted(sorted(rows, key=lambda c: -spread[c])[:14], key=lambda c: rows[c][keep[0]] or 0)
    fig, ax = plt.subplots(figsize=(3.35, 2.6))
    colors = [C_BASE, C_NS, "#6250d6"]
    markers = ["s", "o", "^"]
    for j, i in enumerate(keep):
        ys = range(len(cats))
        xs = [rows[c][i] for c in cats]
        ax.scatter(xs, ys, s=16, color=colors[j], marker=markers[j], label=["PyCG-2026", "V0 LLM-only", "V2.1 NSCG"][j],
                   edgecolor="white", linewidth=0.6, zorder=3)
    for y, c in enumerate(cats):
        vals = [rows[c][i] for i in keep]
        ax.plot([min(vals), max(vals)], [y, y], color=GRID, lw=1.2, zorder=1)
    ax.set_yticks(range(len(cats)))
    ax.set_yticklabels([f"{c} ({d['cases'][c]})" for c in cats], fontsize=6)
    ax.set_xlabel("all-edge F1 per category")
    ax.grid(True, axis="x", color=GRID, lw=0.5)
    ax.legend(frameon=False, fontsize=6, loc="lower left", bbox_to_anchor=(0.0, 1.0), ncol=3, handletextpad=0.2,
              columnspacing=0.8)
    fig.tight_layout()
    fig.savefig(OUT / "categories.pdf", bbox_inches="tight", pad_inches=0.02)
    fig.savefig(OUT / "categories.png", dpi=200, bbox_inches="tight", pad_inches=0.02)


if __name__ == "__main__":
    scatter()
    categories()
    print("figures written to", OUT)
