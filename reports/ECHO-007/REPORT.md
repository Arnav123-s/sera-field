# ECHO-007: reversible learning inside the continuing SERA owner

I implemented complete reversible credit for the Clifford/sheaf field, trained it
through the existing multi-subject learner, evaluated it on fresh source groups
and simulations, and independently replayed all four assessed owners. The new
owner passed every prospectively defined qualification gate. It is packaged at
`checkpoints/ECHO-007` and usable through the same five task interfaces as SCFE-004.

The measured engineering result is a field-gradient computation whose saved
tensors stay constant with integration depth. At 32 steps it retained 12,320
bytes, compared with 73,808 bytes for ordinary differentiation of the identical
field: **83.3% less saved field storage**. The echo and exact-gradient training
arms produced almost identical assessed behavior. This is the relevant validation
of the new learning mechanism.

The original SERA repository, paused laboratories, SCFE-004 default, prior reward
policy and every earlier study remain preserved. This was direct local work.

## Sources and mathematical construction

I read both latest attachments completely. The first is a reformatted copy of
the expanded THDFT proposal; the new twelve-section synthesis is distinct. Their
original bytes, hashes and manifests are preserved. The missing equations in the
first copy were recovered from the earlier unchanged original, not invented.
[Reconciliation](REQUEST_RECONCILIATION.md), [recovered equations](RECOVERED_EQUATIONS.md),
and the [new synthesis audit](NEW_SYNTHESIS_AUDIT.md) distinguish source proposals,
mathematical assumptions and implemented operations.

The action couples eight nodes carrying eight Cl(3,0) grades through trained
rotor restrictions, a prior, source terms and a quartic potential. I introduced
canonical positions and momenta and used symmetric velocity Verlet for 32 steps
of 0.025. Fixed parameter coordinates accumulate conjugate momentum. Two opposite
terminal error impulses, each of size 0.0001, followed by reversed dynamics yield
credit for the source, restrictions, prior, stiffness, quartic strength and both
initial canonical states. The prior's two roles are summed correctly.

The [derivation](DERIVATION.md) specifies signs, coordinates and update order.
The implementation uses float64 internally and float32 at the owner interface.
It saves initial coordinates and final canonical state rather than an unrolled
trajectory. Ordinary local differentiation still handles the input encoders,
readouts and the restriction-to-rotor chain rule. Optimization follows the
reversible pass. The finite perturbation is checked numerically; it is not
silently treated as an exact derivative for every perturbation size.

This separates the reversible operation from the source's Euclidean gradient
flow and from dissipative memory proposals. It also leaves a precise next
contract for timed-input recurrent echoes, rather than equating a terminal-loss
operator with the whole sequence-learning proposal.

## What was taught and what changed

Three arms started from exactly the same qualified, locally trained weights:
echo credit, ordinary differentiation of identical dynamics, and detached field
features. Each completed **2,048 updates of 24 examples**: **49,152 presentations**
per arm, or **147,456 across the comparison**. The arms received the same ordered
curriculum. Repeated records and matched comparison copies are not new data.

| Teaching track | Full run presentations per arm | Selected checkpoint presentations |
|---|---:|---:|
| Human source reading | 16,392 | 8,208 |
| Human mathematics | 8,208 | 4,104 |
| Calculus source associations | 1,776 | 888 |
| Human conversation associations | 1,752 | 888 |
| Descartes source associations | 1,752 | 888 |
| Grammar source associations | 1,752 | 888 |
| Plato source associations | 1,752 | 864 |
| Human program associations | 1,752 | 864 |
| Webster dictionary associations | 1,752 | 864 |
| Labeled physical simulations | 12,264 | 6,120 |

Each full arm encountered **30,346 distinct human records**. Development selection
chose update **1,024** in all three arms; later work through 2,048 remains saved.
The selected echo weights encountered 16,305 human records in this continuation,
of which **3,745 were new to their retained parent**. The complete retained lineage
therefore contains **78,746 distinct human records**, plus the separately recorded
physical curriculum. [Exposure and lineage](LEARNED_STATE.json) provide the exact
selected/full distinction and immutable source-manifest identity.

