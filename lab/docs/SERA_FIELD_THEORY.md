# SERA Field Theory, v1.1: one field, one update rule, and a judge outside it

*development review, 2026-09-25 (afternoon). This replaces v1 (`a9aa251`). It follows plan revisions 3 and 3.1 and folds in
three reviews:*
- independent review's `m1b/reports/REVIEW-FIELD-THEORY.md` (F1–F12, A1–A2, open questions, the playroom addendum, and the independent review's five
  conditions on the one-field mapping);
- the reviewer's formula check, `(review notes, not published)`;
- the reviewer's Field-dynamics dive, `(review notes, not published)`.

Appendix C maps every review item to its fix.

**The author's two directions this version answers (2026-09-25):**
1. "Don't simply give SERA a box of numbers… teach it actual words and actual things, and let it plan on its own…
   let it decide how it wants to play and imagine, not that it can only do this or that."
2. "Each thing, the imagination etc., must be interconnected behaviour of the field, done by the field, not forced or
   propped up… like in the brain everything is the same and interconnected, but still divided into parts that flow into
   each other and influence each other, like entanglement and coherence in fields."

**Labels:**
- **[proven here]:** a derivation in this document;
- **[S4 §x]:** proven in the independent review's study S4;
- **[exact]:** computed without approximation, given the stated model;
- **[approximation]:** a named approximation, with how it is checked;
- **[decision rule]:** a choice on top of the model, with no optimality claim;
- **[to measure]:** a pre-registered test.

---

## The idea in one paragraph

SERA's Field is **one joint probability model** over everything it is unsure of: which law holds, its numbers, each
object's hidden mass and knocks, what each word means, and what will happen next. There is **one update rule**:
condition on what was just observed (a throw, a caretaker's sentence), and carry a faded summary of past worlds as the
next world's prior.

Every faculty is a *question asked of that same model*:
- **imagining** is sampling it;
- **curiosity** is the information an action would give about it;
- **"not regrowing a dead branch"** is what conditioning does to a refuted law;
- **a fading failure** is the faded prior;
- **a word's meaning** is a variable in it, updated by the same rule as a law;
- **speaking** is reading it out.

None of these is a separate machine. Change one part, for example teach a word, and every other part moves through the
shared joint. That is the exact counterpart of the author's "entanglement": the joint does not factorize.

Two things stay **outside** on purpose:
- **the judge,** the voice of the world's evidence, which alone makes "sure";
- **a small guaranteed floor on exploration,** so SERA can never forget a law completely (the relentless seed-31
  lesson).

---

## Part I. The field

### 1. Objects and notation

**The world and its data.**
- A world has objects k = 1..K with hidden inverse masses μ_k, per-object knock states z_k ∈ {clean, knocked}, and a
  hidden law G.
- A throw t acts on object k_t with a push program a_t and returns `Y_t ∈ ℝ^82`.
- The history is `D_t = (a_s, k_s, Y_s)_{s≤t}`. Caretaker sentences add `S_t` (Part IV).

**The law space 𝓛 (from `grammar.log_prior`, verified by B and here):**

| Version | What is claimable | Laws | Σπ₀ |
|---|---|---|---|
| truth-v1 | base families (≤ 2 of the 11 ideas) plus one of 259 open terms, alone or with one idea | 3,175 | 0.95 |
| truth-v2 | plus 57 grown pieces and 551 piece products | 10,471 | – |
| | plus the 9 cells (the families without collinear columns) | 10,564 | 0.9977 |

- π₀ is sub-normalized (Σ ≤ 1), which the union bound allows.
- The smallest prior is log π₀ = −14.0; the largest threshold, log(1/(α·π₀)), is 20.9 nats.

**Two priors, never mixed:**
- **π_j:** the judge's prior. It is D12's frozen snapshot, `π_j = 0.8·π₀ + 0.2·mean_F K_F`, hashed at world start and
  rebuilt by the checker (A1; B condition 2).
- **p_F:** the field's prior for the same world, learned from past worlds (§5). It steers belief and search; it never
  enters a threshold.

### 2. The joint and its one update rule

**The joint model** for one world, given the actions:

```
p(h, θ, z, m, Y, S | a) = p_F(h | c) · p(θ | h) · Π_k p(z_k) · Π_t p_h(Y_t | θ, z_{k_t}, a_t, k_t)
                          · Π_w p(m_w) · Π_j p(s_j | m, h, θ, events)
```

Its parts:
- `c` is the world's context, the teacher's table, encoded by a frozen encoder e;
- `θ_h = (c_h, μ_1..μ_K)` are the law's numbers;
- `p_h(y|…)` is the judge's own observation model (the clipped simulator, Gaussian sensor noise, and a knock density
  when z = knocked; M-1, §13);
- `m_w` is word w's meaning, one of a finite set of predicates M_w (§9);
- `s_j` is a caretaker sentence.

**The one update rule [exact given the model]:**
- **within a world:** Bayes' rule on each new observation (a throw or a sentence);
- **between worlds:** the final belief is folded into the next world's prior with a fade (§5).

**What is computed exactly, and what is approximated** (B condition 4):

