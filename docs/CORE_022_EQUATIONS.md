# A coupled energy and explicit conditional fusion space

This is the engineering construction for the complete-core work order. It is
implemented in `unified_energy.py` and `fibonacci_space.py`, and connected through
`core_owner.py`. Their independent contracts and actual learning paths are checked.
Existing trained
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
memory. The full-vector-field Heun routine remains a diagnostic reference. The
owner uses a symmetric split: a canonical half interval, a two-stage Heun interval
for irreversible coordinates, then a canonical half interval. Every part uses
the same H. The reported numerical energy defect covers the entire split.
Continuous identities do not imply exact discrete conservation. Tests
check step refinement, mass, unchanged inputs, full local-frame transformations,
nonzero mixed boundary/memory derivatives and joint parameter/input gradients.

The finite neural mixture couples represented coordinates globally. This full
energy is therefore not assigned the strictly local dependency bound proved for
a separate fixed-operator finite-hop sheaf filter.

### Canonical credit through the actual coupled energy

During each reversible interval, hold L, f, s, c and the observed source fixed.
Then H=T(p,L)+V(q;L,f,s,c,u,theta) is separable in the canonical q,p pair. A
symmetric kick/drift/kick map is inverted with the negative step. Fixed arguments
theta (including the current slow coordinates) accumulate auxiliary momenta
through minus the appropriate partial derivatives of V and T. The T derivative
with respect to L is included; a Euclidean momentum drift would be incorrect.

For terminal derivatives g_q and g_p, apply two opposite impulses

    q_final -> q_final +/- epsilon g_p
    p_final -> p_final -/+ epsilon g_q

and integrate backward. The difference of the recovered p, q and auxiliary
momenta gives the corresponding input and parameter derivatives. Epsilon is
1e-4 and the echo is evaluated in float64. Tests compare every coupled argument
against differentiation of the identical discrete map, including a timed source
change and an intermediate loss. The method uses two reverse passes; it does not
claim zero computation or exactness for arbitrary impulse magnitude. Encoder,
stationary, irreversible and output operations retain their own local chain rules.

Current coordinates can share computation history. Independent clone nodes are
therefore necessary when taking a partial of H: hold the other current arguments
fixed inside that partial, while retaining the outer learning derivative through
the preceding history. The preserved first integration failure and its repair
are recorded in [the repair log](../reports/CORE-022/REPAIRS.md).

### Literal finite attachment in the common state

One admitted refinement can add a stalk of dimension 1+k at an existing boundary
vertex, with k in 1..16. Intrinsic coordinates are the old q, free eta and edge
disagreement w. The existing full-rank chart reconstructs the new stalk as

    y = (B q_vertex - A eta + w, eta),  R_new = [I,A].

B selects the scalar Clifford blade and A is a supplied constant chart. The
resulting enlarged sheaf has an additional edge whose coboundary is w. The common
energy adds .05*(||eta-W phi(q,f,s,u)||^2+||w||^2), with eight declared invariant
features phi and a newly initialized W. Eta and w have dissipative derivatives
and contribute their passive loss to the same reservoir. Their old/new cross
derivatives are included in canonical credit. An actual input port writes eta;
the same conditional decoder reads it. No different response model is fitted.

W and the new decoder start at zero, preserving old predictions at attachment.
The new port initializes free coordinates from retained observations. New
dissipation legitimately increases the accounted reservoir; preserving an old
answer does not require hiding that cost. Subsequent learning can use the new
coordinates and couple them back into the boundary. Tests verify old-section
preservation, added dimensions, gradients, optimizer migration and exact resume.
The geometry/rank bounds are supplied. Useful learned growth is a subsequent
behavioral assessment, and structural change alone earns no reward.

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

In the current owner, a learned mixture of pinned braid words encodes retained
history and a query. Absent, unread and read instruments are followed by another
learned channel. This makes their differing consequences operational. Every
outcome is preserved and its conditional field branch evolves using the same
energy. Tests verify that averaging the read continuations reproduces the unread
channel, that absent and unread continuations differ, and that neither modifies
the actual observed state. Independent outcome assessment still supplies credit;
an internal conditional calculation does not verify its own physical prediction.

The [owner integration note](CORE_022_OWNER.md) describes persistent investigation,
protected retained coordinates and the local scale-dependent adequacy interface.
