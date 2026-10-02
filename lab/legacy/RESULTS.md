# ccops5 lab: what happened, explained simply

**Built as an isolated experiment.** Numbers come from `legacy/nursery/results/TABLES.md` (seeds 1–3, the seeds used while
building). A second run on fresh seeds 4–6, never looked at while building, is in `legacy/nursery/results-fresh/`.

**How to read a "miss":** 0 is a perfect guess of where a toy goes; 1 is as bad as guessing it never
moves. A miss of 0.004 is 0.4% off; 0.39 is 39% off.

## The story of one life

Imagine a baby robot in a playroom. It cannot see inside things. It can only push them and watch
where they go, with slightly blurry eyes.

1. **Its own hand, like learning to hold a spoon.** At first it knows nothing, not even how its hand
   works. It waves the hand around (babbling) and is surprised every time. After 5 surprises it makes
   up an idea: "the harder I send the command, the more it moves." It does not trust the idea yet.
   Only after the idea is right 3 more times does it keep it for life. That took 8 tries, in every life.
2. **Toys on ice.** With its hand idea it works out how heavy each toy is. It remembers a toy after
   2 good guesses. Soon it guesses where a toy will go *before touching it*, only 0.5% off.
3. **Toys on carpet: a surprise.** The toys slow down, and its ideas cannot explain it. After 5
   surprises it imagines 7 possible reasons: it depends on where the toy is, how fast it goes, how
   hard it pushes, or some mix. It tests each reason on examples it hid from itself. "How fast"
   wins. That is rubbing, and nobody told it.
4. **Toys in water.** Another surprise. It finds a new speed idea, and the shape it learned matches
   real water drag (speed × speed) at 0.996 to 0.999 out of 1.
5. **Springs.** A new idea that depends on *where* the thing is. It matches the real spring at
   1.000 out of 1.
6. **Swings: no new idea needed.** The spring idea already explains swinging. It proposed nothing
   new, and the spring idea did most of the explaining (its strength was about 280 times its
   uncertainty). One idea explains two different-looking things, like Maxwell seeing electricity
   and magnetism as one.
7. **New toys, words only.** While it played, a caretaker sometimes said "heavy", "light", "rough",
   "smooth", "flat", "round". Nobody told it what the words meant. Later it met brand-new toys and
   heard only the words. Its guess from the words was 14% off; guessing from the place alone was 22%
   off; an ordinary neural network given the same words was 42% off. The words got their meaning
   from touching.
8. **Toys stuck together: math and proof.** Old toys were glued into pairs. It had 7 ideas for how
   the parts' numbers make the whole's numbers. Only one survived the world's checks, after just 3
   pairs: "one-overs add up", which means *heaviness adds up*. Then it worked out glued **triples it
   had never seen**, before touching them. It was 0.7% off. Guessing from the place was 151% off, and
   the ordinary network 25% off. That is math (a rule) plus proof (reasoning from checked facts,
   then checking the answer) plus physics, working together.
   *Correction (after an independent review):* the learner is told which toys a glued thing is made
   of; the ordinary network at first was not. So I gave the network the parts too, in two ways
   (seeds 1–3, then fresh seeds 4–6, triples before touching):
   - parts added up into its input: 34% and 47% off, which is *worse* than without the parts (25%, 22%);
   - each part read by its own small network, then added (a "deep sets" network, the fair standard):
     28% and 26% off. It helped on pairs, which it practised on (31% → 23%, 43% → 30%), not on triples.

   The gap holds: 0.7% and 1.1% for the learner. But the learner's "math" is a choice among 7 rules
   I wrote, so this shows that choosing and checking a rule carries over to triples; it does not show
   that the rule was invented.
9. **Final check.** It still remembered every old toy in every place: 0.4% off before touching.
   The ordinary network, by then, was 39% off. It had forgotten.

## Cutting one wire at a time

| Learner | Before touching, while learning | After its pushes | Final check | Words | Stuck triples |
|---|---|---|---|---|---|
| Everything connected | 1.1% | 0.8% | 0.4% | 14% | 0.7% |
| Forgets after every situation (like CORE-022) | 100% | 0.7% | 100% | 100% | 100% |
| Wipes everything | 100% | 100% | 100% | 100% | 100% |
| May not grow new laws | 100% | 45% | 100% | 100% | 0.7% |
| Ordinary neural network | 27% | 3.1% | 39% | 42% | 25% |
| Ordinary network, reading each glued part (deep sets) | 25% | 3.5% | 43% | 38% | 28% |

What this means:

- **Forgetting kills everything that needs memory.** The learner that forgets after every situation
  still finds all four laws, and it guesses well *after* pushing. But before touching, it knows
  nothing, every time. Words, math and the final check all fail. This is the same illness the
  diagnosis found in sera-field: the memory is wiped between examples.
- **No growth, no progress.** Without new laws, carpet, water and springs stay unexplained (45%
  off). Stuck toys on ice still work, because ice needs only the hand law.
- **An ordinary network learns a little in the moment, then forgets.** It is 4 times worse after
  pushing, and 100 times worse at the final check.

## Honest surprises

