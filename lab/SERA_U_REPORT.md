# SERA-U report

Living report, updated in place. Every table between `generated` markers is written by `scripts/sera_u_report.py` from
saved run folders under `sera-runs/` (never typed); the text around them is development review reading of those tables.

## Outcome (2026-10-03)

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
  the discovery-off control's 36 39 39 41) is within the measured spread: discovery as built neither helps nor hurts
  there yet, and it finds hardly any laws in its time.
- **Einstein, scientists, Darwin (U10-U12):** running or finishing on Colab; tables are added as each batch comes home.
  U13 (Newton, Feynman, Fermi) is built and waits for a free machine.
- **False credit:** 0 in every saved case so far.

<!-- generated:begin outcome -->
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
### u9-discovery-vmc (discovery)

Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / f2a2bf86ff5041d695b0e8621e1c47ebeb070900f3b16d870e45e4f8acb37214. Cases are comparable only on equal frozen suites.
Full arm: comparison totals when saved; otherwise latest saved habit snapshot. Sources identify each snapshot; other habits and arms are in the detail file.

| case | certified laws / experiments / seconds | saved evidence | false credit |
|---|---|---|---|
| u9-discovery-vmc/discovery | laws/experiments=0/5; seconds=210.0 | discovery:g3; comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |
| u9-discovery-vmc/discovery-no-unify | laws/experiments=0/2; seconds=245.2 | discovery:g3; comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |
| u9-discovery-vmc/discovery-random | laws/experiments=2/4; seconds=205.6 | discovery:g3; comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |

### u8-u9-vmc-9036ca3 (discovery)

Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / no discovery suite declared. Cases are comparable only on equal frozen suites.
Full arm: comparison totals when saved; otherwise latest saved habit snapshot. Sources identify each snapshot; other habits and arms are in the detail file.

| case | certified laws / experiments / seconds | saved evidence | false credit |
|---|---|---|---|
| u8-u9-vmc-9036ca3/discovery-off | laws/experiments=MISSING/MISSING; seconds=MISSING | habit metrics MISSING; comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |
| u8-u9-vmc-9036ca3/full | laws/experiments=MISSING/MISSING; seconds=MISSING | habit metrics MISSING; comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |
| u8-u9-vmc-9036ca3/mem-choice | laws/experiments=MISSING/MISSING; seconds=MISSING | habit metrics MISSING; comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |
| u8-u9-vmc-9036ca3/no-memory | laws/experiments=MISSING/MISSING; seconds=MISSING | habit metrics MISSING; comparison JSON MISSING (not zero; optional for memory-only cases) | 0 |
<!-- generated:end habits -->

<!-- generated:begin noise -->
Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / f2a2bf86ff5041d695b0e8621e1c47ebeb070900f3b16d870e45e4f8acb37214. Cases are comparable only on equal frozen suites.
Full arm: right - left / maximum replicate spread over all generations, shown per generation. Smaller absolute gaps are within noise; verdicts use unrounded values. Pairs match saved seed, device, allowances and evaluation sizes. All metrics are in the detail file.

| left | right | pair | solved: delta / spread | item seconds: delta / spread | false credit |
|---|---|---|---|---|---|
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-no-unify | A/B | g0: -11 / MISSING noise MISSING; g1: 1 / MISSING noise MISSING; g2: -9 / MISSING noise MISSING; g3: -10 / MISSING noise MISSING | g0: 4.3 / MISSING noise MISSING; g1: 0.8 / MISSING noise MISSING; g2: 4.5 / MISSING noise MISSING; g3: 3.6 / MISSING noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-no-unify: 0 |
| u9-discovery-vmc/discovery | u9-discovery-vmc/discovery-random | A/B | g0: -3 / MISSING noise MISSING; g1: 3 / MISSING noise MISSING; g2: 0 / MISSING noise MISSING; g3: 3 / MISSING noise MISSING | g0: -0.7 / MISSING noise MISSING; g1: -1.0 / MISSING noise MISSING; g2: -0.0 / MISSING noise MISSING; g3: 0.8 / MISSING noise MISSING | u9-discovery-vmc/discovery: 0; u9-discovery-vmc/discovery-random: 0 |
| u9-discovery-vmc/discovery-no-unify | u9-discovery-vmc/discovery-random | A/B | g0: 8 / MISSING noise MISSING; g1: 2 / MISSING noise MISSING; g2: 9 / MISSING noise MISSING; g3: 13 / MISSING noise MISSING | g0: -5.0 / MISSING noise MISSING; g1: -1.8 / MISSING noise MISSING; g2: -4.5 / MISSING noise MISSING; g3: -2.7 / MISSING noise MISSING | u9-discovery-vmc/discovery-no-unify: 0; u9-discovery-vmc/discovery-random: 0 |

Frozen suites: c809fde39db5ec5ecd6085986294c1dd3c53636c039058b511e90481e5081b9f / no discovery suite declared. Cases are comparable only on equal frozen suites.
Full arm: right - left / maximum replicate spread over all generations, shown per generation. Smaller absolute gaps are within noise; verdicts use unrounded values. Pairs match saved seed, device, allowances and evaluation sizes. All metrics are in the detail file.

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
the time we give it (none to two out of fourteen), never claims a wrong one, and is no worse at its tests for trying. It
needs either more time or better ways to look; the Einstein, scientists' and Darwin habits are the next things we measure.
