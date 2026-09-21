"""Bind the whole-cycle report to completed measurements, identities and costs."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.records import write_json


def read(path):
    return json.loads(Path(path).read_text())


def main():
    folder = ROOT / 'reports/JOINT-020'
    qualification = read(folder / 'QUALIFICATION.json')
    teaching = read(folder / 'TEACHING.json')
    result = read(folder / 'RESULTS.json')
    independent = read(folder / 'INDEPENDENT_METRICS.json')
    delivery = read(folder / 'DELIVERY.json')
    attempts = [read(p) for p in sorted((ROOT / 'runs').glob('joint020-*/state.json'))]
    if any(r['status'] in ('STARTING', 'RUNNING') for r in attempts):
        raise ValueError('Finish the owned numerical work before final cost accounting')
    costs = {'attempts': [{k: v for k, v in r.items() if k != 'sources'} for r in attempts],
             'wall_seconds': sum(r['wall_seconds'] for r in attempts),
             'cpu_seconds': sum(r.get('resources', {}).get('cpu_seconds', 0) for r in attempts),
             'peak_bytes': max(r.get('resources', {}).get('peak_committed_bytes', 0) for r in attempts)}
    write_json(folder / 'COSTS.json', costs)
    table = '\n'.join(f"| {route} | {cohort} | {row['metrics']['accuracy']:.2%} | {row['metrics']['after_mse']:.6f} | {row['metrics']['next_query_mse']:.6f} | {row['metrics']['measurement_rate']:.2%} |"
                       for route, groups in result.items() for cohort, row in groups.items())
    comparisons = '\n'.join(f"| {name} | {item['mean']:.6f} | [{item['95_percent_interval'][0]:.6f}, {item['95_percent_interval'][1]:.6f}] |"
                             for name, item in independent['comparisons'].items())
    gates = '\n'.join(f"| {name} | {'Passed' if value else 'Open; preserve candidate and diagnose'} |"
                       for name, value in qualification['gates'].items())
    arms = '\n'.join(f"| {name} | {row['cycles']:,} | {row['optimizer_updates']:,} | {sum(row['presentations'].values()):,} | {row['selection']['step']:,} |"
                      for name, row in teaching['arms'].items())
    status = 'All frozen qualification gates passed.' if qualification['all_gates'] else (
        'The candidate is preserved with its assessed research role. The earlier qualified owners remain the defaults. '
        'The table below identifies the remaining qualification work.')
    text = f'''# JOINT-020: a retained situation, checked investigation and actual learning

I connected the native learner's language, memory, numerical imagination and
existing choice map in a complete investigation cycle. The learner receives a
human premise and physical observations, answers both questions, considers
interventions, receives a performed outcome and independent credit, and returns
to the original goals. Reward changes actual weights; persistence retains the
updated owner and optimizer. {status}

## What was taught and what was supplied

| Arm | Joint cycles | Optimizer updates | Joint plus rehearsal presentations | Selected cycle |
|---|---:|---:|---:|---:|
{arms}

Each arm received 16,384 mixed episodes and 16,384 rehearsal items. The human
text is from the existing attributable human partitions. The physics is declared
simulation data. The action grid, questions, variables, teachers and assessments
are supplied. Pairing an unrelated human premise with a numerical apparatus is
an engineered interference test; it does not claim the text describes that
apparatus or establishes cross-domain causal grounding.

Both arms started from the same development-selected NATIVE-019 weights, whose
lineage was initialized from scratch. They received identical uniformly selected
training actions and observed measurements. All existing weights could learn.
The `credited` arm additionally received the independently measured policy-reward
term; `withheld` retained the same entropy coefficient and supervised lessons.
There is no added policy head or second memory store. The shared choice readout
learns to score an engineered goal/action relation.

Training uses a recorded uniform behavior probability and a detached importance
ratio for the score-function gradient. The original error reduction and cost are
preserved separately from the clipped training signal. Credit marks can inform
a later query; the final original answer is recorded before its own grade reaches
the state. This order prevents the target's feedback from masquerading as a
prediction made before checking.

## Reserved assessment

Every final human premise group is disjoint from the earlier GENRE-017 and
NATIVE-019 final groups. Both courses finished before these predictions opened.
The same candidate also faced longer histories and shifted controls. The shifted
cohort reuses named held-out human material while changing the simulation; it is
not an extra independent human sample. All final weights stayed fixed.

| Route | Cohort | Human accuracy | Returned goal MSE | Later-query MSE | Measurement rate |
|---|---|---:|---:|---:|---:|
{table}

`uniform`, `disagreement` and `stop` change the investigation selector on the
credited predictor. `erase_history` and `no_imagination` are inference removals,
not separately trained architectures. Independent scalar/decimal calculations
rechecked performed outcomes and reward arithmetic. Utility is negative returned
goal error minus .001 per measurement. This avoids rewarding a weaker initial
answer just because it offers more error to reduce.

| Credited utility minus control | Mean difference | Paired 95% group interval |
|---|---:|---|
{comparisons}

Intervals use 2,000 premise-group resamples and describe these fixed models.
They do not measure variation over training seeds or establish universal ranking.
[Independent metrics and comparisons](INDEPENDENT_METRICS.json).

## Whole-cycle verification and retention

Sixteen development investigations ran through the same continuing owner and
optimizer. **{sum(c['credit']['updated'] for c in delivery['cases'])}** decisions caused
actual reward-driven weight updates. Every update recorded its predictor,
original goal, observation prefix, performed measurement and independent outcome.
The learner re-encoded retained observations under changed weights. A fresh
process restored each saved task, including its next-query answer, and rejected
repeated credit. [Persistent delivery](DELIVERY.json).

The delivery's graded answer is distinguished from the different subsequent
query. Its examples are development evidence, separate from held-out comparisons.
The ordinary native human and physical interfaces were also assessed for
[retention](RETENTION.json), without altering the opened final cohort.
Human reading, worked arithmetic, source passages and interpretation have
separate [development retention diagnostics](BROADER_DEVELOPMENT.json).

| Frozen criterion | Result |
|---|---|
{gates}

[Teaching and sources](TEACHING.json), [actual first-cycle learning replay](LEARNING.json)
and [fresh-process final replay](REPLAY.json) link these claims to execution.
An additional [design audit](ORDER_DIAGNOSIS.json) found that the original
schedule paired text-first histories with quadratic drag and measurements-first
histories with linear drag. This supplies a possible family cue. The preserved
course is therefore scoped to that schedule. Both orders were subsequently
checked on the same development worlds, with fixed weights. This extra check is
labeled post-training diagnosis, not a frozen final criterion. The candidate is
held for a counterbalanced teaching repair; no original final is retuned or erased.
The research checklist remains open for learned concept construction, new
representation attachment, broader perspectives and the other proposed operators.
A successful finite cycle does not replace those required implementations.

## Use, costs and preservation

The [usage guide](../../docs/JOINT_USAGE.md) exposes the exact session interface.
The [checkpoint manifest](../../checkpoints/JOINT-020/MANIFEST.json) preserves
its qualification and research role; all predecessor defaults remain addressable.
Raw human wording, full logs, optimizer/RNG states and intermediate revisions stay
in the local lab. Public delivery records use source identities for human wording.

All successful and failed supervised attempts used one CPU numerical thread and
the 2 GiB process-tree cap. Wall time: **{costs['wall_seconds']/60:.2f} minutes**;
CPU time: **{costs['cpu_seconds']/60:.2f} minutes**; peak recorded process-tree
memory: **{costs['peak_bytes']/1024**2:.1f} MiB**. [Complete costs](COSTS.json).
The predecessor NATIVE-019 training cost is recorded separately and remains part
of the lineage's total acquisition cost. No paid compute or external pretrained
weights were used.
'''
    (folder / 'REPORT.md').write_text(text, encoding='utf-8')
    print(json.dumps({'report': 'reports/JOINT-020/REPORT.md', 'qualified': qualification['all_gates'],
                      'wall_minutes': costs['wall_seconds']/60}), flush=True)


if __name__ == '__main__':
    main()
