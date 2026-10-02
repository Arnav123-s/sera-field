# SERA's playroom: things and words as parts of one field (T4b design, draft v0.1)

development review, 2026-09-25 evening. It builds on:
- theory v1.1 §8–9 and Part III (`docs/SERA_FIELD_THEORY.md`);
- S13 (`(review notes, not published)`) as corrected by the reviewer's fact-check S13F (`(review notes, not published)`, audited by independent review:
  17/17 opened; Colas 2020 abstract-only).

**Status:**
- This is a design for independent review, covering the premise gate.
- Nothing here has run. No number in it is a result.
- Labels: **[derived]** is proven in this document; **[exact]** is computed without approximation;
  **[approx]** names its approximation; **[decision rule]** is a heuristic, frozen before dev evaluation.

**The author's two directions this answers:**
- **"Teach it actual words and actual things, and let it plan on its own."** SERA gets real object kinds and a real
  vocabulary. It chooses its own goals and composes its own experiments.
- **Every faculty must be the field's own behaviour, not a propped-up module.** Words, things, laws, goals and speech
  are variables of one joint model. Hearing, seeing, pushing and proving all update the same joint.

**v0.1** (after independent review, m1b `reports/REVIEW-PLAYROOM.md`, findings P1–P6 and L1–L7): the changes are
marked [B P*] / [B L*].

**What is fixed** (S13 §1: no finite system is literally unconstrained, so we say exactly what is fixed):
- the rail physics and the hand;
- the sentence syntax, and each slot's word list, which is given without meanings [B L7];
- the sensor predicates (what can be observed);
- the room predicates of §2 (a frozen total function over every law a room can draw);
- the judge;
- the compute budget.

Everything else is learned or chosen by SERA. Growth of the predicate grammar (T5, Kraft edits) widens what words can
mean.

---

## 1. The room (world v5.0)

**Physics:** the rail, the hand and the noise are unchanged (`ccops5.core.paths`). One law h per room acts on every
object. The law is drawn as the curriculum suites draw it, restricted to `sera.field.LAWS` [B L1]; world validation
checks the restriction. Objects differ **only through μ = 1/m** (independent review M1, option c).
So the judge's premise M holds by construction, as in every world so far.

**Things:** n_obj = 4–6 objects per room, each with three visible features:

| Dimension | Values |
|---|---|
| material | iron, wood, rubber, foam |
| size | small, big |
| shape | ball, block |

**Hidden mass**, drawn by the room's code: log m_i = a_material + 0.4·[big] + N(0, 0.15²), with a_iron = log 2.2,
a_wood = log 1.2, a_rubber = log 0.9 and a_foam = log 0.6. So m spans about 0.5–3.5, near today's range of 0.6–2.5.
- Shape carries no mass information. It is a deliberate distractor: a word for a shape must not come to predict mass.
- "Heavy" is correlated with both "iron" and "big", so telling "heavy" from "big" is real inference, settled by pushes.

**Knocks:** the M-1 generator, unchanged (tricks 0.05, the 8 states).

**Names:** objects carry arbitrary public IDs that are not words; they change on held-out rooms.

**World validation**, before any use ((review notes, not published) rule):
- on dev seeds, the true law explains ≥ 95% of non-knocked situations;
- nothing hits the acceleration clip;
- the material→mass correlation is visible at the rail's resolution.

## 2. The caretaker: the caretaker's code, the author's delegated teacher

**What it says**, only about the past (so premise P holds). After each throw, with probability p_speak = 0.5, it picks
one **template** uniformly among **all** active templates (T1–T5), whatever is true [B P5b], and one **topic**:

| Template | Slot kind d | Topic | Example |
|---|---|---|---|
| T1 "this is made of ⟨w⟩" | material | the object just thrown | "this is made of iron" |
| T2 "this one is ⟨w⟩" | size | the same | "this one is big" |
| T3 "it's a ⟨w⟩" | shape | the same | "it's a ball" |
| T4 "this one feels ⟨w⟩" | property (heavy, light) | the same | "this one feels heavy" |
| T5 "things here ⟨w⟩" | room law | the room | "things here pull back" |
| T6 "⟨ref⟩ is ⟨w⟩ than ⟨ref⟩" | relation (heavier, lighter) | the object just thrown and one thrown earlier | later (v5.1) |

