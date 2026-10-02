# Decision 11 (proposed): scoped claims, "A up to eps where I looked"

*development review part 2, 2026-09-27. The author approved the direction ("Scoped claims": write the design, have independent review and
independent review it, then restart the program with it). No judge code has been changed. The auto-mode classifier blocked
the first judge edit, so the implementation waits for the author's explicit permission to edit `ccops5/core`.*

## 1. Why: what blocks proofs, measured

On 2026-09-27 the judge's office judged SERA's first 10 claims under the frozen judge (universe-1 audit, Decision 8
band). 2 were proven and 8 refused by the universe audit, each for one rival it could not rule out. Both laws were
fitted on the claim's own throws and compared as forces (`colab-upload/lookalike_probe.py`):

| Claim | Blocking rival | log E (needed) | Largest gap at the visited readings | Largest gap on the whole rail |
|---|---|---|---|---|
| x | sin x + \|x\|^2.9 | −48.8 (11.2) | 0.003 | 8.4 |
| v³ | sin v + tanh(v/2) | 8.4 (11.2) | 0.003 | 241 |
| x³ | sin x + tanh(x/2) | −45.2 (11.2) | 0.001 | 40 |
| sin x | x + \|x\|^2.8 | 2.3 (11.2) | 0.004 | 4.1 |
| x + v³ | v³ + tanh(x/3) | −34.6 (11.2) | 0.003 | 2.5 |
| x + v\|v\| | v\|v\| + tanh(x/2) | −8.9 (11.2) | 0.008 | 10.5 |
| x + x³ | x³ + tanh(x/2) | −6.7 (11.2) | 0.007 | 2.8 |
| x³·sin v | sin v + tanh(v) | −∞ (failed fit) | 51 | 249 |

**7 of 8 blocking rivals are within 0.01 of the claim at every visited reading, against eps = 0.2.**

The rule compares the claim's forecast score Q_A with the rival's *best* likelihood. A rival one term richer that
bends to mimic A within the visited region always fits as well or better, so log E cannot reach the threshold. It is
not a lack of data. The dictionary's 57 bends, 551 bend products and 234 near-copy powers and drives supply such a
mimic for almost every simple law. Today's "sure" promises "the law is exactly A", which the evidence on a finite
rail cannot support.

## 2. The claim

A scoped "sure" says: **the true force f is within eps of some member of family A at every reading in the visited
cells** (the D10 scope where the band already holds):

  C(A, eps, S): exists c such that |f(p) − F_A,c(p)| <= eps for every p in S.

This is the promise Decision 8's band already makes for anything outside A's span. The P2 gate's definitions already
count such a claim as right ("proven, surface": the true force the claim left out is within eps wherever the
certificate speaks). The stricter frozen flag (`core_check.wrong`) still marks a claim that is not the exact law, and
is reported beside it as today.

## 3. What must be ruled out, and why the test stays valid

A law (family B, coefficients θ, masses μ) refutes C only if, for every c, max over p in S of |F_B,θ(p) − F_A,c(p)| >
eps. Call that set V_B. The judge must rule out V_B for every family B the audit covers, at the same threshold.

**The e-value.** q_A / sup over V_B of p_B,θ is an e-value against every law in V_B, by the same universal-inference
argument as today's rule, which uses the sup over all of B.

**A computable superset.** Let ĉ be A's best fit, and W_B = {θ : max_p |F_B,θ(p) − F_A,ĉ(p)| >= eps}. Every θ in V_B
is more than eps away from *every* member of A, so in particular from ĉ; hence V_B ⊆ W_B and sup_{W_B} >= sup_{V_B}.
Using sup over W_B in the denominator is therefore conservative: valid.

**Computing sup over W_B.** W_B is the union over points p and signs s of the half-spaces
H(p, s) = {θ : s (ψ(p) · θ − F_A(p)) >= eps}, which are linear in the coefficients, so sup_{W_B} = max over (p, s)
of sup over H(p, s).
1. If B's best fit already lies in W_B (its gap is at least eps somewhere in S), sup_{W_B} is B's plain best fit: the
   rule is exactly today's.
2. Otherwise, B is a look-alike. For each candidate (p, s), the judge fits B with the one-sided penalty
   lam · max(0, b − a · θ)², where a = s ψ(p) and b = s F_A(p) + eps, and records the likelihood alone at the
   penalized optimum θ_lam.

   **Lemma.** If θ_c maximizes the likelihood L on H(p, s), then L(θ_lam) >= L(θ_c): θ_c pays no penalty, so
   P(θ_lam) >= P(θ_c) = L(θ_c), and L >= P everywhere. So the recorded value is never below the constrained sup, for
   any lam. The bound is conservative, and a larger lam only tightens it.
