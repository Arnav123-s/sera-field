# Open problems on the road to the vision: status and the development attacks

*Working index, 2026-09-22. The author asked that open problems be tackled and solved, not avoided. Each entry
gives:*
- *the problem;*
- *what is known, from the dives and checked sources;*
- *the candidate answer;*
- *the test that would show it works.*

*Dive X6 surveys the literature on all of them. Its findings are merged in after they are checked.*

| # | Open problem | Candidate answer | Test | Status |
|---|---|---|---|---|
| OP1 | An honest "sure" when the truth may be outside every idea it can form | A four-part certificate: rivals ruled out by an anytime-valid e-process; rivals that contain the law bounded by confidence sequences; "something else" bounded by a smooth-residual band; scope stated. See `OP1-honest-sure.md` | T4, M1 | Candidate; simulated: never sure-and-wrong in any case, at a cost in samples (`OP1-honest-sure.md`) |
| OP2 | Keep improving after the teacher leaves, without fooling itself | "Dream school": self-made worlds with exactly known answers (below) | T2, T3, M1 | Candidate; probed in the school world on dev seeds, fresh seeds 61–80 registered (below) |
| OP3 | Grow a new concept (like mass) or term (like drag) without ever growing on noise | Growth as an anytime-valid test of the grown family against the current one (below) | T5, M2–M3 | Candidate; simulated: 0 of 20,000 growths on noise vs 29% for the current form (below) |
| OP4 | See two laws as one (Maxwell) and learn faster from it | Anti-unification of program trees, plus compression gain (dive J9) | M4 | J9 checked: anti-unification and structure mapping verified; design in Architecture §8 |
| OP5 | Grounded, compositional word meaning without pretrained models | Words as program pieces, learned across scenes (dive J10) | M5 | J10 checked; design in Architecture §9 |
| OP6 | Measuring discovery: novelty, routes, "right imaginings" | Definitions in plan §4.3; to check against the creativity and quality-diversity literature (X6) | all | Mapped onto creativity research (fluency, flexibility, originality, appropriateness): `BEHAVIOR.md` §4, decision D7 |
| OP7 | Self-improvement with guarantees | Self-edits accepted only through the checker and fresh-seed tests (dive J12) | M9 | Waiting for J12 |

## OP2: dream school, improving after the teacher leaves

**Why the lab's learner stopped** (corrected 2026-09-22; an earlier version said credit had stopped,
which was wrong).
- In the school, the teacher kept revealing answers and giving credit after every practice world, even
  after the hints ended at world 24.
- Over the last 16 practice worlds the taught learner still needed about 4.6–4.9 tries, with no downward
  trend. Its gut put the right idea first 31–34% of the time.
- A gut trained on **all 1,600 practice answers at once** reached **64%** (`legacy/RESULTS.md`, school section).
- So the limit is **how much practice it gets and how slowly its local rule learns from it**, not missing
  credit.
- For *new* forces even that best gut scored **0%**. Practice on known kinds cannot point at new kinds.

