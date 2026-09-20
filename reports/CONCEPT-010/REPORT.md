# CONCEPT-010: Lexical residual and interference

An 8,194-parameter word/character-hash residual was trained from zero: 2,048 batches of 32, 65,536 presentations of 388 supplied phrases. Development selected step 2,048. The numerical and direction gates passed; routing missed its 90% target. All four replays were exact. A clearly labeled post-final diagnostic measured 71.25% routing for the old head, 93.75% for the residual alone and 85% for their sum across 80 unique opened phrases. That diagnosed interference; it did not qualify an untested repair.

| Owner | Forward MSE | Inverse MSE | Counterfactual MSE | Plan MSE | Joint direction | Route |
|---|---:|---:|---:|---:|---:|---:|
| echo | 1.645878 | 65.767573 | 2.211696 | 0.922433 | not assessed | not assessed |
| original | 0.032574 | 0.098255 | 0.048834 | 0.004415 | 56.45% | 57.62% |
| repair | 0.032574 | 0.098255 | 0.048834 | 0.004415 | 82.42% | 85.94% |
| unchanged | 0.032574 | 0.098255 | 0.048834 | 0.004415 | 68.16% | 71.48% |

Each row uses the same fresh 512 supported systems and that study's reserved
question bank. The supplied variable vocabulary is shared with teaching; sentence
forms are held out. The additional 128 omitted-mechanism systems remain in the
raw results. Different studies use different systems, so comparisons between
rows in this table are valid; changes between study tables also reflect cohorts.

This unsuccessful whole-five-use candidate stays preserved with its training
losses, full optimizer/RNG revisions, final records, replays and costs.
Its frozen final was not reused for optimization. The qualified successor is
reported in [CONCEPT-011](../CONCEPT-011/REPORT.md).

[Decision](DECISION.json) · [protocol](../../protocols/CONCEPT-010.md) ·
[source and checkpoint identities](EVIDENCE_INDEX.json) · [costs](COSTS.json)
