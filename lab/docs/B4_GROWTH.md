# B4 design: growing what is missing (decision D11, decided by development review under the author's delegation)

Status: design for review by independent review before any code. Tests come first. The frozen judge `truth-v1` stays untouched
for M1; the extension becomes `truth-v2` on branch `sera-v3`, and no SERA result counts until B has reviewed it.

## The problem
The judge can only say laws built from its fixed pieces:
- the 11 base ideas;
- products of shapes, powers on a grid, and sin/cos drives;
- at most two terms.

A world whose law has a new piece has nothing true to certify, however clever the imagination is. Examples:
- x·|v|;
- saturation tanh(v/0.7);
- a bell exp(−x²);
- three terms;
- a second hidden number per object, such as a "charge".

The alarm fires (M1: 8/8), and then SERA can only recombine the old menu (T5: 4/11 before fixes). This is barrier 1 in
`SERA_V3_PLAN.md`, the author's "grow new representation without human scaffolding" (Schubert cell splitting).

## The mechanism: notice, localize, attach, symbolize, certify
1. **Notice.** The existing alarm (`truth.something_else`) fires on the best law, and the imagination's
   probability over all certifiable laws is spread thin: the best law holds less than 0.2.
2. **Localize** ("where is the gap?"). The leftover force per interval, `y/mu_hat - fbar - F_leader(x, v, t)`, is
   fitted by smooth one-variable curves in x, v and t, and by x·g(v) and v·g(x). The fit that explains the most is
   the gap's address. This extends the `gaps.shape_summary` idea to the "what does it depend on" question.
3. **Attach a cell** (the new dimension). A free-form term g(s) on the implicated variable is added: a
   piecewise-linear curve with K = 8 knots over the scope (new term kind 7, "hat", in `paths`; K linear
   coefficients). The judge treats it as one more term.
   - Its prior price is fixed before data by description length: operator "cell", input, K.
   - The band basis drops the Legendre functions of that variable when a cell is present, the same fix as the
     x·v duplicate (`088cd52`).
   - A cell family can be certified like any other. Its claim is "the force is the leader plus some curve in s,
     within ε where I looked". That is honest and already useful: it predicts, and it names what the force depends on.
4. **Symbolize** (turn the curve into a formula).
   - The certified cell's curve is matched against closed forms from a small expression grammar (depth ≤ 3):
     s, |s|, s², s³, sign, tanh(s/c), exp(−s²/c), sin(ωs), and products with the other variable.
   - Matching is by least squares on the curve (cheap).
   - The best few become new term kind 8, "expression": a short postfix program evaluated in numba. Each gets a
     prior price by its description length. The judge's ledger then decides; the evidence, not the matching, picks.
5. **Certify and keep.**
   - A certified expression becomes a new named piece in SERA's library (for B5).
   - If no formula certifies, the named cell stays in the library as "SERA's own concept, not yet a formula", with its
     curve and scope.
   - A hidden per-object number (L6) is localized in step 2 as a leftover whose best fit changes from object to
     object. It is attached as a per-object coefficient on a term, which the ledger already supports for mass.
     Any mass/size ambiguity is reported, not hidden.

## Judge changes (truth-v2), each test-first
| Change | File | Test that must fail before and pass after |
|---|---|---|
| kind 7 hat term, and kind 8 expression program (numba postfix evaluator) | `paths.py` | readings bit-identical to a direct numpy evaluation; derivatives match central differences |
| terms ('cell', input, K) and ('expr', program); canonical order; codes | `grammar.py` | round trip; the old 3,175 families unchanged; `log_prior` of old families unchanged |
| prior: 0.9 base / 0.1 open, as D9; open terms now include cells and expressions by description length | `grammar.py` | sum of pi over any finite enumerated space ≤ 1; the old open-term prices unchanged up to the new normalization (reported) |
| band basis drops a cell variable's Legendre functions | `truth.py` | band finite and ≤ the old band on cell worlds; unchanged on base worlds (golden) |
| checker: re-derives cell and expression terms from the certificate's own term list, with its own evaluator path | `checker.py` | the forgeries (C11) plus new ones: a wrong program, a wrong K, a cell on the wrong variable |
| golden | `scripts/golden.py` | 0 differences on every truth-v1 world and family |

## Worlds and the gate (tests first, in `tests/sera/test_growth.py` and `scripts/sera_check.py --growth`)
- L6: a per-object "charge" q_k on a position term (c·q_k·x). L8: x·|v|, tanh(v/c), c ∈ {0.3, 0.7, 1.5},
  exp(−x²/c), a three-term law. Each is validated with the same rules: every piece matters, and no certifiable law
  mimics it.
