# ECHO-005: reversible credit qualification for the actual sheaf action

Frozen before numerical execution. This is the next mathematical gate from the
latest Singular Ecosystem paper. It preserves the ongoing CONNECTED/SCFE teaching,
reward study, final registration and all trained owner identities.

Use the implemented Clifford/sheaf action A(q;theta,J,R,kappa,lambda) as a
potential in H = p.p/2 + A. The prior theta is a canonical weight coordinate
with no kinetic term during a pass. Its conjugate momentum r obeys
dr/dt = kappa*(q-theta). The evaluation variables obey dq/dt=p and
dp/dt=-dA/dq. Source, restrictions, stiffness and condensation strength are fixed
during this operator qualification. The initial q,p are independent of theta.

Use symmetric velocity Verlet, dt=.025, 16 steps, double precision. A terminal
loss contributes an error impulse p <- p - epsilon*dC/dq. Reverse both momenta,
evolve the same system, then reverse momenta again. In the small-impulse limit,
the final prior momentum equals -epsilon*dC/dtheta. Symmetric positive/negative
impulses give the derivative estimate (r_minus-r_plus)/(2*epsilon). Count one
forward and two echo trajectories, not two total evaluations. No dissipative
capture or persistent weight update occurs inside these passes.

Qualification uses only declared engineering fixtures, seed70703; no human
final rows or completed study's physical final cases. Require canonical-state
round-trip error below 2e-14; compare prior credit against autograd and a separate
parameter finite difference (absolute2e-8/1e-8). Preserve a damping counterexample
and measured energy error, since reversibility does not imply exact energy
conservation. Verify source/prior immutability. Save supervised costs and all test
failures before any repair.

If these contracts pass, the component qualifies for a future owner experiment.
It is not yet the full HEB/e-prop learner. The next integration must define the
remaining parameter/input sensitivities, a reversible situation readout and the
external evidence-qualified update, then freeze an untouched study. Never
replace dissipative settling by this flow inside an already selected checkpoint
and call the old evaluation its new performance.

The algorithm is motivated by the original
[Hamiltonian Echo Backpropagation paper](https://arxiv.org/html/2103.04992v2).
The finite sheaf potential, discretization, symmetric impulse and tests above
are explicit engineering choices, not formulas recovered from missing pasted
mathematical expressions.
