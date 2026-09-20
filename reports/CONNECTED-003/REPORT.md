# Connected SERA: human teaching, imagined consequences and qualified investigation

The independent lab now contains a usable **SCFE-004 owner with the qualified
SCFE-006 investigation policy**. It learns source evidence selection, constructs
arithmetic proposals, associates human program/text examples, infers physical
responses from observations and transfers those responses into trajectories.
Independently checked progress trained its decision weights. Development-based
policy retention repaired an unsuccessful final-step candidate without changing
the completed final evaluation or restarting training.

I performed this work directly in `D:/ai/labs/sera-field`. Production SERA remains
clean at `0dcbcb902706f3d299cd38a433fcf1f26a357efd`; the paused AG/CC laboratories,
FIELD-001, older checkpoints and unsuccessful work remain preserved.

Start with [usage](../../docs/CONNECTED_USAGE.md),
[the packaged owner](../../checkpoints/SCFE-004/MANIFEST.json),
[the post-build research audit](POST_BUILD_AUDIT.md) and
[the latest-paper comparison](LATEST_ECOSYSTEM_AUDIT.md).

## What changed

Fresh word/phrase and observation encoders feed one learned situation field per
owner. The field participates in reading, arithmetic and empirical-world
computation from the first teaching update. There is no imported model backbone
and no next-token training objective. Source labels remain separate from inputs;
whole passages are encoded without prefix clipping.

CONNECTED-003 uses the finite SU(2) field. SCFE-004 uses genuine Cl(3,0)
multivectors, rotor-induced transport and the adjoint graph-sheaf action, with a
trained prior and explicit quartic potential. The full owners have 889,213 and
863,148 parameters respectively. Their geometric link weights actually changed;
SCFE's link-coordinate change from initialization has L2 norm 0.33157.

The model infers three physical coefficient hypotheses from measured support,
predicts requested consequences and scores possible observations. Its decision,
goal and predictor are recorded before independent outcomes. Reward is signed
verified improvement; failed actuation receives no credit. Canonical contribution
identities prevent renamed goals from renewing novelty bonuses.

## Teaching and source exposure

Both owners started from their own recorded initialization and completed the
same 12,288 attempted minibatches of 24 examples: **294,912 presentations each**.
This is 589,824 presentations across two models, with repeats and shared source
cases. It is not that many distinct examples.

| Teaching track | Presentations per full run |
|---|---:|
| Human reading comprehension | 98,304 |
| Human arithmetic annotations | 49,152 |
| Independently generated physical systems | 73,728 |
| Calculus material | 10,536 |
| Human dialogue turns | 10,536 |
| Descartes | 10,536 |
| Grammar | 10,536 |
| Plato | 10,536 |
| Human programming material | 10,536 |
| Webster dictionary entries | 10,512 |

Each whole run encountered **102,408 distinct human records** and 73,728 distinct
simulated systems. Source identities, source notices and unchanged raw human text
stay in the local curriculum manifests. Simulation and engineering fixtures are
explicitly separate from human material. Exact duplicate inputs crossing source
partitions were quarantined: 3,096 clusters, with original bytes retained.
Article/dialogue/book-block groups do not cross partitions.

Development selection retained CONNECTED-003 at update 7,168 and SCFE at 6,144;
all later training and costs remain preserved. The **released SCFE predictor**
therefore saw 147,456 presentations, including **75,001 distinct human records**
and 36,864 distinct simulated systems. Its exposure includes 49,152 reading and
24,576 arithmetic presentations; complete per-track counts are in
[the audited learned-state record](LEARNED_EVIDENCE.json).

The same source file and curriculum are used across owners, but selected
checkpoints contain different numbers of updates and complete parameter counts
differ. This one-seed study records component behavior, not a broad ranking of
architectures.

## Frozen human and physical evaluation

Both teacher selections and reward arms were jointly registered before opening
the original final cohorts. No model changes or re-selection used these scores.

