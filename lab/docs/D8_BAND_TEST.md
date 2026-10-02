# Decision 8: the band as a test with the claim's own forecast

Plan revision 4, R4-2. development review, 2026-09-26. Status: built behind the policy flag `CCOPS5_BAND` (default `ui`, the
old band), tests first (`tests/core/test_band_test.py`, 7 tests). **the reviewer's independent review (review VD8): accept as an
experimental, default-off policy; not yet the confidence policy.** Its fixes are in `8cbe1ff` (section 6). T-D8 (a)
and (b) pass; (c) and the stress tests are still to run. An independent reviewer may re-review on return.

## 1. Why

The band is SERA's last certificate step before the audit: "anything else acting here is at most `band` in size, at
the visited cells, at confidence 1 − δ". It blocks most right-but-unsure worlds (5 of 6 in the P2 gate).

Its confidence radius comes from the flexible model's own forecast score:

    radius² = 2 (log L̂_f − Q_f + log(1/δ))

The flexible model is the claim plus 9 smooth basis functions plus the masses. `Q_f` is its prequential score. That
score pays the Occam cost of all those coefficients, about 140 nats in the P2 worlds (about 65 from the masses and the
claim, about 75 from the basis). So the radius is about 3.5× wider than the fit alone would need.

## 2. The test

Let `r(p) = b(p)ᵀ c_b` be the extra force at a point `p`, where `b` is the smooth basis and `c_b` its coefficients.

- The null hypothesis for threshold `t` is `H_{>t}`: there is a visited point `p` and a sign `s` with `s r(p) ≥ t`
  (the extra force exceeds `t` somewhere).
- The e-value is `E = exp(Q_A − sup_{θ ∈ H_{>t}} log L_{A+r}(θ))`, where `Q_A` is the claim's own prequential score
  (`ledger.q_claim(A)`, the numerator of every other e-value in the certificate).

**Validity.**
- Assume the truth lies in `A + span(basis)` (premise **F**) and `H_{>t}` holds.
- Then the true parameters `θ*` lie in `H_{>t}`, so `sup_{H_{>t}} L ≥ L_{θ*}`, and `E ≤ q_A(data) / L_{θ*}(data)`.
- That ratio is a nonnegative supermartingale under `θ*` whenever the claim's forecast is a sub-density given the past
  (premise **N**). This holds even though A is false under `H_{>t}`: N concerns the forecast, not the truth.
- By Ville's inequality, `P(ever E ≥ 1/δ) ≤ δ`. The δ is the band's existing share of the certificate's error budget.

**The sup, in closed form.**
- Use the same quadratic (ellipsoid) approximation of `log L` around the flexible fit `θ̂` that the band already uses
  (premise **Q**, unchanged). The maximum over the half-space `s b(p)ᵀ c_b ≥ t` is then
  `log L̂_f − ½ (t − s r̂(p))₊² / v(p)`, with `v(p) = b(p)ᵀ Σ_bb b(p)`.
- It follows that `H_{>t}` is rejected at level δ exactly when, for every visited `p`,
  `|r̂(p)| + R_A √v(p) ≤ t`, with `R_A² = 2 (log L̂_f − Q_A + log(1/δ))`.

**So Decision 8 is the old band formula with `Q_A` in place of `Q_f`.** The band is the smallest `t` the test rejects.
For each fixed `t` it is a valid (1 − δ) upper bound on the extra force's largest size at the visited cells.

**No new kind of premise, but Q is asked for more** (corrected after VD8; the first draft said "nothing new is
assumed", which was too strong). Premises N, F, Q and L (lattice to cells) are the band's premises today. D8 needs Q
one-sided: the computed constrained best fit must never be below the true one at any tested point and sign. With the
smaller radius, less slack hides a failure of that. The S4 C4
standard ("a certified null sup, or fail-closed") is stricter than what the current band meets. Like the current band,
D8 rests on Q, and the premise ledger says so in every certificate. A certified version is the U-1 problem again; the reviewer's
VU1 showed how hard that is.

**Fail-closed.** If `R_A² < 0`, meaning the flexible fit scores below the claim's forecast by more than log(1/δ), the
band is infinite.

## 3. What it costs and what it buys

- **Cost:** none extra. `Q_A` is already in the ledger. The flexible model's prequential is still computed, only as
  the fit's start.
- **Power:** when the claim is right, `log L̂_f − Q_A ≈` the claim's Occam cost plus about 4.5 nats (9 basis
  coefficients fitting noise), instead of adding the basis's 75 nats. Predicted ratio about √(76/147) ≈ 0.72.
  Measured on the clean test world: **0.673**.
- **When the claim is wrong** (a real extra force), `Q_A` falls with the misfit, the radius grows, and the band covers
  the force. This is test 3 (below) and T-D8 (b).

## 4. Built (behind the flag)

- **`ccops5/core/truth.py`:**
  - `BAND = os.environ.get('CCOPS5_BAND', 'ui')`;
  - `band_of` and `grown_band` take `q_ref`;
  - `certify` passes `ledger.q_claim(A)` under `'claim'`;
  - `Certificate.band_test` records the policy.
- **`ccops5/core/checker.py`:**
  - it refuses a certificate made under another band test;
  - its independent grown-band re-derivation uses the claim's forecast, re-computed from the throws.
- **The mind's band-directed search** (`ccops5/core/mind.py: worst_band_cells`) still ranks cells with the old radius.
  That is search only, so validity is unaffected; it can follow later.

## 5. T-D8, pre-registered (2026-09-26, before any T-D8 run; the unit tests above were run)

- **(a) Power:** on the 15 saved P2 ledgers (`sera-runs/b3-dev2/units/*-sera31.json` with `ledger_throws`), the
  claim's band under `'claim'` over its band under `'ui'`, same throws, scope and δ (1e-3 / 67).
  - **Bar:** median ratio ≤ 0.85.
  - **Reported:** every ratio, and how many claims fall below eps = 0.2 under each.
