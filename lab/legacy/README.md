# Legacy tracks (nursery, school, relentless, inventor, ball)

*Moved here from the root README on 2026-09-24, when these tracks moved into legacy/. Paths below are updated to the new places; historical files in (review notes, not published) still use the old root-level paths.*

## ccops5 lab: the SERA loop, connected and tried out

**Built as an isolated experiment.** This is a separate, isolated experiment. Nothing here imports from,
or writes into, `D:\ai\labs\sera-field`. The only thing borrowed is sera-field's Python
interpreter (its `.venv`), run with bytecode writing switched off so that folder is untouched.

## What it is

A learner that grows up like a baby, in a small world whose physics are hidden from it.

It gets only what a baby gets:

- what things look like
- the commands it sends to its own hand
- a caretaker's words
- noisy readings of where things are and how fast they move

Nobody tells it forces, formulas, or what words mean.

It learns in this order, one stage at a time:

| Stage | What happens | What it has to find out |
|---|---|---|
| 0 own hand | It pushes its own hand | How its commands move things (a hidden muscle law), like learning to hold a spoon |
| 1 toys on ice | Six toys, no rubbing | Each toy's heaviness; how to recognise toys |
| 2 toys on carpet | Same toys, rubbing | A new law (rubbing) it has never seen |
| 3 toys in water | Same toys, water drag | Another new law; whether the rubbing law still helps |
| 4 springs | Things tied to springs | A position law |
| 5 swings | Pendulums | Whether the spring law already explains swinging (it should, for small swings) |
| 6 new toys, words only | Toys it has never touched, described in words | Whether the words it heard earlier now carry meaning |
| 7 stuck together | Old toys glued in pairs, then triples | **Math:** how the parts' numbers make the whole's numbers. **Proof:** work out a guess for a combination it has never seen from pieces it has verified, then check it against the world |
| 8 final check | Every old toy in every place | What it kept |

A few situations include a secret bump from someone else: a contradiction that should not become
knowledge.

## The loop, and where each part of the SERA papers lives

| Idea in the papers | In this lab |
|---|---|
| Whiteboard (the boundary, the current situation) | The numbers for this situation: one coefficient per law |
| Library kept for life (the persistent bulk) | Laws, remembered objects, word notes, place notes, and arithmetic rules. None is wiped between situations |
| Library feeds perception (the geodesic pull) | Before touching anything, it guesses from what it remembers: the object, the words said, the place, or parts worked out with a rule |
| Imagination (paths; the inconsistent ones cancel) | It imagines 12 versions of the situation for each of 6 possible pushes, then chooses the push where those versions disagree most |
| Verification with re-trial ("throw again") | At least two different pushes. Then a test push whose outcome it has not seen is compared with its guess |
| Two marks on every memory (bivalent marks) | Every object memory and every rule counts times right and times wrong. A memory is committed after 2 right and corrected after 2 wrong in a row |
| Capture only when verified | Nothing is stored unless the situation checked out |
| Anomaly monitor | Leftover error compared with sensor noise over the last 8 situations. Surprise in 5 of those 8 starts growth, using only those surprising situations |
| Growth of a new axis | A new law grown from the surprising situations. It imagines 7 explanations (one per set of inputs the law could use). Each is judged on situations it was not trained on (every situation held back once), by the typical error. It keeps the simplest one that is nearly the best |
| New knowledge must survive checks | A proposed law stays a candidate until 3 later surprising situations pass the check, with at most 1 failure. Passing means the surprise goes away and the unseen push is guessed better. Otherwise it is rejected |
| Local learning, bottom-up | Old laws are frozen. Each new law is trained alone, only on what the old laws leave unexplained. The stages go from body to world to words to math |
| Physics, language, math, proof interconnected | Words are fitted to physical numbers. The math rules are judged by physics. The worked-out guesses (proof) use memories of parts and a verified rule, then are checked by the world |

## Learners compared

Every learner lives the same childhood (same seed, same toys, same sensor noise):

