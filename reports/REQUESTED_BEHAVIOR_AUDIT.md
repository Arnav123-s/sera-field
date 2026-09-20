# Audit of the requested understanding, imagination and reward behavior

Audited implementation: `c88820e349e0b0cb84af5b89df4ecf4041967d37`. I reread the complete attached proposal and the user's behavioral description, then traced the implementation, training updates, saved evaluation and reward call sites. This audit performs no new training and does not reopen FIELD-001 for selection.

**The complete requested architecture and behavior were not implemented or tested.** FIELD-001 trained a useful physical component and checked its task interfaces. Its 29 passing tests are implementation and finite physical-behavior checks; they are not 29 validations of the complete vision.

## What was learned and what was supplied

| Requested behavior | Evidence in the new lab | Actual status |
|---|---|---|
| Fresh weights using the research-inspired representation | Saved initial tensors, exact seed reconstruction and changed SU(2) connection weights | Implemented and trained |
| Use retained knowledge in several ways | The same acquired acceleration function supports motion, inverse mass, changed-mass rollouts and control search | Demonstrated for the supplied physical curriculum |
| Imagine consequences | Learned dynamics drive numerical trajectories; factual situations and weights remain unchanged | Conditional numerical imagination tested; the integrator, task and modified variables are supplied |
| Notice its own missing understanding | A supplied curriculum introduces resistance; measured support residuals help condition a supplied successor family | Acquired correction tested; self-originated question and gap construction remain open |
| Discover new mechanisms from its own questions | The teacher supplies the physical family and training distribution; the model learns its response functions | Independent construction of a previously unsupplied mechanism was not tested |
| Generate many distinct methods or explanations | Evaluation compares two already-trained predictors and deduplicates their predictions | A learned, diverse candidate generator remains open |
| Choose investigations | `choose_probe` ranks twelve supplied controls using a fixed disagreement/cost formula | Automatic numerical selection exists; the investigation policy is not learned |
| Reward verified progress | Three post-training interventions receive independent-error-reduction credit; duplicates are rejected | Verification/accounting implemented |
| Become better because of reward | `CreditBook.award` writes a Python record; no training update consumes that reward | Reward-to-learning connection remains open |
| Persistent reward over a lifetime | Each evaluation cycle creates a fresh `CreditBook`; results are saved in reports | A resumed, cross-quest reward/update ledger remains open |
| Understand language as a situation | Current input is explicit numerical state; the returned explanation is a fixed string | Learned language grounding, reference and interpretation remain open |
| Imagine another person's perspective | Coordinate rotations are tested | Observer beliefs, perception, intent and practical empathy were not assessed |
| Understand poems, philosophy and different meanings | No such training curriculum or held-out assessment in this new lab | Teaching and testing remain open |
| Improve its own learning methods | Adam, the curriculum, context features and investigation rule are supplied | Independent learning-procedure improvement remains open |

The trained field does more than reproduce stored answers: it learns a numerical function and applies it to unseen physical inputs and several task views. That is the measured result. It is not the full self-directed scientific and semantic behavior requested.

## Exactly what happened to rewards

The model training completed before the final intervention cycle. The training loss in `sera_field/training.py` is physical prediction MSE; its Adam update does not read reward records. The planner optimizes proposed forces, not the predictor's weights or a learned curiosity policy.

During `evaluation.investigation_cycle`, both the base and the successor are already trained. The fixed policy chooses a control. A separate simulator checks the outcome. `CreditBook.award` computes `max(0, before_error - after_error)`, binds that number to the goal and predictor identities, and saves it in the result. It neither backpropagates nor changes any learned investigation procedure.

| Seed | Recorded verified credit | Duplicate credit | Reward-driven policy updates |
|---|---:|---|---:|
| 11 | 0.0000269088144478 | Rejected | 0 |
| 29 | 0.0000261907871391 | Rejected | 0 |
| 47 | 0.0000190866203411 | Rejected | 0 |

The credit is genuine checked error reduction between those predictors, but it is not evidence that the preceding choice taught a new procedure. The candidate correction was acquired before the probe. The current duplicate guard applies within that particular `CreditBook` instance; there is no demonstrated cross-restart anti-replay learning ledger in this new lab.

## Coverage of the pasted architecture

The attachment proposes THDFT: a transient gauge boundary, a persistent effective-action bulk, topological knowledge, holographic coupling, renormalization-driven representation growth and curvature-based eligibility consolidation.

FIELD-001 implements Pauli representations, learned SU(2) links, invariant physical features, residual learning and explicit ownership/verification contracts. A Wilson-loop utility is tested, but it is not a feature extractor in the trained forward path. The effective-action bulk, coupled boundary/bulk PDE solver, holographic reward bridge, learned representation-birth mechanism and derived curvature eligibility update are not implemented. Fixed and wider residuals are constructed by the training script; their existence is not autonomous representation discovery.

These are concrete implementation gaps, not claims that the proposed direction can never work. The mathematical definitions and behavior tests still need to be developed. The existing [post-build audit](../docs/POST_BUILD_AUDIT.md) records where the finite interpretation departs from the literal proposal.

## Correction to the work's acceptance criterion

The user's priority is the integrated behavior, irrespective of whether a classical control scores higher. I retain comparative evidence as a diagnostic and preserve the research direction. I should not make a numerical benchmark the answer to a request for deep understanding and autonomous discovery.

The corrected [behavior acceptance contract](../docs/BEHAVIOR_ACCEPTANCE.md) requires a connected cycle: interpret a situation, identify a gap, generate alternatives, imagine consequences, choose evidence, independently check it, use credit to update a learned procedure, retain the result, and return to the original task. Completion requires held-out evidence for that cycle and its reward effect. Adding another isolated prediction task or accumulating points does not close it.

All earlier SERA work and all FIELD-001 evidence stay preserved. This audit changes scope accounting and research priorities; it makes no new capability claim.
