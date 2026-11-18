# NSCG — Neuro-Symbolic Call Graphs for Python vs. PyCG

Artifact of the CS6215 (NUS, Fall 2026) individual course project
*"Symbolic vs. neuro-symbolic static call-graph construction for Python"*.

The project compares two **symbolic** call-graph generators, **PyCG** (the 2026 engine) and the
original **PyCG of ICSE 2021**, with **NSCG**, a neuro-symbolic analyzer designed and implemented
for this project. NSCG uses a symbolic front-end to enumerate call sites and propose callees, asks
an LLM (Claude Haiku 5.5 through headless Claude Code) to decide each site, and validates the
answers symbolically. All tools are scored with the official scorer of the PyCG evaluation on the
PyCG micro-benchmark (622 cases) and on four real packages with audited ground truths
(autojump, fabric, jmespath, funcy).

The report is `report/main.pdf` (source `report/main.tex`).

## Repository layout

| Path | What it is |
|---|---|
| `nscg/frontend.py` | S1, the symbolic front-end: benchmark naming of nodes, 11 kinds of call sites, value resolver with C3 MRO, name candidates, callbacks, argument flows, attribute facts, package outline, library hooks (V2.1) |
| `nscg/prompts.py` | All LLM-facing text: the conventions "skill", the per-site prompt (V1/V2/V3), the LLM-only prompt (V0), JSON schemas |
| `nscg/llm.py` | LLM backend: `claude -p` with `--json-schema`, on-disk cache of every request (prompt, answer, tokens, cost); optional OpenAI-compatible backend (e.g. SoCLaaS) |
| `nscg/validate.py` | S2, symbolic validation of the answers (index check, constructor/MRO mapping, path repair, alias expansion, symbolic floor) |
| `nscg/run.py` | Runs a variant on the subjects and writes graphs in the layout of the PyCG evaluation |
| `eval/subjects.py` | The evaluation subjects (single source of truth) |
| `eval/score_all.py` | Scores every tool with `pycg-evaluation/evaluation/common/score.py` (raw mode) |
| `eval/errors.py` | Error taxonomy of FP/FN edges and overlap with a baseline |
| `eval/combine.py` | Offline hybrids: union / intersection of two tools' graphs |
| `eval/tables.py`, `eval/fig_*.py` | The tables and figures of the report |
| `scripts/setup.sh` | Fetches the baselines and benchmark at their pinned commits and creates the environment |
| `scripts/run_baselines.sh` | Runs PyCG-2026 and PyCG-2021 with the official runner |
| `scripts/run_experiments.sh`, `scripts/run_experiments_2.sh` | Run every NSCG variant (round 1 and round 2) |
| `results/tools/<tool>/` | Call graphs of every tool: `micro/<category>/<case>.json`, `macro/<project>.json` |
| `results/scores/` | Scores per tool (per case, per project, FP/FN lists) and `summary.json` |
| `results/raw/<tool>/` | Per site: what the front-end proposed and what the LLM answered |
| `results/runs/` | Per run: wall time, requests, tokens, cost, validation statistics |
| `results/llm-cache/` | Every LLM request and answer (makes the results replayable offline) |
| `results/errors/` | Labelled FP/FN edges |
| `report/` | LaTeX source (ACM `sigconf`), figures, generated tables |
| `CLAUDE.md` | Instructions for a coding agent (Claude Code / Codex) to reproduce the study |

## Baselines and benchmark (third-party, pinned)

| Component | Source | Pin |
|---|---|---|
| PyCG (2026 engine) | <https://github.com/vitsalis/PyCG> (submodule of pycg-evaluation) | `c5c6a89` |
| PyCG of ICSE 2021 (the 2021 analysis, ported to Python 3.12+) | <https://github.com/vitsalis/PyCG> | `046479e` |
| PyCG evaluation (macro-benchmark, ground truths, scorer, runner) | <https://github.com/vitsalis/pycg-evaluation> | `8a2e52c` |
| Micro-benchmark | `PyCG/micro-benchmark` in the submodule | `c5c6a89` |
| Package sources | fetched by `pycg-evaluation/evaluation/container/fetch.py` at the commits of `projects.toml` | per project |

PyCG paper: V. Salis, T. Sotiropoulos, P. Louridas, D. Spinellis, D. Mitropoulos.
*PyCG: Practical Call Graph Generation in Python.* ICSE 2021.

## Requirements

* Linux x86-64, `git`, `uv` (to get Python 3.14), network access for the first setup.
* For new LLM requests: Claude Code CLI (`claude`, logged in) — tested with 2.1.321 — or an
  OpenAI-compatible endpoint (see below). **Not needed to reproduce the reported numbers**: every
  answer is cached in `results/llm-cache/` and replayed offline.
* Python dependencies: none for NSCG and the scorer (standard library only); `matplotlib` for figures.

## Reproducing the results

