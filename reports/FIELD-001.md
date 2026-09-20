# FIELD-001 — from-scratch shared physical field

I trained a new field core from fresh initial weights, reused its learned physical mechanism across four task views, and trained an evidence-qualified correction. The original SERA repository and owner remain intact. This report distinguishes supplied structure, learned weights and independently checked outcomes.

## Training and evidence

Twelve base models (four mechanisms × three seeds) and six residual successors each received 3,000 optimizer updates: **54,000 gradient updates and 6,912,000 minibatch query presentations** in total. Each minibatch contained 128 queries. There were 8,192 unique base observations and 8,192 refinement windows containing six supports and one query: **65,536 unique physical observation records** in the gradient curriculum. Repeated presentations are not counted as new observations.

The data are generated physical diagnostic observations. Central differences of simulated positions supply velocity and acceleration targets. Calibrated mass and actual force are inputs. The simulator formula, hidden resistance coefficient and query outcome are excluded from the model's context inputs. Pauli features, the equivariant vector basis, context statistics, training families and task algorithms are supplied engineering. Coefficient functions and residual responses are learned.

All twelve base initializations were reconstructed exactly from seeds 11, 29 and 47. Initial SU(2) tensors changed during training. Every saved intermediate checkpoint, loss curve, optimizer state, sampler state and RNG state is in the evidence archive. The base is frozen inside each successor. Twelve split collections have distinct content identities and zero duplicate input rows across all 66 pairwise comparisons.

Checkpoint selection used development data only. A stronger invariant control and two qualification studies were frozen before the final marker was opened. The final mixture had **664 novel-context and 360 vacuum queries**; the frozen prose has one conflicting count, documented in the [post-build audit](../docs/POST_BUILD_AUDIT.md). No additional cases were added to alter these results.

## Matched neural controls

All base candidates have 783 trainable scalars, matched data, updates, optimizer and seeds. The table reports the mean of three initializations. NMSE is mean squared acceleration error divided by target mean square; it is not a classification accuracy. Lower is better.

| Mechanism | Interpolation NMSE | Rotated NMSE | Mass-extension NMSE | Plan successes by seed | Inverse mass mean relative error |
|---|---:|---:|---:|---|---:|
| SU(2) field | 0.0005453898 | 0.0006169254 | 0.01910843 | 23/24, 23/24, 23/24 | 2.680% |
| Symmetry-broken field | 0.0007030065 | 0.001535406 | 0.02287909 | 22/24, 22/24, 22/24 | 2.842% |
| Raw-input classical network | 0.001400199 | 0.05275042 | 0.1186114 | 9/24, 9/24, 8/24 | 12.897% |
| Invariant classical network | 0.0001212487 | 0.0001446606 | 0.001729821 | 24/24, 24/24, 24/24 | 1.351% |

Interpolation and rotation each use 2,048 cases, and mass extension uses 1,024 cases. The 128 cross-use cases are a subset of the rotated cohort. Planning uses the same 24 cases across mechanisms and seeds: the three repeats are not 72 independently sampled tasks. Success requires both endpoint distance and speed below 0.05 simulator units after one second. A separate DOP853 solver checks applied controls.

The SU(2) field improved transfer relative to the symmetry-broken and raw-input controls. The invariant classical network achieved lower errors and all 24 planning successes in each initialization. These results support the value of the supplied physical invariants on this task; they favor the simpler invariant network over the tested group-link network for this vacuum family.

A separate strong classical control receives a supplied isotropic power-law family and fits two coefficients to the same 8,192 observations. It recovers a mass exponent of -1, reaches rotated NMSE about 3.34e-15 and passes 24/24 plans. Its stronger equation-family prior and least-squares fit differ from neural training; it is recorded as a mechanism control, not hidden or presented as independent discovery.

## Reuse of the learned field

| Field seed | Mean forward position error | Mean inverse mass relative error | Mean half-mass position error | Half-mass median position error |
|---|---:|---:|---:|---:|
| 11 | 0.010583 | 2.804% | 0.109721 | 0.018422 |
| 29 | 0.013048 | 3.122% | 0.133947 | 0.018308 |
| 47 | 0.009834 | 2.114% | 0.136936 | 0.013394 |

