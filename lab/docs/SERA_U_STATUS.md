# SERA-U: implementation and evidence

This is an experimental implementation, not a completed behavioral release.
The source revision is recorded in the publication manifest. No pretrained model
is loaded; the unified learner initializes its geometric Field from fresh weights.

## Implementation status

| Component | Status in this snapshot |
|---|---|
| U1 Field integration | Merged; 883,411 parameters in the saved initial preflight |
| U2 two-layer memory and understanding | Merged |
| US training optimization | Merged; measured standard-batch speedup below |
| US2 batched memory and caches | Merged; saved timing found no overall gain |
| U3 imagination and inner judge | Merged; hypothetical examples use a separate channel |
| U4 adaptive scrutiny | Merged; disabled by default; acceptance requirements preserved |
| U6 consistency-based curiosity | Merged |
| U7 answer or continue, revisit queue | Merged; requires teaching of the choice |
| U5 course, crutch ledger, 12-arm comparison runner | Merged; full comparison not completed |
| US3 faster faculty readouts | Merged; mixed measured results below |
| US3b batched layer-B reads and cache use | Merged; saved profile shows modest memory-on improvement |
| U8 learned memory consultation and retention choices | Merged; outcome per second and later memory-use eligibility guide learning |
| U9 autonomous discovery | Merged; learner poses questions, chooses experiments and submits laws to independent judges |
| U10 thought experiments, invariance, assumptions and predictions | Merged; comparison runs partly complete |
| U11 scientific and mathematical habits | Merged; comparisons pending |
| U12 internal-world lineage and gradual-change reasoning | Merged; comparisons pending |
| U13 typed operations, reconstruction and calibrated estimates | Merged; five full-arm curves saved; one complete all-arm case |
| U14 work clock, one continuing life, question priority and holes | Merged; two gap cases finished with zero exam answers; priority comparison crashed |

Publication regression checks and exact source identity are recorded in the
[manifest](../../PUBLICATION_MANIFEST.json). The suite covers SERA-U, the course
and crutch checks; it does not imply every historical repository test passes.

## Measured speed

[One-thread CPU benchmark](../sera-runs/us-speed-cpu/speed.json), three repetitions:

| Operation | Before | After | Speedup |
|---|---:|---:|---:|
| Standard training batch | 47.35 s | 5.92 s | 8.00x |
| Varied-query training | 22.74 s | 6.43 s | 3.53x |
| Dream diagnostic | 3.84 s | 0.54 s | 7.16x |

Single reads remained about 2 seconds. The maximum parameter difference after a
training step was 1.16e-5; the optimization was not bitwise identical.

## New profiling results

[US2 reference](../sera-runs/us2-memory/prof/memory-reference2.json) and
[optimized memory](../sera-runs/us2-memory/prof/memory-native2.json) were measured
side by side on one-thread Xeon cases, 28 items per case. Median item time with
memory was 15.3 seconds before and 16.0 after; without memory, 11.5 and 10.3.
There was no demonstrated overall memory speedup. Coupled settling of observed
records dominated one profiled step (56.6 of 72.9 seconds).

[US3 before](../sera-runs/us3-step-b5a4883/us3-step-before.json) and
[after](../sera-runs/us3-step-b5a4883/us3-step-after.json), 24 items per case:
with faculty readouts and memory disabled, median item time improved 21.3 to
11.4 seconds. With memory enabled, it worsened 24.7 to 34.1 seconds. Configurations
without faculty readouts were essentially unchanged. All remained over the
10-second item budget. US3b addresses batching across different layer-B rings and
using the step-read cache, and its newer profile is reported below.

U8 lets the learner choose plain/A/B/both reads and whether to remember an item.
Later successful memory use earns eligibility credit; this is not causal proof
of memory usefulness. U9 adds question selection, discriminating experiments,
independently checked laws, and compression priors. New full-arm comparisons for memory and discovery are reported below;
some other arms stopped early, and broader capability claims remain unassessed.