| Learner | What changed |
|---|---|
| `full` | Everything connected |
| `forget_kinds` | Keeps its laws, but forgets objects, words and places after every situation (how CORE-022 treats its state) |
| `reset_all` | The whole library is wiped after every situation |
| `ungated` | Keeps everything without checking it first |
| `passive` | The same push every time: it never throws again differently |
| `frozen_laws` | Learns its hand, then may not grow new laws |
| `no_reuse` | A law may only be used in the kind of place it was found |
| `baseline` | An ordinary neural network. Knowledge lives only in its weights, trained with backpropagation on the same childhood, with the same inputs and more pushes |
| `baseline_parts` | The same network, also shown the parts of a glued thing (their looks added up, and how many) |
| `baseline_sets` | The same network, where a small network reads each part of a glued thing and the results are added (a "deep sets" network). The fairest version |
| `baseline_words` | The plain network, not shown the look of the brand-new toys in the words-only stage, so it can rely on the words |

## School: learning how to discover

A second experiment. The learner already knows its hand and lives 40 practice puzzle worlds. Each
world is a tiny new universe with one hidden force, and laws are not carried between worlds. When
surprised, it imagines explanations from a menu of 11 (a shape along position or speed, or a steady
push) and checks each one as in the main loop. A gut feeling (hunch) chooses which ideas to imagine
first and learns by a local rule: credit × (what it felt − what it expected). Then comes a 12-world
exam with no help and no learning, including two forces it was never shown.

| Learner | How it is taught |
|---|---|
| `humble` | Like `taught`, but being sure and wrong costs points (the surer, the more). Being unsure and wrong costs nothing and effort is free. A daring right idea earns extra. When a surprise looks unfamiliar it imagines more widely and checks twice. It may swap a kept idea for a better one |
| `taught` | Watches the teacher show the right idea (worlds 1–8), then gets fading hints (worlds 9–24), then is alone. Credit from the teacher after every world |
| `credit_only` | The same credit, with no showing and no hints |
| `self_taught` | No teacher: it credits its own kept ideas |
| `untaught` | Its hunch never changes |

### The relentless robot (`ccops5/relentless.py`)

Humble like `humble`, but it does not stop until it has made sure:
- It imagines every idea it has not ruled out, most-felt first.
- It keeps a list of rivals: every idea it can imagine that evidence has not yet beaten, even one it dropped earlier. A new rival starts with the evidence of everything already seen.
- It weighs the evidence for its idea against each rival over everything it has seen. The evidence is the difference in leftover error, in noise units, capped per situation so one situation never decides.
- It pushes where its idea and the strongest rival would part most. It imagines each possible push and adds what it would see.
- It changes its mind when a rival wins.
- A situation that no idea can explain (a hidden bump) counts against nothing.
- It says "sure" only when every rival is beaten. Otherwise it names the rival it could not rule out.

Two comparison robots:
- `no_tests`: the same, without pushes of its own.
- `imagine_all`: imagines every idea but keeps the best fit without weighing rivals.

**Gentle worlds** are the same worlds, but the ordinary pushes are soft (0.3 each way). Only the relentless robot may push harder.

## The ball-throw world: finding mass (`ccops5/ballworld.py`, `ccops5/ballmind.py`)

A person throws balls, and the robot sees where each ball is every 0.05 s, with 1 mm of noise.

**The balls.** Each life has 8 balls:
- a hidden mass, from 0.5 to 3;
- a size it can see, from 0.3 to 1.2, measured to 0.2%;
- a "look" that only loosely goes with size.

Each ball is also pushed once along a rail with a known push. The speed it gets gives the robot a **push number** (push ÷ speed): the mass, blurred slightly by noise.

**The places:**
- **Vacuum:** only a pull down.
- **Air:** the same pull, plus drag 0.05·size²·|v|·v / mass.
- **Windy yard:** the same drag, but the air moves sideways at a hidden speed (−4 to +4 m/s).
- **Water:** a lift of 9.8·size³ / mass, and drag 0.3·size²·|v|·v / mass.
- **Moon:** a weaker pull down. It is shown only in the exam.

