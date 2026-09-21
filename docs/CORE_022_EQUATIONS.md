# A coupled energy and explicit conditional fusion space

This is the engineering construction for the complete-core work order. It is
implemented in `unified_energy.py` and `fibonacci_space.py`; their independent
contracts are checked before integration into the fresh owner. Existing trained
owners retain their original equations and weights.

## Shared finite energy

The continuous coordinates are boundary multivectors q, canonical momenta p,
symmetric log-covariance stalks L, fast/slow vectors f and s, paired conserved
bulk fields c, and a scalar reservoir e. The observed source u is held fixed
within one propagation interval. Define

    H = T(p,L) + A_sheaf(q,u) + A_cov(L,q) + A_alignment(q,f,s,c)
        + A_traces(f,s) + A_bulk(c,f,s) + A_neural(q;u).

The vector part of p uses the positive inverse metric exp(-sym(L)); the other
Clifford grades retain their Euclidean kinetic term. Covariance discrepancy
penalizes both transported disagreement and deviation from log(I+q_v q_v^T).
The alignment energy couples q_v to the mean of f, s and the decoded bulk. The
bulk free energy uses targets from both traces. The neural term is the exact
finite conditional mixture action with source-conditioned means. Its source
context is fixed during this interval; gradients include every dependence on the
joint dynamical coordinates.

Bulk concentration channels stay in a stored reference frame. Learned orthogonal
anchors map their decoded coordinates into local boundary frames and map trace
targets back. Under a boundary frame change, the anchors transform too. This
keeps a componentwise bulk potential from being incorrectly labeled invariant
under arbitrary mixing of its scalar concentration channels.

Write H_x for each full partial derivative. For positive learned rates, the
implemented equation is

    q_dot = H_p
    p_dot = -H_q - gamma_p H_p
    L_dot = -gamma_L H_L
    f_dot = -gamma_f H_f
    s_dot = -gamma_s H_s
    c_dot = M Lap(H_c) + A(c)

where gamma_s is constrained below gamma_f. The active term is

    A(c)_1 = -alpha Lap(c_2),    A(c)_2 = alpha Lap(c_1).

The reservoir gains the nonnegative passive loss:

    e_dot = gamma_p ||H_p||^2 + gamma_L ||H_L||^2
            + gamma_f ||H_f||^2 + gamma_s ||H_s||^2
            - <H_c, M Lap(H_c)>.

For the periodic symmetric negative-semidefinite Laplacian,

    (H+e)_dot = <H_c,A(c)>,     e_dot >= 0,     sum(c_dot)=0.

The active-work term is recorded; it is not silently treated as passive energy
conservation. Changes of observed source, learned parameters or externally
injected observations require separate port-work accounting between intervals.
This is a finite engineering energy, not a derivation of gravitational duality
or a semantic truth theorem. The earlier
[metriplectic alternatives and derivation](UNIFIED_DYNAMICS_ALTERNATIVES.md)
provide its provenance and scope.

The implementation differentiates H with respect to every coordinate, including
memory. It uses a pure two-stage Heun step, with an explicit numerical energy
defect. Continuous identities do not imply exact discrete conservation. Tests
check step refinement, mass, unchanged inputs, full local-frame transformations,
nonzero mixed boundary/memory derivatives and joint parameter/input gradients.

The finite neural mixture couples represented coordinates globally. This full
energy is therefore not assigned the strictly local dependency bound proved for
a separate fixed-operator finite-hop sheaf filter.

## Fibonacci branch contract

The implementation pins the right-handed chiral Fibonacci data of
[Bseiso et al., section II.1](https://arxiv.org/html/2407.21761v2#S2.SS1).
It enumerates left-associated fusion paths with a declared total charge and
constructs adjacent-charge projectors. Braid matrices combine those projectors
with the two R phases. Opposite handedness conjugates those phases.

An independent binary-tree construction checks the pentagon for all four-leaf
charge assignments and both totals. The represented spaces also check adjacent
braid relations, distant commutation, unitarity and complete orthogonal outcomes.
The configured implementation permits 2 through 10 anyons. State-vector and
density-matrix storage are reported separately; four tau anyons of total tau
have three basis states and a 144-byte complex128 density payload, excluding
operators, learner weights and process overhead.

For each projector P_j, the unnormalized outcome is P_j rho P_j, with probability
given by its trace. A possible read outcome returns the conditional normalized
state. An impossible outcome has no fabricated conditional state. A performed
measurement with unread outcome returns the sum of the unnormalized substates;
no measurement retains rho. These can be different states. Input validation
checks trace, Hermiticity and positivity within the declared numerical tolerance;
it does not normalize an invalid input into apparent consistency.

These are conditional calculation instruments. They do not verify their own
physical predictions or write imagined outcomes into factual memory. Their
connection to learned diverse proposals and independent investigation must be
completed and assessed through the whole owner before a learned capability is
assigned to them.
