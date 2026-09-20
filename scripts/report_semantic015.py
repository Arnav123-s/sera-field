"""Report completed human teaching, controls and qualification without retuning."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.records import write_json


def read(path):
    return json.loads(Path(path).read_text())


def main():
    report = ROOT / 'reports/SEMANTIC-015'
    qualification = read(report / 'QUALIFICATION.json')
    teaching = read(report / 'TEACHING.json'); complete = teaching['completion']
    retention = read(report / 'RETENTION.json')
    arms = ('coupled', 'initialized', 'no_imagination', 'no_curvature', 'hypothesis_only')
    metrics = {arm: read(report / 'final' / arm / 'INDEPENDENT_METRICS.json') for arm in arms}
    final = metrics['coupled']; selected = qualification['selection']
    delivery = read(report / 'DELIVERY.json')
    delivered_credit = read(ROOT / 'local/SEMANTIC-015-delivery/observed-result.json')['performed_measurement']['credit']
    write_json(report / 'DELIVERY_CREDIT.json', delivered_credit)
    selected_captures = 0
    for path in sorted((ROOT / 'runs/SEMANTIC-015/coupled').glob('updates-*.jsonl')):
        for line in path.read_text().splitlines():
            row = json.loads(line)
            selected_captures += (row['semantic_step'] <= selected['semantic_step'] and
                row.get('capture') is not None and row['capture'].get('capture') is not None)
    attempts = [read(p) for p in sorted((ROOT / 'runs').glob('semantic015-*/state.json'))]
    if any(row['status'] == 'RUNNING' for row in attempts):
        raise ValueError('Preserve the active job; finalize costs after it completes')
    costs = {'attempts': [{k: v for k, v in row.items() if k != 'sources'} for row in attempts],
        'wall_seconds': sum(row['wall_seconds'] for row in attempts),
        'cpu_seconds': sum(row.get('resources', {}).get('cpu_seconds', 0) for row in attempts),
        'peak_bytes': max(row.get('resources', {}).get('peak_committed_bytes', 0) for row in attempts),
        'source_preparation': complete['source_manifest'],
        'shared_targeted_tests': 'inquiry014-semantic015-tests-001 is counted in INQUIRY-014/COSTS.json, not again here'}
    write_json(report / 'COSTS.json', costs)
    table = '\n'.join(f"| {arm} | {m['accuracy']:.2%} | {m['log_loss']:.5f} | "
        f"{m['expected_calibration_error_10_bins']:.5f} | {m['branch_disagreement']:.2%} |" for arm, m in metrics.items())
    retained_table = '\n'.join(f"| {kind} | {retention['reference'][kind]['accuracy']:.2%} | "
        f"{retention['metrics'][kind]['accuracy']:.2%} |" for kind in ('reading', 'math'))
    physical = retention['physical']
    physical_table = '\n'.join(f"| {key} | {physical['parent'][key]:.7f} | {physical['candidate'][key]:.7f} |"
        for key in ('forward_mse', 'inverse_outcome_error', 'counterfactual_mse', 'planning_mse', 'direction_correct'))
    verdict = ('The candidate passed every prospective qualification gate and was exported for use.'
               if qualification['all_gates'] else
               'The complete candidate and results are preserved. The failed qualification gates are recorded below; '
               'the earlier qualified owner remains available while a fresh repair is prepared.')
    failed = [key for key, value in qualification['gates'].items() if not value]
    text = f'''# SEMANTIC-015 — human meaning through the continuing field

The continuing owner was taught **{complete['exposures']['human_semantic']:,} human-written
sentence pairs** and reached **{final['accuracy']:.2%}** accuracy on 4,096 reserved
human-annotated cases. It reads a premise and evaluates whether a proposed
statement follows, conflicts, or needs additional information. Learned conditional
continuations use the same situation field as its physical acquisition and earlier
reading, mathematics and source-pair routes.

{verdict}

## Source, teaching and learned state

The source is [SNLI 1.0, Bowman et al.](https://nlp.stanford.edu/projects/snli/),
with human-written sentences and manual annotations, attributed under CC BY-SA 4.0.
Original archive SHA-256:
`afb3d70a5af5d8de0d9d81e2637e0fb8c22d1235c2749d83125ca43dab0dbd3e`.
Original text stayed unchanged on disk. The preparation removed 76,180 training
pairs whose image/caption groups were reserved, leaving 473,187 eligible training
pairs, 9,456 development pairs and 9,824 sealed pairs. The independent audit checked
source-group separation again. A label describes a relation conditional on a stated
premise; it does not establish that the premise occurred.

The teaching schedule processed 471,139 primary pairs once, with 2,048 other
training IDs reserved for capture practice. It ran **{complete['semantic_updates']:,}
semantic updates** and **{complete['updates']:,} total updates**, rotating earlier
reading, mathematics, dictionary/conversation/grammar/philosophy/calculus/code and
physical-simulation rehearsal. Exact per-track counts are in [TEACHING.json](TEACHING.json).
Development selected semantic update **{selected['semantic_step']:,}**; no final
outcome selected or trained that revision.

New semantic mappings and curvature coupling were trained first. After 1,024
semantic batches, the existing word encoder also learned, with rehearsal. The
earlier physical operators and remaining parent parameters stayed protected. The
entire model lineage started in this independent lab from initialized weights;
this curriculum imported no pretrained encoder and used no next-token loss.

## Connected imagination and retention

An observed boundary settles from the premise. The hypothesis and that state feed
three learned conditional continuations, and the label readout consumes their
actual resulting field states. Three branches are supplied architecture; they are
not counted as three independent scientific discoveries.

Closed-loop products of the transported connections produce actual holonomy tags.
Their local-frame covariance and derivatives are checked mathematically. A typed
curvature memory region feeds those recalled tags back into the same boundary
before stationary, covariance and temporal processing. A conditional capture is
assessed on separate human-annotated practice records. Positive checked progress
with no accuracy reduction qualifies retention. Existing source, original-goal,
predictor and duplicate-credit protections remain.

The run completed **{teaching['counts'].get('capture_assessments', 0)}** capture assessments,
**{teaching['counts'].get('curvature_captures', 0)}** qualified curvature captures and
**{teaching['counts'].get('consolidations', 0)}** coupled consolidation events. Their
conservation diagnostics, rewards, negative attempts and source identities are
preserved. The selected checkpoint includes **{selected_captures}** captures; later
practice remains in the complete training history. Whether this memory improved prediction is assessed by the disconnected
curvature control below, rather than inferred from its presence.

## Independent final assessment

The initialized head and the inference ablations share the same defined task and
source cohort. These are dependence checks within this model, not equal-training
comparisons with other model families.

| Assessed route | Accuracy | Log loss | Calibration error, 10 bins | Branch disagreement |
|---|---:|---:|---:|---:|
{table}

Per-label confusion, Brier scores and calibration-bin counts are in each arm's
`INDEPENDENT_METRICS.json`. Saved probabilities were checked with a separate
calculation. The final process performed no parameter or memory updates; its
fresh-process replay has matching case identities.

## Earlier abilities and physical use

The prospectively retained human cohort was used only for regression, not as a new
generalization result or as training data in this audit.

| Retained task | Qualified parent | Semantic candidate |
|---|---:|---:|
{retained_table}

The complete conversation/dictionary pair results are in [RETENTION.json](RETENTION.json).
A separately registered set of 128 new physical systems checks all five uses of
the acquired relationship against the same qualified parent:

| Physical measure | Parent | Candidate |
|---|---:|---:|
{physical_table}

Qualification gates failing this assessment: **{', '.join(failed) if failed else 'none'}**.
These outcomes neither alter the frozen selection nor disappear from the record.

## Usable interpretation and continuing task

The [usage guide](../../docs/SEMANTIC_USAGE.md) exposes conditional statement
interpretation and the measured investigation actions using this qualified owner.
The fresh-process [delivery](DELIVERY.json) correctly identified that the selected
human hypothesis needed additional information. It preserved the original measured
goal while reading that sentence and resumed its state exactly.

In this single delivery, the next measurement changed original-task MSE from
**{delivery['initial_original_goal_mse']:.8f}** to **{delivery['returned_original_goal_mse']:.8f}**.
The independently checked policy reward was **{delivered_credit['reward']:.8f}**,
with the actual update and complete identities in [DELIVERY_CREDIT.json](DELIVERY_CREDIT.json).
This event remains part of the record alongside the full frozen cohort. Delivery
checks persistence and evidence-bound credit. Both positive and negative grades
remain available for subsequent procedure research.

## Evidence and continuation

[Protocol](../../protocols/SEMANTIC-015.md), [source/split audit](SPLITS.json),
[teaching](TEACHING.json), [qualification](QUALIFICATION.json),
[registration](FINAL_REGISTRATION.json), [replay](REPLAY.json),
[preserved repairs](REPAIRS.md) and [costs](COSTS.json) provide the claim chain.
All attempted revisions, optimizer/RNG state and exact sampler position remain
in `runs/SEMANTIC-015/coupled/revisions` locally. Source preparation costs are
separate from supervised model work, and failed attempts are included.

The new unified-history addendum is implemented against this same owner, with a
[prospective protocol](../../protocols/HISTORY-016.md) and explicit
[state equations](../../docs/CONTINUOUS_HISTORY_EQUATIONS.md). Its fast/slow traces,
active bulk and protected representation must pass their own connected learning
and evidence checks. The full [research behavior checklist](../../docs/WHOLE_ARCHITECTURE.md)
remains the governing objective across these studies.
'''
    (report / 'REPORT.md').write_text(text, encoding='utf-8')
    print(json.dumps({'accuracy': final['accuracy'], 'qualified': qualification['all_gates'], 'failed_gates': failed}))


if __name__ == '__main__':
    main()