- **Checking before keeping helped only a little here.** The learner that keeps everything
  unchecked did about as well. It stored all 7 secret bumps as knowledge, and on those bumped toys
  it was a bit worse at the end (1.0% vs 0.6% off). In this small world the good memories drowned
  the bad ones.
- **Throwing again differently helped only a little** (1.3% vs 1.1%).
- **Unifying saved effort, not accuracy.** The learner that could not reuse the spring law for
  swings grew one extra law and guessed just as well.
- **Some laws carry one input they barely need** (the hand law in seed 2 also looks at speed).
- **I changed the design after looking at results**; every change is listed in `README.md`. That
  is why the fresh seeds 4–6 matter: they are the fair test.

## What this does not show

- It is a tiny one-line world, not the real world, and it uses none of the papers' special field
  (Clifford algebra, sheaf, Cahn-Hilliard).
- A caretaker chooses the order of the lessons. It does not explore on its own.
- In this main lab it gets no credit for imagining, and its imagination does not get better with
  practice. The school, further down, tries exactly that.
- It keeps each toy's numbers per place. It has not yet found that a toy has one heaviness
  everywhere.
- It does not say its ideas in sentences or formulas.
- **The words test favoured my learner a little, and the gap held when that was fixed.** A brand-new
  toy's look means nothing yet; my learner sees that the look is unfamiliar and leans on the words,
  while the ordinary network had to take the unfamiliar look as input too. So I ran the network
  again without the new toys' looks (words and place only): 33% off on seeds 1–3 and 40% on fresh
  seeds 4–6, against 42% and 41% before, and 14% and 11% for my learner.
- **The rules and ideas come from menus I wrote** (7 glued-toy rules here, 11 force ideas in the
  school), and the worlds are built from the same pieces. Choosing well from a menu is not inventing.
  The invention school and the ball-throw test (being built by helper scripts) are meant to
  test that.

## What you are looking for, and how much your research supports it

From the interview on 2026-09-21. "Lab" means this experiment.

| What you want SERA to do | What your papers give | What the lab showed | Support |
|---|---|---|---|
| Find new laws by itself | Clear: grow a new dimension when error cannot be fitted (5 of 7 papers), and the shared "unannounced drag" test. But the growth math chosen (Wetterich flow) is never defined for SERA's data | Yes: found the hand, rubbing, water drag and spring laws, with no hints. In the invention school it joined known pieces into laws it was never shown, 38% of the time (0% for a menu robot) | Strong idea, weak math |
| See two things as one | Implied: stored laws bend how new things are seen, and one law serves five uses. No test for it | Yes: swings were explained by the spring law, with no new law | Implied |
| Grow like a baby and explore alone | The order is stated: body and physics first, repeat with variation, language on top. No curriculum and no drive to explore | Partly: it follows a given order; it only chooses its own pushes | Principle only |
| Be taught *how* to discover (puzzle worlds, fading hints, famous discoveries, harder step by step) | Not described | In the school: showing, fading hints and credit nearly halved its searching, and the skill carried over to forces it was never shown | Missing from the papers; works in the lab |
| Truly understand words | Language built on top of physical grounding; "explain in words" is one of the five uses. How words attach is not described | Yes, at a small scale: words got meaning from touching (14% vs 22% off) | Principle, thin mechanism |
| Concepts like mass: one hidden number, predicting the unseen, naming it, hidden causes | "Infer mass" is one of the five uses; hidden causes are what growth finds | Hidden causes, yes. Heaviness adds up, yes. One number for a toy in every place, no. Naming, no | Partial |
| Credit for imagination; imagination that improves | The papers disagree on the learning signal (echo, re-trial, or verification). Your lab's acceptance doc rewards novelty against what is kept. Nothing on imagination improving | In the school, credit from the world made its imagination better with practice. Without outside credit it grew sure and wrong. Points off for overconfidence helped a little | Weak, conflicting in the papers; works in the lab |
| Explain itself and prove its ideas, in sentences and formulas | "Explain in words" plus verification | Proof as derive-then-check, yes. In the school, the relentless robot says each idea in a sentence and a formula, with how sure it is and which rivals it beat | Partial: sentences come from a fixed phrase per idea |
| Humble but relentless: sure only when it has made sure | Verification, re-trial with variation, and bivalent marks. Nothing on how sure to be | The relentless robot, on 40 fresh lives: when it said "sure", it was right every time (463 of 463). Pushing where its idea could break found springs 90% vs 50% when easy pushes were too soft | Not in the papers as confidence; works in the lab |
| Physics, math and language linked; ideas from barely any hints (mass → black holes) | The central claim of the Unified Cognitive-Physical Substrate paper. No mechanism for leaps between fields | Linked inside one tiny world; no leaps between fields | Ambition, no mechanism |
| Measurements first, then video | Perception on the boundary field; no path from video | Measurements only | Missing |
| Is the special field needed? | Central to all seven papers, which also require a scrambled-topology control. Some parts cannot work as written (see the diagnosis) | The loop alone, without the field, produced the core behaviors in a tiny world | Open; can be tested now |

