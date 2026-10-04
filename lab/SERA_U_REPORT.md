# SERA-U report

Living report with tables generated from saved runs by `scripts/sera_u_report.py`.
This public edition omits unsupported U14 habit rows and includes a direct saved-schema summary.

## Outcome (2026-10-04)

- **In one line:** none of the discovery habits (U9-U12) has shown a measured benefit yet. Discovery certifies almost
  no laws (0-3 per case over four generations), so the habits built on laws barely run; the same switches differ by up to 10 of 48 between
  runs (measured twice); false credit is 0 everywhere. Short probes implicate the clock cap and thin observation; this diagnosis is provisional, and
  U14 changes the protocol; its saved results and failures are summarized below.
- **Memory (U8), one shared suite, one run per case:** without its memory layers SERA solved 26 48 39 47 of 48 in the
  full arm; with memory always on 28 40 38 34; with SERA choosing 26 33 38 36. Against the measured run-to-run spread
  (10 of 48, from one replicate pair), no-memory beats memory-always only in g3, and beats SERA's choice in g1 and g3;
  every other gap, and every difference in item seconds (spread 4.3 s), is within noise. So: a lean towards no memory,
  not yet a result.
- **Noise is large:** two runs with the same switches differ by up to 10 of 48 in a generation. One run per case is not
  enough; replicates come next.
