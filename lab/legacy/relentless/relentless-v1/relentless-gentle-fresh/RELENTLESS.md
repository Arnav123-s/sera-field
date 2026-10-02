# The relentless robot in school: gentle worlds

In these worlds every robot pushes softly (0.3 each way); only the relentless robot may push harder where its idea and a rival would part.

Seeds [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]. Every robot lived the same 40 practice worlds and the same 12-world exam. Numbers are averages over lives, ± one standard error.

- **Tries:** explanations it imagined before and including the right one (1 is best; 12 means never).
- **Sure:** for the relentless robots, every rival was beaten; for the others, the hunch felt strong (0.6 or more), as in the school.

## Exam

| Robot | Familiar: found | Familiar: tries | New: found | New: tries | Ideas imagined per world |
|---|---|---|---|---|---|
| relentless | 0.96 ± 0.01 | 3.13 ± 0.19 | 0.84 ± 0.05 | 4.79 ± 0.31 | 14.49 ± 0.39 |
| no_tests | 0.89 ± 0.03 | 3.18 ± 0.17 | 0.84 ± 0.05 | 4.67 ± 0.28 | 14.53 ± 0.39 |
| imagine_all | 0.89 ± 0.03 | 3.19 ± 0.19 | 0.84 ± 0.05 | 4.64 ± 0.28 | 14.53 ± 0.39 |

## Honesty: the ideas it kept in the exam

| Robot | Sure → right | Unsure → right | Sure but not right (of all kept) |
|---|---|---|---|
| relentless | 100% (209) | 71% (17) | 0% (226) |
| no_tests | 100% (167) | 71% (59) | 0% (226) |
| imagine_all | 92% (225) | 100% (1) | 8% (226) |

## Per force in the exam: found the force

| Robot | rubbing | water drag | dry friction | spring | tight spring | stiff spring | swing | slope | thick oil | valley |
|---|---|---|---|---|---|---|---|---|---|---|
| relentless | 85% | 90% | 100% | 100% | 100% | 100% | 95% | 100% | 70% | 98% |
| no_tests | 80% | 90% | 100% | 60% | 100% | 100% | 80% | 100% | 70% | 98% |
| imagine_all | 80% | 90% | 100% | 60% | 100% | 100% | 80% | 100% | 70% | 98% |

## What the relentless robots did (exam, per world)

| Robot | Pushes of its own | Rivals beaten | Changed its mind (all worlds) | Said "sure" | Right when it said "sure" | Said "not sure" | Right when it said "not sure" |
|---|---|---|---|---|---|---|---|
| relentless | 2.05 ± 0.14 | 1.36 ± 0.13 | 37 | 87% (240) | 100% (209) | 13% (240) | 39% (31) |
| no_tests | 0.00 ± 0.00 | 1.18 ± 0.13 | 5 | 70% (240) | 100% (167) | 30% (240) | 58% (73) |
| imagine_all | 0.00 ± 0.00 | 0.00 ± 0.00 | 0 | 94% (240) | 92% (225) | 6% (240) | 7% (15) |

## What it says: the relentless robot's exam, seed 11

- **swing** (truth: wave with position). It is pulled back the way a swing is: by the sine of how far it has gone. I am sure: I tested it against "straight with position" and it won. `a = 2.71·tanh(1.6u) − 6.94·sin(x)`
- **valley** (truth: steps with position). It is pushed toward the middle by the same amount on either side, like a valley. I am sure: I tested it against "straight with position", "wave with position" and it won. `a = 2.12·tanh(1.6u) − 1.50·tanh(x/0.05)`
- **thick oil** (truth: cubic with speed). It is slowed a little when slow and very sharply when fast, by speed cubed. I am sure: I tested it against "growing with speed" and it won. `a = 1.56·tanh(1.6u) − 1.27·v³`
- **valley** (truth: steps with position). It is pushed toward the middle by the same amount on either side, like a valley. I am sure: nothing else I can imagine fits what I saw. `a = 1.36·tanh(1.6u) − 0.74·tanh(x/0.05)`
- **thick oil** (truth: cubic with speed). It is slowed a little when slow and very sharply when fast, by speed cubed. I am sure: I tested it against "straight with speed", "wave with speed", "growing with speed", "steps with position" and it won. `a = 3.02·tanh(1.6u) − 1.46·v³`
- **water drag** (truth: growing with speed). It is slowed more and more as it goes faster, by speed times speed, like water. I am sure: I tested it against "straight with speed", "wave with speed", "steps with speed", "cubic with speed", "steps with position" and it won. `a = 1.99·tanh(1.6u) − 1.37·v|v|`
- **slope** (truth: a steady push). A steady push always leans it one way, like a slope. I am sure: nothing else I can imagine fits what I saw. `a = 3.15·tanh(1.6u) − 1.55·1`
- **stiff spring** (truth: cubic with position). It is pulled back gently near the middle and very hard far away. I am sure: I tested it against "growing with position" and it won. `a = 1.67·tanh(1.6u) − 8.07·x³`
- **rubbing** (truth: straight with speed). It is slowed by the sine of its speed. I am not sure: "straight with speed" explains what I saw as well, and none of my pushes could tell them apart. `a = 1.59·tanh(1.6u) − 0.60·sin(v)`
- **spring** (truth: straight with position). It is pulled back toward the middle, harder the farther away it is, like a spring. I am sure: I tested it against "wave with position" and it won. `a = 2.52·tanh(1.6u) − 5.90·x`
- **dry friction** (truth: steps with speed). It is slowed by the same amount whenever it moves, like dry friction. I am sure: I tested it against "wave with speed", "straight with speed" and it won. `a = 1.46·tanh(1.6u) − 0.53·tanh(v/0.05)`
- **tight spring** (truth: growing with position). It is pulled back toward the middle, much harder the farther it goes. I am sure: I tested it against "straight with position", "wave with position", "cubic with position" and it won. `a = 1.61·tanh(1.6u) − 2.23·x|x|`