**Bottom line:** the loop your papers describe is the strongest part. Wired up, even with simple
pieces, it produced four of the behaviors you want, and every wire proved to matter. The things you
said matter most in the interview are mostly not in the papers yet: teaching how to discover,
credit for imagination, concepts shared across places, explaining itself, and exploring alone.
They are the next design work. For the loop, your papers are a design to build. For the special
field, they are hypotheses to test against this plain version.

## The fair test: three fresh lives

After all the changes, seeds 4, 5 and 6 were run once, with nothing changed afterwards (`legacy/nursery/results-fresh/`).
The story held:

- All three found exactly the four hidden laws. No wrong idea was kept, and none was proposed and
  thrown out.
- Words: 11% off from the caretaker's words, 23% from the place alone, 41% for the ordinary network.
- Glued toys worked out before touching: 1.0% off, against 143% from the place, 22% for the
  ordinary network, and 26% for the network that reads each part.
- Final check before touching: 1.0% off. The forgetting robot: 100%. The ordinary network: 43%.
- Swings were explained by the spring law again, with no new law.

## School: teaching it how to discover

The robot's inner system stayed the same: when surprised it imagines explanations and checks them.
It holds each one in doubt until it passes, and keeps only what passed. What it was taught is how to
*use* that system. The teaching went through 40 practice puzzle worlds, each a tiny new universe with
one hidden force. Laws were not carried between worlds; only the skill could carry over.

- **Watch** (worlds 1–8): at the first surprise, the teacher shows the right idea, like watching
  someone use a spoon.
- **Hints** (worlds 9–24): the teacher sometimes says what to look at ("look at the speed"), less and
  less often (80% down to 10%).
- **Alone** (worlds 25–40): no help.
- **Credit** after every world: the teacher reveals the answer and gives credit:

  | For | Credit |
  |---|---|
  | The right idea | +1 |
  | A partly right idea (right thing to look at, or right shape) | +0.5 |
  | A new idea that made sense | +0.25 |
  | An idea that did not fit | −0.25 |
  | Trusting a wrong idea | −0.5 |
  | Guessing well with what it kept | Up to +0.5 |

- **Its gut feeling (hunch)** chooses which 2 of 11 ideas to imagine when surprised. It changes by a
  local rule: credit × (what it felt − what it expected). Its confidence decides how many checks it
  needs before believing an idea: 1 if sure, 2 if not.
- **The exam** is 12 worlds with no help and no learning. Four of them hold forces it was never
  shown: "thick oil" (a speed force with a shape it had only seen on position) and "valley" (a
  position force with a shape it had only seen on speed).

The other robots lived the same worlds. "Credit only" had no showing and no hints. "Taught itself" had
no teacher and credited its own kept ideas. "Never taught" never changed its hunch.

**The humble robot** was added after your note on humility. It is taught the same way, but:

- Being sure and wrong costs points, the surer the more. Being unsure and wrong costs nothing, and
  effort is free.
- A right idea it thought unlikely earns extra: a daring discovery.
- When a surprise looks unlike anything it has met, it doubts its gut. It imagines more widely,
  including the idea it has tried least, and checks twice before believing.
- It may change its mind and replace an idea it already kept.

Every robot lived 10 lives while I built this (`school-legacy/nursery/results/`) and 10 fresh lives run once
afterwards (`legacy/school/school-fresh/`). The numbers below pool all 20
(`scratch/school-pooled.txt`).

### What happened

"Tries" means how many explanations it imagined before and including the right one. Fewer is
better, and 12 means it never imagined it. "±" is how much the average could move by chance.

| Robot | Familiar forces: found | Familiar forces: tries | New forces: found | New forces: tries | Ideas imagined per exam world | Sure but not right (of ideas kept) |
|---|---|---|---|---|---|---|
| Humble | 76% ± 2 | 4.3 ± 0.2 | 80% ± 4 | 4.2 ± 0.3 | 5.0 | 6% |
| Taught (watch, hints, credit) | 82% ± 2 | 3.9 ± 0.1 | 80% ± 5 | 4.5 ± 0.4 | 4.3 | 7% |
| Credit only | 78% ± 2 | 4.3 ± 0.2 | 76% ± 5 | 4.7 ± 0.3 | 4.5 | 8% |
| Taught itself | 75% ± 3 | 4.8 ± 0.2 | 75% ± 4 | 5.6 ± 0.4 | 4.8 | 16% |
| Never taught | 71% ± 3 | 7.1 ± 0.3 | 80% ± 4 | 6.1 ± 0.4 | 6.4 | 0% (it is never sure) |

"New forces" are thick oil and valley, which it was never shown. When it was sure of an idea it
kept, how often was the idea right? And when it was unsure?

| Robot | Sure → right | Unsure → right |
|---|---|---|
| Humble | 82% | 80% |
| Taught | 79% | 84% |
| Credit only | 78% | 80% |
| Taught itself | **61%** | 89% |
| Never taught | (sure only 16 times) | 75% |

### What held up in both sets of lives

1. **Teaching nearly halves the searching.** The never-taught robot needed about 7 tries to reach
   the right idea for a familiar force. The taught one needed about 4. The skill carried over to
   forces it was never shown: about 4.5 tries against 6. Its gut could not point straight at a new
   force, but it still made the search shorter.
2. **Showing and hints add a little on top of credit alone** for familiar forces (3.9 against 4.3
   tries, 82% against 78% found). That is at the edge of what chance can do.
