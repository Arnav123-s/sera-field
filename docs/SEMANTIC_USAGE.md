# Interpret statements and investigate a measured task

SEMANTIC-015 teaches human sentence relations through the continuing situation
field. Given a premise and proposed statements, the owner returns conditional
support, contradiction and unresolved-information probabilities. Its same saved
weights retain physical acquisition and the persistent investigation interface.

The following interface uses `checkpoints/SEMANTIC-015`, created only after the
independent qualification audit passes. The [report](../reports/SEMANTIC-015/REPORT.md)
records teaching, complete assessment and source identities.

Save a request such as this in `local/meaning-request.json`:

```json
{
  "premise": "A person is holding a red flower.",
  "hypotheses": [
    "Someone is holding a flower.",
    "Nobody is holding anything.",
    "The flower was purchased this morning."
  ]
}
```

Run it under the ordinary local resource supervisor:

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt meaning-request-001 -- -m sera_field.meaning_cli interpret --input local/meaning-request.json
```

These are example inputs, not reported evaluation outcomes. Each output lists the
learned relation probabilities and the three conditional continuation choices.
The premise specifies the assumed situation; interpretation leaves recorded
observations and retained weights unchanged.

For a measured investigation, use the JSON requests described in
[the investigation guide](INQUIRY_USAGE.md). Replace its module name with
`sera_field.meaning_cli` and its owner with `checkpoints/SEMANTIC-015`. The actions
remain `start`, `propose`, `observe` and `answer`. A request to interpret text during
that session also includes the session's exact `source` and `assumptions` and
`--session local/my-session`. Its response preserves the original measured goal.

The [delivery record](../reports/SEMANTIC-015/DELIVERY.json) checks fresh-process
restart, a human sentence, an independently performed measurement and return to
the original task using one owner. Text interpretation and measurement inputs
remain explicitly identified in that record.
