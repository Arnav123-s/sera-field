# CONCEPT-008: one acquired relationship, five uses, and verified investigation

This campaign continues the ECHO-007 owner. It preserves all completed experiments
and final groups. Complete engineering, matched teaching, investigation learning,
fresh assessment, independent replay, a usable persistent session, and publication
before closing the campaign. Checkpoints are recovery points, not task completion.

## Construction and mathematical scope

Keep the existing observed basis `[f,v,v*abs(v),1]` and the three learned coefficient
proposals. Acquire a single episode state from measured rows. With observed design
matrix X, responses y, learned prior C and positive precision P, compute
`C' = C + solve(X.T X + P, X.T (y-X C))`. Learn P through held-out consequence
loss; compare full positive-definite and diagonal precision against the unmodified
owner and a fixed ridge control. Positive matrices here regularize acquisition;
they are not silently called SPD sheaf stalks, Chern memory or ERG growth.

The same C' must serve forward consequences, inverse required-force questions,
changed-velocity/force counterfactuals, force planning and a bounded directional
explanation. No downstream task-specific adaptation after acquisition. Equations,
action limits, observation channels and simulation families are supplied. A new
episode's relation is learned from observations, not supplied hidden coefficients.
Language uses the retained word encoder with newly taught question routing and
direction classification; supplied simulation annotations and rendered prose are
explicitly identified. It is a bounded scientific interface.

Human-trained reading/mathematics weights stay exactly retained in this campaign.
Only new acquisition and meaning parameters train in the teaching stage. The
actual continuing owner's investigation parameters may then receive checked
reward. Shared ownership is verified separately from the five-use behavior.

## Frozen finite teaching and development

Two arms, `full` and `diagonal`, seed 8108, each complete 4,096 batches of 24 new
simulated systems. New parameters initialize locally. The retained ECHO parent
is identical. Use AdamW, learning rate .002, weight decay .0001, gradient clip 3.
Support size varies from 2 to 12; measurement noise SD .03. Independent query
outcomes provide acquisition targets. No hidden coefficient targets train P.
The calibrated drive channel has a signed gain of magnitude .7–1.3: the sign
models actuator orientation, not negative mass. Linear response ranges -.7–.7
(zero every fourth case), quadratic response -.2–.2 (zero every third case), and
offset -.5–.5. Velocity/input support and queries lie in [-2,2]. The omitted
diagnostic adds an independently supplied .4–.8 sine response. Positive feedback
is assessed only over the stated finite integration interval.
Train question routing on the recorded phrase bank and directional semantics on
independent outcome differences; semantic loss .3, routing loss .1.

Development: 256 new systems, zero and every 512 updates. Select minimum
`forward_MSE + .05 * directional_error + .05 * routing_error`; earliest tie wins.
The two arms share systems, batches and phrase selections. Full training logs,
initial/selected/later checkpoints, RNG and optimizer states remain preserved.
Training/development split strings start with `CONCEPT-008` and never overlap.

## Reward stage and controls

After selecting the better arm on development alone, freeze the predictor. Train
its existing investigation policy for 2,048 independently simulated episodes,
with one sampled observation per original goal. Use the existing CreditBridge:
signed measured progress, source/verifier identities, novelty deduplication,
policy freshness and actual actuation checks. Preserve the unchanged policy.
Evaluate development at zero and each 256; choose minimum returned-goal MSE on
128 development episodes. Do not reward confidence, raw branch count or reuse of
the same evidence. Compare selected reward, unchanged, random and analytic probes.

## Assessment registered before opening

Jointly register the selected full and diagonal weights, unmodified ECHO parent,
fixed ridge control and selected reward policy. Assess 512 new supported systems
and separately 128 omitted-mechanism systems. Record all five uses and their common
concept identity. Inverse inference solves for required force, not unidentifiable
mass from positions alone. Planning chooses among 41 admissible constant forces
and is checked by a separately implemented DOP853 integration. Compare independent
outcomes, not SERA's own predicted endpoint, for success.

Use independent signal noise for support, requested observations and assessment.
Preserve mismatched actuation receipts (every 41st episode) and return the original
goal even when credit is rejected. Test adequacy on fresh probe residuals; report
both detection and false alarm rates. Ensemble spread is reported independently.
Question paraphrases held out from teaching test bounded language transfer.

Qualification requires supported forward MSE <= .8 parent, inverse required-force
MSE <= .8 parent, counterfactual MSE <= .8 parent, planned endpoint MSE <= .9 parent,
bounded direction and routing accuracy >= .8, immutable original evidence, and
exact retention of all old non-world/non-policy weights. A failed gate preserves
an experimental candidate and diagnoses a next repair; no final tuning. Reward
policy qualification requires <=1.05 unchanged-policy MSE on its separate 256
episode final cohort. Report all controls and all gate outcomes.

Fresh-process replay must match raw records and metrics. Persistent session tests
must recover the same concept and answer after interruption, reject duplicate
evidence, preserve original goals and bind revisions to predictor identity.

One numerical CPU thread, shared exclusive lease, 2 GiB process-tree cap, no paid
compute. Costs include failed attempts, development, controls, replay and delivery.
Publish the independent lab and detailed reports without merging other labs or
replacing the preserved production learner.