**What the robot does:**
1. **Laws.** It finds each place's law by evidence among 27 ideas (sets of force terms, in still or moving air). Where two ideas would part most, it throws a ball itself.
2. **Mass.** It earns the idea "one hidden number per ball explains every place" by predicting balls in places where it never saw them. It weighs four answers:
   - R0: no sharing;
   - Rs: size only;
   - R1: the push number, that is, mass;
   - R2: a second hidden number.
3. **The rest.** It finds Galileo's result in the vacuum, adapts to the moon, throws to a target, names heavy and light, and says what it found in sentences and formulas.

Each ball is thrown by the teacher in 3 of the 4 training places. The 4th is kept back as the test of the concept.

**The comparison robots:**
- `per_place` uses the same law finding but shares nothing between places.
- `baseline` is a neural network given the same numbers, plus 6 extra random throws per place.

**Humility (version 2).**
- "Still air" is a claim with a bound. Every place with drag states the winds it cannot rule out.
- A bigger idea is its idea plus extra parts, such as moving air. If a bigger idea predicts new throws better by at least 1, that is a hint, and the robot throws where the strongest version of that idea the data still allow would show most.
- It says "not sure" in two cases:
  - a hint or a rival is still standing after its 6 throws;
  - no throw on its menu can tell two ideas apart.

## How to run

```bash
python legacy/nursery/run.py
```

This runs every learner on seeds 1, 2 and 3 in parallel (about 15 minutes with `--workers 15`), and writes:

- `legacy/nursery/results/life-seed{S}-{learner}.json`: every situation and every event
- `legacy/nursery/results/TABLES.md`: all the tables
- `legacy/nursery/results/summary.json`: the numbers behind the tables

For one learner or seed: `legacy/nursery/run.py --seeds 1 --modes full baseline`. The fair test on fresh seeds:
`legacy/nursery/run.py --seeds 4 5 6 --results legacy/nursery/results-fresh`.

The school (about 2 minutes): `python legacy/school/school_run.py` runs all five school learners on seeds 1–10 and
writes `legacy/school/school-results/SCHOOL.md`. The fair test on fresh seeds:
`python legacy/school/school_run.py --seeds 11 12 13 14 15 16 17 18 19 20 --results legacy/school/school-fresh` (and seeds 21–30 into
`legacy/school/school-fresh2`).

The relentless robots: `python legacy/relentless/relentless_run.py` (seeds 1–10, compared with `legacy/school/school-results`) and
`python legacy/relentless/relentless_run.py --seeds 41 ... 60 --results legacy/relentless/relentless-fresh --others` (the fair test of the
current version). Add `--gentle` (and a new `--results` folder) for the gentle worlds. Each writes
`RELENTLESS.md`. The first version's results are kept in `legacy/relentless/relentless-v1/`.

The invention school: `python legacy/inventor/inventor_run.py` (seeds 1–10 into `legacy/inventor/inventor-results/`) and
`python legacy/inventor/inventor_run.py --seeds 11 ... 20 --results legacy/inventor/inventor-fresh` (the fair test). Each writes
`legacy/inventor/INVENTOR.md`. `python legacy/inventor/inventor_run.py --quick` is a one-minute smoke test. The check that the worlds are a
fair test: (review notes, not published).

The ball world:
- **Dev seeds (about 2 minutes):** `python legacy/ball/ball_run.py` runs the three robots on seeds 1–10 into `legacy/ball/ball-results/` and writes `BALL.md`.
- **Checks:**
  - `python legacy/ball/ball_check.py --seed 1` checks the invariants live on seed 1: A kinematics, B law selection, C concept hierarchy, E humility.
  - `python legacy/ball/ball_check.py` audits the saved dev runs (A–H).
  - `python legacy/ball/ball_check.py --results legacy/ball/ball-fresh2 --read-only` audits saved fresh runs.
