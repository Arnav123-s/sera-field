import copy
import random

import pytest
import torch

from sera_field.joint_session import JointSession
from sera_field.model import weight_hash
from sera_field.native_data import physical_episode, independent_outcome
from sera_field.native_owner import NativeOwner


def prepared():
    torch.manual_seed(202020); owner = NativeOwner()
    # A tied finite score selects the first permitted measurement. This is
    # fixture setup for receipt validation, not evidence of a learned policy.
    with torch.no_grad(): owner.choice.weight.zero_(); owner.choice.bias.zero_()
    episode = physical_episode('joint-session-fixture', 1)
    goal = {'hypothesis': 'A person is standing.', 'force': .2, 'velocity': -.1}
    task = JointSession(owner, goal, source='engineering-fixture')
    task.remember({'kind': 'text', 'text': 'A person is standing near a window.',
                   'id': 'text-1', 'source': 'fixture'})
    for i, (f, v, response) in enumerate(episode['support'][:2]):
        task.remember({'kind': 'measurement', 'id': 'observation-'+str(i), 'source': 'simulator',
                       'performed': True, 'force': f, 'velocity': v, 'response': response})
    return task, episode


def observe(task, episode, *, mismatch=False):
    decision = task.propose(); f, v = decision['requested']
    if mismatch: f += .125
    result = task.observe(decision['id'], {'kind': 'measurement', 'id': 'probe-1', 'source': 'simulator',
        'performed': True, 'force': f, 'velocity': v,
        'response': independent_outcome(episode['teacher_only'], f, v)})
    return decision, result


def grade(task, episode, decision):
    return task.grade(decision['id'], independent_response=independent_outcome(episode['teacher_only'], .2, -.1),
                      source='independent-goal-assessment', verifier='scalar-checker', evidence_id='assessment-1')


def test_credit_changes_existing_owner_reencodes_history_and_exactly_restores(tmp_path):
    task, episode = prepared(); old = weight_hash(task.owner); goal = copy.deepcopy(task.goal)
    decision, transition = observe(task, episode)
    record = grade(task, episode, decision)
    assert record['updated'] and record['before_weights'] == old
    assert record['after_weights'] != old and task.goal == goal
    assert task.state['events'].item() == 5
    answer = task.answer(); task.save(tmp_path)
    expected_random = torch.rand(3); expected_python_random = random.random()
    restored = JointSession.load(tmp_path)
    assert torch.equal(torch.rand(3), expected_random)
    assert random.random() == expected_python_random
    assert restored.answer() == answer
    assert restored.credits == task.credits
    assert restored.optimizer.state_dict()['param_groups'] == task.optimizer.state_dict()['param_groups']
    for key, state in task.optimizer.state_dict()['state'].items():
        for name, value in state.items():
            assert torch.equal(restored.optimizer.state_dict()['state'][key][name], value)
    with pytest.raises(ValueError, match='Repeated credit'):
        grade(restored, episode, decision)


def test_pending_decision_survives_restart_without_becoming_observation(tmp_path):
    task, _ = prepared(); pending = task.propose(); answer = task.answer()
    task.save(tmp_path); restored = JointSession.load(tmp_path)
    assert restored.propose() == pending and restored.answer() == answer
    with pytest.raises(ValueError, match='Unread or unperformed'):
        restored.observe(pending['id'], {'kind': 'measurement', 'id': 'unread', 'source': 'fixture',
            'performed': True, 'force': pending['requested'][0], 'velocity': pending['requested'][1], 'response': None})
    assert restored.propose() == pending and restored.answer() == answer


def test_wrong_control_is_observed_but_does_not_update_decision_weights():
    task, episode = prepared(); before = weight_hash(task.owner)
    decision, transition = observe(task, episode, mismatch=True)
    assert not transition['performed_as_requested']
    record = grade(task, episode, decision)
    assert record['policy_credit'] == 0 and not record['updated']
    assert weight_hash(task.owner) == before
    assert task.events[-2]['force'] != decision['requested'][0]


def test_stale_or_overflow_credit_preserves_all_state():
    task, episode = prepared(); decision, _ = observe(task, episode)
    before = task.answer(); weights = weight_hash(task.owner)
    with pytest.raises(ValueError, match='Representable independent'):
        task.grade(decision['id'], independent_response=1e100, source='source', verifier='verifier', evidence_id='huge')
    assert task.answer() == before and weight_hash(task.owner) == weights and not task.credits
    task.remember({'kind': 'text', 'id': 'new-text', 'source': 'fixture', 'text': 'The person leaves.'})
    with pytest.raises(ValueError, match='Stale transition'):
        grade(task, episode, decision)


def test_external_predictor_change_cannot_receive_stale_reward():
    task, episode = prepared(); decision, _ = observe(task, episode)
    with torch.no_grad(): task.owner.response.bias.add_(.1)
    with pytest.raises(ValueError, match='Stale session predictor'):
        grade(task, episode, decision)
