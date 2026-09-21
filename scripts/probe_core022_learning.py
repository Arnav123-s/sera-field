"""From a saved mid-practice fixture to checked learning credit and returned task."""
import argparse
import copy
import json
from pathlib import Path
import random
import sys

import torch

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.core_learning import LearningContract
from sera_field.core_owner import CoreOwner
from sera_field.core_programs import OPERATIONS
from sera_field.core_program_verifier import ProgramContract
from sera_field.core_session import CoreSession
from sera_field.native_data import identity
from sera_field.native_owner import NativeConfig
from sera_field.records import write_json

OUT = ROOT/'runs/CORE-022/learning-probe'
SUM = [[[0, 1], '1'], [[1, 0], '1']]
GOAL = {'kind': 'program', 'hypothesis': 'Add the two values.', 'arity': 2, 'assumptions': ['rational inputs']}


def frozen_contract():
    program = {'arity': 2, 'nodes': [['add', 0, 1]]*4, 'output': 9}
    lessons = {name: {'context': context, 'question': question, 'program': program,
        'source_sha256': identity(['supplied-engineering-source', name]), 'group': 'practice-'+name}
        for name, context, question in (
            ('first', 'Two rational quantities are supplied.', 'Compute their sum.'),
            ('second', 'There is one quantity followed by another.', 'Combine them by addition.'))}
    plans = [{'name': 'focused', 'description': 'Practice the new source twice.', 'lessons': ['first', 'first']},
             {'name': 'varied', 'description': 'Practice both attributed sources.', 'lessons': ['first', 'second']}]
    reviews = []
    for role, context, question in (
        ('acquisition', 'These quantities are presented in a fresh context.', 'What is the total?'),
        ('retention', 'Keep the earlier balanced-input behavior.', 'Evaluate the two opposite values.')):
        source = identity(['independent engineering assessor', role])
        goal = {**GOAL, 'hypothesis': question}
        target = {'polynomial_terms': SUM} if role == 'acquisition' else {'cases': [
            {'inputs': [1, -1], 'output': 0}, {'inputs': ['3/2', '-3/2'], 'output': 0}]}
        contract = ProgramContract(goal_id=identity(goal), source_sha256=source,
            assessment_id='learning-fixture-'+role, arity=2, assumptions=GOAL['assumptions'], **target)
        reviews.append({'context': context, 'question': question, 'source_sha256': source,
                        'group': 'independent-'+role, 'role': role, 'contract': contract})
    return LearningContract(lessons, plans, reviews)


def prepared():
    torch.manual_seed(22026); random.seed(22026)
    owner = CoreOwner(NativeConfig(nodes=3, rounds=1))
    # A near-boundary readout fixture lets two real gradient updates move a
    # deterministic answer. The core, memory and policy remain fresh weights.
    with torch.no_grad():
        for layer in (owner.program_map.operations, owner.program_map.left,
                      owner.program_map.right, owner.program_map.output):
            layer.weight.zero_(); layer.bias.fill_(-25.)
        for i in range(4):
            owner.program_map.operations.bias.reshape(4, -1)[i, OPERATIONS.index('add')] = 25.
            owner.program_map.left.bias.reshape(4, -1)[i, 0] = 25.
            owner.program_map.right.bias.reshape(4, -1)[i, 1] = 25.
        owner.program_map.output.bias[6] = .00005; owner.program_map.output.bias[9] = 0.
    task = CoreSession(owner, GOAL, source='supplied-learning-engineering-fixture')
    task.remember({'id': 'learning-context', 'kind': 'text', 'source': 'fixture',
                   'text': 'A calculation is pending and its original question is retained.'})
    return task


def compact(record):
    """Scientific replay excludes measured runtime; every runtime remains saved."""
    if isinstance(record, dict):
        return {k:compact(v) for k,v in record.items() if k not in ('wall_seconds', 'id')}
    if isinstance(record, list): return [compact(v) for v in record]
    return record


def continuation(task, contract):
    task.practice_learning(contract)
    result = task.finish_learning(contract)
    proposed = task.propose_programs(16)
    final = ProgramContract(goal_id=identity(task.goal), source_sha256=identity('independent original-goal fixture'),
        assessment_id='returned-original-goal', arity=2, assumptions=GOAL['assumptions'], polynomial_terms=SUM)
    returned = task.grade_programs(proposed['id'], final)
    return {'procedure': compact(result), 'returned': compact(returned), 'weights': task.weights,
            'state': task.state_id(), 'torch_next': torch.rand(4).tolist(), 'python_next': random.random()}


def prepare():
    if OUT.exists(): raise ValueError('Preserve the existing learning probe')
    OUT.mkdir(parents=True)
    task = prepared(); contract = frozen_contract()
    task.propose_learning(contract, OUT/'trial')
    task.practice_learning(contract)
    expected = continuation(task, contract)
    write_json(OUT/'EXPECTED.json', expected)
    write_json(OUT/'PENDING.json', {'completed': False, 'next': 'scripts/probe_core022_learning.py verify',
        'note': 'current checkpoint is after completed practice; mid-trial copy retained separately'})
    # The first immutable current revision is located by its scientific cursor,
    # leaving CURRENT and later completed revisions unmodified.
    revisions = []
    for path in (OUT/'trial/current/revisions').glob('session-*.json'):
        record = json.loads(path.read_text())
        if record['payload']['extensions']['learning_trial']['cursor'] == 1:
            revisions.append((path.name, record['identity']))
    if len(revisions) != 1: raise ValueError('Expected exactly one completed-first-update revision')
    write_json(OUT/'MIDPOINT.json', {'revision': revisions[0][0], 'identity': revisions[0][1]})
    print(json.dumps({'prepared': True, 'next': 'verify'}))


def verify():
    # Make a separate local checkpoint view; never rewind the original pointer.
    import shutil
    resumed = OUT/'independent-resume'
    if resumed.exists(): raise ValueError('Independent replay directory already exists')
    shutil.copytree(OUT/'trial/current', resumed)
    write_json(resumed/'CURRENT.json', json.loads((OUT/'MIDPOINT.json').read_text()))
    task = CoreSession.load(resumed)
    # Writes from replay belong to its own directory, preserving the original
    # worker's snapshots and costs. Parent identity remains the same immutable one.
    task.learning_trial['directory'] = str(OUT/'replayed-trial')
    actual = continuation(task, frozen_contract())
    expected = json.loads((OUT/'EXPECTED.json').read_text())
    assert actual == expected, 'Interrupted learning procedure did not replay exactly'
    procedure = actual['procedure']
    result = {'exact_mid_trial_replay': True, 'expected_identity': identity(expected),
        'actual_identity': identity(actual), 'weights_after': actual['weights'],
        'baseline': procedure['baseline']['scores'], 'after_practice': procedure['after_practice']['scores'],
        'after_credit': procedure['after_procedure_credit']['scores'], 'reward': procedure['reward'],
        'practice_updates': len(procedure['practice_updates']),
        'procedure_credit_updated_weights': procedure['weights_after_practice'] != procedure['weights_after_credit'],
        'original_goal_qualified_methods': len(actual['returned']['returned_answer']['qualified_programs']),
        'scope': 'constructed readout fixture, two genuine optimizer updates; not the behavioral curriculum'}
    write_json(OUT/'REPLAY.json', result); write_json(OUT/'PENDING.json', {'completed': True})
    print(json.dumps(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('mode', choices=['prepare', 'verify'])
    options = parser.parse_args()
    (prepare if options.mode == 'prepare' else verify)()
