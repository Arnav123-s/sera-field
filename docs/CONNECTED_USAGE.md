# Use the learned reader, arithmetic proposals and imagined worlds

Work in `D:/ai/labs/sera-field`. Each invocation reserves the shared numerical
worker and saves its output under a new `runs/<attempt>/` directory. Give every
attempt a new name. The original physical CLI remains available in `USAGE.md`.

The commands below use the freshly trained Clifford/sheaf owner selected on
development data. The alternative owner is selected by changing `--training` to
`runs/CONNECTED-003-teaching-1103`. Both use locally trained weights throughout.

The latest qualified continuation is **ECHO-007**. Select it in any command below
with `--training checkpoints/ECHO-007`. It uses the same learned task interfaces
and preserved investigation policy, with the field taught through reversible
credit. The [new results](../reports/ECHO-007/REPORT.md) and
[executed examples](../reports/ECHO-007/USAGE_EXAMPLES.json) include its exact
checkpoint identity. SCFE-004 remains the default when the option is omitted.

For a source already included with the lab:

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt echo-reading-001 -- -m sera_field.learned_cli --training checkpoints/ECHO-007 read --question "What did Alice see?" --source examples/reading-practice.txt
```

## Ask about a source you provide

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt my-reading-001 -- -m sera_field.learned_cli --training checkpoints/SCFE-004 read --question "What changes the acceleration?" --source "D:/path/to/your/source.txt"
```

SERA encodes the complete source and question, runs its learned situation field
and ranks supporting passages. The result includes the exact file hash and text
offsets so the answer can be checked against the source. The reported softmax
values describe its ranking, rather than a calibrated probability of truth.

## Generate different executable arithmetic proposals

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt my-arithmetic-001 -- -m sera_field.learned_cli --training checkpoints/SCFE-004 math --question "I have 5 apples and buy 3 more. How many apples do I have?"
```

The learned weights rank operations and operand pointers. Up to five distinct
binary rational programs are executed exactly. Commutative spellings of the
same program share an identity; genuinely different operations remain separate.
The original question, operand inventory and each program are shown for checking.

## Imagine consequences from observations

Each observation is `[velocity, force/mass, measured acceleration]`. Each query
is `[velocity, force/mass]`. Use the same units consistently.

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt my-world-001 -- -m sera_field.learned_cli --training checkpoints/SCFE-004 imagine --observations '[[0,0,0],[0,1,1],[1,0,-0.3],[-1,0,0.3]]' --queries '[[0,2],[1,2],[-1,2]]'
```

The same acquired world encoder produces three coefficient hypotheses and their
consequences. Those alternatives remain conditional on the observations and the
taught force/drag/offset basis. They are predictions to test against outcomes.

## Transfer the acquired response into a trajectory

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt my-motion-001 -- -m sera_field.learned_cli --training checkpoints/SCFE-004 motion --observations '[[0,0,0],[0,1,1],[1,0,-0.3],[-1,0,0.3]]' --velocity 0 --force-per-mass 1 --duration 1
```

SERA's coefficient hypotheses drive three RK4 trajectories. The output includes
position, velocity, the integration conditions and retained alternatives. A
diverging rollout is recorded with its status rather than replaced by an invented
endpoint. The study checks these trajectories with a separately implemented
DOP853 simulator.

## Investigation and reward evidence

The packaged owner includes the policy qualified in SCFE-006. Ask it to choose
the next measurement for your original questions:

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt my-investigation-001 -- -m sera_field.learned_cli investigate --observations '[[0,0,0],[0,1,1],[1,0,-0.3],[-1,0,0.3]]' --queries '[[0,2],[1,2],[-1,2]]'
```

This returns its current alternatives and a proposed velocity/force setting.
After performing the observation, append the actual measured row and repeat
`imagine` with the same queries. A proposed setting is labeled as a proposal.
The complete study's automatic loop uses independent simulation receipts for
the observation, assessment and reward steps.

The trained investigation policies and their exact revisions live in
`runs/CONNECTED-SCFE-rewards-{field,scfe}/`. Final inquiry records preserve the
original goal, the prediction made before the outcome, chosen probe, actual
actuation, independent outcomes, revised answer and reward qualification.
These files provide the full path by which independently verified progress
reinforces a learned decision. Rewards do not affect source truth or permissions.

The selected 768-attempt policy reduced mean error by 39.5% after its observation
on 512 new systems, and by 17.4% relative to the unchanged policy on those same
systems. The later 2,048-attempt candidate remains preserved as an unsuccessful
qualification. Every reward run and all 17 development-assessed policy states
are accounted in the results and cost records.

The completion script is a resumable research command, not a command to restart
completed training:

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt connected-completion-resume-001 -- scripts/complete_connected_campaign.py
```

It verifies completed training, resumes only incomplete reward work, enforces
the prospective joint registration and reuses committed evaluation components.
Its replay uses a fresh Python process and checks exact raw-record identities.