3. **Without a teacher it fools itself.** The robot that taught itself gave itself credit for any
   idea that seemed to work, half-right ones included. It became sure and wrong: its "sure" ideas
   were right only 61% of the time, against 89% for its unsure ones. It was sure and not right twice
   as often as the taught robots (16% of kept ideas against 6–8%). Credit from the world, when the
   answer is revealed, is what kept the others honest.
4. **Swings were mostly taken for springs.** For small swings the two look almost the same, and
   the spring idea explains the pushes within the blur of its eyes. So most robots kept the spring
   idea, a close relative of the right answer, just as in the main lab. The robots with outside
   credit found the swing idea least often (5–30% of swing worlds, against 35–50% without it).
   Perhaps they had learned to favour the spring idea. But each robot met only 20 swings.
5. **It stopped getting better once the teacher left.** After the hints ended, the taught robot
   needed about 4.6–4.9 tries per practice world, with no downward trend. Its gut reached about half
   of what its senses allow. It put the right idea first 31–34% of the time, and the best possible
   gut 64% (first 10 lives).

### The humble robot: what humility did and did not do

- **It worked harder, and that was fine.** It imagined 5.0 ideas per exam world against 4.3.
  Effort cost it nothing, as you wanted.
- **Its "sure" stopped being a warning sign.** For the taught robot, "sure" was right a little
  less often than "unsure" (79% against 84%). For the humble robot the two were about equal (82%
  against 80%), and it was sure of fewer ideas. Its confidence score came out better too (0.22 ±
  0.01 against 0.25 ± 0.01, and on new forces 0.25 ± 0.02 against 0.32 ± 0.03, where lower is
  better). Part of that gain comes from the long-shot ideas it added, which were unsure and
  usually wrong, so they score well. This is a small step in the right direction, not yet wise
  confidence: a wise robot's "sure" would be right *more* often than its "unsure".
- **It was not better at finding new things.** On new forces it needed 4.2 ± 0.3 tries against
  4.5 ± 0.4, and found 80% against 80%. That is no difference. On familiar forces its doubting made
  it a little slower (4.3 against 3.9 tries).

**Why humility did not help with new things yet.** Two gaps showed up:

- **It could not tell new from old.** It doubted its gut in 54% of the worlds with new forces and
  44% of the familiar ones, which is almost no difference. To its senses, a new force looks like an
  old one. On the first 10 lives I checked the best gut its senses allow, one trained on all 1,600
  practice answers at once. That gut put the right idea first 64% of the time for familiar forces
  and **0%** for new ones. (The guts the robots learned managed 31–34% for familiar ones.) A child
  who cannot notice that something is new cannot know when to be humble.
- **It never changed its mind: 0 times in 1,040 worlds.** It was allowed to swap a kept idea for a
  better one. But once a half-right idea made the surprise go away, nothing made it look again.
  Every robot kept a half-right idea in about 1 world in 6 (a swing taken for a spring, thick oil
  taken for water drag or rubbing). Being able to doubt is not enough. Something has to make it doubt at the
  right moment.

### A claim I withdraw

On the first 10 lives, the taught robot found thick oil only 55% of the time, and the never-taught
robot 75%. It seemed to keep jumping to the familiar water-drag idea, and I wrote that up as "the
expert's blind spot". On the 10 fresh lives it went the other way (70% against 55%). Over all 20
lives there is no difference (62% against 65%), and the taught robot still needed fewer tries (5.5
against 7.3). So I withdraw it.

Two more early findings shrank:

- I wrote that the taught robot's confidence was backwards: sure ideas were right 74% of the time,
  unsure ones 87%. Over 20 lives it is 79% against 84%, which is within chance.
- The humble robot's lead on new forces in the first 10 lives (4.0 against 4.9 tries) disappeared
  on the fresh lives (4.3 against 4.0).

In small tests, chance can look like a finding. That is why the fresh lives matter. One thing from
that section still stands: the best possible gut never puts a new force's idea first. That is a
fact about its senses, not about teaching.

### What this says about your plan

| Your idea | What the school showed |
|---|---|
| Show it first, then hold its hand less and less, then let it go alone | Works. Its imagination got better with practice, and it kept the skill with no help and no learning in the exam. It stopped improving once the teacher left, at about half of what its senses allow |
| Reward it from outside when the answer is revealed | Needed. Without it, the robot became sure and wrong |
| It should find things it was never taught | Partly. It found forces it was never shown 80% of the time, with no hints, by using a shape it knew on a new input. The checking did that work, not the gut |
| Teach it humility: points off for being sure and wrong; being wrong and working hard are fine | A small step toward honest confidence and more effort. No gain at finding new things yet, because it cannot notice newness or half-rightness. That needs better senses for "this is new", and a habit of re-checking ideas it already kept |

### Limits of the school

- It chooses from a fixed menu of 11 ideas. Real discovery also makes up ideas that are not on
  the menu.
- I designed its gut picture (the leftover in 5 bands along position and speed). It did not learn
  how to see.
- The credit amounts and learning speed were chosen once and never tuned. Other values could
  change the picture.
