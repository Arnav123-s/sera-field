"""Independent arithmetic, provenance, matched teaching and native-memory decision."""
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import numpy as np
import torch
from scripts.complete_native019 import ROUTES, cohorts
from scripts.uncertainty_genre017 import grouped_replicates
from sera_field.native_data import NativeData, identity, independent_outcome, GENRE, LEGACY
from sera_field.native_training import STUDY, ARMS, TOTAL, read, load_native, development, source_files, loss_cases
from sera_field.records import sha256, write_json

REPORT = ROOT / 'reports/NATIVE-019'


def teaching(arm, eligible):
    root = STUDY / arm; complete = read(root / 'COMPLETE.json')
    steps = {}; duplicates = 0; logs = []
    for path in sorted(root.glob('updates-*.jsonl')):
        logs.append({'path': str(path.relative_to(ROOT)), 'sha256': sha256(path)})
        for line in path.read_text().splitlines():
            row = json.loads(line)
            if row['step'] in steps:
                if steps[row['step']] != row: raise ValueError('A native replayed training step changed')
                duplicates += 1
            steps[row['step']] = row
    count = Counter(); unique = {}; sequence = hashlib.sha256()
    for step, row in sorted(steps.items()):
        if not math.isfinite(row['loss']): raise ValueError('Nonfinite teaching record')
        sequence.update(json.dumps([step, row['kind'], row['ids']]).encode())
        count[row['kind']] += len(row['ids']); unique.setdefault(row['kind'], set()).update(row['ids'])
    checks = {'every_step': set(steps) == set(range(1, TOTAL+1)),
        'declared_exposures': all(count[k] == v for k, v in complete['exposures'].items() if not k.startswith('pair_track:')),
        'full_budget': sum(count.values()) == TOTAL * 32,
        'actual_human_training_ids': all(unique[k] <= valid for k, valid in eligible.items()),
        'no_parent': not complete['parent_checkpoint_loaded'] and not complete['pretrained_weights_loaded']}
    return {'checks': checks, 'presentations': dict(count), 'unique_records': {k: len(v) for k, v in unique.items()},
            'sequence': sequence.hexdigest(), 'logs': logs, 'replayed_uncommitted_steps': duplicates,
            'selected': complete['selected'], 'initial_weights': complete['initial_weights']}


def independently_assess(route, cohort, kind, source):
    root = STUDY / 'final' / route / cohort; report = read(root / 'RESULTS.json')
    path = root / 'cases.jsonl'
    if sha256(path) != report['cases_sha256']: raise ValueError('Final native predictions changed')
    cases = [json.loads(line) for line in path.read_text().splitlines()]
    if [r['id'] for r in source] != [r['id'] for r in cases]: raise ValueError('Native final row order differs')
    if kind == 'semantic':
        p = np.asarray([r['probabilities'] for r in cases], dtype=np.float64)
        target = np.asarray([r['target'] for r in source])
        if not np.isfinite(p).all() or np.any(p < 0) or np.max(abs(p.sum(-1)-1)) > 1e-5:
            raise ValueError('Invalid native probabilities')
        if any((r['group'], r['target']) != (s['source_group'], s['target']) for r, s in zip(cases, source)):
            raise ValueError('Native annotations differ from the immutable source')
        scores = np.stack((p.argmax(-1) == target, -np.log(np.maximum(p[np.arange(len(target)), target], 1e-12))), -1)
        metrics = {'n': len(cases), 'accuracy': float(scores[:, 0].mean()), 'loss': float(scores[:, 1].mean())}
    else:
        expected = np.asarray([[independent_outcome(row['teacher_only'], *q) for q in row['queries']] for row in source])
        given = np.asarray([r['target'] for r in cases]); predictions = np.asarray([r['prediction'] for r in cases])
        if np.max(abs(expected-given)) > 1e-12 or not np.isfinite(predictions).all():
            raise ValueError('Independent simulated outcome mismatch')
        metrics = {'n': len(cases), 'mse': float(np.mean((predictions-expected)**2))}
        scores = None
    for key, value in metrics.items():
        if abs(value-report['metrics'][key]) > 2e-6: raise ValueError('Independent final arithmetic differs')
    write_json(REPORT / 'final' / route / cohort / 'INDEPENDENT_METRICS.json',
               {**metrics, 'cases_sha256': sha256(path), 'checkpoint': report['checkpoint']['weights']})
    return metrics, cases, scores


