# OP1 — An honest "sure" when the truth may lie outside every idea the mind can form

*the development working note, 2026-09-22. Status: a candidate answer. Literature checks are pending (dives J2 and
X6), and it is not yet tested. Anything marked (check) is not yet confirmed from the source.*

## The problem in plain words

- **The failure, seen in every project so far:** the right idea was missing from the menu, and the mind was
  sure of a wrong one.
  - SCFE-006: error 0.494 → 0.674, with the wrong hypotheses agreeing with each other.
  - v18: more than 95% sure of the wrong type in 92.2% of episodes.
  - The ccops5 menu robot: 7 of its 7 "sure" claims were wrong.
- **What you asked for:** "sure" should mean the mind can prove it. Otherwise it is unsure.
- **Why it is hard:** the world never lets us check every possible law.

## What a proof can honestly say: a certificate in four parts

**The setting.**
- Throws j = 1, 2, … are independent units. Each throw is a short path of measurements.
- An *idea* is a family of laws with free numbers, for example "spring + drag", with θ free.
- The mind's idea space S_K holds every idea up to size K.

**Part 1: every rival inside the space is ruled out.**
- **The evidence.** For a candidate law A and a rival family B that does not contain A:

  E_t(A : B) = ∏_{j ≤ t} q_A(y_j | y_{<j}) / sup_θ ∏_{j ≤ t} p_B(y_j ; θ)

  - The numerator predicts each throw only from **earlier** throws. It is *prequential*.
  - The denominator is B's best possible fit to **all** throws so far.
- **The guarantee.** Suppose B is in fact the true family. Then E_t(A : B) is at most a test martingale, and
  by Ville's inequality P(ever E_t ≥ 1/α) ≤ α. This is the sequential form of universal inference
  (Wasserman, Ramdas & Balakrishnan 2020). Their abstract says the method "can also be run sequentially to
  yield anytime-valid p-values and confidence sequences"; the exact theorem is still to check.
- **Why the guarantee survives stopping.** It holds however the mind chooses when to stop, which throws to
  make, and which rivals to test.
- **Many rivals: corrected 2026-09-22.** The earlier claim was "no penalty for many rivals". It holds only
  for a claim A fixed in advance.
  - A mind picks A after seeing the data. Then the event "some wrong A beats the true family" is a union
    over up to |S_K| claims.
  - Each has probability ≤ α, so the total is ≤ |S_K|·α.
  - The fix is the threshold log(|S_K|/α). With 67 families and α = 10⁻³ it is 11.1 instead of 6.9, a
    modest price. It is built into `ccops5/core/truth.py`.
- **What the lab does today, and why it falls short.**
  - `ballmind.retrial` is leave-one-out: it uses later throws, and the wind is fitted on all throws.
  - `relentless.evidence` is in-sample.
  - Neither is an e-process, so neither carries this guarantee.

**Part 2: rivals that contain A are bounded, not rejected.**
- A rival B that contains A (A plus an extra term such as wind) can never be rejected when A is true. The
  lab met this as "a knob that is off can never be decisively ruled out".
- Instead the certificate gives an anytime-valid bound on the extra term's numbers, for example "any wind
  lies in [−0.4, 0.4]". Laws in our grammar are linear in their numbers, so self-normalized martingale
  bounds give ellipsoids that hold at all times with probability 1 − δ. (Abbasi-Yadkori, Pál & Szepesvári
  2011, arXiv 1102.2670; verified.) Ball v2 already does this in spirit.

**Part 3: anything outside the space is bounded.**
- Write the truth as f* = f_A + r, where r is "something else" outside S_K.
- **The assumption:** r is smooth, with RKHS norm ‖r‖_H ≤ R for a stated kernel.
- **The bound:** time-uniform confidence bands for r follow from kernel bandit theory (Chowdhury & Gopalan
  2017, arXiv 1704.00445; verified). The certificate says "any unmodelled effect is within ±ε(x) over the scope".
- This is the honest form of "no hint is left": something else may exist, but if it is smooth it is small.
- **The open part:** choosing R and the kernel honestly. Either would be learned from other worlds, or
  stated and tested.

**Part 4: scope.**
- Claims hold only for the conditions actually probed, such as the range of speeds, sizes and places.
- Outside that scope the certificate says "untested". That is how Newton's laws should have been stated.

**Error budget.** P(the certificate is wrong) ≤ α (part 1) + δ (parts 2 and 3), provided that:
1. the noise model is right;
2. the truth is some family in S_K plus a residual r with ‖r‖_H ≤ R;
3. the scope holds.

Each assumption is written into the certificate. A small checker can re-verify parts 1–4 from the stored
data: recompute the products, the bounds and the scope.

## The noise model (needed for part 1)
- Accelerations taken by central differences of noisy positions share noise. Their covariance, in units of
  σ²/dt⁴, is 6 on the diagonal, −4 one step apart, and +1 two steps apart.
