# M1 design: one mind that learns (`ccops5/core/`)

*Design note, 2026-09-22. It implements the approved Architecture v2 (decisions D1–D8). The tests come first
(`core_check.py`, committed before the code). This note pins the interfaces and the maths so the build can
continue across sessions.*

## 1. What M1 must show
- The checks **C1–C11** of Architecture §12 pass on fresh seeds 11–20 (core track), and each check is run
  twice with the same results.
- Tournaments **T2** (credit), **T3** (hand-holding → zero-shot) and **T4** (sure).

## 2. Build order (each step ends with its checks passing on dev seeds)

| Step | Builds | Checks |
|---|---|---|
| M1a | **The truth layer:** the path likelihood, the e-process, confidence sequences, the residual band, the certificate, the checker | C1, C6, C8, C10 (the temptation world), C11 |
| M1b | **The loop in the school world:** gut-ordered ideas, experiments by expected disagreement, growth, the library, sentences | C3, C4, C5 |
| M1c | **Adapters:** nursery, school, inventor, ball; parity with the old robots | C2, C7 |
| M1d | **Teaching, credit and dreams;** tournaments T2–T4 | C9, and C10 with credit on |

## 3. The truth layer (M1a)

### 3.1 Data
- **A throw** is `Throw(world, situation, action, t, x, v, tag)`:
  - `x` and `v` are the noisy readings (1-D worlds; the ball adapter uses x and y);
  - `tag` records who chose the throw: teacher, own, check or dream.
- Throws are stored in the order they were made and are never changed. **The checker reads only these.**

### 3.2 Families and the grammar
- **A family** is a set of force terms (ideas) plus the known hand, with:
  - one **strength** per term, shared by the whole world;
  - one **inverse mass** μ per situation (the object is unseen, so each situation gets its own).
- Motion: ẍ = μ·(H(u)·[t < T_push] + Σ s_i·φ_i(x, ẋ)). Here H is the hand law learned in the nursery.
- **The idea space S_K** for a world: the empty family, every single idea, and every pair of ideas; 67
  families in the school's grammar. The checker enumerates S_K itself from the grammar, so a certificate cannot
  leave a rival out.
- **Paths are simulated by the world's own method**: RK4 at the world's integration step. This is
  compiled with numba, so the model adds no discretization error of its own.

### 3.2b Changes made while building M1a (2026-09-22)
- **The prequential predictive is a Laplace step.** A throw is predicted from the running Gaussian posterior
  by re-optimizing its own numbers: coefficients and its object's inverse mass. The starts are a
  linear-regression guess and a coarse mass scan. The posterior is then updated recursively.
  - The first version, a linearized predictive, scored −1.4 million for every family, because a spring's phase
    depends nonlinearly on mass.
- **Familiar objects.** A new object's inverse mass is predicted from a mixture: an object already met in this
  world (Chinese-restaurant weights) or a new one (the nursery prior). This cut the cost of learning each
  object's mass from about 7 nats to about 1.
- **Tried and reverted:** scoring only an object's second push. The teacher's second push always goes the
  other way, so the scored data covered half the scope, and the band grew to 4–15,000.
- **Bumps: one shared outlier density** b(y) (every reading N(0, 1)), instead of integrating over pulses:
  - numerator per throw: (1 − ρ)·q_clean + ρ·b, a proper density;
  - denominator per throw: N(y|θ) + ρ·b, an upper bound on the clean density;
  - a bumped throw scores about ρ·b under every family, so it cancels out and does not update the posterior;
  - the fits use each throw's clean-component responsibility as its weight.
- **Choosing the claim after seeing the data costs a factor |S_K|.** The threshold is log(|S_K|/α) = 11.1,
  not log(1/α). OP1's note that there is "no penalty for many rivals" was wrong when the claimed family is
  picked by the data; it is corrected there.
- **A cheap screen in `certify`.** A rival whose prequential score is within the threshold of the claim's
  fails the claim at once, because a marginal likelihood never exceeds the maximum likelihood. Rivals are
  fitted only when needed.
