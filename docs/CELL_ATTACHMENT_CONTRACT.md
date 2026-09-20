# Representation attachment that preserves earlier sections

The latest synthesis requires an actual representation change followed by a
return to the original investigation. This is a prospective mathematical contract,
not an implemented or qualified growth capability. It extends the existing
bounded residual-feature result without renaming it a topological construction.

Let D be the existing degree-zero sheaf coboundary. Its compatible sections satisfy
D x=0. Attach d new stalk coordinates z using r independent restrictions, r<d:

    D_new = [ D    0 ]
            [-B    R ],        rank(R)=r.

Here B maps the earlier coordinates into the new edge's restriction space and
R maps the new stalk into the same space. Write R+ for the Moore-Penrose inverse.
Because R has full row rank, R R+=I_r. An embedding of the old sections is

    E x = (x, R+ B x).

Then D_new E x=(D x,0), so every earlier compatible section remains compatible.
The new free directions are (0,z0) with R z0=0. Thus the compatible-section space
has exactly d-r additional dimensions: solutions are uniquely parameterized by
an old section x and z0 in ker(R). This distinguishes a genuine new degree of
freedom from attaching an entirely constrained copy of an old coordinate.

This elementary attachment is not called Schubert cell splitting without an
explicit Grassmannian/flag construction. The paper's terminology does not specify
the missing attachment maps or a learner that chooses them.

## What preservation proves

The projection P(x,z)=x satisfies P E=I. An old readout extended by P returns the
same answer at initialization. Earlier sections and readouts can therefore be
embedded exactly while a residual-driven learner explores new coordinates.

This alone does not preserve later dynamics. In general D_new^T D_new E differs
from E D^T D. It also does not guarantee unchanged old probabilities after arbitrary
training. A qualified implementation needs explicit old-state recovery, the
actual transition operator, applicability and regression checks after learning.
Those are behavioral tests in addition to the attachment identity.

## Required investigation cycle

1. Detect inadequate predictions on observations separate from parameter fitting.
   Record uncertainty and adequacy separately. A large cumulant or residual does
   not uniquely identify a new physical mechanism.
2. Propose B, R and a small new stalk, initialize the embedding and preserve the
   original goal and source state. The supplied topology vocabulary is engineering;
   a learned selection among it is recorded separately.
3. Fit the proposed coordinates using only available practice observations.
   Generate several consequences and interventions through that same model.
4. Observe the performed intervention and independently compare its outcome with
   the original model, the refined model and alternative explanations.
5. Retain the refinement only within its tested scope, then return the original
   answer. Rejected attachments, failed probes and compute costs remain resumable.
6. Check the simpler regime and all existing uses again. Preserve an old valid
   explanation when the new mechanism applies only under additional conditions.

## Finite tests before use

Check rank, section embedding, new null directions, the old readout and exact
restart; compare autodifferentiation with explicit gradients for learned B/R;
test poorly conditioned restrictions and bound storage/solver costs. Keep final
outcomes outside attachment selection and fitting. Match evidence budgets with
the current R1/field owner, its retained exact methods and simpler investigation
policies. A topology-scrambled control is an observed comparison, not an experiment
required to fail by construction.

The next implementation must support a general edge/stalk description rather than
silently applying a fixed-ring `roll` operation after the topology changes. It must
also define how the source encoder, covariance transport, memory codec and readout
embed or address the new coordinates. That is what makes the attachment part of
one continuing architecture instead of a detached graph demonstration.

## A compatible transition, rather than only a compatible initialization

The preservation problem above has a constructive finite solution before a new
learned coupling is enabled. Let N have orthonormal columns spanning ker(R).
Use intrinsic coordinates (x, eta, w), where eta has d-r coordinates and w has r:

    T(x, eta, w) = (x, R+ B x + N eta + R+ w).

T is square and invertible. Its inverse recovers x from the old vertices,
eta=N^T z and w=R z-B x. Direct multiplication gives

    D_new T(x, eta, w) = (D x, w).

Thus the enlarged consistency energy is exactly the old consistency energy
plus ||w||^2/2. The new eta coordinates are genuinely independent compatible
directions; w measures the new restriction disagreement. With the positive
metric G=(T^-1)^T T^-1, gradient flow of this energy satisfies

    u_dot = -G^-1 D_new^T D_new u,
    (x_dot, eta_dot, w_dot) = (-D^T D x, 0, -w).

Consequently u(0)=E x(0) implies u(t)=E x(t) for this stated flow. This repairs
the earlier non-commutation problem by specifying the metric and transition,
rather than assuming the ordinary Euclidean Laplacian preserves it. Locality,
conditioning and computation costs depend on B/R and must still be measured.
Near rank loss, the inverse can become expensive or unstable; qualification must
bound singular values instead of silently introducing a large inverse.

Learning a coupling among x, eta and observations can then make the new directions
useful. That new coupling changes the flow and requires fresh retention tests;
the initial preservation identity is not asserted after unrestricted training.
This derivation is prospective engineering, not a trained SERA result.

## Local propagation alternative and its precise scope

[Neural Sheaf Diffusion](https://arxiv.org/abs/2202.04579) supplies a learned-map
construction. [Polynomial Neural Sheaf Diffusion, version 1](https://arxiv.org/html/2512.00242v1)
studies polynomial propagation and finite-hop dependence. These are alternatives
to test against the existing field, not capabilities imported by citing them.

For a fixed block-sparse positive sheaf Laplacian L and a verified bound rho on
its largest eigenvalue, set A=I-2L/rho. A convex combination of Chebyshev
polynomials, q(A)=sum_j a_j T_j(A), a_j>=0, sum_j a_j=1, has operator norm at most
one. Since every T_j(1)=1, q preserves ker(L) exactly. If the largest degree is
K, the operator has no block beyond K graph hops. The sign choice in A matters
for preserving the zero-eigenvalue sections.

These identities are for the stated operator. Globally conditioned restrictions,
pooled feature coefficients, dense inverses or an input encoder that broadcasts
to every vertex can create additional dependencies. In particular GENRE-017's
conditional mixture pools context and is not a strict local propagation model.
The next tests must distinguish an operator's finite dependency cone from the
complete learner's input/output dependencies and from a physical relativistic
light cone. A bounded graph filter by itself does not implement causal discovery.
