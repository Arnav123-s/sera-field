import copy
import math

import pytest
import torch

from sera_field.native_data import physical_episode, independent_outcome
from sera_field.native_owner import NativeOwner
from sera_field.native_session import NativeSession


def session():
    torch.manual_seed(19119); model = NativeOwner()
    episode = physical_episode('native-session-test', 4)
    task = NativeSession(model, {'force': .4, 'velocity': -.2}, source='declared-test-simulator')
    for i, (f, v, a) in enumerate(episode['support']):
        task.remember({'id': str(i), 'source': 'test', 'performed': True, 'force': f, 'velocity': v, 'response': a})
    return task, episode


def test_checked_cycle_preserves_goal_and_rejects_repeated_credit(tmp_path):
    task, episode = session(); goal = copy.deepcopy(task.goal)
    proposal = task.propose(); requested = proposal['requested']
    evidence = {'id': 'new', 'source': 'separate-teacher', 'performed': True, **requested,
                'response': independent_outcome(episode['teacher_only'], requested['force'], requested['velocity'])}
    transition = task.observe(proposal['id'], evidence)
    truth = independent_outcome(episode['teacher_only'], goal['force'], goal['velocity'])
    credit = task.grade(proposal['id'], independent_response=truth, source='independent-goal-observation', verifier='scalar-checker')
    expected = (transition['before']-truth)**2 - (transition['after']-truth)**2
    assert math.isclose(credit['signed_progress'], expected, rel_tol=1e-12, abs_tol=1e-12)
    assert task.goal == goal
    with pytest.raises(ValueError, match='Repeated credit'):
        task.grade(proposal['id'], independent_response=truth, source='same', verifier='same')
    before = task.answer(); task.save(tmp_path)
    restored = NativeSession.load(task.owner, tmp_path)
    assert restored.answer() == before and restored.credits == task.credits


def test_unread_and_unperformed_outcomes_do_not_write_history():
    task, _ = session(); before = task.state_id(); count = len(task.observations)
    for performed, response in ((False, .3), (True, None), ('false', .3)):
        with pytest.raises(ValueError, match='unread or unperformed'):
            task.remember({'id': 'bad', 'source': 'test', 'performed': performed, 'force': 0., 'velocity': 0., 'response': response})
    assert task.state_id() == before and len(task.observations) == count


def test_nonfinite_encoded_measurement_preserves_observed_state():
    task, _ = session(); before = task.state_id()
    with pytest.raises(ValueError, match='Finite numerical coordinates'):
        task.remember({'id': 'overflow', 'source': 'test', 'performed': True,
                       'force': 1e35, 'velocity': 1e35, 'response': .4})
    assert task.state_id() == before and len(task.observations) == 4


def test_actual_intervention_values_are_checked_and_used():
    task, episode = session(); proposal = task.propose()
    f, v = .13, -.17
    evidence = {'id': 'actual', 'source': 'test', 'performed': True, 'force': f, 'velocity': v,
                'response': independent_outcome(episode['teacher_only'], f, v)}
    transition = task.observe(proposal['id'], evidence)
    assert not transition['performed_as_requested']
    assert task.observations[-1]['force'] == f


def test_predictor_change_invalidates_session():
    task, _ = session()
    with torch.no_grad(): task.owner.field.links.add_(.01)
    with pytest.raises(ValueError, match='Stale session predictor'): task.answer()


def test_large_outcome_credit_keeps_sign_and_rejects_unrepresentable_marks():
    task, _ = session()
    # An explicit audited transition isolates credit arithmetic from prediction.
    task.last_transition = {'decision': 'large', 'after_state': task.state_id(),
                            'before': 1.5, 'after': .5}
    before = task.state_id()
    with pytest.raises(ValueError, match='representable credit'):
        task.grade('large', independent_response=1e39, source='independent', verifier='test')
    assert not task.credits and task.state_id() == before
    credit = task.grade('large', independent_response=1e20, source='independent', verifier='test')
    assert credit['signed_progress'] == -2e20 and credit['positive_credit'] == 0.
    assert bool(torch.isfinite(task.state['marks']).all())
