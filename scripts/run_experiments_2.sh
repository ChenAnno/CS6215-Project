#!/bin/bash
# Second round (design iteration V2.1, repetitions, model sensitivity). Usage: scripts/run_experiments_2.sh [jobs]
set -u
cd "$(dirname "$0")/.."
J=${1:-16}
PY=.venv/bin/python
$PY -m nscg.run --variant nscg21   --benchmark micro macro --jobs $J
$PY -m nscg.run --variant hybrid21 --benchmark macro       --jobs $J
NSCG_REPEAT=1 $PY -m nscg.run --variant nscg21 --benchmark macro --jobs $J
NSCG_REPEAT=2 $PY -m nscg.run --variant nscg21 --benchmark macro --jobs $J
$PY -m nscg.run --variant nscg21   --benchmark macro micro --jobs $J --model sonnet
$PY -m nscg.run --variant llm-only --benchmark macro       --jobs $J --model sonnet
echo ALL-DONE
