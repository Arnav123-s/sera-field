# SERA discovery lab

One learner that proposes ideas, learns across worlds, and retains discoveries
accepted by an independent judge. Its Field holds learned concepts, words, and
ways of working. No pretrained language model runs inside SERA.

[SERA-U results](SERA_U_REPORT.md) · [Implementation status](docs/SERA_U_STATUS.md) · [Discovery-lab results](docs/SERA_STATUS.md) · [How it works](docs/SERA_EXPLAINED.md)

## Quick start

Use Python 3.12+ and run these commands from `lab/`:

```sh
python -m venv .venv
# Activate the environment: source .venv/bin/activate (Linux/macOS)
# or .venv\Scripts\Activate.ps1 (PowerShell).
python -m pip install -r requirements.txt
python -m pip install -r requirements-torch.txt
python -m pip install -e .
```

The supplied tensor dependency is the CPU build. Use one numerical thread and a
fixed hash seed for comparable runs:

```sh
# Linux/macOS; in PowerShell set the same names with $env:NAME='value'.
export PYTHONHASHSEED=0 PYTHONIOENCODING=utf-8 OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMBA_NUM_THREADS=1
python scripts/sera_one.py --out sera-runs/try --stage teach --hours 0.2 --seed 1
```

Run the teaching course, or talk to a trusted local saved Field:

```sh
python scripts/sera_course.py --out sera-runs/course --hours 0.2 --seed 1
python scripts/sera_talk.py --field sera-runs/try/field-teach.pkl
```

The course progresses through lessons, book study, corrected tests, tests with
only a wrong-answer signal, and finally tests without help. The short command
above is a smoke run; it does not reproduce the longer reported studies.

For the unified learner, inspect the course and frozen comparison interfaces:

```sh
python scripts/sera_u_course.py --help
python scripts/sera_bakeoff.py --help
python scripts/sera_u_report.py --help
python -m pytest -q tests/sera_u
```

The commands above inspect the interfaces and run regression checks. Reproducing
the experiments requires their frozen suites and original runtime states; some
of that evidence remains in the local archive. The published curves and summaries
support inspecting the reported scores.

## Tests and evidence

```sh
python -m pytest -q tests/core tests/sera -m "not slow"
# On Linux/macOS with Bash and timeout, run one file at a time:
JOBS=1 bash scripts/runtests.sh
```

Slow and integration checks have separate budgets in `scripts/runtests.sh`.
Saved measurements are in [sera-runs/](sera-runs/); the [status report](docs/SERA_STATUS.md)
names the source run for every result. S24/S25 runs are incomplete, and the
SERA-U release contains four-generation full-arm memory and discovery comparisons.
Some ablation arms stopped early; the full course and replicated comparisons remain open.
Its course, comparison runner, and current limitations are documented in
[SERA-U status](docs/SERA_U_STATUS.md).

## Layout

| Path | Contents |
|---|---|
| [sera_u/](sera_u/) | Unified learner and pinned Field implementation |
| [sera/](sera/) | Learner, expression language, Field, words, and task interfaces |
| [ccops5/core/](ccops5/core/) | Grammar, simulator, likelihood, certificates, and independent checker |
| [scripts/](scripts/) | Teaching, conversation, course runners, and evidence summaries |
| [tests/](tests/) | Learner and judge checks |
| [docs/](docs/) · [research/](research/) | Explanations, judge decisions, and research notes |
| [sera-runs/](sera-runs/) · [core-results/](core-results/) | Selected compact text evidence |
| [legacy/](legacy/) | Preserved earlier experiment tracks |

Raw corpora, binary Fields, full run logs, and development coordination records
stay local. External comparison and curriculum data are not bundled.

The 2026-10-04 update adds U13 full-arm results and a compact U14 saved-schema
summary. The legacy report generator cannot yet read the U14 exam schema; consult
[implementation status](docs/SERA_U_STATUS.md#u13u14-completion-and-failures) for
the verified zero-answer results, interrupted comparison and open memory issue.