- **The smooth basis drops functions the family already has** (a constant, x, v). Without this the band was
  infinite for the slope.
- **C11 fixture bug (found 2026-09-24 from the seed-1 run on `bf4b536`).** The "other family" forgery was fixed
  as `speed-growing`, which is the true family of the C11 water-drag fixture. So that "forgery" was the genuine
  certificate, and the checker was right to accept it. The forgery now uses the first family in the space that
  differs from the claim and does not contain it. The assertion (every forgery rejected) is unchanged.
- **C6 was vacuous (found 2026-09-24, seed 1 on `d5b3b48`).** Every share of "sure" was 0, because with the
  teacher's pushes only the bands (0.16–0.45) never fit under ε ≤ 0.2. The ε grid is now 0.3/0.5/0.8, and C6 also
  requires a non-zero share at the strongest signal, a stricter assertion. Nothing was loosened.
- **Harness speed (2026-09-24, numbers unchanged):**
  - 12 workers (`CORE_WORKERS`), up from 8;
  - C11's forgeries are checked in parallel;
  - C1's coverage worlds run in parallel;
  - C6 builds each (noise, world) ledger once and certifies it at all three ε. Before, it rebuilt the same world
    for each ε.

### 3.3 The likelihood of a throw (the honest noise model; see 3.2b for the version built)
- Readings have independent Gaussian noise: σ_x = σ_v = 0.001, the nursery's sensor calibration.
- **Occasional bumps** (someone knocks the object) are part of every family's noise model:
  - p(y|θ) = (1−ρ)·N(y | path_θ) + ρ·p_bump(y|θ);
  - p_bump integrates over a pulse of 0.2 s at an unknown start, with amplitude ~ N(0, 2²). The start is
    summed over a grid; the amplitude is integrated by a Laplace approximation;
  - ρ = 0.05 comes from the nursery, where about 1 situation in 20 was bumped.
  - The bump term is computed only when the plain fit leaves a large residual. Elsewhere it is negligible and
    is dropped the same way for every family.

### 3.4 Evidence (D1)
- **E-process of A against a rival B:**

  log E_t(A:B) = Σ_{j≤t} log q_A(y_j | y_<j) − sup_θ Σ_{j≤t} log p_B(y_j; θ)

- **The prequential predictive q_A.** Strengths come from the earlier throws (their maximum-likelihood fit).
  The throw's own μ comes from earlier throws of the same situation; for a situation's first throw, μ is
  integrated over a broad prior (inverse mass in [0.2, 3]) by a Laplace approximation.
- **The denominator** is B's joint maximum-likelihood fit over all throws so far: strengths plus every μ, by
  Gauss–Newton.
- **When it is checked:** at the end of each situation, and before any "sure". Ville's inequality holds at any
  stopping time, so checking less often keeps the guarantee.

### 3.5 The certificate (D2), claim "A, within ε, over scope S", with α = 10⁻³ and δ = 10⁻³
1. **Rivals ruled out:** log E(A:B) ≥ log(1/α) for every B in S_K that does not contain A.
2. **Nested rivals bounded:** for each B = A + one more term ψ, a time-uniform interval for ψ's strength.
   This is the universal-inference confidence sequence: the strengths c with
   log L_t(c) ≥ log Q_t − log(1/δ), the other numbers profiled.
3. **"Something else" bounded:** a flexible family F = A + Σ c_k b_k(x, v) with a fixed smooth basis
   (tensor Legendre polynomials up to degree 2 in scaled x and v; 8 terms besides the constant). The same
   confidence sequence, in its ellipsoid form, gives
   sup |Σ c_k b_k| ≤ |bᵀĉ| + r·√(bᵀ I⁻¹ b) on a grid over the scope, and it must be ≤ ε everywhere.
4. **Scope:** the box of (x, v) actually visited, from the 2nd to the 98th percentile of readings, plus the
   range of pushes.
   **D10 (2026-09-24):** plus the lattice cells (25 × 25 over that box) holding at least 2 readings; the claim and
   the band (part 3) cover only those cells.
