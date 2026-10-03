# SERA-U: one entity, the author's Field with every ability of the lab

Living plan (updated in place). Started 2026-10-02 17:00 UTC on branch `sera-u` (from sera-v4 `080f992`).

## 0. The order (the author, 2026-10-02, lightly cleaned)

"Add all the abilities we have built over time to the Field, not working together: make one copy that conjoins both
together. Improve my Field's imagination with all the methods we have come up with. Try memory with two layers: my
original one, with a layer of holography too. Make the judge adaptive, not fixed. Implement the understanding part in
my Field. Teach the ways of working; teach breaking problems down, the course etc.; use the crutch ledger during the
teaching. Give my Field all the abilities of your lab, make a new entity in this lab, then develop it. After you are
done, run /verify and evaluate, then report the results to me. Plan everything first, update the records and
reports, and continue."

The rules this plan keeps:
- **The originals stay untouched.** The original learned Field and discovery lab are never edited; SERA-U gets
  its own copy of the code, pinned by hash.
- **No pretrained or outside model.** SERA-U starts from fresh weights.
- **No given words, laws or programs.** Only mechanisms; all content is taught, read or discovered.
- **Every coded mechanism is a registered crutch** (`sera/crutches.py`), switchable and reported.
- **`lesson_words` (86cf3e5) is off in every SERA-U run** (decided by development review, delegated): it hands SERA the answer
  words.
- **Numbers come only from saved runs.** Reports are updated in place.
- **The laptop stays light.** Long runs go to Colab.

## 1. What goes in: every part and every ability

**Base, kept whole:** the author's Field (`sera-field-core022` @ `c67ed27`, `CoreOwner`). That means:
- the Cl(3,0) boundary on a sheaf with learned rotor connections, `UnifiedEnergy`, and the stationary field;
- the fast/slow traces, the active bulk, the marks and the flow context;
- the conditional fusion, the three imagined branches, and `GraphProposal`;
- the session, portfolio and verifier;
- bound credit, and exact checkpoints.

| Lab part (where it lives now) | How it enters SERA-U |
|---|---|
| Concept library, invention, reuse (`phi.Field.invent`, `_inner_ability`) | Exact callable library kept as data; each concept gets a learned key in the Field (S28 §2) |
| Program search (`lang.py`) and the proposer join (S28) | The Field proposes fragments; `LG.search` stays as the fallback; the judge decides |
| **Imagination methods:** compose, ring/recall, dream, step, back from the goal, wish/build, closer, dimension, question, explore (`MethodField`, `one.py`) | Each becomes a way the three branches can be driven. The choice of method is a Field readout, taught by the teacher's demonstrations (fading) and then learned from returns |
| **Memory layer B, holographic** (`phi.Ideas`, HRR 2048-d, One Field cue states) | A second memory layer beside the author's traces/bulk (layer A). Observed events are written into both. B's ringing enters the Field as a retained source, like `r(m)` in NATIVE. Ablating A, B or both is a test |
| **Understanding** (`phi` U/L/B pool: understanding^0.5 · laws^0.25 · beliefs^0.25) | U becomes a Field readout of how familiar each part is in this context. L = description length × standing (kept exact). B = this task's evidence. Φ ranks hypotheses and proposals |
| **Ways of working** (`LoopField`: ask, explore, grow, imagine, prove, leave; `teacher_way`) | A Field readout over the same faculties, with teacher evidence fading and Thompson-style draws. Taught, not coded |
| **Breaking problems into steps** (`StepField`, worked steps, `_step`, `_backward`) | the author's way (2026-10-02): a fuzzy roadmap of the whole answer, dreamed by the Field and tried at once; if it is wrong, only the *next* step, then re-dream the rest. The next step is a Field readout, taught by worked values (S27, fading); no coded decomposition rule |
| Words, lexicon, talk, reading, dictionary (`talk.py`, `dictionary.py`, `sera_converse.py`) | Text ports of the author's Field (stable word IDs, no hashing collisions) plus the lab's lexicon of meanings learned from proofs |
| Physics rails: pushes, ask, convince, ramp formulas, honest credit (`tasks.Rail`, `one.py`) | Raw-measurement port; rail moves kept; certified curve/drawing/formula credit unchanged |
| Questions, inbox, serendipity links, dualities, curiosity order | Kept as Field events. **Curiosity from syndromes** (the author, 2026-10-02, after quantum error correction): many cheap self-consistency checks, and an adaptive decoder that locates what SERA does not know; SERA then dreams, asks and reads there (U6) |
| Talk reliability, "I don't know" (talk tally / `frame_identity`) | Part of the inner judge (§1.1) |
| The course (S27): lesson, study with books, test 1/2/3 | The teaching program for SERA-U (§3) |
| The crutch ledger (`crutches.py`) | Every SERA-U mechanism is registered. Each teaching run records the ledger, and crutches fade by course phase |
| Tripwire, ring observer, honest records | Unchanged; they also apply to SERA-U |

