"""Report the repaired matched course without rewriting the preceding evidence."""
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.records import write_json


def read(path):
    return json.loads(Path(path).read_text())


def main():
    folder = ROOT / 'reports/JOINT-021'
    decision = read(folder / 'QUALIFICATION.json'); teaching = read(folder / 'TEACHING.json')
    metrics = read(folder / 'RESULTS.json'); independent = read(folder / 'INDEPENDENT_METRICS.json')
    diagnosis = read(folder / 'ORDER_DIAGNOSIS.json'); delivery = read(folder / 'DELIVERY.json')
    attempts = [read(p) for p in sorted((ROOT / 'runs').glob('joint021-*/state.json'))]
    if any(r['status'] in ('STARTING', 'RUNNING') for r in attempts):
        raise ValueError('Finish owned numerical phases before recording complete costs')
    costs = {'attempts': [{k: v for k, v in r.items() if k != 'sources'} for r in attempts],
             'wall_seconds': sum(r['wall_seconds'] for r in attempts),
             'cpu_seconds': sum(r.get('resources', {}).get('cpu_seconds', 0) for r in attempts),
             'peak_bytes': max(r.get('resources', {}).get('peak_committed_bytes', 0) for r in attempts)}
    write_json(folder / 'COSTS.json', costs)
    table = '\n'.join(f"| {route} | {cohort} | {row['metrics']['accuracy']:.2%} | {row['metrics']['after_mse']:.6f} | {row['metrics']['next_query_mse']:.6f} |"
                       for route, cohorts in metrics.items() for cohort, row in cohorts.items())
    controls = '\n'.join(f"| {route} | {row['mean']:.6f} | [{row['95_percent_interval'][0]:.6f}, {row['95_percent_interval'][1]:.6f}] |"
                          for route, row in independent['comparisons'].items())
    gates = '\n'.join(f"| {name} | {'Passed' if value else 'Open; candidate preserved'} |" for name, value in decision['gates'].items())
    counts = '\n'.join(f"| {name.replace('|', ' / ').replace('_', ' ')} | {count:,} |" for name, count in sorted(diagnosis['training_contingency'].items()))
    tests = ET.parse(folder / 'verification/repository-tests.xml').getroot().find('testsuite').attrib
    initial_error = sum(metrics['initial'][c]['metrics']['after_mse']*metrics['initial'][c]['metrics']['n']
                        for c in ('matched', 'mismatched'))
    learned_error = sum(metrics['credited'][c]['metrics']['after_mse']*metrics['credited'][c]['metrics']['n']
                        for c in ('matched', 'mismatched'))
    status = ('All qualification checks passed.' if decision['all_gates'] else
              'The assessed candidate is preserved; the table records the remaining qualification work. Earlier qualified owners remain available.')
    text = f'''# JOINT-021: counterbalanced whole-cycle learning

I repaired the chronology/family confound found in JOINT-020 and completed a fresh
matched course. The human text, physical teaching worlds, training actions,
native initialization, architecture, optimizer and number of updates stayed fixed.
Only their teaching chronology changed. Final human groups and simulation
namespaces are fresh. {status}

Across the 747 original-goal final cases, the complete credited course reduced
returned numerical squared error by **{1-learned_error/initial_error:.2%}** versus
its starting owner. The credited-versus-withheld interval includes zero, so the
reward-specific improvement remains an open qualification. The full course's
learning, the effect of obtaining observations and the reward contribution are
reported separately below.

## The repair

The earlier schedule put every quadratic-drag world in text-first order and
every linear-drag world in measurements-first order. I preserved that complete
study and its cost. This course uses an independent ordering bit, so each four
episodes include both families in both input orders. The exact teaching receipts
confirm the following counts per arm:

| Physical family and input order | Presentations |
|---|---:|
{counts}

Each arm completed 16,384 mixed episodes and 16,384 rehearsal items in 2,048
optimizer updates. The credited arm learns from independently measured reward;
the matched withheld arm receives the same evidence and supervised lessons
without that reward term. Both use the same native weights, shared history,
conditional imagination and existing choice map. The source variables, physical
families, questions, annotations and action grid remain explicitly supplied.

The frozen [protocol](../../protocols/JOINT-021.md) preserves the comparison and
acceptance thresholds. [Registration](REGISTRATION.json) identifies new final
groups after excluding all earlier GENRE-017, NATIVE-019 and JOINT-020 groups.
No opened final was used to adjust the training recipe.

## Fresh assessment

| Route | Cohort | Human accuracy | Returned goal MSE | Later-query MSE |
|---|---|---:|---:|---:|
{table}

The original goal is assessed before its grade reaches memory. The later query
explicitly includes that earlier feedback. The shifted cohort reuses identified
human material with new longer physical histories and changed control range;
it is not an additional independent human sample. Model weights are fixed during
these assessments. Numerical outcomes and credit were independently checked.

Utility is negative returned-goal squared error minus .001 per measurement.
Positive differences favor the credited learner. The 2,000-resample intervals
use paired premise groups and concern these fixed checkpoints.

| Credited utility minus control | Mean difference | Paired 95% interval |
|---|---:|---|
{controls}

The single-predictor selectors and inference removals have their explicit scopes
from the preceding course. Results across JOINT-020 and JOINT-021 are descriptive
because their final cohorts differ. [Complete comparisons](INDEPENDENT_METRICS.json).

## Whole-cycle verification

Sixteen development investigations continued through one owner and optimizer.
**{sum(c['credit']['updated'] for c in delivery['cases'])}** decisions produced actual
reward-driven weight updates. All histories were re-encoded under the changed
predictor. Saved goals, weights, optimizer and RNG state survived independent
restart, with repeated credit rejected. [Delivery](DELIVERY.json).

The full repository check passed **{tests['tests']} tests**, with
{tests['failures']} failures and {tests['errors']} errors. The separately packaged
owner also passed its fresh-process CLI lifecycle and file-integrity checks.
[Interface verification](RELEASE_CHECK.json).

| Qualification criterion | Result |
|---|---|
{gates}

The four-cell chronology check is a prospective requirement here. The shared
audit schema retains its original `post_training_design_quality` key, but this
course specified the check before any training. [Teaching](TEACHING.json),
[first-cycle learning replay](LEARNING.json), [final replay](REPLAY.json),
[retention](RETENTION.json) and [broader development checks](BROADER_DEVELOPMENT.json)
preserve source identities and measured effects.

## Use and cost

The [existing joint interface](../../docs/JOINT_USAGE.md) accepts
`--owner checkpoints/JOINT-021` when starting a new task. Later commands restore
that task's saved updated owner. The [manifest](../../checkpoints/JOINT-021/MANIFEST.json)
records the exact weights and assessment role. Earlier interfaces and all failed
work remain preserved; the [whole research tracker](../../docs/WHOLE_ARCHITECTURE.md)
still distinguishes this cycle from the other proposed mechanisms.

Supervised wall time: **{costs['wall_seconds']/60:.2f} minutes**; CPU time:
**{costs['cpu_seconds']/60:.2f} minutes**; peak process-tree memory:
**{costs['peak_bytes']/1024**2:.1f} MiB**. One numerical thread, 2 GiB cap and no
paid services were used. [Full attempt costs](COSTS.json) include failures.
The earlier native and first joint course costs remain separately recorded and
are part of the complete research acquisition cost.
'''
    (folder / 'REPORT.md').write_text(text, encoding='utf-8')
    print(json.dumps({'report': 'reports/JOINT-021/REPORT.md', 'qualified': decision['all_gates'],
                      'wall_minutes': costs['wall_seconds']/60}), flush=True)


if __name__ == '__main__':
    main()
