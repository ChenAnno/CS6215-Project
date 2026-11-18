#!/usr/bin/env python3
"""Run PyCG-2026 and PyCG-2021 on the renamed micro cases (memorisation probe) with the official runner."""
import importlib.util
import sys
from pathlib import Path

P = Path(__file__).resolve().parent.parent
EV = P / "third_party" / "pycg-evaluation"
spec = importlib.util.spec_from_file_location("evrun", EV / "evaluation" / "common" / "run.py")
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
snippets = P / "results" / "perturbed" / "micro"
for name, flavour, checkout in (("pycg-2026", "new", EV / "PyCG"), ("pycg-2021", "original", P / "third_party" / "PyCG-2021")):
    tool = run.Tool(name + "+renamed", flavour, checkout.resolve(), sys.executable, 0)
    jobs, skipped = run.micro_jobs(snippets=snippets, version=run.python_version(sys.executable))
    run.run(tool, "micro", jobs, P / "results" / "tools", run.DEFAULT_TIMEOUT, skipped, allow_dirty=True)
