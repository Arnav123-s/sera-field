# Cross-goal novelty audit

During handoff review I found a reward-accounting loophole: the initial novelty
key included the original goal ID. A genuinely new assessment for the same method
under a renamed goal could therefore receive another novelty bonus. Binding credit
to its original goal is necessary; resetting novelty for each goal is not.

The corrected key uses the verifier's canonical contribution and assumption scope
across the learner's goals. A reused method may still earn verified progress credit
on a new problem, but not another discovery bonus. Source/assessment reuse, goal
binding and stale-policy checks are unchanged.

A new regression checks this exact case. All 23 connected-core tests passed after
the correction; the prior complete 55-test suite and four curriculum tests remain
preserved. There are now 56 distinct tests. The first attempted replay found the
shared numerical lease occupied and launched no worker. I preserved that failed
reservation, waited for the other job to finish and ran a fresh supervised attempt.
No other job or lock was modified.

This correction is a separate source-lab commit for Antigravity to incorporate in
its branch, preserving any concurrent changes. It does not require repeating any
completed model training or reopening a final evaluation.