| Part of the joint | How | Label |
|---|---|---|
| the law h over 𝓛 | enumeration: all 10,471 laws, every push | [exact] given the fidelity-0 likelihood (§3) |
| the numbers θ given h | profile fit and Laplace (the judge's own machinery) | [approximation]; its normalization is premise N, measured (§14) |
| knocks z_k | the exact two-state mixture per object (M-1) | [exact] given θ |
| word meanings m_w | enumeration over the finite M_w, jointly with h | [exact] given θ's Laplace summaries |
| goals and play | a decision rule (§8) | [decision rule]; not claimed to follow from Bayes (B condition 5) |

**"Entanglement" and "coherence", exactly:**
- **Entanglement ↔ non-factorization.** The posterior p(h, m | D, S) is not p(h|D)·p(m|S). A sentence about springs
  moves the law belief, and a certified law sharpens the word's meaning. The measure is the mutual information
  I(h; m | D, S) > 0 [exact on the enumerated pairs].
- **Coherence ↔ consistency of read-outs.** What SERA says, believes and predicts are three read-outs of one joint, so
  they cannot disagree. Every sentence's hedge level matches its belief, and every committed forecast is the belief's
  predictive [to measure: 0 contradictions].
- **What coherence does not mean** (B condition 3): reconciling belief with the judge. "Belief says A at 0.999, judge
  says not sure" is a correct state, and the judge outranks.
- Quantum mechanics is a metaphor here; the exact object is the joint model (Appendix B).

### 3. Belief over laws: exact, on one scale

**The fidelity-0 likelihood (one scale for every law; fixes F1 and S12V Definition 2).**
- For law h, per-object regression of the throw's velocity differences on h's columns gives accelerations with a
  Gaussian residual of variance σ_a², fixed from the sensor noise.
- A conjugate Gaussian prior on the coefficients (variance s_c², frozen) gives the closed-form marginal likelihood
  `m̃_t(h)`, computed from cached Gram matrices.
- It carries **no prior term** (the v1 double count is removed).
- It is one surrogate observation model, applied to every law.

**The belief** [exact under the surrogate]:

`b_t(h) = p_F(h | c) · m̃_t(h) / Σ_{h'} p_F(h' | c) · m̃_t(h')`

- **Cost:** O(|𝓛|·d²) per push, about 10⁴ laws × microseconds [to measure in T4].
- **What it is:** the exact posterior over 𝓛 of the surrogate model. It is not the posterior of the judge's model; the
  surrogate ignores the neighbour noise correlation (−½) of velocity differences.
- **Calibration** [approximation, logged]. On the live laws, fit `Q_h ≈ a_t + b_t·log m̃_t(h)` and report the
  residual and the rank correlation. A temperature `1/b_t` may be applied to m̃ for search only.

**The live set.** `Live_t` = the top K laws by b_t, plus the judge's current leader. They get the judge's exact
prequential Q (fidelity 2).
- Q terms are cached per (law, throw). They are exact because each depends only on D_{s−1}, so a law re-entering Live
  pays only for the throws it missed (F11).
- Live is a **decision set**, not a sample.

**Proposition 1 (belief over laws needs no sampling, tempering or thermodynamic integration)** [proven here].
- b_t is a finite sum.
- `log Z_t = logsumexp_h(log p_F(h|c) + log m̃_t(h))` is exact.
- Every tempered belief `b_t^{(β)} ∝ p_F·m̃^β` is exact for every β.

So SMC, the ESS rule and thermodynamic integration are unnecessary while 𝓛 is enumerable (B F2). They move to
Appendix A for a future grammar with more than about 10⁶ laws, or for sampling θ.

**What log Z is and is not** (B F3). `log m̃(h*) − log Z ∈ [0, −log p_F(h*)]` always, so it measures **ambiguity**
(how spread belief is). It never measures **adequacy**. Adequacy comes from the absolute tests of §10.

### 4. The floor: a safety rule outside the joint

A learned prior can grow overconfident and drive p_F(truth) toward 0 in a world where the truth holds. Relentless v1
did exactly this on seed 31: the true idea was dropped and never came back ((review notes, not published)). So a floor is kept **outside**
the learned part (B condition 1):

`p_F(h | c) = (1 − η)·P_mem(h | c) + η·π₀(h)`, with η = 0.1 [decision rule, frozen].

Here P_mem is the faded memory of §5.

**Proposition 2 (no law is ever forgotten, in evidence units)** [proven here]. For every law h and every rival h′, the
posterior odds satisfy

`log[b_t(h)/b_t(h′)] ≥ log m̃_t(h) − log m̃_t(h′) − log(1/(η·π₀(h)))`

since `p_F(h) ≥ η·π₀(h)` and `p_F(h′) ≤ 1`.

So the truth leads any rival once its evidence margin passes `log(1/(ηπ₀(G))) ≤ 16.3` nats (with η = 0.1 and
min log π₀ = −14.0). At σ = 10⁻³, a decisive throw carries hundreds of nats.

**Recall sentinel** [to measure]. On dev worlds, the truth's rank in b_t and its membership in Live are logged every
push. The T4 bar: the truth is in Live at certification in ≥ v3.1's rate (paired, n stated).

### 5. Memory: the faded prior, a fixed whole reshaped by what happens

This replaces v1's failure traces (Definition 4, Proposition 6), which were a separate, hand-coded mechanism. The
user asked for nothing propped up.

**The memory is a Pólya tree over the hypothesis lattice 𝒯**, a Bayesian model of "which laws tend to hold in
contexts like this".
- 𝒯 is the rooted tree of v1 §3: depends-on → operator class → term type → law. Every law has exactly one path. Grown
  laws are assigned by their inputs and operator.
- At each internal node n, the probability of child j is

  `P(j | n, c) = (α₀·π₀(j)/π₀(n) + C_j(c)) / (α₀ + C_n(c))`

  and `P_mem(h | c)` is the product along h's path. It is normalized at every node, because Σ_j C_j = C_n [proven
  here]. With no counts it equals π₀.