| Assessment | SCFE-004 | CONNECTED-003 | Cases |
|---|---:|---:|---:|
| Correct evidence sentence | 76.95% | 77.15% | 1,024 |
| Evidence among first three choices | 94.53% | 95.12% | 1,024 |
| Numerically correct arithmetic, first proposal | 10.94% | 13.48% | 512 |
| Numerically correct arithmetic within five proposals | 38.67% | 38.09% | 512 |
| Human expression matched within five proposals | 34.38% | 34.77% | 512 |
| Human program association | 81.82% | 84.85% | 33 |
| Dictionary association | 62.11% | 59.77% | 256 |
| Dialogue association | 40.23% | 42.58% | 256 |
| Grammar association | 41.41% | 47.47% | 99 |
| Plato association | 39.58% | 41.67% | 48 |
| Calculus association | 52.63% | 42.11% | 38 |
| Acceleration MSE | 0.106818 | 0.106876 | 256 systems |
| Transferred trajectory position/velocity MSE | 0.057239 | 0.054021 | 64 systems |

All 64 trajectories per owner completed. They use learned acceleration
hypotheses through RK4; separately implemented DOP853 supplies the checked
outcomes. The learner was taught acceleration targets, not these trajectories.

Association tasks have four candidates from their source track. They measure
association, separately from program synthesis or deep interpretation. Most
arithmetic records are continuations with explicit earlier human calculations;
only three eligible original one-step questions occur in this sampled cohort.
SCFE's first answer matched one of those three, and its first five contained the
correct expression on two. Descartes was taught but has no held-out partition in
this block split. Exact arithmetic execution certifies the program's calculation;
its interpretation of the word problem still requires checking.

The lexical reading control scored 77.93%. SCFE scored 76.37% with settling
disconnected and 76.76% with the loop feature disconnected, versus 76.95% normally.
These are inference sensitivities, not separately trained architecture controls.
They provide a concrete measure of the current field's contribution to this task.

## Reward experiment, failure and repair

Each owner received 2,048 reward-training investigations and 2,048 matched
reward-disconnected investigations. Each rewarded arm made 2,011 weight updates
and rejected 37 actuation-mismatch assessments. SCFE recorded 1,102 positive and
909 negative rewards; the field variant recorded 1,168 positive and 843 negative.
Only 15 canonical probe contributions earned novelty bonuses. The disconnected
arms retained all policy weights, with equal attempted episodes and outcome access.

The first fixed final assessment retained this result:

| Owner | Initial goal MSE | After rewarded policy | After unchanged policy | Decision |
|---|---:|---:|---:|---|
| CONNECTED-003 | 0.109967 | 0.064270 | 0.072348 | Measured reward benefit in this cohort |
| SCFE-004 | 0.111868 | 0.100924 | 0.075173 | Preserve the final-step policy; do not promote it |

All 256 cases per owner returned the original goal. This first SCFE result was
not erased or retuned. The follow-up hypothesis was that retaining the last
stochastic update lacked a policy-generalization gate.

**SCFE-006** froze all 17 saved policy identities at attempts 0,128,...,2048 and
assessed each on a new 512-system development cohort. No teaching or reward
training was restarted. Minimum development MSE selected the policy from attempt
**768**, containing **753 actual learned weight updates**. A separate, untouched
512-system final cohort then produced:

| Investigation policy | Mean MSE after its observation | Reduction from the original answer |
|---|---:|---:|
| Selected learned policy | **0.066335** | **39.50%** |
| Unchanged policy | 0.080302 | 26.76% |
| Last training update | 0.101377 | 7.54% |
| Random observation | 0.083276 | 24.05% |
| Analytic information control | 0.048418 | 55.84% |