All four task views use the same checkpoint with zero task-specific weight updates. Inverse inference and control optimization are engineered algorithms operating through the learned function. Of the 128 half-mass cases, 28 move below the taught mass range; these cases remain in the aggregate and explain why the tail must be reported alongside the median. Full maxima and 95th percentiles are in `FIELD-001/summary.json`.

## Acquired correction and retention

The residual curriculum adds nonlinear velocity-dependent resistance. At inference, six measured support outcomes summarize the context; a seventh query outcome is withheld from the predictor. Development selection chose the wider successor for seeds 11 and 29 and the smaller one for seed 47. No final selection changed this choice.

| Seed | Width | New-context base MSE | Qualified MSE | Reduction | Vacuum base MSE | Qualified vacuum MSE |
|---|---:|---:|---:|---:|---:|---:|
| 11 | 28 | 0.2344958 | 0.0163303 | 93.036% | 0.0005417 | 0.0005426 |
| 29 | 28 | 0.2325722 | 0.0165686 | 92.876% | 0.0007369 | 0.0007521 |
| 47 | 12 | 0.2335880 | 0.0219553 | 90.601% | 0.0005454 | 0.0005521 |

The raw residuals increased vacuum MSE to 0.00755, 0.01311 and 0.02466. The first energy-only compatibility test failed two development qualifications. The replacement uses the mean and covariance of measured residual statistics, calibrated on fresh vacuum observations, and a separately checked threshold. Final familiar-context MSE stayed within 2.06% of the base across all seeds. With no new context, the successor returns its byte-identical retained base. This protection is explicit, not an inferred guarantee of topological memory.

Each selected successor then faced a fresh chosen intervention. A fixed disagreement-per-cost policy compared alternatives, applied a force and checked the outcome with DOP853. All three improved their original-goal response and earned one evidence-bound credit. Duplicate credit was rejected, and a separate 25% actuator attenuation was detected in each case. Credit is recorded verification; no policy-weight update is claimed in this cycle.

## Actual task demonstration

The designated seed-11 field predicts position 0.49943 after one second for mass 2 under force 2, and 1.01341 when the mass is changed to 1. It estimates mass 1.93346 from force 2 and acceleration 1. For a target displacement of 0.20, it proposes forces +1.65669 and -1.69002; independent simulation reaches 0.20500 with final speed 0.00833. The original situation and weights remain unchanged. These examples and their full identities are in `FIELD-001/demo.json`.

## Verification and costs

The final contract suite passes **29 tests**, including actual link-weight updates, local-frame operations, expansion identity, retained weights, branch integrity, reward integrity, context leakage protection, checkpoint reload and task-interface regressions. Fresh-process replay matches every serialized final value and case exactly. The earlier replay comparator failure is preserved: tuple/list normalization was an engineering repair, not a numerical tolerance or model change.

All supervised numerical attempts consumed **20.157 wall minutes and 19.869 CPU minutes**. Peak committed process-tree memory was **425.12 MiB**, below the 2 GiB cap. One numerical CPU thread was used. Costs include both replay attempts, failed scientific candidates, all tests and the packaged CLI smoke check. No paid compute was used. Reading, engineering, downloads and packaging are outside these measured numerical totals.

The summed model-fit wall times across three seeds were 51.29 s for the field, 49.41 s for the broken-symmetry field, 11.20 s for the raw-input network and 14.02 s for the invariant network. Equal updates did not imply equal computation. Residual training and evaluation costs are also included in the full supervisor ledger.

Base tensors occupy 3,132 bytes. The selected qualified owners occupy 9,308 bytes for seeds 11 and 29, and 6,748 bytes for seed 47, including calibration buffers. These figures exclude optimizer state, serialized evidence and temporary allocations; the measured process-tree peak is reported separately.

## Retained deliverables and continuation

[Evidence index](INDEX.md) · [Usable commands](../docs/USAGE.md) · [Source audit](../docs/POST_BUILD_AUDIT.md) · [Exact costs](COSTS.json) · [Continuation state](STATE.json). All failed qualifications, comparison weights, initializations, intermediate checkpoints and scientific results remain available. The next capability package is a from-scratch human-language-to-situation encoder, retaining field and invariant classical controls and using fresh prospective cohorts. FIELD-001 finals stay closed to further tuning.
