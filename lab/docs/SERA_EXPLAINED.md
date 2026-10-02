# SERA explained: the one SERA, how it lives a world, and how it differs from a neural network

*Rewritten 2026-10-01 for branch `sera-v4` (plan revisions 6 to 8). The earlier explainer, which described the v3
minds now in `legacy/sera_v3/`, is in git (tag `reports-journal-2026-10-01`). Current results: `docs/SERA_STATUS.md`.
The theory: `docs/SERA_FIELD_THEORY.md`.*

---

## 1. SERA in one page

SERA is one learning mind. It lives in **worlds**: a rail where things are pushed and move (physics), lists to turn
into other lists (code), numbers to map to numbers (math), stories and questions (language), conversations, and ARC
puzzles. A world says what can be seen, what can be done, and how an answer is checked. SERA lives every world the
same way:

1. **It thinks in its one language.** An idea is an expression built from a few innate mechanisms and from its own
   concepts. Nothing else is given: no laws, programs, words or formulas.
2. **It weighs every idea with its Field.** How well the idea fits what it understands, how short and well-proven it
   is, and what this world's evidence says.
3. **It acts.** It pushes a thing, asks about an input, takes a small step, grows its search, imagines, looks
   closer, or wishes for an ability it lacks. These ways of working are themselves part of the Field: taught at
   first, then its own.
4. **It proves.** When an idea is good enough, it sends it to the world's judge. The judge is outside SERA. SERA can
   convince it but cannot change or bypass it.
5. **It keeps what was proven.** A new proven idea becomes one of its concepts, a part it can use in any subject.
   Words heard while working are learned against what it now understands, and it says what it found in its own
   words.

A **teacher** shows it examples and words at first, and its help fades. An **observer** grades every answer against
the hidden truth for us; SERA never sees that grade.

## 1.1 SERA and its Field: what is the difference?

**The short answer.** The **Field** is what SERA *is made of*: everything it has learned and how it tends to act. It
is one object (`sera/phi.py`, class `Field`), saved after every world as `field.pkl`, and a new life can start
from it. **SERA** is that Field *living*: the Field plus the code that makes it act in a world (`sera/one.py`, class
`Sera`). Load the same Field into `Sera` and you get the same mind; give `Sera` a new Field and you get a newborn.

**An analogy.** The Field is like everything in a person's head that came from living: memories, skills, words,
habits, beliefs. `one.py` is like the body and the brain's wiring: how attention moves, how an idea is tried, how an
answer is handed in. The **judge** (`ccops5/core`) is the examiner. It is not part of SERA, and SERA cannot change it.
The **worlds, the teacher and the observer** (`sera/tasks.py`) are the school, not the pupil.

**Why the two are not yet the same.** Your direction (2026-09-29) is "SERA is its Field": memory, belief,
understanding, imagination and the moves themselves are one superposed state, with no separate stores and no recall
step. Fixed code should end up holding only the innate mechanisms. Everything else is either taught and then held in
the Field, or learned. Today SERA is partway there:

| What | Where it lives today | Learned, taught or fixed? |
|---|---|---|
| Its concepts (every law, program and word-meaning it invented) | `Field.concepts`, a hash-chained list | learned (proven by the judge) |
| What it understood of past worlds | `Field.understood`, a list of the last explanations | learned; still a separate list (to be folded in, review 12 F9) |
| How often each idea was proven or refuted (standing) | `Field.standing`, a table | learned; still separate |
| Its words | `Field.lexicon` | learned |
| Its ways of working (push, ask, step, wish, imagine, …) | `Field.loop`, `Field.methods`, `Field.steps`: weights over the moves | the weights are learned; the moves themselves are code |
| Memory of things and situations | `Field.ideas`: each thing has a fixed random 2048-number identity and a state that is a sum of what was bound to it | learned; this is the superposition |
| Ideas set aside, and the 'recall' move | `Field.possibilities`, a list | a separate store: gone when `ONE_FIELD` is on |
| Which kinds of question an idea answers reliably in a talk | a per-talk tally in `one.py`; with `ONE_FIELD` on, a row in `Field.ideas` | moving into the Field |
| 44 fixed numbers (time shares, sizes, fades) | the top of `one.py` | fixed; each can be set for an A/B, none learned yet |
| 9 crutches (rules we coded after watching it fail) | `one.py` and `tasks.py`, each with a switch (`sera/crutches.py`) | fixed or taught; each is to be taught or removed |
| The language (0, 1, add, …, lists, the free curve) and the search | `sera/lang.py`, `one.py` | innate |
| The judge | `ccops5/core` | outside SERA |

**What "superposed" means here, concretely.** In `Field.ideas` every thing has a random identity vector of 2,048
numbers: a word, a cue of a situation (for example "position and force strongly anti-correlated"), an idea, a kind of
question. A thing's *state* is the sum of the identities bound to it. Nothing is looked up. A new situation is the
sum of its cues' states, and the ideas whose identities are most similar to that sum "ring". So one vector holds many
memories at once, and similar situations bring up what fit them before. This is memory as an automatic trigger, as
you asked.

