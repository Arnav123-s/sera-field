# The relentless robot in school: gentle worlds

In these worlds every robot pushes softly (0.3 each way); only the relentless robot may push harder where its idea and a rival would part.

Seeds [41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]. Every robot lived the same 40 practice worlds and the same 12-world exam. Numbers are averages over lives, ± one standard error.

- **Tries:** explanations it imagined before and including the right one (1 is best; 12 means never).
- **Sure:** for the relentless robots, every rival was beaten; for the others, the hunch felt strong (0.6 or more), as in the school.

## Exam

| Robot | Familiar: found | Familiar: tries | New: found | New: tries | Ideas imagined per world |
|---|---|---|---|---|---|
| relentless | 0.97 ± 0.01 | 3.01 ± 0.13 | 0.91 ± 0.03 | 4.49 ± 0.21 | 14.81 ± 0.28 |
| no_tests | 0.86 ± 0.03 | 2.98 ± 0.12 | 0.91 ± 0.03 | 4.29 ± 0.21 | 14.98 ± 0.29 |
| imagine_all | 0.86 ± 0.03 | 2.96 ± 0.10 | 0.91 ± 0.03 | 4.24 ± 0.22 | 14.98 ± 0.29 |

## Honesty: the ideas it kept in the exam

| Robot | Sure → right | Unsure → right | Sure but not right (of all kept) |
|---|---|---|---|
| relentless | 100% (228) | 25% (4) | 0% (232) |
| no_tests | 100% (173) | 64% (59) | 0% (232) |
| imagine_all | 91% (232) | - | 9% (232) |

## Per force in the exam: found the force

| Robot | rubbing | water drag | dry friction | spring | tight spring | stiff spring | swing | slope | thick oil | valley |
|---|---|---|---|---|---|---|---|---|---|---|
| relentless | 100% | 95% | 100% | 90% | 100% | 100% | 95% | 100% | 82% | 100% |
| no_tests | 80% | 95% | 100% | 50% | 100% | 100% | 65% | 100% | 82% | 100% |
| imagine_all | 75% | 95% | 100% | 50% | 100% | 100% | 65% | 100% | 82% | 100% |

## What the relentless robots did (exam, per world)

| Robot | Pushes of its own | Rivals beaten | Changed its mind (all worlds) | Said "sure" | Right when it said "sure" | Said "not sure" | Right when it said "not sure" |
|---|---|---|---|---|---|---|---|
| relentless | 3.66 ± 0.09 | 10.61 ± 0.17 | 44 | 95% (240) | 100% (228) | 5% (240) | 8% (12) |
| no_tests | 0.00 ± 0.00 | 9.66 ± 0.08 | 7 | 72% (240) | 100% (173) | 28% (240) | 57% (67) |
| imagine_all | 0.00 ± 0.00 | 0.00 ± 0.00 | 0 | 97% (240) | 91% (232) | 3% (240) | 0% (8) |

## What it says: the relentless robot's exam, seed 41

- **thick oil** (truth: cubic with speed). It is slowed a little when slow and very sharply when fast, by speed cubed. I am sure: I tested it against "straight with speed", "growing with speed", "straight with position", "cubic with position", "growing with position", "wave with speed", "wave with position", "steps with speed", "steps with position" and it won, and every other idea I can imagine fits worse. `a = 1.84·tanh(1.6u) − 2.25·v³`
- **spring** (truth: straight with position). It is pulled back toward the middle, harder the farther away it is, like a spring. I am sure: I tested it against "growing with position", "wave with position" and it won, and every other idea I can imagine fits worse. `a = 3.55·tanh(1.6u) − 4.64·x`
- **slope** (truth: a steady push). A steady push always leans it one way, like a slope. I am sure: nothing else I can imagine fits what I saw. `a = 1.23·tanh(1.6u) − 0.38·1`
- **tight spring** (truth: growing with position). It is pulled back toward the middle, much harder the farther it goes. I am sure: nothing else I can imagine fits what I saw. `a = 3.42·tanh(1.6u) − 10.84·x|x|`
- **rubbing** (truth: straight with speed). It is slowed in step with its speed, like rubbing. I am sure: I tested it against "wave with speed" and it won, and every other idea I can imagine fits worse. `a = 3.52·tanh(1.6u) − 1.42·v`
- **swing** (truth: wave with position). It is pulled back the way a swing is: by the sine of how far it has gone. I am sure: I tested it against "straight with position" and it won, and every other idea I can imagine fits worse. `a = 3.67·tanh(1.6u) − 11.24·sin(x)`
- **valley** (truth: steps with position). It is pushed toward the middle by the same amount on either side, like a valley. I am sure: I tested it against "straight with position", "wave with position" and it won, and every other idea I can imagine fits worse. `a = 4.21·tanh(1.6u) − 1.63·tanh(x/0.05)`
- **stiff spring** (truth: cubic with position). It is pulled back gently near the middle and very hard far away. I am sure: I tested it against "growing with position" and it won, and every other idea I can imagine fits worse. `a = 4.04·tanh(1.6u) − 14.36·x³`
- **thick oil** (truth: cubic with speed). It is slowed a little when slow and very sharply when fast, by speed cubed. I am sure: I tested it against "straight with speed", "growing with position", "growing with speed", "wave with speed", "straight with position", "steps with speed", "cubic with position", "wave with position", "steps with position" and it won, and every other idea I can imagine fits worse. `a = 1.49·tanh(1.6u) − 0.64·v³`
- **water drag** (truth: growing with speed). It is slowed more and more as it goes faster, by speed times speed, like water. I am sure: nothing else I can imagine fits what I saw. `a = 1.63·tanh(1.6u) − 1.12·v|v|`
- **dry friction** (truth: steps with speed). It is slowed by the same amount whenever it moves, like dry friction. I am sure: nothing else I can imagine fits what I saw. `a = 1.36·tanh(1.6u) − 0.51·tanh(v/0.05)`
- **valley** (truth: steps with position). It is pushed toward the middle by the same amount on either side, like a valley. I am sure: nothing else I can imagine fits what I saw. `a = 1.39·tanh(1.6u) − 0.79·tanh(x/0.05)`
