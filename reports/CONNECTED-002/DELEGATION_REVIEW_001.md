# Startup review: repair before accepting sustained training

Status: **the first delegated curriculum implementation does not pass the training
gate**. Preserve its code, runs, checkpoints and costs as development failures.
Do not use their scores as capability evidence or initialize the qualified final
candidate from answer-leaking training without explicitly recording that exposure.
This review concerns the new delegated implementation, not FIELD-001's results.

Inspected source identities before repair:

- curriculum_episodes.py: `3086f6645ac0664126fd25dab480e4e9dbf9e04e12a499282f9d2d7f519cb3c5`.
- sustained_training.py: `e4bd4afe80acdde10144574e005a435e27ea4900bfb8ad1b6fa60b778c0e651b`.

Snapshots and the observed supervised run state are preserved in the source lab's
local/CONNECTED-002-startup-review/. The active attempt observed was
sustained-seed-1103-retry under the actual one-CPU/2 GiB supervisor. No other job
or working tree was stopped or overwritten by this audit.

## Concrete defects

1. **Direct label leakage.** curriculum_episodes.py lines 104-105 set candidate
   feature 2 to one only for the correct language answer. Lines 250-251 mark good
   and bad code candidates as +1/-1. Lines 323-325 similarly mark the preferred
   interpretation. These labels reach the policy input. Remove every
   correctness-dependent input feature. Encode candidate text/programs identically
   through learned inputs; use plausible independently sampled distractors and
   counterbalance candidate order. Add tests that changing a hidden label without
   changing the observed task/candidate content cannot change any learner input.

2. **Source and checker identities are placeholders.** Strings such as
   v_language_ followed by zeros and s_language_ followed by zeros are not SHA-256
   identities of the source/checker. Use actual immutable source bytes, source
   record/group/split identity, transformation version and actual verifier code
   hashes. Verify the frozen human-view manifest. A finite simulated task must be
   labeled simulation, and a humanities rubric must not be labeled a performed
   physical simulation. Restore independently auditable provenance.

3. **Manufactured assessment/novelty records.** Before-loss is set to 1 for every
   episode, evidence/assessment IDs are generated from new decision IDs, and both
   intervention fields contain the literal string intervention. Canonical method
   and assumptions are a stage/choice index. These cannot establish measured
   progress, actual intervention, unique evidence or method novelty. Record a real
   before prediction/answer, proposal-before-outcome commitment, actual observation
   or checker assessment, real action receipt and canonical method/scope. Put
   record_decision before checker execution. Adopt the independently tested
   cross-goal novelty correction in source commit 48e221a.

4. **Attempts are omitted and comparisons are unequal.** stage_updates advances
   only after successful credited changes in the trained arm, but on every
   attempt for controls. Failed attempts have no matching exposure/cost counter.
   Checkpoint/development conditions may repeat indefinitely while the success
   count stays at a multiple of 512. Count all attempted episodes, proposals,
   observations, failures and updates separately; trigger periodic work once per
   attempted-step boundary. Match exposure and evidence budgets across controls.

5. **Resume is claimed but not implemented.** The engine creates a fresh owner at
   entry, uses process-randomized hash(stage_id), and saves only stage/update
   counters, omitting its local Random generator, carried goal memory, replay
   pool, stage cursor, development patience and schedule. initial_weights_hash is
   computed from a newly constructed model at the end, not the real initialization.
   Save the true initialization before training, use stable seeds and implement
   an actual resume entry point. Demonstrate exact next-episode/next-update
   equality after process interruption under the numerical supervisor.

6. **Frozen campaign and actual teaching diverge.** Stage budgets were reduced to
   4,096/6,144 without a recorded prospective amendment, development changed from
   2,048 to 512, and caching silently caps human sources at 2,000 per subject.
   The streaming input still truncates context/question to 128 bytes, often
   dropping the question. Loading mathematics/programming caches does not show
   that those human records actually drive those stages. Connect real views,
   retain the full question/context through streamed memory, log source exposure,
   and follow the campaign allocation or document a justified prospective revision.
   A one-codon or fixed-addition task does not complete a broad science/math track.

7. **Full-loop integration remains unqualified.** Handcrafted options plus a
   correct-index checker do not establish learned proposal construction, detection
   of missing knowledge, informative investigation or a returned original goal.
   Include the learned proposal/investigation path in actual training, retain
   competing hypotheses and check a real original-goal cycle in at least two
   subject interfaces. Assess representation-growth and interpretation under
   their true mathematical scope. Do not award solved-paper rows for a filename.

## Required continuation

Repair this as one coherent work package in the delegated branch. Preserve the
running attempt and do not launch further supposedly qualified seeds/controls
from this adapter. The lab owner may conclude its own flawed attempt cleanly at a
safe checkpoint; no unrelated job is authorized to be interrupted. Retain all
artifacts and costs and mark the affected result unsuitable as capability evidence.

Implement regression tests for label noninterference, source/checker hashes,
duplicate underlying assessments, actual progress/actuation, equal attempt
budgets, full input coverage and exact resume. Test beyond a self-generated
correctness flag. Freeze the repaired executable protocol and source exposure
before starting the qualified sustained run. Keep completed finals closed.

Then continue the full end-to-end campaign autonomously. No new routine approval
is required, and this review is not a request to end after another micro-pilot.
Publish local/REPAIR_001.json with each finding, exact code/test evidence and
qualification decision. Update local/PROGRESS.json with actual jobs, metrics and
costs. The user will return later for an independent trained-candidate audit.