**One Field, parts 2 and 4 (built 2026-10-01, behind the switch `ONE_FIELD`).**
- *Part 2:* what a world proved is laid into the states of that world's cues, with weight from the proof. What it
  only believed is laid in more weakly, and what was refuted pushes the other way. A later world rings with it.
- *Part 4:* the separate `possibilities` list and the 'recall' move are not used. The ideas that ring loudest become
  first thoughts (at most 3), but only after a structural check that they could apply here.
- The talk's "is this idea reliable for this kind of question?" record is held in the Field instead of a tally.

**Where that stands.** In the A/B (run `b1`, see `SERA_STATUS` §2) the switch is still off: on two rails, the ringing
brought up wrong laws first and SERA was twice as slow there. In talk, its reliability record did not learn to say
"I do not know" where the old tally did. The next steps are in `SERA_STATUS` §4.

**And `sera/field.py`?** Despite its name, it is not the Field. It holds older statistics that `phi.py` uses to weigh
laws: the `Stats` of a fit, the `Vocab` of law terms, and a prototype `Memory`.

## 2. The language: only mechanisms (`sera/lang.py`)

Innate:
- numbers: zero, one, add, sub, mul (the same for whole numbers and measured quantities);
- comparing and choosing: lt, eq, if;
- lists: nil, cons, head, tail, range, and map, filter, fold, at any depth (a list of lists is as much a value as a
  list of numbers);
- the world's inputs: a thing's position, speed and time; a list; a number;
- the free curve: a curve of one input whose values SERA shapes from its own measurements. It is how a new shape is
  first seen.

Everything else is **content**, taught or discovered: spring, drag, sum, reverse, "where is", "who is in". Once
proven, each is one of SERA's **concepts**, a named function of its language. It is usable in every subject, and
it makes the next search shorter (an idea built from its concepts is short to describe).

**How it searches.** Bigger and bigger expressions, smallest first, guided by its Field. Each expression is a typed
program, told apart from others by trying them on probe inputs. Its own moves change the search:
- **step:** a small proven step toward the answer, which becomes a new input for the rest (shown by the teacher
  first);
- **see around:** a λ that looks at the whole input;
- **the way back:** imagine the last step from the goal, then look for the part that leads to it;
- **wish, build, use:** when no idea fits, build the ability it needs as a concept, then use it.

## 3. The Field: one state that is SERA (`sera/phi.py`, `sera/field.py`)

The Field holds, in one object saved after every world:
- **concepts:** its inventions in every subject, append-only and hash-chained, with where each came from and its
  words;
- **understanding:** the explanations of past worlds (the kind of world, the idea, its parts, proven or believed);
- **standing:** proofs and refutations of each idea;
- **lexicon:** what its words mean to it, learned and never given;
- **the loop:** how it acts, a superposition of ways of working (`LoopField`), weighed like everything else;
- **memory as Field state:** holographic traces of what it met. An echo credits what led to a result, and the
  traces are consolidated after each world, so a familiar situation rings with what fit it before.

**Three layers over every idea h.**
- **U, understanding:** how well h fits what it understood in situations like this. Its parts and pairs of parts
  that explained such worlds before count most; its own concepts count as parts.
- **L, laws:** h's own standing: short to describe in its own language, proven more than refuted.
- **B, beliefs:** what this world's evidence and the words it heard say.

