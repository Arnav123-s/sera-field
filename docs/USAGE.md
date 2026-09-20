# Use the trained field model

The working directory is `D:/ai/labs/sera-field`. The installed `.venv` is ready. Each command below uses a new attempt directory and preserves its output in `runs/<attempt>/process.log`. Change the attempt name when repeating a task.

## Imagine a changed mass

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt my-imagination-001 -- -m sera_field.cli imagine --mass 2 --force "2,0,0" --counterfactual-mass 1
```

Starting at rest with a force of 2 along the x axis, the saved seed-11 field predicts position 0.49943 after one second for mass 2, and 1.01341 for mass 1. The supplied vacuum simulator's corresponding values are 0.5 and 1.0. These are learned conditional predictions. The output contains both trajectories, the original goal and the predictor identity; imagination does not update recorded facts or weights.

## Infer a mass from measured response

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt my-mass-001 -- -m sera_field.cli infer-mass --force "2,0,0" --acceleration "1,0,0"
```

The saved field estimates mass 1.93346 for this example. The search uses the learned predictor over 512 trial masses in [0.25, 8]. Interpretation requires a known applied force and the model's applicable context. The Python API retains an equivalence-class result when force is unknown.

## Plan a controlled movement

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt my-plan-001 -- -m sera_field.cli plan --mass 2 --target "0.2,0,0"
```

The default planner proposes two half-second forces using the same learned acceleration weights. In the saved demonstration these are approximately +1.65669 and -1.69002 along x. A separate DOP853 simulator reaches position 0.20500 and velocity -0.00833 after one second. The target was position 0.20 and zero velocity. The force limit is 8 units per component.

`--steps` and `--dt` adjust the horizon. The two-part planner requires an even number of steps. The final research benchmark used 20 steps of 0.05 seconds. New user horizons are conditional uses of the model, not extra validated benchmark cohorts.

## Choose a saved checkpoint

The CLI defaults to the prospectively designated **field-11** checkpoint. Two directly usable copies are packaged:

- `checkpoints/FIELD-001/field-11.pt`: the base field.
- `checkpoints/FIELD-001/calibrated-11.pt`: the evidence-qualified successor, including the identical base and learned residual field.

For example, append `--checkpoint checkpoints/FIELD-001/field-11.pt`. File and tensor SHA-256 identities are in [the checkpoint manifest](../checkpoints/FIELD-001/manifest.json). The complete archive contains all initializations, comparison models, refinement candidates and intermediate saved checkpoints.

The successor's Python interface accepts measured context:

```python
from sera_field.training import load_model

owner, metadata = load_model(checkpoint)
context = owner.context(support_velocity, support_force,
                        support_mass, support_acceleration)
answer = owner(query_velocity, query_force, query_mass, context=context)
```

Run numerical Python code through the supervisor. Support arrays have shape `[batch, 6, 3]` for vectors and `[batch, 6, 1]` for mass. Queries have shape `[batch, 3]` and `[batch, 1]`. Query acceleration is not an input to context construction. Without context, this owner uses its retained base. The current command interface exposes base-context tasks; the measured-context route is available through Python and the independently checked investigation records.

## Environment and integrity

For a new Windows checkout, create its own environment and install the recorded versions:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.lock --extra-index-url https://download.pytorch.org/whl/cpu
```

The original research machine uses one shared numerical lease at `D:/ai/projects/sera/runs/v3-batch-001/active.lock`. A busy lease causes a new attempt to stop without launching a worker. Leave an active owner's lease alone. The supervisor is Windows-specific and checks its 2 GiB Job Object cap and CPU affinity before resuming its worker. `scripts/recover_orphan.py` is a preserved, one-time forensic recovery tool pinned to a particular archived lease; it is not a routine startup command.

For checks, use a fresh attempt:

```powershell
.\.venv\Scripts\python.exe scripts/supervise.py --attempt my-contracts-001 -- -m pytest
```

FIELD-001 training, selection and finals are completed. Reproduction records live in the [evidence archive](../reports/INDEX.md); do not restart or retune the completed study. The original runs preserve optimizer states and exact RNG cursors, and final evaluation has an explicit opened marker. Further learning belongs to a new prospective work package with untouched cohorts.