The selected policy improved mean error by **17.39% relative to its unchanged
control**, exceeding the predeclared 5% requirement. The paired 95% bootstrap
interval for absolute MSE improvement was **[0.005947, 0.023012]**, passing the
predeclared positive-lower-bound gate. All 512 original goals returned answers.
The result and every raw record replayed exactly in a new interpreter.

This qualified policy is integrated into the packaged owner. Every non-policy
parameter is bit-identical to the selected SCFE teacher, preserving its reading,
mathematics and world predictor. Policy selection is my engineering contribution;
the decision weights were acquired by SERA's checked reward updates. A stronger
analytic control remains documented without changing the project's design goal.

## Preserved errors and exact scope

The original omitted-mechanism diagnostic is retained: SCFE mean MSE increased
from 0.494180 to 0.674116 after investigation, while its mean model spread was
only 0.026512. This is evidence to improve model adequacy and representation
growth; it is not a claim about all future SERA capabilities. The finite physical
basis and observation menu were supplied. Learned hypotheses remain conditional.

The unchanged usage fixture also preserves an arithmetic error: for five apples
plus three, SERA ranked programs producing ten above the correct addition,
which appeared fourth. I did not retune on this demonstration or label correct
rational execution as correct word-problem interpretation. The same owner
selected the flower sentence in the reading fixture, proposed a new physical
measurement and produced three trajectory alternatives. All five CLI outputs
are in [the usage record](usage-examples.json).

## Latest paper and reversible-learning qualification

The newest attachment is distinct from the older saved texts. Its shift toward
cohomology-based growth, Hamiltonian echoes, biological capture and anyonic
operators is recorded in [the latest-paper audit](LATEST_ECOSYSTEM_AUDIT.md).
Its typed geometry is already in the freshly trained owner.

ECHO-005 implements a separate reversible canonical flow using the same sheaf
potential. Four tests pass: full-state reversal, prior-gradient agreement with
autograd and parameter finite differences, a damping counterexample and source
immutability. The numerical operator qualifies the next learning-method gate;
it does not silently replace the dynamics inside the already trained model.
All original and latest mechanism/behavior rows are reviewed in
[the post-build audit](POST_BUILD_AUDIT.md).

## Integrity, costs and use

- 80 integrated engineering tests passed; four additional echo contracts passed.
- Both original owners' final records and the selected policy's fresh final
  records independently replayed exactly.
- The five actual CLI tasks use the identical packaged weight identity.
- **63.58 supervised wall minutes**, **62.30 CPU minutes**, peak committed
  process-tree memory **1,515,155,456 bytes**. One numerical CPU thread, a 2 GiB
  cap and no paid compute. All original, repair, selection and replay costs count.
- Numerical leases are released; no jobs are delegated or scheduled. Earlier
  interrupted delegated costs remain explicitly marked as a lower bound.

Full machine-readable evidence: [learned state](LEARNED_EVIDENCE.json),
[original SCFE results](evaluations/scfe/RESULTS.json),
[policy qualification](policy-qualification/RESULTS.json),
[policy replay](policy-qualification/REPLAY.json),
[artifact identities](EVIDENCE_INDEX.json), [all costs](COSTS.json).
Raw case journals, source identities and all resumable revisions remain under
the lab's `runs/` and private curriculum directories.

The release has **863,148 parameters**, 3,452,592 parameter bytes, and a 3,466,597-byte
inference file. This is distinct from its 256-byte single field state and from
training activation/optimizer/process costs. The inference copy excludes raw
corpus text; complete resumable training and credit state remain preserved.

From the lab directory:

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt my-reading-001 -- -m sera_field.learned_cli read --question "What did Alice see?" --source examples/reading-practice.txt
```

[The usage guide](../../docs/CONNECTED_USAGE.md) includes your own source files,
arithmetic, observation selection, conditional worlds and trajectories. The next
research gate extends reversible credit to the remaining inputs/parameters and
connects one acquired concept across the paper's five task views, using fresh
protocols and untouched cohorts.