- **Assumptions written into the certificate:** the noise model (σ, ρ); the truth lying in F up to a
  negligible remainder; the scope.

### 3.6 The checker (pure functions, no access to learning state)
- `check(certificate, throws, grammar) → (accepted, reasons)`. It:
  - enumerates S_K;
  - recomputes every e-value, interval, band and scope from the stored throws;
  - rejects any claim the numbers do not support, or any missing rival.
- **C11 forgeries:** altered readings; a missing rival; a widened scope; a changed product; a claimed interval
  narrower than recomputed; ε smaller than the band; a certificate for other throws.

### 3.7 "Something else" and growth (OP3)
- **The alarm:** log E(F:A) ≥ log(1/α) means "something else is here", and the growth search starts.
- **Growth candidates** (a new term from the grammar, a number per object or per place) are tested the same
  way, with e-BH when there are many.

## 4. The loop (M1b), per world
1. For each situation, the mind makes the teacher's pushes. If surprised (the certified law, or the leading
   law, predicts badly), it imagines ideas in the order its gut ranks them.
2. It keeps a leading family and live rivals. It chooses its own pushes (at most 3 per situation) by the
   expected log-evidence gain against the strongest live rival, simulated on copies (relentless's
   `best_test`, with the new evidence).
3. It says "sure" only with an accepted certificate. Otherwise it names what is still open: a rival not yet
   ruled out, a nested term's interval, or the band.
4. **The library** records each certified claim with its certificate, scope, history and name. Claims are
   never overwritten. A failure outside the scope narrows the scope and starts a new claim (C4).
5. **Sentences** reuse relentless's `SENTENCE` table and add the numbers: "any extra v² term is between −0.02
   and 0.03", and "within ±ε over speeds 0.1–0.9".

## 4a. M1b details decided from the M1a runs
- **Richer actions.** Look-alikes such as "x" versus "sin x + x³/6" or "v" versus "sin v + v³/6" cannot
  be told apart by the teacher's pushes, which are already at full strength. So the mind's own action is a
  push *program*: up to three segments (start, end, command).
  - This allows long pushes, and pumping in time with the motion (as on a swing) to build amplitude beyond
    what one push reaches.
  - The simulator takes the segments as arrays, and teacher pushes become one segment.
- **Choosing an action.** Maximize the expected log-evidence between the leader and whatever blocks its
  certificate (the strongest unbeaten rival, or the nested term whose interval is widest). Evaluate the menu
  on copies with posterior means: ½·‖(f_A − f_B)/σ‖².
  - The menu: single pushes of 0.2–1.2 s at ±0.5 and ±1, and two-segment reversals timed from the leader's
    predicted velocity zero-crossings.
- **Budget:** up to 3 own actions per situation, as the relentless robot had.
- **Invention (for the surprise).** When the alarm fires, search an extended grammar and test each candidate
  by prequential replay on the stored throws, with the threshold using the enlarged space's size:
  - products of pieces (position-shape × speed-shape);
  - powers |v|^p and |x|^p;
  - a time-dependent drive sin(ωt);
  - a second per-object number.

  The residual shape of the flexible fit (which Legendre terms dominate) orders the candidates. This is
  "seeing the gap and imagining how to fill it".

## 4c. The author's "many ideas at once, thin trace, train on the trace" idea (2026-09-22)

The author proposed this during M1b, and it is built faithfully.
- **Imagine many at once, test on the spot.** There are two tiers:
  - **Imagination tier (fast, approximate):** hundreds of candidate ideas, including the extended grammar of
    §4a, are scored together from the measured accelerations by linear least squares in one matrix
    operation. It is used for ranking only, and is about 1000× cheaper than the exact tier.
  - **Testing tier (exact):** the top ideas enter the ledger (path likelihood, e-process), and only the
    checker can make one "sure". This is the speed-up within the same bottleneck.