- **(b) Coverage:** 200 worlds of drag plus a planted spring `k x` (x is P1 of the basis). `|k|` is set so that the
  spring's largest size over the visited cells is 1–3 × eps, with random signs, seeds 1–200, and the throw pattern of
  `test_band_test.py`.
  - **Bar:** band under `'claim'` ≥ the planted size in 200/200.
- **(c) Validity:** under `CCOPS5_BAND=claim`, the P2 suites (mind sera31, dev seed 1) and bump probe v3.
  - **Bar:** 0 sure-and-wrong, and 0 checker refusals of accepted certificates.
  - **Reported:** right-but-unsure against the `'ui'` run.
- **Adoption:** D8 becomes the policy (`CCOPS5_BAND=claim` by default, truth-v3.1) only if (a), (b) and (c) all pass
  and the reviewer's review accepts it. It is never retroactive.

## 6. the reviewer's review ((review notes, not published)) and what changed

**Verdict: accept with changes, as an experimental, default-off policy.** The e-value construction and the `Q_A`
substitution are sound under explicit premises. The main plumbing is right: `certify` passes `ledger.q_claim(A)`, and
the checker replays the claim's forecast from the throws. reviewer ran no Python; the development review re-checked every point below against
the code.

**The theorem, stated as it holds** (VD8 sections 1 and 2):
- The null for threshold `t` is `H_{≥t}`: some tested point `p` and sign `s` with `s r(p) ≥ t`. Its supremum is the
  **maximum** of the per-(point, sign) constrained suprema, so rejection needs every point and sign to pass.
- **Coverage, for a fixed claim:** let `M` be the true extra force's largest size at the tested points. If the band
  `B < M`, the null at `t = M` was rejected while the true parameters were in it. So `P(B < M) ≤ δ`, even with
  data-chosen points, repeated looks, or an eps chosen after seeing the band. There is no extra penalty for the
  continuum of thresholds.
- **Choosing the claim after the data** costs an allocation over every eligible claim. `δ/n` is valid for a fixed,
  declared universe of `n` claims. A universe that grows needs a summable allocation, not the current `n_space`.
- **At `v(p) = 0`** the degenerate limit applies. At `R_A² = 0` the "exactly when" has a boundary exception, and the
  code's infinite band for `R_A² < 0` is conservative.

**Premises, as the certificate now says them** (`8cbe1ff`; the 'ui' ledger is unchanged):
- **Q (one-sided):** the quadratic approximation's constrained best fit is never below the true one, at any tested
  point and sign, across the nuisance masses and knocks. This is not certified; a local quadratic around one optimum
  does not give it. The old band had the same gap, with more slack.
- **L:** `band_of` tests the lattice points of the visited cells, not every reading or cell interior. "At the visited
  cells" holds at those points only, until an interpolation bound exists. T-D8 (b) also compares at the lattice points,
  so it does not test that gap.
- **N and F** as before. Sharing `Q_A` with the rivals' e-values does not break the `α + δ` union bound; no
  independence is needed.

**Fixed in `8cbe1ff`:**
- `CCOPS5_BAND` is checked against `ui` and `claim`. Before, any other string silently computed the `ui` band while the
  certificate named it.
- `band_of` fails closed on a nan or infinite radius, on a materially negative variance, and on a nan cell value. Before,
  `max(worst, nan)` kept the unsafe smaller `worst`. `grown_band` fails closed the same way.
- Under `claim`, the premise ledger states the one-sided Q and L. The checker rebuilds it with the certificate's band
  test.
- New tests: a claim-mode certificate is accepted by the checker; nonfinite scores give an infinite band; an unknown
  policy is refused at import.

**Known limits, inherited from the old band and not fixed here:**
- **The grown band** tolerates a null-space share up to `NULL_SHARE = 1e-9`. A functional with any component the data
  cannot see is unbounded in an exact quadratic, so this is engineering, not exact coverage.
- **The checker's grown-band re-derivation** accepts up to 5% above its own estimate (`BAND_AGREE`).
- For grown claims D8 is therefore **not an exact e-test as coded**. The ordinary band's checker path is not independent
  of truth (it re-runs `certify`).

**T-D8 so far** (generated: `sera-runs/t-d8/part_a.json`, `part_b.json`):

| Part | Result | Bar | Note |
|---|---|---|---|
| (a) power, 15 P2 ledgers | median ratio **0.727** | ≤ 0.85: pass | 14 ratios in 0.671–0.793. L3-01 is 2.307: its claim misfits, `Q_A` falls, and the band widens, as it should. Below eps 0.2: 2 under `ui`, 3 under `claim` |
| (b) planted spring, 200 worlds | **200/200** covered | 200/200: pass | A regression gate only. With 0 failures in 200, the one-sided 95% upper bound on the failure rate is about 1.5%, far above the nominal `0.001/67`. It does not show the rare-event level |
| (c) P2 suites and bump v3 under `claim` | not run | 0 sure-and-wrong, 0 checker refusals | next |

**Before adoption, still needed (VD8 section 6):**
- (b) stress tests: basis combinations and scales, near-boundary strengths, weakly identified designs, grown claims,
  nuisance masses, both knock policies, `δ/n` rather than `1e-4`. Report every planted size, band and failure, at the
  actual tested scope, at lattice points and at readings.
- (c) with world counts, sure-and-wrong, right-but-unsure, accepted certificates and every checker refusal, paired with
  the `ui` run. If the mind's throws diverge, also compare bands on identical saved ledgers.
- A proof or certified bound for one-sided Q, or its measurement. Until then D8 stays default-off.