## Latest comparisons (2026-10-04)

The [research report](../SERA_U_REPORT.md) and [detail tables](../SERA_U_REPORT_TABLES.md)
retain the generated measurements, suite identities and interpretation. Some
underlying runtime-state snapshots referenced by those tables remain in the local
archive; compact curves, protocols and summaries are published here.

On one shared assessment suite, full-arm solved counts out of 48 across g0-g3:

| Memory configuration | g0 | g1 | g2 | g3 |
|---|---:|---:|---:|---:|
| Layers disabled | 26 | 48 | 39 | 47 |
| Always enabled | 28 | 40 | 38 | 34 |
| Learner chooses | 26 | 33 | 38 | 36 |

One replicate pair differed by up to 10/48 items and 4.3 seconds. This is an
observed spread, not a confidence interval. Most differences are within it; a
single run per configuration does not establish a memory benefit or disadvantage.
The full-arm generations are available even where later ablation arms stopped.

Discovery found few of 14 hidden laws in approximately 15 minutes per full arm:
designed experiments certified 0, random experiments 2, and no unification credit 2.
Certificate kinds differ: curves must not be described as formula proofs.
Discovery assessment was 42/45/47/43 of 48, versus 36/39/39/41 for the off control;
these gaps are within the observed spread. Recorded false credit was zero.
This does not establish an autonomous-discovery gain. Short proposal budgets and
few observations are the current diagnosis, not a verified remedy.

[US3b profile](../sera-runs/us3b-profile-ff5d65a/us3b-summary.txt), eight tasks with
three repeats under concurrent VM load: with readouts and memory enabled, median
item time improved 17.8 to 16.5 seconds; with readouts but memory disabled,
16.0 to 10.5 seconds. All configurations remained at or above the 10-second budget.

U10-U13 are implemented. Their scientist-inspired methods are learned search and
reasoning mechanisms; the names do not establish scientist-level capability.
The saved U10 full arm solved 41/41/42/42 of 48 across g0-g3, versus
36/40/41/37 for its discovery control. Removing the assumption-revision method
scored 47/46/46/47, so the results do not support claiming that every method helps.
These are individual runs, and several other arms stopped early. See the
[U10 summary](../sera-runs/u10-einstein-vma/summary.txt). Complete replicated
comparisons for U10-U13 are pending. Full course and whole-system evaluation
also remain open.

## New U11-U14 evidence

U11's full arm solved 45/45/46/46 of 48, versus 40/40/34/37 for the Einstein
control. Disabling one-change experiments scored 48/47/48/47. Anomaly pursuit
and audited conjectures did activate; the full set found one conserved quantity
and certified three laws. Single-run differences do not establish a benefit.
All full arms finished, while several later arms stopped on caps or repaired bugs.
U10's paradox, invariance and assumption-revision methods did not activate in
its full arm; these methods depend on certified laws, of which discovery found
few. One bold prediction in an ablation failed. Building the methods has not yet
demonstrated their usefulness.

U12's full arm scored 37/43/47/45; its replicate scored 36/39/37/42 of 48.
The same switches differed by up to 10 answers again. Forecast accuracy was
approximately 19-22% per trial in cases with a world picture. Cases built
13-19 likeness trees and 0-3 mechanisms; none of their mechanism predictions
came true. Nearly all ablation gaps were within the observed spread.

A short U9 probe found that six of nine exact worlds lacked the four observations
needed before proposing. In the two reported eligible cases, a 0.5-second search
found nothing while a 2-second allowance found a law, certified by the same judge.
This supports a budget/observation diagnosis in those cases; it does not establish
the efficacy of the redesign.

## U13/U14 completion and failures

U13 full-arm solved counts out of 48 across g0-g3 are 36/42/42/40 (roadmap),
41/47/45/47 (without own operations), 40/39/41/40 (without reconstruction),
47/46/47/46 (Darwin control), and 40/42/42/41 (without rough estimates).
Only the last case completed all arms; the others exhausted their allowance.
There are no replicates in this batch and no established benefit from U13.

