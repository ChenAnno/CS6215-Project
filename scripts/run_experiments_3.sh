#!/bin/bash
# Round 3: memorisation probe on the renamed micro cases (eval/perturb.py must have run).
set -u
cd "$(dirname "$0")/.."
J=${1:-16}
PY=.venv/bin/python
NSCG_MICRO=renamed $PY -m nscg.run --variant nscg21   --benchmark micro --jobs $J
NSCG_MICRO=renamed $PY -m nscg.run --variant llm-only --benchmark micro --jobs $J
NSCG_MICRO=renamed $PY -m nscg.run --variant sym      --benchmark micro
echo ALL-DONE
