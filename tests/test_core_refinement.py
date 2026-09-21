import copy

import pytest
import torch

from sera_field.core_adequacy import action_scale_diagnostic, adequacy_features
from sera_field.core_owner import CoreOwner
from sera_field.core_session import CoreSession
from sera_field.native_owner import NativeConfig


def test_action_hessian_gaussian_identity_and_learned_adequacy_gradients():
    torch.manual_seed(22027); owner = CoreOwner(NativeConfig(nodes=3, rounds=1)).double()
    with torch.no_grad(): state, _ = owner.remember_texts(['A tree stands outside.'])
    source = owner.encode_texts(['A tree is visible.'])
    diagnostic = action_scale_diagnostic(owner, state, source)
    hessian = torch.tensor(diagnostic['hessian'], dtype=torch.float64)
    assert torch.allclose(hessian, hessian.T, atol=1e-12, rtol=0)
    if diagnostic['quadratic_regulated_domain_valid']:
        direct = .5*(torch.linalg.slogdet(hessian+4*torch.eye(3))[1]
                     -torch.linalg.slogdet(hessian+.25*torch.eye(3))[1])
        assert abs(direct.item()-diagnostic['integral']) < 1e-12
    features = adequacy_features([-.2, .3], [.01, .03], diagnostic, source)
    logits = owner.assess_adequacy(state, source, features)
    loss = -logits.log_softmax(-1)[0, 2]; loss.backward()
    assert owner.adequacy_policy[0].weight.grad.abs().sum() > 0
    assert owner.core.links.grad.abs().sum() > 0
    assert features[0, 2] != features[0, 3]  # measured error is not model spread


def test_actual_attachment_optimizer_migration_persistence_and_returned_goal(tmp_path):
    torch.manual_seed(22028); owner = CoreOwner(NativeConfig(nodes=3, rounds=1))
    with torch.no_grad():
        # Force the route only as an engineering fixture, not learned evidence.
        owner.adequacy_policy[-1].weight.zero_(); owner.adequacy_policy[-1].bias.copy_(torch.tensor([0., 0., 1.]))
    task = CoreSession(owner, {'hypothesis': 'A child is outside.', 'force': .2, 'velocity': -.1}, source='fixture')
    assert task.propose_refinement()['action'] == 'investigate'
    task.remember({'kind': 'measurement', 'id': 'seen-1', 'source': 'independent-fixture',
                   'performed': True, 'force': .3, 'velocity': -.2, 'response': .25})
    # A preexisting optimizer moment must survive literal growth. This fixture
    # does not train a curriculum or determine a final model selection.
    p = owner.response.weight
    task.optimizer.state[p] = {'step': torch.tensor(3.), 'exp_avg': torch.ones_like(p)*.1,
                               'exp_avg_sq': torch.ones_like(p)*.02}
    expected = copy.deepcopy(task.optimizer.state[p]); goal = copy.deepcopy(task.goal)
    proposal = task.propose_refinement(); assert proposal['action'] == 'attach'
    record = task.attach_for_retry(proposal, tmp_path, size=4)
    assert task.goal == goal and task.owner.core.extension_size == 4
    assert record['new_stalks'] == [8, 8, 8, 5]
    assert all(torch.equal(task.optimizer.state[p][k], v) for k, v in expected.items())
    assert abs(record['returned_answer']['physical']-record['before_answer']['physical']) < 1e-7
    task.save(tmp_path/'continued'); restored = CoreSession.load(tmp_path/'continued')
    assert restored.answer() == task.answer() and restored.refinements == task.refinements
    rp = restored.owner.response.weight
    assert all(torch.equal(restored.optimizer.state[rp][k], v) for k, v in expected.items())
    assert task.propose_refinement()['action'] != 'attach'
    with pytest.raises(ValueError, match='Current evidence-bound'):
        task.attach_for_retry(proposal, tmp_path)
