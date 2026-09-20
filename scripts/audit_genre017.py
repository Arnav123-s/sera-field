"""Read-only source, teaching, final arithmetic and retained-task audit."""
import argparse
from collections import Counter
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import shutil
import sys

import numpy as np
import torch
from scipy.integrate import solve_ivp

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from scripts.audit_semantic015 import final_arithmetic, retention
from sera_field import extension_tasks as tasks
from sera_field.extension_world import episode
from sera_field.genre_training import (ARMS, DATA, STUDY, ENCODER, NEW, assess,
    final_rows, load_genre, parent_owner, sources)
from sera_field.model import parameters, weight_hash
from sera_field.records import sha256, write_json
from sera_field.semantic_training import HumanBank


def read(path): return json.loads(Path(path).read_text())


@torch.no_grad()
def physical_retention(owner):
    cases = []
    for index in range(128):
        world, adaptation, calibration, queries = episode(index, 'GENRE-017-retention')
        model, qualified = owner.acquire_extension(torch.from_numpy(adaptation)[None], torch.from_numpy(calibration)[None])
        concept = tasks.serialize_model(owner, model, qualified,
            evidence_ids=[f'GENRE-017-retention:{index}:{i}' for i in range(len(adaptation))],
            original_goal={'index': index, 'queries': queries.tolist()})
        prediction = tasks.predict(concept, queries).mean(0)
        truth = world.observe(queries[:, 0], queries[:, 1])
        inverse = tasks.inverse(concept, float(queries[0, 0]), float(truth[0]))
        changed = queries.copy(); changed[:, 1] += .4
        imagined = tasks.predict(concept, changed).mean(0) - prediction
        actual = world.observe(changed[:, 0], changed[:, 1]) - truth
        def endpoint(control):
            return solve_ivp(lambda t, y: [y[1], world.observe(y[1], control)],
                (0, .4), [0., 0.], method='DOP853', rtol=1e-10, atol=1e-12).y[:, -1]
        desired = endpoint(float(queries[1, 1])); plan = tasks.plan(concept, desired)
        point = queries[2].copy(); point[1] = min(float(point[1]), 1.5)
        explanation = tasks.explain(owner, concept, 'What happens when the control input increases?', point)
        altered = point.copy(); altered[1] += .5
        delta = float(world.observe(*altered) - world.observe(*point))
        direction = 2 if delta > .08 else 0 if delta < -.08 else 1
        cases.append({'index': index, 'selected_rank': model['rank'],
            'forward_mse': float(np.mean((prediction - truth) ** 2)),
            'inverse_outcome_error': float((world.observe(queries[0, 0], inverse['input']) - truth[0]) ** 2),
            'counterfactual_mse': float(np.mean((imagined - actual) ** 2)),
            'planning_mse': float(np.mean((endpoint(plan['input']) - desired) ** 2)),
            'direction_correct': explanation['direction'] == direction,
            'predictions': prediction.tolist(), 'outcomes': truth.tolist()})
    keys = ('forward_mse', 'inverse_outcome_error', 'counterfactual_mse', 'planning_mse', 'direction_correct')
    result = {key: float(np.mean([r[key] for r in cases])) for key in keys}
    if not all(math.isfinite(v) for v in result.values()): raise ValueError('Nonfinite retained physical outcome')
    return {'n': len(cases), **result}, cases


def split_audit():
    groups = {}; identifiers = {}; count = {}
    manifest = read(DATA / 'MANIFEST.json')
    for split in manifest['partitions']:
        groups[split] = set(); identifiers[split] = set(); count[split] = 0
        path = DATA / (split + '.jsonl')
        if sha256(path) != manifest['partitions'][split]['sha256']: raise ValueError('Source view changed')
        with path.open(encoding='utf-8') as handle:
            for line in handle:
                row = json.loads(line); count[split] += 1
                if row['id'] in identifiers[split]: raise ValueError('Duplicate source identity')
                groups[split].add(row['source_group']); identifiers[split].add(row['id'])
    checks = {a + ':' + b: not (groups[a] & groups[b] or identifiers[a] & identifiers[b])
              for a, b in itertools.combinations(groups, 2)}
    checks['counts'] = all(count[k] == v['rows'] for k, v in manifest['partitions'].items())
    return {'counts': count, 'group_counts': {k: len(v) for k, v in groups.items()}, 'checks': checks}, identifiers


