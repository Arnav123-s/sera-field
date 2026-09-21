"""Exercise retained state, an actual new measurement, credit and returned answer."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import torch
from sera_field.native_data import physical_episode, independent_outcome, identity
from sera_field.native_session import NativeSession
from sera_field.native_training import STUDY, load_native
from sera_field.records import sha256, write_json


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'): raise SystemExit('Use the numerical supervisor')
    torch.set_num_threads(1)
    owner, selected, _ = load_native(STUDY / 'native')
    root = ROOT / 'local/NATIVE-019-delivery' / os.environ['SERA_FIELD_SUPERVISED']
    if root.exists(): raise ValueError('Preserve the existing delivery attempt')
    checks = {}; cases = []
    for number in range(16):
        row = physical_episode('NATIVE-019-development', number)
        f, v = row['queries'][0]
        session = NativeSession(owner, {'force': f, 'velocity': v}, source=identity(row['support']))
        for i, (force, velocity, response) in enumerate(row['support']):
            session.remember({'id': row['id'] + ':' + str(i), 'source': row['namespace'], 'performed': True,
                              'force': force, 'velocity': velocity, 'response': response})
        path = root / str(number); before = session.answer(); session.save(path)
        query_state = session.state_id()
        conditional = session.answer([[f-.3, v], [f+.3, v]])
        checks[f'{number}:branch_isolation'] = session.state_id() == query_state
        restored = NativeSession.load(owner, path)
        checks[f'{number}:exact_restart'] = restored.answer() == before
        proposal = restored.propose(); restored.save(path)
        requested = proposal['requested']
        # The assessor performs the requested control in the independent scalar
        # world. It does not substitute SERA's own expected response.
        actual = independent_outcome(row['teacher_only'], requested['force'], requested['velocity'])
        evidence = {'id': row['id'] + ':new-probe', 'source': identity(row['teacher_only']), 'performed': True,
                    **requested, 'response': actual}
        transition = restored.observe(proposal['id'], evidence)
        truth = independent_outcome(row['teacher_only'], f, v)
        credit = restored.grade(proposal['id'], independent_response=truth,
                                source=row['id'] + ':withheld-original-goal', verifier=sha256(__file__))
        checks[f'{number}:actual_intervention'] = transition['performed_as_requested']
        checks[f'{number}:original_goal'] = restored.answer()['original_goal'] == before['original_goal']
        try:
            restored.grade(proposal['id'], independent_response=truth, source='duplicate', verifier=sha256(__file__))
            checks[f'{number}:duplicate_rejected'] = False
        except ValueError: checks[f'{number}:duplicate_rejected'] = True
        returned = restored.answer(); revision = restored.save(path)
        if number == 0:
            command = [sys.executable, '-X', 'utf8', '-m', 'sera_field.native_cli', 'answer',
                       '--owner', str(STUDY / 'native'), '--session', str(path)]
            output = subprocess.check_output(command, cwd=ROOT, text=True, encoding='utf-8')
            replay = json.loads(output); replay.pop('saved_revision')
            checks['fresh_process_cli'] = replay == returned
        cases.append({'id': row['id'], 'before': before, 'conditional': conditional, 'proposal': proposal,
                      'actual_evidence': evidence, 'credit': credit, 'returned_answer': returned, 'revision': revision})
    result = {'checkpoint': selected, 'checks': checks, 'cases': cases,
        'before_goal_mse': sum((c['credit']['before']-c['credit']['independent_response'])**2 for c in cases)/len(cases),
        'after_goal_mse': sum((c['credit']['after']-c['credit']['independent_response'])**2 for c in cases)/len(cases),
        'positive_credit_cases': sum(c['credit']['signed_progress'] > 0 for c in cases),
        'negative_credit_cases': sum(c['credit']['signed_progress'] < 0 for c in cases),
        'new_policy_weight_updates': 0, 'policy': 'fixed disagreement selector; graded state correction',
        'scope': 'Sixteen already-open development tasks; delivery audit, not new sealed generalization.'}
    write_json(ROOT / 'reports/NATIVE-019/DELIVERY.json', result)
    if not all(checks.values()): raise ValueError('Native persistent delivery check failed')
    print(json.dumps({'delivery_checks': len(checks), 'passed': all(checks.values()),
                      'before_mse': result['before_goal_mse'], 'after_mse': result['after_goal_mse']}))


if __name__ == '__main__': main()
