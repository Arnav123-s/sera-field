# Connecting reversible dynamics, memory and observations

The newest source asks for a single evolving mechanism. The current owner already
couples its field, covariance and memory during each task, but a composition of
substeps is not automatically the solution of one physical action. This note
records competing constructions and a concrete finite derivation for a future
coupled update. It does not change GENRE-017 or count a cited method as implemented.

## Primary research consulted

[Gruber et al., *Efficiently Parameterized Neural Metriplectic Systems*,
arXiv v3 / ICLR 2025](https://arxiv.org/html/2405.16305v3) learn energy,
entropy and compatible operators, with a representation based on exterior
algebra. Their approximation results have explicit nondegeneracy assumptions.
This is an alternative to assuming that every part of memory is reversible.

[Hernández et al., *Port-metriplectic neural networks*](https://link.springer.com/article/10.1007/s00466-023-02296-w)
addresses interacting/open physical systems. External driving must be represented
in the energy accounting; an externally driven learner should not be described
as an isolated conservative system merely because one internal subflow is Hamiltonian.

[Sulskis and Ravi, *GENERIC-FNO*, version 1](https://arxiv.org/html/2606.08343v1)
uses projected spectral operators to enforce degeneracy identities. Its
continuous-time guarantees must be distinguished from time-discretization error.
Its projection also uses global inner products, so an exact algebraic constraint
does not by itself establish a local information cone. The decomposition of a
learned flow into energy/entropy channels need not be uniquely identifiable.

These papers report their own physical-model experiments. They supply candidates
and mathematical conditions, not evidence that SERA has acquired the corresponding
reasoning or memory behavior.

## A finite construction for the continuing field

The following derivation is engineering for this project. Let q contain the
field coordinates, p their momenta, m memory coordinates, and e a scalar reservoir.
Choose a differentiable coupled energy H(q,p,m), and define

    E(q,p,m,e) = H(q,p,m) + e,       S(q,p,m,e) = e.

Here S is an accounting potential. It is not identified with measured biological
entropy. Let J be the constant canonical q/p matrix with zeros on m/e. Then
J is skew, satisfies the Jacobi identity, and J grad(S)=0. For each dissipative
direction (u_i,v_i) in momentum/memory space, define

    a_i = u_i . grad_p(H) + v_i . grad_m(H),
    b_i = (0, u_i, v_i, -a_i),
    M = sum_i gamma_i b_i b_i^T,     gamma_i >= 0.

Directly b_i.grad(E)=0. Therefore M is positive semidefinite and M.grad(E)=0.
The joint update z_dot=J.grad(E)+M.grad(S) is

    q_dot = grad_p(H)
    p_dot = -grad_q(H) - sum_i gamma_i u_i a_i
    m_dot = -sum_i gamma_i v_i a_i
    e_dot = sum_i gamma_i a_i^2.

Substitution gives E_dot=0 and S_dot>=0 for the continuous equation. Momentum
and memory exchange information through the same H and the selected directions.
If every v_i has zero sum within a conserved memory region, its total mass is
preserved. Timescale-separated gamma values provide a stated fast/slow family.
Learned nonnegative rates can be parameterized without changing these identities.

An example coupling H includes a sheaf discrepancy, kinetic energy, a memory free
energy and an alignment term between the field and transported memory. The
coupling's gradients must be taken with respect to both q and m. Treating memory
as a fixed injected source would instead describe a conditional subflow.

Observed input adds an explicit port f, contributing grad(E).f to the energy
balance. Active nonreciprocal memory and stochastic perturbations need their own
flux/noise accounting. They cannot be inserted into the expression above while
retaining its conservation claim without checking the changed equation.

## Tests and choices before adoption

An implementation would compare this finite construction, the current composed
field, a directly learned update and soft-constraint alternatives on the same
fresh task/evidence budgets. Tests must cover the full derivative, conservation
and dissipation residuals, integration error, observed trajectory accuracy,
partial observation, retained language and useful factual memory. The current
GENRE-017 models remain frozen during that decision.

Two algebraic details need explicit treatment. A general state-dependent skew
operator need not satisfy the Jacobi identity. Also, adding an epsilon to a
projection denominator changes exact degeneracy near a zero gradient. Neither
detail should be hidden by terminology or a tolerance chosen after assessment.

The [attachment transition](CELL_ATTACHMENT_CONTRACT.md) handles growing state
coordinates. If its chart depends on time or learned parameters during an actual
trajectory, the transformed derivative contains a chart-velocity term; the
fixed-chart preservation result alone is insufficient. Every revision must keep
the actual original task and independently qualified evidence available.

Conservation, compatibility and stability are useful structural checks. Correct
interpretation and improved answers remain outcomes measured against independent
observations or supplied proof obligations. A single equation can connect the
computations while those external observations continue to determine what was
learned about the world.
