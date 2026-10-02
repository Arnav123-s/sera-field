# The relentless robot in school

Seeds [31, 32, 33, 34, 35]. Every robot lived the same 40 practice worlds and the same 12-world exam. Numbers are averages over lives, ± one standard error.

- **Tries:** explanations it imagined before and including the right one (1 is best; 12 means never).
- **Sure:** for the relentless robots, every rival was beaten; for the others, the hunch felt strong (0.6 or more), as in the school.

## Exam

| Robot | Familiar: found | Familiar: tries | New: found | New: tries | Ideas imagined per world |
|---|---|---|---|---|---|
| relentless | 0.97 ± 0.02 | 3.60 ± 0.28 | 1.00 ± 0.00 | 3.50 ± 0.49 | 13.68 ± 0.72 |
| no_tests | 0.97 ± 0.02 | 3.70 ± 0.26 | 1.00 ± 0.00 | 3.85 ± 0.57 | 13.68 ± 0.72 |
| imagine_all | 0.95 ± 0.05 | 3.08 ± 0.19 | 1.00 ± 0.00 | 3.55 ± 0.51 | 13.68 ± 0.72 |

## Honesty: the ideas it kept in the exam

| Robot | Sure → right | Unsure → right | Sure but not right (of all kept) |
|---|---|---|---|
| relentless | 98% (58) | 100% (2) | 2% (60) |
| no_tests | 98% (58) | 100% (2) | 2% (60) |
| imagine_all | 97% (59) | 100% (1) | 3% (60) |

## Per force in the exam: found the force

| Robot | rubbing | water drag | dry friction | spring | tight spring | stiff spring | swing | slope | thick oil | valley |
|---|---|---|---|---|---|---|---|---|---|---|
| relentless | 80% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% |
| no_tests | 80% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% | 100% |
| imagine_all | 80% | 100% | 100% | 80% | 100% | 100% | 100% | 100% | 100% | 100% |

## What the relentless robots did (exam, per world)

| Robot | Pushes of its own | Rivals beaten | Changed its mind (all worlds) | Said "sure" | Right when it said "sure" | Said "not sure" | Right when it said "not sure" |
|---|---|---|---|---|---|---|---|
| relentless | 1.67 ± 0.29 | 1.35 ± 0.29 | 6 | 97% (60) | 98% (58) | 3% (60) | 100% (2) |
| no_tests | 0.00 ± 0.00 | 1.35 ± 0.29 | 5 | 97% (60) | 98% (58) | 3% (60) | 100% (2) |
| imagine_all | 0.00 ± 0.00 | 0.00 ± 0.00 | 0 | 98% (60) | 97% (59) | 2% (60) | 100% (1) |

## What it says: the relentless robot's exam, seed 31

- **dry friction** (truth: steps with speed). It is slowed by the same amount whenever it moves, like dry friction. I am sure: nothing else I can imagine fits what I saw. `a = 1.25·tanh(1.6u) − 0.30·tanh(v/0.05)`
- **slope** (truth: a steady push). A steady push always leans it one way, like a slope. I am sure: nothing else I can imagine fits what I saw. `a = 3.53·tanh(1.6u) + 0.79·1`
- **water drag** (truth: growing with speed). It is slowed more and more as it goes faster, by speed times speed, like water. I am sure: I tested it against "straight with speed", "straight with position", "wave with speed", "cubic with speed", "steps with speed", "wave with position", "growing with position", "steps with position", "cubic with position" and it won. `a = 1.40·tanh(1.6u) − 0.56·v|v|`
- **thick oil** (truth: cubic with speed). It is slowed a little when slow and very sharply when fast, by speed cubed. I am sure: I tested it against "straight with speed", "wave with speed", "growing with speed", "steps with position" and it won. `a = 2.16·tanh(1.6u) − 2.89·v³`
- **valley** (truth: steps with position). It is pushed toward the middle by the same amount on either side, like a valley. I am sure: nothing else I can imagine fits what I saw. `a = 3.97·tanh(1.6u) − 3.73·tanh(x/0.05)`
- **tight spring** (truth: growing with position). It is pulled back toward the middle, much harder the farther it goes. I am sure: nothing else I can imagine fits what I saw. `a = 1.79·tanh(1.6u) − 4.74·x|x|`
- **stiff spring** (truth: cubic with position). It is pulled back gently near the middle and very hard far away. I am sure: nothing else I can imagine fits what I saw. `a = 4.70·tanh(1.6u) − 31.41·x³`
- **spring** (truth: straight with position). It is pulled back toward the middle, harder the farther away it is, like a spring. I am sure: I tested it against "wave with position" and it won. `a = 3.31·tanh(1.6u) − 6.95·x`
- **valley** (truth: steps with position). It is pushed toward the middle by the same amount on either side, like a valley. I am sure: nothing else I can imagine fits what I saw. `a = 1.50·tanh(1.6u) − 1.30·tanh(x/0.05)`
- **swing** (truth: wave with position). It is pulled back the way a swing is: by the sine of how far it has gone. I am sure: I tested it against "straight with position" and it won. `a = 3.92·tanh(1.6u) − 13.63·sin(x)`
- **thick oil** (truth: cubic with speed). It is slowed a little when slow and very sharply when fast, by speed cubed. I am sure: nothing else I can imagine fits what I saw. `a = 4.20·tanh(1.6u) − 4.55·v³`
- **rubbing** (truth: straight with speed). It is slowed by the sine of its speed. I am sure: I tested it against "steps with speed", "cubic with speed", "growing with speed", "steps with position" and it won. `a = 1.21·tanh(1.6u) − 0.46·sin(v)`
