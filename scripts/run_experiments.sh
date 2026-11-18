#!/bin/bash
# Runs every NSCG variant on the selected subjects (LLM answers are cached in results/llm-cache,
# so re-running this script replays them for free). Usage: scripts/run_experiments.sh [jobs]
set -u
cd "$(dirname "$0")/.."
J=${1:-16}
PY=.venv/bin/python
$PY -m nscg.run --variant sym      --benchmark micro macro
$PY -m nscg.run --variant nscg     --benchmark micro macro --jobs $J
$PY -m nscg.run --variant llm-only --benchmark micro macro --jobs $J
$PY -m nscg.run --variant nohints  --benchmark micro macro --jobs $J
$PY -m nscg.run --variant hybrid   --benchmark macro       --jobs $J
echo ALL-DONE
