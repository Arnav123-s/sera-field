"""Read-only paired premise-group uncertainty for already frozen predictions."""
import json
import os
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sera_field.records import sha256, write_json

ARMS = ('exact_noisy', 'exact_clean', 'gaussian_noisy', 'parent', 'no_imagination', 'no_action')


def read(path):
    return json.loads(Path(path).read_text())


def align(reference, cases):
    indexed = {row['id']: row for row in cases}
    if len(indexed) != len(cases) or set(indexed) != {r['id'] for r in reference}:
        raise ValueError('Paired predictions require exactly the same distinct cases')
    result = [indexed[r['id']] for r in reference]
    if any((a['target'], a['source_group'], a['genre']) !=
           (b['target'], b['source_group'], b['genre']) for a, b in zip(reference, result)):
        raise ValueError('A paired source, genre or annotation differs')
    return result


def case_metrics(rows):
    probability = np.asarray([r['probability'] for r in rows], dtype=np.float64)
    target = np.asarray([r['target'] for r in rows], dtype=np.int64)
    if (probability.shape != (len(rows), 3) or not np.isfinite(probability).all()
            or (probability < 0).any() or np.max(np.abs(probability.sum(1) - 1)) >= 1e-5
            or (target < 0).any() or (target >= 3).any()):
        raise ValueError('Finite saved three-way probabilities and annotations required')
    return np.stack((probability.argmax(1) == target,
                     -np.log(np.maximum(probability[np.arange(len(rows)), target], 1e-12))), -1)


def grouped_replicates(groups, values, rng, count=2000):
    if values.ndim != 3 or len(values) != len(groups) or not len(groups):
        raise ValueError('Expected per-case, per-arm, per-metric observations')
    distinct = sorted(set(groups)); lookup = {g: i for i, g in enumerate(distinct)}
    index = np.asarray([lookup[g] for g in groups])
    totals = np.zeros((len(distinct), *values.shape[1:]), dtype=np.float64)
    np.add.at(totals, index, values)
    sizes = np.bincount(index, minlength=len(distinct))
    sampled = []
    for start in range(0, count, 64):
        chosen = rng.integers(len(distinct), size=(min(64, count - start), len(distinct)))
        sampled.append(totals[chosen].sum(1) / sizes[chosen].sum(1)[:, None, None])
    return np.concatenate(sampled), len(distinct)


def comparisons(means, replicates):
    result = {}
    for i, arm in enumerate(ARMS[1:], 1):
        # Both reported signs mean improvement by the primary candidate.
        delta = np.array([means[0, 0] - means[i, 0], means[i, 1] - means[0, 1]])
        samples = np.stack((replicates[:, 0, 0] - replicates[:, i, 0],
                            replicates[:, i, 1] - replicates[:, 0, 1]), -1)
        interval = np.quantile(samples, [.025, .975], axis=0)
        result[arm] = {name: {'mean': float(delta[j]), 'interval_95': interval[:, j].tolist()}
                       for j, name in enumerate(('accuracy_improvement', 'log_loss_improvement'))}
    return result


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use scripts/supervise.py')
    root = ROOT / 'reports/GENRE-017'
    if not (root / 'QUALIFICATION.json').exists() or not (root / 'REPORT.md').exists():
        raise SystemExit('Complete the active registered sequence first')
    if (root / 'UNCERTAINTY.json').exists():
        raise SystemExit('Preserve the existing once-completed uncertainty analysis')
    registration = read(root / 'FINAL_REGISTRATION.json')
    rng = np.random.default_rng(171170)
    inputs, all_means, all_replicates, result = {}, [], [], {}
    for split in ('matched', 'mismatched'):
        reference = None; values = []; inputs[split] = {}
        for arm in ARMS:
            directory = ROOT / 'runs/GENRE-017/final' / arm / split
            path = directory / 'cases.jsonl'
            digest = sha256(path)
            if digest != read(directory / 'RESULTS.json')['cases_sha256']:
                raise ValueError('A registered prediction file changed')
            rows = [json.loads(line) for line in path.read_text().splitlines()]
            if [r['id'] for r in rows] != registration['ids'][split]:
                raise ValueError('Final identifiers differ from registration')
            reference = rows if reference is None else reference
            rows = align(reference, rows)
            values.append(case_metrics(rows)); inputs[split][arm] = digest
        values = np.stack(values, 1)
        samples, count = grouped_replicates([r['source_group'] for r in reference], values, rng)
        mean = values.mean(0)
        all_means.append(mean); all_replicates.append(samples)
        result[split] = {'rows': len(reference), 'source_groups': count,
                        'comparisons': comparisons(mean, samples)}
    result['equal_cohort_mean'] = comparisons(np.mean(all_means, axis=0), np.mean(all_replicates, axis=0))
    result.update(replicates=2000, seed=171170, input_case_sha256=inputs,
        protocol_sha256=sha256(ROOT / 'protocols/GENRE-017-UNCERTAINTY.md'),
        script_sha256=sha256(__file__), final_registration_sha256=sha256(root / 'FINAL_REGISTRATION.json'),
        numerical_attempt=os.environ['SERA_FIELD_SUPERVISED'],
        scope='paired source-premise sampling for fixed models; not training-seed uncertainty',
        effect_on_selection_or_qualification='none', model_updates=0)
    write_json(root / 'UNCERTAINTY.json', result)
    lines = []
    for split in ('matched', 'mismatched', 'equal_cohort_mean'):
        table = result[split] if split == 'equal_cohort_mean' else result[split]['comparisons']
        for arm, metrics in table.items():
            a, l = metrics['accuracy_improvement'], metrics['log_loss_improvement']
            lines.append(f"| {split} | {arm} | {a['mean']*100:+.2f} "
                f"[{a['interval_95'][0]*100:+.2f}, {a['interval_95'][1]*100:+.2f}] | "
                f"{l['mean']:+.5f} [{l['interval_95'][0]:+.5f}, {l['interval_95'][1]:+.5f}] |")
    (root / 'UNCERTAINTY.md').write_text('''# Paired uncertainty for the fixed GENRE-017 comparison

Positive differences favor the primary exact/noisy candidate. Accuracy is in
percentage points. Brackets contain the prespecified 95% percentile interval.
All sentences from a resampled source premise remain together and all controls
share the same resample. Both reserved cohorts contribute equally to the combined
estimate. These are fixed-model evaluation-sampling intervals; they do not
estimate variation over training seeds or change any frozen qualification gate.

| Cohort | Control | Accuracy improvement [95% interval] | Log-loss improvement [95% interval] |
|---|---|---:|---:|
''' + '\n'.join(lines) + '''

[Protocol](../../protocols/GENRE-017-UNCERTAINTY.md) and
[exact inputs, counts and arithmetic](UNCERTAINTY.json) preserve every comparison.
No training, checkpoint selection or repeated model evaluation occurs here.
''', encoding='utf-8')
    print(json.dumps({'status': 'prespecified_read_only_group_uncertainty_complete', 'model_updates': 0}))


if __name__ == '__main__':
    main()
