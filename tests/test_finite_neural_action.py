import copy
import math

import pytest
import torch

from sera_field.finite_neural_action import (
    FiniteNeuralAction, covariance, cumulant_generator, directional_fourth,
    edgeworth_action, exact_action_and_score, fourth_connected,
    gaussian_action, gaussian_inverse_product,
)
from sera_field.gauge import adjoint_rotations


def test_exact_conditional_density_normalization_and_score():
    x = torch.linspace(-8, 8, 8193, dtype=torch.float64)[:, None]
    f = torch.tensor([[[.3], [-.1]]], dtype=x.dtype).expand(len(x), -1, -1)
    sigma = x.new_tensor(.4)
    action, _ = exact_action_and_score(x, f, sigma)
    integral = torch.trapezoid((-action).exp(), x[:, 0])
    assert abs(float(integral) - 1) < 1e-10
    z = torch.tensor([[.17, -.23]], dtype=x.dtype, requires_grad=True)
    features = torch.tensor([[[.4, -.2], [.1, .3]]], dtype=x.dtype)
    exact, score = exact_action_and_score(z, features, sigma)
    gradient, = torch.autograd.grad(exact.sum(), z)
    assert torch.allclose(score, -gradient, atol=1e-12)


def test_connected_correlators_are_derivatives_of_the_generator():
    f = torch.tensor([[[.2, -.1], [.4, .3], [-.15, .25]]], dtype=torch.float64)
    sigma = f.new_tensor(.37)
    j = torch.zeros(2, dtype=f.dtype)
    measured = torch.autograd.functional.hessian(lambda x: cumulant_generator(x[None], f, sigma).sum(), j)
    assert torch.allclose(measured, covariance(f, sigma)[0], atol=1e-12)
    direction = f.new_tensor([[.6, -.8]])
    scale = torch.tensor(0., dtype=f.dtype, requires_grad=True)
    derivative = cumulant_generator(scale * direction, f, sigma).sum()
    for _ in range(4):
        derivative, = torch.autograd.grad(derivative, scale, create_graph=True)
    fourth = fourth_connected(f)[0]
    contracted = torch.einsum('abcd,a,b,c,d->', fourth, *[direction[0]] * 4)
    assert torch.allclose(derivative, directional_fourth(direction, f)[0], atol=1e-12)
    assert torch.allclose(contracted, derivative, atol=1e-12)


def test_finite_width_scaling_and_gaussian_limit():
    sigma = torch.tensor(.4, dtype=torch.float64)
    value = torch.tensor([[.3, -.1]], dtype=sigma.dtype)
    empty_features = torch.zeros(1, 4, 2, dtype=sigma.dtype)
    action, score = exact_action_and_score(value, empty_features, sigma)
    assert torch.allclose(action, gaussian_action(value, empty_features, sigma), atol=1e-12)
    assert torch.allclose(score, -value / sigma.square(), atol=1e-12)
    baseline = None
    for n in (1, 2, 4, 8):
        features = value[:, None].repeat(1, n, 1) / math.sqrt(n)
        k4 = directional_fourth(value, features) * n
        if baseline is None: baseline = k4
        assert torch.allclose(k4, baseline, atol=1e-12)


