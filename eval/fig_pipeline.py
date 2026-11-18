#!/usr/bin/env python3
"""Draw the NSCG architecture figure (report/figures/pipeline.pdf)."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parent.parent / "report" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

INK, MUTED, SYM, NEU, EDGE = "#0b0b0b", "#52514e", "#e8f0fb", "#fdeee6", "#8a8984"

fig, ax = plt.subplots(figsize=(7.0, 2.5))
ax.set_xlim(0, 100)
ax.set_ylim(0, 34)
ax.axis("off")


def box(x, y, w, h, title, lines, fill):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.2", fc=fill, ec=EDGE, lw=0.8))
    ax.text(x + w / 2, y + h - 1.6, title, ha="center", va="top", fontsize=6.8, weight="bold", color=INK,
            linespacing=1.1)
    ax.text(x + w / 2, y + h - 8.4, "\n".join(lines), ha="center", va="top", fontsize=5.6, color=MUTED,
            linespacing=1.3)


def arrow(x0, y0, x1, y1, text=None, dashed=False):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=8, lw=0.9, color=INK,
                                 linestyle=(0, (3, 2)) if dashed else "-"))
    if text:
        ax.text((x0 + x1) / 2, (y0 + y1) / 2 + 1.0, text, ha="center", va="bottom", fontsize=5.8, color=MUTED)


box(0.5, 7, 9.5, 20, "Python\nprogram", ["source", "modules", "(read only)"], "#f4f4f2")
box(13, 4, 23.5, 26, "S1 Symbolic\nfront-end", ["benchmark naming of nodes", "13 kinds of call sites",
                                               "(explicit + implicit)", "value resolver + C3 MRO",
                                               "name candidates, callbacks,", "argument flows, attr. facts",
                                               "package outline"], SYM)
box(39.5, 4, 22, 26, "N  LLM\nresolution", ["one request per module", "chunk (<=45 sites)",
                                          "prompt = skill + outline +", "source + facts + sites",
                                          "claude -p (Haiku 5.5),", "JSON-schema output,",
                                          "on-disk cache"], NEU)
box(64.5, 4, 22.5, 26, "S2 Symbolic\nvalidation", ["names checked vs. index", "class -> constructor (MRO)",
                                                "inherited -> definer", "path repair / reject",
                                                "alias expansion", "implicit: package only",
                                                "symbolic floor"], SYM)
box(90, 7, 9.5, 20, "Call\ngraph", ["caller ->", "callees", "(scored)"], "#f4f4f2")
arrow(10.4, 17, 12.6, 17)
arrow(36.9, 17, 39.1, 17)
arrow(61.9, 17, 64.1, 17)
arrow(87.4, 17, 89.6, 17)
ax.text(50.5, 0.6, "V3 (hybrid): PyCG callees per caller added to the prompt as evidence", ha="center", fontsize=6.0,
        color=MUTED, style="italic")
arrow(50.5, 2.2, 50.5, 3.6, dashed=True)
ax.text(24.75, 32.2, "deterministic, own implementation", ha="center", fontsize=6.0, color=MUTED)
ax.text(75.75, 32.2, "deterministic, own implementation", ha="center", fontsize=6.0, color=MUTED)
ax.text(50.5, 32.2, "neural (LLM)", ha="center", fontsize=6.0, color=MUTED)
fig.savefig(OUT / "pipeline.pdf", bbox_inches="tight", pad_inches=0.02)
fig.savefig(OUT / "pipeline.png", dpi=200, bbox_inches="tight", pad_inches=0.02)
print("wrote", OUT / "pipeline.pdf")