- **The trace.** After each situation, every imagined idea leaves a trace weight: softmax of its evidence
  score (exact when tested, approximate otherwise), with a small floor ("a very thin trace" for weak ideas,
  so they can come back). Strong ideas leave a thick trace.
- **Training on the trace.** The gut learns to predict the trace weights from the leftover's picture
  (cross-entropy to soft targets).
  - This is expert iteration with soft targets, as AlphaZero trains its policy on MCTS visit counts.
  - Guided at first: a teacher's correction puts a heavy trace on the right idea.
  - Later it trains on its own traces.
- **The guard.** Trace weights come from evidence against the world (prequential scores), never from its own
  confidence. So training on the trace is learning from the world. This avoids v14's self-confirmation
  trap and follows D3.
- **The author's rule (2026-09-22): no training on real-world data in real time.**
  - During a world the trace is only recorded.
  - Training happens afterwards, and only on what was checked:
    - claims the checker accepted;
    - the teacher's corrections, with their deciding evidence.
  - Anything unchecked stays in the trace but does not train the gut.
  - The foundation grows one checked step at a time: a certified claim or a corrected mistake.
- **The test:** in the §4b experiment, one arm trains its gut on the trace and another on answers only. The
  measures are tries, exact-tier compute per discovery, and first-try success on never-shown kinds and on
  the surprise.

## 4b. The first experiment: the author's "correct, teach why, master, then surprise" protocol (2026-09-22)

The author proposed this during M1a, and it is tried faithfully. It becomes T3's main protocol.
1. **Try.** The mind proposes its answer for a practice world.
2. **If wrong, correct it and teach why.** The teacher gives:
   - the right family;
   - the evidence that decides between them: the throw where the mind's idea failed most, the shape of the
     leftover there (along speed or position, rising or steady), and the e-value against its idea.

   The gut learns from the evidence (symptom → idea), not just from the answer.
3. **Master it.** It keeps getting worlds of the same kind until it solves one unaided. Help fades per kind,
   by success.
4. **Repeat** for several kinds.
5. **Surprise.** Worlds whose law nothing taught can express, each needing something new:
   - a new ingredient (a product x·v, or a power like v^1.5 beyond what the pieces approximate);
   - a hidden property of each object (a second number per object, like charge);
   - a force that depends on time (a hidden motor).

**Scoring:**
- Before it invents anything, it must say "something else is here", never sure-and-wrong.
- Then: does it invent a term or concept that the checker certifies, and how many tries does that take?