```sh
scripts/setup.sh                 # pinned clones in third_party/, Python 3.14 venv, package sources
scripts/run_baselines.sh         # PyCG-2026 and PyCG-2021 on micro + macro (official runner)
NSCG_OFFLINE=1 scripts/run_experiments.sh      # replays every round-1 LLM answer from the cache
NSCG_OFFLINE=1 scripts/run_experiments_2.sh    # round 2 (V2.1, repetitions, Sonnet)
.venv/bin/python -I eval/perturb.py --validate # renaming probe: renamed micro cases, checked dynamically
.venv/bin/python -I scripts/run_baselines_renamed.py
NSCG_OFFLINE=1 scripts/run_experiments_3.sh    # round 3 (probe)
NSCG_OFFLINE=1 .venv/bin/python -m nscg.run --variant nscg21 --benchmark micro macro --no-validate
NSCG_OFFLINE=1 .venv/bin/python -m nscg.run --variant nscg21 --benchmark micro macro --no-floor
.venv/bin/python -I eval/combine.py pycg-2026 nscg-v21
.venv/bin/python -I eval/score_all.py          # results/scores/*.json (takes a few minutes)
NSCG_MICRO=renamed .venv/bin/python -I eval/score_all.py --tools pycg-2026+renamed pycg-2021+renamed \
    nscg-sym+renamed llm-only+renamed nscg-v21+renamed
for t in nscg-sym llm-only nscg nscg-v21 nscg-hybrid-v21; do .venv/bin/python -I eval/errors.py $t --benchmark macro; done
.venv/bin/python -I eval/tables.py             # report/tables/*.tex, report/numbers.tex, results/tables.md
.venv/bin/python eval/fig_pipeline.py && .venv/bin/python eval/fig_results.py
```

Without `NSCG_OFFLINE=1`, a request that is not in the cache is sent to the LLM (new answers are
added to the cache). To run a single variant:

```sh
.venv/bin/python -m nscg.run --variant nscg21 --benchmark micro macro --model haiku --jobs 16
```

### Variants

| Variant (`--variant`) | Tool directory | What it is |
|---|---|---|
| `sym` | `nscg-sym` | S1 only: the symbolic pre-resolution of each site, no LLM |
| `llm-only` | `llm-only` | V0: the LLM reads the source and writes the call graph |
| `nohints` | `nscg-nohints` | V1: symbolic sites, no per-site symbolic information |
| `nscg` | `nscg` | V2: sites + resolution + candidates + callbacks + facts, then validation |
| `nscg21` | `nscg-v21` | V2.1: V2 + library-hook candidates + validator fixes (the final design) |
| `hybrid` / `hybrid21` | `nscg-hybrid`, `nscg-hybrid-v21` | V3: V2 / V2.1 plus PyCG-2026's callees per caller as evidence |
| — | `union--pycg-2026--nscg-v21`, `inter--...` | offline edge-set union / intersection |

`--model sonnet` adds the suffix `@sonnet`; `NSCG_REPEAT=k` makes an independent repetition
(suffix `-rk`).

### Using another LLM service (e.g. SoCLaaS)

```sh
export NSCG_BACKEND=openai OPENAI_BASE_URL=https://<gateway>/v1 OPENAI_API_KEY=...
.venv/bin/python -m nscg.run --variant nscg21 --benchmark macro --model <served-model-name>
```

## Subject selection

* **Micro-benchmark**: the 622 cases whose `requires-python` is at most 3.12 — the cohort that the
  PyCG evaluation uses to compare tools; one small program per language feature, 34 categories.
* **Macro-benchmark**: 4 of the 30 audited packages, chosen to cover both regimes of the baseline
  (PyCG-2026 strong: autojump, jmespath; PyCG-2026 weak: fabric — framework subclassing of Invoke —
  and funcy — higher-order functional code), two packages of the ICSE 2021 set and two of the
  later batches, and to fit the token budget (1,973 sites in total).

## Key results

Inside edges (callee in the analysed package), official scorer, raw names. Full tables:
`results/tables.md`.

| Tool | Micro P / R / F1 | exact cases (of 622) | 4 packages P / R / F1 |
|---|---|---|---|
| PyCG-2021 | 0.868 / 0.605 / 0.713 | 201 | 0.927 / 0.308 / 0.462 (timeout on funcy) |
| PyCG-2026 | 0.925 / 0.936 / 0.931 | 466 | 0.894 / 0.712 / 0.793 |
| V0 LLM-only (Haiku) | 0.893 / 0.995 / 0.941 | 265 | 0.958 / 0.685 / 0.799 |
| **NSCG V2.1 (Haiku)** | 0.889 / 0.974 / 0.930 | 251 | 0.913 / 0.732 / 0.812 |
| NSCG V2.1 (Sonnet) | 0.912 / 0.973 / 0.941 | 273 | 0.928 / 0.739 / 0.823 |
| PyCG-2026 ∩ NSCG | 0.943 / 0.916 / 0.929 | 450 | 0.977 / 0.698 / 0.814 |
| PyCG-2026 ∪ NSCG | 0.875 / 0.994 / 0.931 | 428 | 0.844 / 0.746 / 0.792 |

Three repetitions of NSCG V2.1 on the packages: inside F1 0.812 ± 0.009 (recall identical in all
runs). Renaming probe (580 micro cases): NSCG V2.1 inside F1 0.930 → 0.933, V0 0.942 → 0.948.

## Resource budget

All LLM requests of the study cost US$21.15 (Haiku runs about $5, Sonnet runs about $16; per
run in `results/runs/*.json` and Table "cost" of the report). A full NSCG run on the four
packages takes about a minute with 16 parallel requests. The baselines run in seconds per
package except the 2021 engine, which timed out (30-minute limit, as in the PyCG evaluation) on
funcy, bottle and crashed on itables.

## Licences

Our code: MIT. Third-party code (PyCG, pycg-evaluation, the packages) keeps its own licence and is
not redistributed here; `scripts/setup.sh` fetches it.
