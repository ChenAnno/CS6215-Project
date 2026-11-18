#!/bin/bash
# Runs both PyCG engines with the official runner of the PyCG evaluation (30-minute limit per job).
set -eu
cd "$(dirname "$0")/.."
P=$(pwd)
cd third_party/pycg-evaluation
$P/.venv/bin/python -I evaluation/common/run.py --flavour new --checkout PyCG --name pycg-2026 --out $P/results/tools
$P/.venv/bin/python -I evaluation/common/run.py --flavour original --checkout ../PyCG-2021 --name pycg-2021 --out $P/results/tools
