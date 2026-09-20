# Finite mathematical contract

## Situation and persistent model

A situation contains position `x`, velocity `v`, applied force `f`, positive mass `m`, evidence provenance and the original goal. Explicit step count and `dt` supply the rollout's time coordinate. A learned model estimates `a_theta(v,f,m)`. A fixed numerical integrator gives conditional trajectories; optimization of controls through that same function gives plans. No task-specific inverse or planning network is trained.

For a real vector `r`, write the traceless Hermitian matrix `X(r)=sum_a r_a sigma_a`. Then `tr(X(r) X(s))/2 = r dot s`. Conjugation by SU(2) rotates its adjoint vector. Independent local frames are related by links; transport to the reference frame precedes invariant feature construction. The finite covariant architecture uses scalar functions of invariant contractions multiplying `f`, `v` and `f cross v`. These vectors span generic equivariant vector outputs; their presence is a supplied geometric bias, while coefficient functions are learned from observations.

`a_theta = c_1(q) f + c_2(q) v + c_3(q) (f cross v)`, where `q` contains eight fixed scalar features built from `log(m)`, norms and dot products. No `1/m` or drag coefficient is supplied to the learned model. A classical dot-product implementation is algebraically equivalent to the Pauli trace implementation. I test that equivalence rather than claim a quantum advantage from it.

The persistent hidden weights are SU(2) links: `U_ij = exp(i theta_ij dot sigma)`, with each `theta_ij` randomly initialized in this lab. Boundary activations are adjoint fields, transported by these learned links and summed at each node. The radial activation `H -> H tanh(exp(g)||H||)/||H||` is covariant. Invariant field norms feed learned scalar readouts for the three physical coefficients. There is no pretrained or ordinary dense hidden backbone in the field candidate. These links, radial gains and readouts are active from the first update.

The graph has 8 input fields, 12 intermediate fields and 12 output fields. Its 783 trainable scalars comprise 288 first-layer link coordinates, 432 second-layer coordinates, 24 radial gains and 39 scalar readout weights/biases. Wilson loops around graph cycles and local adjoint transport have separate gauge-invariance tests. A depth-two graph is a finite boundary/persistent-link interpretation, not an asserted AdS/CFT correspondence or a solved Wetterich PDE.

The symmetry-broken control changes the scalar contractions to fixed anisotropic quadratic forms and otherwise keeps the same gauge-weight architecture. The dense control uses 8-20-25-3 layers, also exactly 783 parameters, and raw vector components, with a scalar mass and an informative norm feature. Every trained weight participates in its computation. Initial models have matched examples, updates, loss, optimizer and seeds; architectural information differs and is reported. Equal update counts do not imply equal compute; measured cost is reported separately.

## Learning from trajectories

Acceleration targets are computed from observed central position differences; velocities are computed from the central first difference. Applied force and calibrated mass are recorded as known experimental inputs. Training sees no analytic equation or teacher coefficient. The simulator and observation conversion are supplied engineering and explicitly synthetic diagnostic evidence. They are not human text or real laboratory measurements.

Training minimizes error in physical consequences. Prediction remains necessary for testable imagination; next-token prediction is not this model's learning objective. Language output in this work package renders qualified numerical results through a documented interface.

## Refinement and adequacy

A new environment first supplies observations only. Persistent residuals trigger comparison of fixed-width and expanded residual field graphs. Both learn from three invariant summary statistics of six measured support residuals; these context channels are supplied engineering and contain no hidden medium label. Expansion appends trainable group-link channels with zero outgoing weights, preserving the pre-update function exactly. The base graph is frozen in the successor and a new residual field is trained with old-context rehearsal. An unobserved context retains the earlier predictor and ambiguity about the new environment. Weight freezing is an explicit retention intervention, not a claimed topological guarantee.

Disagreement is a reason to investigate, not a calibrated guarantee of adequacy. Intervention outcomes are independently simulated with a distinct numerical solver. Evidence records intended and actual control. Candidate selection and refinement see development data only. Final cohorts are opened once after the selection manifest is fixed.

## Qualification and credit

Credit is a checked reduction of error on independent evidence, scoped to the original goal, decision, source identity, predictor versions and evaluation contract. Reusing an evidence identifier, an imaginary outcome or a stale predictor yields no additional credit. Diverse methods earn separate credit only for distinct verified contributions, not different names. The reward ledger does not grant correctness or system permissions.

## Scope of the field analogy

This finite model implements gauge-covariant physical representations and dual-timescale state ownership. It does not numerically solve the proposal's coupled PDEs: a regulator, action truncation, bridge and projection must first be derived and tested. Exact mathematical routes in existing SERA are preserved independently. FIELD-001 establishes what the finite mechanism learns before further structure is added.
