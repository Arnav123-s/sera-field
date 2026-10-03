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
| US2 batched memory and caches | Merged; completed before/after timing not saved here |
| U3 imagination and inner judge | Merged; hypothetical examples use a separate channel |
| U4 adaptive scrutiny | Merged; disabled by default; acceptance requirements preserved |
| U6 consistency-based curiosity | Merged |
| U7 answer or continue, revisit queue | Merged; requires teaching of the choice |
| U5 course, crutch ledger, 12-arm comparison runner | Merged; full comparison not completed |
| US3 faster faculty readouts | Work in progress; absent from this snapshot |
| U8 learned memory consultation and retention choices | Work in progress; absent from this snapshot |

The local development record reports 204 SERA-U tests passing after U5 and US2.
This is a historical test result; see the publication manifest for checks actually
run on this public snapshot. Test totals from different stages overlap.

## Measured speed

[One-thread CPU benchmark](../sera-runs/us-speed-cpu/speed.json), three repetitions:

| Operation | Before | After | Speedup |
|---|---:|---:|---:|
| Standard training batch | 47.35 s | 5.92 s | 8.00x |
| Varied-query training | 22.74 s | 6.43 s | 3.53x |
| Dream diagnostic | 3.84 s | 0.54 s | 7.16x |

Single reads remained about 2 seconds. The maximum parameter difference after a
training step was 1.16e-5; the optimization was not bitwise identical.

## Incomplete comparisons

The [memory pilot](../sera-runs/u2-ab-f152e14/) completed its first memory-enabled
assessment at 21/48 solved. The memory-disabled run solved 40 of 46 attempted
items before stopping (48 planned). Median item time was 11.3 seconds with memory
versus 1.0 without, against a 10-second budget; median inference was 3.03 versus
0.35 seconds. Of 46 shared items, both solved 15, memory alone solved 5, memory
disabled alone solved 25, and neither solved 1. These are time-confounded results.

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
No completed multi-generation self-improvement curve, full course assessment,
or 12-arm comparison is available. Zero placeholders for unattempted generations
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
