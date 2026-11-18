"""The evaluation subjects of the study (single source of truth for every script).

Micro: every case of the PyCG micro-benchmark whose `requires-python` is at most 3.12
(the 622-case cohort that the PyCG evaluation uses for cross-tool comparison).
Macro: four real-world packages of the pycg-evaluation macro-benchmark; see
README.md ("Subject selection") and the report (Section 4.1) for the rationale.
"""

import os
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
EVAL_REPO = PROJECT / "third_party" / "pycg-evaluation"
SNIPPETS = EVAL_REPO / "PyCG" / "micro-benchmark" / "snippets"
ORIGINAL_SNIPPETS = SNIPPETS
# NSCG_MICRO=renamed: the memorisation probe (eval/perturb.py), renamed cases that still validate.
RENAMED = os.environ.get("NSCG_MICRO") == "renamed"
if RENAMED:
    SNIPPETS = PROJECT / "results" / "perturbed" / "micro"
MACRO = EVAL_REPO / "macro-benchmark"

ALL_MACRO = sorted(p.name[:-5] for p in (MACRO / "ground-truth").glob("*.json") if p.name.count(".") == 1)

# The selected packages (override with NSCG_PROJECTS=a,b,c for exploration).
SELECTED = ["autojump", "fabric", "jmespath", "funcy"]
MACRO_PROJECTS = os.environ["NSCG_PROJECTS"].split(",") if os.environ.get("NSCG_PROJECTS") else SELECTED
if MACRO_PROJECTS == ["ALL"]:
    MACRO_PROJECTS = ALL_MACRO


def _version(text):
    return tuple(int(x) for x in text.strip().split("."))


def micro_cases(max_python=(3, 12), renamed=None):
    """Keys `<category>/<case>` of the micro cohort (of the renamed probe if NSCG_MICRO=renamed)."""
    import json

    if RENAMED if renamed is None else renamed:
        return set(json.loads((PROJECT / "results" / "perturbed" / "micro-perturbation.json").read_text())["cohort"])
    keys = set()
    for case in sorted(p for p in ORIGINAL_SNIPPETS.glob("*/*") if p.is_dir()):
        req = case / "requires-python"
        if req.exists() and _version(req.read_text()) > max_python:
            continue
        keys.add(f"{case.parent.name}/{case.name}")
    return keys
