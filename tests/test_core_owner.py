import copy

import torch

from sera_field.core_owner import CoreOwner, ConditionalFusion
from sera_field.model import weight_hash
from sera_field.native_owner import NativeConfig


def fresh():
    torch.manual_seed(22022)
    return CoreOwner(NativeConfig(nodes=4, rounds=2))


def test_fusion_channels_are_normalized_positive_and_differentiable():
    torch.manual_seed(22022)
    router = ConditionalFusion(4).double()
    past = torch.randn(2, 4, 3, dtype=torch.float64, requires_grad=True)
    query = torch.randn_like(past, requires_grad=True)
    result = router(past, query); density = result['density']
    assert torch.allclose(density, density.mH, atol=2e-14, rtol=0)
    assert torch.linalg.eigvalsh(density).min() > -1e-14
    assert torch.allclose(result['path_probabilities'].sum(-1), torch.ones(2, dtype=torch.float64), atol=2e-14, rtol=0)
    assert not torch.allclose(density, result['unread_density'])
    result['path_probabilities'][:, 0].sum().backward()
    assert past.grad.abs().sum() > 0 and query.grad.abs().sum() > 0
    assert router.encoding.weight.grad.abs().sum() > 0


def test_absent_unread_and_read_fusion_events_change_actual_conditional_continuation():
    owner = fresh()
    with torch.no_grad():
        state, _ = owner.remember_texts(['A person watches a bird.'])
        source = owner.encode_texts(['Something flies.'])
        before = {k: v.clone() for k, v in state.items()}
        absent, a = owner.conditional(state, source)
        unread, u = owner.conditional(state, source, measurement='unread')
        assert not torch.allclose(a['continued_density'], u['continued_density'])
        assert (absent-unread).abs().max() > 1e-9
        expected = torch.zeros_like(u['continued_density'])
        for j in range(3):
            _, read = owner.conditional(state, source, measurement='read', outcome=j)
            expected += a['measurement_probabilities'][:, j, None, None]*read['continued_density']
        assert torch.allclose(expected, u['continued_density'], atol=2e-7, rtol=0)
        assert all(torch.equal(state[k], v) for k, v in before.items())


def test_observed_and_hypothetical_routes_use_one_fresh_energy_owner():
    owner = fresh(); original = owner.empty(1)
    observed, audit = owner.remember_texts(['A woman carries a flower near a tree.'])
    assert observed['events'].item() == 2
    for name in ('q', 'p', 'log_covariance', 'fast', 'slow', 'bulk'):
        assert observed[name].abs().sum() > 0, name
        assert original[name].abs().sum() == 0, name
    saved = {k:v.detach().clone() for k,v in observed.items()}; weights = weight_hash(owner)
    features, branches = owner.conditional(observed, owner.encode_texts(['Someone holds a flower.']))
    assert features.shape == (1, 3, 64)
    assert all(torch.equal(saved[k], v) for k,v in observed.items())
    assert weight_hash(owner) == weights
    assert branches['hypothetical_state']['events'].tolist() == [2, 2, 2]
    assert not hasattr(owner, 'field') and not hasattr(owner, 'memory')


def test_language_loss_reaches_fusion_flow_geometry_and_all_memory_coordinates():
    owner = fresh()
    logits = owner.semantic(['A child looks at a red ball.'], ['Someone sees a ball.'])
    loss = -logits.log_softmax(-1)[..., 0].mean(); loss.backward()
    for name in ('words.weight', 'core.links', 'core.anchors', 'core.raw_rates',
                 'core.raw_couplings', 'core.raw_activity', 'core.action.coefficients',
                 'fusion.encoding.weight', 'flow.rates.2.weight', 'raw_stationary'):
        value = dict(owner.named_parameters())[name]
        assert value.grad is not None and torch.isfinite(value.grad).all(), name
        assert value.grad.abs().sum() > 0, name


def test_numerical_context_uses_the_same_state_and_changed_observation_changes_answer():
    owner = fresh()
    support = torch.tensor([[[.2, -.3, .1], [.4, .1, .3]]])
    queries = torch.tensor([[[.3, .2]]])
    first = owner.physical(support, queries)
    second = owner.physical(support+torch.tensor([0., 0., .4]), queries)
    assert first.shape == (1, 1, 3) and not torch.allclose(first, second)
    first.square().sum().backward()
    assert owner.core.raw_rates.grad.abs().sum() > 0
    assert owner.number_source[0].weight.grad.abs().sum() > 0


def test_exact_state_and_next_update_after_checkpoint_restore(tmp_path):
    owner = fresh(); optimizer = torch.optim.AdamW(owner.parameters(), lr=.0001)
    before = copy.deepcopy(owner.state_dict()); rng = torch.get_rng_state()
    path = tmp_path/'engineering.pt'
    torch.save({'owner': before, 'optimizer': optimizer.state_dict(), 'rng': rng}, path)
    def update(model, opt):
        opt.zero_grad(set_to_none=True)
        loss = model.semantic(['A person stands outside.'], ['Someone is outdoors.']).square().mean()
        loss.backward(); opt.step()
        return model.state_dict()
    expected = copy.deepcopy(update(owner, optimizer))
    payload = torch.load(path, weights_only=False)
    restored = fresh(); restored.load_state_dict(payload['owner'])
    opt = torch.optim.AdamW(restored.parameters(), lr=.0001); opt.load_state_dict(payload['optimizer'])
    torch.set_rng_state(payload['rng'])
    actual = update(restored, opt)
    assert all(torch.equal(expected[k], actual[k]) for k in expected)


def test_multievent_learning_derivative_matches_finite_differences():
    owner = fresh().double()
    def objective():
        return owner.semantic(['A woman picks a flower.'], ['Someone holds a plant.']).square().mean()
    loss = objective()
    parameters = (owner.raw_observation_port, owner.core.raw_rates, owner.core.raw_couplings)
    analytic = torch.autograd.grad(loss, parameters)
    epsilon = 2e-4
    for parameter, derivative in zip(parameters, analytic):
        # Includes covariance, fast and slow coordinates sharing history.
        for index in range(parameter.numel()):
            original = parameter.detach().clone()
            with torch.no_grad():
                parameter.reshape(-1)[index] += epsilon
                plus = objective().item()
                parameter.copy_(original)
                parameter.reshape(-1)[index] -= epsilon
                minus = objective().item()
                parameter.copy_(original)
            numerical = (plus-minus)/(2*epsilon)
            assert abs(numerical-derivative.reshape(-1)[index].item()) < 2e-8 + 2e-4*abs(numerical)