def gradients_and_changes(data):
    model, selected, _ = load_native(STUDY / 'native')
    initial, _, _ = load_native(STUDY / 'native', pointer='INITIAL.json')
    params = dict(model.named_parameters()); base = dict(initial.named_parameters())
    delta = {key: float((value-base[key]).double().square().sum().sqrt()) for key, value in params.items()}
    groups = ('words.', 'local.', 'text_source.', 'number_source.', 'field.', 'observation_write.', 'memory.', 'joint_readout.')
    changed = {prefix: sum(value for key, value in delta.items() if key.startswith(prefix)) for prefix in groups}
    # The preflight tests retain their small path probes. Here replay the actual
    # first course batch and objective against its recorded loss/gradient norm.
    kind, rows = data.lesson(0)
    initial.train()
    first_loss, _ = loss_cases(initial, data, kind, rows)
    first_loss.backward()
    gradients = {name: float(p.grad.abs().sum()) if p.grad is not None else 0.
                 for name, p in initial.named_parameters()}
    gradient_norm = math.sqrt(sum(float(p.grad.double().square().sum())
                                  for p in initial.parameters() if p.grad is not None))
    records = []
    for path in sorted((STUDY / 'native').glob('updates-*.jsonl')):
        with path.open(encoding='utf-8') as handle:
            for line in handle:
                record = json.loads(line)
                if record['step'] == 1:
                    records.append(record)
                    break
    if not records or any(record != records[0] for record in records):
        raise ValueError('Missing or inconsistent first native teaching receipt')
    recorded = records[0]
    checks = {
        'same_kind_and_ids': recorded['kind'] == kind and recorded['ids'] == [r['id'] for r in rows],
        'same_loss': math.isclose(float(first_loss.detach()), recorded['loss'], rel_tol=1e-6, abs_tol=1e-7),
        'same_gradient_norm': math.isclose(gradient_norm, recorded['gradient_norm'], rel_tol=1e-5, abs_tol=1e-7),
    }
    if not all(checks.values()):
        raise ValueError('The actual first native learning step did not replay')
    return {'selected_step': selected['step'], 'parameter_change_l2': delta, 'groups_changed': changed,
            'initial_lesson_gradient_l1': gradients,
            'first_course_batch': {'kind': kind, 'ids': recorded['ids'], 'checks': checks,
                                   'loss': float(first_loss.detach()), 'gradient_norm': gradient_norm},
            'note': 'Zero entries are retained. Observed marks receive no invented positive credit.'}


