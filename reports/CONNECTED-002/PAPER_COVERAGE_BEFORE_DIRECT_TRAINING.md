# Paper and intended-behavior coverage audit

The original proposal is retained byte-for-byte in the private intake, SHA-256
`b0be4b4aea776bcdfd580e000aebbb1bd7b56523e6b0df32f0c1fdb89fbfc9cd`.
I compared each substantive mechanism and requested behavior with executable code,
training records and tests. A research objective, an engineered component and a
demonstrated learned capability have separate statuses below.

The paper has not been fully implemented or fully trained. This audit does not
make a verdict about eventual feasibility. It identifies the exact work needed to
test the intended system, including mathematically under-specified parts.

| ID | Research or behavior requirement | Current evidence and precise next obligation |
|---|---|---|
| P01 | Entirely fresh learned weights | FIELD-001 is independently initialized; SituationOwner is also fresh. No pretrained or legacy SERA backbone. Preserve initialization hash and lineage for every new seed. |
| P02 | One persistent shared substrate | FIELD-001 shares a physical predictor across engineered task routes. SituationOwner now shares its field across text/numerical input, prediction and choice. Train and measure cross-domain beneficial transfer. |
| P03 | SU(N), gauge-equivariant links | Actual learned SU(2) link coordinates exist and were trained in FIELD-001. Local-frame and physical-rotation tests cover specified operations. Semantic equivalences require their own learning/evaluation. |
| P04 | Wilson-loop contextual features | New input-conditioned closed-loop features participate in forward computation and gradients. Invariance is tested. Their learned contribution needs a loop-disconnected control. |
| P05 | Dynamical transient boundary | New explicit finite lattice action and repeated working-state updates are implemented and derivative-tested. Persistent goal-bound memory and long-stream behavior remain integration work. |
| P06 | Bulk-to-boundary action coupling | Learned prior, links and stiffness constrain finite boundary evolution. This is a declared finite approximation, not a derived holographic correspondence. Derive/test projections and action scope. |
| P07 | Separation of facts and imagination | Branch storage and parameter immutability are tested; FIELD-001 exercises physical what-ifs. Extend evidence-qualified promotion and interruption recovery to all taught subjects. |
| P08 | Gauge transformation as physical counterfactual | A gauge frame change preserves invariant observables; changing mass changes the physical input. Keep these separate. Test physical interventions through changed situation variables. |
| P09 | Topological defects as persistent knowledge | No trained Chern-class/defect storage exists. Define encoding, extraction and scope, test noise/retention, and retain an independently verified storage control. |
| P10 | Topology as proof/truth and perfect retention | Stability alone is not a semantic verification rule. Derive a checkable mapping if proposed, and evaluate it against independent proof/observation checks. Do not delete verifiers on the strength of the analogy. |
| P11 | Wetterich effective-action flow | Not implemented. Specify field content, regulator, truncation, second derivative, scale discretization, projections, boundary conditions and computational cost before calling a mechanism ERG. |
| P12 | Autonomous representation growth | FIELD-001 used supplied residual families and scripted expansion. A learned inadequacy/growth decision and an explicit growth operator still need implementation, ablation, retention and novel-mechanism tests. |
| P13 | e-prop/local biological credit | New delayed score-function eligibility is real and derivative-tested. It is not e-prop or curvature-as-eligibility. Derive a local temporal estimator and compare to a short exact gradient reference. |
| P14 | Reward-triggered consolidation | FIELD-001 only logged credit. The new bridge actually changes owner weights and persists credit atomically. A training study must establish improved next-task behavior from this update. |
| P15 | Non-dissipative continuous update | New action descent is explicitly dissipative. Preserve this departure and investigate a precisely specified alternative where useful; do not relabel the existing solver. |
| P16 | Exactly matched 35,840-byte working state | FIELD-001 matched four models at 783 parameters, not the older owner's entire state. Account for state, activations, optimizer, traces and branch storage separately before an exact memory-matched claim. |
| P17 | Scrambled topology/control | FIELD-001 preserved a scrambled physical metric control. It is not a full scrambled holographic/ERG model. Specify matched controls for each actual new component. Winning a leaderboard is not a project gate. |
| P18 | Five-way zero-shot cross-use | Physical forward/inverse/what-if/planning routes were evaluated with one frozen predictor. Natural language explanation is still engineered/untaught in this lab. Test all five uses and task-specific exposures honestly. |
| P19 | Omitted-drag growth and regression | FIELD-001 qualified a learned residual while preserving the base; supplied context statistics and family. Test genuinely learned growth decisions and additional omitted mechanisms. |
| B01 | Language forms a situation/perspective | New byte input path exists; human corpora are qualified for intake. It is not yet a trained language capability. Test roles, negation, reference, observation vs belief and held-out human wording. |
| B02 | Self-noticed gaps and original goals | Supplied disagreement probes existed. Train gap/investigation selection, keep original goals across interruptions, and return checked answers rather than only collecting gaps. |
| B03 | Diverse learned ideas and methods | Existing alternatives were supplied. Train proposal construction; deduplicate aliases using assumptions and observable consequences. Commit proposals before revealing answers. |
| B04 | Imagination contributes to answers | Physical counterfactuals worked in FIELD-001; new shared boundary is executable. Train multi-step consequences and compare behavior with imagination disconnected at matched evidence cost. |
| B05 | Independent checking and useful rewards | Existing checkers plus new durable credit bridge. Preserve failed interventions, assessments and negative reward. Separate simulated evidence, measurements, proofs and interpretation rubrics. |
| B06 | Breadth: maths/code/language/sciences/humanities | Human sources are staged, not yet trained into the new owner. Curriculum must include all tracks with source-specific assessments, depth metrics and retention. |
| B07 | Creativity, connections and discovery | Credit canonical new verified contributions, not count or wording. Test withheld mechanisms/compositions and scope novelty relative to training exposure. Compare external knowledge only after proposals are locked. |
| B08 | Better learning procedures | No new-lab evidence yet. Reward only improved acquisition on subsequently unseen tasks under matched teaching/evidence cost; record unsuccessful attempts too. |
| B09 | Empathy, philosophy and poetry | Operationalize perspective-taking, constraints, alternative interpretations and textual support. These assessments do not establish subjective feeling or the author's private mental state. |
| B10 | Real tasks, persistent self-study and correction | Existing bounded physical CLI is usable. Build connected task episodes, goal memory, correction/revision and resumable self-study, then demonstrate practical use from the trained checkpoint. |

## Training audit

FIELD-001: 54,000 gradient updates across 18 runs; 6,912,000 sampled training queries
with repeats; 65,536 distinct generated training observation records. Physical
results and all controls/failures remain in FIELD-001.md and its evidence archive.
Its original independent rewards caused zero policy updates. The new engineering
tests cause controlled parameter updates solely to test wiring; they are not a
broad curriculum or evidence of autonomous discovery.

Human-source intake: 7,473 mathematics records inspected, 7,376 passing literal
arithmetic annotation checks; 97 retained for review. There are 374 official MBPP
training records parsed, plus preserved human dictionary, grammar, conversation,
philosophy, calculus and reading-comprehension sources. Syntax checking is not
program execution. Exact arithmetic checks are not proof of word-problem meaning.

## Completion rule for the delegated campaign

Every row above must receive a linked outcome: implemented and tested; trained
with measured behavior; repaired after a recorded failure; or investigated and
left open with its mathematical/empirical obstacle and exact next action. A row
must never be silently dropped or marked complete solely from a document, code
name, larger training run or successful unit test. Re-read the original proposal
and the user's behavioral vision before freezing training and after evaluation.
