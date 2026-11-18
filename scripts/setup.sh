#!/bin/bash
# Fetches the baselines and the benchmark at their pinned commits and creates the environment.
set -eu
cd "$(dirname "$0")/.."
mkdir -p third_party logs
if [ ! -d third_party/pycg-evaluation ]; then
  git clone https://github.com/vitsalis/pycg-evaluation.git third_party/pycg-evaluation
fi
git -C third_party/pycg-evaluation checkout -q 8a2e52c
git -C third_party/pycg-evaluation submodule update --init      # PyCG (2026 engine) at c5c6a89
git -C third_party/pycg-evaluation/PyCG checkout -q c5c6a89
if [ ! -d third_party/PyCG-2021 ]; then
  git clone https://github.com/vitsalis/PyCG.git third_party/PyCG-2021
fi
git -C third_party/PyCG-2021 checkout -q 046479e                  # the 2021 analysis
uv python install 3.14
[ -d .venv ] || uv venv --python 3.14 .venv
uv pip install --python .venv/bin/python matplotlib
# Sources of the 30 packages of the macro-benchmark at the commits of projects.toml
if [ ! -d third_party/pycg-evaluation/macro-benchmark/projects/funcy ]; then
  (cd third_party/pycg-evaluation && ../../.venv/bin/python -I evaluation/container/fetch.py macro macro-benchmark/projects)
fi
echo "setup done"
