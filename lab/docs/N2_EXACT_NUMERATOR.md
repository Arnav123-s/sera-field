# N-2: an exactly normalized numerator (truth-v2, Decision 7 draft; A, 2026-09-25)

Status: **design; tests first; not in use.** Needs an independent review and the author's confirmation.

## Why

Every "sure" rests on the e-value log E = Q_A - sup_theta log p_B(data | theta). It is anytime-valid only if each
factor of the numerator, q_i(y) = p_A(y_i | y_<i, push_i), is a **proper conditional density**: it must integrate to
at most 1 over the throw's readings y, given the past (research R3, card A; Wasserman, Ramdas and Balakrishnan).

Today `likelihood.step` returns a **Laplace approximation** of the integral of p(y | theta) N(theta; m, C) over theta,
with the mode theta-hat found *after* seeing y:
- it is exact for laws whose readings are linear in the numbers;
- for our nonlinear paths it is unproven. If it integrates above 1, log E is inflated and the D9 bound
  P(ever sure and wrong) <= alpha is not guaranteed.

N-1 (independent review) measures the size of the error. N-2 removes the question.

## Principle

Two facts, each one line of proof (Lean targets for P6):
1. **Any proper prior works.** Any distribution over the numbers, chosen from the past alone, gives a numerator whose
   predictive integrates to exactly 1 (Fubini). It need not be the Bayesian posterior; closeness only buys power.
2. **Any subset of a normalized mixture is sub-normalized.** If sum_k w_k <= 1 and each component is a normalized
   density, then evaluating ANY subset S(y), even one chosen after seeing y, gives q(y) <= a normalized density.
   Dropping components only lowers q, so it costs power, never validity.

## Construction: a lattice prior (for the claim, of dimension d = n_coef + 1)

For throw i in situation s, with past-only Gaussian N(m, C) over theta = (coef, mu_s):
- For a new object, one mixture component per CRP option, as today; each option's prior is proper and past-only.
- **The frame (past-only).** Take C = L L^T, J0 = the whitened Jacobian at m, and A = L^T J0^T J0 L, the predicted
  information in whitened units. Eigen-decompose A = R diag(lam) R^T. In z = R^T L^-1 (theta - m) the prior is
  exactly N(0, I), since a rotation keeps it standard.
