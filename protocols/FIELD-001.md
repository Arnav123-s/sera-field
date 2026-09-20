# FIELD-001 — shared physical understanding and refinement

Status: prospective protocol; freeze manifest required before numerical training.

## Cohorts and prospective decisions

Training, development and final episodes use disjoint deterministic seeds. Final datasets are not constructed or evaluated until the selected configurations and checkpoint hashes are written to the selection manifest. A opened-final marker prevents repeated selection against finals. A fresh-process replay may reproduce the fixed results without changing any model or selection.

Base models: covariant field, symmetry-broken field, and dense classical MLP, three initialization seeds each. The equivalent classical invariant formula is checked against the Pauli implementation, not redundantly counted as another independent model. Identical parameter counts, batch sizes and update counts are required for the three base candidates.

Base training: 8,192 synthetic observation episodes, 3,000 minibatch updates per model, batch 128, Adam 0.002 with fixed decay to 0.0002. Development: 1,024 fresh in-distribution episodes and 1,024 rotated episodes. Initialization seeds 11, 29 and 47. Initial data seed 19092026; development seed 29092026; sealed final seed 39092026. The numerical run writes exact data hashes and RNG state.

Training force directions lie predominantly in the xy plane. New Haar rotations test full 3D frame transfer. Mass is calibrated over [0.8,4.0]. Final interpolation and mass-range extension are reported separately. No final-based retraining or hyperparameter selection is permitted.

Primary metrics: acceleration normalized MSE and rollout position/velocity error, each by distribution and seed. Secondary cross-use metrics: inverse mass relative error, mass-halving counterfactual error, and independent endpoint error for goal-directed plans. Planning uses 120 optimizer iterations through the same learned predictor and a 20-step horizon; force bounds and feasibility are recorded. A supplied exact physical oracle provides a reference, not a trained competitor.

## Correction phase

A held-back development environment adds nonlinear velocity-dependent resistance. The learner receives trajectories and measured interventions, not the simulator formula. It first records baseline error, selects discriminating interventions, and compares no update, 3,000 steps of fixed-width residual adaptation, and 3,000 steps of an expanded residual successor. Both successors have the same three context statistics computed from six observed support residuals and receive the same new observations and vacuum rehearsal. A residual is necessary because identical instantaneous states can have different consequences in different media. Context is never a supplied environment label. Expansion adds 16 channels to the second hidden layer using zero outgoing weights; pre-update equivalence is checked. The initial base is frozen in both successors. Report total and trainable parameter costs separately; the successors have larger total capacity than the initial base.

Qualification uses a separate 512-episode development set: at least 50% error reduction on the new environment, finite predictions and a recorded old-context error. The smaller valid predictor wins unless expansion improves new-environment development error by at least 20%. Initial base weights are preserved byte for byte. Context selection uses measured residuals, never an environment identifier supplied at inference. Unsupported candidates and all costs are retained.

Refinement training uses 8,192 episodes with six support observations and one query each; 35% have vacuum dynamics and the others have a hidden resistance sampled over [0.1,0.65]. The source generator keeps resistance values only for audits. The learner receives measured positions, inferred velocities/accelerations, calibrated masses and actual forces. Training code explicitly whitelists these fields. Training seed 49092026, development seed 59092026, final seed 69092026. This is a supplied family of environments and an engineered three-dimensional context encoding, not a claim that the model invented its input channels.

The field candidate uses explicit complex Pauli matrices, trace contractions and learned SU(2) connection weights from its very first training update. The two hidden graphs contain 12 fields each. Field and symmetry-broken controls each have 783 trainable scalars; the 8-20-25-3 dense control also has 783. All hidden layers start randomly; no token-model pretraining, reference-SERA weights, or later attachment of a geometric label is used. The fixed residual has 12 output fields and the expanded residual has 28; both have a 12-field first layer and retain the same frozen base. This finite interpretation tests the source's gauge/state-learning ideas; the source audit records the additional definitions needed for its literal coupled PDE proposal.

Scope of expansion comparison: it compares widths in the common residual field, not a mathematical theorem that the environment requires a new dimension. The development selection score averages new and vacuum contexts. The 50% qualification threshold is applied on new-context episodes, separately from vacuum retention. Final planning success uses both endpoint distance below 0.05 units and speed below 0.05 units/s. All counts, failures and errors are reported. Extrapolation to half-masses below the training range is explicitly counted.

Finals: 2,048 interpolation, 2,048 rotated, 1,024 mass-extension cases per base model; 128 rollout/inverse/counterfactual cases; 24 independently evaluated plans per base seed; 1,024 new-environment cases and 1,024 retained vacuum cases per refinement. Common case identities across mechanisms. Report each seed and aggregate mean/range, no invented statistical significance.

## Integrity gates

Test independent local gauge frames and physical mass interventions separately; hash weights and factual situations before and after imagination; exercise ambiguous inverse cases; test finite input/domain guards; verify expansion preserves initial outputs; reject stale, duplicated and imagined credit; validate split identities; save optimizer, RNG and exact cursor; compare reload predictions.

All numerical work uses the shared lease, one CPU numerical thread and a verified 2 GiB Windows Job Object cap. No paid services. Attempt directories are append-only. Failed attempts and fixes stay in the evidence log. No changes to existing SERA weights, pointers or experiment outputs.
