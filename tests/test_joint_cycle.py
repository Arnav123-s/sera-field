import copy

import pytest
import torch

from sera_field.joint_cycle import (replay, answers, checked_progress,
                                   policy_objective, investigation_logits)
from sera_field.joint_data import paired
from sera_field.joint_training import cycle, mixed_state, observe_actions
from sera_field.native_owner import NativeOwner


def fixture():
    torch.manual_seed(202020)
    owner = NativeOwner()
    rows = [{'id': str(i), 'source_group': str(i), 'premise': text,
             'hypothesis': 'Someone is near a window.', 'target': i % 3}
            for i, text in enumerate(('A person looks through a window.', 'The empty room is dark.'))]
    return owner, paired(rows, 'joint-engineering-tests')


def test_mixed_queries_are_pure_and_share_observed_state():
    owner, rows = fixture(); state = mixed_state(owner, rows)
    saved = copy.deepcopy({k: v.detach() if isinstance(v, torch.Tensor) else v for k, v in state.items()})
    result = answers(owner, state, [r['human']['hypothesis'] for r in rows], torch.tensor([[.2, .3], [-.1, .4]]))
    assert result['semantic'].shape == (2, 3, 3)
    assert result['physical'].shape == (2, 3)
    assert all(torch.equal(v.detach(), saved[k]) for k, v in state.items() if isinstance(v, torch.Tensor))
    assert state['events'].tolist() == [4, 4]


def test_stop_is_not_an_unread_or_invented_measurement():
    owner, rows = fixture(); state = mixed_state(owner, rows)
    after, measured, _ = observe_actions(owner, state, rows, torch.tensor([9, 0]))
    assert measured.tolist() == [False, True]
    assert after['events'].tolist() == [4, 5]
    for key, value in state.items():
        if isinstance(value, torch.Tensor):
            assert torch.equal(after[key][0], value[0])


def test_executed_control_mismatch_cannot_earn_policy_credit():
    result = checked_progress(torch.tensor([2., 2.]), torch.tensor([1., 1.]), torch.tensor([0., 0.]),
        requested=torch.tensor([[1., 0.], [1., 0.]]), actual=torch.tensor([[1., 0.], [0., 0.]]))
    assert torch.allclose(result['signed_progress'], torch.tensor([3., 3.]))
    assert result['performed_as_requested'].tolist() == [True, False]
    assert result['policy_credit'][1] == 0
    assert torch.isclose(result['policy_credit'][0], torch.tensor(2.999))


def test_uniform_behavior_policy_gradient_matches_exact_expected_reward():
    logits = torch.tensor([[.3, -.5, 1.]], dtype=torch.float64, requires_grad=True)
    reward = torch.tensor([.2, -.3, .7], dtype=torch.float64)
    repeated = logits.expand(3, -1)
    objective = policy_objective(repeated, torch.arange(3), reward,
        behavior_probability=torch.full((3,), 1/3, dtype=torch.float64), entropy_weight=0)
    estimated, = torch.autograd.grad(objective, logits, retain_graph=True)
    exact, = torch.autograd.grad(-(logits.softmax(-1)*reward).sum(), logits)
    assert torch.allclose(estimated, exact, atol=1e-14, rtol=1e-12)


def test_reward_reaches_existing_choice_and_memory_without_new_parameters():
    owner, rows = fixture(); state = mixed_state(owner, rows)
    names = tuple(dict(owner.named_parameters()))
    logits = investigation_logits(owner, state, torch.tensor([[.4, .2], [-.3, .1]]), torch.tensor([[-1., 0.], [1., 0.]]))
    policy_objective(logits, torch.tensor([0, 1]), torch.tensor([.5, -.3]), entropy_weight=0).backward()
    assert owner.choice.weight.grad.abs().sum() > 0
    assert owner.number_source[0].weight.grad.abs().sum() > 0
    assert owner.memory.raw_fast.grad.abs().sum() > 0
    assert tuple(dict(owner.named_parameters())) == names


def test_masked_actions_keep_finite_entropy_and_gradient():
    logits = torch.tensor([[1., -torch.inf, .2]], requires_grad=True)
    policy_objective(logits, torch.tensor([0]), torch.tensor([1.])).backward()
    assert torch.isfinite(logits.grad).all()
    with pytest.raises(ValueError, match='permitted action'):
        policy_objective(logits, torch.tensor([1]), torch.tensor([1.]))


def test_mixed_training_has_finite_credit_and_backward():
    owner, rows = fixture()
    loss, records, components = cycle(owner, rows, training=True)
    loss.backward()
    assert torch.isfinite(loss)
    assert len(records) == 2 and set(components) == {'semantic', 'physical', 'next_query', 'policy'}
    assert all(r['behavior_probability'] == .1 for r in records)
    assert all(p.grad is None or torch.isfinite(p.grad).all() for p in owner.parameters())


def test_replay_masks_absent_observation_and_rejects_bad_shapes():
    owner, _ = fixture()
    state = replay(owner, [{'kind': 'measurement', 'actual': torch.tensor([[1., 0., .2], [1., 0., .2]]),
                           'present': torch.tensor([False, True])}], 2)
    assert state['events'].tolist() == [0, 1]
    with pytest.raises(ValueError, match='Aligned human'):
        answers(owner, state, ['question'], torch.tensor(1.))
