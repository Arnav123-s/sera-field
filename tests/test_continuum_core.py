import itertools

import pytest
import torch

from sera_field.continuum_core import ConditionalGaugeFlow, MemoryContinuum, nrch_step, bulk_laplacian, bulk_spectral_length
from sera_field.semantic_owner import rotation
from sera_field.perfect_tensor_memory import code_isometry, pauli_word, encode, recover, encode_density, decode_density


def test_conditional_flow_inverse_covariance_density_and_gradients():
    torch.manual_seed(1601)
    flow = ConditionalGaugeFlow(4).double()
    source = torch.randn(2, 4, 3, dtype=torch.float64) * .2
    context = torch.randn(2, 4, dtype=torch.float64)
    links = rotation(torch.randn(4, 3, dtype=torch.float64) * .1)
    frames = rotation(torch.randn(4, 3, dtype=torch.float64))
    value, logdet = flow(source, context, links)
    returned, inverse_logdet = flow(value, context, links, reverse=True)
    assert torch.allclose(returned, source, atol=1e-12)
    assert torch.equal(logdet, -inverse_logdet)
    rotated_source = torch.einsum('nij,bnj->bni', frames, source)
    rotated_links = frames.roll(-1, 0) @ links @ frames.transpose(-1, -2)
    rotated, changed_logdet = flow(rotated_source, context, rotated_links)
    assert torch.allclose(rotated, torch.einsum('nij,bnj->bni', frames, value), atol=1e-12)
    assert torch.allclose(changed_logdet, logdet, atol=1e-12)
    jacobian = torch.autograd.functional.jacobian(
        lambda x: flow(x.reshape(1, 4, 3), context[:1], links)[0].flatten(), source[:1].flatten())
    assert abs(torch.linalg.slogdet(jacobian)[1] - logdet[0]) < 1e-12
    value.square().sum().backward()
    assert flow.rates[-1].weight.grad.abs().sum() > 0
    assert bool((flow.gaussian_reverse_kl(context, links) >= -1e-12).all())


def test_nrch_conserves_mass_and_matches_independent_dense_step():
    torch.manual_seed(1602)
    fields = torch.randn(1, 2, 3, 4, 3, dtype=torch.float64) * .1
    target = torch.randn_like(fields) * .1
    actual = nrch_step(fields, target, alpha=.3)
    # Build the spatial Laplacian independently, without the Fourier formula.
    size = 12; lap = torch.zeros(size, size, dtype=torch.float64)
    for d in range(3):
        for n in range(4):
            i = 4 * d + n; lap[i, i] = -4
            for dd, nn in (((d + 1) % 3, n), ((d - 1) % 3, n), (d, (n + 1) % 4), (d, (n - 1) % 4)):
                lap[i, 4 * dd + nn] += 1
    one, two = fields[0]; expected = []
    for i, (value, other, coefficient, kappa, rate) in enumerate(((one, two, .45, .08, 1.), (two, one, -.15, .16, .5))):
        mu = -.5 * value + value.pow(3) - coefficient * other + .5 * (value - target[0, i])
        rhs = value.reshape(size, 3) + .01 * rate * lap @ mu.reshape(size, 3)
        expected.append(torch.linalg.solve(torch.eye(size, dtype=torch.float64) + .01 * rate * kappa * lap @ lap, rhs).reshape_as(value))
    assert torch.allclose(actual[0], torch.stack(expected), atol=1e-12)
    assert torch.allclose(actual.sum((-3, -2)), fields.sum((-3, -2)), atol=1e-12)
    assert torch.allclose(bulk_laplacian(one).reshape(size, 3), lap @ one.reshape(size, 3), atol=1e-12)


def test_coupled_traces_are_distinct_differentiable_and_do_not_mutate_input():
    torch.manual_seed(1603)
    model = MemoryContinuum(4).double()
    state = model.empty(1); stimulus = torch.randn(1, 4, 3, dtype=torch.float64) * .2
    links = torch.eye(3, dtype=torch.float64).repeat(4, 1, 1)
    first, _ = model.advance(state, stimulus, torch.tensor([.2], dtype=torch.float64), links)
    second, report = model.advance(first, -stimulus, torch.tensor([-.1], dtype=torch.float64), links)
    assert not torch.equal(second['fast'], second['slow'])
    assert bool((second['marks'] > 0).all())
    assert torch.equal(state['fast'], torch.zeros_like(state['fast'])) and state['events'] == 0
    assert report['relaxation_mass_error'].abs().max() < 1e-12
    assert report['slow_rate'] < report['fast_rate']
    model.recall(second, links).square().sum().backward()
    assert model.raw_fast.grad.abs() > 0 and model.raw_slow.grad.abs() > 0


def test_spectral_length_distinguishes_uniform_and_known_spatial_period():
    constant = torch.ones(1, 2, 4, 8, 3, dtype=torch.float64)
    length, power = bulk_spectral_length(constant)
    assert not length.any() and not power.any()
    wave = torch.sin(2 * torch.pi * torch.arange(8, dtype=torch.float64) / 4)
    value = constant + wave[None, None, None, :, None]
    length, power = bulk_spectral_length(value)
    assert torch.allclose(length, torch.full_like(length, 4.), atol=1e-12)
    assert bool((power > 0).all())


def test_perfect_tensor_isometry_and_all_unknown_single_pauli_errors():
    code = code_isometry()
    assert torch.allclose(code.conj().T @ code, torch.eye(2, dtype=code.dtype), atol=1e-12)
    logical = torch.tensor([.4 + .2j, -.3 + .7j], dtype=torch.complex128)
    logical /= torch.linalg.vector_norm(logical)
    encoded = encode(logical); expected = logical[:, None] * logical.conj()[None]
    words = ['IIIII']
    for i in range(5):
        for letter in 'XYZ':
            word = ['I'] * 5; word[i] = letter; words.append(''.join(word))
    for word in words:
        density, syndrome = recover(pauli_word(word) @ encoded)
        assert torch.allclose(density, expected, atol=1e-12)
        assert abs(syndrome.sum() - 1) < 1e-12


def test_every_pair_of_declared_erasures_and_finite_density_roundtrip():
    logical = torch.tensor([1., 1j], dtype=torch.complex128) / 2 ** .5
    encoded = encode(logical); expected = logical[:, None] * logical.conj()[None]
    for sites in itertools.combinations(range(5), 2):
        mixture = torch.zeros(2, 2, dtype=torch.complex128)
        for errors in itertools.product('IXYZ', repeat=2):
            word = ['I'] * 5
            for site, letter in zip(sites, errors):
                word[site] = letter
            decoded, _ = recover(pauli_word(''.join(word)) @ encoded, erasures=sites)
            mixture += decoded / 16
        assert torch.allclose(mixture, expected, atol=1e-12)
    with pytest.raises(ValueError, match='at most two'):
        recover(encoded, erasures=(0, 1, 2))
    represented = torch.linspace(.001, .999, 13, dtype=torch.float64)
    restored, _ = decode_density(encode_density(represented))
    assert torch.allclose(restored, represented, atol=1e-12)