Both completed U14 gap cases, seeds 3 and 5, recorded 0/384 eventual exam answers:
each full and no-holes arm answered 0/48 at each of g0-g3. Both recorded zero gaps
found and zero false credit. Finishing a run does not establish question solving.
The seed-5 question-priority case stopped on a receipt-provenance error; its five
saved generation assessments also recorded zero answers (0/240). Its full arm
reached g3, but the comparison did not complete. The seed-3 priority snapshot is
partial, not a completed comparison, and is excluded from these totals.

The [saved-schema summary](../sera-runs/u14-vma/saved-summary.json) preserves exam
generation rows, gap counters, protocol identity, source hashes and stop records.
Legacy generated tables below still show U14 scores as MISSING because the reader
expects `rows`, while these files store `exam` and `holes`. Their U14 habit zeros
are unsupported by that reader and are omitted here. The raw saved exam and gap
counters above are read directly; per-item payloads and full life states stay local.

The development memory log records peaks near 10.9 GB per life, superseding the
earlier 0.7-1.1 GB snapshot. Table-count limits do not bound all retained values.
That memory issue and rejection of the question origin `interaction` remain
unfixed in this source revision. Cross-machine work-clock equivalence is untested.
Implementation code is unchanged in this publication update.

Counted-work U14 budgets differ from earlier wall-clock assessments. Comparisons
require matched work definitions, budgets and suites.

## Earlier incomplete comparisons

The [memory pilot](../sera-runs/u2-ab-f152e14/) completed its first memory-enabled
assessment at 21/48 solved. The memory-disabled run solved 40 of 46 attempted
items before stopping (48 planned). Median item time was 11.3 seconds with memory
versus 1.0 without, against a 10-second budget; median inference was 3.03 versus
0.35 seconds. Of 46 shared items, both solved 15, memory alone solved 5, memory
disabled alone solved 25, and neither solved 1. These are time-confounded results. The cases also froze different observer
suites from their own bootstraps: only partly overlapping items were compared.
They are not a fully matched memory ablation. The newer runner accepts one shared
frozen observer suite across cases. Its newer full-arm comparison is reported
above; replicated confirmation and complete comparisons across all arms remain pending.

In the [later pilot](../sera-runs/u2-ab-96d1d19/), memory disabled solved 39/48
at the first assessment. The memory-enabled case stopped at engineering preflight
because of a test-folder conflict and has no behavioral score.

The [U3/U6/U7 pilot](../sera-runs/u7-ab-5d3ff44/summary.json) found that the
continuation-disabled control proved 22 answers but solved 0/48 within budget:
median item time was about 25.4 seconds and inference about 18.8 seconds.
The continuation-enabled arm proved only 2/12 bootstrap lessons and did not reach
assessment. The bootstrap did not teach its answer/continue choice, so this is
not a fair efficacy test of U7. The control later stopped on an unsupported
dream-input bug, subsequently fixed in the source.

Other interrupted pilots and their stop records remain in the evidence directory.
These earlier pilots did not complete. Newer full-arm generation curves are
available above, but a completed full course or 12-arm comparison is unavailable.
Their noisy scores do not establish consistent self-improvement. Zero placeholders for unattempted generations
must not be interpreted as measured performance.

## Run and inspect

From `lab/`, after installing the dependencies in the [README](../README.md):

```sh
python scripts/sera_u_course.py --help
python scripts/sera_bakeoff.py --help
python scripts/crutch_ledger.py --help
python -m pytest -q tests/sera_u
```

The comparison runner freezes suite identities before teaching. External datasets,
books and saved binary Fields are not bundled. Full courses need substantial time;
running a smoke course does not reproduce the reported comparisons.

The [design](../SERA_U_PLAN.md) defines the intended system. The older discovery
lab's [status](SERA_STATUS.md) records separate experiments and their limitations.