- The school is small: 40 practice worlds, a 12-world exam, 20 lives per robot. Differences under
  about half a try, or about 5 points in "found", are within chance.
- The humble rules are my reading of your note. Other kinds of humility might do better. The two
  gaps above point to where to try next.

## The relentless robot: humble, and sure only when it has made sure

You asked for a robot that is humble but does not give up, one that tries its best until it is
sure and is confident because it was thorough. It keeps the humble robot's rules: being sure and
wrong costs the most, and being wrong or working hard is fine. It adds five habits:

1. **It tries every idea**, not just the two its gut likes best. Its gut still decides the order.
2. **It keeps a list of rivals**: every idea it can imagine that the evidence has not yet beaten,
   even one it dropped earlier.
3. **It weighs the evidence** for its idea against each rival, over everything it has seen. It never
   decides from one situation alone: that is your re-trial.
4. **It pushes where its idea could break.** It imagines each push it could make and picks the one
   where its idea and the strongest rival would disagree most.
5. **It says "sure" only when every rival is beaten.** Otherwise it says which rival it could not
   rule out. If a rival wins, it changes its mind, even about an idea it already kept.

For comparison, two robots have only some of these habits. "No tests" has everything except
pushes of its own. "Imagine all" tries every idea but keeps the best fit without weighing rivals.

### A hole, found by an independent check, and fixed

The first version passed 20 fresh lives (seeds 11–30), but a helper script re-ran it on 5 more
(seeds 31–35), and once it said "sure" and was wrong: it called rubbing "sin(speed)". I followed
that world step by step. Its first guess was right, but then two moments came with a hidden bump
that no idea could explain, and it counted them against the right idea and dropped it. The right
idea never came back as a rival, so "sure" only meant "I beat the rivals I happened to list".

Two changes, and no numbers tuned:
- A moment that nothing can explain counts against nothing.
- The rivals are every idea it can imagine that evidence has not beaten, including dropped ones,
  weighed over everything already seen.

Then I re-ran seeds 1–10, and ran brand-new seeds 41–60 once, with the older robots on the same
seeds. The numbers below are from those 20 fresh lives (`legacy/relentless/relentless-fresh/`,
`legacy/relentless/relentless-gentle-fresh/`). The first version's results are kept in `legacy/relentless/relentless-v1/`. On seeds
31–35 the failure is gone: when it said "sure", it was right 58 times out of 58.

### In the normal school

| Robot | Familiar forces found | New forces found | Swings found | When it said "sure", it was right |
|---|---|---|---|---|
| Relentless | 98% | 100% | 95% | 100% (235 of 235) |
| No tests | 98% | 100% | 95% | 100% (231 of 231) |
| Imagine all | 95% | 100% | 90% | 97% |
| Humble | 78% | 68% | 35% | 74% |
| Taught | 84% | 72% | 30% | 80% |
| Taught itself | 78% | 70% | 45% | 67% |
| Never taught | 71% | 82% | 50% | (rarely sure) |

For the older robots, "sure" means their gut felt strong, as in the school, and they never made
extra pushes. So the fair comparisons for "sure" are with "no tests" and "imagine all".

**What this shows:**
- The relentless robot finds almost everything, including the swing, which the older robots
  mostly mistook for a spring.
- **An honest surprise:** most of the gain comes from habit 1, trying every idea. "Imagine all" is
  nearly as good at finding. The older robots failed mainly because they stopped at the first idea
  that seemed good enough.
- Weighing rivals makes "sure" trustworthy: 0 sure-and-wrong, against 3% for "imagine all".

### In gentle worlds, where the ordinary pushes are too soft

The same worlds, but every robot's usual pushes are soft (0.3 instead of 0.6–1.0), so curved forces
look almost straight. Only the relentless robot may push harder, and only where its idea could break.

| Robot | Familiar forces found | Springs | Swings | Rubbing | When it said "sure", it was right | Sure but wrong | Changed its mind |
|---|---|---|---|---|---|---|---|
| Relentless | 97% | 90% | 95% | 100% | 100% (228 of 228) | never | 44 times |
| No tests | 86% | 50% | 65% | 80% | 100% (173 of 173), but it said "sure" in only 72% of worlds | never | 7 times |
| Imagine all | 86% | 50% | 65% | 75% | 91% | 9% of the ideas it kept | never |

**What this shows:**
- **Pushing where your idea could break finds the truth when the easy tests are not enough.**
  Springs went from 50% to 90%, swings from 65% to 95%.
- **Weighing rivals is what makes "sure" mean something.** The robot that never doubts is wrong
  about 1 in 11 of the ideas it is sure of. The relentless robot was never sure and wrong.
- **It knows when it does not know.** It said "not sure" in 12 of 240 worlds and was right in only
  1 of them, so its doubt pointed at exactly the worlds where it was wrong:
  - 8 times it kept nothing and said "I do not know what it is yet" (7 of those were thick oil);
  - 3 times it named the right answer as the rival it could not rule out.

### What it says

Every kept idea comes with a sentence, a formula, and how sure it is and why. From gentle worlds:

> Spring (seed 41): "It is pulled back toward the middle, harder the farther away it is, like a
> spring. I am sure: I tested it against 'growing with position', 'wave with position' and it won,
> and every other idea I can imagine fits worse." `a = 3.55·tanh(1.6u) − 4.64·x`

