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
    storage = read(root / 'OWNER_STORAGE.json')
    diagnosis = read(root / 'DIAGNOSIS.json') if (root / 'DIAGNOSIS.json').exists() else None
    diagnostic_text = (f"The retained training log contains {diagnosis['positive_query_progress']:,} positive, "
        f"{diagnosis['negative_query_progress']:,} negative and {diagnosis['zero_query_progress']:,} zero query-loss changes. "
        f"Mean verified training progress was {diagnosis['training_reward']['mean']:.9g}; "
        f"mean probability-vector L1 change was {diagnosis['training_probability_l1_change']['mean']:.9g}. "
        f"The last trained history gain was {diagnosis['last_history_gain']:.9g}. "
        "[DIAGNOSIS.json](DIAGNOSIS.json) records exact initial/latest parameter changes, "
        "regularization, retrieval errors and the complete development curve. "
        "It separates observed evidence from hypotheses about cross-support interference and retrieval relevance. "
        "This inspection opens no new final and changes no selection."
        if diagnosis else 'The exact teaching logs and complete development curve remain available for descriptive diagnosis.')
    recovery_scope = ('Clean, corrupted and erasure-recovered retained history are compared '
        'through the actual returned answer.' if delivery['retained_count'] else
        'No proposal earned factual retention in this delivery. Therefore the runtime '
        'corrupted-history and erasure-recovered-answer comparisons were inapplicable; '
        'the separate mathematical code-recovery tests remain recorded in the test suite.')
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
not separately trained architecture comparisons. At a selected step of zero,
the zero history gain makes returned answers equal to the preserved parent even
when the conditional support dynamics differ. Such a tie documents preservation
and selection; it is not a comparison among successfully trained active memories.
The paired learned-minus-no-history
query-loss difference is **{comparison['paired_query_loss_difference']:.8f}**, with
a percentile interval **{comparison['percentile_95_interval']}** under the recorded
distinct-query-group resampling and fixed support pool. The prospectively frozen
utility gate requires a trained selected step, at least 1% lower log loss and no
more than a two-point accuracy decrease. The opened final changes no threshold,
selection, parameter or factual memory.

{diagnostic_text}

## Actual retention, restart and correction

The fixed eight-case development delivery retained **{delivery['retained_count']}**
independently improved proposals. It reports every positive and negative grade.
Its first performed proposal is deliberately mismatched and must be rejected.
Each query is assessed once; repeated or stale credit is rejected. Retained history
is used only for its original goal. {recovery_scope} Fresh processes resume the same
original goal and evidence record. [DELIVERY.json](DELIVERY.json) supplies each result.

The independent audit checks protected parent parameters and the opened earlier
human regression cohort in an empty new scope. [RETENTION.json](RETENTION.json)
records that comparison. Every final case file has an immutable identity and the
replay matches exactly. Full local revisions retain optimizer/RNG and update cursor.

## Source alignment and costs

[OWNER_STORAGE.json](OWNER_STORAGE.json) separates the latest paper's footprint
categories. Persistent parameters occupy **{storage['parameters']['logical_bytes']:,}
bytes**, and buffers occupy **{storage['buffers']['logical_bytes']:,} bytes**.
One returned field state has **{storage['single_field_boundary']['returned_state']['logical_bytes']:,}
logical bytes**, backed by
**{storage['single_field_boundary']['returned_state']['unique_backing_bytes']:,} bytes**
of storage. The complete one-pair semantic differentiation tape retains
**{storage['semantic_differentiation_tape']['unique_backing_bytes']:,} unique backing
bytes** under its recorded all-parameters-trainable probe. These categories are
distinct from each other, optimizer state and peak process-tree memory. The
small returned state alone is not an entire-system footprint comparison.

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