def test_woodbury_and_edgeworth_have_independent_references():
    torch.manual_seed(17101)
    f = torch.randn(2, 4, 3, dtype=torch.float64) * .1
    sigma = f.new_tensor(.7); value = torch.randn(2, 3, dtype=f.dtype) * .3
    cov = covariance(f, sigma)
    reference = torch.linalg.solve(cov, value[..., None]).squeeze(-1)
    assert torch.allclose(reference, gaussian_inverse_product(value, f, sigma), atol=1e-12)
    reference_action = -.0 + .5 * ((value * reference).sum(-1) +
        torch.linalg.slogdet(cov).logabsdet + 3 * math.log(2 * math.pi))
    assert torch.allclose(reference_action, gaussian_action(value, f, sigma), atol=1e-12)
    exact, _ = exact_action_and_score(value, f, sigma)
    expansion, delta = edgeworth_action(value, f, sigma)
    assert torch.allclose(expansion, reference_action - delta, atol=1e-12)
    assert float((expansion - exact).abs().max()) < .002
    # A truncated density is not operational: explicitly retain its tail failure.
    tail = torch.tensor([[10.]], dtype=f.dtype)
    _, tail_delta = edgeworth_action(tail, torch.tensor([[[.5]]], dtype=f.dtype), sigma)
    assert float(1 + tail_delta) < 0
    tail_action, tail_score = exact_action_and_score(tail, torch.tensor([[[.5]]], dtype=f.dtype), sigma)
    assert torch.isfinite(tail_action).all() and torch.isfinite(tail_score).all()


def test_local_frames_preserve_action_and_transform_the_actual_update():
    torch.manual_seed(17102)
    model = FiniteNeuralAction(4).double()
    with torch.no_grad(): model.raw_gain.fill_(.7)
    source = torch.randn(2, 4, 3, dtype=torch.float64) * .3
    transport = adjoint_rotations(torch.randn(4, 3, dtype=source.dtype))
    frame = adjoint_rotations(torch.randn(4, 3, dtype=source.dtype))
    changed_source = (frame[None] @ source[..., None]).squeeze(-1)
    changed_transport = frame.roll(-1, 0) @ transport @ frame.transpose(-1, -2)
    for mode in ('exact', 'gaussian'):
        original = model(source, transport, mode=mode)
        changed = model(changed_source, changed_transport, mode=mode)
        expected = (frame[None] @ original[..., None]).squeeze(-1)
        assert torch.allclose(changed, expected, atol=2e-12)
        assert float((original - source).norm(dim=-1).max()) <= .15
    a = model.diagnostics(source, transport)
    b = model.diagnostics(changed_source, changed_transport)
    assert torch.allclose(torch.tensor(a['exact_action']), torch.tensor(b['exact_action']), atol=1e-6)


def test_action_gradients_and_noise_modes():
    torch.manual_seed(17103)
    model = FiniteNeuralAction(3).double()
    with torch.no_grad(): model.raw_gain.fill_(.4)
    source = torch.randn(2, 3, 3, dtype=torch.float64) * .5
    r = torch.eye(3, dtype=source.dtype).repeat(3, 1, 1)
    output = model(source, r)
    output.square().sum().backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in model.parameters())
    assert model.coefficients.grad.abs().sum() > 0
    assert model.raw_sigma.grad.abs() > 0
    assert torch.equal(model(source, r, mode='disabled'), source)
    state = torch.get_rng_state(); noisy = model(source, r, noise=.03)
    torch.set_rng_state(state)
    assert torch.equal(noisy, model(source, r, noise=.03))
    assert not torch.equal(noisy, output)
    with pytest.raises(ValueError): model(source, r, noise=.5)


def test_continuing_owner_initializes_to_parent_and_restarts():
    from sera_field.genre_owner import GenreOwner, extend_genre
    from sera_field.semantic_owner import SemanticOwner
    torch.manual_seed(17104)
    parent = SemanticOwner(width=8, nodes=3, rounds=1, steps=4, extension_width=16)
    parent.eval(); owner = extend_genre(parent); owner.eval()
    source = torch.randn(2, 3, 3) * .1
    with torch.no_grad():
        a = parent.field.imagine(source)
        b = owner.field.imagine(source)
    assert all(torch.equal(x, y) for x, y in zip(a, b))
    spec = dict(owner.specification()); spec.pop('type')
    reloaded = GenreOwner(**spec); reloaded.load_state_dict(copy.deepcopy(owner.state_dict())); reloaded.eval()
    with torch.no_grad(): c = reloaded.field.imagine(source)
    assert all(torch.equal(x, y) for x, y in zip(b, c))
    assert owner.specification() == reloaded.specification()