> Swing (seed 47): "It is pulled back toward the middle, harder the farther away it is, like a
> spring. I am not sure: 'wave with position' explains what I saw as well, and none of my pushes
> could tell them apart." `a = 1.27·tanh(1.6u) − 4.24·x`

The second one is wrong, but it says so, and it names the right answer. At small swings, sin(x)
and x really are almost the same. Being wrong is okay as long as it knows it could be.

### What did not improve, and the limits

- **Thick oil in gentle worlds** stayed at 82% for every robot. Even its strongest push could not
  always tell speed cubed from its rivals.
- **It works much harder:** about 15 ideas per world, against 5–6. The menu here has only 11 ideas.
  In a world with thousands of possible ideas it cannot try them all; its gut and chosen tests
  will have to do the work. The invention school is meant to test that, and it is not ready yet.
- Its thoroughness is a habit I built in; it did not learn it. What it learned from the teacher is
  which ideas to try first.
- Changes made after looking at results are listed in `README.md`. No numbers were tuned.

## The invention school: making up ideas that are not on the menu

Until now every robot chose from a menu of 11 ideas that I wrote, and the worlds were built from the
same pieces. Choosing well is not inventing. So here the robot gets **pieces**: the 10 old shapes,
a steady push, and two new ones, "how far from the middle" (|x|) and "how fast, either way" (|v|).
It can **invent** by joining one position piece with one speed piece, for example
"slowed by speed, more the farther it is from the middle" = |x|·v. That makes 49 ideas. When
surprised it may imagine only 4, chosen by its gut, plus the neighbours of its current idea (one
piece swapped). It keeps the relentless robot's habits.

Five hidden forces need an invention. Three are practised with the teacher (|x|·v, x·|v|,
tanh(x/0.05)·|v|). Two are never shown until the exam (|x|·sin(v) and |x|·v³), and their pairings
of pieces never appear in practice.

**Are these worlds a fair test?** I checked this before trusting any result, because the first
version failed: its forces ran away and even the true answer could not explain them. Now, on seeds
1–3 (`(review notes, not published)`):
- the true idea explains 100% of normal moments of every invention world;
- nothing runs away;
- over one world, the true invention beats every old idea and every sum of two old ideas by
  decisive evidence, in 100% of worlds;
- the best old rival fails to explain 41–87% of moments, so the robot does get surprised.

**Results on fresh seeds 11–20** (run once after freezing the design; seeds 1–10 gave the same
picture). In each exam: 8 old forces, 3 practised inventions, 2 never-shown old-style forces and 2
never-shown inventions, twice each.

| Robot | Old forces found | Practised inventions found | **Never-shown inventions found** | Kept nothing ("I don't know yet") on never-shown inventions | Sure but wrong, on inventions |
|---|---|---|---|---|---|
| Inventor (taught) | 91% | 47% | **38% ± 12** | 40% | **never** (0 of 13 sure) |
| Inventor, gut never taught | 84% | 60% | **33% ± 9** | 42% | **never** (0 of 13 sure) |
| Menu only (can add old ideas, cannot join pieces) | 97% | 0% | **0%** | 100% | all 7 of its "sure" were wrong |

**What this shows:**
1. **It invents.** It joined pieces into laws it was never shown about a third of the time, where
   the menu robot never can. It said each in a sentence and a formula, for example: "It is slowed
   very sharply when fast, depending on distance. I am sure: nothing else I can form fits what I
   saw." `a = 2.29·tanh(1.6u) − 2.84·v³·|x|`
2. **In a big space, "sure" needs a final check against everything it can form.** Before I added
   it, the inventor was sure and wrong on 22–42% of kept inventions (seeds 1–10). It confused
   |x|·v with x·|v|: they push the same way whenever the thing moves outward. The right idea was two
   piece-swaps away, so it never became a rival. With the final check it was **never sure and
   wrong** (seeds 1–20). When its idea was wrong, it named the right one as a rival it could not
   rule out: 19 times out of 19 on the fresh seeds. The check never changes what it keeps, so
   "found" still measures its own limited search.
3. **You cannot be sure of what you cannot imagine.** The menu robot's final check covers only the
   ideas it can form. It said "sure" 7 times on practised inventions, and was wrong all 7 times.
4. **Teaching the gut did not help invention.** The untaught inventor did as well on inventions
   (33% vs 38%, and 60% vs 47% on practised ones: no clear difference). Teaching still helped on
   old forces (91% vs 84%, 7 tries vs 11).
5. **Most never-shown inventions were not found** (62%). In 40% it kept nothing and said it did not
   know yet, which is honest but not yet good enough.

**Limits.**
- The final check tries all 49 ideas. That is possible here, but not in a truly huge space.
- Inventions are only products of two pieces: no sums inside, no numbers inside, no deeper nesting.
- The gut's picture of the leftover was designed by me and a helper script.
- I made three changes after looking at results, all on seeds 1–10, listed in `README.md`:
  1. stable forces;
  2. the fairness check judged by evidence;
  3. the final check before "sure".

## The ball-throw world: finding mass