They are pooled as log Φ = 0.5 log U + 0.25 log L + 0.25 log B (the author's order: understanding heaviest). They
move each other: a proof becomes understanding and standing, and evidence against understanding lowers it.
**Curiosity** is where they disagree, the tension KL(B || U).

**Not yet one Field** (plan revision 8, Phase 3.4). By default, proven ideas also sit in a separate `possibilities`
store with a 'recall' move, and the beliefs live per world. The author's direction is that the whole Field is the
memory, with no recall step. That is built behind `ONE_FIELD` (§1.1) and stays off until it loses nothing in an
A/B.

## 4. Words (`sera/talk.py`)

SERA is born with no words. Any token it hears becomes a word. What a word can mean is something SERA can tell about
an idea it understands: one of its concepts, the input it depends on, which way it pushes. That set grows as it
invents. It learns which word means what across situations (IBM Model 1 by EM, as in child word learning). A word
heard while working is evidence about the idea, and a word it has not learned moves nothing. It names its new ideas
with words it coins.

**Talking with it** (`scripts/sera_talk.py`): what you say is read into its Field; a question is answered by the idea
that rings for it, or "I do not know". **Its ideas as Python:** `scripts/sera_code.py` prints its proven ideas
(`sera/pyprint.py`).

## 5. The judge: how "proven" is decided (`ccops5/core`)

The judge belongs to the world, not to SERA, and nothing in the Field enters a proof.

**Programs** (lists, numbers, language): an audit on fresh inputs. The program must give the right output on all of
them.

**Physics:** a certificate and an independent checker.
- **What SERA claims** (Decision 13, functional claims): "the force is this law, with its fitted strengths, up to eps
  at every reading where I looked". The judge accepts it when the law does not misfit (the adequacy test) and a band
  bounds anything else below eps.
- **What the band holds:** a 33-knot free curve on every input the law uses, priced by the claim language's own code.
  No rivals are named: a law within eps of it where SERA looked is as right as it.
- **The checker** recomputes every column independently (pivoted QR, exact null space, finite differences) and must
  agree.
- **SERA's senses on the judge's side:** its invented shapes (Decision 12), lenses that look closer (14) and its own
  dimensions, programs over position, speed and time (15). Each is priced so that the code still sums to at most 1.

**What a curve proof does and does not say** (review 10, 2026-10-01):
- An idea sent as a dimension is proven as "some curve of SERA's expression", not "a strength times exactly the
  expression". On stiff 2, the wrong 1 + x³ passes as well as x³.
- So SERA keeps what the judge certified, part by part (the honesty fix, 2026-10-01): a **curve** (a free curve on
  an input or on its dimension), a **drawing** (one of its registered shapes) or a **formula**.
- **The ramp (Decision 16, in force 2026-10-02):** `c * clip(e, -R, R)`, one strength times exactly SERA's
  expression. SERA tries it first and falls back to the curve. Only a part accepted as its own ramp is credited as a
  formula. x³ on stiff 2 now passes as a formula, while the wrong 1 + x³ still passes only as a curve. The judge
  regression gave the same verdict on all 306 old claims (`sera-runs/ab-b1/judge`).

## 6. A life

`scripts/sera_one.py` runs the program:
1. **Teach:** the teacher shows examples and words, and SERA proves each lesson.
2. **Alone:** new worlds, including laws in no list and compositions of what it was taught.
3. **The twin:** the same worlds with its taught inventions hidden, to see what it built itself.

It works until the judge accepts. A safety cap stops it there, and then it says so and asks. Every world's time,
moves and doubt are recorded, and every table we report is generated from the saved run.

## 7. How SERA differs from a neural network

| | A neural network (e.g. a language model) | SERA |
|---|---|---|
| What it knows | Millions to billions of numbers (weights), learned by gradient descent on large data | A list of named concepts, each a short program in its own language, each proven by an outside judge |
| How it learns | Many small weight updates over many examples | One proof at a time: an idea is searched for, checked, and kept whole as a concept |
| What is given | An architecture and a lot of data | Only mechanisms (count, compare, choose, lists, a free curve); every law, program and word is taught or found |
| Why you can trust an answer | You test it on held-out data; it can be confidently wrong | Each claim carries a certificate (physics) or an audit (programs) that someone else can re-check |
| Can it say what it knows? | Not directly; its knowledge is spread across weights | Yes: every concept prints as an expression or as Python, with where it came from and its words |
| Reuse | Implicit, through shared weights | Explicit: a concept is a part, used in any subject; it makes the next search shorter |
| Where it is weak | Little: it is broad and fluent | Breadth and speed. Search grows fast with idea size, so it needs teaching, small steps and its own concepts to go far; it cannot yet read a book and answer from it later |
| Memory | The weights, and a context window | The Field: one superposed state (2,048-number vectors per thing) that rings with what fit before; the last separate stores are being folded in (plan Phase 3.4, §1.1) |

In short: a network is fluent and approximate, and SERA is narrow and exact. SERA's bet is that a mind that keeps
only what it can prove, and builds every new idea from those proven parts, can grow without becoming confidently
wrong.

## 8. Where the code is

| What | File |
|---|---|
| The one mind | `sera/one.py` |
| Its language | `sera/lang.py`, with `sera/general.py` and `sera/synth.py` (program search) |
| The Field | `sera/phi.py`, `sera/field.py` |
| Words | `sera/talk.py` |
| Worlds | `sera/tasks.py`, `sera/worlds.py`, `sera/novel.py` (laws in no list) |
| Rails: experiments, evidence, the laws the judge can certify | `sera/design.py`, `sera/compact.py`, `sera/lawspace.py` |
| Python printer, dictionary | `sera/pyprint.py`, `sera/dictionary.py` |
| The judge | `ccops5/core/` (truth, checker, likelihood, paths, grammar) |
| Programs | `scripts/sera_one.py`, `sera_talk.py`, `sera_converse.py`, `sera_code.py`, `sera_write.py`, `sera_steps_ab.py`, `sera_understand.py` |
| Tests | `tests/` (run with `scripts/runtests.sh`); legacy tests in `legacy/sera_v3/tests/` |
| The legacy minds | `legacy/sera_v3/` |
