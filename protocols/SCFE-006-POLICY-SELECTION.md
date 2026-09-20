# SCFE-006: development-qualified policy retention

Prospective follow-up after the completed CONNECTED/SCFE final experiment. The
SCFE policy at the final training step increased final post-investigation MSE
relative to the unchanged policy (0.100924 versus 0.075173). This result is retained
and is not re-scored or used to modify those frozen checkpoints.

The repair hypothesis is that selecting the final stochastic policy update did
not qualify its generalization. Use every distinct already-saved reward-policy
checkpoint at attempted episodes 0,128,...,2048. Do not restart teaching/rewards,
add new policy updates, change the predictor or select using the old final cases.

Before new development evaluation, freeze all candidate file/weight identities,
source files, this protocol and the chosen cohort keys. The development cohort
has 512 independent systems, seed73113, split `SCFE-006-development-v1`. Choose
minimum mean post-probe goal MSE, including actual actuation outcomes; break ties
by earliest attempted training episode and then weight identity. The unchanged
initial policy is eligible. Record all candidates and every incurred probe.

Then freeze the selection before opening 512 fresh systems with split
`SCFE-006-final-v1`. Compare the selected, unchanged and final-step learned
policies, plus the same analytic and random controls. All candidates see the same
initial observations, original goals and one chosen probe per case. Check
actuation; retain all returned answers, alternatives and errors. Shared predictor
parameters must match the selected SCFE teacher exactly.

Promotion requires a genuinely changed selected policy, at least a 5% reduction
in final mean post-probe MSE relative to the unchanged policy, and a positive
lower endpoint of a paired 95% percentile bootstrap for mean error reduction
(2000 resamples; independent evaluation RNG seed6006). This is a finite empirical
qualification rule, not a guarantee for new physical mechanisms. A failed gate
retains the useful taught predictor and records the policy candidate as research.

Replay all final records in a fresh interpreter with the identical fixed selection.
No final-based repair/reselection on this cohort. Save exact costs and resumable
per-candidate/per-control records. This repair is engineering of policy selection;
SERA's learned content remains the saved reward-updated decision weights.