These are unchanged human-source training views and explicitly labeled simulated
systems. Source associations train a measured retrieval/matching task; consuming
philosophy or program records is not silently counted as independently generating
a philosophical interpretation or writing an arbitrary program.

The field's actual rotor coordinates, prior, stiffness and quartic strength all
changed. Their selected L2 changes were respectively 0.037613, 0.077214, 0.019313
and 0.001496. These changes were zero in the detached-field control. Input and
readout learning remained active in that control. All weights originate in this
independent lab; this cycle continued its learned history without importing a
pretrained backbone or restarting earlier training.

The independently rewarded investigation policy from SCFE-006 was retained
exactly. This cycle trained teaching credit, not a new reward policy. In the
checkpoint metadata, `step: 1024` counts these teaching updates; `updates: 0`
counts new reward updates in this continuation. The earlier policy's 753 learned
reward updates remain in its provenance.

## Fresh evaluation and retained abilities

I froze all selected file and weight identities together before opening the new
evaluation. Source groups already opened by CONNECTED-003 were excluded, including
unused tails of those groups. Human development, training and final partitions
retain the existing duplicate exclusions. All four owners received the same
cases. No final result was used to alter training or checkpoint selection.

| Measurement | Preserved parent | Echo | Exact-gradient control | Detached-field control |
|---|---:|---:|---:|---:|
| Reading evidence accuracy, 512 questions | 70.12% | **71.09%** | 71.09% | 71.09% |
| Evidence within first three choices | 92.77% | **92.97%** | 92.97% | 92.58% |
| Arithmetic continuation correct in first proposal, 256 cases | 11.72% | **12.50%** | 12.50% | 12.50% |
| Arithmetic continuation correct within five proposals | 38.67% | **40.23%** | 40.23% | 39.84% |
| Conversation matching accuracy, 64 cases | 29.69% | **32.81%** | 32.81% | 35.94% |
| Dictionary matching accuracy, 64 cases | 67.19% | **65.63%** | 65.63% | 67.19% |
| Physical response MSE, 512 systems | 0.107977 | **0.106413** | 0.106413 | 0.106421 |
| Trajectory MSE, 128 independent checks | 0.052775 | **0.048611** | 0.048611 | 0.048925 |
| Original-goal MSE after investigation, 256 systems | 0.067761 | **0.067693** | 0.067693 | 0.067993 |

Echo trajectory error was **7.9% lower than the parent on these matched cases**.
Reading improved by five correct answers out of 512. The detached control is close
to the echo owner, with stronger results on some matching measures. The evidence
supports a working reversible credit mechanism and retained finite abilities;
it does not isolate a large new behavioral gain from field credit. This is one
matched seed and curriculum, not a ranking of broadly trained architectures.

All 256 arithmetic cases were teacher-forced human-solution continuations. The
fresh cohort contained zero eligible original one-step questions. Only conversation
and dictionary tracks still had untouched eligible final source groups; previous
grammar, philosophy, calculus and program finals were not reopened. Development
results for those tracks remain in the three complete training records. Reading
scores here and the older 76.95% result concern different cohorts; they should not
be subtracted to infer forgetting.

In the echo investigation cases, mean error changed from **0.141489 to 0.067693**
after one observation: a **52.16% reduction**, with improvement in 159/256 cases.
Every original goal received a returned answer. Six actual-actuation mismatches
were recorded. The observation, predictor, action and original-goal identities
remain bound in each raw record. Weight identities stayed unchanged throughout
assessment. The policy was not given additional reward training on this final.

Every owner completed 128 trajectories assessed by an independent DOP853 solver.
The [decision](DECISION.json) passed all eight frozen checks, including aggregate
pair-loss retention, independent replay and agreement with the exact-gradient
control. The new owner is a **qualified optional successor**.

## Verification, memory and full supervised costs

The complete engineering suite passed **93 tests**, including reversal, all seven
gradient groups, independent finite differences, the tied initial-prior path,
source immutability, actual reading-loss gradients, detached credit and exact
next-update recovery in a fresh interpreter. Every final metric and raw-record
identity replayed exactly in **four separate owner replays**. The executed five
CLI interfaces also all reported the same packaged weight identity.

