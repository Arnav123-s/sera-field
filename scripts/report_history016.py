"""Write the assessed connected-history evidence, including rejection and costs."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.records import write_json


def read(path):
    return json.loads(Path(path).read_text())


def main():
    root = ROOT / 'reports/HISTORY-016'
    qualification = read(root / 'QUALIFICATION.json'); teaching = read(root / 'TEACHING.json')
    delivery = read(root / 'DELIVERY.json'); complete = teaching['complete']; selected = qualification['selected']
    arms = ('learned', 'initialized', 'no_history', 'reciprocal', 'equal_rates')
    outcomes = {arm: read(root / 'final' / arm / 'INDEPENDENT_METRICS.json') for arm in arms}
    attempts = [read(path) for path in sorted((ROOT / 'runs').glob('history016-*/state.json'))]
    if any(row['status'] == 'RUNNING' for row in attempts):
        raise ValueError('Wait for exact supervisor costs before finalizing the report')
    costs = {'attempts': [{k: v for k, v in r.items() if k != 'sources'} for r in attempts],
        'wall_seconds': sum(r['wall_seconds'] for r in attempts),
        'cpu_seconds': sum(r.get('resources', {}).get('cpu_seconds', 0) for r in attempts),
        'peak_bytes': max(r.get('resources', {}).get('peak_committed_bytes', 0) for r in attempts),
        'source_preparation': read(root / 'PREPARATION.json'),
        'shared_test_scope': 'history016 tests also verify the new semantic delivery interface; counted once here'}
    write_json(root / 'COSTS.json', costs)
    table = '\n'.join(f"| {arm} | {r['before']['accuracy']:.2%} | {r['after']['accuracy']:.2%} | "
        f"{r['after']['loss']:.8f} | {r['after']['calibration_error_10_bins']:.6f} |" for arm, r in outcomes.items())
    failed = [k for k, v in qualification['gates'].items() if not v]
    decision = ('The learned procedure passed the frozen qualification gates and was exported as a qualified successor.'
        if qualification['all_gates'] else 'The assessed procedure remains a preserved research candidate. '
        'The earlier qualified semantic owner remains the usable reference. '
        'The recorded failed gates are: ' + ', '.join(failed) + '.')
    comparison = qualification['comparison']
    report = f'''# HISTORY-016 — learned history in the continuing situation field

The continuing owner practiced **{complete['episodes']:,} human-annotated episodes**,
using **{complete['support_presentations']:,} support presentations** and a separate
query after each four-support sequence. Development selected update
**{selected['step']:,}**. Frozen evaluation covered 256 previously unused query
source groups and four controls, followed by an exact replay.

{decision}

## One connected state

The same situation field now receives a history contribution formed by conditional
gauge transport, bidirectional fast/slow traces, opposing evidence traces and two
active conserved concentration fields. These variables feed the existing learned
language and physical computations; there is no separate history answer model.
The earlier owner parameters remain unchanged. The new gain begins at zero, so
the initial owner and every empty task scope preserve the preceding computation.

The conditional flow is an explicitly invertible finite vector-fiber CNF. Its
Jacobian, inverse and local-frame transformation are verified. The active bulk
uses eight semi-implicit NRCH steps per support event. Mass introduced by an
evidence write is distinguished from conserved relaxation; passive energy,
spectral length and signal reconstruction are recorded in every episode.

Retention encodes the same state in finite five-qubit perfect-tensor cells. The
declared noise contract covers one unknown qubit error or two declared erasures
per cell. A checked numerical round trip precedes any write. The stored connection
and flow identity prevent reinterpretation after geometry changes. This simulated
code protects represented values; the external human annotation judges whether
their proposed use improved the answer.

## What was supplied and what was learned

The source is the attributed human SNLI bank prepared for SEMANTIC-015. A supplied,
label-independent lexical selector chooses four source-disjoint supports from
64 deterministic candidates. The first-order annotation gradient supplies the
practice signal. The independent query then trains the new rates, conditional
transport and gain, using negative verified loss improvement plus a small stated
Gaussian KL regularizer. The fixed baseline does not change the cross-entropy
gradient. Neither branch count nor repeated easy success earns a bonus.

The supplied equations, teaching selection, episode boundary and assessor are
engineering. The changed new parameter values and development learning curve are
in [TEACHING.json](TEACHING.json). The query's answer never enters its proposed
history state. Support and query source pools are disjoint within each partition,
and all three partitions are source-disjoint. Previous SEMANTIC-015 final source
groups are excluded from this final. Repeated support exposures remain counted.

## Frozen assessment and controls

| Route | Before accuracy | After accuracy | After log loss | Calibration error |
|---|---:|---:|---:|---:|
{table}

Reciprocal and equal-rate routes are inference ablations of the trained candidate,
not separately trained architecture comparisons. The paired learned-minus-no-history
query-loss difference is **{comparison['paired_query_loss_difference']:.8f}**, with
a percentile interval **{comparison['percentile_95_interval']}** under the recorded
distinct-query-group resampling and fixed support pool. The prospectively frozen
utility gate requires a trained selected step, at least 1% lower log loss and no
more than a two-point accuracy decrease. The opened final changes no threshold,
selection, parameter or factual memory.

## Actual retention, restart and correction

The fixed eight-case development delivery retained **{delivery['retained_count']}**
independently improved proposals. It reports every positive and negative grade.
Its first performed proposal is deliberately mismatched and must be rejected.
Each query is assessed once; repeated or stale credit is rejected. Retained history
is used only for its original goal. Clean, corrupted and erasure-recovered history
are compared through the actual returned answer. Fresh processes resume the same
original goal and evidence record. [DELIVERY.json](DELIVERY.json) supplies each result.

The independent audit checks protected parent parameters and the opened earlier
human regression cohort in an empty new scope. [RETENTION.json](RETENTION.json)
records that comparison. Every final case file has an immutable identity and the
replay matches exactly. Full local revisions retain optimizer/RNG and update cursor.

## Source alignment and costs

[Protocol](../../protocols/HISTORY-016.md),
[equations](../../docs/CONTINUOUS_HISTORY_EQUATIONS.md),
[preflight](PREFLIGHT.md), [qualification](QUALIFICATION.json),
[teaching](TEACHING.json), [registration](FINAL_REGISTRATION.json),
[replay](REPLAY.json) and [costs](COSTS.json) form the evidence chain.

Supervised attempts, including failures and tests, total
**{costs['wall_seconds'] / 60:.2f} wall minutes** and
**{costs['cpu_seconds'] / 60:.2f} CPU minutes**. Peak committed process-tree memory
was **{costs['peak_bytes'] / 1024 ** 2:.1f} MiB**. The separate source preparation
record explicitly preserves its unavailable CPU time rather than counting it as
zero. One numerical CPU thread and the 2 GiB process-tree cap were maintained.

The [whole-architecture tracker](../../docs/WHOLE_ARCHITECTURE.md) remains open for
broader interpretation, transfer, structural concept construction and learning
efficiency. A finite retention or coding result closes only its tested contract.
'''
    (root / 'REPORT.md').write_text(report, encoding='utf-8')
    print(json.dumps({'qualified': qualification['all_gates'], 'failed_gates': failed, 'selected_step': selected['step']}))


if __name__ == '__main__':
    main()
