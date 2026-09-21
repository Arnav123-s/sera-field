# A retained situation that learns from a checked investigation

JOINT-020 continues the from-scratch NATIVE-019 weights. Language, observed
measurements, conditional branches and action scores use the same memory field.
Its [manifest](../checkpoints/JOINT-020/MANIFEST.json) records the candidate's
assessment and role; [results](../reports/JOINT-020/REPORT.md) give the matched
reward comparison and retention. Earlier qualified interfaces stay available.

The counterbalanced continuation is **JOINT-021**. It keeps the same interface
and native architecture, with both physical families taught in both input
orders. Its [protocol](../protocols/JOINT-021.md) identifies the preserved
JOINT-020 evidence and the fresh assessment groups. To use its separately
packaged owner, add `--owner checkpoints/JOINT-021` to `start`; use a new session
directory. Subsequent commands restore that session's own owner.

## Start, ask and investigate

The [example](../examples/joint-situation.json) puts a supplied human description
and two simulated measurements in one retained workspace. The description is a
separate question; it is not presented as a causal account of the apparatus.
Replace these with your own identified observations in the studied input units.

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt joint-start-001 -- -m sera_field.joint_cli start --session local/joint-task --input examples/joint-situation.json
.\.venv\Scripts\python.exe scripts/supervise.py --attempt joint-ask-001 -- -m sera_field.joint_cli answer --session local/joint-task
.\.venv\Scripts\python.exe scripts/supervise.py --attempt joint-probe-001 -- -m sera_field.joint_cli propose --session local/joint-task
```

Use fresh attempt names after the current numerical lease is released. A proposal
records the original questions, source, predictor, state, observation prefix and
learned action probabilities. Its highest permitted score selects a measurement
or STOP. A repeated call returns the same pending decision. `answer` returns
human relation probabilities and conditional numerical predictions.

## Observe the actual result

Call `observe --input receipt.json` with `decision_id` and `evidence`. The evidence
contains `kind: "measurement"`, unique `id`, `source`, `performed: true`, actual
`force`, `velocity`, and observed `response`. Keep the actual controls even if
they differed from the request. For STOP, omit evidence. Reading or proposing a
conditional branch does not create an observed event.

## Independently grade and learn

When the original numerical question has an independent measured answer, call
`grade --input assessment.json`. Supply `decision_id`, `independent_response`,
`source`, `verifier` and a unique `evidence_id`. These are explicit external
assessment receipts; the API does not authenticate a user's measurement.

Signed error reduction minus measurement cost trains the existing choice
procedure. Actual controls must match requested controls for that policy credit.
Repeated or stale credit is rejected. The update saves before/after weight
identities and optimizer state. The session then re-encodes its retained
observations under the changed weights and returns to both original questions.
Raw observations and all earlier revisions remain available.

The saved task contains its own exact updated owner. Later commands restore that
owner and optimizer, rather than silently loading the initial packaged weights.
`answer` can also receive `force` and `velocity` in its input JSON for an additional
conditional query; it leaves the original goal intact.

## What the experiment measures

The [frozen protocol](../protocols/JOINT-020.md) compares identical human lessons,
simulated observations and training actions, with the reward term enabled or
withheld. Original-goal final predictions are recorded before their grading
signal reaches memory. A different later query tests use of that prior feedback.
Persistent delivery separately checks a real weight update, retained goals,
exact restart and duplicate-credit rejection. The report distinguishes acquired
behavior from the supplied families, questions, action grid and verification.
