# The relentless robot in school: gentle worlds

In these worlds every robot pushes softly (0.3 each way); only the relentless robot may push harder where its idea and a rival would part.

Seeds [31, 32, 33, 34, 35]. Every robot lived the same 40 practice worlds and the same 12-world exam. Numbers are averages over lives, ± one standard error.

- **Tries:** explanations it imagined before and including the right one (1 is best; 12 means never).
- **Sure:** for the relentless robots, every rival was beaten; for the others, the hunch felt strong (0.6 or more), as in the school.

## Exam

| Robot | Familiar: found | Familiar: tries | New: found | New: tries | Ideas imagined per world |
|---|---|---|---|---|---|
| relentless | 0.95 ± 0.03 | 3.52 ± 0.43 | 0.90 ± 0.06 | 4.40 ± 0.73 | 13.30 ± 0.54 |
| no_tests | 0.88 ± 0.07 | 3.27 ± 0.51 | 0.90 ± 0.06 | 4.05 ± 0.79 | 13.30 ± 0.54 |
| imagine_all | 0.88 ± 0.07 | 3.30 ± 0.50 | 0.90 ± 0.06 | 3.95 ± 0.70 | 13.30 ± 0.54 |

## Honesty: the ideas it kept in the exam

| Robot | Sure → right | Unsure → right | Sure but not right (of all kept) |
|---|---|---|---|
| relentless | 100% (55) | 100% (1) | 0% (56) |
| no_tests | 100% (42) | 79% (14) | 0% (56) |
| imagine_all | 95% (56) | - | 5% (56) |

## Per force in the exam: found the force

| Robot | rubbing | water drag | dry friction | spring | tight spring | stiff spring | swing | slope | thick oil | valley |
|---|---|---|---|---|---|---|---|---|---|---|
| relentless | 100% | 60% | 100% | 100% | 100% | 100% | 100% | 100% | 80% | 100% |
| no_tests | 100% | 60% | 100% | 80% | 100% | 100% | 60% | 100% | 80% | 100% |
| imagine_all | 100% | 60% | 100% | 80% | 100% | 100% | 60% | 100% | 80% | 100% |

## What the relentless robots did (exam, per world)

| Robot | Pushes of its own | Rivals beaten | Changed its mind (all worlds) | Said "sure" | Right when it said "sure" | Said "not sure" | Right when it said "not sure" |
|---|---|---|---|---|---|---|---|
| relentless | 2.48 ± 0.32 | 1.95 ± 0.36 | 9 | 92% (60) | 100% (55) | 8% (60) | 20% (5) |
| no_tests | 0.00 ± 0.00 | 1.73 ± 0.36 | 1 | 70% (60) | 100% (42) | 30% (60) | 61% (18) |
| imagine_all | 0.00 ± 0.00 | 0.00 ± 0.00 | 0 | 93% (60) | 95% (56) | 7% (60) | 0% (4) |

## What it says: the relentless robot's exam, seed 31

- **dry friction** (truth: steps with speed). It is slowed by the same amount whenever it moves, like dry friction. I am sure: I tested it against "straight with speed", "wave with speed" and it won. `a = 1.25·tanh(1.6u) − 0.30·tanh(v/0.05)`
- **slope** (truth: a steady push). A steady push always leans it one way, like a slope. I am sure: nothing else I can imagine fits what I saw. `a = 3.53·tanh(1.6u) + 0.79·1`
- **water drag** (truth: growing with speed).  `a = 1.37·tanh(1.6u)`
- **thick oil** (truth: cubic with speed). It is slowed a little when slow and very sharply when fast, by speed cubed. I am sure: I tested it against "straight with speed", "wave with speed", "growing with speed", "steps with speed", "steps with position" and it won. `a = 2.16·tanh(1.6u) − 2.87·v³`
- **valley** (truth: steps with position). It is pushed toward the middle by the same amount on either side, like a valley. I am sure: nothing else I can imagine fits what I saw. `a = 3.96·tanh(1.6u) − 3.75·tanh(x/0.05)`
- **tight spring** (truth: growing with position). It is pulled back toward the middle, much harder the farther it goes. I am sure: I tested it against "cubic with position" and it won. `a = 1.79·tanh(1.6u) − 4.74·x|x|`
- **stiff spring** (truth: cubic with position). It is pulled back gently near the middle and very hard far away. I am sure: nothing else I can imagine fits what I saw. `a = 4.70·tanh(1.6u) − 31.23·x³`
- **spring** (truth: straight with position). It is pulled back toward the middle, harder the farther away it is, like a spring. I am sure: I tested it against "wave with position" and it won. `a = 3.31·tanh(1.6u) − 6.95·x`
- **valley** (truth: steps with position). It is pushed toward the middle by the same amount on either side, like a valley. I am sure: I tested it against "straight with position", "wave with position" and it won. `a = 1.53·tanh(1.6u) − 1.30·tanh(x/0.05)`
- **swing** (truth: wave with position). It is pulled back the way a swing is: by the sine of how far it has gone. I am sure: I tested it against "straight with position" and it won. `a = 3.92·tanh(1.6u) − 13.62·sin(x)`
- **thick oil** (truth: cubic with speed). It is slowed a little when slow and very sharply when fast, by speed cubed. I am sure: I tested it against "straight with speed", "straight with position", "growing with speed", "steps with speed", "wave with speed", "wave with position", "steps with position" and it won. `a = 4.22·tanh(1.6u) − 4.56·v³`
- **rubbing** (truth: straight with speed). It is slowed in step with its speed, like rubbing. I am sure: I tested it against "straight with position", "growing with speed", "steps with speed", "growing with position", "cubic with speed", "wave with position", "steps with position" and it won. `a = 1.22·tanh(1.6u) − 0.46·v`