### 1.1 The adaptive judge (the author: "adaptive, not fixed")

It has two parts:
- **The inner judge** is new and learned, and *taught what is correct*: corrections train it by contrast (the right
  answer against its wrong one). Its answer-or-abstain bar is adaptive, not tight (the author: a tight judge hinders
  SERA even when it is right). It weighs the learned cost of a wrong answer against the cost of not answering, and
  starts permissive. It is the Field's own sense that "this could be right": a readout calibrated
  against every outer verdict.
  - It decides what to send to the outer judge, what to say, and when to answer "I don't know".
  - Its trust is earned: its advice counts as far as its measured agreement with the outer judge allows.
  - It never certifies a proof by itself.
- **The outer judge** (`ccops5/core`, `Exact.verify`) adapts *how hard it looks*: more counterexample probes and more
  throws where SERA was wrong before, and where the inner judge is overconfident. Its acceptance bar never drops.
  "Sure" must still be earned, and the tripwire stays.
  - Any change to the acceptance rule itself goes through independent review and a paired regression, as for Decision 16.
  - **Decided (by development review, delegated by the author 2026-10-02):** the outer bar itself does not adapt.

## 2. Implementation components

| Build | What | Done when |
|---|---|---|
| **U1 entity + proposer** | `sera_u/field/`: the pinned copy of the author's Field code (the dependency closure of `CoreOwner`, its session, portfolio and verifier) with `SOURCE.json` hashes; device fixes only. A parity test: same seed and inputs give identical tensors to the original. `sera_u/mind.py` `SeraU`: one object that saves the owner, optimizer, library, lexicon, layer B, the ledger and the RNGs. S28 Build 1 inside it: the task ports, the proposer feeding `LG.search`, wake/abstract/dream/train, and `scripts/sera_u_rsi.py` with its four arms | parity passes; S28 §6 tests pass; a tiny smoke run on the laptop |
| **U2 memory + understanding** | Layer B (holographic) beside layer A, written and read through the Field; the U/L/B pool inside the Field | ablation tests: each layer can be switched off and the effect measured; Φ ranks proposals; nothing leaks from the observer |
| **U3 ways of working + imagination + inner judge** | Faculty and method readouts with teacher evidence; all imagination methods drive the branches; the calibrated inner judge, with "I don't know" | the readouts learn from teacher evidence that fades; calibration curve recorded; abstention only past the bar |
| **US speed** (after U2) | The Field reads training, dream and assessment views as one batch of rows; one read per view per step. The same results (parity tests), faster. Measured need: one training batch takes 50 s on one CPU thread (laptop and Colab), and the T4 GPU is slower (108 s) | `train(1, 8)` ≤ 12 s on one CPU thread; batched equals single |
| **U6 curiosity from syndromes** (after U3) | the author's idea: QEC-style checks (two programs that fit but disagree on queries, the two memories, roadmap against execution, inner against outer judge, Field surprise, familiar but failing) and an adaptive decoder learned from learning progress; dreams aimed at the gap, questions where answers are allowed, books read first | the decoder adapts both ways; no leak; aimed against unaimed A/B on Colab |
| **U7 not yet** (after U6; the author, 2026-10-02 21:50) | "I don't know" is not an end and not coded: when unsure it keeps going (next-best method, smallest step, ask, recall, dig) until right or the item's budget, then the revisit queue; answering is a taught faculty choice (teacher evidence fading, then returns), the U3 cost bar kept only as the crutch `abstain_bar`; talk keeps a question pending and answers when it finds it; the words for "not yet" are taught | not-yet continues; taught then learned both ways; no hard-coded phrase; switches reproduce U3/U2 |
| **U4 outer judge scrutiny** (touches the judge's caller, never the bar) | Adaptive probing and throws; independent reviews the diff; paired regression | the old claims keep their verdicts and bands; no claim accepted that was refused before |
| **U5 course + ledger** | S27's course runs on SERA-U; the ledger is recorded and crutches fade per phase; talks | the course runs end to end on a smoke budget |
| **U9 discovery** (the author, 2026-10-03: discover on its own, as Newton did) | A discovery phase in every RSI generation: open worlds with no question posed, its own questions from surprise and syndromes, experiments it designs, laws certified by the judge (honest kinds), one law for many things (compression credit), hidden quantities, anomalies as not-yet items; discoveries feed the library and dreams | no world law reaches the Field; each switch off reproduces the old records; rediscovery A/B on held-out worlds |
| **U10 Einstein's ways** (the author, 2026-10-03: think like Einstein) | Four moves SERA chooses, taught then learned: thought experiments (its own laws run in imagined extremes; a contradiction is a paradox, its next question and experiment), invariance as principles (transformations from its own inverse concepts; a fallible search prior), doubting the assumption two clashing laws share (revisions certified on both worlds), bold predictions (recorded before the experiment) | U9's records unchanged with it off; Einstein suite A/B (conflict, invariance and paradox worlds) |
| **U11 the scientists' habits** (the author, 2026-10-03) | Galileo (one change at a time), Mendeleev (predict the withheld member of a family), Euler/Gauss/Ramanujan (conjectures about its own concepts, audited), Noether (conserved quantities, one fading lesson), Curie/Pasteur (chase an anomaly across items until explained); Kepler is U9. Roadmap, not built: Newton's new mathematics (new operations in its own language), Feynman (rebuild to understand), Fermi (rough estimates); Darwin is U12 | U10's records unchanged with it off; scientists suite A/B |
| **U12 Darwin in its own picture of the world** (the author, 2026-10-03: SERA need not live in our world; it builds a rough picture, a hologram, from what it receives, and thinks like Darwin there on its own problems) | The hologram (its own fuzzy, measured picture of the worlds it met, in the Field; renders imagined worlds and runs imagined time; never certifies anything), patient observation (a field notebook kept across generations), likeness trees (shared structure in its own language; compression, not true history), a mechanism of gradual change (its own edits plus a sorting rule from its concepts, run in imagined time, predictions recorded first), deep imagined time; all taught then learned. Roadmap: feed it information about our world (books, public data), each download with the author's permission | U11's records unchanged with it off; lineage suite A/B (a hidden branching process of worlds; SERA sees only specimens) |
| **U13 Newton, Feynman, Fermi** (the author's roadmap, 2026-10-03) | Own new operations from old primitives (a new basis for search, not new primitive semantics), rebuilding concepts from their own values, calibrated rough estimates that may prune once earned; all taught then learned | U12's records unchanged with it off; roadmap suite A/B |

S27 (the course on the lab SERA) is merged into `sera-v4` first, once its tests pass. U5 reuses it.

## 3. Teaching, verification, evaluation

**Keep going until right** (the author): an unsolved lesson or practice item is revisited later in the phase instead of
given up; speed comes from learning, not from giving up. Test 3 stays one attempt.

**Teaching (Colab GPU):** the course (lesson, then study with books, then tests 1, 2 and 3), plus 3 RSI generations
(wake, sleep, dream). The ledger is recorded per phase.

**/verify:** after U5 (the author's step 4).
- All tests pass with the switches at their defaults and off.
- An independent review of the whole SERA-U diff.
- The original Field's parity, and the lab SERA's old records reproduced.

**Evaluation: the bake-off that never ran (B7), on one frozen suite and one time box.**

| Arm | What |
|---|---|
| F | the author's Field alone (CORE-022 owner, fresh, same course) |
| Φ | The lab SERA alone (sera-v4, same course) |
| U | SERA-U |
| U minus each part | No proposer / no layer A / no layer B / no understanding / no inner judge / no taught ways |

**Measures:**
- the course tests 1–3 (right, wrong, "I don't know");
- physics worlds;
- lists and numbers (unseen compositions);
- talk;
- the RSI g-curve (S28 §3);
- the list benchmark;
- a small ARC development subset;
- time, memory, and the laptop limits.

**The report:** two parts (technical, then plain words), leading with the outcome. Which one is best where, from
saved runs only.

## Plain words

We are building one new SERA, SERA-U, in the lab. Its body is your Field: the same geometric network, learning from
scratch. Into it goes everything the lab built:
- the library of inventions;
- the step-by-step thinking;
- all the ways of imagining;
- understanding;
- the taught ways of working;
- the words and the talks;
- physics;
- the course.

Its memory has two layers: yours, and a holographic one on top. It gets an inner judge that learns when its own
answers are probably right. "I don't know" is taught, and means "not yet": it keeps going with the next way
of imagining or the smallest step until it gets there. The outer judge still checks every proof, and adapts by
looking harder where SERA was wrong, but never lowers its bar.

Beyond that, it learns to find things out for itself, the way great scientists did: Newton (worlds with no question), Einstein (thought experiments, what stays the same, bold predictions), and the habits of Galileo, Mendeleev, Euler, Noether and Curie. For Darwin, it does not need our world: it builds its own rough picture of the worlds it has met, watches patiently, sorts what it sees by likeness, and looks for the slow process that made the variety, testing its guesses on what turns up next.

The implementation now includes U1-U13 and the speed refinements, with their status recorded separately.
It is taught with the course, verified, and measured against your
Field alone and the lab SERA alone, on the same tests. Then you get the report.

Latest implementation and evidence: [SERA-U status](docs/SERA_U_STATUS.md).