**What it is.** A person throws balls, and the robot sees where each ball is 20 times a second, a
little blurred. Each ball has a hidden mass. The robot also gives each ball one known push along a
rail and sees how fast it goes: a heavy ball goes slower. The balls are thrown in five places:
- a vacuum room;
- air;
- a windy yard;
- water;
- the moon, only in the exam.

Each ball is kept out of one of the training places, so the robot has to guess how it will fly
there. All tables are in `legacy/ball/ball-results/BALL.md` (dev seeds) and in the fresh-seed folders.

**Version 1** (built on dev seeds 1–10, then run once on fresh seeds 11–20). On the fresh seeds:
- It found every place's law.
- It found that one hidden number per ball, its mass, explains every place.
- It found Galileo's result: heavy and light balls fall the same in the vacuum.
- It guessed balls in places where it had never seen them to about 2 cm. The robot without the
  idea of mass missed by about 84 cm, and the ordinary network by about 58 cm.

There was one real failure: **in the windy yard it was sure and wrong in 2 of 10 fresh lives.**
- The wind was faint: −0.65 and +0.47 m/s.
- The idea "the air moves" was ahead by 7 and 8 (9 settles it).
- But its rule let a bigger idea go unless it won by 9. So it said "sure: still air" without
  throwing a single ball to check.
- All the dev-seed winds were 1.09 m/s or stronger, so the dev seeds could never have shown this.

**Version 2: humility, the way you chose ("test at the edge").**
- **Hints.** If a bigger idea predicts new throws better by at least 1, that is a hint. A bigger
  idea is its idea plus something extra, like moving air. The robot then throws balls where the
  strongest version of that idea the data still allow would show most.
- **Bounds.** "Still air" is now said with a bound, for example "the air seems still (any flow lies
  between −0.4 and +0.4 m/s)". A claim counts as right only if its bound holds the real wind.
- **Not sure.** If a hint or a rival still stands after its 6 throws, it says "not sure".

With seed 1's balls and the wind set by hand from 0 to 1 m/s:
- **0.5 m/s or more:** it found every wind.
- **0.25 m/s:** it found the wind but said "not sure". Seen through its eyes, a steady sideways push
  on each ball looks the same as a faint wind, and no throw it knows can tell them apart.
- **0.1 m/s:** it said "still air, any wind between −0.4 and +0.6", which holds the truth.
- **0.25 m/s, with no throws of its own allowed:** "not sure".
- It was never sure and wrong.

On dev seeds 1–10, version 2 guesses exactly as version 1 did, to the last digit. No dev life had a
faint wind, so no hint ever came up. Its sure claims were wrong 0 times out of 100.

**Changes made after looking at results.** All of them are listed in the README.
1. Version 1's build: weaker drag, sizes 0.3–1.2, and size measured to 0.2%. At 2%, the true size
   acted like a second hidden number.
2. Version 2: the hint rule, testing at the edge, and wind bounds. This was your decision.
3. Two fixes found by the independent review:
   - it now tries both ends of the wind range;
   - the "cannot be seen" test also applies after its throws run out.
4. One check loosened, with your approval. The rail cannot put two balls in order when their masses
   are closer than its blur. Seeds 2 and 4 had pairs only 0.002 and 0.008 apart.

Then the design was frozen, and fresh seeds 21–30 were run once (`legacy/ball/ball-fresh2/`).

**Fresh seeds 21–30: version 2 held.**
- **Laws.** It kept the true law in all 50 places, including three faint winds (0.45, 0.72 and
  0.84 m/s). It found all three winds.
- **Humility.** It said "not sure" in exactly those three windy lives, because a steady sideways push
  on each ball fits as well there. Its other 94 sure claims were all right.
- **Mass.** It kept the concept of mass in 10 of 10 lives, with the right power of size every time.
  A second hidden number never won.
- **Galileo.** Found in 10 of 10 lives.
- **Naming.** It named no ball wrong: 22 right and 18 "not sure".

**The same fresh seeds, run with frozen version 1 as a control** (`legacy/ball/ball-fresh2-v1/`, run after
version 2, with nothing tuned). Version 1 was sure and wrong in the windy yard once: seed 27, wind
+0.84 m/s. It said "sure: still air" without throwing a ball. On the same seed, version 2 threw 3
balls of its own, found the wind, and said "not sure" about a look-alike idea.

Over 20 fresh lives, version 1 was sure and wrong 3 times. Version 2 was never sure and wrong in its
10 fresh lives.

**How much better than the comparison robots.** These numbers were generated from the saved runs,
not typed in. Misses are in cm, and the figure in brackets is how many times bigger the miss is than
the concept robot's.

**Dev seeds 1–10:**
- balls in a place never seen there: concept 1.5; per_place 87.2 (58x); baseline 70.0 (47x)
- new throws of balls already seen there: concept 1.2; per_place 1.2 (1x); baseline 5.9 (5x)
- throw to a target, ball never thrown in air: concept 0.7; per_place 11.8 (17x); baseline 7.3 (10x)
- moon, ball never thrown there, after 1 moon throw: concept 1.5; per_place 1.5 (1x); baseline 511.0 (338x)