- **The counts are the faded, context-weighted beliefs of past worlds:**

  `C_n(c) = Σ_{s<now} γ^{age(s)} · κ(c, c_s) · Σ_{h∈L(n)} b_s^{final}(h)`

  - γ = 2^{−1/τ_half} fades them;
  - `κ(c, c′) = exp(−‖e(c) − e(c′)‖²/2ℓ²)` recalls by similarity, with the encoder e frozen per generation (stable
    coordinates, S12V).
- **Bounded:** past worlds are merged into M context prototypes (online k-means in e-space), each holding its node
  counts. Memory is M × |nodes| numbers, fixed.

**What the author's picture becomes, exactly** [proven here from the formulas]:

| The author's words | What the equations do |
|---|---|
| **"a dead branch is not regrown"** (within a world) | A law behind the leader by r nats of fidelity-0 evidence has `b_t(h)/b_t(leader) ≤ e^{−r}/(η·π₀(leader))`. Conditioning alone does this; no trace is written. The belief never proves anything: refutation for claims stays the judge's |
| **"failure is a fuzzy memory"** (across worlds) | A world where h failed gives h ≈ 0 count, and its siblings gain. h's prior share in similar contexts falls to about `(α₀·π₀-share)/(α₀ + C_n)`; in dissimilar contexts (κ → 0) nothing changes |
| **"…that fades"** | The deviation of P(j\|n) from its base is `w·(C_j/C_n − π₀(j)/π₀(n))`, with weight `w = C_n/(α₀ + C_n)`. With no new support, a uniform fade keeps the proportion C_j/C_n and shrinks only the weight: `w_k = γ^k·C_n/(α₀ + γ^k·C_n)`. So a memory supported by C_n effective worlds holds nearly unchanged for about `τ_half·log₂(C_n/α₀)` worlds, then halves every τ_half worlds. Well-learned things are stiff; rarely seen things fade at once [proven here] |
| **"…and is replaced by the correct, better way"** | The proven law's count rises in that context, so its share, and its coarse ancestors' ("it depends on the speed"), grows. Coarse nodes gather counts from many laws, so the fuzzy, coarse knowledge is learned first |
| **"it doesn't need to keep growing"** | M × \|nodes\| is fixed. Old worlds fade into the prototypes; nothing is appended |

**The imagination network W** (30k parameters, one pass):
- It is **amortization**: it is trained to reproduce b^{final} from the teacher's table, so the Field can guess in one
  pass what enumeration would compute ("like light").
- It provides the context encoder e.
- Under exact enumeration it is a speed path and a proposal for fidelity-1 work, not a second belief. Its training
  targets are the judge-free beliefs b plus the credit ladder of plan revision 2.
- Grades steer only these targets, never a proof.

### 6. Imagination: sampling the joint

**Definition (a dream).** Draw `h ~ b_t^{(β)}`, `θ ~ Laplace(θ | h, D_t)`, `z ~ p(z | h, θ, D_t)`, and simulate
`Y_a` for a candidate program a with the judge's simulator.
- **Fuzziness is the temperature:** β < 1 flattens belief. It is also the depth in 𝒯 at which a dream is fixed: a
  dream can fix only "depends on v" and leave the leaf to be drawn per rollout.
- **"Dream many, test the best, revise everything"** is exact:
  1. draw N_d dreams;
  2. score the programs by how much the dreams disagree (§7);
  3. push;
  4. the next throw updates the whole joint by Bayes (§2);
  5. the next dreams come from the revised belief.

  Nothing is patched; everything is re-conditioned.
- **Cost:** the batched simulator does about 2 ms per imagined future (measured, v3.1). N_d = 64 × 16 programs is
  about 2 s per push [to measure].

### 7. Curiosity and discovery: the information an action gives about the joint

**The quantity.** `EIG(a) = I(h ; Y_a | D_t, S_t)`, the mutual information between the law and the next reading
under action a.
- Estimated from the dreams with the nested Monte Carlo estimator [approximation, bias O(1/N_inner)].
- Its two-law, locally linear Gaussian case is the **surviving gap**:

  `½(dᵀd − gᵀ(JᵀJ + P)⁻¹g)`

  This is the minimum penalized linearized squared gap, if P ⪰ 0 and JᵀJ + P is invertible, with the same whitening
  for d and J (S12V). It stays the fast stage.
- When the band blocks, the band-directed score uses the Schur complement:

  `S_a = P_β + J_BᵀWJ_B − J_BᵀWJ_η(P_η + J_ηᵀWJ_η)⁻¹J_ηᵀWJ_B`

  It is the local marginal precision of the basis coefficients when the nuisance precision is invertible. The scope
  compared must be fixed (S12V).

**The one objective (fixes F10 and S12V §10):**

`U(a | Φ) = [R(Φ) − E_O R(T(Φ, a, O))] / E C(a)`

