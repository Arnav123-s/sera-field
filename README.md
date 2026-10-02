# SERA Field

**State-Space Engine for Reasoning and Adaptation**

A research project on persistent learners that retain experience, imagine alternatives,
investigate missing information, and keep independently checked discoveries.

This repository contains two research implementations. Their results and checkpoints
are recorded separately; neither establishes general intelligence.

## Start here

| Track | Implementation | Documentation and evidence |
|---|---|---|
| **SERA discovery lab** | [lab/sera](lab/sera/) and its independent [judge](lab/ccops5/core/) | [Overview](lab/README.md) · [Current results](lab/docs/SERA_STATUS.md) · [How it works](lab/docs/SERA_EXPLAINED.md) |
| **Learned SERA Field** | [sera_field](sera_field/) | [Architecture](docs/NATIVE_ARCHITECTURE.md) · [Usage guides](docs/INDEX.md) · [Assessed studies](reports/INDEX.md) |

## Current research

The discovery lab uses one learner across physics, lists, numbers, and language.
It proposes expressions, learns words and methods, and retains discoveries accepted
by an outside checker. No pretrained language model runs inside the learner.

In the saved four-hour physics/list comparison, both memory configurations proved
24 of 25 physics worlds. A judge regression preserved the verdicts on all 306 old
claims, with 51 accepted. These are bounded experimental results, not general
capability claims. [Full measurements and limitations](lab/docs/SERA_STATUS.md#2-what-it-can-do-measured).

The latest code adds a teaching course with lessons, book study, and three tests
with progressively less help. S24/S25 experiment records are **incomplete**;
SERA-U is a research plan, not an assessed release.

The earlier learned-field track preserves assessed native memory, language,
prediction, and investigation checkpoints. Its native owner completed 786,432
matched teaching presentations and passed 11 qualification checks with exact
replay. [Native study](reports/NATIVE-019/REPORT.md) · [Whole-cycle study](reports/JOINT-021/REPORT.md).

## Run

For the discovery learner, use Python 3.12+ and follow the [lab setup and examples](lab/README.md#quick-start).

For the learned-field interfaces, use Python 3.11+ in a virtual environment:

```sh
python -m pip install -e ".[dev]"
```

Then follow the [task guides](docs/INDEX.md#run-a-task), including the packaged
[persistent investigation example](docs/CONCEPT_USAGE.md).

## Repository layout

| Path | Contents |
|---|---|
| [lab/](lab/) | Discovery learner, judge, tests, research notes, and selected text results |
| [sera_field/](sera_field/) · [tests/](tests/) | Learned-field implementation and independent checks |
| [docs/](docs/) · [protocols/](protocols/) | Architecture, usage, and frozen study protocols |
| [reports/](reports/) · [checkpoints/](checkpoints/) | Compact evidence and assessed inference revisions |
| [Publication scope](PUBLICATION_SCOPE.md) · [manifest](PUBLICATION_MANIFEST.json) | Release provenance, exclusions, and file identities |

Private research history, raw corpora, full training states, and bulky run artifacts
remain in the local research archive. Earlier assessed releases remain available.
