# Executable coupled-state equations

These specify the finite construction used by UNIFIED-012 and GROW-013. They are
engineering definitions and derivations, with source relationships listed in
[the primary-source audit](COUPLED_FIELD_SOURCES.md).

For a boundary source `x_i`, let `S_i=log(I+x_i x_i^T)`. The edge discrepancy is
`D_i=S_(i+1)-R_i S_i R_i^T`. Its adjoint is computed in the Frobenius log-group
metric. Four covariance steps apply
`S <- S - 0.08 (delta*delta S + lambda(S-S_observed))`. The same rotations lift
to Clifford restriction maps. `exp(S)x` modifies the boundary injection, with a
learned bounded gain. Orthogonal frame changes commute with this construction.

Each resulting source frame drives eight reversible Verlet steps of the retained
Clifford/sheaf action. Timed echo applies loss impulses at their actual frame
boundaries and reverses the input sequence. Source-coordinate credit is recovered
per frame; geometric/prior credit is accumulated across frames. All seven
coordinate derivative families are checked against ordinary autograd over the
same discrete flow. Returned output sequences and replayed external inputs are
counted separately from the trajectory differentiation tape.

Bulk density `c_(d,i,j)` lies in `(0,1)`, with four depth positions, a periodic
boundary-node ring and three components. For fixed verified pinning field `t`,
the discrete energy is

`F = sum [c log(c)+(1-c)log(1-c)+2.2 c(1-c)
          + 0.08/2 sum_axes (neighbor(c)-c)^2 + 8/2 (c-t)^2]`.

Conserved relaxation applies `c <- c + dt Laplacian(dF/dc)`, backtracking until
the density stays in its domain and energy does not increase. The discrete
Laplacian has zero column sum, so total concentration is preserved during
relaxation. Capture initializes a new scoped slot from external qualified evidence;
it is a reservoir/write event, not a claimed mass-conserving creation of knowledge.
Retrieval decodes the relaxed density and modifies the same boundary source.

The density pinning field has an 8-bit bounded codec. Each bit is represented by
the phase of `H(k) = sin(kx) sigma_x + sin(ky) sigma_y
                    + (m+cos(kx)+cos(ky)) sigma_z`, with `m=+1` or `-1`.
The fast decoder uses the exact phase intervals of this family. A separate
periodic overlap-link calculation checks integer charge and spectral gap. The
codec has explicit quantization error and addresses; it does not remove the need
for independent correctness checks, source records or correction history.

The stationary FHN member in GROW-013 uses

`u_dot = -L u - a u - |u|^2 u - v + I`,
`v_dot = epsilon (u-b v)`, with `a,b>0`.

At a stationary point `v=u/b`. The reduced equation is
`(L+(a+1/b)I)u + |u|^2 u = I`. Its energy is strictly convex: the Hessian is the
positive sheaf Laplacian plus `(a+1/b)I` and local blocks
`|u|^2 I + 2 u u^T`. A checked Newton solve yields the stationary state. Its
implicit adjoint solves this symmetric Hessian once; local residual derivatives
provide parameter credit. This is an explicitly stable member, not the paper's
entire pattern-forming regime, and not a temporal reversal of dissipative dynamics.

For learned residual features `Phi`, adaptation data form the old basis `X`.
`B=(X^T X+1e-4 I)^-1 X^T Phi` removes the old fitted span. The new coordinates
are `Z=Phi-XB`; their coefficients solve a regularized observed residual problem.
The context-dependent `Phi` weights are trained using query supervision during
meta-learning. Acquisition later uses measured rows and separate calibration.
The finite Gaussian coefficient action has Hessian `H=Z^T Z+P`. With regulator
`R_k=k^2 I`, its scale derivative is `k Tr((H+k^2 I)^-1)` and its integrated
Gaussian normalization is a log-determinant difference. Independent calibration,
not the trace alone, decides whether the candidate extension qualifies.

These equations expose what is actually coupled and what is learned. They make
the implementation reproducible without rebranding arbitrary prediction errors
as cohomology, curvature, proof or renormalization.