- The costs satisfy E C(a) > 0 for every action, including stop, which has a fixed positive cost.
- Wrong certifications are a **hard constraint**, never a term that can be traded.
- The free-energy identity `F(q) = KL(q ‖ p(·|D)) − log p(D)` holds for a normalized joint with p(D) > 0. Expected
  information gain lowers the **expected posterior entropy**. It does not lower expected F, whose minimum −log p(D)
  grows with data (B F10).

### 8. Play: its own goals and its own actions [decision rule]

B condition 5: none of this is claimed to follow from Bayes. It is how SERA chooses what to do on top of the joint.

**The action language.**
- Programs are built from primitives:
  - `push(k, u, d)`: the hand at strength u for d seconds on object k;
  - `wait(d)`;
  - `seq(p, q)`;
  - `repeat(n, p)`.
- Their prior is a prefix-free code, `P(p) = 2^{−|code(p)|}` (Kraft ≤ 1). The length and the number of segments are
  capped per judge version (B N2).
- v5.0 programs start from rest, since the judge's model starts from rest.
- **Library learning** (DreamCoder-style compression) turns subprograms that often earn information into new
  primitives, with their code length reserved at a version boundary. This is SERA's own repertoire of ways to play.
- There is no fixed menu. The candidates each push are:
  - draws from the code prior;
  - mutations of the best recent programs;
  - library calls;
  - the analytic surviving-gap programs, always included as a floor.

**Goals.**
- A goal g is an outcome description built from SERA's own words and events: an object, a verb and a place or a
  comparison. Examples: "make the iron one stop before the wall", "tell 'heavy' from 'big'", "find where the two
  leading laws part".
