# Connected situation and credit core

This addition gives the next experiment an executable starting point for word and
numerical observations, field evolution, candidate choice and delayed reward. All
parameters begin with fresh random initialization. FIELD-001 remains a preserved
trained physical reference; its opened finals are not training or selection data.

## Finite mathematical contract

Let h_i and J_i be three-component adjoint fields on a ring, U_i in SU(2) the
learned link from i+1 to i, and R_i its real adjoint rotation. The implemented
working-state action is

    E(h; J, U) = 1/2 sum_i ||h_i - R_i h_(i+1)||^2
                + kappa/2 sum_i ||h_i||^2 - sum_i J_i dot h_i.

The update is h' = h - dt dE/dh, with

    dE/dh_i = (2+kappa)h_i - R_i h_(i+1) - R_(i-1)^T h_(i-1) - J_i.

The code constrains kappa to [0.1,1] and dt to (0,0.2]. The Hessian's largest
eigenvalue is at most 4+kappa <= 5, giving a conservative descent step. This is a
finite, dissipative lattice action. It does not instantiate the paper's claim of
non-dissipative evolution. Its derivative and energy reduction are tested directly.

The closed-loop feature is 1/2 Re Tr product_i [exp(i J_i.sigma) U_i]. Under a local
frame change g_i, J_i becomes Ad(g_i)J_i and U_i becomes g_i U_i g_(i+1)^dagger.
The product is conjugated at its starting point and its trace is invariant. This
feature is in the actual forward/gradient path, unlike the earlier standalone
Wilson-loop utility. It is a finite holonomy feature, not a Chern number or proof.

Byte embeddings, a local convolution, masked numerical inputs and a learned
projection supply J. These are learned from scratch but their layout is supplied
engineering. A word's meaning, physical rotation and changes of latent gauge frame
must not be equated. Semantic transfer must be taught and tested independently.
There is no token-prediction output head. The input view defaults to 256 bytes; a
long-book adapter must stream views with explicit memory, offsets and coverage.

All prediction and candidate-choice heads consume the same field features. The
single parameter owner is an implementation fact, not evidence of positive transfer.
Prediction/candidate dimensions are interfaces. A candidate descriptor or teacher
label supplied by engineering is not a concept autonomously discovered by SERA.

## Verified credit and actual updates

Before an outcome is available, record a decision, its original goal, predictor,
assumptions, policy hash, choice probabilities and score-function eligibility

    e_theta = d log pi_theta(chosen action | situation) / d theta.

After independent assessment, use r = clip(progress + novelty bonus, -1, 1), where
progress = (before_loss - after_loss)/(1+before_loss). A bonus of 0.1*positive
progress applies only to a new verifier-canonical contribution under its assumption
scope, across the learner's goals. Renaming the goal does not renew novelty. Update
theta by SGD ascent on r*e_theta, clipping gradient norm
to one. A regression yields a negative learning signal. A zero-progress result
receives no novelty credit. Raw candidate count and confidence are not rewarded.

This is a delayed single-decision score-function estimator. It is not an e-prop
implementation, a general long-horizon credit solution or a topological phase
transition. The next campaign must research and derive those extensions, test
their gradients/estimators and report approximations explicitly.

The bridge rejects self-imagined outcomes, unknown source/verifier identities,
unperformed interventions, changed policies, mismatched goals/predictors/scopes,
invalid assessments and reused evidence. An assessment cannot be reused under a
different evidence alias. Registered verifiers still require semantic independence:
the allowlist establishes identity and does not make an incorrect checker correct.

Weights, optimizer, pending traces, consumed credit, NumPy/Python/PyTorch RNG and
the caller's data cursor are saved together in immutable hashed revisions. An
atomic CURRENT pointer and compare-before-commit reject concurrent overwrites.
Only this experiment's trusted local checkpoints may be loaded. Committed event
history remains in the revision chain. The training adapter must include its own
sampler generator, curriculum schedule and complete exposure cursor in progress.

## Evidence and next engineering

The repository tests cover the action derivative, closed-loop invariance, live
word/link gradients, branch separation, actual reward-induced parameter changes,
invalid and stale credit, alias rejection, and identical updates after resume.
These tests establish executable contracts, not broad trained understanding.

The long campaign still needs subject adapters/verifiers, learned candidate
construction, durable goal/situation memory, source-grounded explanations, bounded
program execution and independent full-loop behavioral evaluation. It must also
investigate the remaining mathematical components in PAPER_COVERAGE.md. They must
not disappear from the checklist merely because the connected core trains.

Primary research used to distinguish these contracts:

- [Lattice gauge equivariant convolutional networks](https://arxiv.org/abs/2012.12901): gauge-covariant layers and loop features.
- [Eligibility propagation](https://arxiv.org/abs/1901.09049): local traces plus learning signals; not an identity between curvature and a learning derivative.
- [Exact evolution equation for the effective potential](https://arxiv.org/abs/1710.05815): a specified effective-action flow; a representation-growth operator remains a separate derivation.
