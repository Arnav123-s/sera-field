# Learn an observed response and reuse it

GROW-013 adds a learned residual representation to the coupled owner. Its input is
a scoped set of measured `[velocity, control input, response]` rows, with separate
calibration measurements. The acquisition interface fits from these observations,
tests the extension and returns to the original goal. The checkpoint/report state
determines whether the candidate is qualified; CONCEPT-011 remains preserved.

An input JSON contains:

```json
{
  "original_goal": {"queries": [[0.5, 1.0]]},
  "source": {"kind": "measurement", "id": "my-device-experiment"},
  "assumptions": {"velocity_units": "m/s", "control_units": "N/kg", "response_units": "m/s^2"},
  "adaptation": [],
  "calibration": []
}
```

Supply at least eight adaptation and four separate calibration observations.
The registered study uses 24 and 8. The empty arrays above show the schema only.
Source declarations are retained; the interface returns an observation-fitted
conditional model and does not turn the declaration into externally verified fact.

From the repository root, after the assessed package is exported:

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt my-response-learn-001 -- -m sera_field.extension_cli learn --session local/my-response --input local/my-measurements.json
.\.venv\Scripts\python.exe scripts/supervise.py --attempt my-response-ask-001 -- -m sera_field.extension_cli answer --session local/my-response --input local/my-question.json
```

Every supervisor attempt needs a new name. Session creation will not overwrite an
existing session. Inference uses the exact owner identity recorded at acquisition.
A question file can request multiple uses of the same concept:

```json
{
  "queries": [[0.5, 1.0], [0.5, 1.5]],
  "inverse": {"velocity": 0.5, "response": 1.0},
  "question": "What happens when the control input increases?",
  "point": [0.5, 1.0],
  "plan": {"target": [0.1, 0.5], "velocity": 0.0, "duration": 0.4}
}
```

The answer retains the original goal, concept identity, assumptions, model
alternatives and numerical residuals. The inverse route preserves distinct roots
within its bounded search; the planning route retains its five best candidate
controls. These are conditional proposals until their executed outcomes are
observed. The training/evaluation report records the learned feature procedure,
teacher-supplied worlds, source separation, failures and verification costs.
