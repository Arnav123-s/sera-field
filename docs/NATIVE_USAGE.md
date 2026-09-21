# Use the native memory-field owner

NATIVE-019 initializes and teaches perception, memory and imagination together.
Its [manifest](../checkpoints/NATIVE-019/MANIFEST.json) records the exact assessment
and research role. Its [report](../reports/NATIVE-019/REPORT.md) gives the measured
tasks, complete comparisons and costs. All 11 native qualification gates and
fresh-process replay passed. The earlier released interfaces remain available.

Every command runs in the existing environment with a fresh attempt name, after
any current numerical worker releases the shared lease.

## Read a situation and consider alternatives

The included [meaning example](../examples/native-meaning.json) contains:

```json
{
  "premise": "A person is holding a red flower beside a window.",
  "hypotheses": [
    "Someone holds a flower.",
    "Nobody is holding anything.",
    "The flower was bought this morning."
  ]
}
```

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt native-meaning-001 -- -m sera_field.native_cli interpret --input examples/native-meaning.json
```

The premise is consumed into history once; each proposed statement reads the
same retained state. The result gives learned entailment, contradiction and
unresolved-information probabilities. This example is an input illustration;
its labels are not claimed to be a measured result in the research report.

## Keep a measured task and investigate it

Use the included [observations](../examples/native-observations.json), or create
a JSON file with `source`, `goal` and `observations`. A goal supplies
`force` and `velocity`. Each observation supplies a unique `id`, its `source`,
`performed: true`, actual `force`, `velocity` and measured `response`. Inputs use
the training study's normalized force/velocity/acceleration conventions.

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt native-device-001 -- -m sera_field.native_cli start --session local/native-device --input examples/native-observations.json
.\.venv\Scripts\python.exe scripts/supervise.py --attempt native-probe-001 -- -m sera_field.native_cli propose --session local/native-device
```

The saved original goal stays fixed. The proposal includes the exact predictor,
state and proposed control. The current investigation selector chooses the
largest disagreement among three imagined continuations on its declared grid.
The included observations come from a declared illustrative simulator; the
learner consumes their measured triples. The source label records the generating
rule for the human reader and is not an input to the numerical predictor.

After performing a measurement, call `observe` with a JSON request containing
`decision_id` and `evidence`. Evidence has the same receipt fields as an initial
observation. SERA records whether actual controls matched the requested controls
and updates from the actual values. A performed measurement with an unread
response does not supply a numerical observation.

Call `answer` to return to the original goal, or supply a `queries` array of
`[force, velocity]` pairs to imagine alternatives. These queries do not write
observations. Each command atomically preserves a new session revision.

If the original goal is independently measured, `grade` accepts `decision_id`,
`independent_response`, `source` and `verifier`. Signed squared-error improvement
is tied to that transition and outcome. Positive credit and opposing evidence
are recorded; repeated credit or an altered predictor is rejected. Grading a
state update is separate from training a new investigation policy.
