# SERA Field

**State-Space Engine for Reasoning and Adaptation**

I am building a persistent learner that turns observations and language into a
situation, imagines alternatives, investigates missing information and retains
checked discoveries. SERA Field is an independent research laboratory; the
original SERA project and every earlier experiment remain preserved.

## How it works

Learned input maps drive a geometric situation field. Connected local states
exchange information through learned rotor/sheaf connections. Retained experience
feeds that field; conditional branches explore possible consequences. Observed
outcomes qualify corrections and bind learning credit to the original task.

The **NATIVE-019** owner learned perception, active memory and imagination
together from their first lesson, with freshly initialized weights. Its three
matched courses completed 786,432 presentations; the native owner passed all
11 qualification checks and exact replay. Earlier working releases remain
available. [Teaching and results](reports/NATIVE-019/REPORT.md).
[Architecture and equations](docs/NATIVE_ARCHITECTURE.md) ·
[Research-to-implementation audit](docs/WHOLE_ARCHITECTURE.md)

## Use the assessed releases

| Capability | Measured result | Guide |
|---|---|---|
| Retain human language and numerical observations in the native memory core | 53.34% across 1,496 reserved MultiNLI pairs; MSE 0.0530 on 512 simulated systems | [Native owner](docs/NATIVE_USAGE.md) |
| Interpret a premise and proposed statements | 59.20% on 4,096 reserved human sentence pairs | [Human meaning](docs/SEMANTIC_USAGE.md) |
| Learn an observed response and reuse it for prediction, changed conditions and planning | MSE 0.00454; 255/256 correct directions on new simulated systems | [Acquired models](docs/EXTENSION_USAGE.md) |
| Investigate a measured task and return to its original question | Three measurements reduced mean answer error by 51.8% on 128 supported systems | [Persistent investigations](docs/INQUIRY_USAGE.md) |

Each result links through its guide to the exact curriculum, assumptions,
comparisons, checkpoint and independent assessment.

The latest [whole-cycle study](reports/JOINT-021/REPORT.md) connects retained
language, numerical investigation and actual reward-driven updates through the
same weights. It completed 65,536 matched teaching presentations and 16 persistent
investigations with exact restart. Returned numerical error fell 54% versus its
starting owner on 747 fresh cases. Comparisons and retention are in the report.
The [next work order](docs/COMPLETE_CORE_WORK_ORDER.md) completes the core before
from-scratch behavioral teaching and later incremental learning.
The [current build](docs/CORE_022_OWNER.md) connects a common energy, temporal
credit, conditional alternatives, protected retained state and representation
growth through one fresh owner. Its [executable proposal path](docs/CORE_022_EXECUTABLE_WORK.md)
constructs scalar programs and binds checked methods to actual learning credit.
The [fresh training course](protocols/CORE-022-FOUNDATION.md) combines human
language, complete math problems, programming material and physical investigation
through that owner. [Engineering and teaching records](reports/CORE-022/REPORT.md).

## Run locally

Install Python 3.11+ and create and activate a virtual environment. Then install:

```sh
python -m pip install -e ".[dev]"
```

On the existing Windows setup, run the packaged persistent task example:

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt my-device-001 -- -m sera_field.session_cli --session local/my-device new --input examples/concept-task.json
```

The supervisor reserves one numerical CPU thread and caps its process tree at
2 GiB. Use a fresh attempt name and wait for any existing numerical job to finish.
[Ask further questions or add measurements](docs/CONCEPT_USAGE.md).

## Repository guide

| Location | Contents |
|---|---|
| [Evidence index](reports/INDEX.md) | Results, teaching, comparisons, failures, costs and replay records |
| [Documentation guide](docs/INDEX.md) | Architecture, usage and equation guides grouped by purpose |
| [Current research state](reports/STATE.json) | Active work and qualified checkpoint identities |
| [Architecture tracker](docs/WHOLE_ARCHITECTURE.md) | Source requirements, implemented connections and next acceptance tests |
| [Protocols](protocols/) | Experiments specified before their final assessments |
| [Implementation](sera_field/) · [Tests](tests/) | Learner equations, task interfaces and independent checks |
| [Checkpoints](checkpoints/) | Packaged inference revisions and manifests |
| [Publication manifest](PUBLICATION_MANIFEST.json) | Identities of the reviewed public files |

Raw sources, complete training revisions and optimizer state stay in the local
lab. Compact evidence is published here. The
[earlier detailed README](docs/README_HISTORY_20260920.md) preserves the release
history; the [evidence index](reports/INDEX.md) is the main route to those studies.