| Integration steps | Echo saved field tensors | Exact-gradient saved field tensors |
|---|---:|---:|
| 4 | 12,320 bytes | 14,672 bytes |
| 16 | 12,320 bytes | 40,016 bytes |
| 32 | 12,320 bytes | 73,808 bytes |
| 64 | 12,320 bytes | 141,392 bytes |

These measurements count unique retained tensor storage for one eight-node,
eight-grade, batch-one field call. They exclude the encoder/readout tapes,
optimizer, temporary arrays and branch/process memory. Echo costs one forward
and two reversed trajectories; this table makes a storage claim, not a speed
claim. The whole packaged model has **863,148 parameters**, **3,452,592 parameter
bytes**, and a **3,466,853-byte checkpoint**. This does not relabel the complete
model as the proposal's small core-state budget.

All five supervised attempts passed. Together, contracts, full training,
development, final assessment, replays, storage/lineage audit and delivery took
**890.940 wall seconds** and **870.750 CPU seconds**. Peak committed process-tree
memory was **1,520,812,032 bytes** under the **2 GiB cap**, with one numerical CPU
thread and no paid compute. These are supervised numerical costs; research,
editing and documentation time are separate. Every attempt is in [COSTS.json](COSTS.json).
Earlier unsuccessful studies and their costs remain in their original reports.

## Use and audit the saved owner

From `D:/ai/labs/sera-field`, with a fresh attempt name:

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt echo-reading-001 -- -m sera_field.learned_cli --training checkpoints/ECHO-007 read --question "What did Alice see?" --source examples/reading-practice.txt
```

The same `--training checkpoints/ECHO-007` option works for `math`, `imagine`,
`investigate` and `motion`. [Task commands](../../docs/CONNECTED_USAGE.md) describe
their inputs. The default remains the preserved SCFE-004 owner.

[Recorded interface outputs](USAGE_EXAMPLES.json) are usage fixtures, not new
capability tests. The reader ranked the flower sentence first. The arithmetic
fixture placed the correct value 8 fourth among five proposals and placed the
incorrect value 10 first; both outputs are preserved. Exact execution verifies
the proposed arithmetic, while correspondence to the question remains separately
checked. The other interfaces returned three conditional response hypotheses,
a proposed observation and three completed imagined trajectories.

Packaged file SHA-256:
`b8428610ee13211547ee83f9c741cc01c9fcd5581b8a10f25cb6f5b2e14d4ae1`.
Learned weight SHA-256:
`6bb452bbb714d068925180aacc03cbc48ef296410361ceb990e1c50edd291a85`.
The full selected training state, optimizer, random state and later revisions
remain under `runs/ECHO-007/echo/revisions`. The [manifest](../../checkpoints/ECHO-007/MANIFEST.json)
links the small inference package to its assessed training state.

[Frozen protocol](../../protocols/ECHO-007.md), [source freeze](FROZEN.json),
[joint final registration](FINAL_REGISTRATION.json), [evidence hashes](EVIDENCE_INDEX.json),
[complete checklist](CHECKLIST.md), [paper coverage](PAPER_COVERAGE.md), and
[new synthesis audit](NEW_SYNTHESIS_AUDIT.md) make the implementation reviewable.

## Next executable research gate

The next capability gate is the synthesis's five-way reuse of **one acquired
relationship**: forward prediction, inverse inference, changed assumptions,
goal-directed intervention and grounded language. Freeze a new observed-system
cohort; bind the same acquired state to all five paths; withhold task-specific
teaching after acquisition; and check actuation plus independently measured
outcomes. A calibrated force channel must distinguish mass from force scale.
That measures the connection the user wants instead of treating five separate
interfaces as proof of shared conceptual transfer.

Timed-input RHEL requires a separate persistent position/momentum sequence
operator with reversed input/loss scheduling and interruption replay. SPD
transport, Cahn-Hilliard capture, Schubert/ERG growth and topological semantic
memory each have explicit mathematical and behavioral acceptance contracts in
the new synthesis audit. They remain preserved research directions, not renamed
versions of the already implemented components. Completed ECHO-007 finals are
sealed against further tuning; new work starts with a prospective protocol.