**How it picks the word.** Within the slot, the caretaker says a word uniformly among the words **true** of the topic,
under the room's true lexicon. With slip rate ε = 0.05 it says a uniformly random word of that slot instead. If no
word of the slot is true of the topic, it says a uniformly random word [B P5a].

**Condition R-P** [B P1]: the utterance after throw t is a function of only three things:
- the hidden state (h, θ, μ, the true lexicon L*, the knocks);
- the throws up to t;
- the caretaker's own random numbers.

It never uses present or future throw noise. Theorem A is conditional on the hidden state, so the caretaker may know
the answer; what it must not know is the noise still to come. The code enforces R-P structurally: the caretaker object
receives the room's state and the past throw list, and nothing else.

- **Property words:** "heavy" is true if the topic's μ is below the median μ of the room's objects (fixed at room
  start; the caretaker knows the masses). "Light" is true if it is above.
- **Room-law words:** a frozen **total** function over every law in `field.LAWS` [B L1]. Write the force as
  `f(x) + g(v) + k(t) + cross terms`, with coefficients c. The two sign predicates are linear functionals of c,
  computed once per term on a fixed reference range with no data. So each is decided by the sign of one number,
  exactly.

  | Word | True when |
  |---|---|
  | pull back | `a·c < 0`, with `a_j = ∫_{−3}^{3} x·φ_j(x) dx` over position-only terms (0 if there are none): the position force points back on average over the rail [B note: the range goals and throws use] |
  | slow down | `b·c < 0`, with `b_j = ∫_{−6}^{6} v·φ_j(v) dv` over speed-only terms (0 if there are none): the speed force opposes motion on average over the cells' speed range |
  | push along | the law has a term with neither position nor speed: a steady push (a slope) or a time drive |
  | wave | the law has a periodic (wave) term in position or speed. Periodic *drives* count as "push along" only, so the two are disjoint |
  | nothing | none of the above |

  N_true ≥ 1 always, because "nothing" covers the rest. Cross terms (products) count toward none of the four; this is
  stated, not hidden. Validation lists the truth vector of every drawable law.

  **Where sign uncertainty comes from** (independent review note): the v5.0 regimes fix their signs. Springs restore and drags
  resist; only the slope is drawn ±. So a room's words are fixed by its regime. The uncertain sign that §3's orthant
  sum handles lives only in SERA's belief (the Field's posterior over c), never in the room.

**Its likelihood is exact by construction** [derived]. SERA observes the template (the syntax) and the topic (the
object thrown). The template's and topic's choice probabilities do not depend on what the words mean, so they cancel
from every comparison of meanings. For a slot of kind d with word list W_d:

`p(w | L, topic) = (1 − ε)·1[w true of topic under L]/N_true(L, topic) + ε/|W_d|` if N_true(L, topic) ≥ 1, and
`p(w | L, topic) = 1/|W_d|` if N_true(L, topic) = 0 [B P5a]

where L is the lexicon (which predicate each word names). The templates are chosen uniformly among all of them and
the topic by the throw, so neither depends on L or on hidden μ. That holds in every slot, the property slot included
[B P5b].
- This is S13's noisy model, with the uniform-over-true sampling that the size principle needs: S13F derivation
  item 6. We did not assume that sampling; we built it.
- A slot's words are the words the caretaker's code can put in it. SERA is given each slot's word list, but not what
  the words mean: the child hears the words before knowing them. Unknown new words are v5.1.
- **Selective timing (S13 red team; S13F item 6):** the caretaker speaks after every throw with a fixed probability,
  not at surprises. Its timing therefore carries no information about meanings. A "timed" arm that speaks at surprises
  is a later ablation, with its own likelihood.