- **The fair test:** `python legacy/ball/ball_run.py --seeds 21 ... 30 --results legacy/ball/ball-fresh2`.
- **Visible runs:** `scripts/run_dev.ps1` and `scripts/run_fresh.ps1` do the same in their own PowerShell window, with logs.
- **Version 1's runs** are kept in `legacy/ball/ball-results-v1/` (dev seeds) and `legacy/ball/ball-fresh/` (fresh seeds 11–20).

## Files

| File | What it holds |
|---|---|
| `ccops5/world.py` | The nursery: hidden physics, toys, words, the order of the childhood |
| `ccops5/laws.py` | A law as a small learned function, and how a new one is grown |
| `ccops5/mind.py` | The connected learner (the loop above) and its switches |
| `ccops5/baseline.py` | The ordinary neural network to compare with |
| `ccops5/life.py` | One whole life |
| `ccops5/report.py` | Tables from saved lives |
| `legacy/nursery/run.py` | Runs everything |
| `ccops5/puzzles.py` | School: 52 small puzzle worlds, each with one hidden force, and the 11 ideas it can imagine |
| `ccops5/school.py` | School: the gut feeling (hunch), the teacher (watch, fading hints, credit), the humble learner and the exam |
| `python legacy/school/school_run.py` | Runs the school for every learner and writes `SCHOOL.md` in the results folder |
| `ccops5/relentless.py` | School: the relentless robot and its two comparison robots, and the gentle worlds |
| `python legacy/relentless/relentless_run.py` | Runs them and writes `RELENTLESS.md`, next to the earlier robots on the same seeds |
| `ccops5/inventor.py` | Invention school: pieces joined into new ideas, limited imagination, relentless checking, a final check before "sure" (built by a helper script, reviewed and fixed during development) |
| `python legacy/inventor/inventor_run.py` | Runs it and writes `legacy/inventor/INVENTOR.md` |
| `(review notes, not published)` | The fairness check for the invention worlds, its table, the dev-seed report and the smoke test |
| `ccops5/ballworld.py` | The ball-throw world: five places, balls with hidden mass, the rail push, and which (ball, place) pairs are kept back |
| `ccops5/ballmind.py` | The ball robot (laws by evidence with its own throws, wind ranges, the concept of mass, Galileo, naming, sentences) and the network baseline |
| `python legacy/ball/ball_run.py` | Runs the ball world and writes `BALL.md` |
| `python legacy/ball/ball_check.py` | The ball world's checks, live on one seed or over saved runs |
| `legacy/USER_REPORT.md` | A short, live status of the current work, for the SERA author |
| `(review notes, not published)` | Reports and builds by helper scripts (development), with the prompts used |
| `(review notes, not published)` | Working rules learned the hard way, and which seeds are used up |
| `legacy/RESULTS.md` | Everything explained simply, including how the research supports it |

## Changes made after looking at results

This is a development experiment, not a test fixed in advance. After the first runs, I changed
the design, and every change is listed here.

| What went wrong | Change |
|---|---|
| Memories of water made before the water law was found were averaged with newer ones, so guesses were poor | When a law is found in a place, older memories of that place stop being used once newer ones exist |
| The guess from words mixed numbers from different words and sometimes went badly wrong | Word meanings are a small linear fit: each word nudges the expected numbers |
| A new toy looked almost the same as an old one and was taken for it | Things are described by 8 appearance numbers instead of 4, so different things are far apart |
| Old one-off bumps, kept since the last law, decided which new law was grown. A "position" law was kept for rubbing | A new law grows only from the surprising situations behind the current alarm (the last 8 situations) |
| One odd situation in a small held-back set could decide the winning explanation | Every situation is held back once, and the typical (median) error decides. Training also lets one odd situation pull less |
| A half-right law was kept because it beat having no law | A law passes a check only when the surprise goes away with it |
| A spring law learned from one spring's range went flat outside it | Every law is a straight-line part plus a bendy part |
| A guess from words, made from very few examples, was far too sure of itself. The learner held on to it, blamed the new water law, and never kept one (seed 3) | Surprise is measured with free numbers: what no numbers for its current laws can explain, as the papers define growth. If its laws explain the pushes with different numbers than it expected, it drops the expectation (so wrong memories get corrected). Word guesses need 12 examples and admit their spread |