- Noise worlds: nothing to find.
- **Gate:**
  - the missing piece is grown and certified in ≥ 90% of eligible worlds (as a formula or as a named cell);
  - growth in 0 noise worlds;
  - 0 sure-and-wrong (the new pieces are judged by the true force outside the claim, within ε where it looked);
  - the symbolized formula is exactly the true one in ≥ 60% (reported by kind).

## What this does not claim
- A cell is a new representation grown from data. It is not yet a law of nature in a formula.
- Symbolization searches a small, stated grammar of formula pieces. Growing that grammar itself, and turning a
  certified expression into a new primitive, is B5's library. Pieces SERA invents there are counted separately from
  the ones listed here.

## Revision 1 (2026-09-24, after independent review `m1b/reports/REVIEW-B1-B2.md`): every blocker answered
**B4-1: the band must not get laxer.** Only band functions that lie exactly inside the cell's span are dropped.
- An 8-knot piecewise-linear cell on s spans P0(s) and P1(s), and nothing of higher degree. So on a cell in v, only
  P0(x)P0(v) and P0(x)P1(v) may go. P2(v), and every product with x, stay.
- The test is reversed to the right direction:
  - the cell family's band is ≥ the band computed with the cell's columns projected out of the full basis;
  - 0 sure-and-wrong on sharp worlds between knots: tanh(v/0.3), sin(6s), exp(−x²/0.3), each on dev seeds.

**B4-2: knots fixed before any data.** A fixed, pre-registered grid per variable:
- 9 knots on x ∈ [−3, 3], v ∈ [−6, 6] and t ∈ [0, 2];
- constant beyond the end knots.

No part of the cell depends on the readings, so the prequential score stays a true sequential prediction and the rival
e-values keep their anytime validity. (A data-placed grid is permitted only if chosen inside the prequential from past
throws; not used.)

**B4-3: expressions registered before data, with a Kraft-valid prior.**
- The expression grammar, depth ≤ 3, uses these tokens:
  - unary: s, |s|, s², s³, sign(s);
  - functions: tanh(s/c), exp(−s²/c), sin(ωs);
  - binary: product with the other variable.
- Constants c and ω come from fixed grids: c ∈ {0.1, 0.2, 0.3, 0.5, 0.7, 1, 1.5, 2, 3}, ω on grammar.W_GRID.
- The prior is a prefix-free code over whole programs, token by token with a stop token, so Σ π ≤ 1 over the entire
  (infinite) grammar. It is fixed now and never renormalized over the candidates in play.
- The union bound then covers every program the matcher could have picked, so choosing candidates from the data is
  harmless.

**B4-4: truth-v2 is a new judge, and its golden is honest.**
- Golden = 0 differences on the base families (Q, fits, bands, thresholds).
- The open grammar's 0.1 share is split three ways, each pre-registered:
  - 0.05 for truth-v1's open terms, a threshold shift of exactly +log 2 = 0.693 nats for each, reported;
  - 0.03 for cells;
  - 0.02 for expressions.
- T5-style results on v2 are new results, never truth-v1 results.

**B4-5: a cell's nested region and its "wrong".**
- Per-knot intervals at δ/(n·K) (Bonferroni over the K knots), which is valid and simple.
- A cell claim can never equal a formula truth, so its "wrong" is necessarily the ε-surface meaning: the true force
  outside the claim exceeds ε where it looked. This is pre-registered here for B4 only. B1–B3 gates stay on the frozen
  definition.

**B4-6: price per-object numbers.** A charge-like number per object is integrated in the prequential exactly like the
inverse mass, with a Gaussian prior per object and Laplace marginalization. Its evidence is paid, not free.

**B4-7: the author's approval.**
- The author delegated all decisions to development review (in the development session, 2026-09-24 about 19:20).
- independent review cannot see that and asks the author directly. No truth-v2 result counts until the author has confirmed it in
  independent review's session (or here).
- The code is written test-first on branch `sera-v3` in the meantime.

## Revision 2 (after independent review's re-review, `m1b@bb6854f`)
- **R1.** The band functions P0 and P1 of the cell's variable are dropped only when the certificate's scope lies inside
  the knot range. Beyond the end knots the cell is constant, so P1 there is not in its span, and it is kept.
- **R2.** Expression programs are deduplicated by their values on a fixed grid. Programs that equal a base or open
  term (s³, s|s|, sin(1·s), sign(s)·|s|^p on the grid) are excluded. Identical functions have equal evidence and would
  block each other forever.