- **The cells (past-only).** An axis-aligned grid in z with spacing s_j = SPACING / sqrt(1 + lam_j) on axis j (the
  forecast posterior's width). Cell k is the box prod_j [(k_j - 1/2) s_j, (k_j + 1/2) s_j). The cells partition R^d, so
  their prior masses w_k = prod_j [Phi((k_j + 1/2) s_j) - Phi((k_j - 1/2) s_j)] sum to exactly 1 (log-space: `log_ndtr`
  differences).
- **The points.** theta_k = m + L R (k s), each cell's centre.
- **The numerator.**

  q(y) = (1 - RHO) * sum over k in S(y) of w_k N(y; f(theta_k), Sigma) + RHO * b(y).

  S(y) is the grid points within radius R_EVAL of theta-hat(y) (today's Laplace mode) in the metric of the actual
  posterior H(theta-hat). At most MAX_POINTS points, nearest first.
- **Numerics.** Every component is an exact Gaussian in y. The simulation is the judge's own compiled RK4, the same
  f the rival's likelihood uses. A float underflow drops a component, which is valid.

**Power:** with spacing at most the posterior's width, the lattice sum of exp(-|z - z_hat|^2 / 2) w_k is within a
tiny factor of the integral (Poisson summation), so q_N2 is close to the Laplace q wherever the Laplace q is right.
The losses are:
- **Truncation:** about P(chi2_d > R_EVAL^2), which is 0.04 at d = 2 and 0.1 at d = 3 for R_EVAL = 2.5.
- **Quantization:** when the actual posterior is much narrower than the forecast (nonlinear first throws). Guard: a
  mixture over NRES spacings (factors of 10, weight 1/NRES each; past-only) for a throw whose forecast is poor (a new
  object, or tr(C) above a past-only cut). It costs log NRES nats on those throws only.

## Where it is used (cost)

Only where validity is claimed:
- `truth.certify`: the claim's Q_A for the rival e-values and adequacy;
- the grown band's flexible fit (`q_f` in `grown_band` / `band_of`). This fit has d >> 4, where a lattice is
  infeasible. **N-2b:** the single Gaussian linearized at the past mean m, N(y; f(m), Sigma + J0 C J0^T), exact in
  any d, used when a past-only nonlinearity check passes; otherwise the band is "not shown" (refused, which is
  valid).
- The independent checker recomputes both.

The ledger's running Laplace Q is kept for ranking laws, choosing pushes and grading imaginations. Adaptive choices
may use anything; only the certified numerator must be exact. Cost: one family, 40 throws, at most MAX_POINTS
simulations each: about 1-3 s per certificate.

## Constants (fixed before any measurement)

SPACING = 0.7, R_EVAL = 3.5, MAX_POINTS = 1024, NRES = 3 (spacings x1, x0.1, x0.01).

Changed once, on the toy only (2026-09-25, before any world). The first choice, R_EVAL = 2.5 with MAX_POINTS = 512,
kept 0.869 of the mass, against my bar of 0.9 written before the run. On the toy (2 numbers, 2 readings, sigma 0.3,
a non-Gaussian posterior):

| numerator | integral over y |
|---|---|
| full lattice mixture | 0.99999 (the partition is exact) |
| Laplace (today's) | 0.972 |
| lattice, R_EVAL = 2.5 / 3.0 / 3.5 | 0.869 / 0.915 / 0.939 |

The remaining loss comes from guiding by a Gaussian ellipse around a Gauss-Newton mode where the posterior is not
Gaussian. The judge's posteriors (sigma = 1e-3) are far tighter.

## Tests (written before the code)

1. **Partition:** over a window of +-40 sd on every axis, the cell masses sum to 1 within 1e-12 (d = 1..4, rotated
   frames). Every component's density integrates to 1 (closed form).
2. **Sub-normalized by construction:** on a nonlinear toy (1 coefficient + mu, 3 readings, so the integral over y is
   computable by quadrature), the integral of q_N2 over y is <= 1 + 1e-9. The same toy measures the Laplace
   numerator's integral (N-1's question in miniature).
3. **Agreement:** on saved B3 worlds (the claim's throws), the median per-throw |log q_N2 - log q_Laplace| < 0.1 nat.
   Per-world Q_A differences are reported; a decision changed by N-2 is listed, never hidden.
4. **Checker:** the independent re-derivation matches; a certificate whose numerator was computed by Laplace is
   refused once N-2 is the rule.
5. **Power (reported, not a gate):** B3 dev worlds re-certified under N-2: sure / right / sure-and-wrong against
   Laplace.

## Open (for independent review)

- Is the Laplace mode, used only to pick S(y), a safe choice? It may depend on y by fact 2.
- Must the CRP option weights stay fixed before y? They do today (counts from past situations).
- N-2b's nonlinearity check: which past-only statistic, and what threshold?
- Rival denominators (R3's U): a separate track (U-1); this note does not touch them.

## independent review (m1b e2564db, 2026-09-25): valid by construction; adopted

- **Validity, stated generally:** any past-only mixture of densities normalized in y, with sum w <= 1, integrates to
  at most 1, and so does any subset chosen after seeing y. Frame, spacing, R_EVAL and MAX_POINTS affect power only.
  - The Laplace-mode guide is safe; it is made deterministic so the checker reproduces it.
  - The CRP option weights are past-only; summing or taking the max over options are both valid.
  - N-2b is normalized in any d, so its nonlinearity check is only a fast path, not a validity condition.
- **S-1:** adequacy uses no Q, so it is removed from the scope.
- **S-2:** the nested intervals keep Laplace. An inflated Q there narrows A + psi's interval, which makes "an extra
  term is needed" more likely, so it errs on the safe side. N-2 goes to the claim's Q_A and the band's q_f only.
- **P-1:** NRES at 1/3 each would cost log 3 = 1.1 nats per new-object throw, about 8.8 per world against a threshold
  of 11.2. The weights become skewed and past-only (0.9 / 0.08 / 0.02, costing 0.1 nat), or a past-only trigger
  replaces them, decided by test 5.
- **P-2 (to test beside the full lattice):** a 1-D lattice on mu (normal-CDF masses), times a Gaussian over the
  coefficients linearized at each mu_j (`linearized_logq`). Every component is normalized, so it is valid in any d:
  one construction for the claim and the band's flexible fit, with no MAX_POINTS and no truncation in d.
- **P-3:** the per-throw median is too weak (0.1 nat x 40 throws = 4 nats). Test 5 reports the per-world
  distribution of the change in Q_A and is the gate.
- **Tests added:** T-a (an adversarially chosen subset still integrates to at most 1); T-b (N-2b integrates to 1 on
  the nonlinear toy).