The first full run's files are kept in `scratch/old-results/` for comparison.

The school was built on seeds 1–10. The `humble` learner was added after those results, at the
SERA author's request. Then seeds 11–20 were run once, with nothing changed afterwards
(`legacy/school/school-fresh/`). Two findings from seeds 1–10 did not hold on the fresh seeds and are withdrawn
in `legacy/RESULTS.md`.

The relentless robot was built on seeds 1–10. After the first test life (seed 1), I made two changes:
- The end-of-world check now asks whether most of its last 3 situations were explained. Before, one odd last situation made it call a right idea unsure.
- I added the `imagine_all` comparison robot.

After the seeds 1–10 results, I added the gentle worlds, because its own pushes were rarely needed in the normal worlds. No numbers were tuned. Seeds 11–30 were then run once (now in `legacy/relentless/relentless-v1/`), with the older robots on the new seeds 21–30 (`legacy/school/school-fresh2/`).

**Version 2.** A helper script re-ran version 1 on unused seeds 31–35 (`legacy/relentless/validation-check/`). Once, it said "sure" and was wrong (seed 31, rubbing kept as sin(speed)). Tracing that world showed why. Two hidden bumps, which no idea could explain, counted against the right idea it held, so it dropped it. The right idea never came back as a rival, so "sure" only meant "beat the rivals I happened to list". Two changes:
- A situation that no idea can explain counts against nothing (as `doubt()` already did).
- The rivals are every idea it can imagine that evidence has not beaten, including dropped ones, weighed over everything already seen.

No numbers were tuned. Seeds 1–10 were re-run (`legacy/relentless/relentless-results/`, `legacy/relentless/relentless-gentle/`), then brand-new seeds 41–60 once (`legacy/relentless/relentless-fresh/`, `legacy/relentless/relentless-gentle-fresh/`), and seeds 31–35 again (`relentless-check31/`).

**The glued-toy baseline.** An independent review pointed out that the ordinary network was never shown the parts of a glued toy, though the learner was. I added `baseline_parts` and `baseline_sets` and ran them on seeds 1–6. The same review said the words test favoured my learner, so I added `baseline_words`. Nothing else changed.

The invention school was built by a helper script over three rounds, in its own git worktree
(branch `development/inventor`). I reviewed it and made these changes, all on seeds 1–10:
- The first product forces changed sign with position and ran away into the acceleration limit, so
  even the true idea explained only 2–34% of moments. They were replaced by stable forces built
  with the new "size" pieces |x| and |v|.
- The fairness check "median surprise of the best old idea ≥ 3" failed on these worlds, because old
  ideas pass about half the moments. After seeing that, I replaced it with the robot's own rule:
  over one world, the true invention must beat every old idea and pair by decisive evidence. It
  passes in 100% of worlds.
- A fairness table typed in by hand was replaced by the computed one.
- "Sure" was wrong on 22–42% of kept inventions: the right idea was two piece-swaps away and never
  became a rival. Before "sure", the robot now weighs its idea against every idea it can form. This
  check never changes what it keeps.

Then seeds 11–20 were run once (`legacy/inventor/inventor-fresh/`).

**The ball world.** helper scripts built it over four rounds, on branch `development/ball`, which is not merged. Each round's checks passed while its results were wrong. I then built it myself on dev seeds 1–10. The code's notes give three changes made after seeing dev data:
- Drag is weaker than in the earlier drafts, so a throw changes slowly enough to be measured every 0.05 s.
- Sizes span 0.3–1.2 instead of 0.5–1.5, so that size² and size³ can be told apart.
- Size is measured to 0.2% instead of 2%. At 2%, the true size acted as a second hidden number, and a two-number concept (R2) could win for the wrong reason.

