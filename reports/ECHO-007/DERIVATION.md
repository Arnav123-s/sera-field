# Full-coordinate reversible credit

The experiment reuses the finite action already implemented in
`sera_field/clifford_sheaf.py`. Let edge discrepancy be
`d_i = q_(i+1) - R_i q_i`, prior `b`, source `J`, stiffness `k`, and
quartic strength `s`. The action is

`A = 0.5 sum ||d_i||^2 + 0.5 k sum ||q_i-b_i||^2`
`    + 0.25 s sum (||q_i||^2-0.25)^2 - sum J_i.q_i`.

Use `H = 0.5 sum ||p_i||^2 + A`. The fixed coordinates have no kinetic term;
they are constant during each pass and acquire conjugate momentum. Their local
forces, in the order source/restriction/prior/stiffness/strength, are

`J: q`, `R_i: d_i q_i^T`, `b: k(q-b)`,
`k: -0.5 sum ||q-b||^2`, `s: -0.25 sum (||q||^2-0.25)^2`.

Velocity Verlet advances all momenta symmetrically. Given terminal derivative
`g = d loss / d q_T`, apply terminal momentum impulses `-epsilon*g` and
`+epsilon*g`, reverse every canonical momentum, evolve, then reverse again.
Denote the two returned initial states by plus/minus. Fixed-coordinate gradients
are `(r_minus-r_plus)/(2 epsilon)`. Initial position credit is
`(p_minus-p_plus)/(2 epsilon)`, and initial momentum credit is
`(q_plus-q_minus)/(2 epsilon)`. Shared-coordinate contributions sum over the batch.
Source credit remains per example. The prior receives both the fixed-coordinate
credit and the initial-position credit because `q_0=b`.

These formulas are an independently checked finite construction, not reconstructed
missing equations attributed to the supplied THDFT text. The restriction gradient
passes through the local rotor Jacobian; it does not permit arbitrary SO(8)
mixing. Typed source lifting also receives its ordinary local chain rule.

The backward operator saves the initial coordinates and final canonical state,
not a list of trajectory activations. Its saved tensor size is independent of
the number of integration steps, which a test checks directly. Encoders/readouts
still use ordinary differentiation. Canonical state, parameter credit, working
arrays and process memory must all be counted; the tiny original field-state
figure is not the total echo cost. The method costs one forward and two echo
trajectories for each credited field call. Float64 internal arithmetic and
float32 owner interfaces are explicit.

Qualification checks all seven input/parameter groups against exact autograd
and directional finite differences, full canonical reversal, source immutability,
the tied prior's two paths, actual reading-model gradients, a detached control,
and exact next-update replay in a fresh interpreter. Parameter decay/optimization
occurs after reversible processing. No dissipative step is hidden inside the echo.
