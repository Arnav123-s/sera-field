"""Independent final arithmetic, retained-task regression and conditional export.

This script neither trains nor selects the candidate. Failure preserves every
result and leaves the qualified parent available. Run after the frozen campaign.
"""
from collections import Counter
import json
import math
import os
from pathlib import Path
import random
import shutil
import sys

import numpy as np
import torch
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sera_field import extension_tasks as tasks
from sera_field.extension_world import episode
from sera_field.inquiry_study import load_inquiry
from sera_field.model import parameters, weight_hash
from sera_field.records import sha256, write_json
from sera_field.semantic_training import DATA, HumanBank, load_semantic, ENCODER
from sera_field.study_data import load_records
from sera_field.study_training import reading_batch, math_batch, pair_batch
from sera_field.study_world import stable_seed


def read(path):
    return json.loads(Path(path).read_text())


def final_arithmetic(rows):
    probability = np.asarray([r['probability'] for r in rows], dtype=np.float64)
    labels = np.asarray([r['target'] for r in rows])
    if not (np.isfinite(probability).all() and (probability >= 0).all() and
            np.max(np.abs(probability.sum(1) - 1)) < 1e-5):
        raise ValueError('Invalid saved final probability distribution')
    choices = probability.argmax(1); confidence = probability.max(1)
    correct = choices == labels
    confusion = np.zeros((3, 3), dtype='int64')
    for target, choice in zip(labels, choices):
        confusion[target, choice] += 1
    bins = []
    for index in range(10):
        mask = (confidence >= index / 10) & (confidence <= 1 if index == 9 else confidence < (index + 1) / 10)
        n = int(mask.sum())
        bins.append({'lower': index / 10, 'upper': (index + 1) / 10, 'n': n,
                     'accuracy': float(correct[mask].mean()) if n else None,
                     'confidence': float(confidence[mask].mean()) if n else None})
    return {'n': len(rows), 'accuracy': float(correct.mean()),
        'log_loss': float(-np.log(np.maximum(probability[np.arange(len(rows)), labels], 1e-12)).mean()),
        'confusion': confusion.tolist(),
        'brier': float(((probability - np.eye(3)[labels]) ** 2).sum(1).mean()),
        'expected_calibration_error_10_bins': sum(r['n'] / len(rows) * abs(r['accuracy'] - r['confidence']) for r in bins if r['n']),
        'calibration_bins': bins,
        'branch_disagreement': sum(len(set(r['branch_predictions'])) > 1 for r in rows) / len(rows)}


@torch.no_grad()
def retention(owner):
    registration = read(ROOT / 'runs/UNIFIED-012/FINAL_REGISTRATION.json')
    data = ROOT / 'local/CONNECTED-003-data-v1'
    metrics = {}
    for kind, function in (('reading', reading_batch), ('math', math_batch)):
        bank = {r['id']: r for r in load_records(data, 'sealed', kind)}
        scores = [function(owner, [bank[i]]) for i in registration['cohorts'][kind]]
        metrics[kind] = {'n': len(scores), 'accuracy': sum(r[1] for r in scores) / len(scores)}
    metrics['pairs'] = {}; bank = {r['id']: r for r in load_records(data, 'sealed', 'pairs')}
    for track, ids in registration['cohorts']['pairs'].items():
        rows = [bank[i] for i in ids]
        if len(rows) < 4:
            continue
        rng = random.Random(stable_seed('UNIFIED-012-final-v1', track))
        scores = [pair_batch(owner, [r], rows, rng) for r in rows]
        metrics['pairs'][track] = {'n': len(rows), 'accuracy': sum(r[1] for r in scores) / len(rows)}
    return metrics