**The trap to avoid: self-credit.**
- Paying itself for ideas that only seemed right made it sure and wrong (ccops5 school).
- Training on its own guesses shrinks uncertainty without moving a wrong answer (the author's v14 THEORY §3).

**The candidate: dream school.** The mind becomes its own teacher on *made-up* worlds, where the answer is
exactly known because it made the world.
1. **Dream up a world.** Pick a law from its library plus the grammar. Include new combinations it has never
   kept, so dreams reach beyond what it already knows (as in DreamCoder's dreams).
2. **Solve it.** Simulate the world with the mind's own noise model. Let the mind discover the law with its
   normal loop: gut, experiments, certificate.
3. **Grade it exactly** against the known answer, and pay credit to the gut and to the test-chooser:
   - the rank the true idea had;
   - throws spent;
   - false "sure" claims, heavily penalized.
4. **Keep dreams out of the evidence.** Dreams never touch the evidence about the real world. They are
   tagged *model-conditional* and may train only the search (the rule in the author's v14 notes).

**Why it should work.** Dreams give unlimited practice with exact answers, the thing that took the best gut
from 31–34% to 64%. This is self-play: AlphaZero trains on games it plays itself, where the rules
guarantee the scores are true. Here the world-program guarantees the answer is true.

**The risk.** Dreams drawn only from what it already knows make it faster at old kinds of laws, not new
ones. The dream generator must also sample laws it has never kept.

**The test (T3).** After the teacher leaves:
- tries on **fresh real** worlds keep falling with dream school, against the same mind without it;
- zero-shot first-try accuracy on never-shown kinds rises;
- sure-and-wrong stays 0.

### First probe in the school world (`research/op2_dreams.py`, 2026-09-22)

**Setup.**
- The school's taught learner lives its usual 40 practice worlds, then gets 120 extra worlds in one of five
  arms, then the same 12-world exam: 8 familiar forces and 4 never-shown ones (thick oil = cubic in speed;
  valley = steps in position).
- The arms:
  - `none`: nothing more;
  - `extra_real`: 120 more real practice worlds, graded by the teacher (a reference);
  - `dreams_known`: 120 dreams of the kinds of force it practised;
  - `dreams_all`: 120 dreams from its whole grammar (every shape along position or speed, plus the steady
    push), including combinations it never kept;
  - `dreams_mixed`: each dream is from the practised kinds half the time and from the whole grammar half the
    time. It was added after the first dev run.
- Dreams are graded exactly against the law the learner planted and train only its hunch (search).
- The exam worlds, objects, pushes and noise are identical in every arm.
- "Tries" = the rank of the right idea when it was found (12 if never found).

**Dev seeds 1–10.** Paired: each arm minus `none` on the very same exam worlds.

| Arm | Familiar: change in tries | Never-shown: change in tries | Right idea first (all exam) |
|---|---|---|---|
| none | – | – | 20% |
| extra_real | −0.46 ± 0.33 | −0.68 ± 0.50 | 31% |
| dreams_known | −0.17 ± 0.33 | −0.97 ± 0.55 | 24% |
| dreams_all | **+0.95 ± 0.57** (a cost) | **−1.52 ± 0.60** | 28% |
| dreams_mixed | +0.04 ± 0.46 | −0.95 ± 0.51 | 29% |

Rerunning with `PYTHONHASHSEED=0` reproduced the first four arms exactly.

**What dev suggests.**
- Dreaming beyond what it kept helps most on never-shown kinds, and costs skill on familiar kinds: the practice
  is spread over more kinds, and credit pulls the hunch toward the unusual.
- Mixing removes the familiar cost and keeps about two-thirds of the gain.
- Caveats:
  - This grammar is tiny (11 ideas). So `dreams_all` covers the exam's never-shown kinds outright, which it
    cannot do in a large grammar.
  - The effects are about 2 standard errors on 10 seeds.
  - "Sure but not right" is 8–12 claims per arm under the school's old rule. That is D2's job, not dreams'.

**Frozen for one fresh run** (registered before running: school seeds 61–80, never used).
- **The design:** the five arms, 120 extra worlds each, and this exam, unchanged.
- **Predictions**, each judged by a 95% interval (mean ± 1.96 SE) of the paired change against `none`:
  1. `dreams_all` lowers never-shown tries, with the interval below 0.
  2. `dreams_all` raises familiar tries, with the interval above 0.
  3. `dreams_mixed` lowers never-shown tries, with the interval below 0, and its familiar change stays below
     +0.3.
  4. No arm brings "sure but not right" to 0.
- Whatever comes out is reported as it is, with no retuning.

**Fresh seeds 61–80, run once** (`research/op2-fresh.json`, `op2-fresh.log`). Each arm minus `none` on the same
exam worlds: 160 familiar and 80 never-shown exam worlds per arm.

| Arm | Familiar: change in tries | Never-shown: change in tries | Familiar found | Right idea first |
|---|---|---|---|---|
| none | – | – | 83% | 22% |
| extra_real | −0.47 ± 0.27 | −0.09 ± 0.39 | 85% | 24% |
| dreams_known | **−0.56 ± 0.26** | −0.07 ± 0.36 | 84% | 26% |
| dreams_all | +0.33 ± 0.41 | **−1.15 ± 0.47** | 74% | 28% |
| dreams_mixed | −0.34 ± 0.32 | −0.36 ± 0.45 | 82% | 29% |

**The predictions, judged as registered:**
1. `dreams_all` lowers never-shown tries: **confirmed.** The interval is −2.07 to −0.23; on dev it was −1.52.
2. `dreams_all` raises familiar tries: **not confirmed.** The interval (−0.47 to +1.13) includes 0, though its
   familiar found-rate fell from 83% to 74%.
3. `dreams_mixed` lowers never-shown tries: **not confirmed.** The interval is −1.24 to +0.52. Its familiar
   change (−0.34) did stay below +0.3.
4. No arm reaches 0 "sure but not right": **confirmed** (13–17 per arm).

Not predicted:
- **Dreams of known kinds helped on familiar forces** (−0.56 ± 0.26), as much as 120 extra real worlds did
  (−0.47 ± 0.27).
- **They did not help on new ones.** The dev gain on new forces (−0.97) did not replicate.

**What this means for dream school (D4).**
- **What a dream reaches is what improves:**
  - dreams of known kinds build skill on known kinds, like real practice;
  - only dreams beyond the library improve zero-shot on new kinds.
- In this tiny grammar, "the whole grammar" happens to contain the exam's new kinds. In a large grammar it
  cannot.
- **So the dream generator must choose *which* unkept combinations to dream about.** The candidate is
  abstraction: anti-unifying its certified laws gives general forms such as "shape along an input", and their
  unkept instances ("cubic along speed") are what it dreams about. That is the next probe.
- A fixed 50/50 mix was a weak compromise. The share of dreams beyond the library should follow learning
  progress per family.

## OP3: growth that provably never fires on noise

**Growth as a test.** Growing means rejecting the current family in favour of a bigger one: a hidden number
per object or per place, or a new term. Use the same machinery as the certificate:

E_t(grown : current) = ∏ q_grown(y_j | y_<j) / sup_θ ∏ p_current(y_j ; θ)

- The numerator predicts each throw with the grown family fitted to earlier throws only.
- The denominator is the current family's best fit to all throws so far.

**The guarantee.** If the current family is true (nothing new exists), P(ever grow) ≤ α by Ville's
inequality. That is the answer to "never grow on noise", with a stated rate. When something new is real,
E_t grows exponentially, so growth comes quickly.

**Where the leftover belongs.**
- Test each candidate against the current family: per object, per place, per pair, or a new term from the
  grammar.
- Among those that pass, prefer the one that predicts new throws best, and state near-ties honestly as
  look-alikes. For example, a steady push on each ball against a faint wind.
- Then design the experiment that separates the look-alikes (job 8).

**How this relates to the author's ideas.**
- It is the *coboundary* idea made exact: grow exactly where the current family's contradictions pile up.
- It tests the Wetterich / Betti-void idea on the same worlds, as a rival growth trigger in T5.

**The test (T5).**
- In pure-noise worlds, growth fires in ≤ α of lives.
- Unannounced drag is grown within a stated number of throws.
- Mass (per object) is grown in the ball world and density is not, unless a push pins it.

### First evidence: a simulation (`research/op3_sim.py`, 2026-09-22; table in `research/op3-results.txt`)

**The setup.**
- A 1-D drag world with 4 objects. Each reading comes from a random object: a = −θ_object·v + noise,
  σ = 0.05.
- **The current family:** one number shared by all objects.
- **The grown family:** one number per object, a hidden quantity like mass.
- The mind checks after every reading and grows at its first "yes", up to 400 readings.
- The e-process predicts each reading from earlier ones only: the object's own estimate, shrunk toward the
  pooled one.

| Truth | Rule | Grew | Median readings to grow |
|---|---|---|---|
| Objects all the same (growth would be on noise) | in-sample, threshold 9 (the lab's form) | **29.2%** of 20,000 lives | 44 |
| | **e-process, α = 10⁻³** | **0 of 20,000** | – |
| Faint differences (θ = 0.95–1.10) | in-sample | 100% | 14 |
| | e-process | 55% within 400 readings | 220 |
| Clear differences (θ = 0.8–1.5) | in-sample | 100% | 5 |
| | e-process | 100% | 34 |

**What it shows.**
- The same pattern as OP1. The lab's current form of evidence grows a fake hidden number in about 3 lives in
  10 when it may stop at any time. The e-process never did.
- **The price is readings:** about 7× more when the difference is clear. When the difference is faint, it
  detects about half within the budget; the other half is "not yet", never "no".
- The shrinkage constant (KAPPA) affects only the speed, not the guarantee. A better prequential predictor
  (a Bayesian mixture over shrinkage) could buy back some of the speed. That is future work.