def teaching_audit(arm, primary_ids):
    root = STUDY / arm; complete = read(root / 'COMPLETE.json')
    steps = {}; duplicate_replays = 0; logs = []
    for path in sorted(root.glob('updates-*.jsonl')):
        logs.append({'path': str(path.relative_to(ROOT)), 'sha256': sha256(path), 'bytes': path.stat().st_size})
        with path.open(encoding='utf-8') as handle:
            for line in handle:
                row = json.loads(line)
                if row['step'] in steps:
                    if steps[row['step']] != row: raise ValueError('A resumed teaching step differs; reconcile before promotion')
                    duplicate_replays += 1
                steps[row['step']] = row
    sequence = hashlib.sha256(); taught = Counter(); count = Counter()
    for step, row in sorted(steps.items()):
        if not math.isfinite(row['loss']): raise ValueError('Nonfinite logged teaching loss')
        count[row['kind']] += len(row['ids'])
        sequence.update(json.dumps([step, row['kind'], row['ids']], separators=(',', ':')).encode())
        if row['kind'] == 'human_genre': taught.update(row['ids'])
    checks = {'exact_cursor': set(steps) == set(range(1, complete['updates'] + 1)),
        'all_primary_once': set(taught) == primary_ids and set(taught.values()) == {1},
        'declared_primary': complete['exposures']['human_genre'] == count['human_genre'] == 371929,
        'declared_rehearsal': all(complete['exposures'].get('rehearsal:' + k) == v
                                  for k, v in count.items() if k != 'human_genre')}
    return {'complete': complete, 'counts': dict(count), 'checks': checks,
            'matched_exposure_sequence': sequence.hexdigest(), 'replayed_uncommitted_steps': duplicate_replays, 'logs': logs}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--test-attempt', required=True)
    parser.add_argument('--campaign-attempt', required=True); args = parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'): raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1); report = ROOT / 'reports/GENRE-017'; report.mkdir(parents=True, exist_ok=True)
    if (report / 'QUALIFICATION.json').exists():
        print('Preserved completed genre audit'); return
    owner, selected = load_genre(STUDY / 'exact_noisy'); parent, parent_selection = parent_owner()
    owner.eval(); parent.eval(); before = weight_hash(owner)
    registration = read(STUDY / 'FINAL_REGISTRATION.json'); launch = read(ROOT / 'runs' / args.campaign_attempt / 'state.json')
    tests = read(ROOT / 'runs' / args.test_attempt / 'state.json')
    source_checks = {name: sha256(ROOT / name) == value for name, value in launch['sources'].items()
                     if name.startswith('sera_field/')}
    source_checks.update(registered_sources=sources() == registration['sources'], parent=parent_selection == registration['parent'])
    source_checks['matched_initial_weights'] = len({read(STUDY / arm / 'INITIAL.json')['weights'] for arm in ARMS}) == 1
    source_checks['matched_registered_parents'] = all(read(STUDY / arm / 'PARENT.json') == parent_selection for arm in ARMS)
    source_checks['matched_registered_sources'] = all(read(STUDY / arm / 'SOURCES.json') == registration['sources'] for arm in ARMS)
    test_files = ('sera_field/finite_neural_action.py', 'sera_field/genre_owner.py',
                  'sera_field/genre_training.py', 'tests/test_finite_neural_action.py', 'tests/test_genre_training.py')
    tested = tests['status'] == 'PASS' and all(tests['sources'].get(name) == sha256(ROOT / name) for name in test_files)
    protected = {name: bool(torch.equal(p, dict(owner.named_parameters())[name]))
                 for name, p in parent.named_parameters() if not name.startswith((*NEW, *ENCODER))}
    splits, identifiers = split_audit()
    teaching = {arm: teaching_audit(arm, identifiers['train']) for arm in ARMS}
    matched = len({v['matched_exposure_sequence'] for v in teaching.values()}) == 1
    truth = {split: {r['id']: r for r in rows} for split, rows in final_rows().items()}
    finals = {}; final_checks = {}
    for arm in (*ARMS, 'parent', 'no_imagination', 'no_action'):
        finals[arm] = {}
        for split in truth:
            src = STUDY / 'final' / arm / split; result = read(src / 'RESULTS.json')
            rows = [json.loads(line) for line in (src / 'cases.jsonl').read_text().splitlines()]
            if any((r['target'], r['source_group'], r['genre']) !=
                   (truth[split][r['id']]['target'], truth[split][r['id']]['source_group'], truth[split][r['id']]['genre']) for r in rows):
                raise ValueError('Final output differs from independent human source annotation')
            independent = final_arithmetic(rows)
            independent['by_genre'] = {genre: final_arithmetic([r for r in rows if r['genre'] == genre])
                                       for genre in sorted({r['genre'] for r in rows})}
            finals[arm][split] = independent; key = arm + ':' + split
            final_checks[key] = (sha256(src / 'cases.jsonl') == result['cases_sha256'] and
                [r['id'] for r in rows] == registration['ids'][split] and
                result['weights_before'] == result['weights_after'] and
                abs(independent['log_loss'] - result['loss']) < 1e-5 and independent['accuracy'] == result['accuracy'])
            dest = report / 'final' / arm / split; dest.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src / 'RESULTS.json', dest / 'RESULTS.json'); write_json(dest / 'INDEPENDENT_METRICS.json', independent)
    final_checks['replay'] = all(sha256(STUDY / 'replay/exact_noisy' / split / 'cases.jsonl') ==
        read(STUDY / 'replay/exact_noisy' / split / 'RESULTS.json')['cases_sha256'] ==
        read(STUDY / 'final/exact_noisy' / split / 'RESULTS.json')['cases_sha256'] for split in truth)
    retained = {}; physical = {}
    old_registration = read(ROOT / 'runs/SEMANTIC-015/FINAL_REGISTRATION.json')
    old_bank = HumanBank(ROOT / 'local/SEMANTIC-015-data-v1/sealed.jsonl')
    all_old = {r['id']: r for r in old_bank.get(range(len(old_bank.offsets)))}
    old_rows = [all_old[i] for i in old_registration['ids']]
    for arm, model in (('candidate', owner), ('parent', parent)):
        retained[arm] = retention(model)
        # The historical cohort is regression only. Its identities are unchanged.
        from sera_field.semantic_training import assessment
        retained[arm]['semantic'], _ = assessment(model, old_rows)
        physical[arm], cases = physical_retention(model)
        path = STUDY / ('physical-retention-' + arm + '.jsonl')
        path.write_text(''.join(json.dumps(r, sort_keys=True) + '\n' for r in cases), encoding='utf-8')
        physical[arm]['cases_sha256'] = sha256(path)
    retention_checks = {name: retained['candidate'][name]['accuracy'] >= retained['parent'][name]['accuracy'] - .03
                        for name in ('reading', 'math', 'semantic')}
    retention_checks['pairs'] = np.mean([r['accuracy'] for r in retained['candidate']['pairs'].values()]) >= \
                                np.mean([r['accuracy'] for r in retained['parent']['pairs'].values()]) - .03
    retention_checks.update({name: physical['candidate'][name] <= 1.1 * physical['parent'][name] + 1e-5
                            for name in ('forward_mse', 'counterfactual_mse', 'planning_mse')})
    retention_checks['direction'] = physical['candidate']['direction_correct'] >= physical['parent']['direction_correct'] - .02
    average = lambda arm, key: sum(v[key] for v in finals[arm].values()) / 2
    useful = (selected['semantic_step'] > 0 and
        average('exact_noisy', 'accuracy') >= average('parent', 'accuracy') + .02 and
        average('exact_noisy', 'log_loss') <= .98 * average('parent', 'log_loss'))
    delivery = read(report / 'DELIVERY.json')
    gates = {'tested_mechanism': tested, 'sources': all(source_checks.values()),
        'splits': all(splits['checks'].values()), 'matched_teaching': matched and all(all(v['checks'].values()) for v in teaching.values()),
        'finals': all(final_checks.values()), 'protected_parameters': all(protected.values()),
        'retention': bool(all(retention_checks.values())), 'useful_new_human_learning': useful,
        'persistent_delivery': all(delivery['checks'].values()), 'read_only': weight_hash(owner) == before}
    write_json(report / 'TEACHING.json', teaching); write_json(report / 'SPLITS.json', splits)
    write_json(report / 'RETENTION.json', {'metrics': retained, 'physical': physical,
        'checks': {k: bool(v) for k, v in retention_checks.items()}})
    result = {'gates': {k: bool(v) for k, v in gates.items()}, 'all_gates': bool(all(gates.values())),
        'selected': selected, 'parent': parent_selection, 'source_checks': source_checks,
        'protected_parameters': protected, 'final_checks': final_checks, 'whole_architecture_completed': False}
    write_json(report / 'QUALIFICATION.json', result)
    shutil.copyfile(STUDY / 'FINAL_REGISTRATION.json', report / 'FINAL_REGISTRATION.json')
    if result['all_gates']:
        target = ROOT / 'checkpoints/GENRE-017'; (target / 'revisions').mkdir(parents=True, exist_ok=True)
        if not (target / 'SELECTION.json').exists():
            temporary = target / 'revisions/export.tmp'
            torch.save({'bridge': {'owner': owner.state_dict(), 'specification': owner.specification()},
                'source_checkpoint_sha256': selected['sha256']}, temporary)
            digest = sha256(temporary); temporary.rename(target / 'revisions' / (digest + '.pt'))
            exported = {**selected, 'sha256': digest, 'revision': digest + '.pt',
                'source_checkpoint_sha256': selected['sha256'], 'role': 'qualified_broader_human_interpretation_owner'}
            write_json(target / 'SELECTION.json', exported)
            write_json(target / 'MANIFEST.json', {'selection': exported, 'parameters': parameters(owner),
                'specification': owner.specification(), 'report': 'reports/GENRE-017/REPORT.md',
                'full_training_state': 'runs/GENRE-017/exact_noisy/revisions'})
        exported, _ = load_genre(target)
        if weight_hash(exported) != before: raise ValueError('Export differs from the qualified owner')
    print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
