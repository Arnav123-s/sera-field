# Broad grounded curriculum

**Current-state note (UNIFIED-012):** The intake narrative below is the preserved
pre-training snapshot. Subsequent CONNECTED-003, ECHO-007 and CONCEPT studies did
teach the source tracks and preserve their results. UNIFIED-012 is now teaching
the coupled continuing owner on reading, arithmetic programs, dictionary,
grammar, conversation, calculus, programming, Plato, Descartes and simulated
physical observations. See the [whole-architecture tracker](WHOLE_ARCHITECTURE.md)
and [current research state](../reports/STATE.json) for integration status.
The old "no new subject training" paragraph below describes that earlier intake
turn only, not the present learner.

The user's clarified direction is to teach the entire intended learner: physical simulations are one experience source alongside mathematics, programming, language, other sciences and interpretation. The current trained release covers a finite physical curriculum. The additional tracks below are explicit teaching requirements; listing or downloading them does not mark them trained.

## Subject tracks and checks

| Track | Teaching experience | Imagination and understanding check | Independent assessment |
|---|---|---|---|
| Physical systems | Controlled simulations, trajectories, measurements, interventions and human explanations | Imagine changed initial conditions, identify missing influences, distinguish models with an intervention | A separate simulator or physical observations; document model assumptions and actuator behavior |
| Mathematics | Human worked problems, arithmetic, algebra, geometry, probability, definitions and proof examples | Construct several valid routes, test assumptions, seek counterexamples, connect representations | Exact calculation or proof checking with stated assumptions; numerical examples alone are not proofs |
| Programming | Human-written programs, specifications, tests, execution traces and debugging tasks | Predict program state, propose alternative implementations, generate a repair and test it | Actual bounded execution and independent tests, including unseen cases |
| Language and conversation | Human dictionary entries, grammar, conversation, narratives and multiple languages | Build the described situation, bind reference and roles, preserve ambiguity, track different observers' information | Held-out human descriptions and independently assessed consequences; separate meaning from text matching |
| Chemistry and biology | Human textbooks and curated empirical data; explicitly scoped simulations where appropriate | Connect interacting processes, predict changes under conditions, identify evidence that separates explanations | Source-specific empirical or independently simulated checks; simulation assumptions remain visible |
| History, philosophy and literature | Human-authored texts with provenance and historical context | Develop supported interpretations, compare alternatives, infer perspectives with uncertainty | Textual evidence and independent rubrics that permit several defensible interpretations |
| Practical tasks | Bounded file, data, coding and planning tasks in the lab | Form a goal state, imagine alternative procedures, perform actions, diagnose mismatches and recover | Verifiable task completion and state inspection; points do not expand permissions |

A mixed curriculum needs explicit subject sampling and separate held-out assessments so an easy, high-volume source does not absorb the entire training budget. Questions, procedures, uncertainty, retention and later transfer must be assessed within each taught track and across tracks. Record both topic coverage and the depth of the exercised behavior.

## Sources reconciled now

The local originals of Webster's dictionary, Baskervill and Sewell's grammar, DailyDialog, Plato, Descartes, Thompson's calculus text and SQuAD match their existing SHA-256 identities. They remain in the earlier source store; no earlier learner weights or implementation code is imported. The existing OpenStax science source manifests are identified for subject-specific intake. A filename or a downloaded book is not itself a teaching result.

Two additional pinned human-source collections have been obtained for the new lab:

- **GSM8K:** the original human-authored training problems and worked solutions from the [publisher repository](https://github.com/openai/grade-school-math), revision `3101c7d5072418e28b9008a6636bde82a006892c`. The automatically generated Socratic variants and example model solutions are excluded. The official test file has not been downloaded for this intake.
- **MBPP:** crowd-sourced Python problems, reference programs and tests from the [publisher's data directory](https://github.com/google-research/google-research/tree/4700efb9afa54286b0e04473ba80a13e8461e25f/mbpp). The author's split is retained: IDs 601–974 for training, 511–600 for development, 11–510 for testing and 1–10 for prompting. Only the training reference bodies were selected for inspection. Dataset-specific license attribution remains an intake item; raw records stay local.

The intake checker inspected 7,473 human mathematics training records and 23,714 arithmetic annotations. In 7,376 records the available annotations passed exact literal-arithmetic checks; 97 records are retained for review, including possible intentional approximations. These checks do not certify that the written solution correctly interprets the word problem. All 374 MBPP training records passed Python syntax and assertion-structure inspection. No reference program was executed and no coding semantics or tests have yet been certified by that inspection.

Full hashes, source roles and the distinction between acquisition, validation and training are recorded in [the source readiness ledger](../reports/CURRICULUM_READINESS.json). Raw human materials and review details stay local. Previous sealed evaluations are excluded from new teaching and selection.

## Learning mechanism and reward

All tracks must connect to the shared learner and the [behavior acceptance contract](BEHAVIOR_ACCEPTANCE.md). A teacher, simulator, program runner or proof checker supplies observations or checks; the learner must acquire the representation and procedures that use them. Log what the teacher supplied and what the learner constructed.

The existing FIELD-001 credit ledger is verification accounting. The next integrated implementation must connect independently checked progress to an actual update of the learned proposal/investigation procedure and then assess its effect on new tasks. Extra credit for breadth requires distinct, valid contributions rather than repeated wording or guesses. Reward type is conditional on the subject: exact proof, executable behavior, empirical fit and literary interpretation use different verification contracts.

Model-based learning literature provides examples of improving a policy through imagined outcomes ([Dreamer](https://www.nature.com/articles/s41586-025-08744-2)). Diversity-based skill objectives provide a separate mechanism to investigate ([DIAYN](https://arxiv.org/abs/1802.06070)). These sources motivate questions about the update rule; they are not recorded as SERA implementations. In particular, diversity of behavior does not by itself establish factual correctness.

## Current execution state

The scope audit and broader source intake are completed. **No new subject training was performed during this audit.** FIELD-001 weights and finals remain unchanged. The next implementation must freeze one connected, mixed-domain learning protocol with source lineage, subject-specific checks, reward-driven updates, untouched transfer/retention cohorts and exact resumable checkpoints. It must not rename a corpus download, a passage matcher or another supplied physical task as completion of the full understanding/imagination goal.