- **Fix: whole-throw likelihoods.**
  - Each throw's joint likelihood uses this banded covariance, or better, fits the path to the positions
    directly.
  - Throws stay independent, so the prequential product is over throws.
  - This also removes the "evidence too cautious" problem the lab noted, where fits sat within 0.6 SE of the
    truth.

## Growing the space without breaking old certificates
- **Old certificates stay valid** for the space they name. When S_K grows to S_{K+1}:
  - re-test each old claim against the new rivals, using the stored throws in their original order;
  - the numerator's predictions do not depend on which rivals are tested, so each new test is still valid.
- **The genuinely open part: whether the space itself is adequate.** Our answer is part 3's residual band,
  plus a standing "something else" alarm. The alarm is a GP rival's e-process against A:
  - if it grows, the space is missing something, and growth (job 5) starts;
  - if it stays small, the bound in part 3 is what the mind reports.

## What to test (T4, in M1)
- **Pure-noise and look-alike worlds:** sure-and-wrong must be 0 at α = 10⁻³ over all fresh lives.
- **The omitted-mechanism replay** (true drag outside the space): the mind must not say "sure". The GP alarm
  must fire, or the residual band must honestly cover the missing term.
- **Price:** throws needed until "sure", compared with the current rules. The certificate is stricter
  (roughly 1/α = 1000 to 1 per rival), so it will need more throws. That trade-off is measured, not assumed.
- **The checker:** it re-computes the certificate from stored data, and rejects a set of forged certificates.

## Still open after this note
- An honest choice of R and the kernel.
- What happens when the noise model itself is wrong. We will test the noise model on held-out throws.
- Claims over continuous "scope" regions in higher dimensions.
- Whether a certificate this strict leaves the mind "unsure" far too often in richer worlds.

## First evidence: a simulation (`research/op1_sim.py`, 2026-09-22)

**The setup.**
- A 1-D drag world: a = law(v) + noise, σ = 0.05, speeds 0.2–1.0, where linear and quadratic drag look alike.
- Two ideas: A = linear drag, B = quadratic drag.
- Three possible truths: A, B, or M = v^1.5, which lies outside both ideas.
- Each rule checks after every sample and stops at its first "sure". That is optional stopping, as a real mind
  does.

**Part 1 only**: 20,000 lives per truth, up to 200 samples.

| Truth | Rule | Sure and **wrong** | Sure and right | Median samples |
|---|---|---|---|---|
| A | in-sample (form of `relentless.evidence`, threshold 9) | 0.13% | 99.9% | 3 |
| A | leave-one-out (form of `ballmind.retrial`) | 3.0% | 97.0% | 2 |
| A | e-process (α = 10⁻³) | **0** | 100% | 19 |
| B | in-sample | 0.28% | 99.7% | 4 |
| B | leave-one-out | 3.8% | 96.2% | 3 |
| B | e-process | **0** | 99.9% | 18 |
| M | in-sample | **100%** | 0 | 6 |
| M | leave-one-out | **100%** | 0 | 3 |
| M | e-process | **49.8%** | 0 | 97 |

**The full certificate**: part 1 plus part 3, a time-uniform band from the flexible family {v, v², v³},
checked every 20 samples, 2,000 lives per truth.

| Tolerance ε | Truth | Sure and wrong | Sure and right | Median samples |
|---|---|---|---|---|
| 0.10 | A | 0 | 100% | 200 |
| 0.10 | B | 0 | 100% | 200 |
| 0.10 | M | **0** (never sure: "something else is here") | 0 | – |
| 0.05 | A | 0 | 100% | 820 |
| 0.05 | B | 0 | 100% | 820 |
| 0.05 | M | **0** | 0 | – |

**What it shows**
1. **The current rules' form is fooled by optional stopping.**
   - It is fooled rarely when the truth is among the ideas (0.1–4%).
   - It is fooled **always** when the truth lies outside them. This is the omitted-mechanism failure seen in
     every project.
2. **The e-process alone fixes the first case but not the second:** about 50% sure and wrong when the truth
   is outside every idea.
3. **The full certificate is never sure and wrong in any case.** When the truth is outside its ideas it says
   "something else is here", which is where growth (OP3) should start.
4. **The price is samples:** 200 at ε = 0.1 and 820 at ε = 0.05, against 3–19 before. So the tolerance ε
   must be part of every claim ("sure within ±ε"), and tightened with more data.

**Limits.**
- It is a 1-D toy with known σ and independent noise.
- It assumes the truth lies in the flexible family up to a negligible remainder.
- The **ccops5 robots carry extra guards** that this simulation leaves out: WORTH, edge tests and final
  audits. Their real false-sure rates in their own worlds were 0 in most fresh runs, but not all (ball v1:
  2 of 10).
- The constants matter. A prior-norm term √λ·S = 0.5 once made the band too wide ever to certify; the run
  above uses λ = 10⁻⁴ and S = 2.
