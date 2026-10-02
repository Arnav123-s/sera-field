# Decisions 12 and 13: SERA's own shapes and functional claims (plan revision 6)

*development review, 2026-09-27. The author granted permission for judge edits on 2026-09-27. Both decisions are behind
policies (`CCOPS5_SHAPES=library`, `CCOPS5_CLAIM=functional`); with the defaults, every earlier certificate is unchanged
(tests: `tests/core/test_shapes_functional.py`; the judge's older tests pass: 69 of 69 in the fast set). the reviewer's review is
pending. Until then, a claim made under these policies counts only inside the revision-6 program, where the observer's
tripwire (an accepted answer wrong by more than eps) guards every world.*

## Why

The author's rule (2026-09-27): SERA gets **no predefined set of words, sentences or formulas**. It is taught, and it
invents. So SERA's laws are made of its own concepts - free curves it shaped from measurements, expressions of its
language, and the concepts it made from earlier proofs - never terms of the judge's dictionary. Two things follow:

1. The judge must be able to certify a claim in SERA's language (Decision 12: its invented shapes).
2. The judge's own dictionary must not block SERA. The exact claim ("the law is family A, and no other family")
   needs every rival ruled out. But a SERA shape that draws "a straight line in position" is a look-alike of the
   dictionary's spring: they are the same force, so neither can ever beat the other. This is the look-alike and
   near-copy flaw measured on 2026-09-27: 7 of 8 audit refusals were look-alikes within 0.01, and 234 of 259 open
   terms are near-copies. Decision 13 claims the force, not the name.

## Decision 12: SERA's invented shapes (tied cells)

- **The term** is ('shape', input, K, n, knots): the n-th shape SERA invented, on the K-knot grid of one input.
  - Its force is a strength times sum_k knots_k hat_k(input). The simulator runs the cell's own K hats (no new
    kernel).
  - `likelihood.Model.tie` maps the one strength to the K codes' coefficients. The Jacobian is the chain rule
    (J_codes x tie, exact). Every site that simulated with a model's coefficients now goes through
    `Model.codes_coef`.
- **The prior.** Under `library`, the cells' 0.03 of the prior becomes 0.02, and the shapes get 0.01. The n-th
  shape's share is 6 / (pi^2 n^2) of that (the e-LOND sequence), so Kraft holds over every shape SERA will ever
  invent.
  - The library is fixed before each world (`grammar.use_library`). Which curve became the n-th shape depends only on
    earlier worlds, so the prior is fixed before this world's data (premise L, proven by construction).
  - A shape not in the library is never claimable.
- **Around it:**
  - a cell whose grid holds the shape's grid contains it;
  - a cell on the same input is collinear with it (left out of a space);
  - the universe audit includes the library's shapes;
  - wide rivals and curve checks treat a shape like a grown piece.
- **The checker** evaluates each shape from its own formula (knots times its own hats) and compares the library's
  digest with the certificate's.

## Decision 13: functional claims

**The claim.** "The force is this law, with its fitted strengths, up to eps at every reading in the visited cells;
nothing is said beyond them."

**Accepted when:**
1. the law does not misfit: the adequacy test, unchanged (per object, against the share knocks explain);
2. the band is at most eps.
   - The band is the flexible fit of the law, plus the smooth basis, plus a 33-knot free curve on every input the law
     uses (less what the law already spans there, see below).
   - It bounds, at every visited reading, what the law leaves out: (I - P)[basis | curves] theta, with P the
     projection onto the law's own columns at those readings, and theta in the confidence set
     {loglik >= Q_law - log(1 / delta_eff)}.
   - That set is valid for any predictable forecast Q_law: the universal-inference argument of Decision 8.

**The price of choosing the law after seeing the data:**
- delta_eff = delta x pi_F(law), a union bound over SERA's claim language.
- pi_F: the empty law 0.1; one part 0.45; two parts on different inputs 0.45.
- A part's code probability:
  - a free curve: 1/2 x 1/3 per input x the grid's weight;
  - a library shape: 1/2 x 6 / (pi^2 n^2).

**No rivals.** A law within eps of it at the visited readings is as right as it. A law farther away is outside the
band (under premise F).

**Premises** (the checker requires exactly this ledger):

| Premise | Status | Meaning |
|---|---|---|
| P | proven | every push and every claim uses only the past |
| M | measured or assumed | the knock model, as before |
| N | measured | the band's reference forecast |
| L | proven | the library is fixed before the world (under `library`) |
| S | not needed | a functional claim names no rivals |
| F | assumed | anything else lies in the span of the band basis: smooth in position and speed up to degree 2, and a 33-knot free curve on every input the law uses. Beyond it only the adequacy test guards: a force in time, or a sharp one elsewhere |
| Q | assumed | the quadratic approximation of the flexible fit is taken as one-sided; the band holds at visited readings, not between them |
| C | computed | what the claim says |

**What it buys:**
- no universe audit (about 1,100 s of CPU per proof before);
- no look-alike or near-copy blocking;
- one claim language for everything SERA makes.

**What it costs:** the claim is weaker. "Up to eps where I looked" is not "the law is exactly this family". Two
different laws can both be proven (a duality SERA then keeps as a question).

## The checker's numerics (found and fixed on 2026-09-27)

The independent re-derivation of a functional claim's band (finite-difference Jacobian, QR projection, other column
formulas) refused SERA's first physics proof: a drag as a 9-knot free curve in speed, band 0.043 by the judge and
238,155 by the checker. Diagnostics (`colab-upload/diag_band*.py`):
1. The finite-difference Jacobian matches the exact one to 1e-9 per column (not the fault).
2. The exact Jacobian has a clean gap: 8 directions below 1e-15 (a free curve's knots no throw reached, and two
   combinations at the edge of where the throws went) and none between 1e-15 and 1e-5. The band's content in those 8
   is 8.6e-16 (none).
3. **The fault:** the checker projected out the claim's span with an unpivoted QR. A claim column no reading touches
   (a knot nothing reached) got an arbitrary direction, and dropping it took part of the claim's real span with it.
   The leftover claim content looked like band content in near-null directions.
   - **Fixed** with a pivoted QR (the zero columns go last and are dropped whole).
   - The old least-squares path then gives 0.04346 against the judge's 0.04319.

**Also added**, for a functional claim only:
- the band's check curve holds only what the claim does not already span:
  - beside a K-knot claim cell, the 33-grid's hats between its knots (a hierarchical basis of the same curves);
  - beside a shape, every hat but its largest;
- the checker reads which combinations the paths never depend on from the exact Jacobian (after checking it against
  the finite differences column by column, to 1e-6), requires the band's content there to be nil (1e-9, else it fails
  closed), and re-derives the band from the finite differences alone on the rest, cut at their precision (1e-9).

Result: 0.043187348 against the judge's 0.043186735; the checker accepts.

## Review questions for reviewer

1. Is delta x pi_F(law) the right price for a law SERA chooses after seeing the data, given that the band's set is
   universal inference with the law's own forecast as the reference?
2. Premise F's span (degree-2 smooth basis plus a 33-knot curve on the law's inputs): is an input the law does not
   use adequately covered by the smooth basis and the adequacy test? (A sharp force in an unused input can hide.)
3. The checker reads the paths' null space from the exact Jacobian. It first checks that Jacobian against finite
   differences column by column (1e-6). Is that independent enough?
4. Decision 12: is fixing the library before each world (in the program, and carried in the office's jobs) enough for
   premise L?
