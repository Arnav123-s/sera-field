# JOINT-021: counterbalanced chronology repair

This protocol is prospective. It corrects the design issue found by source
inspection during JOINT-020, preserving every prior course, final and failed
attempt. It does not change weights in response to any particular opened final
case. The sole teaching change is to cross the order of human text and physical
measurements independently of physical family.

## Exact repair and constants

Keep JOINT-020's native architecture, initialization, human/simulation training
examples, action choices, source views, optimizer, objective, update counts,
rehearsal, development ranking and fixed selection rule. Every arm again starts
from the same NATIVE-019/native development selection, with fresh optimizer state.
Use the same 1,024 cycles of 16 mixed episodes and 16 rehearsal items per cycle.
Both credited and reward-withheld arms complete 2,048 optimizer updates.

For training episode number n, the existing physical family is n modulo 2.
Set text-first order to floor(n/2) modulo 2. Each block of four then includes
both families in both orders, giving exactly 4,096 presentations in each of the
four cells per arm. Preserve the original human/world ID, simulator parameters,
uniform training action, measured outcome and rehearsal ordering. Thus this
repair changes chronology alone in the teaching data. It supplies no new family
indicator to the learner.

The development examples are the same attributable examples and worlds, with
this corrected chronology. Keep the composite development selection rule and
128-cycle assessment interval. No new hyperparameter search is introduced.

## Fresh final evidence and controls

Register 128 complete human premise groups per cohort after excluding all groups
opened by GENRE-017, NATIVE-019 and JOINT-020. Stop preparation if fewer than 128
groups remain; do not silently reuse opened finals. Use fresh `JOINT-021-final-`
simulation namespaces and the independent four-cell chronology. The shifted
cohort has 256 examples, four measurements before the probe, and the same
previously declared expanded control range. The retention simulation namespace
must also be new. Count repeated human material in the shifted cohort explicitly.

Complete both matched courses before opening finals. Retain JOINT-020's learned,
reward-withheld, initial, uniform, branch-disagreement, STOP, erased-history and
query-settling-removed controls, with identical assessment. Final model weights
stay fixed. The original goal is assessed before its grading signal enters state.
The later-query score has access to the explicitly recorded preceding feedback.

Keep all JOINT-020's frozen qualification thresholds: changed learned decision
weights; improved returned mixed-task goal MSE over the initial owner; ordinary
human retention within three percentage points and physical retention within
10%; exact source/teaching/replay/engineering and persistent-delivery checks; and
credited-versus-withheld utility interval above zero. Utility is negative final
original-goal squared error minus .001 per performed probe. Use 2,000 paired
premise-group bootstrap samples, seed 202020. The fixed-model scope remains.

Add the explicit design check that all four family/order cells occur equally in
the teaching logs. Run both orders on the same development worlds after the
course as a separate descriptive diagnostic. It neither changes selection nor
provides another opportunity to tune finals.

## Persistence, resource and interpretation contracts

Use the existing mixed session, independent reward, weight update, history
re-encoding and exact owner/optimizer/RNG restart. Run 16 development deliveries
through one continuing owner, preserving original goals and individual revisions.
Earlier numerical and human interfaces remain separately available.

Use the same supervised one-thread, 2 GiB process-tree resource contract with no
paid services. Every phase is a new capped process after its predecessor exits.
Save logs, optimizer/RNG and next cursor; retain failed attempts and costs.
Compare to JOINT-020 descriptively because the final cohorts are fresh, not as
an unqualified between-study leaderboard. Actual learned reward benefit and the
supplied teachers, variables, actions and annotations remain separate claims.
