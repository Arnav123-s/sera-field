import copy
import random

import pytest
import torch

from sera_field.core_owner import CoreOwner
from sera_field.core_programs import BASE, OPERATIONS, execute, method
from sera_field.core_program_verifier import ProgramContract
from sera_field.core_proposals import sample, log_probability
from sera_field.core_session import CoreSession
from sera_field.model import weight_hash
from sera_field.native_data import identity
from sera_field.native_owner import NativeConfig


GOAL = {'kind': 'program', 'hypothesis': 'Return the square of the sum of the two inputs.',
        'arity': 2, 'assumptions': ['rational inputs']}
TARGET = [[[0, 2], '1'], [[1, 1], '2'], [[2, 0], '1']]


def prepared(*, force=True):
    torch.manual_seed(22023); random.seed(22023)
    owner = CoreOwner(NativeConfig(nodes=3, rounds=1))
    if force:
        # Fixture decision only: exposes the correct and alias credit paths.
        nodes = [('add', 0, 1), ('square', 9, 9), ('add', 6, 6), ('add', 6, 6)]
        with torch.no_grad():
            for layer in (owner.program_map.operations, owner.program_map.left,
                          owner.program_map.right, owner.program_map.output):
                layer.weight.zero_(); layer.bias.fill_(-25.)
            for i, (op, a, b) in enumerate(nodes):
                owner.program_map.operations.bias.reshape(4, -1)[i, OPERATIONS.index(op)] = 25.
                owner.program_map.left.bias.reshape(4, -1)[i, a] = 25.
                owner.program_map.right.bias.reshape(4, -1)[i, b] = 25.
            owner.program_map.output.bias[10] = 25.
    task = CoreSession(owner, GOAL, source='engineering-fixture')
    task.remember({'kind': 'text', 'text': 'The inputs are two rational quantities.',
                   'source': 'fixture', 'id': 'input-1'})
    return task


def assessor(task, assessment_id='exact-1', *, terms=TARGET):
    return ProgramContract(goal_id=identity(task.goal), source_sha256='b'*64, assessment_id=assessment_id,
                           arity=task.goal['arity'], assumptions=task.goal['assumptions'], polynomial_terms=terms)


def test_parallel_graph_likelihood_reaches_the_actual_field_and_memory():
    task = prepared(force=False); owner = task.owner
    state = task.rebuild()
    distribution = owner.program_distribution(state, [task.executable_question()], [2])
    proposals = sample(distribution, 16)
    objective = -torch.stack([log_probability(distribution, p['program'], p['branch']) for p in proposals]).mean()
    objective.backward()
    for name in ('words.weight', 'core.links', 'core.raw_rates', 'core.raw_couplings',
                 'core.action.coefficients', 'fusion.encoding.weight', 'flow.rates.2.weight',
                 'program_map.operations.weight', 'program_map.left.weight', 'program_map.output.weight'):
        gradient = dict(owner.named_parameters())[name].grad
        assert gradient is not None and torch.isfinite(gradient).all() and gradient.abs().sum() > 0, name
    assert all(p['program']['arity'] == 2 for p in proposals)


def test_proposals_are_pure_and_alias_credit_updates_the_same_optimizer_once():
    task = prepared(); state = task.state_id(); weights = task.weights; optimizer = task.optimizer
    proposed = task.propose_programs(8)
    assert task.state_id() == state and task.weights == weights
    assert all(execute(p['program'], [2, 3])['value'] == '25' for p in proposed['proposals'])
    record = task.grade_programs(proposed['id'], assessor(task))
    assert record['updated'] and task.weights != weights and task.optimizer is optimizer
    assert len(task.portfolio) == 1 and sum(a['reward'] > 0 for a in record['assessments']) == 1
    assert record['returned_answer'] == task.answer() and task.goal == GOAL
    assert task.state_id() != state and task.events[-1]['kind'] == 'credit'
    assert task.portfolio[0]['review']['kind'] == 'polynomial_identity'
    with pytest.raises(ValueError, match='committed'): task.grade_programs(proposed['id'], assessor(task))


