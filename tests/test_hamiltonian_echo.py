"""Qualification fixtures for a new operator; no final cohort or training repair."""
import torch

from sera_field.clifford_sheaf import lift_rotation
from sera_field.gauge import adjoint_rotations
from sera_field.hamiltonian_echo import PhaseState, SheafHamiltonian


def fixture(*, prior=None):
    generator = torch.Generator().manual_seed(70703)
    source = .2*torch.randn(2, 4, 8, generator=generator, dtype=torch.float64)
    links = .15*torch.randn(4, 3, generator=generator, dtype=torch.float64)
    restrictions = lift_rotation(adjoint_rotations(links))
    base = .05*torch.randn(4, 8, generator=generator, dtype=torch.float64)
    q = .1*torch.randn(2,4,8, generator=generator, dtype=torch.float64)
    p = .05*torch.randn(2,4,8, generator=generator, dtype=torch.float64)
    initial = PhaseState(q, p, torch.zeros_like(q))
    system = SheafHamiltonian(source, restrictions, base if prior is None else prior,
                              torch.tensor(.5, dtype=torch.float64), torch.tensor(.15, dtype=torch.float64))
    return system, initial


def test_echo_reconstructs_full_canonical_state_without_dissipation():
    system, initial = fixture()
    with torch.no_grad():
        final = system.evolve(initial)
        restored = system.echo(final, torch.zeros_like(final.position), 0.)
    for name in ('position','momentum','prior_momentum'):
        torch.testing.assert_close(getattr(initial,name), getattr(restored,name), atol=2e-14, rtol=2e-14)
    assert (system.energy(final)-system.energy(initial)).abs().max() < .002


def test_echo_prior_credit_matches_autograd_and_parameter_finite_difference():
    system, initial = fixture()
    prior = system.prior.detach().clone().requires_grad_(True)
    exact, _ = fixture(prior=prior)
    target = torch.zeros_like(initial.position)
    final = exact.evolve(initial)
    loss = .5*(final.position-target).square().sum()
    expected, = torch.autograd.grad(loss, prior)
    actual, cost = system.prior_gradient(initial, final.position.detach()-target)
    torch.testing.assert_close(actual, expected, atol=2e-8, rtol=2e-7)
    direction = torch.linspace(-1, 1, prior.numel(), dtype=prior.dtype).reshape_as(prior)
    plus, minus = fixture(prior=prior.detach()+1e-5*direction)[0], fixture(prior=prior.detach()-1e-5*direction)[0]
    numerical = (.5*plus.evolve(initial).position.square().sum() -
                 .5*minus.evolve(initial).position.square().sum())/2e-5
    torch.testing.assert_close((actual*direction).sum(), numerical, atol=1e-8, rtol=1e-7)
    assert not actual.requires_grad and cost['integration_steps'] == 48


def test_damping_is_not_accepted_as_a_hamiltonian_echo():
    system, initial = fixture()
    final = system.evolve(initial)
    damped = PhaseState(final.position, .8*final.momentum, final.prior_momentum)
    restored = system.echo(damped, torch.zeros_like(final.position), 0.)
    assert (restored.position-initial.position).norm() > .001


def test_reversal_does_not_mutate_source_or_prior():
    system, initial = fixture()
    before = [x.clone() for x in (system.source, system.prior, initial.position, initial.momentum)]
    final = system.evolve(initial)
    system.prior_gradient(initial, final.position.detach())
    for a,b in zip(before, (system.source,system.prior,initial.position,initial.momentum)):
        torch.testing.assert_close(a,b,rtol=0,atol=0)
