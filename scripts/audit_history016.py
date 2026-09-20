"""Independently assess the frozen history procedure and preserve every outcome."""
import argparse
import json
import math
import os
from pathlib import Path
import random
import shutil
import sys

import torch

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.history_training import load_history, ARMS, DATA
from sera_field.model import parameters, weight_hash
from sera_field.records import sha256, write_json
from sera_field.semantic_training import load_semantic
from scripts.audit_semantic015 import retention


def read(path):
    return json.loads(Path(path).read_text())


def metrics(cases):
    result = {'n': len(cases)}
    for prefix in ('before', 'after'):
        losses = []; correct = []; bins = [[] for _ in range(10)]
        confusion = [[0] * 3 for _ in range(3)]
        for case in cases:
            p = case[prefix + '_probability']; target = case['target']
            if not (all(math.isfinite(v) and 0 <= v <= 1 for v in p) and abs(sum(p) - 1) < 1e-5):
                raise ValueError('Invalid history final probability')
            choice = max(range(3), key=p.__getitem__); hit = choice == target
            losses.append(-math.log(max(p[target], 1e-12))); correct.append(hit)
            bins[min(9, int(max(p) * 10))].append((max(p), hit)); confusion[target][choice] += 1
        result[prefix] = {'loss': sum(losses) / len(cases), 'accuracy': sum(correct) / len(cases),
            'confusion': confusion, 'calibration_error_10_bins': sum(
                abs(sum(p for p, _ in b) - sum(c for _, c in b)) / len(cases) for b in bins)}
    return result


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--test-attempt', required=True)
    parser.add_argument('--campaign-attempt', required=True); args = parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1)
    study = ROOT / 'runs/HISTORY-016'; report = ROOT / 'reports/HISTORY-016'; report.mkdir(parents=True, exist_ok=True)
    if (report / 'QUALIFICATION.json').exists():
        print('Preserved completed history audit; inspect its decision.'); return
    owner, selected = load_history(study / 'learned')
    parent, parent_selection = load_semantic(ROOT / 'checkpoints/SEMANTIC-015')
    before = weight_hash(owner)
    protected = {name: bool(torch.equal(p, dict(owner.named_parameters())[name])) for name, p in parent.named_parameters()}
    retained_candidate, retained_parent = retention(owner), retention(parent)
    empty_scope_retained = retained_candidate == retained_parent
    write_json(report / 'RETENTION.json', {'candidate': retained_candidate, 'parent': retained_parent,
        'exact_metrics': empty_scope_retained,
        'scope': 'opened regression only, with no task-specific new history active'})
    registration = read(study / 'FINAL_REGISTRATION.json'); preparation = read(DATA / 'MANIFEST.json')
    launch = read(ROOT / 'runs' / args.campaign_attempt / 'state.json')
    tests = read(ROOT / 'runs' / args.test_attempt / 'state.json')
    sources = {name: sha256(ROOT / name) == value for name, value in launch['sources'].items()
               if name.startswith('sera_field/')}
    sources.update(protocol=sha256(ROOT / 'protocols/HISTORY-016.md') == registration['protocol'],
                   preparation=sha256(DATA / 'MANIFEST.json') == registration['source'],
                   selection=sha256(study / 'learned/SELECTION.json') == registration['selected'])
    sources['preparation_producer'] = sha256(ROOT / 'scripts/prepare_history016.py') == preparation['script_sha256']
    sources['human_parent_manifest'] = sha256(ROOT / 'local/SEMANTIC-015-data-v1/MANIFEST.json') == preparation['source_manifest_sha256']
    tested = tests['status'] == 'PASS' and all(tests['sources'].get(name) == sha256(ROOT / name) for name in (
        'sera_field/continuum_core.py', 'sera_field/history_owner.py',
        'sera_field/perfect_tensor_memory.py', 'sera_field/history_training.py'))
    split_checks = {}; groups = {}
    for split, partition in preparation['partitions'].items():
        queries, support = set(partition['query_groups']), set(partition['support_groups'])
        split_checks[split + '_support_query'] = not (queries & support)
        split_checks[split + '_view_hash'] = sha256(DATA / (split + '.jsonl')) == partition['sha256']
        groups[split] = queries | support
    for a, b in (('train', 'development'), ('train', 'sealed'), ('development', 'sealed')):
        split_checks[a + ':' + b] = not (groups[a] & groups[b])
    split_checks['prior_final_excluded'] = not groups['sealed'] & set(preparation['previous_final_source_groups'])
    complete = read(study / 'learned/COMPLETE.json')
    expected_training = {r['id']: r for r in (json.loads(line) for line in (DATA / 'train.jsonl').read_text(encoding='utf-8').splitlines())}
    expected_final = {r['query']['id']: r for r in (json.loads(line) for line in (DATA / 'sealed.jsonl').read_text(encoding='utf-8').splitlines())}
    logfiles = sorted((study / 'learned').glob('episodes-*.jsonl'))
    steps = set(); ids = set(); rewards = []; mass_errors = []
    for path in logfiles:
        for line in path.read_text().splitlines():
            row = json.loads(line)
            if row['step'] in steps or row['id'] in ids:
                raise ValueError('Reconcile repeated/uncommitted history teaching before counting it')
            steps.add(row['step']); ids.add(row['id'])
            expected = expected_training[row['id']]
            if row['query_id'] != expected['query']['id'] or row['target'] != expected['query']['target'] or [s['id'] for s in row['supports']] != [s['id'] for s in expected['supports']]:
                raise ValueError('Training outcome does not match the registered human episode')
            if not row['original_goal_returned'] or len(row['supports']) != 4:
                raise ValueError('Incomplete history teaching episode')
            if any(s['source_group'] == row['query_group'] for s in row['supports']):
                raise ValueError('A teaching query shares support source')
            if abs(row['verified_progress_reward'] - row['before_loss'] + row['after_loss']) > 1e-10:
                raise ValueError('History reward arithmetic changed')
            rewards.append(row['verified_progress_reward'])
            mass_errors.extend(s['relaxation_mass_error'] for s in row['supports'])
    teaching_checks = {'complete': steps == set(range(1, 2049)), 'finite': all(math.isfinite(x) for x in rewards + mass_errors),
                       'conserved_relaxation': max(mass_errors) < 1e-4}
    finals = {}; rows = {}; final_checks = {}
    for arm in ARMS:
        src = study / 'final' / arm
        summary = read(src / 'RESULTS.json')
        cases = [json.loads(line) for line in (src / 'cases.jsonl').read_text().splitlines()]
        rows[arm] = cases; independent = metrics(cases); finals[arm] = independent
        final_checks[arm + '_human_annotations'] = all(r['target'] == expected_final[r['query_id']]['query']['target'] and
            [s['id'] for s in r['supports']] == [s['id'] for s in expected_final[r['query_id']]['supports']] for r in cases)
        final_checks[arm + '_cohort'] = [r['query_id'] for r in cases] == registration['query_ids']
        final_checks[arm + '_identity'] = sha256(src / 'cases.jsonl') == summary['cases_sha256']
        final_checks[arm + '_immutable'] = (summary['weights_before'] == summary['weights_after'] and
            summary['factual_captures'] == summary['final_parameter_updates'] == 0)
        final_checks[arm + '_arithmetic'] = (abs(independent['after']['loss'] - summary['loss']) < 1e-5 and
            independent['after']['accuracy'] == summary['accuracy'])
        dest = report / 'final' / arm; dest.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src / 'RESULTS.json', dest / 'RESULTS.json')
        write_json(dest / 'INDEPENDENT_METRICS.json', independent)
    final_checks['replay'] = (sha256(study / 'replay/learned/cases.jsonl') ==
        sha256(study / 'final/learned/cases.jsonl') == read(study / 'replay/learned/RESULTS.json')['cases_sha256'])
    difference = [r['after_loss'] - b['after_loss'] for r, b in zip(rows['learned'], rows['no_history'])]
    rng = random.Random(1611601)
    bootstrap = sorted(sum(rng.choices(difference, k=len(difference))) / len(difference) for _ in range(4096))
    comparison = {'paired_query_loss_difference': sum(difference) / len(difference),
        'percentile_95_interval': [bootstrap[102], bootstrap[3993]],
        'scope': 'resampled distinct query source groups with a fixed support pool; finite-cohort evidence'}
    delivery = read(report / 'DELIVERY.json')
    delivery_passed = delivery['all_checks'] and delivery['retained_count'] > 0
    useful = (selected['step'] > 0 and finals['learned']['after']['loss'] <= .99 * finals['no_history']['after']['loss'] and
              finals['learned']['after']['accuracy'] >= finals['no_history']['after']['accuracy'] - .02)
    gates = {'mathematical_tests': tested, 'sources': all(sources.values()), 'splits': all(split_checks.values()),
        'teaching': all(teaching_checks.values()), 'finals': all(final_checks.values()),
        'protected_parent_parameters': all(protected.values()), 'empty_scope_retention': empty_scope_retained,
        'read_only_audit': weight_hash(owner) == before,
        'persistent_qualified_delivery': bool(delivery_passed),
        'useful_learned_update': bool(useful)}
    result = {'gates': {k: bool(v) for k, v in gates.items()}, 'all_gates': bool(all(gates.values())),
        'selected': selected, 'parent': parent_selection, 'source_checks': sources,
        'split_checks': split_checks, 'teaching_checks': teaching_checks, 'final_checks': final_checks,
        'comparison': comparison, 'delivery_retained_count': delivery['retained_count'], 'whole_architecture_completed': False}
    write_json(report / 'QUALIFICATION.json', result)
    write_json(report / 'TEACHING.json', {'complete': complete, 'verified_progress_reward_sum': sum(rewards),
        'max_relaxation_mass_error': max(mass_errors), 'protected_parameters': protected,
        'selected_new_parameters': {name: p.detach().tolist() for name, p in owner.named_parameters()
            if name.startswith(('field.continuum.', 'field.raw_history_gain'))},
        'logs': [{'name': p.name, 'sha256': sha256(p), 'bytes': p.stat().st_size} for p in logfiles]})
    shutil.copyfile(study / 'FINAL_REGISTRATION.json', report / 'FINAL_REGISTRATION.json')
    shutil.copyfile(study / 'replay/learned/RESULTS.json', report / 'REPLAY.json')
    # A numerically sound but unhelpful mechanism remains available as an
    # assessed research candidate; it is not silently installed as the successor.
    if all(gates.values()):
        target = ROOT / 'checkpoints/HISTORY-016'; (target / 'revisions').mkdir(parents=True, exist_ok=True)
        if not (target / 'SELECTION.json').exists():
            temporary = target / 'revisions/export.tmp'
            torch.save({'bridge': {'owner': owner.state_dict(), 'specification': owner.specification()},
                'source_checkpoint_sha256': selected['sha256']}, temporary)
            digest = sha256(temporary); temporary.rename(target / 'revisions' / (digest + '.pt'))
            exported = {**selected, 'sha256': digest, 'revision': digest + '.pt',
                'source_checkpoint_sha256': selected['sha256'], 'role': 'qualified_history_update_owner'}
            write_json(target / 'SELECTION.json', exported)
            write_json(target / 'MANIFEST.json', {'selection': exported, 'parameters': parameters(owner),
                'specification': owner.specification(), 'report': 'reports/HISTORY-016/REPORT.md'})
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
