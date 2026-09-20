# Continue an observed task through investigation

The investigation interface keeps its learned response model, original goal,
pending local eligibility, source scope and complete credit history in one
versioned owner. Each command can run in a fresh process. It generates conditional
probes, accepts the actual performed measurement and returns to the original goal.

From the repository root, begin with the measured response example:

```powershell
.venv/Scripts/python.exe scripts/supervise.py --attempt inquiry-start-001 -- -m sera_field.interactive_inquiry start --session local/my-inquiry --input examples/learned-response-task.json
```

The input contains at least eight adaptation rows, four separate calibration rows,
source identity, assumptions and `original_goal.queries`. Rows are
`[velocity, control, response]`, with velocity/control in `[-2,2]`. Original-goal
query inputs must be separate from adaptation and calibration inputs. The example
uses independently simulated measurements; use your actual instrument/source
records for another observed system.

Write `local/my-inquiry-scope.json` containing the exact `source` and `assumptions`
objects from the task. Then request an investigation:

```powershell
.venv/Scripts/python.exe scripts/supervise.py --attempt inquiry-propose-001 -- -m sera_field.interactive_inquiry propose --session local/my-inquiry --input local/my-inquiry-scope.json
```

The result preserves all 24 measurement branches, merged probe alternatives,
conditional response predictions and the selected `requested` coordinates.
The command records a pending decision and its exact policy derivatives before
seeing the new outcome. A second proposal waits until that decision is resolved.

After performing the measurement, prepare a JSON receipt containing:

- The original `source` and `assumptions`, the proposal's `decision`, and new
  `measurement_id` and `assessment_id` identifiers.
- `performed`: the two coordinates the instrument actually applied.
- `response`: the observed result at those performed coordinates.
- `goal_measurements`: independently measured `[velocity, control, response]`
  rows for the original-goal queries, in their original order.

```powershell
.venv/Scripts/python.exe scripts/supervise.py --attempt inquiry-observe-001 -- -m sera_field.interactive_inquiry observe --session local/my-inquiry --input local/my-inquiry-receipt.json
.venv/Scripts/python.exe scripts/supervise.py --attempt inquiry-answer-001 -- -m sera_field.interactive_inquiry answer --session local/my-inquiry --input local/my-inquiry-scope.json
```

SERA incorporates the performed observation, independently calculates progress,
applies qualified local credit and returns current predictions. A mismatched
intervention is recorded and used as its actual observation; credit for the
unperformed proposal is rejected. Duplicate receipts and changed original-goal
assessment rows are rejected. Imagined values do not count as measurements.

Source fields record the provider's declaration. They do not authenticate a
physical instrument or turn an unmeasured guess into independent evidence. The
packaged candidate's measured policy-training result and full model provenance
are recorded in the INQUIRY-014 report. All predictions retain their fitted scope.