- **R3.** Resolution: a 9-knot v-grid (1.5 apart) cannot carry tanh(v/0.3). Cells therefore come in priced
  resolutions K ∈ {9, 17, 33}. Each resolution is a separate term, with the description-length price fixed before
  data, and the evidence decides between them. The prior gives the resolutions 9, 17 and 33 the shares 1/2, 1/4 and 1/4
  (Kraft-valid; corrected text, independent review review).

## Revision 3 (independent review, `m1b@31db888`)
- Nested knot grids (9 ⊂ 17 ⊂ 33) are treated as nested families: the finer cell contains the coarser one, so a
  coarse cell's claim does not have to beat the finer cell as a rival. Otherwise the Occam margin could never reach
  the threshold. The grids are chosen to nest exactly.

## Revision 4 (independent review, `m1b@f29cefe`): conditions for the two-stage judgement
1. **Formula-stage rivals are the whole grown formula grammar on the implicated input(s)**, plus the base laws:
   - all 19 pieces on that input (|s|, 9 tanh, 9 bell);
   - for a product address, the pieces on both inputs and the x·g(v) or g(x)·v products.

   Matching only chooses what is claimed. `sera/grow.py`, `rival_formulas`.
2. **The finest curve moves from the rivals into the certificate's checks.** For a claim with a grown formula, the
   33-knot cell on each input the formula depends on is a mandatory nested check. Every knot's interval must hold 0,
   at δ/(n·K). It is never a rival. `truth.curve_checks`; the ledger answers such families on demand.
   - Below the knot spacing (x 0.19, v 0.375, t 0.0625), only the adequacy test guards. The certificate states this
     limit.
3. **A cell certificate is never counted as a formula discovery.** The B4 gate counts formulas and cells separately.
4. **Union over stages:**
   - the rival part is covered by the one Kraft prior over the whole grammar;
   - the band and the nested checks are each at δ;
   - the two stages together are at most 2δ;
   - so P(a wrong "sure" in a world) ≤ α + 2δ.

## Revision 5 (independent review T1, T3): a size bound, not only zero-inside
- **T1: `truth.grown_band` replaces `band_of` for a claim with a grown formula.**
  - One flexible fit: the claim, the smooth basis and the 33-knot cell on each input the claim's pieces use.
  - "What the claim leaves out" at a point is (I − P)·[basis | cells]·θ. P projects onto the claim's own columns over
    the measured points: what the claim's own coefficients can say is not "something else".
  - It is bounded like `band_of`: |value| + sqrt(radius² · var), with radius² = 2(loglik − Q + log(1/δ_eff)). The
    maximum is taken over every reading in a visited D10 cell.
  - The variances come from the SVD of the whitened Jacobian (`likelihood.whitened_jacobian`), never from inverting
    the information matrix. The cell spans the claim's pieces up to interpolation error, so that matrix is
    near-singular.
    - A reverted first draft inverted it and reported 2.9·10⁵ on a clean world.
    - A value with more than a 10⁻⁹ share in the Jacobian's null space (a knot the data never touched) is unbounded.
  - Measured on the T1 worlds (6 objects, 24 throws, ε = 0.2):

    | World | `grown_band` | Old smooth band |
    |---|---|---|
    | Clean bell | 0.151 | 0.21 (refused the clean claim) |
    | Bump 0.1 at x = 1.125 | 0.214 | — |
    | Bump 0.25 at x = 1.125 | 0.359 | — |
    | Bump 0.4 at x = 1.125 | 0.500 | — |

    The worst point sits at the bump (x = 1.124), with the size estimated within 2%.
  - The per-knot nested checks (revision 4, condition 2) stay; they can only refuse.
- **Where the band is measured: at the readings, not at the lattice nodes.**
  - `band_of` measures the smooth basis at the 25×25 lattice nodes of the visited cells.
  - A 33-knot cell is finer than that lattice (x spacing 0.19 against about 0.2). So a node between readings can sit
    in a knot the data never touched, and its value there is unbounded.
  - `grown_band` therefore bounds the leftover wherever the data looked. Between readings, below the sampling, only
    the adequacy test guards.
- **T3: a claim's resolution, stated.**
  - A K-knot cell claim resolves its own knot spacing: v 1.5 / 0.75 / 0.375, x 0.75 / 0.375 / 0.1875, t 0.25 / 0.125
    / 0.0625, for K = 9 / 17 / 33.
  - A grown formula claim is bounded down to the 33-knot spacing inside the knot ranges x [−3, 3], v [−6, 6],
    t [0, 2].
  - Finer than that, or outside those ranges, only the smooth basis and the adequacy test guard.
  - Every B4 report states this.