Then seeds 11–20 were run once (`legacy/ball/ball-fresh/`). Everything held except the windy yard. There the robot was sure and wrong in 2 of 10 lives:
- Seeds 14 and 17 had faint winds, −0.65 and +0.47 m/s. Every dev wind was 1.09 m/s or stronger.
- Version 1 closed a bigger idea (still air plus a wind) unless it won by 9. So it said "sure: still air" while the wind idea predicted better by 7 and 8, and it never threw a ball of its own.

**Version 2** (approved by the SERA author):
- **Tests first.** The new `python legacy/ball/ball_check.py` was committed before any code change, and it failed on version 1. It checks:
  - energy books in all five places;
  - law selection;
  - the concept hierarchy;
  - humility over hand-set winds on seed 1.
- **Hints.** A bigger idea that predicts new throws better by at least 1 stays open. That is the least evidence the throw chooser already needed, so no new number was tuned. The robot throws where the strongest version of the bigger idea the data still allow would show most. If even that version could not be seen on any throw, it adds nothing.
- **Wind ranges.** Every place with drag states the winds it cannot rule out. A claim is true only if its range holds the true wind.
- **Two fixes from an independent review** (`(review notes, not published)`):
  - both ends of the wind range are tried;
  - the "cannot be seen" test also applies once its throws are used up.
- **One check changed after the dev audit, with the SERA author's approval.** "The push number ranks the masses perfectly" failed on seeds 2 and 4, where two masses 0.002 and 0.008 apart swapped places. The rail cannot tell those apart. Now a swap only counts when the masses differ by more than 3 times the rail's noise blur.

Seeds 1–10 were then re-run (`legacy/ball/ball-results/`). Version 1's dev runs are in `legacy/ball/ball-results-v1/`.
Then brand-new seeds 21–30 were run once (`legacy/ball/ball-fresh2/`). After that, frozen version 1 was run on
the same seeds as a control (`legacy/ball/ball-fresh2-v1/`, concept robot only), with nothing changed.

## Honest limits

- **Simple parts, not the substrate.** This tests the papers' wiring, not their substrate. Laws are small neural networks and each situation's numbers come from a Bayesian fit. None of the Clifford algebra, sheaf or Cahn-Hilliard substrate is used.
- **Push choice is built in.** It comes from imagination (the push where imagined versions disagree most), not from learned reward.
- **Math is a fixed menu.** It is born with seven ways that parts' numbers might combine and finds out which one the world obeys. It does not invent new operations.
- **Proof means derive then check.** It works out a guess for something it has never seen from verified pieces, then the world tests it. It is not formal symbolic proof.
- **Language is small.** Words are single labels from a caretaker, with no grammar.
- **The world is small.** Motion is along one line and there are only a few kinds of things.
- **Look-alikes can fool it.** Two objects that look almost the same can still be confused, because it cannot split one memory into two objects.
- **Three seeds** (plus three fresh ones) is a small sample.
- **The ball robot's menu is fixed too.** It has 27 ideas made from 4 force terms, and a wind searched in 0.2 m/s steps.
  - Only the wind gets a stated bound; extra per-ball pushes are ruled out by the hint rule alone.
  - It throws only to settle an open question. So in still air its bound comes from the teacher's throws and stays wide, about ±0.6 to ±0.8 m/s.
  - Its noise units treat the accelerations it works out as independent, but neighbouring ones share noise. Its evidence is therefore cautious: on seed 1, fitted numbers sat within 0.6 standard errors of the truth.
- **The school's menu is fixed.** It picks among 11 ideas and never makes up a new one. I designed
  its gut picture (the leftover in 5 bands along position and speed), and the credit amounts and
  learning speed were never tuned. With 20 lives per learner, differences under about half a try,
  or 5 points in "found", are within chance.
