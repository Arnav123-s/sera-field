# Prospective amendment: preserve information access in the delayed control

I found a design confound while reviewing the implementation, before any native
model test, training update or final prediction. Version 1 disabled observation
history entirely during the first half of the delayed arm's course. That would
mix the timing of richer memory with whether the learner could see any retained
observation at all. The original HISTORY-016 parent already had useful state;
an observation-free early control would be a weak comparison for this question.

Version 2 retains a simple fast trace in all controls from their first lesson.
The primary native arm has full fast/slow/bulk memory from the outset. The
delayed arm starts with that basic trace, then enables the richer dynamics halfway
through. A third `trace` arm keeps the basic trace for the full course. Data,
initialization, schedules, update counts, cohort selection, frozen qualification
gates and memory-erasure inference tests remain the same.

The trace uses the same learned observation/geometry/flow/query route and a
fixed 0.5 retention/write mixture. Its slow and active-bulk state is zero.
This is an attributed simple algorithmic control, not an independently discovered
learning rule. Every arm's actual cost is measured. The native final uses only
the already registered prospective source groups; none was opened for this change.

`NATIVE-019-v1.md` preserves the original text. The original source-preparation
record retains its original protocol hash; the v2 preparation binds the same
source identities and cohorts to this amendment. Both are published.
