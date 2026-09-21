# JOINT-021: counterbalanced whole-cycle learning

I repaired the chronology/family confound found in JOINT-020 and completed a fresh
matched course. The human text, physical teaching worlds, training actions,
native initialization, architecture, optimizer and number of updates stayed fixed.
Only their teaching chronology changed. Final human groups and simulation
namespaces are fresh. The assessed candidate is preserved; the table records the remaining qualification work. Earlier qualified owners remain available.

Across the 747 original-goal final cases, the complete credited course reduced
returned numerical squared error by **53.96%** versus
its starting owner. The credited-versus-withheld interval includes zero, so the
reward-specific improvement remains an open qualification. The full course's
learning, the effect of obtaining observations and the reward contribution are
reported separately below.

## The repair

The earlier schedule put every quadratic-drag world in text-first order and
every linear-drag world in measurements-first order. I preserved that complete
study and its cost. This course uses an independent ordering bit, so each four
episodes include both families in both input orders. The exact teaching receipts
confirm the following counts per arm:

| Physical family and input order | Presentations |
|---|---:|
| linear / measurements first | 4,096 |
| linear / text first | 4,096 |
| quadratic / measurements first | 4,096 |
| quadratic / text first | 4,096 |

Each arm completed 16,384 mixed episodes and 16,384 rehearsal items in 2,048
optimizer updates. The credited arm learns from independently measured reward;
the matched withheld arm receives the same evidence and supervised lessons
without that reward term. Both use the same native weights, shared history,
conditional imagination and existing choice map. The source variables, physical
families, questions, annotations and action grid remain explicitly supplied.

The frozen [protocol](../../protocols/JOINT-021.md) preserves the comparison and
acceptance thresholds. [Registration](REGISTRATION.json) identifies new final
groups after excluding all earlier GENRE-017, NATIVE-019 and JOINT-020 groups.
No opened final was used to adjust the training recipe.

## Fresh assessment

| Route | Cohort | Human accuracy | Returned goal MSE | Later-query MSE |
|---|---|---:|---:|---:|
| credited | matched | 52.97% | 0.088323 | 0.084583 |
| credited | mismatched | 49.34% | 0.073048 | 0.062650 |
| credited | shifted | 47.27% | 0.177036 | 0.149208 |
| withheld | matched | 51.89% | 0.087362 | 0.091632 |
| withheld | mismatched | 49.07% | 0.085646 | 0.069935 |
| withheld | shifted | 46.48% | 0.193811 | 0.158858 |
| initial | matched | 48.11% | 0.189572 | 0.195272 |
| initial | mismatched | 42.97% | 0.160893 | 0.150032 |
| initial | shifted | 46.48% | 0.236457 | 0.204837 |
| uniform | matched | 53.78% | 0.077370 | 0.090776 |
| uniform | mismatched | 49.34% | 0.069498 | 0.066574 |
| uniform | shifted | 49.61% | 0.182450 | 0.143961 |
| disagreement | matched | 52.97% | 0.086150 | 0.083467 |
| disagreement | mismatched | 50.66% | 0.075256 | 0.065682 |
| disagreement | shifted | 47.27% | 0.183193 | 0.148942 |
| stop | matched | 54.86% | 0.099720 | 0.106612 |
| stop | mismatched | 51.19% | 0.086787 | 0.074687 |
| stop | shifted | 50.00% | 0.213239 | 0.163615 |
| erase_history | matched | 45.68% | 0.153659 | 0.175858 |
| erase_history | mismatched | 42.71% | 0.164871 | 0.138409 |
| erase_history | shifted | 41.80% | 0.252879 | 0.245936 |
| no_imagination | matched | 52.70% | 0.161984 | 0.159402 |
| no_imagination | mismatched | 49.34% | 0.166861 | 0.148902 |
| no_imagination | shifted | 47.27% | 0.214030 | 0.181203 |

The original goal is assessed before its grade reaches memory. The later query
explicitly includes that earlier feedback. The shifted cohort reuses identified
human material with new longer physical histories and changed control range;
it is not an additional independent human sample. Model weights are fixed during
these assessments. Numerical outcomes and credit were independently checked.

Utility is negative returned-goal squared error minus .001 per measurement.
Positive differences favor the credited learner. The 2,000-resample intervals
use paired premise groups and concern these fixed checkpoints.

| Credited utility minus control | Mean difference | Paired 95% interval |
|---|---:|---|
| withheld | 0.005879 | [-0.000659, 0.012984] |
| initial | 0.094482 | [0.075203, 0.115196] |
| uniform | -0.007332 | [-0.014870, 0.000304] |
| disagreement | 0.000038 | [-0.004789, 0.004787] |
| stop | 0.011579 | [0.005927, 0.017616] |
| erase_history | 0.078703 | [0.066438, 0.091012] |
| no_imagination | 0.083829 | [0.067053, 0.100976] |

The single-predictor selectors and inference removals have their explicit scopes
from the preceding course. Results across JOINT-020 and JOINT-021 are descriptive
because their final cohorts differ. [Complete comparisons](INDEPENDENT_METRICS.json).

## Whole-cycle verification

Sixteen development investigations continued through one owner and optimizer.
**16** decisions produced actual
reward-driven weight updates. All histories were re-encoded under the changed
predictor. Saved goals, weights, optimizer and RNG state survived independent
restart, with repeated credit rejected. [Delivery](DELIVERY.json).

The full repository check passed **205 tests**, with
0 failures and 0 errors. The separately packaged
owner also passed its fresh-process CLI lifecycle and file-integrity checks.
[Interface verification](RELEASE_CHECK.json).

| Qualification criterion | Result |
|---|---|
| source_identity | Passed |
| complete_matched_teaching | Passed |
| same_order_and_evidence | Passed |
| selected_updated_state | Passed |
| learned_choice_weights_changed | Passed |
| mixed_goal_improvement | Passed |
| human_retention | Passed |
| physical_retention | Passed |
| credit_contrast | Open; candidate preserved |
| exact_replay | Passed |
| persistent_weight_update_and_restart | Passed |
| engineering_tests | Passed |

The four-cell chronology check is a prospective requirement here. The shared
audit schema retains its original `post_training_design_quality` key, but this
course specified the check before any training. [Teaching](TEACHING.json),
[first-cycle learning replay](LEARNING.json), [final replay](REPLAY.json),
[retention](RETENTION.json) and [broader development checks](BROADER_DEVELOPMENT.json)
preserve source identities and measured effects.

## Use and cost

The [existing joint interface](../../docs/JOINT_USAGE.md) accepts
`--owner checkpoints/JOINT-021` when starting a new task. Later commands restore
that task's saved updated owner. The [manifest](../../checkpoints/JOINT-021/MANIFEST.json)
records the exact weights and assessment role. Earlier interfaces and all failed
work remain preserved; the [whole research tracker](../../docs/WHOLE_ARCHITECTURE.md)
still distinguishes this cycle from the other proposed mechanisms.

Supervised wall time: **29.75 minutes**; CPU time:
**29.40 minutes**; peak process-tree memory:
**948.5 MiB**. One numerical thread, 2 GiB cap and no
paid services were used. [Full attempt costs](COSTS.json) include failures.
The earlier native and first joint course costs remain separately recorded and
are part of the complete research acquisition cost.
