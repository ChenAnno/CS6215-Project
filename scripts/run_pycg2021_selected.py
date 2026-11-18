#!/usr/bin/env python3
"""Run PyCG-2021 on selected macro projects only (same runner and limits); output in results/tools-extra."""
import importlib.util
import sys
from pathlib import Path

P = Path(__file__).resolve().parent.parent
EV = P / "third_party" / "pycg-evaluation"
spec = importlib.util.spec_from_file_location("evrun", EV / "evaluation" / "common" / "run.py")
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
names = sys.argv[1:]
tool = run.Tool("pycg-2021", "original", (P / "third_party" / "PyCG-2021").resolve(), sys.executable, 0)
jobs = [j for j in run.macro_jobs()[0] if j.key.split("/", 1)[1] in names]
run.run(tool, "macro", jobs, P / "results" / "tools-extra", run.DEFAULT_TIMEOUT, [], allow_dirty=False)