- The goal space grows as words ground (§9).
- **Learning progress:** `LP(g)` = the drop in prediction error of g's outcomes, from older to recent attempts
  (Oudeyer's absolute LP) [decision rule].
- **Choice:** a goal is chosen with probability ∝ LP(g) + ε_g, and switched when its LP falls below the median.
- **Within a goal,** the program is chosen by EIG plus goal attainment under the dreams.
- **The link to proof:** "find where the leading laws part" is always in the goal space, with LP computed like the
  others. So proof-seeking is one kind of play, not a separate mode. Certification is attempted whenever the judge's
  screen passes, whatever the goal.

**Validity** [S4 Theorem 2, remark]. Goals and programs depend only on D_{t−1}, S_{t−1} and independent randomness.
So premise P holds, and play cannot weaken Theorem A. Whether N and U hold on the throws play chooses is measured
(§14, F6).

### 9. Words and things: meanings as variables of the joint

**Things.** In the playroom (Part III), objects have visible features (material word, size, shape) and hidden
properties. In v5.0 the hidden properties act only through μ (B M1).

**Meanings.**
- Each word w has a finite hypothesis set M_w of predicates:
  - over visible features ("iron");
  - over hidden quantities through the joint ("heavy" = μ below the median of the objects met);
  - over law nodes ("springy" = the law has a restoring position term);
  - over events ("stops", "bounces").
- The prior over M_w is a description-length prior, frozen.

**The caretaker's sentences.**
- Generated by code from what really happened (B: past events only, so P holds). A is the caretaker, the author's
  delegated teacher.
- **Likelihood:** `p(s | m, world) = (1 − ε)·1[s true under m]/N_true + ε/N_all`, a truthful caretaker who slips at
  rate ε (frozen, e.g. 0.05).

**The coupled update [exact on the finite product M_w × 𝓛, given θ's Laplace summaries]:**

`p(h, m_w | D, S) ∝ b(h | D) · p(m_w) · Π_j p(s_j | m_w, h, θ̂)`

- **Hearing** "the red ball is springy", with springy grounded, raises every law with a restoring term.
- **Proving** a spring law sharpens what "springy" means.
- This is the non-factorization of §2, computed.

**Knowledge in words.** A general sentence ("springs pull back") is a sentence about law nodes. It updates b over 𝓛
through the same rule, so it shifts belief and search. It never enters a threshold or a proof.

**Speaking:**
- SERA's sentences are read-outs of the joint, with a hedge word fixed per belief level ("I think" > 0.9, "maybe"
  > 0.5).
- "Sure" is used only for certified claims.
- The statement checker re-derives every number (v3.1's `express.py`).

**Word claims are claims** (B C1):
- "Iron is heavier" or "'springy' means a restoring force" are claims only through their own anytime-valid tests:
  - `lexicon.py`'s grounding test;
  - confidence sequences for μ_i − μ_j;
  - "not sure" when masses are closer than the rail resolves.
- α is allocated across claim types up front (Σ α_type ≤ α per world), with e-BH or α-spending across the vocabulary.
- A posterior of 0.999 on a meaning is a proposal, never a grounding (B condition 3).

### 10. Growth and adequacy

**Adequacy is absolute** (B F3). SERA grows its grammar only on:
- the judge's adequacy test (per situation, Decision 6);
- the something-else alarm (basis-extended Q against the leader);
- or a posterior-predictive check of held-out throws.

**Growth:**
- truth-v2's localized formulas, then cells;
- later, edits under a prefix-free code with mass reserved at a judge-version boundary (Kraft);
- composition depth bounded per version, so 𝓛 stays finite. Beyond that depth, S is stated as assumed (B C2).

**Mid-life rivals** (B, open question 1). Pieces grown within a world join the **audit** at once, since adding
rivals is always valid. They join the **claim side** only with reserved mass.

### 11. From taught to autonomous proving (fixes F5, F6 and S12V Proposition 7)

**Stage 1, taught (now).**
- A grades each report (right / wrong / how much / where; grader "A (delegated)").
- B re-grades a random 20% (Cohen's κ with an interval).
- Grades train W's targets only.

**Stage 2, apprentice.** A learned grader is trusted for a claim kind only when:
- the Wilson lower 95% bound of its agreement on a pre-specified, representative held-out set is ≥ 0.9;
- the repeated promotion checks spend α (below);
- humans spot-check a fixed 10%.

Agreement with A is imitation, not truth; the judge alone certifies.

**Stage 3, autonomous.**
- The proof-strategy policy (designs, goals, when to certify) is trained on judge outcomes.
- **Reward:** −(throws to an accepted certificate) − c·CPU, computed **on the frozen reference suite P_\*** only, never
  on self-scheduled worlds (F6 b).
- **Every generation passes premise sentinels on its own throws** before promotion (F6 a):
  - an N probe (`n1_designed.py` generalized);
  - a U flip audit (multi-start rival fits);
  - per program class (B N2).

**The anchored competence gate** (replaces Definition 5; F5, S12V).
- Metrics are oriented so that larger is better: recall, −median throws, −CPU; wrong certifications are a hard zero.
- Each update W_k is compared with a fixed **anchor**: W₀, or the last version that passed fresh seeds.
- The per-update α is `α_k = α_gate·6/(π²k²)`.
- R is refreshed at each fresh-seed milestone.
- **Statement:** with probability ≥ 1 − Σα_k, competence on R never falls more than τ below the anchor [proven here by
  the union bound]. It says nothing outside R; fresh seeds measure that.

**What α means over a lifetime** (F6 c, S12V Proposition 7):
- α = 10⁻³ bounds the probability of a wrong acceptance **per world**, under the premises.
- Over N worlds, about N·α are expected under the theorem itself.
- Reports print the observed count beside N·α and the e-LOND bound on the admission record.
- α is not a false-discovery fraction among accepted claims.

**Goodhart resistance, measured, not proven.**
- Scope is weighted by a fixed external measure of extent.
- The "sub-law" route (certifying A ⊊ G quickly) is closed only because "sure" needs the band ≤ ε.
- Easy-world selection is closed by reward on P_* only.
- The sentinels guard the measured premises.

---

## Part II. The anchor: the judge, outside the field

### 12. Theorem A, restated precisely

**Theorem A** [S4 §2.2, with S12V's conditions].

**The premises:**
- **P:** every action and every choice of claim is a measurable function of the past and of independent randomness.
- **M:** the model family contains the true observation law, knocks included (M-1, §13).
- **N:** each claim's forecast `q_{A,s}` is a predictable sub-density, for every A in the claim universe.
- **U:** each rival denominator dominates the rival's likelihood at its true numbers, at every time.
- **S:** the truth G lies in the audited universe.
- Constants are frozen, including π_j, which is positive with Σπ_j ≤ 1.

**The statement:**

`P(∃t, ∃A: sure of A at t, and G ⊉ A) ≤ α`

**Supplements:**
- The missing-term case G ⊃ A is the band's, under F (the missing force lies in the basis span) and Q (the ellipsoid
  approximation).
- Scope errors are outside it.
- The empty claim has no rivals and is never certified by this route.

### 13. The field cannot weaken Theorem A (Proposition 3; A1, A2)

**Claim.** Suppose:
- (i) every field operation (belief, memory, dreams, play, words, learning, which laws are live, what to certify,
  when to stop) is a measurable function of the past and of independent randomness;
- (ii) the judge computes Q and the denominators from the throws alone, with frozen constants and the frozen π_j;
- (iii) certification runs the universe audit (§14).

Then Theorem A holds for SERA v4, with S discharged over the audited universe **given U**.

**Proof.**
- (i) is P.
- The union over claims uses π_j weights (A1), so a data-selected claim is covered.
- The audit makes every audited law not containing A a rival.
- Learning and play only change proposals and actions, which are covered by (i). ∎

**The premise clause** (A2). The corollary "everything in Part I may be heuristic without affecting validity" holds
**only while N and U hold on the throws the field chooses**. They are measured approximations, so they are re-measured
whenever the design or play policy changes (§11 sentinels).

### 14. The universe audit (Decision 9; premise S) — stage 1, as built in truth-v3

**The lemma** [proven here; S12V: correct with conditions].
- Take a claim A with terms T_A, and a claimable rival B ⊉ A. B has at most one non-base term t, and at most one idea
  beside it.
- B lacks some a ∈ T_A, so `B ⊆ U(t, −a) = {t} ∪ (IDEAS ∖ {a})`, with t ∈ {∅} ∪ (every universe term, the claim's own
  included), t ≠ a (B 1a, 1b).
- The models nest: B embeds in U with the extra coefficients at 0. So `sup_U ≥ sup_B`. This holds also under the
  robust mixture and M-1 denominators (B), hence `Q_A − sup_U ≥ thr ⇒ Q_A − sup_B ≥ thr`.

**The algorithm** (`truth.universe_audit`, policy `CCOPS5_AUDIT = 'universe-1'`):
1. **The tree.** For each a ∈ T_A, the roots are the universe's terms other than a, grouped by kind (products; powers
   of one input; sin or cos drives; pieces of one input; piece products), 8 at a time in grammar order. It is fixed
   before data.
2. **Superset nodes.** A node's superset `U(node, −a)` is fitted by `audit_fit`:
   - the pooled regression;
   - a plain Gaussian fit;
   - embedded starts;
   - and (B 2) the best-fitting space law it contains that does not contain the claim, with its extra terms at 0.
3. **Monotonicity guard.** A result below that member is marked unusable. The starts depend only on the space and the
   claim, so the mind and the checker agree.
4. **Pruning and splitting.** A node ruled out (`Q_A − sup ≥ thr`) is recorded and covers its laws. Otherwise it is
   halved. At a single term, its laws {t}, {t, i} are fitted one by one.
   - An unusable internal node splits.
   - An unusable member refuses (B 2).
5. **The checker:**
   - re-derives the audit;
   - runs its own coverage test `audit_gaps` (every (a, t) covered by a recorded superset, or by all of t's laws being
     in the space or recorded);
   - refuses a certificate whose `audit` is not the policy.

**What it discharges, precisely** (S12V §14.1):
- S over the audited universe, **given U**. A converged fit is a feasible lower bound on a sup, so a pruned node is
  valid only if its fit reached the sup.
- U is measured today (0 flips in 956) and becomes publicly attackable through the refutation API (§15). U-1's
  certified upper bounds (T3) would remove the assumption for low-dimensional rivals.

**Stage 1 leaves out the cells** (independent review's ruling):
- The certificate's scope says `not_audited = 'cells (stage 1) …'`.
- Its conditions:
  - stage-1 suites contain no cell-truth worlds, or they are reported separately under "S assumed";
  - a cell claim carries the same flag;
  - the self-report says it in words, since all cell families, containing or not, are unaudited.
- **Stage 2:** semantic containment. B contains A iff every term of A is a term of B, or is spanned by a cell of B on
  the same input, with every reading of that input (plus a path margin max|Δi|) inside the knot range. The checker
  recomputes it; otherwise the cell rival is audited normally. Unit test: the least-squares residual of (i, straight),
  steady and |i| on each cell basis is ≤ 1e-12 inside the range and > 0 just outside.

**Tests (written before the code, `tests/core/test_universe_audit.py`):**
- the universe size (10,471);
- tree coverage over six claims, exhaustively;
- the claim's own term is audited;
- a superset is never below a member;
- an out-of-ledger look-alike blocks a base claim that truth-v2 certified: forward-only pushes make |v| = v;
- the control world certifies, with the audit's CPU reported;
- the checker refuses a certificate made without the audit, or with a hole.

**T-S** [to measure]:
- 60 dev worlds whose true invented term is masked from the imagination;
- 0 sure claims contradicted;
- median ≤ 300 s CPU per certificate, including narrow-scope worlds (B).

### 15. The other premises

**M-1: per-object knocks.**
- **Numerator:** the exact two-state predictive per object.
- **Denominator:** `sup_θ Π_k[(1−ρ)Π φ + ρ Π b]`.
- **Test:** bump probe v3 (40 lives); 0 sure-and-wrong; bumped certifications ≥ v2; clean Q within 0.1 nat.

**N.**
- Laplace passed N-1 (teacher throws).
- T-ADAPT (B, running) measures designed throws: 183 throws; bar Z_corr ≤ 1.0025; the first 15 are within the bar.
- If it fails, designed throws use N-2 (exact), whose power is re-measured with the NRES guard.

**U.**
- Measured (0 flips in 956).
- U-1 (T3): separable certified bounds `sup_c Σ_k sup_{μ_k} ℓ_k` for rivals within 15 nats of the threshold.
- The refutation API `challenge(cert, B, θ′)` refutes a certificate if a witness in the rival model, under the same
  likelihood and threshold version, has `log L_B(θ′) > Q_A − thr(A)`.

**Decision 8 (the band as a test).**
- `log E_band = Q_A − sup_{(r,η)∈H_>} log L_{A+r,η}` (S12V: log form; v1 wrote a dimensionally wrong ratio).
- **Requires:** a normalized, predictable numerator; a certified null sup covering every (point, sign) pair, or
  fail-closed.
- **T-D8:** median ratio ≤ 0.85; 200/200 planted coverage; 0 sure-and-wrong.

**The premise ledger.** Every certificate records P, M, N, U, S, F and Q (and the lattice→cell bound) as computed,
measured or assumed. `express.py` says any assumed one in words (`rests_on`).

---

## Part III. The playroom: things and words (T4b)

**World v5.0** (on the rail physics; single-object throws, B M2):
- **Things:** 3–6 objects per world, each with visible features:
  - material word: iron, wood, rubber, foam;
  - size word: small, big;
  - shape word: ball, block.
- **Hidden properties** act **only through μ** in v5.0 (B M1 option c). Each material has a mass range, so "iron is
  heavy" is learnable.
- **Surfaces and walls** are smooth (tanh walls, smooth friction), as law terms shared by all objects (B N1).
- **The vocabulary** (about 40 words to start):
  - nouns: ball, block, wall, floor;
  - materials and sizes;
  - property words: heavy, light, springy, rough, slippery;
  - verbs: push, stop, bounce, slow down, speed up;
  - relations: heavier, faster, same, different;
  - hedges.
- **The caretaker's grammar:** subject + verb + (object | property | comparison). Sentences come from true events,
  with slip rate ε, spoken after events (past only).

**The premise gate before any "sure" in a playroom world** (B):
- M holds by construction (v5.0), or per-object random effects with their own N probe (later);
- an N probe on the world class passes the T-ADAPT rules;
- a U flip audit shows 0 flips;
- α is allocated across claim types.

**T4b tests** [to measure; n and paired intervals stated at pre-registration]:
- word grounding: grounded words, with false groundings ≤ α (e-BH);
- verified-sentence rate (0 false);
- held-out own-goal success;
- reachable-outcome coverage;
- discoveries per CPU-hour;
- all against a **fixed-menu, no-words baseline** on the same worlds;
- the one-field intervention test (§17).

S13 (reviewer, running) supplies the literature design.

---

## Part IV. Measurement

### 16. Self-acceleration, measured, never assumed

**Unchanged from v1, with S12V's conditions:**
- `ρ_j = C_j/C_{j−1}` and `R_k = ΔJ_k/C_k` on a frozen task definition, with C > 0, full CPU accounting, rewards
  defined for failed and unresolved runs, and the task mix matched;
- simultaneous intervals when three consecutive bounds are used.

**The growth model** `dI/dt = a·I^p` blows up at `T = I₀^{1−p}/(a(p−1))` only for p > 1. Finite hardware can show
only **local** self-acceleration.

**The decision rule** for claiming "local self-accelerating discovery" is S8 Design A:
- ≥ 3 consecutive ρ_j bounds < 1 (simultaneous);
- p's lower bound > 1, with a positive intervention × generation interaction;
- ≥ 2 grown operator kinds certified and replicated;
- every promoted change passed the anchored gate and the sentinels;
- the observed wrong count is reported against N·α.

### 17. The one-field tests (the author's second direction, made testable)

1. **Intervention.** Teaching one grounded word, or proving one law, changes proposals, goals and word meanings
   elsewhere through the shared joint. The measures are KL(q_before ‖ q_after) on held-out worlds, and the sign of the
   change in throws to certificate. An ablation that removes the word channel must cost measurably (paired, n stated).
2. **Coherence.** 0 contradictions between what SERA says, believes and forecasts, on every report.
3. **Nothing special-cased.** Fading, no-regrowth and replacement are measured as properties of §5's formulas, with no
   separate code path. The fading unit test checks the weight law `w_k = γ^k·C/(α₀ + γ^k·C)` on a synthetic count history.

---

## Part V. Build order (plan revision 3.1)

| Phase | Build | First tests |
|---|---|---|
| T2 (running) | §14 audit stage 1; M-1; the premise ledger; challenge; the lattice→cell bound; the CRP check | `test_universe_audit.py`; T-S; bump v3; ledger round-trip |
| T3 | Decision 8; U-1; profiling (golden diff 0) | T-D8; U-1 sanity |
| T4 | Part I: `sera/field.py` with exact belief (§3), the floor (§4), the Pólya memory (§5), dreams (§6), EIG (§7), the action language and goals (§8) | exact-belief unit tests (a 50-law toy against brute force); the fading weight law; the recall sentinel; compute with churn logged; the P2 suites as paired intervals |
| T4b | Part III: the playroom, words and speaking | the T4b tests; the premise gate |
| T5 | Kraft edits; D12 with the head hash; library learning of programs; bounded meta-improvement | Kraft audit; D12 rebuild; retention |
| T6 | B5 with ρ_j, R_k, TPC, CPC, RBU; fresh seeds; Lean L1/L3 | §16 decision rule; sentinels |

---

## Appendix A. For a future non-enumerable grammar: tempering, SMC and thermodynamic integration (corrected)

This applies only when |𝓛| is beyond enumeration, or θ is sampled.
- **The ESS rule.** ESS(β) is continuous but **not monotone** (B F9, S12V). Choose β_t as the largest qualifying value
  on a grid, not by bisection.
- **Replacing particles.** Replacing the lowest-weight particles with fresh proposal draws is **not** a valid
  importance sampler for the combined population (S12V, B F4). Use a mixture proposal with multiple-importance weights,
  or rejuvenate with a target-invariant (MH) kernel.
- **Thermodynamic integration.** `d/dβ log Z_β = E_{π_β}[log m]` and `d²/dβ² log Z_β = Var_{π_β}[log m]`. The
  trapezoid error per step h is `−h³ f″(ξ)/12`, with f″ = the **third central moment** of log m under π_β (B F7,
  S12V), plus the particles' Monte Carlo error.
- **The target** must be one coherent likelihood for all particles (F1), with no prior inside the likelihood.

## Appendix B. The author's picture, classified (v1's table, plus the new rows)

| Picture | Exact counterpart | Status |
|---|---|---|
| a black hole summarized by a few numbers | sufficient statistics | formal analogy |
| the holographic area bound | the capacity of a finite state (35,840 B = 286,720 bits, if that is the entire working state) | formal analogy |
| destroyed-looking information recovered | erasure codes (XOR recovers one erased chunk with intact parity) | formal analogy |
| compressed beyond sense | the data-processing inequality: a compressed table can slow a proof, never forge one (the judge reads raw throws) | exact theorem |
| bubbles nucleating | a critical-radius threshold → the growth gate | metaphor-derived |
| electricity, all interconnected | random walks and networks, `vol(G)·R_ij` on a finite connected weighted graph | formal analogy |
| **entanglement between the parts of the mind** | non-factorization of the joint; mutual information I(h; m \| D, S) | formal analogy, measured (§17) |
| **coherence** | consistency of read-outs of one joint (said = believed = predicted) | formal analogy, measured (§17) |
| **a brain divided into parts that flow into each other** | one joint model; each faculty a query on it; one update rule (§2) | the architecture |
| **neurons revising themselves; a tree not regrowing a dead branch** | Bayesian conditioning within a world; a faded Pólya-tree prior across worlds (§5) | exact (given the model) |
| quantum "making sense" | – | metaphor |

## Appendix C. Review ledger: where each finding is fixed

| Finding | Fix |
|---|---|
| B F1 / S12V Def. 2 (two scales, double prior) | §3: one fidelity-0 marginal for all laws; no prior inside m̃; calibration logged |
| B F2 (enumerable) | §3 Proposition 1; SMC and TI to Appendix A |
| B F3 / S12V (log Z gap) | §3: log Z measures ambiguity only; §10: absolute adequacy |
| B F4 / S12V Alg. F 3–5 (replacement) | removed (exact belief); Appendix A for the future |
| B F5 / S12V Def. 5 (gate drift, orientation) | §11: anchored gate, oriented metrics, α_k spending, R refresh |
| B F6 / S12V Prop. 7 (optimizer vs measured premises) | §11: sentinels per generation, reward on P_*, lifetime α wording; §13 A2 |
| B F7 / S12V Prop. 4 (third moment) | Appendix A |
| B F8 / S12V Prop. 2 floor | §4: the floor is η·π₀(h), exact |
| B F9 / S12V Prop. 3 (ESS not monotone) | Appendix A: grid |
| B F10 / S12V §10 (F direction; Dirac KL) | §7: EIG lowers expected posterior entropy; KL is finite on discrete h, and θ is profiled, not claimed |
| B F11 (replay churn) | §3: cached Q terms per (law, throw) |
| B F12 (thr index; rule e) | traces removed (§5); refutation uses the leader's threshold where used |
| B A1 (π_j), A2 (premise clause) | §1, §12, §13 |
| B open Q1 (mid-life grammar) | §10: audit side open, claim side reserved |
| B open Q4 (re-audit and e-LOND) | §5 memory is proposal-only. Re-opening a past certificate shrinks the event, so no α charge; the admission record is append-only, and the FDR claim is scoped to it |
| B §14.1 (enumeration, warm start, split, G ⊉ A) | §12, §14, as built |
| B cells ruling | §14 stage 1 conditions, stage 2 rule |
| B playroom M1, M2, N1, N2, U1, C1, C2 | Part III gate; §8 caps; §9 claim types; §10 depth bound |
| B one-field conditions 1–5 | §4 floor outside; §1 π_j frozen; §2 and §9 "posterior is never a claim"; §2 factorization table; §8 decision rule |
| S12V §1 (frozen universe, codebook) | §1 and §10: frozen per judge version, reserved mass |
| S12V Theorem A conditions | §12 |
| S12V §6 fidelity 1/2 wording | §3: fidelity 1 is a local fit on recent throws, a heuristic rank, not a bound; the Laplace predictive's normalization is N, measured |
| S12V Prop. 5 (cost) | §3: churn logged, Q cached; the cost is measured in T4, not asserted |
| S12V Prop. 6 | replaced by §5's exact properties |
| S12V §9 (receipts) | re-grades are versioned labels; re-audits are append-only |
| S12V §12 (conformal) | the Live size K uses the finite-sample quantile ⌈(n+1)(1−α)⌉/n, re-calibrated per generation (exchangeability stated) |
| S12V §13 (surviving gap, Schur) | §7 conditions |
| S12V §14.5 (E_band dimensions) | §15 log form |
| S12V §18 (DPI, capacity, XOR) | Appendix B conditions |
| S12V §19 | §16 conditions |

---

## In plain words

**What SERA is now.** Picture one big "sense of how things might be", shared by everything SERA does. Imagining,
wondering what to try, remembering, learning words and talking are not separate machines bolted together. They are
different ways of *looking at that one sense*. When SERA sees a throw, or hears "springs pull back", the whole sense
updates at once, so all the parts move together. That is the "everything is connected" the author asked for. The
technical name is a joint probability that doesn't split into independent pieces.

**How it forgets.** A law that fails in this world gets pushed down by the evidence itself; nothing has to write
"don't try this again". Across worlds, SERA keeps a fixed-size memory of which kinds of laws showed up in which kinds
of situations. That memory fades a little with every new world, faster for things seen rarely and slower for things
seen often. A small guaranteed "maybe it's something else" is always kept, so SERA can never completely forget a law
that might turn out true.

**How it plays.** SERA gets building blocks for actions and words, not a menu. It invents its own little games ("can
I make the iron ball stop before the wall?"). It keeps playing the games where it's learning fastest, and switches
when a game stops teaching it anything.

**What stays fixed.** Only the judge, and its check against everything SERA could have imagined, is allowed to say
"sure". SERA can believe, guess and talk freely, but it cannot bend that check. That is why its "sure" can be trusted.