**Fresh seeds 21–30:**
- balls in a place never seen there: concept 1.6; per_place 72.7 (47x); baseline 56.1 (36x)
- new throws of balls already seen there: concept 1.4; per_place 1.4 (1x); baseline 4.8 (4x)
- throw to a target, ball never thrown in air: concept 0.5; per_place 7.7 (16x); baseline 7.4 (16x)
- moon, ball never thrown there, after 1 moon throw: concept 1.3; per_place 1.3 (1x); baseline 412.0 (305x)

The per-place robot finds the same laws, so it matches the concept robot wherever mass is not
needed. Where a ball meets a place for the first time, it misses by 16 to 58 times more. The gain
comes from the idea of mass, not from better throws.

**What this does not show.**
- **Faint winds.** "Not sure" at faint winds is honest but not clever. A throw that changes speed a
  lot, such as a high lob, could tell a wind from a steady push; its menu has no such throw.
- **Bounds.** Only the wind gets a stated bound. In still air the bound comes from the teacher's
  throws alone and stays wide, about ±0.6 to ±0.8 m/s, because it throws only when a hint appears.
- **Small sample.** Ten fresh lives per version is a small sample.

## Research reviews

At the author's request, additional research reviews were collected through a helper script's command
line. The reviews were read-only: they could search the web but not change anything, and the notes were saved
outside this publication, with their briefs (review notes, not published).

- `C-roadmap.md`: a 12-month roadmap toward general intelligence, how SERA compares with world
  models, active inference, DreamCoder and POET, and what would prove it wrong.
- `D-discoveries.md`: a ladder of 16 famous discoveries to replay, from the lever to radioactive
  decay. It notes which ones need a hidden concept (mass, density, charge, absolute zero).
- `E-video.md`: a practical plan from measurements to phone video. It covers wall markers, 120 fps,
  and smoothing before working out speeds, because raw differences blow up the noise.

I checked them only lightly. Parts are good, especially the video plan and the discovery ladder.
But `D-discoveries.md` invents reasons for the humble robot's failure that our data does not show,
and a few of its citations point to generic web pages. Treat them as a second opinion, not as
results.

Once the lab could be read, four more reviews were produced. I checked each one against the code.

| Report | What it said | What I found when I checked |
|---|---|---|
| `A-gaps.md`: gaps in your papers | Top gap: sera-field wipes its memory every example, so nothing builds up. Wetterich growth and Cahn-Hilliard memory are speculative for this job. The loop itself is sound | Agrees with the diagnosis. Its fixes are sensible but untested. One number (memory rates "0.027%") is copied from the diagnosis, not measured by it |
| `B-review.md`: an independent review of this lab | (1) For glued toys, the ordinary network was never shown the parts, so the comparison was unfair. (2) The idea menu is exactly the pieces the world is built from, so "discovery" is choosing. (3) The words test favours my learner | (1) True. Fixed, and the gap held (see "Toys stuck together" above). (2) True: a real limit, now written down; the invention school and the ball test are meant to address it. (3) Partly fair: tested, and the gap held (see "What this does not show") |
| `G-replicate.md`: re-ran the relentless robot on unused seeds 31–35 | Most claims held. Once it was sure and wrong. It blamed a bookkeeping hole | The failure was real, but the cause was different: hidden bumps made it drop the right idea, which never came back as a rival. Fixed; see version 2 above. Its "unfair comparison" point is fair for the older robots, whose "sure" is only a strong hunch; the fair comparisons are with `no_tests` and `imagine_all` |
| `F-literature.md`: literature for the next steps | Borrow expected-information-gain experiments (Box & Hill 1967, MacKay 1992), abstaining when unsure, Bayesian surprise, library learning (DreamCoder), inverting a physics engine to infer mass (Galileo), and scaffolding. Beware that showing the answer reduces exploring (Bonawitz et al. 2011) | The works are real and fairly summarized, but its links are search pages, not checked sources. Two claims go too far: that infants' "core knowledge" was *proved* innate, and a vague claim that language and physics were *proved* to share one structure. Its top experiment, choosing a test where rivals disagree, is what the relentless robot already does. The pedagogy trial (showing versus hints) is a good next test of "show it first" |

**A safety note.** While working, a helper script wrote one file, `docs/list.bat`, into sera-field, to list
files. Running it was blocked. The rule meant to stop writes there was written in a path style
the helper script ignored. I tested which style it obeys and fixed the rule. With the author's approval I deleted
the file; nothing else in sera-field changed.

Two build sessions also produced the invention school (`ccops5/inventor.py`) and the ball-throw world
(`ccops5/ballworld.py`), each in its own git worktree. Each round stopped before its runs finished,
because the build sessions end while their commands still run.
- **Inventor**, after three rounds: I reviewed it, found that its test forces ran away (the true
  answer explained only 2–34% of moments), that a fairness table was typed in by hand, and that
  "sure" had the relentless robot's hole in a bigger space. I fixed these, and ran every experiment
  myself. Its results are above.
- **Ball world**: round 3 printed "all checks pass", but its "masses" were all about 0.15 and its
  exponents were wrong. It had also shown something real: from throws alone, mass cannot be told
  apart from density. Round 4 adds a direct push, which measures mass, and fixes the other defects.
  Nothing from it is a result yet.
