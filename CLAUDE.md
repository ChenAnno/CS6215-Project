# Instructions for coding agents (Claude Code, Codex, ...)

This repository is the artifact of a course project that compares symbolic call-graph
generators for Python (PyCG-2026, PyCG-2021) with NSCG, a neuro-symbolic analyzer
(`nscg/`). Read `README.md` first. To reproduce the study, do exactly this:

1. `scripts/setup.sh` — clones the baselines and the benchmark at their pinned commits into
   `third_party/`, creates `.venv` (Python 3.14 via `uv`), fetches the 30 package sources.
2. `scripts/run_baselines.sh` — runs both PyCG engines with the official runner
   (PyCG-2021 needs up to 30 minutes on some packages; that limit is part of the protocol).
3. `.venv/bin/python -I eval/perturb.py --validate` then
   `.venv/bin/python -I scripts/run_baselines_renamed.py` — the memorisation probe inputs.
4. `NSCG_OFFLINE=1 scripts/run_experiments.sh && NSCG_OFFLINE=1 scripts/run_experiments_2.sh && NSCG_OFFLINE=1 scripts/run_experiments_3.sh`
   — replays every LLM answer from `results/llm-cache/` (no LLM access needed). Drop
   `NSCG_OFFLINE=1` to send new requests through `claude -p` (requires a logged-in Claude Code CLI).
5. `.venv/bin/python -I eval/combine.py pycg-2026 nscg-v21`
6. `.venv/bin/python -I eval/score_all.py` and
   `NSCG_MICRO=renamed .venv/bin/python -I eval/score_all.py --tools pycg-2026+renamed pycg-2021+renamed nscg-sym+renamed llm-only+renamed nscg-v21+renamed`
7. `for t in nscg-sym llm-only nscg nscg-v21 nscg-hybrid-v21; do .venv/bin/python -I eval/errors.py $t --benchmark macro; done`
8. `.venv/bin/python -I eval/tables.py` (writes `report/tables/*.tex`, `results/tables.md`) and
   `.venv/bin/python eval/fig_pipeline.py`, `.venv/bin/python eval/fig_results.py`.
9. Compare `results/tables.md` with the tables of `report/main.pdf`; they must be equal.

Rules:
- Never edit a ground truth or the third-party code; the baselines run unmodified.
- Always run Python with `-I` for scripts that read third-party code.
- Long runs: start them detached (`setsid nohup ... &`) and log to `logs/`.
- The scorer is `third_party/pycg-evaluation/evaluation/common/score.py` (raw mode); do not
  write another one.
