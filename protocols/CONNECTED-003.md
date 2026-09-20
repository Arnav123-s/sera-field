# CONNECTED-003: direct, audited continuation

This prospective amendment replaces the delegated training adapter, not the SERA
vision or preserved FIELD-001 evidence. The user paused Antigravity and requested
direct execution. No delegated weights are imported. All parameters start fresh.

## Frozen first integration

Train one field owner on (1) human question-to-evidence grounding, (2) executable
arithmetic proposals derived from human worked problems, (3) human program and
prose associations, and (4) simulated systems learned from observed interventions.
Then reward evidence choices using independently measured improvement on the
original physical goal. Preserve distinct conditional hypotheses and return an
answer with the observation that changed it. Human prose exposure is not scored
as philosophical understanding, and program association is not program synthesis.

The original maximum allocations remain available for later integrations. This
first executable integration uses 12,288 attempted minibatches of 24 cases, seed
1103, mixed schedule [reading, reading, math, pairs, physics, reading, math, pairs,
physics, pairs, reading, physics]. Development every 1,024 attempted batches;
checkpoints every 512; select by mean of per-objective normalized development
losses relative to initialization, with equal objective weight. No adaptive final
tuning. Two reward-policy arms receive the same 2,048 fresh physical episodes:
verified progress versus reward disconnected. Reward updates do not alter their
frozen, common pretrained-for-this-study outcome predictor. In this context that
means the freshly trained CONNECTED-003 predictor, never an external backbone.

Sources: existing immutable CONNECTED-002 human partitions; human dictionary,
grammar, Plato, Descartes, calculus and DailyDialog with source notices retained.
Program teaching is local research on the repository's Apache-2.0 licensed MBPP
release, with original README and license pinned. No corpus text is published.
Candidate input construction must not inspect hidden labels. Whole passages and
questions are encoded, with offsets; no prefix clipping or answer-marked features.
Stable token hashing is an engineering vocabulary, not pretrained knowledge.

Math scope: learned construction of binary rational expressions from observed
numbers and disclosed constants. Human solution steps outside that grammar are
recorded as unsupported teaching transformations, not forced into wrong targets.
Human prior steps are identified as teacher forcing. Report original one-step
questions separately from continuation of supplied previous work.

Physics scope: acceleration response with linear/quadratic velocity effects and
offset, observed through supplied measurement channels. The basis and bounded
probe menu are supplied. Coefficients are inferred from observations; no true
coefficient/family labels reach the learner. Independent verifier computes actual
outcomes, checks actuation, and evaluates a held-out query set. Conditional
imagination is not measurement. Unmodeled effects receive an adequacy diagnostic.

## Controls and evaluation

Development only: initial weights, lexical evidence ranking, exact arithmetic
execution, random versus learned versus analytic physical investigation. Matched
no-imagination and no-loop inference interventions are sensitivity diagnostics,
not equally trained architecture comparisons. A separate no-reward trained arm
isolates policy learning with equal attempted episodes and equal outcome access.

After selection, open one deterministic final cohort: up to 1,024 human questions,
512 mathematics continuations, 256 examples per human-pair track, and 256 physical
systems. Reserve the remaining human final groups and a separate physics seed for
future studies. Freeze the final candidate identity before opening; store all raw
predictions and failures. No final-derived repair/reselection on that cohort.

## Integrity and resumption

Record real initial weights, per-source unique exposure and repeated attempts,
source/checker/code identities, raw losses, negative reward, compute costs,
optimizer, all random generators, data permutations/cursors and schedule. Test
bit-identical next update after fresh-process resume. A decision is committed
before an independent outcome is obtained. Reward never changes correctness or
permissions. Duplicate evidence, stale weights and renamed-goal novelty farming
must remain rejected. Independent replay uses frozen weights and no updates.

Use the shared lease, one CPU numerical thread, 2 GiB committed job-tree memory,
no paid resources, and no scheduled follow-up. Original production and all other
labs remain untouched. Review every paper/behavior row after this integration;
do not mark an under-specified holographic/ERG/topological claim implemented by
renaming the finite field solver.