3. **Which (p, s).** There are hundreds of candidate points. They are ranked by the quadratic approximation of B's
   likelihood around its best fit. The cost of pushing the force at p by the needed amount
   d = eps − s (ψ(p) · θ̂ − F_A(p)) is d² / (2 ψ(p)ᵀ Σ ψ(p)), with Σ the coefficient block of the fit's covariance.
   The K = 4 cheapest are fitted exactly, and the largest likelihood is taken.

   **This ranking is a new premise, T**, assumed like Decision 8's premise Q: the quadratic approximation ranks
   correctly enough that the exact constrained sup is within the fitted candidates. Measured, not proven; the
   validation below measures it.
4. **Fail closed.** A penalized fit that is not ok, not converged, or not finite makes the rival not ruled out, as
   today (T2-A/B). So does a non-finite Σ, or a point where ψᵀΣψ is not positive.

The value recorded for B is then log E = Q_A − sup_{W_B}, compared with the same D9 threshold.

## 4. Where it applies (the judge's steps)

| Step | Today | Scoped |
|---|---|---|
| In-space rivals | log E = Q_A − L(B̂); the screen Q_B > Q_A − thr fails the claim without fitting | the same, then a rival that fails and is a look-alike gets the W_B bound. The Q-screen is off, because a constrained sup can be below Q_B |
| Universe audit (supersets and members) | a node is covered when Q_A − sup_fit(U) >= thr, else split | a node that fails and whose best fit (refitted without the E2 early stop) is within eps of A gets the W_U bound before splitting. Nesting still holds: a member's W lies inside its superset's W when its missing terms are 0 |
| Wide rivals (the pre-certificate, grown claims) | as the audit | the same change |
| Nested intervals, adequacy, band, scope | unchanged | unchanged |

## 5. The certificate, the premise ledger, the checker

- **New certificate fields:**
  - `claim` = 'scoped' (policy `CCOPS5_CLAIM`, default 'exact' until reviewed);
  - `lookalikes` = {rival: (its gap at its best fit, the fitted candidate (p, s), the recorded bound)};
  - the scope says "A up to eps at the visited readings".
- **Premise ledger:** premise T is added (§3.3). S reads "every claimable law that differs from A by more than eps at
  a visited reading was ruled out (cells excepted), given U and T".
- **The checker:**
  - requires the policy claim kind;
  - re-runs `certify` and compares `lookalikes` as it compares rivals;
  - and, independently, re-derives each look-alike's gap at its best fit from its own column formulas
    (`checker._column_np`, not `paths.term_t`), refusing if a rival recorded as a look-alike is not within eps
    (the pattern of `band_reason`).

## 6. Code (after permission)

| File | Change |
|---|---|
| `ccops5/core/likelihood.py` | an optional `penalty=(a, b, lam)` through `fit`, `_fit`, `_fit_knocks` and `sup_fit`; the returned loglik excludes the penalty. Behaviour without a penalty is unchanged (the golden tests must pass bit for bit) |
| `ccops5/core/truth.py` | the `CLAIM` policy; the scope points (`grown_band`'s visited readings); force columns by `paths.term_t`; `scoped_sup`; the three places of §4; the certificate fields; premise T |
| `ccops5/core/checker.py` | §5 |
| `sera/` | nothing required (the mind reads `cert.rivals` as today); narration may name look-alikes ("… agrees with it within 0.2 wherever I looked") |

## 7. Validation before the program restarts (dev only)

1. **The existing core suite** passes with `CCOPS5_CLAIM=exact` (nothing changes by default).
2. **The office's 8 refused claims** re-certified with `scoped`. Expected: the 7 look-alikes pass the audit (if T
   holds), and the real rival (gap 51) is still refused; every accepted certificate is re-derived by the checker.
3. **Planted violations:** dev worlds whose true force is a look-alike that differs from the simple law by 2·eps
   *inside* the visited cells (built from the refused pairs, scaled). A scoped claim of the simple law must be refused
   in every one. **The bar: 0 sure-and-wrong.**
4. **Premise T measured:** in those worlds, the exact constrained sup found over *all* candidate points (brute force)
   against the top-4 value. Report the largest miss.
5. **Then the program restarts** from Stage 0's yardstick with `CCOPS5_CLAIM=scoped`. The run already going under the
   exact claim is kept as the baseline, and every tripwire stays on.

## 8. Questions for the reviewers (independent review, reviewer)

1. Is W_B ⊇ V_B enough, or should the claim fix c at ĉ explicitly (a slightly weaker, simpler claim)?
2. The penalized-optimum lemma assumes the global penalized optimum. Is the local-optimum risk the same as today's
   premise U, or larger near the constraint?
3. K = 4 candidates by the quadratic ranking: acceptable as an assumed premise T, with its measurement (§7.4)?
4. The nested-interval step still demands "0 inside" for extra ideas. Under scoped semantics, should an extra idea
   whose effect is below eps at every visited reading pass (the band's job), or stay as today?
5. D10 scope: S is the readings in the visited cells, where the band holds. Should the claim also bound the lattice
   between readings (premise L)?
