# Audit against the original proposal

I read the complete source before implementation and reread it after training. The retained source SHA-256 is `b0be4b4aea776bcdfd580e000aebbb1bd7b56523e6b0df32f0c1fdb89fbfc9cd`. The original remains in the private intake directory; the public record contains its identity and the tested mathematical interpretations.

## From-scratch lineage

The new repository, source, environment, supervisor and training runs are independent of the previous SERA repositories. Each of the twelve base models starts at a saved step-zero checkpoint. The delivery audit reconstructs those initial tensors exactly from their declared seeds and newly written constructors. Field and scrambled controls share matched initial tensors within a seed, as do the two classical controls; their subsequent training is separate.

The field's trainable hidden weights are SU(2) connection coordinates from initialization. Radial gains and scalar readouts are also newly initialized; zero initialization is used for gains and correction readouts where specified. No pretrained tensors are loaded. The successors inherit only the new lab's own trained base and add fresh residual weights. Their initializer, optimizer, sampler state, RNG state, learning logs and saved intermediate checkpoints are retained.

The prior reference remains at `0dcbcb902706f3d299cd38a433fcf1f26a357efd`, with owner checkpoint SHA-256 `b29d8cccea6a7b8b9e0f0bbc28432d146a6388bca7716a828c446b3b42036d95`. Preserving that project does not transfer its older language, mathematics or other abilities into the new model.

## Requirement-to-implementation map

| Source idea | Implemented mechanism and evidence | Mathematical scope |
|---|---|---|
| Persistent structure and transient imagination | Learned connection tensors; immutable situations; hash checks around imagination and planning | A finite graph and transient activations; there is no implemented effective action `Gamma_k` |
| Non-Abelian field representation from the start | SU(2) exponentials, Pauli contractions, transported adjoint fields, radial nonlinearities | Actual group-parameterized hidden weights, computed classically |
| One mechanism across several tasks | Identical checkpoint used for forward motion, inverse mass, changed-mass imagination and goal-directed controls | Task algorithms are supplied; no task-specific predictor retraining |
| Different perspectives | Rotation transfer, local-frame transport and Wilson-loop invariance checks | Coordinate invariance is distinct from a physical change in mass |
| Missing mechanism and revision | Context-conditioned residual trained on six measured supports per query; held-out intervention checks | Context statistics and the candidate family are supplied engineering |
| Representation growth | Fixed and expanded residuals, initial function preservation, prospective selection | Controlled capacity comparison, not a Wetterich flow or independent invention of a new variable |
| Retain valid simple knowledge | Base tensors frozen, compatibility statistics calibrated on separate evidence | Protection is explicit ownership and qualification, not topological certainty |
| Independent reward | Goal/version/evidence-bound credit; duplicate, stale, imagined and actuator-fault checks | The credit rule and probe policy are engineered; this study does not train their selection procedure |
| Living language and experiential meaning | Structured situation interface and faithful numerical explanations | A raw human-language encoder and its grounding curriculum are the next capability package |
| Diverse scientific ideas | Distinguishable predictive alternatives and a chosen discriminating intervention | A finite supplied physical question family; autonomous open-domain idea generation requires a separate curriculum and evaluation |

## Deliberate mathematical departures

The literal coupled PDE proposal needs field content, an action truncation, regulator, boundary conditions, a projection and a learning bridge. None is supplied by simply naming the Wetterich equation. This release implements a tractable finite connection network, not a solution of those PDEs. The network evaluates a two-layer field graph; it does not perform recurrent field settling or holographic bulk reconstruction.

An SU(2) change of coordinates rotates the representation of a physical vector. A change in mass changes the physical problem. I keep these separate. Stable topology alone does not verify a proposition or the applicability of a physical model. Independent observations remain the verification mechanism.

Training uses ordinary gradient differentiation and Adam. Curvature is not substituted for an eligibility derivative. A future local learning rule must be derived and compared to the derivative it approximates. The reward ledger in this release records independently checked improvement; its points are not themselves extra gradient updates.

The symmetry-broken control changes the contractions used as physical inputs. It is a symmetry ablation, not a topological-memory ablation. All four base architectures have 783 trainable scalars and matched examples and updates. Their compute costs differ. The older Stage 47 model is a preserved reference, not a participant in this from-scratch comparison.

The proposal's 35,840-byte retained-state target is not used as a claim about total process memory. Base parameter tensors occupy 3,132 bytes; selected qualified successors occupy 6,748 or 9,308 persistent tensor bytes. JSON evidence, optimizer state, graph temporaries and process-tree memory are separate costs. No exact 35,840-byte working-state match or per-operation peak allocation claim was tested.

## Protocol discrepancies and engineering repairs

1. **Final context cohort count.** One sentence in the frozen protocol says 1,024 new-context and 1,024 vacuum cases per refinement. Its earlier specification and the frozen implementation instead generate **1,024 mixed-context episodes**, which yielded 664 new and 360 vacuum queries, plus base retention on the 2,048 rotated cases. I report those actual counts. I do not rewrite the frozen protocol, manufacture extra final cases, or treat them as 2,048 mixed-context queries.
2. **Order of acquisition and investigation.** The frozen protocol describes selecting interventions before fitting the correction. The implemented study first trains the correction on a supplied curriculum, then chooses a fresh intervention and independently checks the acquired model. This demonstrates acquired-model reuse and checked revision, not a learned policy collecting its own training curriculum.
3. **Rotation sampling.** Code inspection found that the original QR sampler produced proper rotations without Haar-uniform sampling. A prospective addendum corrected unopened final sampling and preserved all original training/development identities.
4. **Retention qualification.** Raw residuals harmed familiar-context accuracy. The energy-only qualification failed two development candidates. A distinct covariance-based mechanism was frozen and assessed on fresh calibration and development evidence before finals. Both failed energy qualifications and raw regressions remain in the record.
5. **Replay serialization.** The first fresh-process replay reproduced the same serialized values, but its in-memory comparison rejected tuples that became lists in JSON. The correction compares canonical JSON values without numerical tolerance. Both the failed attempt and the repaired replay are retained; no model or selection changed.
6. **Command interface.** Post-final review found that the CLI did not pass an explicitly requested planning horizon through to the planner. The interface now honors even horizons and rejects unsupported odd ones, with finite vector validation. The final study used the existing twenty-step default and is unaffected.

## Decisions supported by this study

The learned field does reuse one acquired mechanism across physical tasks. Measured context helps it apply a learned correction while protecting familiar predictions. The strong invariant classical network and fitted power-law control remain essential reference methods: the held-out evidence favors those controls on the supplied vacuum family. Group structure is therefore a tested implementation choice, not a demonstrated general cognitive advantage.

I retain the successful cross-use and evidence contracts. The next comparison should ask whether learned situations and investigation improve acquisition on a new capability family, using both field and invariant classical cores. New experiments must have fresh prospective cohorts; opened FIELD-001 finals remain an immutable result.
