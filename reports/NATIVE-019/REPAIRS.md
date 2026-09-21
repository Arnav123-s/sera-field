# Preserved pre-training diagnosis and repair

The first native engineering attempt (`native019-tests-001`) passed 14 checks
and failed one exact-equality assertion. No native training had started and no
native final prediction existed.

The failed assertion compared two identical questions at different batch
positions after their observed histories were erased. Their float32 logits
differed by at most **1.4901161193847656e-08**. The independent supervised
[diagnostic](ROUNDING_DIAGNOSIS.json) found:

- Changing the discarded premises while preserving batch positions produced
  exactly identical logits.
- Querying an explicitly empty state produced exactly identical logits.
- Repeating the cross-position comparison in float64 gave zero difference.
- Retained observations changed the logits by about `0.00066236`.

The regression now checks the actual no-bypass contract through both exact
comparisons, and bounds the cross-position arithmetic discrepancy by one float32
machine epsilon at unit scale. The model, training schedule, source cohorts and final
criteria are unchanged. The original failed test and diagnostic costs remain
in their supervised attempt records and the study's complete cost ledger.

The repaired test suite uses a fresh attempt name. Completed source preparation,
the earlier GENRE-017 course, attachment checks and uncertainty analysis are
preserved without repetition.

During teaching, a source review tightened the later joint-learning audit. Its
initial-gradient report now reconstructs the actual first curriculum batch and
training objective, and checks that loss and gradient norm against the teaching
receipt. The small initial-state examples remain preflight path tests. This
changes neither training nor model selection, source partitions or final
criteria; no final prediction had been opened when the audit was clarified.
# Fresh-process replay resource recovery

All three 8,192-update courses and all 32 original route/cohort assessments
completed in `native019-campaign-001`. The worker then launched its independent
replay while its allocator still retained training memory. The child raised
`MemoryError` under the existing 2 GiB Windows process-tree limit, before replay
predictions. This is a resource orchestration failure, not a changed final result.

I preserved the failed attempt and its complete costs. `resume_native019.py`
checks the completed courses, original final records and exact failure before
running the unchanged replay in a separately supervised process, followed by
unfinished delivery/audit/packaging. Training, selection, model code, frozen
protocol, original final predictions and the resource cap remain unchanged.