- **Discovery (U9), finished:** in about 15 minutes of discovery per arm (4 generations, ~230 s each), SERA certified very
  few of the 14 hidden laws: full arm 0 (with designed experiments), 2 (random experiments), 2 (no unification credit);
  false credit 0 (`sera-runs/u9-discovery-vmc/discovery_summary.txt`). Its held-out assessment (42 45 47 43 of 48 against
  the discovery-off control's 36 39 39 41) is within the measured spread: no reliable discovery effect is established by these runs. This does not establish equivalence.
- **Why so few laws (probe, `sera-runs/u9-discovery-vmc/probe-u9.json`):** 6 of 9 exact worlds never reached the 4
  observations discovery needs before it proposes; in the two that did, a 0.5 s proposal found nothing, and 2 s found
  the hidden law (in 0.67 s) and the unchanged judge certified it. A wall-clock cap and thin observation starve it.
- **Einstein (U10, one run per case):** its four ways never fired in the full arm: 0 paradoxes, 0 principles, 0
  revisions, and one bold prediction (failed) in one ablation; 0-2 laws per case. They act on certified laws, and
  discovery certified almost none. Assessment gaps between cases reach 11 of 48 with no replicate in this batch
  (U8's spread: 10): no claim.
- **Scientists' habits (U11, one run per case):** these did fire: anomaly chases 3-31 per case (0 with that habit off),
  conjectures audited 5-23 (0 with that habit off), one conserved quantity, found only by the full set, which also
  certified the most laws (3). Its assessment, 45 45 46 46, against the Einstein control's 40 40 34 37, and the no-one-change case's 48 47 48 47:
  gaps of 5-14 on single runs, so no claim yet. Every full arm is complete; later arms are partial: two cases reached
  the 6-hour cap, two hit it at once after a 4-hour pause for a full disk, one ended by its training allowance, and
  no-number-conjectures stopped in its last arm on the MemoryField bug fixed in 05b4955 (it and the Einstein control
  ran on the earlier package 477f36d).
- **Darwin (U12, with a replicate of the full case):** its picture of the lineage worlds forecast about one specimen
  in five right (0.19-0.22 correct per trial in every case that keeps a picture); it built 13-19 likeness trees (none
  with trees off) and 0-3 mechanisms, made 0-3 predictions from them and none came true; laws certified: 0 in seven
  cases, 1 in one. The full case and its replicate solved 37 43 47 45 and 36 39 37 42 of 48: the same switches differ
  by up to 10 again, and every Darwin A/B gap is within that spread except no-lineage-trees in g0 (30 of 48, 10-11
  below two other cases; one generation of single runs). All eight full arms are complete; later arms ended at the
  wall-clock cap, which counted a 4-hour pause for a full disk as time spent.
- U13 full-arm results are saved for all five cases; only one case completed every arm. **U14 is implemented:** it checks the wiring between the parts and gives SERA its
  own clock (work, not seconds), one continuing life, questions first, and the holes a law leaves
  (development design; implementation and current limitations are in [SERA-U status](docs/SERA_U_STATUS.md)).
- **False credit:** 0 recorded in the saved cases reviewed here; not a universal guarantee.

## Saved U13/U14 update (2026-10-04)

U13 full-arm solved counts out of 48 across g0-g3 are 36/42/42/40 (roadmap),
41/47/45/47 (without own operations), 40/39/41/40 (without reconstruction),
47/46/47/46 (Darwin control), and 40/42/42/41 (without rough estimates).
Only the last case completed all arms; the others exhausted their allowance.
There are no replicates in this batch and no established benefit from U13.

Both completed U14 gap cases, seeds 3 and 5, recorded 0/384 eventual exam answers:
each full and no-holes arm answered 0/48 at each of g0-g3. Both recorded zero gaps
found and zero false credit. Finishing a run does not establish question solving.
The seed-5 question-priority case stopped on a receipt-provenance error; its five
saved generation assessments also recorded zero answers (0/240). Its full arm
reached g3, but the comparison did not complete. The seed-3 priority snapshot is
partial, not a completed comparison, and is excluded from these totals.

The [saved-schema summary](sera-runs/u14-vma/saved-summary.json) preserves exam
generation rows, gap counters, protocol identity, source hashes and stop records.
Legacy generated tables below still show U14 scores as MISSING because the reader
expects `rows`, while these files store `exam` and `holes`. Their U14 habit zeros
are unsupported by that reader and are omitted here. The raw saved exam and gap
counters above are read directly; per-item payloads and full life states stay local.

The development memory log records peaks near 10.9 GB per life, superseding the
earlier 0.7-1.1 GB snapshot. Table-count limits do not bound all retained values.
That memory issue and rejection of the question origin `interaction` remain
unfixed in this source revision. Cross-machine work-clock equivalence is untested.
Implementation code is unchanged in this publication update.

<!-- generated:begin outcome -->
Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / 4944c914d4a29ac2553e8e37aaa3a340afe617b2990244592656ed5285a4129e. Cases are comparable only on equal frozen suites.

| case | outcome | full generations | full solved /N | median item seconds | false credit |
|---|---|---|---|---|---|
| u10-einstein-vma/discovery | finished | 0 1 2 3 | 36 40 41 37 /48 | 4.0 3.7 2.2 1.8 | 0 |
| u10-einstein-vma/einstein | declared allowance: Declared training allowance exhausted | 0 1 2 3 | 41 41 42 42 /48 | 1.9 0.9 0.9 1.1 | 0 |
| u10-einstein-vma/einstein-no-bold-predictions | unfinished saved snapshot; stage=arms | 0 1 2 3 | 42 24 41 42 /48 | 2.8 9.5 1.2 2.1 | 0 |
| u10-einstein-vma/einstein-no-doubt-assumptions | finished | 0 1 2 3 | 47 46 46 47 /48 | 1.9 3.4 1.4 2.6 | 0 |
| u10-einstein-vma/einstein-no-symmetry-principles | finished | 0 1 2 3 | 37 37 39 36 /48 | 3.9 2.3 2.7 1.5 | 0 |
| u10-einstein-vma/einstein-no-thought-experiments | unfinished saved snapshot; stage=arms | 0 1 2 3 | 38 38 40 42 /48 | 6.2 3.2 1.1 2.1 | 0 |

Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / 7e074fe4fa2891213ea447156770ce4774c828eb8fa7d15dbbcd82bb89a165e2. Cases are comparable only on equal frozen suites.

| case | outcome | full generations | full solved /N | median item seconds | false credit |
|---|---|---|---|---|---|
| u11-scientists-vmc/einstein | finished | 0 1 2 3 | 40 40 34 37 /48 | 5.3 1.2 1.0 2.9 | 0 |
| u11-scientists-vmc/scientists | unfinished saved snapshot; stage=arms | 0 1 2 3 | 45 45 46 46 /48 | 3.5 3.8 1.3 5.3 | 0 |
| u11-scientists-vmc/scientists-no-anomaly-pursuit | unfinished saved snapshot; stage=arms | 0 1 2 3 | 38 43 44 42 /48 | 4.3 2.9 2.1 1.5 | 0 |
| u11-scientists-vmc/scientists-no-conserved-quantities | unfinished saved snapshot; stage=arms | 0 1 2 3 | 39 39 39 40 /48 | 3.3 1.1 2.8 3.8 | 0 |
| u11-scientists-vmc/scientists-no-gap-predictions | unfinished saved snapshot; stage=arms | 0 1 2 3 | 36 39 41 42 /48 | 5.8 3.3 1.3 3.4 | 0 |
| u11-scientists-vmc/scientists-no-number-conjectures | unfinished saved snapshot; stage=arms | 0 1 2 3 | 37 42 48 45 /48 | 3.9 1.5 0.9 1.6 | 0 |
| u11-scientists-vmc/scientists-no-one-change-experiments | declared allowance: Declared training allowance exhausted | 0 1 2 3 | 48 47 48 47 /48 | 2.8 2.5 1.1 2.7 | 0 |

Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / bba3a22d0c667016d6128ee862116b2575bba12e943250fd8525abc7bdea4535. Cases are comparable only on equal frozen suites.

| case | outcome | full generations | full solved /N | median item seconds | false credit |
|---|---|---|---|---|---|
| u12-darwin-vma/darwin | unfinished saved snapshot; stage=arms | 0 1 2 3 | 37 43 47 45 /48 | 4.8 4.4 2.0 3.7 | 0 |
| u12-darwin-vma/darwin-no-change-mechanisms | unfinished saved snapshot; stage=arms | 0 1 2 3 | 40 38 39 41 /48 | 4.0 1.7 4.6 2.3 | 0 |
| u12-darwin-vma/darwin-no-deep-time | unfinished saved snapshot; stage=arms | 0 1 2 3 | 39 38 42 42 /48 | 3.2 3.5 1.8 1.2 | 0 |
| u12-darwin-vma/darwin-no-lineage-trees | unfinished saved snapshot; stage=arms | 0 1 2 3 | 30 47 45 43 /48 | 7.8 1.7 1.7 2.6 | 0 |
| u12-darwin-vma/darwin-no-patient-observation | unfinished saved snapshot; stage=arms | 0 1 2 3 | 39 43 46 44 /48 | 6.8 4.6 1.9 3.8 | 0 |
| u12-darwin-vma/darwin-no-world-hologram | unfinished saved snapshot; stage=arms | 0 1 2 3 | 41 39 42 41 /48 | 2.9 3.6 3.3 1.4 | 0 |
| u12-darwin-vma/darwin-rep | unfinished saved snapshot; stage=arms | 0 1 2 3 | 36 39 37 42 /48 | 3.4 4.2 1.5 3.0 | 0 |
| u12-darwin-vma/scientists | unfinished saved snapshot; stage=arms | 0 1 2 3 | 35 42 40 40 /48 | 5.2 1.3 3.5 4.0 | 0 |

Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / cec6b3be2e5c1b297f65c0bf9b9d5fad7bbfff7261b2a857f60c356136d92781. Cases are comparable only on equal frozen suites.

| case | outcome | full generations | full solved /N | median item seconds | false credit |
|---|---|---|---|---|---|
| u14-vma/holes-s3 | finished | 0 1 2 3 | MISSING MISSING MISSING MISSING /48 | MISSING MISSING MISSING MISSING | 0 |
| u14-vma/holes-s5 | finished | 0 1 2 3 | MISSING MISSING MISSING MISSING /48 | MISSING MISSING MISSING MISSING | 0 |
| u14-vma/priority-s5 | stop: A checked exact program scope and provenance are required | 0 1 2 3 | MISSING MISSING MISSING MISSING /48 | MISSING MISSING MISSING MISSING | 0 |

Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / d64f3f8b41e53e8d764bc96ae58cd78fdaf42ebb07f98c7cd8fc6e374a32c862. Cases are comparable only on equal frozen suites.

| case | outcome | full generations | full solved /N | median item seconds | false credit |
|---|---|---|---|---|---|
| u13-roadmap-vma/roadmap | declared allowance: Declared training allowance exhausted | 0 1 2 3 | 36 42 42 40 /48 | 2.1 2.1 4.0 2.3 | 0 |
| u13-roadmap-vma/roadmap-no-own-operations | declared allowance: Declared training allowance exhausted | 0 1 2 3 | 41 47 45 47 /48 | 2.7 3.2 1.9 2.8 | 0 |
| u13-roadmap-vma/roadmap-no-rederive-concepts | declared allowance: Declared training allowance exhausted | 0 1 2 3 | 40 39 41 40 /48 | 6.5 2.8 1.1 3.0 | 0 |
| u13-roadmap-vmc/darwin | declared allowance: Declared training allowance exhausted | 0 1 2 3 | 47 46 47 46 /48 | 2.3 2.7 1.1 2.9 | 0 |
| u13-roadmap-vmc/roadmap-no-rough-estimates | finished | 0 1 2 3 | 40 42 42 41 /48 | 4.4 1.1 1.5 1.7 | 0 |

Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / f2a2bf86ff5041d695b0e8621e1c47ebeb070900f3b16d870e45e4f8acb37214. Cases are comparable only on equal frozen suites.

| case | outcome | full generations | full solved /N | median item seconds | false credit |
|---|---|---|---|---|---|
| u9-discovery-vmc/discovery | declared allowance: Declared training allowance exhausted | 0 1 2 3 | 42 45 47 43 /48 | 2.6 2.9 0.8 0.6 | 0 |
| u9-discovery-vmc/discovery-no-unify | declared allowance: Declared training allowance exhausted | 0 1 2 3 | 31 46 38 33 /48 | 6.9 3.7 5.4 4.2 | 0 |
| u9-discovery-vmc/discovery-random | declared allowance: Declared training allowance exhausted | 0 1 2 3 | 39 48 47 46 /48 | 1.9 2.0 0.8 1.5 | 0 |

Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / no discovery suite declared. Cases are comparable only on equal frozen suites.

| case | outcome | full generations | full solved /N | median item seconds | false credit |
|---|---|---|---|---|---|
| u8-u9-vmc-9036ca3/discovery-off | finished | 0 1 2 3 | 36 39 39 41 /48 | 4.5 4.0 1.2 3.7 | 0 |
| u8-u9-vmc-9036ca3/full | finished | 0 1 2 3 | 28 40 38 34 /48 | 8.5 4.0 3.7 4.6 | 0 |
| u8-u9-vmc-9036ca3/mem-choice | declared allowance: Declared 1.5-hour training allowance exhausted | 0 1 2 3 | 26 33 38 36 /48 | 9.4 4.3 5.0 3.4 | 0 |
| u8-u9-vmc-9036ca3/no-memory | unfinished saved snapshot; stage=arms | 0 1 2 3 | 26 48 39 47 /48 | 8.8 0.8 0.9 2.4 | 0 |
<!-- generated:end outcome -->

## Technical

<!-- generated:begin habits -->
### u10-einstein-vma (einstein)

Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / 4944c914d4a29ac2553e8e37aaa3a340afe617b2990244592656ed5285a4129e. Cases are comparable only on equal frozen suites.
Full arm: comparison totals when saved; otherwise latest saved habit snapshot. Sources identify each snapshot; other habits and arms are in the detail file.

| case | certified laws / experiments / seconds | paradoxes | principles / revisions | predictions | saved evidence | false credit |
|---|---|---|---|---|---|---|
| u10-einstein-vma/discovery | laws/experiments=2/62; seconds=1000.9 | found/confirmed=MISSING/MISSING | principles=MISSING; revisions=MISSING | made=MISSING; confirmed=MISSING; failed=MISSING | u10-comparison.json:glatest | 0 |
| u10-einstein-vma/einstein | laws/experiments=0/68; seconds=904.2 | found/confirmed=0/0 | principles=0; revisions=0 | made=0; confirmed=0; failed=0 | u10-comparison.json:glatest | 0 |
| u10-einstein-vma/einstein-no-bold-predictions | laws/experiments=0/72; seconds=1343.9 | found/confirmed=0/0 | principles=0; revisions=0 | made=0; confirmed=0; failed=0 | u10-comparison.json:glatest | 0 |
| u10-einstein-vma/einstein-no-doubt-assumptions | laws/experiments=0/77; seconds=987.8 | found/confirmed=0/0 | principles=0; revisions=0 | made=0; confirmed=0; failed=0 | u10-comparison.json:glatest | 0 |
| u10-einstein-vma/einstein-no-symmetry-principles | laws/experiments=1/97; seconds=878.2 | found/confirmed=0/0 | principles=0; revisions=0 | made=1; confirmed=0; failed=1 | u10-comparison.json:glatest | 0 |
| u10-einstein-vma/einstein-no-thought-experiments | laws/experiments=1/81; seconds=876.5 | found/confirmed=0/0 | principles=0; revisions=0 | made=0; confirmed=0; failed=0 | u10-comparison.json:glatest | 0 |

### u11-scientists-vmc (scientists)

Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / 7e074fe4fa2891213ea447156770ce4774c828eb8fa7d15dbbcd82bb89a165e2. Cases are comparable only on equal frozen suites.
Full arm: comparison totals when saved; otherwise latest saved habit snapshot. Sources identify each snapshot; other habits and arms are in the detail file.

| case | certified laws / experiments / seconds | conjectures | conserved quantities | chases / endings | saved evidence | false credit |
|---|---|---|---|---|---|---|
| u11-scientists-vmc/einstein | laws/experiments=0/103; seconds=968.4 | audited/refuted=MISSING/MISSING | MISSING | started=MISSING; pending=MISSING; active=MISSING; released=MISSING; explained=MISSING | u11-comparison.json:glatest; u10-comparison.json MISSING (not zero) | 0 |
| u11-scientists-vmc/scientists | laws/experiments=3/66; seconds=956.0 | audited/refuted=5/0 | 1 | started=3; pending=1; active=0; released=0; explained=2 | u11-comparison.json:glatest | 0 |
| u11-scientists-vmc/scientists-no-anomaly-pursuit | laws/experiments=0/77; seconds=863.1 | audited/refuted=10/10 | 0 | started=0; pending=0; active=0; released=0; explained=0 | u11-comparison.json:glatest | 0 |
| u11-scientists-vmc/scientists-no-conserved-quantities | laws/experiments=1/78; seconds=854.7 | audited/refuted=11/11 | 0 | started=13; pending=3; active=2; released=8; explained=0 | u11-comparison.json:glatest | 0 |
| u11-scientists-vmc/scientists-no-gap-predictions | laws/experiments=2/85; seconds=824.3 | audited/refuted=23/16 | 0 | started=31; pending=10; active=8; released=13; explained=0 | u11-comparison.json:glatest | 0 |
| u11-scientists-vmc/scientists-no-number-conjectures | laws/experiments=2/62; seconds=896.7 | audited/refuted=0/0 | 0 | started=3; pending=0; active=1; released=1; explained=1 | u11-comparison.json:glatest | 0 |
| u11-scientists-vmc/scientists-no-one-change-experiments | laws/experiments=2/61; seconds=876.7 | audited/refuted=7/7 | 0 | started=13; pending=4; active=1; released=7; explained=1 | u11-comparison.json:glatest | 0 |

### u12-darwin-vma (darwin)

Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / bba3a22d0c667016d6128ee862116b2575bba12e943250fd8525abc7bdea4535. Cases are comparable only on equal frozen suites.
Full arm: comparison totals when saved; otherwise latest saved habit snapshot. Sources identify each snapshot; other habits and arms are in the detail file.

| case | certified laws / experiments / seconds | hologram fidelity / calibration | trees / mechanisms | predictions | saved evidence | false credit |
|---|---|---|---|---|---|---|
| u12-darwin-vma/darwin | laws/experiments=0/25; seconds=204.5 | correct/trials=0.20; Brier/trial=0.18 | trees/mechanisms=19/3 | made=3; confirmed=0; failed=3 | scientists:g3; u12-comparison.json:glatest | 0 |
| u12-darwin-vma/darwin-no-change-mechanisms | laws/experiments=0/30; seconds=203.2 | correct/trials=0.21; Brier/trial=0.19 | trees/mechanisms=14/0 | made=0; confirmed=0; failed=0 | scientists:g3; u12-comparison.json:glatest | 0 |
| u12-darwin-vma/darwin-no-deep-time | laws/experiments=0/34; seconds=205.3 | correct/trials=0.22; Brier/trial=0.19 | trees/mechanisms=13/1 | made=1; confirmed=0; failed=1 | scientists:g3; u12-comparison.json:glatest | 0 |
| u12-darwin-vma/darwin-no-lineage-trees | laws/experiments=0/44; seconds=202.8 | correct/trials=0.19; Brier/trial=0.17 | trees/mechanisms=0/1 | made=1; confirmed=0; failed=1 | scientists:g3; u12-comparison.json:glatest | 0 |
| u12-darwin-vma/darwin-no-patient-observation | laws/experiments=0/25; seconds=203.5 | correct/trials=0.20; Brier/trial=0.18 | trees/mechanisms=14/1 | made=1; confirmed=0; failed=1 | scientists:g3; u12-comparison.json:glatest | 0 |
| u12-darwin-vma/darwin-no-world-hologram | laws/experiments=0/18; seconds=223.5 | correct/trials=MISSING; Brier/trial=MISSING | trees/mechanisms=13/0 | made=0; confirmed=0; failed=0 | scientists:g3; u12-comparison.json:glatest | 0 |
| u12-darwin-vma/darwin-rep | laws/experiments=0/29; seconds=202.9 | correct/trials=0.22; Brier/trial=0.19 | trees/mechanisms=13/0 | made=0; confirmed=0; failed=0 | scientists:g3; u12-comparison.json:glatest | 0 |
| u12-darwin-vma/scientists | laws/experiments=0/40; seconds=203.6 | correct/trials=MISSING; Brier/trial=MISSING | trees/mechanisms=MISSING/MISSING | made=MISSING; confirmed=MISSING; failed=MISSING | scientists:g3; u11-comparison.json MISSING (not zero) | 0 |

U14 habit rows are omitted because the legacy reader does not support the saved schema.

<!-- generated:end habits -->

<!-- generated:begin noise -->
Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / 4944c914d4a29ac2553e8e37aaa3a340afe617b2990244592656ed5285a4129e. Cases are comparable only on equal frozen suites.
Full arm: right - left / maximum replicate spread over all generations, shown per generation. Smaller absolute gaps are within noise; verdicts use unrounded values. Pairs match saved seed, device, allowances and evaluation sizes. Every arm and generation is in the detail file.

| left | right | pair | solved: delta / spread | item seconds: delta / spread | false credit |
|---|---|---|---|---|---|
| u10-einstein-vma/discovery | u10-einstein-vma/einstein | A/B | g0: 5 / MISSING noise MISSING; g1: 1 / MISSING noise MISSING; g2: 1 / MISSING noise MISSING; g3: 5 / MISSING noise MISSING | g0: -2.0 / MISSING noise MISSING; g1: -2.8 / MISSING noise MISSING; g2: -1.3 / MISSING noise MISSING; g3: -0.8 / MISSING noise MISSING | u10-einstein-vma/discovery: 0; u10-einstein-vma/einstein: 0 |
| u10-einstein-vma/discovery | u10-einstein-vma/einstein-no-bold-predictions | A/B | g0: 6 / MISSING noise MISSING; g1: -16 / MISSING noise MISSING; g2: 0 / MISSING noise MISSING; g3: 5 / MISSING noise MISSING | g0: -1.2 / MISSING noise MISSING; g1: 5.8 / MISSING noise MISSING; g2: -1.0 / MISSING noise MISSING; g3: 0.3 / MISSING noise MISSING | u10-einstein-vma/discovery: 0; u10-einstein-vma/einstein-no-bold-predictions: 0 |
| u10-einstein-vma/discovery | u10-einstein-vma/einstein-no-doubt-assumptions | A/B | g0: 11 / MISSING noise MISSING; g1: 6 / MISSING noise MISSING; g2: 5 / MISSING noise MISSING; g3: 10 / MISSING noise MISSING | g0: -2.0 / MISSING noise MISSING; g1: -0.3 / MISSING noise MISSING; g2: -0.8 / MISSING noise MISSING; g3: 0.8 / MISSING noise MISSING | u10-einstein-vma/discovery: 0; u10-einstein-vma/einstein-no-doubt-assumptions: 0 |
| u10-einstein-vma/discovery | u10-einstein-vma/einstein-no-symmetry-principles | A/B | g0: 1 / MISSING noise MISSING; g1: -3 / MISSING noise MISSING; g2: -2 / MISSING noise MISSING; g3: -1 / MISSING noise MISSING | g0: -0.1 / MISSING noise MISSING; g1: -1.4 / MISSING noise MISSING; g2: 0.5 / MISSING noise MISSING; g3: -0.3 / MISSING noise MISSING | u10-einstein-vma/discovery: 0; u10-einstein-vma/einstein-no-symmetry-principles: 0 |
| u10-einstein-vma/discovery | u10-einstein-vma/einstein-no-thought-experiments | A/B | g0: 2 / MISSING noise MISSING; g1: -2 / MISSING noise MISSING; g2: -1 / MISSING noise MISSING; g3: 5 / MISSING noise MISSING | g0: 2.2 / MISSING noise MISSING; g1: -0.5 / MISSING noise MISSING; g2: -1.1 / MISSING noise MISSING; g3: 0.3 / MISSING noise MISSING | u10-einstein-vma/discovery: 0; u10-einstein-vma/einstein-no-thought-experiments: 0 |
| u10-einstein-vma/einstein | u10-einstein-vma/einstein-no-bold-predictions | A/B | g0: 1 / MISSING noise MISSING; g1: -17 / MISSING noise MISSING; g2: -1 / MISSING noise MISSING; g3: 0 / MISSING noise MISSING | g0: 0.9 / MISSING noise MISSING; g1: 8.6 / MISSING noise MISSING; g2: 0.3 / MISSING noise MISSING; g3: 1.0 / MISSING noise MISSING | u10-einstein-vma/einstein: 0; u10-einstein-vma/einstein-no-bold-predictions: 0 |
| u10-einstein-vma/einstein | u10-einstein-vma/einstein-no-doubt-assumptions | A/B | g0: 6 / MISSING noise MISSING; g1: 5 / MISSING noise MISSING; g2: 4 / MISSING noise MISSING; g3: 5 / MISSING noise MISSING | g0: 0.0 / MISSING noise MISSING; g1: 2.4 / MISSING noise MISSING; g2: 0.5 / MISSING noise MISSING; g3: 1.5 / MISSING noise MISSING | u10-einstein-vma/einstein: 0; u10-einstein-vma/einstein-no-doubt-assumptions: 0 |
| u10-einstein-vma/einstein | u10-einstein-vma/einstein-no-symmetry-principles | A/B | g0: -4 / MISSING noise MISSING; g1: -4 / MISSING noise MISSING; g2: -3 / MISSING noise MISSING; g3: -6 / MISSING noise MISSING | g0: 2.0 / MISSING noise MISSING; g1: 1.4 / MISSING noise MISSING; g2: 1.8 / MISSING noise MISSING; g3: 0.4 / MISSING noise MISSING | u10-einstein-vma/einstein: 0; u10-einstein-vma/einstein-no-symmetry-principles: 0 |
| u10-einstein-vma/einstein | u10-einstein-vma/einstein-no-thought-experiments | A/B | g0: -3 / MISSING noise MISSING; g1: -3 / MISSING noise MISSING; g2: -2 / MISSING noise MISSING; g3: 0 / MISSING noise MISSING | g0: 4.2 / MISSING noise MISSING; g1: 2.3 / MISSING noise MISSING; g2: 0.3 / MISSING noise MISSING; g3: 1.1 / MISSING noise MISSING | u10-einstein-vma/einstein: 0; u10-einstein-vma/einstein-no-thought-experiments: 0 |
| u10-einstein-vma/einstein-no-bold-predictions | u10-einstein-vma/einstein-no-doubt-assumptions | A/B | g0: 5 / MISSING noise MISSING; g1: 22 / MISSING noise MISSING; g2: 5 / MISSING noise MISSING; g3: 5 / MISSING noise MISSING | g0: -0.9 / MISSING noise MISSING; g1: -6.2 / MISSING noise MISSING; g2: 0.2 / MISSING noise MISSING; g3: 0.5 / MISSING noise MISSING | u10-einstein-vma/einstein-no-bold-predictions: 0; u10-einstein-vma/einstein-no-doubt-assumptions: 0 |
| u10-einstein-vma/einstein-no-bold-predictions | u10-einstein-vma/einstein-no-symmetry-principles | A/B | g0: -5 / MISSING noise MISSING; g1: 13 / MISSING noise MISSING; g2: -2 / MISSING noise MISSING; g3: -6 / MISSING noise MISSING | g0: 1.1 / MISSING noise MISSING; g1: -7.2 / MISSING noise MISSING; g2: 1.5 / MISSING noise MISSING; g3: -0.6 / MISSING noise MISSING | u10-einstein-vma/einstein-no-bold-predictions: 0; u10-einstein-vma/einstein-no-symmetry-principles: 0 |
| u10-einstein-vma/einstein-no-bold-predictions | u10-einstein-vma/einstein-no-thought-experiments | A/B | g0: -4 / MISSING noise MISSING; g1: 14 / MISSING noise MISSING; g2: -1 / MISSING noise MISSING; g3: 0 / MISSING noise MISSING | g0: 3.4 / MISSING noise MISSING; g1: -6.3 / MISSING noise MISSING; g2: -0.1 / MISSING noise MISSING; g3: 0.0 / MISSING noise MISSING | u10-einstein-vma/einstein-no-bold-predictions: 0; u10-einstein-vma/einstein-no-thought-experiments: 0 |
| u10-einstein-vma/einstein-no-doubt-assumptions | u10-einstein-vma/einstein-no-symmetry-principles | A/B | g0: -10 / MISSING noise MISSING; g1: -9 / MISSING noise MISSING; g2: -7 / MISSING noise MISSING; g3: -11 / MISSING noise MISSING | g0: 1.9 / MISSING noise MISSING; g1: -1.1 / MISSING noise MISSING; g2: 1.3 / MISSING noise MISSING; g3: -1.1 / MISSING noise MISSING | u10-einstein-vma/einstein-no-doubt-assumptions: 0; u10-einstein-vma/einstein-no-symmetry-principles: 0 |
| u10-einstein-vma/einstein-no-doubt-assumptions | u10-einstein-vma/einstein-no-thought-experiments | A/B | g0: -9 / MISSING noise MISSING; g1: -8 / MISSING noise MISSING; g2: -6 / MISSING noise MISSING; g3: -5 / MISSING noise MISSING | g0: 4.2 / MISSING noise MISSING; g1: -0.2 / MISSING noise MISSING; g2: -0.2 / MISSING noise MISSING; g3: -0.5 / MISSING noise MISSING | u10-einstein-vma/einstein-no-doubt-assumptions: 0; u10-einstein-vma/einstein-no-thought-experiments: 0 |
| u10-einstein-vma/einstein-no-symmetry-principles | u10-einstein-vma/einstein-no-thought-experiments | A/B | g0: 1 / MISSING noise MISSING; g1: 1 / MISSING noise MISSING; g2: 1 / MISSING noise MISSING; g3: 6 / MISSING noise MISSING | g0: 2.3 / MISSING noise MISSING; g1: 0.9 / MISSING noise MISSING; g2: -1.6 / MISSING noise MISSING; g3: 0.7 / MISSING noise MISSING | u10-einstein-vma/einstein-no-symmetry-principles: 0; u10-einstein-vma/einstein-no-thought-experiments: 0 |

Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / 7e074fe4fa2891213ea447156770ce4774c828eb8fa7d15dbbcd82bb89a165e2. Cases are comparable only on equal frozen suites.
Full arm: right - left / maximum replicate spread over all generations, shown per generation. Smaller absolute gaps are within noise; verdicts use unrounded values. Pairs match saved seed, device, allowances and evaluation sizes. Every arm and generation is in the detail file.

| left | right | pair | solved: delta / spread | item seconds: delta / spread | false credit |
|---|---|---|---|---|---|
| u11-scientists-vmc/einstein | u11-scientists-vmc/scientists | A/B | g0: 5 / MISSING noise MISSING; g1: 5 / MISSING noise MISSING; g2: 12 / MISSING noise MISSING; g3: 9 / MISSING noise MISSING | g0: -1.8 / MISSING noise MISSING; g1: 2.7 / MISSING noise MISSING; g2: 0.3 / MISSING noise MISSING; g3: 2.4 / MISSING noise MISSING | u11-scientists-vmc/einstein: 0; u11-scientists-vmc/scientists: 0 |
| u11-scientists-vmc/einstein | u11-scientists-vmc/scientists-no-anomaly-pursuit | A/B | g0: -2 / MISSING noise MISSING; g1: 3 / MISSING noise MISSING; g2: 10 / MISSING noise MISSING; g3: 5 / MISSING noise MISSING | g0: -1.0 / MISSING noise MISSING; g1: 1.8 / MISSING noise MISSING; g2: 1.1 / MISSING noise MISSING; g3: -1.4 / MISSING noise MISSING | u11-scientists-vmc/einstein: 0; u11-scientists-vmc/scientists-no-anomaly-pursuit: 0 |
| u11-scientists-vmc/einstein | u11-scientists-vmc/scientists-no-conserved-quantities | A/B | g0: -1 / MISSING noise MISSING; g1: -1 / MISSING noise MISSING; g2: 5 / MISSING noise MISSING; g3: 3 / MISSING noise MISSING | g0: -2.0 / MISSING noise MISSING; g1: -0.0 / MISSING noise MISSING; g2: 1.8 / MISSING noise MISSING; g3: 0.9 / MISSING noise MISSING | u11-scientists-vmc/einstein: 0; u11-scientists-vmc/scientists-no-conserved-quantities: 0 |
| u11-scientists-vmc/einstein | u11-scientists-vmc/scientists-no-gap-predictions | A/B | g0: -4 / MISSING noise MISSING; g1: -1 / MISSING noise MISSING; g2: 7 / MISSING noise MISSING; g3: 5 / MISSING noise MISSING | g0: 0.5 / MISSING noise MISSING; g1: 2.1 / MISSING noise MISSING; g2: 0.3 / MISSING noise MISSING; g3: 0.5 / MISSING noise MISSING | u11-scientists-vmc/einstein: 0; u11-scientists-vmc/scientists-no-gap-predictions: 0 |
| u11-scientists-vmc/einstein | u11-scientists-vmc/scientists-no-number-conjectures | A/B | g0: -3 / MISSING noise MISSING; g1: 2 / MISSING noise MISSING; g2: 14 / MISSING noise MISSING; g3: 8 / MISSING noise MISSING | g0: -1.4 / MISSING noise MISSING; g1: 0.3 / MISSING noise MISSING; g2: -0.1 / MISSING noise MISSING; g3: -1.3 / MISSING noise MISSING | u11-scientists-vmc/einstein: 0; u11-scientists-vmc/scientists-no-number-conjectures: 0 |
| u11-scientists-vmc/einstein | u11-scientists-vmc/scientists-no-one-change-experiments | A/B | g0: 8 / MISSING noise MISSING; g1: 7 / MISSING noise MISSING; g2: 14 / MISSING noise MISSING; g3: 10 / MISSING noise MISSING | g0: -2.5 / MISSING noise MISSING; g1: 1.4 / MISSING noise MISSING; g2: 0.1 / MISSING noise MISSING; g3: -0.2 / MISSING noise MISSING | u11-scientists-vmc/einstein: 0; u11-scientists-vmc/scientists-no-one-change-experiments: 0 |
| u11-scientists-vmc/scientists | u11-scientists-vmc/scientists-no-anomaly-pursuit | A/B | g0: -7 / MISSING noise MISSING; g1: -2 / MISSING noise MISSING; g2: -2 / MISSING noise MISSING; g3: -4 / MISSING noise MISSING | g0: 0.8 / MISSING noise MISSING; g1: -0.9 / MISSING noise MISSING; g2: 0.8 / MISSING noise MISSING; g3: -3.7 / MISSING noise MISSING | u11-scientists-vmc/scientists: 0; u11-scientists-vmc/scientists-no-anomaly-pursuit: 0 |
| u11-scientists-vmc/scientists | u11-scientists-vmc/scientists-no-conserved-quantities | A/B | g0: -6 / MISSING noise MISSING; g1: -6 / MISSING noise MISSING; g2: -7 / MISSING noise MISSING; g3: -6 / MISSING noise MISSING | g0: -0.2 / MISSING noise MISSING; g1: -2.7 / MISSING noise MISSING; g2: 1.5 / MISSING noise MISSING; g3: -1.5 / MISSING noise MISSING | u11-scientists-vmc/scientists: 0; u11-scientists-vmc/scientists-no-conserved-quantities: 0 |
| u11-scientists-vmc/scientists | u11-scientists-vmc/scientists-no-gap-predictions | A/B | g0: -9 / MISSING noise MISSING; g1: -6 / MISSING noise MISSING; g2: -5 / MISSING noise MISSING; g3: -4 / MISSING noise MISSING | g0: 2.3 / MISSING noise MISSING; g1: -0.5 / MISSING noise MISSING; g2: 0.0 / MISSING noise MISSING; g3: -1.9 / MISSING noise MISSING | u11-scientists-vmc/scientists: 0; u11-scientists-vmc/scientists-no-gap-predictions: 0 |
| u11-scientists-vmc/scientists | u11-scientists-vmc/scientists-no-number-conjectures | A/B | g0: -8 / MISSING noise MISSING; g1: -3 / MISSING noise MISSING; g2: 2 / MISSING noise MISSING; g3: -1 / MISSING noise MISSING | g0: 0.4 / MISSING noise MISSING; g1: -2.3 / MISSING noise MISSING; g2: -0.4 / MISSING noise MISSING; g3: -3.7 / MISSING noise MISSING | u11-scientists-vmc/scientists: 0; u11-scientists-vmc/scientists-no-number-conjectures: 0 |
| u11-scientists-vmc/scientists | u11-scientists-vmc/scientists-no-one-change-experiments | A/B | g0: 3 / MISSING noise MISSING; g1: 2 / MISSING noise MISSING; g2: 2 / MISSING noise MISSING; g3: 1 / MISSING noise MISSING | g0: -0.7 / MISSING noise MISSING; g1: -1.3 / MISSING noise MISSING; g2: -0.2 / MISSING noise MISSING; g3: -2.6 / MISSING noise MISSING | u11-scientists-vmc/scientists: 0; u11-scientists-vmc/scientists-no-one-change-experiments: 0 |
| u11-scientists-vmc/scientists-no-anomaly-pursuit | u11-scientists-vmc/scientists-no-conserved-quantities | A/B | g0: 1 / MISSING noise MISSING; g1: -4 / MISSING noise MISSING; g2: -5 / MISSING noise MISSING; g3: -2 / MISSING noise MISSING | g0: -1.0 / MISSING noise MISSING; g1: -1.8 / MISSING noise MISSING; g2: 0.7 / MISSING noise MISSING; g3: 2.3 / MISSING noise MISSING | u11-scientists-vmc/scientists-no-anomaly-pursuit: 0; u11-scientists-vmc/scientists-no-conserved-quantities: 0 |
| u11-scientists-vmc/scientists-no-anomaly-pursuit | u11-scientists-vmc/scientists-no-gap-predictions | A/B | g0: -2 / MISSING noise MISSING; g1: -4 / MISSING noise MISSING; g2: -3 / MISSING noise MISSING; g3: 0 / MISSING noise MISSING | g0: 1.5 / MISSING noise MISSING; g1: 0.4 / MISSING noise MISSING; g2: -0.8 / MISSING noise MISSING; g3: 1.8 / MISSING noise MISSING | u11-scientists-vmc/scientists-no-anomaly-pursuit: 0; u11-scientists-vmc/scientists-no-gap-predictions: 0 |
| u11-scientists-vmc/scientists-no-anomaly-pursuit | u11-scientists-vmc/scientists-no-number-conjectures | A/B | g0: -1 / MISSING noise MISSING; g1: -1 / MISSING noise MISSING; g2: 4 / MISSING noise MISSING; g3: 3 / MISSING noise MISSING | g0: -0.4 / MISSING noise MISSING; g1: -1.4 / MISSING noise MISSING; g2: -1.2 / MISSING noise MISSING; g3: 0.1 / MISSING noise MISSING | u11-scientists-vmc/scientists-no-anomaly-pursuit: 0; u11-scientists-vmc/scientists-no-number-conjectures: 0 |
| u11-scientists-vmc/scientists-no-anomaly-pursuit | u11-scientists-vmc/scientists-no-one-change-experiments | A/B | g0: 10 / MISSING noise MISSING; g1: 4 / MISSING noise MISSING; g2: 4 / MISSING noise MISSING; g3: 5 / MISSING noise MISSING | g0: -1.5 / MISSING noise MISSING; g1: -0.4 / MISSING noise MISSING; g2: -1.0 / MISSING noise MISSING; g3: 1.2 / MISSING noise MISSING | u11-scientists-vmc/scientists-no-anomaly-pursuit: 0; u11-scientists-vmc/scientists-no-one-change-experiments: 0 |
| u11-scientists-vmc/scientists-no-conserved-quantities | u11-scientists-vmc/scientists-no-gap-predictions | A/B | g0: -3 / MISSING noise MISSING; g1: 0 / MISSING noise MISSING; g2: 2 / MISSING noise MISSING; g3: 2 / MISSING noise MISSING | g0: 2.5 / MISSING noise MISSING; g1: 2.1 / MISSING noise MISSING; g2: -1.5 / MISSING noise MISSING; g3: -0.4 / MISSING noise MISSING | u11-scientists-vmc/scientists-no-conserved-quantities: 0; u11-scientists-vmc/scientists-no-gap-predictions: 0 |
| u11-scientists-vmc/scientists-no-conserved-quantities | u11-scientists-vmc/scientists-no-number-conjectures | A/B | g0: -2 / MISSING noise MISSING; g1: 3 / MISSING noise MISSING; g2: 9 / MISSING noise MISSING; g3: 5 / MISSING noise MISSING | g0: 0.6 / MISSING noise MISSING; g1: 0.3 / MISSING noise MISSING; g2: -1.9 / MISSING noise MISSING; g3: -2.2 / MISSING noise MISSING | u11-scientists-vmc/scientists-no-conserved-quantities: 0; u11-scientists-vmc/scientists-no-number-conjectures: 0 |
| u11-scientists-vmc/scientists-no-conserved-quantities | u11-scientists-vmc/scientists-no-one-change-experiments | A/B | g0: 9 / MISSING noise MISSING; g1: 8 / MISSING noise MISSING; g2: 9 / MISSING noise MISSING; g3: 7 / MISSING noise MISSING | g0: -0.5 / MISSING noise MISSING; g1: 1.4 / MISSING noise MISSING; g2: -1.7 / MISSING noise MISSING; g3: -1.1 / MISSING noise MISSING | u11-scientists-vmc/scientists-no-conserved-quantities: 0; u11-scientists-vmc/scientists-no-one-change-experiments: 0 |
| u11-scientists-vmc/scientists-no-gap-predictions | u11-scientists-vmc/scientists-no-number-conjectures | A/B | g0: 1 / MISSING noise MISSING; g1: 3 / MISSING noise MISSING; g2: 7 / MISSING noise MISSING; g3: 3 / MISSING noise MISSING | g0: -1.9 / MISSING noise MISSING; g1: -1.8 / MISSING noise MISSING; g2: -0.4 / MISSING noise MISSING; g3: -1.8 / MISSING noise MISSING | u11-scientists-vmc/scientists-no-gap-predictions: 0; u11-scientists-vmc/scientists-no-number-conjectures: 0 |
| u11-scientists-vmc/scientists-no-gap-predictions | u11-scientists-vmc/scientists-no-one-change-experiments | A/B | g0: 12 / MISSING noise MISSING; g1: 8 / MISSING noise MISSING; g2: 7 / MISSING noise MISSING; g3: 5 / MISSING noise MISSING | g0: -3.0 / MISSING noise MISSING; g1: -0.7 / MISSING noise MISSING; g2: -0.2 / MISSING noise MISSING; g3: -0.7 / MISSING noise MISSING | u11-scientists-vmc/scientists-no-gap-predictions: 0; u11-scientists-vmc/scientists-no-one-change-experiments: 0 |
| u11-scientists-vmc/scientists-no-number-conjectures | u11-scientists-vmc/scientists-no-one-change-experiments | A/B | g0: 11 / MISSING noise MISSING; g1: 5 / MISSING noise MISSING; g2: 0 / MISSING noise MISSING; g3: 2 / MISSING noise MISSING | g0: -1.1 / MISSING noise MISSING; g1: 1.0 / MISSING noise MISSING; g2: 0.2 / MISSING noise MISSING; g3: 1.1 / MISSING noise MISSING | u11-scientists-vmc/scientists-no-number-conjectures: 0; u11-scientists-vmc/scientists-no-one-change-experiments: 0 |

Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / bba3a22d0c667016d6128ee862116b2575bba12e943250fd8525abc7bdea4535. Cases are comparable only on equal frozen suites.
Full arm: right - left / maximum replicate spread over all generations, shown per generation. Smaller absolute gaps are within noise; verdicts use unrounded values. Pairs match saved seed, device, allowances and evaluation sizes. Every arm and generation is in the detail file.

| left | right | pair | solved: delta / spread | item seconds: delta / spread | false credit |
|---|---|---|---|---|---|
| u12-darwin-vma/darwin | u12-darwin-vma/darwin-no-change-mechanisms | A/B | g0: 3 / 10 within noise; g1: -5 / 10 within noise; g2: -8 / 10 within noise; g3: -4 / 10 within noise | g0: -0.8 / 1.4 within noise; g1: -2.7 / 1.4 at or above measured spread; g2: 2.6 / 1.4 at or above measured spread; g3: -1.4 / 1.4 at or above measured spread | u12-darwin-vma/darwin: 0; u12-darwin-vma/darwin-no-change-mechanisms: 0 |
| u12-darwin-vma/darwin | u12-darwin-vma/darwin-no-deep-time | A/B | g0: 2 / 10 within noise; g1: -5 / 10 within noise; g2: -5 / 10 within noise; g3: -3 / 10 within noise | g0: -1.6 / 1.4 at or above measured spread; g1: -0.9 / 1.4 within noise; g2: -0.2 / 1.4 within noise; g3: -2.5 / 1.4 at or above measured spread | u12-darwin-vma/darwin: 0; u12-darwin-vma/darwin-no-deep-time: 0 |
| u12-darwin-vma/darwin | u12-darwin-vma/darwin-no-lineage-trees | A/B | g0: -7 / 10 within noise; g1: 4 / 10 within noise; g2: -2 / 10 within noise; g3: -2 / 10 within noise | g0: 3.1 / 1.4 at or above measured spread; g1: -2.8 / 1.4 at or above measured spread; g2: -0.3 / 1.4 within noise; g3: -1.2 / 1.4 within noise | u12-darwin-vma/darwin: 0; u12-darwin-vma/darwin-no-lineage-trees: 0 |
| u12-darwin-vma/darwin | u12-darwin-vma/darwin-no-patient-observation | A/B | g0: 2 / 10 within noise; g1: 0 / 10 within noise; g2: -1 / 10 within noise; g3: -1 / 10 within noise | g0: 2.0 / 1.4 at or above measured spread; g1: 0.1 / 1.4 within noise; g2: -0.1 / 1.4 within noise; g3: 0.1 / 1.4 within noise | u12-darwin-vma/darwin: 0; u12-darwin-vma/darwin-no-patient-observation: 0 |
| u12-darwin-vma/darwin | u12-darwin-vma/darwin-no-world-hologram | A/B | g0: 4 / 10 within noise; g1: -4 / 10 within noise; g2: -5 / 10 within noise; g3: -4 / 10 within noise | g0: -1.9 / 1.4 at or above measured spread; g1: -0.9 / 1.4 within noise; g2: 1.3 / 1.4 within noise; g3: -2.3 / 1.4 at or above measured spread | u12-darwin-vma/darwin: 0; u12-darwin-vma/darwin-no-world-hologram: 0 |
| u12-darwin-vma/darwin | u12-darwin-vma/darwin-rep | replicate | g0: -1 / 10 within noise; g1: -4 / 10 within noise; g2: -10 / 10 at or above measured spread; g3: -3 / 10 within noise | g0: -1.4 / 1.4 at or above measured spread; g1: -0.2 / 1.4 within noise; g2: -0.4 / 1.4 within noise; g3: -0.8 / 1.4 within noise | u12-darwin-vma/darwin: 0; u12-darwin-vma/darwin-rep: 0 |
| u12-darwin-vma/darwin | u12-darwin-vma/scientists | A/B | g0: -2 / 10 within noise; g1: -1 / 10 within noise; g2: -7 / 10 within noise; g3: -5 / 10 within noise | g0: 0.4 / 1.4 within noise; g1: -3.2 / 1.4 at or above measured spread; g2: 1.5 / 1.4 at or above measured spread; g3: 0.3 / 1.4 within noise | u12-darwin-vma/darwin: 0; u12-darwin-vma/scientists: 0 |
| u12-darwin-vma/darwin-no-change-mechanisms | u12-darwin-vma/darwin-no-deep-time | A/B | g0: -1 / 10 within noise; g1: 0 / 10 within noise; g2: 3 / 10 within noise; g3: 1 / 10 within noise | g0: -0.8 / 1.4 within noise; g1: 1.8 / 1.4 at or above measured spread; g2: -2.7 / 1.4 at or above measured spread; g3: -1.1 / 1.4 within noise | u12-darwin-vma/darwin-no-change-mechanisms: 0; u12-darwin-vma/darwin-no-deep-time: 0 |
| u12-darwin-vma/darwin-no-change-mechanisms | u12-darwin-vma/darwin-no-lineage-trees | A/B | g0: -10 / 10 at or above measured spread; g1: 9 / 10 within noise; g2: 6 / 10 within noise; g3: 2 / 10 within noise | g0: 3.8 / 1.4 at or above measured spread; g1: -0.0 / 1.4 within noise; g2: -2.9 / 1.4 at or above measured spread; g3: 0.3 / 1.4 within noise | u12-darwin-vma/darwin-no-change-mechanisms: 0; u12-darwin-vma/darwin-no-lineage-trees: 0 |
| u12-darwin-vma/darwin-no-change-mechanisms | u12-darwin-vma/darwin-no-patient-observation | A/B | g0: -1 / 10 within noise; g1: 5 / 10 within noise; g2: 7 / 10 within noise; g3: 3 / 10 within noise | g0: 2.8 / 1.4 at or above measured spread; g1: 2.9 / 1.4 at or above measured spread; g2: -2.7 / 1.4 at or above measured spread; g3: 1.5 / 1.4 at or above measured spread | u12-darwin-vma/darwin-no-change-mechanisms: 0; u12-darwin-vma/darwin-no-patient-observation: 0 |
| u12-darwin-vma/darwin-no-change-mechanisms | u12-darwin-vma/darwin-no-world-hologram | A/B | g0: 1 / 10 within noise; g1: 1 / 10 within noise; g2: 3 / 10 within noise; g3: 0 / 10 within noise | g0: -1.1 / 1.4 within noise; g1: 1.9 / 1.4 at or above measured spread; g2: -1.3 / 1.4 within noise; g3: -0.8 / 1.4 within noise | u12-darwin-vma/darwin-no-change-mechanisms: 0; u12-darwin-vma/darwin-no-world-hologram: 0 |
| u12-darwin-vma/darwin-no-change-mechanisms | u12-darwin-vma/darwin-rep | A/B | g0: -4 / 10 within noise; g1: 1 / 10 within noise; g2: -2 / 10 within noise; g3: 1 / 10 within noise | g0: -0.6 / 1.4 within noise; g1: 2.5 / 1.4 at or above measured spread; g2: -3.0 / 1.4 at or above measured spread; g3: 0.7 / 1.4 within noise | u12-darwin-vma/darwin-no-change-mechanisms: 0; u12-darwin-vma/darwin-rep: 0 |
| u12-darwin-vma/darwin-no-change-mechanisms | u12-darwin-vma/scientists | A/B | g0: -5 / 10 within noise; g1: 4 / 10 within noise; g2: 1 / 10 within noise; g3: -1 / 10 within noise | g0: 1.2 / 1.4 within noise; g1: -0.4 / 1.4 within noise; g2: -1.1 / 1.4 within noise; g3: 1.7 / 1.4 at or above measured spread | u12-darwin-vma/darwin-no-change-mechanisms: 0; u12-darwin-vma/scientists: 0 |
| u12-darwin-vma/darwin-no-deep-time | u12-darwin-vma/darwin-no-lineage-trees | A/B | g0: -9 / 10 within noise; g1: 9 / 10 within noise; g2: 3 / 10 within noise; g3: 1 / 10 within noise | g0: 4.6 / 1.4 at or above measured spread; g1: -1.8 / 1.4 at or above measured spread; g2: -0.1 / 1.4 within noise; g3: 1.4 / 1.4 within noise | u12-darwin-vma/darwin-no-deep-time: 0; u12-darwin-vma/darwin-no-lineage-trees: 0 |
| u12-darwin-vma/darwin-no-deep-time | u12-darwin-vma/darwin-no-patient-observation | A/B | g0: 0 / 10 within noise; g1: 5 / 10 within noise; g2: 4 / 10 within noise; g3: 2 / 10 within noise | g0: 3.6 / 1.4 at or above measured spread; g1: 1.1 / 1.4 within noise; g2: 0.1 / 1.4 within noise; g3: 2.6 / 1.4 at or above measured spread | u12-darwin-vma/darwin-no-deep-time: 0; u12-darwin-vma/darwin-no-patient-observation: 0 |
| u12-darwin-vma/darwin-no-deep-time | u12-darwin-vma/darwin-no-world-hologram | A/B | g0: 2 / 10 within noise; g1: 1 / 10 within noise; g2: 0 / 10 within noise; g3: -1 / 10 within noise | g0: -0.3 / 1.4 within noise; g1: 0.1 / 1.4 within noise; g2: 1.5 / 1.4 at or above measured spread; g3: 0.3 / 1.4 within noise | u12-darwin-vma/darwin-no-deep-time: 0; u12-darwin-vma/darwin-no-world-hologram: 0 |
| u12-darwin-vma/darwin-no-deep-time | u12-darwin-vma/darwin-rep | A/B | g0: -3 / 10 within noise; g1: 1 / 10 within noise; g2: -5 / 10 within noise; g3: 0 / 10 within noise | g0: 0.2 / 1.4 within noise; g1: 0.7 / 1.4 within noise; g2: -0.3 / 1.4 within noise; g3: 1.8 / 1.4 at or above measured spread | u12-darwin-vma/darwin-no-deep-time: 0; u12-darwin-vma/darwin-rep: 0 |
| u12-darwin-vma/darwin-no-deep-time | u12-darwin-vma/scientists | A/B | g0: -4 / 10 within noise; g1: 4 / 10 within noise; g2: -2 / 10 within noise; g3: -2 / 10 within noise | g0: 2.0 / 1.4 at or above measured spread; g1: -2.2 / 1.4 at or above measured spread; g2: 1.7 / 1.4 at or above measured spread; g3: 2.9 / 1.4 at or above measured spread | u12-darwin-vma/darwin-no-deep-time: 0; u12-darwin-vma/scientists: 0 |
| u12-darwin-vma/darwin-no-lineage-trees | u12-darwin-vma/darwin-no-patient-observation | A/B | g0: 9 / 10 within noise; g1: -4 / 10 within noise; g2: 1 / 10 within noise; g3: 1 / 10 within noise | g0: -1.1 / 1.4 within noise; g1: 2.9 / 1.4 at or above measured spread; g2: 0.2 / 1.4 within noise; g3: 1.2 / 1.4 within noise | u12-darwin-vma/darwin-no-lineage-trees: 0; u12-darwin-vma/darwin-no-patient-observation: 0 |
| u12-darwin-vma/darwin-no-lineage-trees | u12-darwin-vma/darwin-no-world-hologram | A/B | g0: 11 / 10 at or above measured spread; g1: -8 / 10 within noise; g2: -3 / 10 within noise; g3: -2 / 10 within noise | g0: -4.9 / 1.4 at or above measured spread; g1: 1.9 / 1.4 at or above measured spread; g2: 1.6 / 1.4 at or above measured spread; g3: -1.1 / 1.4 within noise | u12-darwin-vma/darwin-no-lineage-trees: 0; u12-darwin-vma/darwin-no-world-hologram: 0 |
| u12-darwin-vma/darwin-no-lineage-trees | u12-darwin-vma/darwin-rep | A/B | g0: 6 / 10 within noise; g1: -8 / 10 within noise; g2: -8 / 10 within noise; g3: -1 / 10 within noise | g0: -4.5 / 1.4 at or above measured spread; g1: 2.6 / 1.4 at or above measured spread; g2: -0.2 / 1.4 within noise; g3: 0.4 / 1.4 within noise | u12-darwin-vma/darwin-no-lineage-trees: 0; u12-darwin-vma/darwin-rep: 0 |
| u12-darwin-vma/darwin-no-lineage-trees | u12-darwin-vma/scientists | A/B | g0: 5 / 10 within noise; g1: -5 / 10 within noise; g2: -5 / 10 within noise; g3: -3 / 10 within noise | g0: -2.7 / 1.4 at or above measured spread; g1: -0.4 / 1.4 within noise; g2: 1.8 / 1.4 at or above measured spread; g3: 1.5 / 1.4 at or above measured spread | u12-darwin-vma/darwin-no-lineage-trees: 0; u12-darwin-vma/scientists: 0 |
| u12-darwin-vma/darwin-no-patient-observation | u12-darwin-vma/darwin-no-world-hologram | A/B | g0: 2 / 10 within noise; g1: -4 / 10 within noise; g2: -4 / 10 within noise; g3: -3 / 10 within noise | g0: -3.9 / 1.4 at or above measured spread; g1: -1.0 / 1.4 within noise; g2: 1.4 / 1.4 at or above measured spread; g3: -2.4 / 1.4 at or above measured spread | u12-darwin-vma/darwin-no-patient-observation: 0; u12-darwin-vma/darwin-no-world-hologram: 0 |
| u12-darwin-vma/darwin-no-patient-observation | u12-darwin-vma/darwin-rep | A/B | g0: -3 / 10 within noise; g1: -4 / 10 within noise; g2: -9 / 10 within noise; g3: -2 / 10 within noise | g0: -3.4 / 1.4 at or above measured spread; g1: -0.4 / 1.4 within noise; g2: -0.3 / 1.4 within noise; g3: -0.9 / 1.4 within noise | u12-darwin-vma/darwin-no-patient-observation: 0; u12-darwin-vma/darwin-rep: 0 |
| u12-darwin-vma/darwin-no-patient-observation | u12-darwin-vma/scientists | A/B | g0: -4 / 10 within noise; g1: -1 / 10 within noise; g2: -6 / 10 within noise; g3: -4 / 10 within noise | g0: -1.6 / 1.4 at or above measured spread; g1: -3.3 / 1.4 at or above measured spread; g2: 1.6 / 1.4 at or above measured spread; g3: 0.2 / 1.4 within noise | u12-darwin-vma/darwin-no-patient-observation: 0; u12-darwin-vma/scientists: 0 |
| u12-darwin-vma/darwin-no-world-hologram | u12-darwin-vma/darwin-rep | A/B | g0: -5 / 10 within noise; g1: 0 / 10 within noise; g2: -5 / 10 within noise; g3: 1 / 10 within noise | g0: 0.5 / 1.4 within noise; g1: 0.6 / 1.4 within noise; g2: -1.8 / 1.4 at or above measured spread; g3: 1.5 / 1.4 at or above measured spread | u12-darwin-vma/darwin-no-world-hologram: 0; u12-darwin-vma/darwin-rep: 0 |
| u12-darwin-vma/darwin-no-world-hologram | u12-darwin-vma/scientists | A/B | g0: -6 / 10 within noise; g1: 3 / 10 within noise; g2: -2 / 10 within noise; g3: -1 / 10 within noise | g0: 2.3 / 1.4 at or above measured spread; g1: -2.3 / 1.4 at or above measured spread; g2: 0.2 / 1.4 within noise; g3: 2.6 / 1.4 at or above measured spread | u12-darwin-vma/darwin-no-world-hologram: 0; u12-darwin-vma/scientists: 0 |
| u12-darwin-vma/darwin-rep | u12-darwin-vma/scientists | A/B | g0: -1 / 10 within noise; g1: 3 / 10 within noise; g2: 3 / 10 within noise; g3: -2 / 10 within noise | g0: 1.8 / 1.4 at or above measured spread; g1: -2.9 / 1.4 at or above measured spread; g2: 1.9 / 1.4 at or above measured spread; g3: 1.1 / 1.4 within noise | u12-darwin-vma/darwin-rep: 0; u12-darwin-vma/scientists: 0 |

Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / cec6b3be2e5c1b297f65c0bf9b9d5fad7bbfff7261b2a857f60c356136d92781. Cases are comparable only on equal frozen suites.
Full arm: right - left / maximum replicate spread over all generations, shown per generation. Smaller absolute gaps are within noise; verdicts use unrounded values. Pairs match saved seed, device, allowances and evaluation sizes. Every arm and generation is in the detail file.

| left | right | pair | solved: delta / spread | item seconds: delta / spread | false credit |
|---|---|---|---|---|---|
| MISSING | MISSING | MISSING | MISSING | MISSING | u14-vma/holes-s3: 0; u14-vma/holes-s5: 0; u14-vma/priority-s5: 0 |

Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / d64f3f8b41e53e8d764bc96ae58cd78fdaf42ebb07f98c7cd8fc6e374a32c862. Cases are comparable only on equal frozen suites.
Full arm: right - left / maximum replicate spread over all generations, shown per generation. Smaller absolute gaps are within noise; verdicts use unrounded values. Pairs match saved seed, device, allowances and evaluation sizes. Every arm and generation is in the detail file.

| left | right | pair | solved: delta / spread | item seconds: delta / spread | false credit |
|---|---|---|---|---|---|
| u13-roadmap-vma/roadmap | u13-roadmap-vma/roadmap-no-own-operations | A/B | g0: 5 / MISSING noise MISSING; g1: 5 / MISSING noise MISSING; g2: 3 / MISSING noise MISSING; g3: 7 / MISSING noise MISSING | g0: 0.6 / MISSING noise MISSING; g1: 1.1 / MISSING noise MISSING; g2: -2.1 / MISSING noise MISSING; g3: 0.5 / MISSING noise MISSING | u13-roadmap-vma/roadmap: 0; u13-roadmap-vma/roadmap-no-own-operations: 0 |
| u13-roadmap-vma/roadmap | u13-roadmap-vma/roadmap-no-rederive-concepts | A/B | g0: 4 / MISSING noise MISSING; g1: -3 / MISSING noise MISSING; g2: -1 / MISSING noise MISSING; g3: 0 / MISSING noise MISSING | g0: 4.4 / MISSING noise MISSING; g1: 0.7 / MISSING noise MISSING; g2: -2.9 / MISSING noise MISSING; g3: 0.7 / MISSING noise MISSING | u13-roadmap-vma/roadmap: 0; u13-roadmap-vma/roadmap-no-rederive-concepts: 0 |
| u13-roadmap-vma/roadmap | u13-roadmap-vmc/darwin | A/B | g0: 11 / MISSING noise MISSING; g1: 4 / MISSING noise MISSING; g2: 5 / MISSING noise MISSING; g3: 6 / MISSING noise MISSING | g0: 0.2 / MISSING noise MISSING; g1: 0.6 / MISSING noise MISSING; g2: -2.8 / MISSING noise MISSING; g3: 0.6 / MISSING noise MISSING | u13-roadmap-vma/roadmap: 0; u13-roadmap-vmc/darwin: 0 |
| u13-roadmap-vma/roadmap | u13-roadmap-vmc/roadmap-no-rough-estimates | A/B | g0: 4 / MISSING noise MISSING; g1: 0 / MISSING noise MISSING; g2: 0 / MISSING noise MISSING; g3: 1 / MISSING noise MISSING | g0: 2.3 / MISSING noise MISSING; g1: -1.0 / MISSING noise MISSING; g2: -2.4 / MISSING noise MISSING; g3: -0.6 / MISSING noise MISSING | u13-roadmap-vma/roadmap: 0; u13-roadmap-vmc/roadmap-no-rough-estimates: 0 |
| u13-roadmap-vma/roadmap-no-own-operations | u13-roadmap-vma/roadmap-no-rederive-concepts | A/B | g0: -1 / MISSING noise MISSING; g1: -8 / MISSING noise MISSING; g2: -4 / MISSING noise MISSING; g3: -7 / MISSING noise MISSING | g0: 3.8 / MISSING noise MISSING; g1: -0.4 / MISSING noise MISSING; g2: -0.8 / MISSING noise MISSING; g3: 0.2 / MISSING noise MISSING | u13-roadmap-vma/roadmap-no-own-operations: 0; u13-roadmap-vma/roadmap-no-rederive-concepts: 0 |
| u13-roadmap-vma/roadmap-no-own-operations | u13-roadmap-vmc/darwin | A/B | g0: 6 / MISSING noise MISSING; g1: -1 / MISSING noise MISSING; g2: 2 / MISSING noise MISSING; g3: -1 / MISSING noise MISSING | g0: -0.4 / MISSING noise MISSING; g1: -0.5 / MISSING noise MISSING; g2: -0.7 / MISSING noise MISSING; g3: 0.1 / MISSING noise MISSING | u13-roadmap-vma/roadmap-no-own-operations: 0; u13-roadmap-vmc/darwin: 0 |
| u13-roadmap-vma/roadmap-no-own-operations | u13-roadmap-vmc/roadmap-no-rough-estimates | A/B | g0: -1 / MISSING noise MISSING; g1: -5 / MISSING noise MISSING; g2: -3 / MISSING noise MISSING; g3: -6 / MISSING noise MISSING | g0: 1.7 / MISSING noise MISSING; g1: -2.1 / MISSING noise MISSING; g2: -0.4 / MISSING noise MISSING; g3: -1.1 / MISSING noise MISSING | u13-roadmap-vma/roadmap-no-own-operations: 0; u13-roadmap-vmc/roadmap-no-rough-estimates: 0 |
| u13-roadmap-vma/roadmap-no-rederive-concepts | u13-roadmap-vmc/darwin | A/B | g0: 7 / MISSING noise MISSING; g1: 7 / MISSING noise MISSING; g2: 6 / MISSING noise MISSING; g3: 6 / MISSING noise MISSING | g0: -4.2 / MISSING noise MISSING; g1: -0.1 / MISSING noise MISSING; g2: 0.1 / MISSING noise MISSING; g3: -0.1 / MISSING noise MISSING | u13-roadmap-vma/roadmap-no-rederive-concepts: 0; u13-roadmap-vmc/darwin: 0 |
| u13-roadmap-vma/roadmap-no-rederive-concepts | u13-roadmap-vmc/roadmap-no-rough-estimates | A/B | g0: 0 / MISSING noise MISSING; g1: 3 / MISSING noise MISSING; g2: 1 / MISSING noise MISSING; g3: 1 / MISSING noise MISSING | g0: -2.1 / MISSING noise MISSING; g1: -1.6 / MISSING noise MISSING; g2: 0.4 / MISSING noise MISSING; g3: -1.4 / MISSING noise MISSING | u13-roadmap-vma/roadmap-no-rederive-concepts: 0; u13-roadmap-vmc/roadmap-no-rough-estimates: 0 |
| u13-roadmap-vmc/darwin | u13-roadmap-vmc/roadmap-no-rough-estimates | A/B | g0: -7 / MISSING noise MISSING; g1: -4 / MISSING noise MISSING; g2: -5 / MISSING noise MISSING; g3: -5 / MISSING noise MISSING | g0: 2.1 / MISSING noise MISSING; g1: -1.5 / MISSING noise MISSING; g2: 0.4 / MISSING noise MISSING; g3: -1.2 / MISSING noise MISSING | u13-roadmap-vmc/darwin: 0; u13-roadmap-vmc/roadmap-no-rough-estimates: 0 |

Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / f2a2bf86ff5041d695b0e8621e1c47ebeb070900f3b16d870e45e4f8acb37214. Cases are comparable only on equal frozen suites.
Full arm: right - left / maximum replicate spread over all generations, shown per generation. Smaller absolute gaps are within noise; verdicts use unrounded values. Pairs match saved seed, device, allowances and evaluation sizes. Every arm and generation is in the detail file.

| left | right | pair | solved: delta / spread | item seconds: delta / spread | false credit |
|---|---|---|---|---|---|
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | A/B | g0: -11 / MISSING noise MISSING; g1: 1 / MISSING noise MISSING; g2: -9 / MISSING noise MISSING; g3: -10 / MISSING noise MISSING | g0: 4.3 / MISSING noise MISSING; g1: 0.8 / MISSING noise MISSING; g2: 4.5 / MISSING noise MISSING; g3: 3.6 / MISSING noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | A/B | g0: -3 / MISSING noise MISSING; g1: 3 / MISSING noise MISSING; g2: 0 / MISSING noise MISSING; g3: 3 / MISSING noise MISSING | g0: -0.7 / MISSING noise MISSING; g1: -1.0 / MISSING noise MISSING; g2: -0.0 / MISSING noise MISSING; g3: 0.8 / MISSING noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | A/B | g0: 8 / MISSING noise MISSING; g1: 2 / MISSING noise MISSING; g2: 9 / MISSING noise MISSING; g3: 13 / MISSING noise MISSING | g0: -5.0 / MISSING noise MISSING; g1: -1.8 / MISSING noise MISSING; g2: -4.5 / MISSING noise MISSING; g3: -2.7 / MISSING noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |

Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / no discovery suite declared. Cases are comparable only on equal frozen suites.
Full arm: right - left / maximum replicate spread over all generations, shown per generation. Smaller absolute gaps are within noise; verdicts use unrounded values. Pairs match saved seed, device, allowances and evaluation sizes. Every arm and generation is in the detail file.

| left | right | pair | solved: delta / spread | item seconds: delta / spread | false credit |
|---|---|---|---|---|---|
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/full | A/B | g0: -8 / 10 within noise; g1: 1 / 10 within noise; g2: -1 / 10 within noise; g3: -7 / 10 within noise | g0: 4.1 / 4.3 within noise; g1: -0.0 / 4.3 within noise; g2: 2.4 / 4.3 within noise; g3: 0.8 / 4.3 within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/full: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/mem-choice | A/B | g0: -10 / 10 at or above measured spread; g1: -6 / 10 within noise; g2: -1 / 10 within noise; g3: -5 / 10 within noise | g0: 5.0 / 4.3 at or above measured spread; g1: 0.2 / 4.3 within noise; g2: 3.8 / 4.3 within noise; g3: -0.3 / 4.3 within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/discovery-off | u8-u9-vmc-9036ca3/no-memory | replicate | g0: -10 / 10 at or above measured spread; g1: 9 / 10 within noise; g2: 0 / 10 within noise; g3: 6 / 10 within noise | g0: 4.3 / 4.3 at or above measured spread; g1: -3.2 / 4.3 within noise; g2: -0.4 / 4.3 within noise; g3: -1.3 / 4.3 within noise | u8-u9-vmc-9036ca3/discovery-off: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/mem-choice | A/B | g0: -2 / 10 within noise; g1: -7 / 10 within noise; g2: 0 / 10 within noise; g3: 2 / 10 within noise | g0: 0.9 / 4.3 within noise; g1: 0.3 / 4.3 within noise; g2: 1.4 / 4.3 within noise; g3: -1.1 / 4.3 within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/mem-choice: 0 |
| u8-u9-vmc-9036ca3/full | u8-u9-vmc-9036ca3/no-memory | A/B | g0: -2 / 10 within noise; g1: 8 / 10 within noise; g2: 1 / 10 within noise; g3: 13 / 10 at or above measured spread | g0: 0.2 / 4.3 within noise; g1: -3.2 / 4.3 within noise; g2: -2.8 / 4.3 within noise; g3: -2.1 / 4.3 within noise | u8-u9-vmc-9036ca3/full: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
| u8-u9-vmc-9036ca3/mem-choice | u8-u9-vmc-9036ca3/no-memory | A/B | g0: 0 / 10 within noise; g1: 15 / 10 at or above measured spread; g2: 1 / 10 within noise; g3: 11 / 10 at or above measured spread | g0: -0.6 / 4.3 within noise; g1: -3.5 / 4.3 within noise; g2: -4.2 / 4.3 within noise; g3: -1.0 / 4.3 within noise | u8-u9-vmc-9036ca3/mem-choice: 0; u8-u9-vmc-9036ca3/no-memory: 0 |
<!-- generated:end noise -->

Per-arm and per-generation tables, provenance and switches: `SERA_U_REPORT_TABLES.md` (generated).

## Plain words

We built one SERA (SERA-U) from your Field plus every ability from the lab, then gave it ways to find things out
for itself, like Newton, Einstein, Darwin and other scientists. Now we are measuring which parts help. The first answer
is about memory: SERA without memory did a little better, but the same SERA run twice can differ by ten questions
out of forty-eight, and most of the gap is inside that. So it leans towards "memory does not pay yet", and we need more
runs to be sure. Letting SERA decide when to remember has not shown a benefit yet either.

The second answer is about discovery: when SERA is left alone with worlds that hide a law, it finds very few of them in
the time we give it (none to two out of fourteen). Recorded false credit was zero,
and assessment differences were within the observed spread. These bounded findings
do not establish a universal correctness guarantee or equivalence to the control.
More time and better search are hypotheses to test. U14 is implemented, but its
behavioral benefits remain unverified.

Then we looked closer. In most worlds SERA never collected enough observations to try a law, and where it did, we had
cut each try off after half a second; with two seconds it found the law, and the judge agreed. So the habits that build
on laws, Einstein's above all, had nothing to work with and never switched on. The scientists' habits that do not need
a finished law (chasing a surprise, testing its own guesses) did switch on. Darwin's ways switched on too: SERA drew
family trees of the worlds it saw and a rough picture of them, but its picture guessed only about one new specimen in
five, and none of its predictions came true yet. None of these runs says yet whether a habit helps: one run each is not
enough, and two runs of the same SERA again differed by ten questions.

U14 now implements counted work, a continuing life, question priority and gaps left by laws.
The saved gap cases produced no exam answers; the priority comparison crashed.
Repairing provenance, memory bounds and report-schema support remains necessary before
a complete matched comparison can assess these mechanisms.
