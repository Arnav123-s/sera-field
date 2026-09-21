"""A persistent learned investigation, checked update and fresh-process return."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import torch
from sera_field.joint_data import JointData
from sera_field.joint_session import JointSession
from sera_field.joint_training import STUDY
from sera_field.native_training import load_native, read
from sera_field.native_data import independent_outcome
from sera_field.records import write_json

REPORT = ROOT / 'reports/JOINT-020'
SESSIONS = ROOT / 'local/JOINT-020-delivery'


def public_view(value):
    # Raw human wording remains with the private source/session. Public evidence
    # retains its exact identity, controls, predictions and qualification.
    from sera_field.native_data import identity
    if isinstance(value, list):
        return [public_view(v) for v in value]
    if isinstance(value, dict):
        return {(k+'_sha256' if k == 'hypothesis' else k): identity(v) if k == 'hypothesis' else public_view(v)
                for k, v in value.items()}
    return value


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--replay', action='store_true'); args = parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use the numerical supervisor')
    torch.set_num_threads(1)
    if args.replay:
        delivery = read(SESSIONS / 'DELIVERY_PENDING.json'); same = []; duplicate = []
        for record in delivery['cases']:
            restored = JointSession.load(SESSIONS / record['task'])
            same.append(restored.answer() == record['returned_answer'])
            same.append(restored.answer(force=record['next_query'][0], velocity=record['next_query'][1]) == record['next_answer'])
            credit = record['credit']
            try:
                restored.grade(credit['decision'], independent_response=credit['independent_response'],
                    source=credit['independent_source'], verifier=credit['verifier'], evidence_id=credit['independent_evidence_id'])
            except ValueError as error:
                duplicate.append('Repeated credit' in str(error))
            else:
                duplicate.append(False)
        checks = {'fresh_process_exact_restore': all(same), 'repeated_credit_rejected': all(duplicate),
                  'actual_reward_weight_update': any(c['credit']['updated'] and c['credit']['before_weights'] != c['credit']['after_weights']
                                                       for c in delivery['cases']),
                  'all_histories_reencoded': all(c['credit']['history_reencoded_under_updated_owner'] for c in delivery['cases']),
                  'original_goals_returned': all(c['returned_answer']['original_goal'] == c['original_goal'] for c in delivery['cases']),
                  'same_continuing_weight_lineage': all(a['credit']['after_weights'] == b['credit']['before_weights']
                                                        for a, b in zip(delivery['cases'], delivery['cases'][1:]))}
        write_json(REPORT / 'DELIVERY.json', {**public_view(delivery), 'checks': checks, 'all_checks': all(checks.values())})
        print(json.dumps({'delivery_checks': checks}), flush=True)
        return
    if (SESSIONS / 'DELIVERY_PENDING.json').exists():
        raise ValueError('Preserve the completed live delivery; replay or inspect rather than re-teaching it')
    data = JointData(); owner, selected, _ = load_native(STUDY / 'credited'); cases = []; shared_optimizer = None
    for index, row in enumerate(data.development[:16]):
        physics = row['physics']; f, v = physics['queries'][0]
        goal = {'hypothesis': row['human']['hypothesis'], 'force': f, 'velocity': v}
        task = JointSession(owner, goal, source=row['id'])
        if shared_optimizer is not None:
            task.optimizer = shared_optimizer
        text = {'kind': 'text', 'id': row['human']['id'], 'source': 'registered-human-premise', 'text': row['human']['premise']}
        measurements = [{'kind': 'measurement', 'id': row['id']+'-support-'+str(j), 'source': 'declared-development-simulator',
                          'performed': True, 'force': p[0], 'velocity': p[1], 'response': p[2]}
                         for j, p in enumerate(physics['support'][:2])]
        for observation in ([text, *measurements] if row['text_first'] else [*measurements, text]):
            task.remember(observation)
        before = task.answer(); proposed = task.propose(); receipt = None
        if proposed['requested'] is not None:
            actual_f, actual_v = proposed['requested']
            receipt = {'kind': 'measurement', 'id': row['id']+'-new-probe', 'source': 'declared-performed-simulator',
                       'performed': True, 'force': actual_f, 'velocity': actual_v,
                       'response': independent_outcome(physics['teacher_only'], actual_f, actual_v)}
        transition = task.observe(proposed['id'], receipt)
        next_f, next_v = physics['queries'][1]
        next_before = task.answer(force=next_f, velocity=next_v)
        truth = independent_outcome(physics['teacher_only'], f, v)
        credit = task.grade(proposed['id'], independent_response=truth, source='separate-original-goal-outcome',
                            verifier='independent-scalar-assessor', evidence_id=row['id']+'-goal-assessment')
        returned = task.answer(); next_answer = task.answer(force=next_f, velocity=next_v)
        name = 'task-'+str(index).zfill(2); task.save(SESSIONS / name)
        cases.append({'task': name, 'source_id': row['human']['id'], 'original_goal': goal,
                       'before': before, 'transition': transition, 'credit': credit,
                       'returned_answer': returned, 'next_query': [next_f, next_v],
                       'next_before_reward_update': next_before, 'next_answer': next_answer,
                       'next_independent_truth': independent_outcome(physics['teacher_only'], next_f, next_v)})
        shared_optimizer = task.optimizer
    write_json(SESSIONS / 'DELIVERY_PENDING.json', {'initial_selection': selected, 'cases': cases,
        'scope': 'Sixteen supplied development investigations, same continuing owner and optimizer; final cohort unchanged.',
        'graded_goal_and_next_query_separated': True})
    print(json.dumps({'saved_delivery_tasks': len(cases), 'actual_updates': sum(c['credit']['updated'] for c in cases)}), flush=True)


if __name__ == '__main__':
    main()
