"""Publish compact evidence and an inference-only native research checkpoint."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.records import write_json


def read(path): return json.loads(Path(path).read_text())


def main():
    report = ROOT / 'reports/NATIVE-019'; decision = read(report / 'QUALIFICATION.json')
    taught = read(report / 'TEACHING.json'); delivery = read(report / 'DELIVERY.json')
    attempts = [read(p) for p in sorted((ROOT / 'runs').glob('native019-*/state.json'))]
    if not attempts or any(r['status'] == 'RUNNING' for r in attempts):
        raise ValueError('Finish supervised phases before recording their exact costs')
    costs = {'attempts': [{k: v for k, v in r.items() if k != 'sources'} for r in attempts],
        'wall_seconds': sum(r['wall_seconds'] for r in attempts),
        'cpu_seconds': sum(r.get('resources', {}).get('cpu_seconds', 0.) for r in attempts),
        'peak_bytes': max(r.get('resources', {}).get('peak_committed_bytes', 0) for r in attempts)}
    costs['source_preparation'] = read(report / 'SOURCE_PREPARATION.json')
    costs['summed_measured_work_wall_seconds'] = costs['wall_seconds'] + costs['source_preparation']['wall_seconds']
    costs['summed_measured_cpu_seconds'] = costs['cpu_seconds'] + costs['source_preparation']['cpu_seconds']
    write_json(report / 'COSTS.json', costs)
    selected = decision['selected']
    package = read(report / 'PACKAGE.json')
    if not package['exact_tensor_identity']: raise ValueError('Complete the verified inference package first')
    rows = '\n'.join(f"| {arm} | {m['presentations']['semantic']:,} | {sum(m['presentations'].values()):,} | {m['selected']['step']:,} |"
                     for arm, m in taught.items())
    finals = '\n'.join(f"| {route} | {cohort} | " +
        (f"{m['accuracy']:.2%} | {m['loss']:.6f}" if 'accuracy' in m else f"— | MSE {m['mse']:.6f}") + ' |'
        for route, results in decision['metrics'].items() for cohort, m in results.items())
    gates = '\n'.join(f"| {key} | {'Passed' if value else 'Unmet; retained for diagnosis'} |" for key, value in decision['gates'].items())
    track_counts = '\n'.join(f"| {name} | {count:,} | {taught['native']['unique_records'][name]:,} |"
        for name, count in taught['native']['presentations'].items())
    development = read(report / 'BROADER_DEVELOPMENT.json')['tracks']
    dev_table = '\n'.join(f"| {name} | {value['n']} | " +
        (f"{value['accuracy']:.2%}" if 'accuracy' in value else f"MSE {value['mse']:.6f}") + ' |'
        for name, value in development.items())
    text = f'''# NATIVE-019: memory, perception and imagination from the first lesson

I initialized one complete owner from scratch and trained its input encoding,
geometric situation, active memory and conditional answer maps jointly. No earlier
owner or pretrained tensor was loaded. The earlier SERA and field releases remain
preserved. The selected native state is update **{selected['step']:,}**.

## What was taught

| Arm | Human semantic pairs | Total presentations/episodes | Selected update |
|---|---:|---:|---:|
{rows}

The primary arm's distinct records and repeated teaching are counted separately:

| Track | Presentations or episodes | Distinct records or systems |
|---|---:|---:|
{track_counts}

The identical course interleaves human sentence relations, dictionaries,
conversation, grammar, philosophical prose, calculus, programming passages,
reading, worked arithmetic and simulated physical measurements. Each physical
episode supplies four observed force/velocity/acceleration points before three
withheld queries. Source-choice and arithmetic alternatives are engineered task
views. Arithmetic supplies the human worked-step operands. The field learns the
task mappings; the annotations, physical families and assessment are supplied.
The numerical encoder also receives engineered force/velocity product and
squared-velocity coordinates; it never receives the hidden family or coefficients.

`native` has fast/slow/bulk memory throughout. `delayed` retains a basic observed
trace before enabling the richer dynamics halfway through. `trace` keeps the
basic trace for the whole course. Every arm can use the same observations from
its first lesson. They share fresh initialization and ordered examples. This
comparison concerns the specified developmental schedule; it does not assign a
cause to the earlier HISTORY-016 result. The
[pre-training amendment](../../protocols/NATIVE-019-AMENDMENT.md) preserves the
information-access confound corrected before any native numerical result.

## Once-opened final evidence

The human cohorts exclude complete premise groups used by GENRE-017's reserved
assessment. Every arm completed training before these predictions were opened.
The physical namespaces are fresh. All original records and failures are retained.

| Route | Cohort | Accuracy | Log loss or physical MSE |
|---|---|---:|---:|
{finals}

Erasing history, removing bulk, equalizing trace rates and bypassing imagination
are inference interventions on the selected native model. They are not separately
trained architecture comparisons. [Paired premise-group intervals](UNCERTAINTY.json)
describe evaluation sampling for fixed models, not variation over training seeds.
[Physical uses](PHYSICAL_USES.json) additionally check changed-input consequences,
planning, history length and the explicitly supplied exact-basis reference.

## Actual integration and retained task

These broader scores are development diagnostics used during selection. They
are kept separate from the once-opened final tables above.

| Development track | Records or episodes | Result |
|---|---:|---:|
{dev_table}

[Joint learning](JOINT_LEARNING.json) records first-lesson gradients and every
parameter change. [Independent qualification](QUALIFICATION.json) checks the frozen
criteria. [Fresh-process replay](REPLAY.json) preserves exact predictions. The
[architecture](../../docs/NATIVE_ARCHITECTURE.md) explains how the same remembered
state enters human and numerical questions.

| Frozen criterion | Result |
|---|---|
{gates}

The persistent delivery exercised 16 development tasks, recorded actual probes,
checked whether each intervention was performed as requested, independently
graded the original answer and restored the task in a fresh process. Mean goal
MSE changed from **{delivery['before_goal_mse']:.6f}** to
**{delivery['after_goal_mse']:.6f}**; {delivery['positive_credit_cases']} cases earned
positive credit and {delivery['negative_credit_cases']} retained negative progress.
The disagreement selector is fixed; no new policy-weight learning is claimed.
[Full delivery and scoped credit](DELIVERY.json).

## Sources, costs and use

[Teaching identities](TEACHING.json), [source/selection registration](FINAL_REGISTRATION.json),
[storage accounting](STORAGE.json) and [all attempt costs](COSTS.json) are preserved.
Supervised wall time: **{costs['wall_seconds']/60:.2f} minutes**; CPU time:
**{costs['cpu_seconds']/60:.2f} minutes**; peak committed process-tree memory:
**{costs['peak_bytes']/1024**2:.1f} MiB**. Earlier GENRE-017 costs are recorded in its
own report. No paid compute or external pretrained weights were used.

The [packaged native owner](../../checkpoints/NATIVE-019/MANIFEST.json) records its
qualification and research role; the earlier default remains available. See the
[native usage guide](../../docs/NATIVE_USAGE.md) for remembered text and measured
task examples. The [source coverage audit](SOURCE_ALIGNMENT.md) maps this study
back to the requested architecture without treating a component test as the
completion of every research objective.
'''
    (report / 'REPORT.md').write_text(text, encoding='utf-8')
    print(json.dumps({'native_report': 'reports/NATIVE-019/REPORT.md', 'qualified': decision['all_gates'],
                      'source_checkpoint': selected['weights'], 'costs': costs['wall_seconds']}))


if __name__ == '__main__': main()
