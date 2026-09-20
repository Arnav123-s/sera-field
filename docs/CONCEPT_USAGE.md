# Use the acquired-model owner

The packaged `CONCEPT-011` owner learns a local response from observations and
reuses that same state for prediction, inverse answers, imagined interventions,
planning and directional explanations. A session preserves its original goal,
source receipts, earlier revisions and a proposed next measurement.

Use the existing environment from the repository directory on this Windows
machine. The supervisor reserves the shared numerical lease, one CPU thread and
2 GiB for the complete process tree. Choose a new attempt name for every command.

## Start a persistent task

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt my-device-001 -- -m sera_field.session_cli --session local/my-device new --input examples/concept-task.json
```

The example is an explicitly labeled engineering simulation. Each measured row
is `[velocity, calibrated control input, acceleration]`. Replace the example
with your observations and their actual source identities to study another
device in this response family. Observation conditioning happens on those rows;
the source's hidden model parameters are never needed as learner input.

The answer contains the same concept identity across numerical predictions,
the required control input for a target acceleration, changed-input consequences,
five candidate constant-control plans and a learned direction explanation.
The trained explanation interface distinguishes increasing control input from
increasing velocity, at the stated operating point.

## Resume and reuse its understanding

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt my-device-002 -- -m sera_field.session_cli --session local/my-device solve
```

Put a follow-up task in a JSON file, using any of the `predict`, `inverse`,
`counterfactual`, `plan`, `question` and `operating_point` fields shown in the
example. Then reuse the acquired model:

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt my-device-003 -- -m sera_field.session_cli --session local/my-device ask --task local/followup.json
```

This preserves the original goal and acquired state. Returned answers name both
the original goal and the requested follow-up task.

## Add actual evidence and return to the goal

The `next_investigation` item proposes a velocity and control setting. Obtain an
actual measured or independently simulated outcome, and save a receipt such as:

```json
{
  "source": "your instrument and calibration record",
  "kind": "measurement",
  "measurement_id": "sample-005",
  "measured": [0.5, 1.0, 0.95]
}
```

The numbers above illustrate the schema. Use the result actually observed.

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt my-device-004 -- -m sera_field.session_cli --session local/my-device observe --receipt local/receipt.json
```

SERA stores the complete receipt and a new acquired-concept revision, then answers
the original goal again. Repeated evidence is rejected. The prior revision remains
available. A declared source is provenance, not automatic certification: runtime
receipt intake does not grant reward. The separately tested credit path requires
an independent checked outcome bound to the decision and original goal.

## Use its retained reading and arithmetic

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt my-reading-001 -- -m sera_field.learned_cli --training checkpoints/CONCEPT-011 read --question "What did Alice see?" --source examples/reading-practice.txt
.\.venv\Scripts\python.exe scripts/supervise.py --attempt my-math-001 -- -m sera_field.learned_cli --training checkpoints/CONCEPT-011 math --question "I have 5 apples and buy 3 more. How many apples do I have?"
```

Reading returns ranked source passages. Arithmetic returns learned executable
proposals with exact arithmetic execution. Their outputs are retained exactly
from ECHO-007 in the delivery checks.

The [engineering explanation](CONCEPT_ENGINEERING.md),
[teaching/results report](../reports/CONCEPT-011/REPORT.md), and
[checkpoint manifest](../checkpoints/CONCEPT-011/MANIFEST.json) connect these
commands to the trained mechanisms and measured scope. For a fresh checkout,
the environment setup is in [the original usage guide](USAGE.md).