@torch.no_grad()
def physical_uses(owner, source):
    cases = []
    for start in range(0, len(source), 16):
        rows = source[start:start+16]
        support = torch.tensor([r['support'] for r in rows]); state = owner.physical_state(support)
        for length in (1, 2, 4):
            partial = owner.physical_state(support[:, :length])
            query = torch.tensor([r['queries'] for r in rows])
            answer = owner.physical_query(partial, query).mean(-1).numpy()
            for row, prediction in zip(rows, answer):
                error = float(np.mean((prediction-np.asarray(row['targets']))**2))
                cases.append({'id': row['id'], 'history_length': length, 'mse': error})
        queries = np.asarray([r['queries'][0] for r in rows]); changed = queries.copy(); changed[:, 0] += .4
        original = owner.physical_query(state, torch.tensor(queries[:, None], dtype=torch.float32)).mean(-1)[:, 0].numpy()
        altered = owner.physical_query(state, torch.tensor(changed[:, None], dtype=torch.float32)).mean(-1)[:, 0].numpy()
        grid = np.linspace(-1, 1, 17)
        probes = np.stack([np.stack((grid, np.full_like(grid, q[1])), -1) for q in queries])
        predicted = owner.physical_query(state, torch.tensor(probes, dtype=torch.float32)).mean(-1).numpy()
        for i, row in enumerate(rows):
            teacher = row['teacher_only']; actual = independent_outcome(teacher, *queries[i])
            truth = independent_outcome(teacher, *changed[i])-actual
            target = independent_outcome(teacher, .3, queries[i, 1])
            selected = int(np.argmin((predicted[i]-target)**2))
            achieved = independent_outcome(teacher, grid[selected], queries[i, 1])
            all_actual = np.asarray([independent_outcome(teacher, f, queries[i, 1]) for f in grid])
            # The supplied exact basis is an attributed numerical reference.
            measured = np.asarray(row['support']); v = measured[:, 1]
            basis = np.stack((measured[:, 0], v*abs(v) if teacher['quadratic'] else v, np.ones(len(v))), -1)
            fit = np.linalg.lstsq(basis, measured[:, 2], rcond=None)[0]
            q = np.asarray(row['queries']); vv = q[:, 1]
            exact_prediction = np.stack((q[:, 0], vv*abs(vv) if teacher['quadratic'] else vv, np.ones(len(vv))), -1) @ fit
            cases.append({'id': row['id'], 'counterfactual_error': float(((altered[i]-original[i])-truth)**2),
                'direction_correct': bool(np.sign(altered[i]-original[i]) == np.sign(truth)),
                'planning_error': float((achieved-target)**2),
                'oracle_grid_error': float(np.min((all_actual-target)**2)),
                'supplied_basis_mse': float(np.mean((exact_prediction-np.asarray(row['targets']))**2))})
    use = [r for r in cases if 'planning_error' in r]
    return {'n': len(use), 'history_length_mse': {str(length): float(np.mean([r['mse'] for r in cases if r.get('history_length') == length]))
            for length in (1, 2, 4)}, 'uses': {key: float(np.mean([r[key] for r in use])) for key in
            ('counterfactual_error', 'direction_correct', 'planning_error', 'oracle_grid_error', 'supplied_basis_mse')},
            'cases': cases, 'reference_scope': 'Exact least squares receives the correct supplied family basis; NativeOwner does not.'}


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'): raise SystemExit('Use the numerical supervisor')
    torch.set_num_threads(1); registered = read(REPORT / 'FINAL_REGISTRATION.json')
    eligible = {}
    for kind, path in {'semantic': GENRE / 'train.jsonl', 'pairs': LEGACY / 'train-pairs.jsonl',
                       'reading': LEGACY / 'train-reading.jsonl', 'math': LEGACY / 'train-math.jsonl'}.items():
        with path.open(encoding='utf-8') as handle:
            eligible[kind] = {json.loads(line)['id'] for line in handle}
    taught = {arm: teaching(arm, eligible) for arm in ARMS}; write_json(REPORT / 'TEACHING.json', taught)
    matched = len({r['sequence'] for r in taught.values()}) == len({r['initial_weights'] for r in taught.values()}) == 1
    metrics = {}; raw = {}; uncertainty = {}; rng = np.random.default_rng(191190)
    for cohort, (kind, source) in cohorts().items():
        if identity(source) != registered['cohorts'][cohort]['source_rows_sha256']: raise ValueError('Registered cohort changed')
        values = []
        for route in ROUTES:
            m, cases, scores = independently_assess(route, cohort, kind, source)
            metrics.setdefault(route, {})[cohort] = m; raw[route, cohort] = cases
            if route in ('native', 'delayed') and kind == 'semantic': values.append(scores)
        if kind == 'semantic':
            sample, groups = grouped_replicates([r['source_group'] for r in source], np.stack(values, 1), rng)
            samples = sample[:, 0, 0]-sample[:, 1, 0]
            uncertainty[cohort] = {'groups': groups, 'native_minus_delayed_accuracy':
                metrics['native'][cohort]['accuracy']-metrics['delayed'][cohort]['accuracy'],
                'interval_95': np.quantile(samples, [.025, .975]).tolist()}
    write_json(REPORT / 'UNCERTAINTY.json', {'comparisons': uncertainty, 'replicates': 2000, 'seed': 191190,
        'scope': 'Paired source-premise uncertainty for fixed models; no training-seed variance.'})
    data = NativeData()
    changes = gradients_and_changes(data); write_json(REPORT / 'JOINT_LEARNING.json', changes)
    model, selected, training_payload = load_native(STUDY / 'native')
    uses = physical_uses(model, cohorts()['physics'][1]); write_json(REPORT / 'PHYSICAL_USES.json', uses)
    broader = development(model, data)
    write_json(REPORT / 'BROADER_DEVELOPMENT.json', {'scope': 'Already used development diagnostics; not new final evidence', **broader})
    mean = lambda route: np.mean([metrics[route][s]['accuracy'] for s in ('matched', 'mismatched')])
    source_checks = {path: sha256(ROOT / path) == expected
                     for path, expected in registered['sources']['implementation'].items()}
    source_checks['runner'] = sha256(ROOT / 'scripts/complete_native019.py') == registered['sources']['runner_sha256']
    source_checks['protocol'] = sha256(ROOT / 'protocols/NATIVE-019.md') == registered['sources']['prospective_protocol']
    source_checks['amendment'] = sha256(ROOT / 'protocols/NATIVE-019-AMENDMENT.md') == registered['sources']['prospective_amendment']
    checks = {'matched_fresh_teaching': matched, 'source_identity': all(source_checks.values()),
        'complete_teaching': all(all(r['checks'].values()) for r in taught.values()),
        'selected_learned_state': selected['step'] > 0,
        'semantic_learning': mean('native') >= mean('initial')+.05,
        'semantic_history_use': mean('native') >= mean('erase_history')+.05,
        'physical_history_use': metrics['native']['physics']['mse'] <= .75*metrics['erase_history']['physics']['mse'],
        'all_core_groups_updated': all(v > 0 for v in changes['groups_changed'].values()),
        'exact_replay': read(REPORT / 'REPLAY.json')['exact']}
    delivery = REPORT / 'DELIVERY.json'
    checks['persistent_checked_delivery'] = delivery.exists() and all(read(delivery)['checks'].values())
    tests = sorted((ROOT / 'runs').glob('native019-tests-*/state.json'))
    required = {**source_files(), **{name: sha256(ROOT / name) for name in
        ('sera_field/native_session.py', 'sera_field/native_cli.py', 'tests/test_native_owner.py', 'tests/test_native_session.py')}}
    test_evidence = {str(p.relative_to(ROOT)): read(p)['status'] == 'PASS' and read(p).get('lease_released') and
                     all(read(p)['sources'].get(name) == digest for name, digest in required.items()) for p in tests}
    checks['engineering_tests'] = any(test_evidence.values())
    checks = {key: bool(value) for key, value in checks.items()}
    result = {'gates': checks, 'all_gates': all(checks.values()), 'metrics': metrics,
              'source_checks': source_checks, 'test_evidence': test_evidence,
              'selected': selected, 'default_predecessor_preserved': True,
              'scope': 'Fresh joint training in the specified curriculum; no replacement from unequal historical training.'}
    write_json(REPORT / 'QUALIFICATION.json', result)
    parameters = sum(p.numel()*p.element_size() for p in model.parameters())
    buffers = sum(p.numel()*p.element_size() for p in model.buffers())
    state = model.empty(1)
    storage = {'parameters': sum(p.numel() for p in model.parameters()), 'parameter_bytes': parameters,
        'buffer_bytes': buffers, 'returned_state_bytes': sum(v.numel()*v.element_size() for v in state.values() if isinstance(v, torch.Tensor)),
        'optimizer_tensor_bytes': sum(v.numel()*v.element_size()
            for slot in training_payload['optimizer']['state'].values() for v in slot.values()
            if isinstance(v, torch.Tensor)),
        'torch_rng_tensor_bytes': training_payload['rng'].numel()*training_payload['rng'].element_size(),
        'training_revision_bytes': (STUDY / 'native/revisions' / selected['revision']).stat().st_size,
        'process_tree_resources': 'COSTS.json',
        'per_arm_cpu_measured': False,
        'cost_scope': 'The supervisor measures the full three-arm campaign, all evaluations and replays together. Equal updates do not imply equal FLOPs.'}
    write_json(REPORT / 'STORAGE.json', storage)
    print(json.dumps({'qualified_native_memory': result['all_gates'], 'gates': checks, 'storage': storage}))


if __name__ == '__main__': main()
