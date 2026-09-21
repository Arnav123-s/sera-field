import copy
import json

import pytest
import torch

from sera_field.core_learning import LearningContract
from sera_field.core_session import CoreSession
from scripts.probe_core022_learning import prepared, frozen_contract, compact, continuation


def test_real_practice_checked_credit_and_returned_question(tmp_path):
    task = prepared(); contract = frozen_contract(); original = copy.deepcopy(task.goal)
    optimizer = task.optimizer; weights = task.weights
    proposed = task.propose_learning(contract, tmp_path/'trial')
    assert not proposed['assessment_seen'] and proposed['weights'] == weights
    first = task.practice_learning(contract)
    assert first['after_weights'] != weights and task.learning_trial['cursor'] == 1
    result = continuation(task, contract)
    procedure = result['procedure']
    assert procedure['gain'] == 1 and procedure['retention_loss'] == 0 and procedure['reward'] == .998
    assert procedure['weights_after_practice'] != procedure['weights_after_credit']
    assert procedure['after_procedure_credit']['scores'] == {'acquisition': 1., 'retention': 1.}
    assert task.optimizer is optimizer and task.goal == original
    assert result['returned']['returned_answer']['qualified_programs']
    with pytest.raises(ValueError, match='already consumed'):
        task.propose_learning(contract, tmp_path/'again')


def test_mid_trial_resume_uses_next_cursor_without_repeating_practice(tmp_path):
    task = prepared(); contract = frozen_contract(); task.propose_learning(contract, tmp_path/'trial')
    task.practice_learning(contract)
    task.save(tmp_path/'midpoint')
    expected = continuation(task, contract)
    resumed = CoreSession.load(tmp_path/'midpoint')
    resumed.learning_trial['directory'] = str(tmp_path/'resumed')
    assert resumed.learning_trial['cursor'] == 1
    actual = continuation(resumed, contract)
    assert actual == expected


def test_learning_splits_and_equal_update_limits_are_enforced():
    source = frozen_contract()
    reviews = copy.deepcopy(source.reviews)
    reviews[0]['group'] = next(iter(source.lessons.values()))['group']
    with pytest.raises(ValueError, match='overlaps'):
        LearningContract(source.lessons, source.plans, reviews)
    plans = copy.deepcopy(source.plans); plans[0]['lessons'].append('first')
    with pytest.raises(ValueError, match='same finite'):
        LearningContract(source.lessons, plans, source.reviews)
    source.lessons['first']['question'] = 'changed after freeze'
    with pytest.raises(ValueError, match='changed'): source.id


def test_stale_cursor_and_parent_cannot_be_credited(tmp_path):
    task = prepared(); contract = frozen_contract(); task.propose_learning(contract, tmp_path/'trial')
    task.learning_trial['cursor'] = 1
    with pytest.raises(ValueError, match='cursor'): task.practice_learning(contract)
    task.learning_trial['cursor'] = 0
    task.practice_learning(contract); task.practice_learning(contract)
    task.learning_trial['parent_identity'] = 'bad'
    with pytest.raises(ValueError, match='advanced'): task.finish_learning(contract)
    assert task.learning_trial is not None and task.pending is not None


def test_failed_practice_does_not_consume_an_update(tmp_path, monkeypatch):
    task = prepared(); contract = frozen_contract(); task.propose_learning(contract, tmp_path/'trial')
    weights = task.weights; state = task.state_id()
    def invalid():
        with torch.no_grad(): next(task.owner.parameters()).fill_(torch.nan)
    monkeypatch.setattr(task.optimizer, 'step', invalid)
    with pytest.raises(ValueError, match='Nonfinite'): task.practice_learning(contract)
    assert task.weights == weights and task.state_id() == state and task.learning_trial['cursor'] == 0
    assert CoreSession.load(tmp_path/'trial/current').weights == weights