@torch.no_grad()
def physical_retention(owner):
    """Fresh 128 worlds; exact outcomes stay outside acquisition and qualification."""
    cases = []
    for index in range(128):
        world, adaptation, calibration, queries = episode(index, 'SEMANTIC-015-physical-regression-v1')
        model, assessment = owner.acquire_extension(torch.from_numpy(adaptation)[None], torch.from_numpy(calibration)[None])
        concept = tasks.serialize_model(owner, model, assessment,
            evidence_ids=[f'SEMANTIC-015-physical-{index}-{i}' for i in range(len(adaptation))],
            original_goal={'index': index, 'queries': queries.tolist()})
        prediction = tasks.predict(concept, queries).mean(0)
        truth = world.observe(queries[:, 0], queries[:, 1])
        velocity = float(queries[0, 0]); target = float(truth[0])
        inverse = tasks.inverse(concept, velocity, target)
        changed = queries.copy(); changed[:, 1] += .4
        imagined = tasks.predict(concept, changed).mean(0) - prediction
        actual = world.observe(changed[:, 0], changed[:, 1]) - truth
        def endpoint(control):
            return solve_ivp(lambda t, y: [y[1], world.observe(y[1], control)],
                (0, .4), [0., 0.], method='DOP853', rtol=1e-10, atol=1e-12).y[:, -1]
        target_endpoint = endpoint(float(queries[1, 1])); plan = tasks.plan(concept, target_endpoint)
        point = queries[2].copy(); point[1] = min(float(point[1]), 1.5)
        explanation = tasks.explain(owner, concept, 'What happens when the control input increases?', point)
        changed_point = point.copy(); changed_point[1] += .5
        delta = float(world.observe(*changed_point) - world.observe(*point))
        direction = 2 if delta > .08 else 0 if delta < -.08 else 1
        cases.append({'index': index, 'rank': model['rank'],
            'forward_mse': float(np.mean((prediction - truth) ** 2)),
            'inverse_outcome_error': float((world.observe(velocity, inverse['input']) - target) ** 2),
            'counterfactual_mse': float(np.mean((imagined - actual) ** 2)),
            'planning_mse': float(np.mean((endpoint(plan['input']) - target_endpoint) ** 2)),
            'direction_correct': explanation['direction'] == direction,
            'predictions': prediction.tolist(), 'outcomes': truth.tolist()})
    metrics = {'n': len(cases), **{key: float(np.mean([r[key] for r in cases])) for key in
        ('forward_mse', 'inverse_outcome_error', 'counterfactual_mse', 'planning_mse', 'direction_correct')}}
    return metrics, cases


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1)
    study = ROOT / 'runs/SEMANTIC-015'; report = ROOT / 'reports/SEMANTIC-015'
    report.mkdir(parents=True, exist_ok=True)
    if (report / 'QUALIFICATION.json').exists():
        print('Preserved completed audit; inspect its result rather than repeating it.'); return
    owner, selected = load_semantic(study / 'coupled')
    parent, parent_selection = load_inquiry(ROOT / 'checkpoints/INQUIRY-014')
    owner.eval(); parent.eval(); before = weight_hash(owner)
    protected = {name: bool(torch.equal(parameter, dict(owner.named_parameters())[name]))
        for name, parameter in parent.named_parameters() if not name.startswith((*ENCODER, 'capture_policy.'))}
    registration = read(study / 'FINAL_REGISTRATION.json')
    complete = read(study / 'coupled/COMPLETE.json')
    launch = read(ROOT / 'runs/semantic015-campaign-002/state.json')
    source_checks = {name: sha256(ROOT / name) == digest for name, digest in launch['sources'].items()
                     if name.startswith('sera_field/')}
    source_checks.update({'protocol': sha256(ROOT / 'protocols/SEMANTIC-015.md') == registration['protocol_sha256'],
        'selection': sha256(study / 'coupled/SELECTION.json') == registration['selected_sha256'],
        'human_manifest': sha256(DATA / 'MANIFEST.json') == registration['source_manifest_sha256'],
        'parent': read(study / 'coupled/PARENT.json') == parent_selection})
    # Independently inspect all split identities. Raw text is not published.
    groups = {}; ids = {}; split_counts = {}
    for split in ('train', 'development', 'sealed'):
        groups[split] = set(); ids[split] = set(); split_counts[split] = 0
        with (DATA / f'{split}.jsonl').open(encoding='utf-8') as handle:
            for line in handle:
                record = json.loads(line); split_counts[split] += 1
                if record['id'] in ids[split]:
                    raise ValueError('Duplicate human view identity')
                ids[split].add(record['id']); groups[split].add(record['source_group'])
    split_checks = {a + ':' + b: not (groups[a] & groups[b] or ids[a] & ids[b])
                    for a, b in (('train', 'development'), ('train', 'sealed'), ('development', 'sealed'))}
    source_checks['final_reserved_ids'] = set(registration['ids']) <= ids['sealed']
    bank = HumanBank(DATA / 'train.jsonl', reserve=2048)
    practice_ids = {r['id'] for r in bank.get(bank.reserved)}
    logs = sorted((study / 'coupled').glob('updates-*.jsonl'))
    steps = set(); counts = Counter(); credit_ids = set(); rewards = []; conservation = []
    for path in logs:
        with path.open(encoding='utf-8') as handle:
            for line in handle:
                record = json.loads(line)
                if record['step'] in steps:
                    raise ValueError('Reconcile replayed uncommitted updates before audit')
                steps.add(record['step']); counts['updates'] += 1
                if not math.isfinite(record['loss']):
                    raise ValueError('Nonfinite training loss')
                if record.get('capture'):
                    capture = record['capture']; event = capture['credit']; outcome = event['outcome']
                    if not (capture['lesson_id'] in ids['train'] - practice_ids and
                            set(capture['assessed_ids']) <= practice_ids and len(set(capture['assessed_ids'])) == 12):
                        raise ValueError('Capture practice is not independently reserved training data')
                    counts['capture_assessments'] += 1
                    counts['capture_assessment_presentations'] += 12
                    counts['conditional_capture_choices'] += capture['choice'] == 1
                    if event['accepted']:
                        if outcome['decision'] in credit_ids:
                            raise ValueError('Duplicate accepted capture decision')
                        credit_ids.add(outcome['decision']); counts['accepted_credit'] += 1
                        progress = (outcome['before_loss'] - outcome['after_loss']) / (1 + outcome['before_loss'])
                        if abs(event['reward'] - max(-1., min(1., progress + event['bonus']))) > 1e-12:
                            raise ValueError('Incorrect recorded semantic reward')
                        rewards.append(event['reward'])
                    if capture['capture'] is not None:
                        if not (event['accepted'] and capture['choice'] and
                            capture['after']['accuracy'] >= capture['before']['accuracy'] and
                            capture['after']['loss'] < capture['before']['loss']):
                            raise ValueError('Unqualified curvature capture')
                        counts['curvature_captures'] += 1
                if 'consolidation' in record:
                    counts['consolidations'] += 1; conservation.append(record['consolidation'])
    teaching_checks = {'complete_cursor': steps == set(range(1, complete['updates'] + 1)),
        'full_human_curriculum': complete['exposures']['human_semantic'] == 471139,
        'capture_count': counts['curvature_captures'] == complete['curvature_captures']}
    finals = {}; final_checks = {}
    for arm in ('coupled', 'initialized', 'no_imagination', 'no_curvature', 'hypothesis_only'):
        src = study / 'final' / arm; summary = read(src / 'RESULTS.json')
        rows = [json.loads(line) for line in (src / 'cases.jsonl').read_text().splitlines()]
        independent = final_arithmetic(rows); finals[arm] = independent
        final_checks[arm + '_identities'] = sha256(src / 'cases.jsonl') == summary['cases_sha256']
        final_checks[arm + '_cohort'] = [r['id'] for r in rows] == registration['ids']
        final_checks[arm + '_immutable'] = summary['weights_before'] == summary['weights_after']
        final_checks[arm + '_arithmetic'] = (independent['accuracy'] == summary['accuracy'] and
            independent['confusion'] == summary['confusion'] and abs(independent['log_loss'] - summary['loss']) < 1e-5)
        dest = report / 'final' / arm; dest.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src / 'RESULTS.json', dest / 'RESULTS.json')
        write_json(dest / 'INDEPENDENT_METRICS.json', independent)
    final_checks['exact_replay'] = (sha256(study / 'replay/coupled/cases.jsonl') ==
        read(study / 'replay/coupled/RESULTS.json')['cases_sha256'] == read(study / 'final/coupled/RESULTS.json')['cases_sha256'])
    metrics = retention(owner); reference = read(ROOT / 'reports/INQUIRY-014/RETENTION.json')['metrics']
    retention_checks = {kind: metrics[kind]['accuracy'] >= reference[kind]['accuracy'] - .03 for kind in ('reading', 'math')}
    retention_checks['pairs'] = (np.mean([r['accuracy'] for r in metrics['pairs'].values()]) >=
                                  np.mean([r['accuracy'] for r in reference['pairs'].values()]) - .03)
    physical = {}
    for arm, model in (('candidate', owner), ('parent', parent)):
        physical[arm], cases = physical_retention(model)
        path = study / f'physical-retention-{arm}.jsonl'
        path.write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in cases), encoding='utf-8')
        physical[arm]['cases_sha256'] = sha256(path)
    retention_checks['physical'] = physical['candidate']['forward_mse'] <= 1.15 * physical['parent']['forward_mse']
    gates = {'source_identity': all(source_checks.values()), 'split_integrity': all(split_checks.values()),
        'teaching_integrity': all(teaching_checks.values()), 'final_integrity': all(final_checks.values()),
        'protected_parameters': all(protected.values()), 'retention': all(retention_checks.values()),
        'audit_read_only': weight_hash(owner) == before}
    write_json(report / 'TEACHING.json', {'completion': complete, 'counts': dict(counts),
        'checks': teaching_checks, 'total_capture_reward': sum(rewards), 'conservation': conservation,
        'logs': [{'name': p.name, 'bytes': p.stat().st_size, 'sha256': sha256(p)} for p in logs]})
    write_json(report / 'SPLITS.json', {'counts': split_counts, 'source_group_counts': {k: len(v) for k, v in groups.items()},
        'checks': split_checks, 'capture_practice_ids': sorted(practice_ids), 'source_manifest': read(DATA / 'MANIFEST.json')})
    write_json(report / 'RETENTION.json', {'metrics': metrics, 'reference': reference, 'physical': physical,
        'checks': {k: bool(v) for k, v in retention_checks.items()},
        'scope': 'Opened human cohort for regression only; new registered physical worlds, no training or selection'})
    result = {'gates': {k: bool(v) for k, v in gates.items()}, 'all_gates': bool(all(gates.values())),
        'selection': selected, 'parent_selection': parent_selection, 'source_checks': source_checks,
        'protected_parameters': protected, 'final_checks': final_checks, 'whole_architecture_completed': False}
    write_json(report / 'QUALIFICATION.json', result)
    shutil.copyfile(study / 'FINAL_REGISTRATION.json', report / 'FINAL_REGISTRATION.json')
    shutil.copyfile(study / 'replay/coupled/RESULTS.json', report / 'REPLAY.json')
    if not all(gates.values()):
        raise ValueError('Candidate preserved. Required gate failed; use fresh repair protocol before promotion.')
    target = ROOT / 'checkpoints/SEMANTIC-015'; (target / 'revisions').mkdir(parents=True, exist_ok=True)
    if not (target / 'SELECTION.json').exists():
        temporary = target / 'revisions/export.tmp'
        torch.save({'bridge': {'owner': owner.state_dict(), 'specification': owner.specification()},
            'source_checkpoint_sha256': selected['sha256']}, temporary)
        digest = sha256(temporary); temporary.rename(target / 'revisions' / (digest + '.pt'))
        exported = {**selected, 'sha256': digest, 'revision': digest + '.pt',
            'source_checkpoint_sha256': selected['sha256'], 'role': 'qualified_human_semantic_owner'}
        write_json(target / 'SELECTION.json', exported)
        write_json(target / 'MANIFEST.json', {'selection': exported, 'parameters': parameters(owner),
            'specification': owner.specification(), 'report': 'reports/SEMANTIC-015/REPORT.md',
            'full_training_state': 'runs/SEMANTIC-015/coupled/revisions'})
    exported, _ = load_semantic(target)
    assert weight_hash(exported) == selected['weights']
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
