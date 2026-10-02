# The relentless robot in school: gentle worlds

In these worlds every robot pushes softly (0.3 each way); only the relentless robot may push harder where its idea and a rival would part.

Seeds [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]. Every robot lived the same 40 practice worlds and the same 12-world exam. Numbers are averages over lives, ± one standard error.

- **Tries:** explanations it imagined before and including the right one (1 is best; 12 means never).
- **Sure:** for the relentless robots, every rival was beaten; for the others, the hunch felt strong (0.6 or more), as in the school.

## Exam

| Robot | Familiar: found | Familiar: tries | New: found | New: tries | Ideas imagined per world |
|---|---|---|---|---|---|
| relentless | 0.99 ± 0.01 | 2.98 ± 0.09 | 0.85 ± 0.06 | 4.42 ± 0.32 | 14.54 ± 0.42 |
| no_tests | 0.89 ± 0.02 | 2.85 ± 0.12 | 0.85 ± 0.06 | 4.05 ± 0.38 | 14.62 ± 0.45 |
| imagine_all | 0.89 ± 0.02 | 2.77 ± 0.08 | 0.85 ± 0.06 | 4.03 ± 0.39 | 14.62 ± 0.45 |

## Honesty: the ideas it kept in the exam

| Robot | Sure → right | Unsure → right | Sure but not right (of all kept) |
|---|---|---|---|
| relentless | 100% (113) | 0% (1) | 0% (114) |
| no_tests | 100% (82) | 72% (32) | 0% (114) |
| imagine_all | 92% (114) | - | 8% (114) |

## Per force in the exam: found the force

| Robot | rubbing | water drag | dry friction | spring | tight spring | stiff spring | swing | slope | thick oil | valley |
|---|---|---|---|---|---|---|---|---|---|---|
| relentless | 100% | 100% | 100% | 100% | 100% | 100% | 90% | 100% | 70% | 100% |
| no_tests | 90% | 100% | 100% | 50% | 100% | 100% | 70% | 100% | 70% | 100% |
| imagine_all | 90% | 100% | 100% | 50% | 100% | 100% | 70% | 100% | 70% | 100% |

## What the relentless robots did (exam, per world)

| Robot | Pushes of its own | Rivals beaten | Changed its mind (all worlds) | Said "sure" | Right when it said "sure" | Said "not sure" | Right when it said "not sure" |
|---|---|---|---|---|---|---|---|
| relentless | 3.57 ± 0.14 | 10.35 ± 0.23 | 11 | 94% (120) | 100% (113) | 6% (120) | 0% (7) |
| no_tests | 0.00 ± 0.00 | 9.52 ± 0.12 | 2 | 68% (120) | 100% (82) | 32% (120) | 61% (38) |
| imagine_all | 0.00 ± 0.00 | 0.00 ± 0.00 | 0 | 95% (120) | 92% (114) | 5% (120) | 0% (6) |

## What it says: the relentless robot's exam, seed 1

- **spring** (truth: straight with position). It is pulled back toward the middle, harder the farther away it is, like a spring. I am sure: I tested it against "wave with position", and it won. `a = 2.86·tanh(1.6u) − 6.33·x`
- **swing** (truth: wave with position). It is pulled back the way a swing is: by the sine of how far it has gone. I am sure: I tested it against "straight with position" and every other idea I can imagine fits worse, and it won. `a = 1.63·tanh(1.6u) − 3.86·sin(x)`
- **thick oil** (truth: cubic with speed). It is slowed a little when slow and very sharply when fast, by speed cubed. I am sure: I tested it against "growing with speed", "straight with speed", "wave with speed" and every other idea I can imagine fits worse, and it won. `a = 2.99·tanh(1.6u) − 2.03·v³`
- **slope** (truth: a steady push). A steady push always leans it one way, like a slope. I am sure: nothing else I can imagine fits what I saw. `a = 3.18·tanh(1.6u) + 0.82·1`
- **dry friction** (truth: steps with speed). It is slowed by the same amount whenever it moves, like dry friction. I am sure: I tested it against "wave with speed", "straight with speed" and every other idea I can imagine fits worse, and it won. `a = 1.40·tanh(1.6u) − 0.42·tanh(v/0.05)`
- **thick oil** (truth: cubic with speed). It is slowed a little when slow and very sharply when fast, by speed cubed. I am sure: I tested it against "growing with speed", "straight with speed", "wave with speed", "straight with position", "wave with position", "steps with speed", "steps with position" and every other idea I can imagine fits worse, and it won. `a = 1.45·tanh(1.6u) + 0.61·v³`
- **valley** (truth: steps with position). It is pushed toward the middle by the same amount on either side, like a valley. I am sure: nothing else I can imagine fits what I saw. `a = 3.66·tanh(1.6u) − 1.66·tanh(x/0.05)`
- **rubbing** (truth: straight with speed). It is slowed in step with its speed, like rubbing. I am sure: I tested it against "growing with speed", "steps with speed", "steps with position", "wave with speed" and every other idea I can imagine fits worse, and it won. `a = 1.47·tanh(1.6u) − 0.41·v`
- **valley** (truth: steps with position). It is pushed toward the middle by the same amount on either side, like a valley. I am sure: nothing else I can imagine fits what I saw. `a = 1.78·tanh(1.6u) − 0.99·tanh(x/0.05)`
- **stiff spring** (truth: cubic with position). It is pulled back gently near the middle and very hard far away. I am sure: nothing else I can imagine fits what I saw. `a = 1.83·tanh(1.6u) − 9.63·x³`
- **tight spring** (truth: growing with position). It is pulled back toward the middle, much harder the farther it goes. I am sure: nothing else I can imagine fits what I saw. `a = 1.60·tanh(1.6u) − 1.87·x|x|`
- **water drag** (truth: growing with speed). It is slowed more and more as it goes faster, by speed times speed, like water. I am sure: I tested it against "wave with speed", "straight with speed", "cubic with speed" and every other idea I can imagine fits worse, and it won. `a = 1.25·tanh(1.6u) − 0.78·v|v|`