## 3. Meanings as variables of the joint: exact, and interconnected

For each slot kind d, the lexicon L_d is a **bijection** between the slot's words and its predicates. A bijection builds
in mutual exclusivity: one word per meaning, one meaning per word.

| Slot kind | Words × predicates | Lexicons (\|𝓛_d\|) |
|---|---|---|
| material | 4 × 4 | 24 |
| size | 2 × 2 | 2 |
| shape | 2 × 2 | 2 |
| property | 2 words × P_prop, ordered pairs of distinct predicates | 30 |
| room law | 5 × 5 | 120 |

The property slot's predicate set is P_prop = {μ below median, μ above median, big, small, iron, foam}. This is
where "heavy" competes with "big" and "iron".

**The joint** (the Field's state, extended). All of these are variables of one model:
- the law h and its coefficients θ;
- the objects' μ;
- the lexicons L_d;
- the kind parameters (§4).

The factors are the throws (through the judge's likelihood and the Field's evidence table), the sentences (§2), and
the priors. Their product is the Field's posterior. The coupling edges:
- **L_room ↔ h:** a room sentence is a factor on (L_room, h, sign θ).
- **L_prop ↔ μ:** a property sentence is a factor on (L_prop, μ_topic, μ_others).
- **L_material, L_size ↔ visible features:** these factors are exact and observed.
- **μ ↔ kind parameters ↔ material:** the prior of a new object's mass.

**Updates:**
1. **Visible-feature lexicons** [exact]. Each sentence multiplies the posterior over the 24, 2 or 2 lexicons by
   `p(w | L, topic)`. This is 24 multiplications per sentence.
2. **Room-law lexicon with the laws** [exact over the finite product 𝓛_room × 𝓛, given θ's Gaussian posterior]:

   `log b(h, L) = log b(h | D) + log p(L) + Σ_j log p(s_j | L, h)`

   evaluated on 120 × 3,175 = 381,000 cells, **summed exactly over sign orthants** [B P4]. The two sign predicates
   (a·c < 0, b·c < 0) are linear functionals of the coefficients. Under the Field's exact Gaussian posterior
   c | h, D ~ N(m_h, S_h), they are jointly Gaussian, so the four orthants (s₁, s₂) ∈ {<0, ≥0}² have exact
   probabilities: a bivariate normal orthant, via Owen's T or an mvn CDF, and a 1-D CDF when a law has only one of the
   functionals. The sentences' factor is then

   `Σ_{(s₁,s₂)} P(s₁, s₂ | h, D) · Π_j p(s_j | L, h, s₁, s₂)`

   which is exact within the Field's model, with 381,000 × 4 terms. The per-sentence product of sign marginals
   (v0) was biased against a law with an uncertain sign by about 0.68 nats per sentence (B P4: 2.72 nats at n = 5, 6.14
   at n = 10). v0.1 removes it.
   - The marginals are the non-factorization the author asked for, computed:
     - **hearing moves belief about laws:** `b(h) ∝ Σ_L b(h, L)`;
     - **proving a law sharpens word meanings:** `p(L) ∝ Σ_h b(h, L)`.
   - **Replacing S13's κ = log 2** [derived]. For one grounded sentence, the ratio of belief between a law where the
     word is true and one where it is false is `1 + (1 − ε)|W_d|/(ε N_true(h))`. With ε = 0.05, |W| = 5 and
     N_true = 1, that is 96 (4.6 nats). It is fixed by the caretaker model, not by a knob. An ungrounded word (a flat
     posterior over L) gives a ratio near 1 automatically.
3. **Property lexicon with the masses** [approx: μ's joint posterior from the judge's leading fit, Gaussian in μ].
   p(w | L_prop, μ) is evaluated in expectation over μ's posterior. Hearing "this one feels heavy" also updates that
   object's μ belief (for the Field's dreams and designs only).
4. **The floor** (§4 of the theory) holds on the prior side only. Sentences are evidence, so the floor does not cap
   them. Instead, the slip model bounds each sentence's effect [derived]: a single sentence moves the odds between two
   laws by at most `log((1 − ε + ε/|W|)·|W|/ε)` = 4.6 nats (ε = 0.05, |W| = 5). So one wrong sentence never outweighs
   a few nats of throw evidence, and it is never enough to hide the truth from the judge. The universe audit weighs
   every claimable law regardless.

**None of this touches the judge** [derived; S13F derivation item 3]. Sentences enter only the Field's belief. That
belief chooses which laws to weigh, which terms to open and which pushes to make: all predictable functions of the
past. The judge's inputs remain the throws, the policy prior π₀ (D9) and its own fits. The certificate never reads b,
L or any sentence. So Theorem A's premises are unchanged (P holds because sentences are past data), and the universe
audit still weighs every claimable law whatever the words said. A proposal biased by a wrong sentence costs CPU,
measured as discoveries per CPU-hour; it cannot cost validity.

## 4. Kinds: what iron things tend to weigh [approx; S13F correction 4 and derivation item 7]

Kemp et al. (2007) model feature distributions over latent kinds. The Gaussian log-mass hierarchy here is **our
adaptation**, derived for this room, not the paper's model.

- **Model** (it matches the generator's form, not its values): `x_i = log m_i ~ N(θ_{k(i)} + β·[big], σ²)`,
  `θ_k ~ N(θ₀, τ²)`, with kind k = material, β ~ N(0, 0.5²), θ₀ = 0 and τ = 0.5 [B L2].
  **σ is learned** [B L2 follow-up, option (a)]: σ ∈ {0.1, 0.15, 0.2, 0.3} with a uniform prior. The posterior is an
  exact finite mixture of four conjugate regressions, one per σ, weighted by their marginal likelihoods and learned
  across rooms. A fixed σ = 0.2 would have covered 99.1% against the generator's 0.15, failing test 7 by design.
- **Scope in time** [B L2]: kinds are learned **across rooms**. The universe's kinds are fixed, so the kind posterior
  is part of the Field's memory, faded with the same γ as the law memory.
- **Observation:** the judge's posterior of μ_i is approximately N(μ̂_i, v_i), so x_i ≈ N(−log μ̂_i, v_i/μ̂_i²) by the
  delta method [approx].
- **Update** [derived; conjugate]: Bayesian linear regression of x̂_i on the design row (one-hot kind, [big]).
  - The parameter is ψ = (θ_iron, θ_wood, θ_rubber, θ_foam, β).
  - Each object's noise variance is r_i = σ² + v_i/μ̂_i².
  - Prior: ψ ~ N(ψ₀, P₀⁻¹), with ψ₀ = 0 and P₀ = diag(τ⁻², τ⁻², τ⁻², τ⁻², 0.5⁻²).
  - Posterior: `P = P₀ + Σ_i z_i z_iᵀ / r_i` and `m = P⁻¹(P₀ψ₀ + Σ_i z_i x̂_i / r_i)`, where z_i is the design row.
  - With β fixed at 0 this reduces to the scalar per-kind formulas `V_k⁻¹ = τ⁻² + Σ_{i∈k} r_i⁻¹`,
    `M_k = V_k(θ₀τ⁻² + Σ_{i∈k} x̂_i r_i⁻¹)`.
- **Use:** the predictive log mass of a new object with design row z is the σ-mixture of `N(zᵀm_σ, zᵀP_σ⁻¹z + σ²)`. It feeds the Field's
  dreams and design only. **Never the judge**, whose μ prior MU_PRIOR stays frozen (premise N is measured on it).
- **Calibration, pre-registered** [B L3]: 95% predictive intervals for held-out objects' log m, on ≥ 1,000 held-out
  objects over dev rooms. The Wilson 95% interval of the coverage must contain 0.95.

## 5. Goals and play [decision rule; S13F corrections 5–6, derivation items 8 and 10]

**Goals are predicates on observable outcomes**, built from the words SERA has grounded and the sensor primitives
[B L4]. Each primitive is evaluated on one throw's readings with frozen thresholds:

| Primitive | True when |
|---|---|
| `stopped` | \|v\| < 0.05 at the last reading |
| `moving(dir)` | the sign of v at the last reading is dir, and \|v\| ≥ 0.05 |
| `near(bin)` | the last x lies in the bin (bins of width 0.5 over [−3, 3]) |
| `before(bin)` | x stays below the bin's lower edge at every reading |
| `crossed(mark)` | x passes the mark at some reading |
| `faster(y)` | this throw's max \|v\| exceeds the max \|v\| of object y's latest throw with the same program |

Goals combine primitives with `and`. The object is referred to by grounded words, for example "the iron one":
"make the iron one stop before bin 2" is `and(stopped, before(bin 2))`, on an object that SERA's lexicon calls
"iron".
- **False success** [B L4]: the checker reports a goal achieved while the **evaluator** says it was not. The evaluator
  applies the same predicate, but with the true lexicon (which object really is iron) on the same readings.
- So a goal scored on a wrongly grounded word counts as a false success. Bar: 0.

A goal's achievement is checked **deterministically on the observed readings**. It is valid as an achievement function
exactly when every primitive in it is observable (S13F item 10). A goal using an ungrounded word or a hidden quantity
is not a goal (it cannot be checked). It becomes a question for the Field instead, since the Field's EIG already asks
questions.

**Competence and learning progress** (Forestier et al.'s LP is a competence derivative; the windows are ours):
- A **goal family** is a template with its object, a word and a place bin.
- **Competence** c_f(t) is the mean success of the last n = 8 *attempted* goals of family f.
  - Hindsight relabelling updates coverage records but never competence (S13F item 8).
- **LP_f = |c_f(recent 8) − c_f(previous 8)|.**
  - **Initialisation** [B L5]: a family with fewer than 16 attempts has LP_f = 0.5, a fixed optimism, so that every
    family gets tried.
- **Choice** [decision rule, theory §8; how the two rules combine, B L5]:
  - At a switch point, a family is drawn with probability ∝ LP_f + 0.05.
  - It is kept, and re-checked every 4 attempts, until its LP falls below the median LP of all families. Then comes
    the next switch point.
- **Within a family:** the push program maximizes P̂(goal | program) under the Field's dreams, plus the Box–Hill score
  over the top laws. So proof-seeking is one family among the others ("find where the leading laws part"), always
  present.

**Actions:**
- the action language of `sera/field.py` (disjoint segments, prefix code, Kraft ≤ 1), extended with the choice of
  object;
- library learning (DreamCoder) is a **local MDL heuristic** here (S13F correction 7), and it waits for T5.

## 6. Words as claims: anytime-valid grounding [derived; S13F derivation items 1–2]

"'Iron' means iron" is a claim. It must be earned like a law, never taken from a posterior (theory §9; independent review
condition 3).

**Setting.** One slot kind d with its finite lexicon set 𝓛_d, and a claim C = "word w names predicate v". The null is
H₀ = {L ∈ 𝓛_d : L(w) ≠ v}.
- **Filtration:** everything observed before utterance j: throws, templates, topics and earlier words.
- The template and topic are chosen by the caretaker's code from past events, with its own randomness. Under every L,
  the j-th word's conditional density is `p_L(w_j | past, template_j, topic_j)` from §2.

**The e-process:**

`E_t(C) = Π_{j≤t} q_j(w_j) / max_{L∈H₀} Π_{j≤t} p_L(w_j | …)`

where `q_j = Σ_L π_{j−1}(L)·p_L(w_j | …)` is the predictive of SERA's own sequential posterior over 𝓛_d. The
posterior uses only the past, so q_j is a predictable, normalized density.

**Validity** [derived; universal inference, Wasserman–Ramdas–Balakrishnan 2020, as used by the judge]:
- If the true lexicon L* ∈ H₀, then `max_{L∈H₀} Π p_L ≥ Π p_{L*}`, so `E_t(C) ≤ Π q_j/p_{L*}(w_j)`.
- The right side is a nonnegative martingale under L* with mean 1, since each q_j integrates to 1 over the slot's words.
- By Ville's inequality, P(∃t: E_t(C) ≥ 1/α_C) ≤ α_C.

The maximum over H₀ is exact, because 𝓛_d is finite (at most 120 elements). Nothing is maximized locally, so there is
no U-type premise for visible-feature words.

**Family-wise** [derived]:
- The claims C = (d, w, v) form a **fixed finite set per room version**, listed before any evidence. So the weights
  `α_C = α_words·2^{−ℓ(C)}` with Σ_C 2^{−ℓ(C)} ≤ 1 (Kraft) give P(any false grounding) ≤ α_words by a union bound.
- Adaptively invented predicates (T5) enter only at a version boundary, with reserved code length: S13F item 2.
- Repeated looks are covered by Ville (anytime).

**Slots whose truth depends on the hidden state** [B P2, P3]. There, p_L(w) depends on more than L. The fix is to
enlarge the null to a finite superset and maximize over it exactly. A superset of the null is still valid: its max is
≥ the true state's likelihood.
- **Room-law words** [B P2]. The state enters only through the truth vector τ ∈ {0,1}⁴ of the four predicates
  ("nothing" follows from them). The denominator is `max over (L, τ) ∈ H₀ × {0,1}⁴`: at most 120 × 16 = 1,920 cells,
  exact. It needs no premise about which law is true, not even S: piece or cell laws are covered, because only τ
  matters.
- **Property words** [B P3]. "μ below/above the median" depends on μ only through the split of the room's objects into
  a lower and an upper half: C(6,3) = 20 splits for n = 6 and C(4,2) = 6 for n = 4. For n = 5 there are
  C(5,2)·3 = 30 labelled splits: 2 below, the median object (neither heavy nor light, so N_true = 0 for it), and 2
  above. The visible predicates are known. So the denominator is a
  finite max over H₀ × splits, exact, with no U premise. **Property-word groundings are therefore claimable**, which
  replaces v0's "needs derivation".

**Scope:**
- This proves "w names v", given that the caretaker follows §2 with R-P, which holds by construction for our caretaker.
- A human caretaker's words would need their own M-type premise.

**α budget per world** (theory §9; S13 needs the split):
- laws α = 10⁻³ (unchanged);
- words α_words = 10⁻³;
- relations (later) 10⁻³.

Each is reported separately, never pooled with the law guarantee.

## 7. Speaking

SERA's sentences are read-outs of the joint. `express.py` renders them and its checker re-derives them:
- **"Sure"** only for certified laws, and for grounded words (§6), each with its own e-value.
- **Hedges:** "I think" when a belief is > 0.9, "maybe" when it is > 0.5.
- **Kinds:** "iron things seem heavy (95% of their masses between a and b)", from §4.

Every sentence is a checkable claim. Checker acceptance of emitted factual sentences must be 100% (bar below).

## 8. Premise gate before any "sure" in a playroom (theory Part III, independent review)
0. **The universe audit is on** (`CCOPS5_AUDIT=universe-1`) [B P1]. Under 'wide', sentences would steer which rivals
   are weighed, and S would only be assumed.
1. **M by construction** (§1). World validation passes, including the room-predicate truth vector of every drawable
   law and the R-P structure of the caretaker's code.
2. **N:** the Laplace forecast's normalization, probed with the T-ADAPT rules on playroom throws [B L6]. The probe
   covers the wider mass range (log-normal by kind, m ≈ 0.5–3.5), knocked programs (M-1), and the programs that the
   goal policy and the Field's designs actually choose.
3. **U:** a flip audit with 0 flips, superset refits included (review H1).
4. **α split** as in §6.
5. **The caretaker's code reviewed by B:** that it matches §2's likelihood exactly (template, topic, uniform over true
   words, slip ε) and that it never reads the future.

## 9. Tests (written before the code)

| # | Test | Bar |
|---|---|---|
| 1 | The caretaker's empirical word frequencies match §2's likelihood (10⁵ draws) | χ² p > 0.001 |
| 2 | Lexicon posteriors equal brute-force enumeration on a toy | 1e-12 |
| 3 | The joint (L_room × 𝓛) marginals, summed over sign orthants, equal a brute-force sum over sampled sign vectors (10⁶ samples); **n ≥ 5 same-word sentences** on a law with an uncertain sign [B P4] | within the Monte Carlo interval; one sentence moves b by the derived ratio (§3) |
| 4 | Grounding e-process on 1,000 simulated rooms per claim, true and false lexicons, **at α_test = 0.05 and 0.1** [B P6] (Ville holds for every α; 1e-3 is the deployment level, unreachable to validate at n = 1,000) | false groundings: Wilson upper bound ≤ α_test at both levels; true-word grounding times reported |
| 5 | "Heavy" vs "big": in rooms where size and mass disagree for some objects, the posterior over L_prop picks "μ below median" after pushes | ≥ 90% of dev rooms |
| 6 | Shape words never predict mass: the kind model's shape coefficient, if added as a control, has a CI covering 0 | – |
| 7 | Kinds: held-out log-mass 95% coverage on ≥ 1,000 held-out objects [B L3] | Wilson 95% interval contains 0.95 |
| 8 | No judge input changes with sentences: the certificate is byte-identical with and without the caretaker on the same throws | – |
| 9 | Goals: every chosen goal is observable-checkable; 0 false successes | – |
| 10 | The one-field intervention (theory §17): teaching one room word changes proposals, goals and other word meanings. KL on held-out rooms > 0; the word-channel ablation costs throws-to-certificate | paired interval, n stated at pre-registration |

**The T4b gate** (S13 §6.6, adapted; n and intervals fixed at pre-registration, after dev):
- **Arms:** (A) full; (B) fixed menu, no words, fixed goals; (C) open actions and goals, no words; (D) words plus
  fixed menu. Paired by room seed.
- **Bars:** reachable-outcome coverage (A ≥ 1.25× B, lower bound > 1); held-out goal success (A − B ≥ 10 points,
  lower bound > 0); verified sentences 100%; discoveries per CPU-hour (A/B ≥ 1.1, lower bound > 1); 0 sure-and-wrong
  laws; false groundings ≤ α_words.
- A higher goal score with fewer certificates is **not** a pass.

## 10. Build order
1. `ccops5/core/playroom.py`: the room (§1) and the caretaker (§2). Tests 1 and 8, plus world validation.
2. `sera/field.py`: lexicons and the joint (§3), with tests 2, 3 and 5; kinds (§4), with tests 6 and 7. The mind's
   view of a thing exposes only its look and ID, never the hidden material, mass or knock (independent review C3); a test pins
   this down.
3. `sera/lexicon2.py` or an extension of `ccops5/core/lexicon.py`: the grounding e-process (§6), with test 4.
4. Goals and object choice in the action language (§5), with test 9.
5. `express.py` hedges and word claims (§7).
6. The premise gate (§8), B.
7. Dev runs, freeze note, the gate on fresh room seeds once.

## In plain words
SERA gets a toy room: iron, wood, rubber and foam things, big and small, balls and blocks. A grown-up (my program)
talks about what just happened: "this is made of iron", "this one feels heavy", "things here pull back". SERA doesn't
know what the words mean at first. It works it out the way a child does: noticing which word goes with which thing, and
knowing that two words rarely mean the same thing. All of it lives in the same "sense of the world" as its laws:
- hearing "things here pull back" makes it expect a spring;
- finding a spring makes it more sure what "pull back" means.

"Heavy" is the tricky one. Iron things and big things are often heavy, so SERA has to push them to find out whether
"heavy" means iron, big, or hard to move.

It can say "I'm sure 'iron' means iron" only after a test like the one for laws, a test that can be wrong less than
1 time in 1,000. Nothing it hears can ever make the judge say "sure" about a law. Words only help it decide where to
look.