**Arms:**
- answer-only teaching (the school's way);
- correct-with-why plus mastery (the author's);
- no teaching;
- the author's protocol plus invention episodes in practice (practice that sometimes requires growing the
  grammar). This tests whether "learning to invent" transfers to a new kind of invention.

## 4d. The teaching layer (B2, 2026-09-24): School, Caretaker, Stigmergy

The author asked for three teaching principles, applied to the mind (the learner) and never to the truth layer:
- **curriculum design** (simple worlds first, complex later);
- **caretaker vocabulary** (a word at the moment of resistance, never a definition);
- **stigmergy** (the environment is the memory; place challenges where the flaws are).

Nothing here can make a claim "sure": only the checker does that. Everything here only orders search and chooses
worlds.

### 4d.1 The School: one persistent mind, many worlds (`school.py`)
- **A life** is a sequence of worlds chosen by the curriculum. The mind lives each one (`Mind.live`). After each
  world it learns, only from checked outcomes:
  - the **outcome** o of a world is the family in an accepted certificate (the checker ran through
    `Library.record`), or the family a teacher correction names;
  - otherwise the outcome is `unchecked`, and nothing learns from that world.
- **What persists** across worlds: the gut, the lexicon, the board, the library (certified claims) and the mastery
  record. Laws are not carried between worlds; each world has its own hidden law, as in the school.
- **Tries.** At the start of each world, after its first situation, the gut ranks the 67 families. **Tries** is the
  rank of the true family (1 = first try right). A world with a hint counts as hinted, not as a try.
- **Zero-shot:** the share of never-shown worlds (thick oil, valley) where the true family has rank 1, with no hint.

### 4d.2 Curriculum (`curriculum.py`)
**Stages** (kinds are force names; pairs are two forces at once):

| Stage | Kinds | What it asks |
|---|---|---|
| S0 ice | `none` | Only its hand and the objects' masses: the claim "nothing but my hand" |
| S1 linear | rubbing, spring, slope | One straight law |
| S2 nonlinear | water drag, dry friction, tight spring, stiff spring, swing | One bent law |
| S3 pairs | rubbing+spring, slope+dry friction, water drag+spring | Two laws at once |
| S4 look-alikes | swing (small pushes), faint rubbing (strength 0.1–0.3) | Tell look-alikes apart with its own pushes, or say "not sure" |
| S5 surprises (B3) | x·v, v^p drag, motor, charge | Something no idea can say |
| Exam, never shown | thick oil, valley | Zero-shot |

**Mastery.** A kind is mastered when the mind certifies a world of that kind correctly with no hint. A stage
unlocks the next when all its kinds are mastered, or after 12 worlds in the stage.

**Order (a tournament entry each):**
- `ladder`: stages in order, kinds round-robin within the unlocked stage;
- `progress`: among unlocked kinds, the one with the largest recent learning progress (the absolute change in mean
  tries over its last 3 worlds versus the 3 before), with 20% uniform exploration;
- `random`: all kinds from the start, uniformly (the "dump everything" control).

**Pairs** are `MultiWorld`s: the same world layout with two ideas and two strengths.

### 4d.3 Caretaker and lexicon (`caretaker.py`, `lexicon.py`)
**The caretaker** is world-side. It sees the world's truth, and the mind's public events only.

**Events:**
- E1: the alarm fired;
- E2: a situation ended with the leader not certified because a rival blocked it;
- E3: a teacher push moved the object more than 5σ away from the mind's prediction (resistance).

**Words:**
- **Regime words**, one per force, from a fixed table: rubbing "rough", water drag "wet", dry friction "sticky",
  thick oil "gooey", spring "springy", tight spring "tight", stiff spring "stiff", swing "swingy", valley "bumpy",
  slope "downhill", none "free".
- **Mass words:** "heavy" (mass above 2.0) and "light" (mass below 0.9), for the object of the situation.
- **Fillers:** "look", "nice", "oops", "again", said at random in 20% of situations.

**Arms:**
- `timed`: the regime word at the world's first E1/E2/E3 event; a mass word at the E3 of an extreme object's
  situation.
- `random`: the same number of each word, at uniformly random situations over the whole life (so often in the wrong
  world).
- `none`: no words.
- `definition`: a labelled reference, not an entry. The lexicon is handed the word-to-family table at the start.

**The lexicon is a betting market on checked outcomes.**
- For word w, after each checked world j: h_j = 1 if w was heard in world j, o_j = the outcome.
- The word bets on "hearing w depends on the outcome". Its log e-value is:
  - log E_w = Σ_j log q(h_j | o_j, past) − sup_π Σ_j log Bern(h_j; π);
  - q is a Beta(½, ½) (Krichevsky–Trofimov) predictive of h, kept separately for each outcome.
- Under the null (the word is said independently of the outcome, as fillers are), E_w is an e-process: it is
  universal inference, the lab's own evidence form.
- **Grounded** when log E_w ≥ log(|V|/α), with |V| the vocabulary size and α = 10⁻³.
- **Gut prior** from grounded words: log P(o | heard words) up to a constant = Σ_w log q(h_w | o) (naive Bayes over
  the same counts).
- **Mass words** keep the mean and spread of log μ̂ over the checked situations where they were heard. They are
  measured by predicting a new object's first push. They never enter the ledger.

### 4d.4 The board: stigmergic memory (`board.py`)
**A file outside the mind** (JSON in the life's folder), read by the gut, the experiment chooser and the curriculum.

**Trails** τ[idea], one per idea:
- start at 1;
- after each world: τ ← max(τ_min, (1 − ρ)·τ), with ρ = 0.1 and τ_min = 0.05 (the author's "thin trace": weak ideas
  never vanish);
- **deposits:** +1 per idea of a family in an accepted certificate (the deposit must carry the certificate digest
  that the checker accepted); +0.5 per idea of a family in a teacher correction (it must carry the correction id).
  A deposit without a valid id is refused.

**Hotspots:** an 8×8 grid over the scope in normalized (x, v). When the alarm fires, the alarm's log e-value is
spread over the cells where the leader's misfit is largest (the top 10% of cells). Hotspots evaporate like trails.

**Look-alike marks:** at the end of a world, a (leader, rival) pair that blocked the certificate with
|Q_A − Q_B| < log(|S_K|/α) gets +1. The marks evaporate.

**Placement** (curriculum, a tournament arm) reads only the board, never the world's truth:
- the strongest look-alike mark (≥ 2) puts the next world of that kind in the "large-amplitude" template: the
  mind's menu gains 1.6 s pushes and commands ±1.5 (the longer rail and the stronger hand);
- the strongest hotspot at high |v| puts the next world in the "fast" template: the teacher's pushes at ±1.0 only;
- otherwise the curriculum's own choice.

### 4d.5 The gut and the teacher (`gut.py`, `teacher.py`)
**Features of family F:**
- the fast-tier fit gain on the first situation's accelerations (central differences; least squares of
  a = μ·H(u)·1[t < T] + Σ_i c_i φ_i over F);
- Σ log τ over F's ideas;
- the lexicon prior;
- |F|;
- one bias per idea.

**Scoring and training:**
- score s_F = θ·features(F); softmax over the 67 families;
- trained after each checked world by cross-entropy on the outcome (learning rate 0.1);
- plus the §4c trace (the soft targets are the softmax of the world's exact prequential scores Q), used only when
  the world was checked.

**The teacher (§4b protocol).** Help per kind: level 2 (show the family before the world), 1 (say its input:
"along speed"), 0 (none). A kind drops a level after each unaided correct certification.

**Arms:**
- `none`;
- `answer`: after each world, give the right family;
- `why`: if the mind's claim is wrong or unsure, give:
  - the right family;
  - the deciding throw: the one where the leader and the truth separate most;
  - the leftover's shape there;
  - the e-value log E(truth : leader).

  The gut then also trains on the deciding throw's features (symptom → idea), and the kind is repeated until it
  is mastered.

## 5. Checks, made concrete (in `core_check.py`)

| Check | World and data | Pass |
|---|---|---|
| C1 honest noise | 20 school worlds per seed: 95% predictive intervals of held-out readings under the certified law; pure-noise worlds (hand only, no hidden force) | Coverage 93–97%; in noise worlds 0 "sure" of any force term and 0 growth |
| C6 humility sweep | One world family at noise × {1, 2, 4, 8} and ε × {0.3, 0.5, 0.8} (changed from {0.05, 0.1, 0.2} on 2026-09-24: those were all below the bands, so the check was vacuous) | The share of "unsure" rises monotonically as the signal weakens; at least one "sure" at the strongest signal (added 2026-09-24); 0 sure-and-wrong everywhere |
| C8 omitted mechanism | A force outside S_K (v^1.5 drag, or x·v) | "Something else is here" in ≥ 95% of worlds where it exceeds ε; the prediction error is no worse than before the alarm |
| C10 temptation | A world whose score rewards an early "sure" | "Sure" only with an accepted certificate; 0 sure-and-wrong |
| C11 checker | ≥ 20 forged certificates; attempted writes from learner code | 100% rejected; writes impossible (the checker takes copies, holds no references, is a separate module) |
| C2–C5, C7, C9 | Written in M1b–M1d | As Architecture §12 |

## 6. Seeds and runs
- **Dev seeds 1–10; fresh seeds 11–20, run once** (the "core" track).
- `PYTHONHASHSEED=0` in every runner.
- Every check runs twice and the results must match (D5).
