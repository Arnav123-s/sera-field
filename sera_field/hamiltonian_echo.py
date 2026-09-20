"""Reversible prior-credit operator for the existing Clifford/sheaf action.

This is an explicitly qualified component, not a replacement for the trained
settling owner. Fixed canonical weight coordinates have no kinetic term during
a trajectory; their conjugate momenta accumulate local forces. Dissipative
capture and parameter updates are external to every reversible pass.
"""
from dataclasses import dataclass

import torch

from .clifford_sheaf import sheaf_action, sheaf_gradient


@dataclass
class PhaseState:
    position: torch.Tensor
    momentum: torch.Tensor
    prior_momentum: torch.Tensor

    def reverse(self):
        return PhaseState(self.position, -self.momentum, -self.prior_momentum)


class SheafHamiltonian:
    """H = p.p/2 + A(q; prior, restrictions, source, stiffness, strength).

    The prior is constant within each pass; r_dot = stiffness*(q-prior).
    Velocity Verlet is a symmetric symplectic discrete flow. It is reversible
    within numerical precision, not an exactly energy-conserving integrator.
    """
    def __init__(self, source, restrictions, prior, stiffness, strength, *, dt=.025, steps=16):
        if not 0 < dt <= .05 or not isinstance(steps, int) or not 1 <= steps <= 256:
            raise ValueError('Explicit finite, positive integration parameters required')
        if any(not torch.isfinite(x).all() for x in (source, restrictions, prior, stiffness, strength)):
            raise ValueError('Finite Hamiltonian coefficients required')
        self.source, self.restrictions, self.prior = source, restrictions, prior
        self.stiffness, self.strength = stiffness, strength
        self.dt, self.steps = dt, steps

    def forces(self, q):
        return (-sheaf_gradient(q, self.source, self.restrictions, self.prior,
                                self.stiffness, self.strength),
                self.stiffness * (q-self.prior))

    def evolve(self, state):
        q, p, r = state.position, state.momentum, state.prior_momentum
        for _ in range(self.steps):
            force, credit_force = self.forces(q)
            half_p = p + .5*self.dt*force
            half_r = r + .5*self.dt*credit_force
            q = q + self.dt*half_p
            force, credit_force = self.forces(q)
            p = half_p + .5*self.dt*force
            r = half_r + .5*self.dt*credit_force
        return PhaseState(q, p, r)

    def energy(self, state):
        return .5*state.momentum.square().sum((-1,-2)) + sheaf_action(
            state.position, self.source, self.restrictions, self.prior, self.stiffness, self.strength)

    @torch.no_grad()
    def echo(self, final, output_gradient, epsilon):
        perturbed = PhaseState(final.position, final.momentum - epsilon*output_gradient,
                               final.prior_momentum)
        return self.evolve(perturbed.reverse()).reverse()

    @torch.no_grad()
    def prior_gradient(self, initial, output_gradient, *, epsilon=1e-4):
        if not 0 < epsilon <= .01:
            raise ValueError('A finite positive error impulse in (0,.01] is required')
        final = self.evolve(initial)
        if output_gradient.shape != final.position.shape or not torch.isfinite(output_gradient).all():
            raise ValueError('A finite terminal gradient matching the position state is required')
        plus = self.echo(final, output_gradient, epsilon)
        minus = self.echo(final, output_gradient, -epsilon)
        gradient = ((minus.prior_momentum-plus.prior_momentum)/(2*epsilon)).sum(0)
        if not torch.isfinite(gradient).all():
            raise ValueError('Divergent echo; no prior update is qualified')
        return gradient, {'forward_passes': 1, 'echo_passes': 2,
                          'integration_steps': 3*self.steps, 'epsilon': epsilon,
                          'credit_scope': 'Gradient with respect to the fixed prior coordinates only',
                          'training_weights_modified': False}
