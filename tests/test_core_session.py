import copy
import random

import pytest
import torch

from sera_field.core_owner import CoreOwner
from sera_field.core_session import CoreSession
from sera_field.native_owner import NativeConfig
from sera_field.model import weight_hash


def prepared():
    torch.manual_seed(22202)
    owner = CoreOwner(NativeConfig(nodes=4, rounds=1))
    # Force a non-STOP choice solely to exercise the update and receipt path.
    # These fixtures are not policy teaching or evidence of learned curiosity.
    with torch.no_grad():
        owner.choice.weight.zero_(); owner.choice.bias.zero_()
    task = CoreSession(owner, {'hypothesis': 'A person sees a flower.', 'force': .2, 'velocity': .1},
                       source='core-engineering-fixture')
    task.remember({'id': 'text-1', 'source': 'fixture', 'kind': 'text',
                   'text': 'A person looks at a flower.'})
    return task


def measurement(task, decision, *, mismatch=False):
    f, v = decision['requested']
    if mismatch: f += .125
    return task.observe(decision['id'], {'kind': 'measurement', 'id': 'measurement-'+str(len(task.events)),
        'source': 'independent-fixture-simulator', 'performed': True,
        'force': f, 'velocity': v, 'response': .5*f-.2*v})


def grade(task, decision, evidence_id):
    return task.grade(decision['id'], independent_response=.08, source='separate-assessor-fixture',
                      verifier='independent-linear-law', evidence_id=evidence_id)


def test_pending_question_evidence_credit_and_next_update_resume_exactly(tmp_path):
    task = prepared(); original_goal = copy.deepcopy(task.goal)
    decision = task.propose(); weights = weight_hash(task.owner); state = task.state_id()
    task.save(tmp_path)
    expected_rng = torch.rand(2); expected_python = random.random()
    restored = CoreSession.load(tmp_path)
    assert torch.equal(torch.rand(2), expected_rng) and random.random() == expected_python
    assert restored.propose() == decision and restored.state_id() == state
    assert restored.answer() == task.answer()
    for run in (task, restored):
        measurement(run, decision)
        record = grade(run, decision, 'independent-1')
        assert record['updated'] and record['before_weights'] == weights
        assert record['after_weights'] != weights and run.goal == original_goal
        assert record['returned_answer'] == run.answer()
        with pytest.raises(ValueError, match='Repeated credit'):
            grade(run, decision, 'independent-1')
    assert weight_hash(restored.owner) == weight_hash(task.owner)
    assert restored.answer() == task.answer() and restored.credits == task.credits
    restored.save(tmp_path); again = CoreSession.load(tmp_path)
    assert again.answer() == restored.answer() and again.credits == restored.credits


def test_unread_outcome_and_wrong_intervention_do_not_farm_credit():
    task = prepared(); decision = task.propose(); before = task.answer()
    with pytest.raises(ValueError, match='Unread or unperformed'):
        task.observe(decision['id'], {'id': 'unread', 'source': 'fixture', 'kind': 'measurement',
            'performed': True, 'force': 0., 'velocity': 0., 'response': None})
    assert task.answer() == before and task.propose() == decision
    measurement(task, decision, mismatch=True)
    weights = weight_hash(task.owner)
    record = grade(task, decision, 'independent-2')
    assert not record['updated'] and not record['transition']['performed_as_requested']
    assert weight_hash(task.owner) == weights


def test_changed_predictor_rejects_stale_reward():
    task = prepared(); decision = task.propose(); measurement(task, decision)
    with torch.no_grad(): task.owner.response.bias.add_(.1)
    with pytest.raises(ValueError, match='Stale session predictor'):
        grade(task, decision, 'independent-3')