def test_exact_pending_portfolio_next_update_optimizer_and_rng_resume(tmp_path):
    task = prepared(); proposed = task.propose_programs(4); task.save(tmp_path)
    expected_random = torch.rand(2); expected_python = random.random()
    expected = task.grade_programs(proposed['id'], assessor(task))
    restored = CoreSession.load(tmp_path)
    assert torch.equal(torch.rand(2), expected_random) and random.random() == expected_python
    assert restored.propose_programs() == proposed
    actual = restored.grade_programs(proposed['id'], assessor(restored))
    assert actual == expected and restored.weights == task.weights
    assert restored.answer() == task.answer()
    for left, right in zip(task.optimizer.state.values(), restored.optimizer.state.values()):
        assert left.keys() == right.keys()
        assert all(torch.equal(left[k], right[k]) for k in left)
    restored.save(tmp_path); again = CoreSession.load(tmp_path)
    assert again.answer() == restored.answer() and again.program_reviews == restored.program_reviews


def test_repeated_assessment_and_renamed_goal_do_not_reset_novelty():
    task = prepared(); first = task.propose_programs(2); contract = assessor(task)
    task.grade_programs(first['id'], contract)
    next_decision = task.propose_programs(2)
    with pytest.raises(ValueError, match='Repeated'): task.grade_programs(next_decision['id'], contract)
    task.grade_programs(next_decision['id'], assessor(task, 'exact-2'))
    task.continue_with_goal({**GOAL, 'hypothesis': 'Please compute the squared sum.',
                            'assumptions': ['two rational numbers']}, source='new-question')
    third = task.propose_programs(2); weights = task.weights
    reviewed = task.grade_programs(third['id'], assessor(task, 'exact-3'))
    assert not reviewed['updated'] and task.weights == weights
    assert all(r['reward'] == 0 for r in reviewed['assessments'])
    assert len(task.portfolio) == 1 and len(task.goal_history) == 1
    assert task.answer()['qualified_programs']


def test_changed_scope_predictor_and_committed_graph_reject():
    task = prepared(); decision = task.propose_programs(1)
    wrong = ProgramContract(goal_id='a'*64, source_sha256='b'*64, assessment_id='wrong',
                            arity=2, assumptions=GOAL['assumptions'], polynomial_terms=TARGET)
    with pytest.raises(ValueError, match='different original'): task.grade_programs(decision['id'], wrong)
    task.pending['proposals'][0]['program']['output'] = 0
    with pytest.raises(ValueError, match='committed'): task.grade_programs(decision['id'], assessor(task))
    task.pending = decision
    with torch.no_grad(): task.owner.program_map.output.bias.add_(.1)
    with pytest.raises(ValueError, match='Stale'): task.grade_programs(decision['id'], assessor(task))


def test_failed_proposals_are_retained_and_receive_no_discovery_bonus():
    task = prepared(); decision = task.propose_programs(4)
    reviewed = task.grade_programs(decision['id'], assessor(task, terms=[[[0, 0], '1']]))
    assert reviewed['updated'] and not task.portfolio and len(task.program_reviews) == 1
    assert sum(r['reward'] < 0 for r in reviewed['assessments']) == 1
    assert all(r['method_bonus'] == 0 for r in reviewed['assessments'])
    assert all(r['review']['failure'] for r in reviewed['assessments'])


def test_failed_optimizer_update_restores_owner_and_keeps_pending(monkeypatch):
    task = prepared(); decision = task.propose_programs(1)
    original = copy.deepcopy(task.owner.state_dict()); state = task.state_id()
    def fail():
        with torch.no_grad(): next(task.owner.parameters()).fill_(torch.nan)
    monkeypatch.setattr(task.optimizer, 'step', fail)
    with pytest.raises(ValueError, match='Nonfinite'): task.grade_programs(decision['id'], assessor(task))
    assert all(torch.equal(v, task.owner.state_dict()[k]) for k, v in original.items())
    assert task.state_id() == state and task.pending == decision and not task.portfolio


def test_preserved_specification_reconstructs_without_new_weights(tmp_path):
    torch.manual_seed(22)
    owner = CoreOwner(NativeConfig(nodes=3, rounds=1), program_slots=0)
    old = CoreSession(owner, {'hypothesis': 'A measured response.', 'force': .2, 'velocity': .1}, source='old-fixture')
    old.save(tmp_path); restored = CoreSession.load(tmp_path)
    assert 'program_slots' not in restored.owner.specification()
    assert restored.answer() == old.answer() and weight_hash(restored.owner) == weight_hash(owner)
