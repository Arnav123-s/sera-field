"""Separate-process executable-portfolio replay, before curriculum teaching.

Output biases explicitly construct a mixed fixture with two correct methods and
two incorrect ones. This tests engineering; it is not discovery by taught SERA.
"""
import argparse
import json
from pathlib import Path
import random
import sys

import torch

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.core_owner import CoreOwner
from sera_field.core_programs import OPERATIONS
from sera_field.core_program_verifier import ProgramContract
from sera_field.core_session import CoreSession
from sera_field.native_data import identity
from sera_field.native_owner import NativeConfig
from sera_field.records import write_json

OUT = ROOT/'runs/CORE-022/program-probe'


def serial(value):
    if isinstance(value, torch.Tensor): return {'dtype': str(value.dtype), 'values': value.tolist()}
    if isinstance(value, dict): return {str(k): serial(v) for k,v in value.items()}
    if isinstance(value, (tuple, list)): return [serial(v) for v in value]
    return value


def continuation(task):
    contract = ProgramContract(goal_id=identity(task.goal), source_sha256=identity('independent algebra fixture'),
        assessment_id='four-way-polynomial-check', arity=2, assumptions=task.goal['assumptions'],
        polynomial_terms=[[[0, 2], '1'], [[1, 1], '2'], [[2, 0], '1']])
    report = task.grade_programs(task.pending['id'], contract)
    return {'assessment': report, 'answer': task.answer(), 'weights': task.weights,
        'optimizer': identity(serial(task.optimizer.state_dict())), 'state': task.state_id(),
        'torch_next': torch.rand(4).tolist(), 'python_next': random.random()}


def prepare():
    if OUT.exists(): raise ValueError('Preserve the completed attempt; replay the pending checkpoint')
    OUT.mkdir(parents=True)
    torch.manual_seed(22025); random.seed(22025)
    owner = CoreOwner(NativeConfig(nodes=3, rounds=1))
    # Programs choose either (x+y)^2 or x(x+y)+y(x+y), or one of two
    # mismatched combinations. Every proposal is recorded before assessment.
    with torch.no_grad():
        for layer in (owner.program_map.operations, owner.program_map.left,
                      owner.program_map.right, owner.program_map.output):
            layer.weight.zero_(); layer.bias.fill_(-25.)
        nodes = [('add', 0, 1), ('mul', 9, 0), ('mul', 9, 1), ('add', 10, 11)]
        for i, (op, a, b) in enumerate(nodes):
            owner.program_map.operations.bias.reshape(4, -1)[i, OPERATIONS.index(op)] = 25.
            owner.program_map.left.bias.reshape(4, -1)[i, a] = 25.
            owner.program_map.right.bias.reshape(4, -1)[i, b] = 25.
        owner.program_map.operations.bias.reshape(4, -1)[1, OPERATIONS.index('square')] = 25.
        owner.program_map.output.bias[10] = 25.; owner.program_map.output.bias[12] = 25.
    task = CoreSession(owner, {'kind': 'program', 'hypothesis': 'Return the square of the input sum.',
        'arity': 2, 'assumptions': ['rational inputs']}, source='fresh-process-program-fixture')
    task.remember({'kind': 'text', 'id': 'source-1', 'source': 'engineering-fixture',
                   'text': 'Two measured quantities are supplied to the calculation.'})
    task.remember({'kind': 'measurement', 'id': 'source-2', 'source': 'independent-fixture',
        'performed': True, 'force': .2, 'velocity': .1, 'response': .125})
    decision = task.propose_programs(64); task.save(OUT/'session')
    result = continuation(task)
    assessments = result['assessment']['assessments']
    assert len(task.portfolio) == 2
    assert any(r['reward'] < 0 for r in assessments)
    assert sum(r['reward'] > 0 for r in assessments) == 2
    assert result['assessment']['updated']
    write_json(OUT/'EXPECTED.json', result)
    write_json(OUT/'PORTFOLIO.json', {'scope': 'engineered decision fixture, not trained discovery',
        'proposal_count': len(decision['proposals']), 'distinct_verified_methods': len(task.portfolio),
        'qualified_proposals': sum(r['review']['qualified'] for r in assessments),
        'failed_proposals': sum(not r['review']['qualified'] for r in assessments),
        'positive_credit_count': sum(r['reward'] > 0 for r in assessments),
        'negative_credit_count': sum(r['reward'] < 0 for r in assessments),
        'method_expressions': [p['expression'] for p in task.portfolio],
        'actual_weight_update': result['assessment']['updated'],
        'same_owner_optimizer': True, 'protected_pending_state_saved': True,
        'curriculum_presentations': 0, 'expected_identity': identity(result)})
    write_json(OUT/'PENDING.json', {'completed': False, 'next': 'scripts/probe_core022_programs.py verify'})
    print(json.dumps({'prepared': True, 'next': 'verify'}))


def verify():
    task = CoreSession.load(OUT/'session')
    expected = json.loads((OUT/'EXPECTED.json').read_text())
    actual = continuation(task)
    assert actual == expected, 'Program continuation differs in a new process'
    report = {'exact_fresh_process_replay': True, 'weights_after': actual['weights'],
        'expected_identity': identity(expected), 'actual_identity': identity(actual),
        'optimizer_identity': actual['optimizer'], 'same_goals_methods_failures_credit_and_rng': True}
    write_json(OUT/'REPLAY.json', report)
    write_json(OUT/'PENDING.json', {'completed': True, 'result': 'REPLAY.json'})
    print(json.dumps(report))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('mode', choices=['prepare', 'verify'])
    arguments = parser.parse_args()
    (prepare if arguments.mode == 'prepare' else verify)()
