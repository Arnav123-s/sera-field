"""Independent registered-case, credit, retention and inference-package audit.

Run once after the campaign completes, under the shared numerical supervisor.
No model selection or final-based parameter adjustment occurs here.
"""
from collections import Counter
import json
import os
from pathlib import Path
import random
import shutil
import sys

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sera_field.credit_bridge import identity
from sera_field.extension_study import load_extension
from sera_field.inquiry_study import load_inquiry
from sera_field.model import parameters, weight_hash
from sera_field.records import sha256, write_json
from sera_field.study_data import load_records
from sera_field.study_training import reading_batch, math_batch, pair_batch
from sera_field.study_world import stable_seed


def read(path):
    return json.loads(path.read_text())


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1)
    runs = ROOT / 'runs/INQUIRY-014'
    report = ROOT / 'reports/INQUIRY-014'
    report.mkdir(parents=True, exist_ok=True)
    registration = read(runs / 'FINAL_REGISTRATION.json')
    owner, selection = load_inquiry(runs / 'learned')
    parent, parent_selection = load_extension(ROOT / 'runs/GROW-013/learned')
    owner.eval()
    protected = all(torch.equal(p, dict(owner.named_parameters())[name])
                    for name, p in parent.named_parameters())
    source_checks = {'protocol': sha256(ROOT / 'protocols/INQUIRY-014.md') == registration['protocol'],
                     'parent': sha256(ROOT / 'runs/GROW-013/learned/SELECTION.json') == registration['parent']}
    # Numerical source identities are compared to the launch snapshot, not a
    # changing documentation commit. Other files created during training are irrelevant.
    launch = read(ROOT / 'runs/inquiry014-campaign-001/state.json')
    for name in ('inquiry_study.py', 'inquiry_owner.py', 'fusion_inquiry.py',
                 'credit_bridge.py', 'learned_extension.py', 'extension_world.py',
                 'coupled_owner.py', 'condensate.py'):
        relative = 'sera_field/' + name
        source_checks[relative] = sha256(ROOT / relative) == launch['sources'][relative]
    teaching = {}
    for arm in ('learned', 'disconnected'):
        complete = read(runs / arm / 'COMPLETE.json')
        source_checks['selected_' + arm] = sha256(runs / arm / 'SELECTION.json') == registration['selections'][arm]
        counts = Counter()
        decisions, evidence, assessments, contribution_keys, indices = set(), set(), set(), set(), set()
        logs = sorted((runs / arm).glob('episodes-*.jsonl'))
        rewards, before_losses, after_losses = [], [], []
        checks = {'complete_outcomes': True, 'finite_cases': True, 'no_repeated_credit': True,
                  'novelty_once': True, 'actuation_credit': True, 'independent_progress': True,
                  'all_goals_returned': True}
        for path in logs:
            with path.open(encoding='utf-8') as handle:
                for line in handle:
                    row = json.loads(line)
                    if row['index'] in indices:
                        raise ValueError('Preserve and reconcile interrupted uncommitted attempts before counting')
                    indices.add(row['index'])
                    counts['episodes'] += 1
                    checks['all_goals_returned'] &= row['original_goal_returned']
                    checks['finite_cases'] &= all(np.isfinite(row['returned_answer']))
                    before_losses.append(row['initial_mse']); after_losses.append(row['final_mse'])
                    for event in row['events']:
                        counts['probes'] += 1
                        counts['branches'] += len(event['branches'])
                        counts['charge_projections'] += event['cost']['charge_projections']
                        counts['goal_outcomes'] += event['cost']['goal_outcomes']
                        checks['complete_outcomes'] &= (len(event['branches']) == 24 and
                            abs(sum(b['probability'] for b in event['branches']) - 1) < 1e-9)
                        credit = event['event']; outcome = credit['outcome']
                        checks['independent_progress'] &= (outcome['before_loss'] == event['before_mse'] and
                            outcome['after_loss'] == event['after_mse'] and
                            outcome['goal'] == row['goal'] and
                            outcome['source_sha256'] == sha256(ROOT / 'sera_field/extension_world.py') and
                            outcome['verifier_sha256'] == sha256(ROOT / 'sera_field/inquiry_study.py'))
                        if not event['receipt']['actuation_matched']:
                            counts['actuation_mismatches'] += 1
                            checks['actuation_credit'] &= (not credit['accepted'] and
                                credit['reason'] == 'intervention was not performed as assumed')
                        if not credit['accepted']:
                            counts['rejected'] += 1
                            continue
                        counts['accepted'] += 1
                        counts['parameter_updates'] += credit['weights_changed']
                        checks['no_repeated_credit'] &= (outcome['decision'] not in decisions and
                            outcome['evidence_id'] not in evidence and outcome['assessment_id'] not in assessments)
                        decisions.add(outcome['decision']); evidence.add(outcome['evidence_id'])
                        assessments.add(outcome['assessment_id'])
                        progress = (event['before_mse'] - event['after_mse']) / (1 + event['before_mse'])
                        key = identity([outcome['assumptions_id'], outcome['canonical_contribution']])
                        expected_bonus = .1 * max(0., progress) if key not in contribution_keys else 0.
                        checks['novelty_once'] &= abs(credit['bonus'] - expected_bonus) < 1e-12
                        checks['independent_progress'] &= abs(credit['reward'] - max(-1., min(1., progress + expected_bonus))) < 1e-12
                        if progress > 0:
                            contribution_keys.add(key)
                            counts['improved_probes'] += 1
                        counts['positive_bonuses'] += credit['bonus'] > 0
                        counts['captures'] += event['capture'] is not None
                        rewards.append(credit['reward'])
        checks['complete_cursor'] = indices == set(range(1024)) and counts['probes'] == 3072
        teaching[arm] = {'counts': dict(counts), 'checks': {k: bool(v) for k, v in checks.items()},
            'total_reward': sum(rewards), 'mean_initial_mse': float(np.mean(before_losses)),
            'mean_final_mse': float(np.mean(after_losses)), 'canonical_positive_contributions': len(contribution_keys),
            'logs': [{'name': p.name, 'sha256': sha256(p), 'bytes': p.stat().st_size} for p in logs],
            'completion': complete}
    arms = ('learned', 'disconnected', 'initialized', 'uniform', 'information', 'retained_parent_memory')
    finals = {arm: read(runs / 'final' / arm / 'RESULTS.json') for arm in arms}
    final_checks = {}
    for arm, summary in finals.items():
        path = runs / 'final' / arm / 'cases.jsonl'
        final_checks[arm + '_identity'] = sha256(path) == summary['cases_sha256']
        final_checks[arm + '_immutable'] = summary['weights_before'] == summary['weights_after']
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        final_checks[arm + '_cohort'] = {(r['omitted'], r['index']) for r in rows} == (
            {(False, i) for i in range(128)} | {(True, i) for i in range(64)})
        final_checks[arm + '_no_final_updates'] = all(e['event'] is None and e['capture'] is None for r in rows for e in r['events'])
        final_checks[arm + '_finite_returned'] = all(r['original_goal_returned'] and
            np.isfinite(r['returned_answer']).all() and np.isfinite(r['final_mse']) for r in rows)
        dest = report / 'final' / arm; dest.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(runs / 'final' / arm / 'RESULTS.json', dest / 'RESULTS.json')
    replay = read(runs / 'replay/learned/RESULTS.json')
    final_checks['exact_replay'] = (replay['cases_sha256'] == finals['learned']['cases_sha256'] ==
        sha256(runs / 'replay/learned/cases.jsonl'))
    # These opened rows are used strictly as the prospectively declared retention
    # cohort. They do not become new generalization evidence or training data.
    old_registration = read(ROOT / 'runs/UNIFIED-012/FINAL_REGISTRATION.json')
    data = ROOT / 'local/CONNECTED-003-data-v1'
    retained = {}
    with torch.no_grad():
        for kind, fn in (('reading', reading_batch), ('math', math_batch)):
            bank = {r['id']: r for r in load_records(data, 'sealed', kind)}
            values = [fn(owner, [bank[i]]) for i in old_registration['cohorts'][kind]]
            retained[kind] = {'n': len(values), 'accuracy': sum(v[1] for v in values) / len(values)}
        retained['pairs'] = {}; bank = {r['id']: r for r in load_records(data, 'sealed', 'pairs')}
        for track, ids in old_registration['cohorts']['pairs'].items():
            rows = [bank[i] for i in ids]
            if len(rows) < 4:
                continue
            rng = random.Random(stable_seed('UNIFIED-012-final-v1', track))
            values = [pair_batch(owner, [r], rows, rng) for r in rows]
            retained['pairs'][track] = {'n': len(rows), 'accuracy': sum(v[1] for v in values) / len(rows)}
    reference = read(ROOT / 'reports/GROW-013/RETENTION.json')['metrics']
    retention_checks = {kind: retained[kind]['accuracy'] >= reference[kind]['accuracy'] - .03
                        for kind in ('reading', 'math')}
    retention_checks['pairs'] = np.mean([v['accuracy'] for v in retained['pairs'].values()]) >= np.mean(
        [v['accuracy'] for v in reference['pairs'].values()]) - .03
    gates = {'protected_parent_parameters': protected,
             'source_identities': all(source_checks.values()),
             'teaching_integrity': all(all(v['checks'].values()) for v in teaching.values()),
             'final_integrity': all(final_checks.values()),
             'retention': all(retention_checks.values())}
    qualification = {'gates': {k: bool(v) for k, v in gates.items()}, 'all_gates': bool(all(gates.values())),
        'selected': selection, 'source_checks': source_checks, 'final_checks': final_checks,
        'policy_learning_effect': {regime: {'selected_final_mse': finals['learned'][regime]['final_mse'],
            'initialized_final_mse': finals['initialized'][regime]['final_mse'],
            'information_final_mse': finals['information'][regime]['final_mse'],
            'relative_improvement_vs_initialized': 1 - finals['learned'][regime]['final_mse'] / finals['initialized'][regime]['final_mse']}
            for regime in ('supported', 'omitted')}, 'whole_architecture_completed': False}
    write_json(report / 'TEACHING.json', teaching)
    write_json(report / 'RETENTION.json', {'metrics': retained, 'reference': reference,
        'checks': {k: bool(v) for k, v in retention_checks.items()},
        'scope': 'Opened UNIFIED-012 cohort, prospectively used only for retention'})
    write_json(report / 'QUALIFICATION.json', qualification)
    shutil.copyfile(runs / 'FINAL_REGISTRATION.json', report / 'FINAL_REGISTRATION.json')
    shutil.copyfile(runs / 'replay/learned/RESULTS.json', report / 'REPLAY.json')
    if not all(gates.values()):
        raise ValueError('Preserved inquiry candidate requires a qualified repair; inspect audit')
    target = ROOT / 'checkpoints/INQUIRY-014'; (target / 'revisions').mkdir(parents=True, exist_ok=True)
    if not (target / 'SELECTION.json').exists():
        temporary = target / 'revisions/export.tmp'
        torch.save({'bridge': {'owner': owner.state_dict(), 'specification': owner.specification()},
                    'source_checkpoint_sha256': selection['sha256']}, temporary)
        digest = sha256(temporary); temporary.rename(target / 'revisions' / (digest + '.pt'))
        exported = {**selection, 'sha256': digest, 'revision': digest + '.pt',
                    'source_checkpoint_sha256': selection['sha256'], 'role': 'assessed_local_investigation_candidate'}
        write_json(target / 'SELECTION.json', exported)
        write_json(target / 'MANIFEST.json', {'selection': exported, 'parameters': parameters(owner),
            'specification': owner.specification(), 'report': 'reports/INQUIRY-014/REPORT.md',
            'full_training_state': 'runs/INQUIRY-014/learned/revisions'})
    exported, _ = load_inquiry(target)
    assert weight_hash(exported) == selection['weights']
    print(json.dumps(qualification, indent=2))


if __name__ == '__main__':
    main()
