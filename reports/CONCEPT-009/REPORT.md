# CONCEPT-009: Paired question teaching

Only the existing question-head weights were taught: 1,536 batches of 32, 49,152 presentations of 120 distinct supplied phrases. Development selected step 512. Every non-routing weight and every numerical output was exactly retained. The final direction and routing targets were not met. All three fresh-process replays were exact.

| Owner | Forward MSE | Inverse MSE | Counterfactual MSE | Plan MSE | Joint direction | Route |
|---|---:|---:|---:|---:|---:|---:|
| echo | 1.770150 | 53.757325 | 2.413066 | 0.964458 | not assessed | not assessed |
| repair | 0.076725 | 0.892681 | 0.102156 | 0.019607 | 74.41% | 79.88% |
| unchanged | 0.076725 | 0.892681 | 0.102156 | 0.019607 | 57.42% | 59.96% |

Each row uses the same fresh 512 supported systems and that study's reserved
question bank. The supplied variable vocabulary is shared with teaching; sentence
forms are held out. The additional 128 omitted-mechanism systems remain in the
raw results. Different studies use different systems, so comparisons between
rows in this table are valid; changes between study tables also reflect cohorts.

This unsuccessful whole-five-use candidate stays preserved with its training
losses, full optimizer/RNG revisions, final records, replays and costs.
Its frozen final was not reused for optimization. The qualified successor is
reported in [CONCEPT-011](../CONCEPT-011/REPORT.md).

[Decision](DECISION.json) · [protocol](../../protocols/CONCEPT-009.md) ·
[source and checkpoint identities](EVIDENCE_INDEX.json) · [costs](COSTS.json)
