# The relentless robot in school

Seeds [41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]. Every robot lived the same 40 practice worlds and the same 12-world exam. Numbers are averages over lives, ± one standard error.

- **Tries:** explanations it imagined before and including the right one (1 is best; 12 means never).
- **Sure:** for the relentless robots, every rival was beaten; for the others, the hunch felt strong (0.6 or more), as in the school.

## Exam

| Robot | Familiar: found | Familiar: tries | New: found | New: tries | Ideas imagined per world |
|---|---|---|---|---|---|
| relentless | 0.98 ± 0.01 | 3.33 ± 0.10 | 1.00 ± 0.00 | 3.73 ± 0.22 | 15.19 ± 0.32 |
| no_tests | 0.98 ± 0.01 | 3.33 ± 0.10 | 1.00 ± 0.00 | 3.89 ± 0.21 | 15.19 ± 0.32 |
| imagine_all | 0.95 ± 0.02 | 3.15 ± 0.09 | 1.00 ± 0.00 | 3.96 ± 0.22 | 15.19 ± 0.32 |
| humble | 0.78 ± 0.03 | 4.03 ± 0.15 | 0.68 ± 0.07 | 4.86 ± 0.36 | 5.35 ± 0.15 |
| taught | 0.84 ± 0.02 | 4.21 ± 0.13 | 0.72 ± 0.05 | 5.41 ± 0.48 | 4.83 ± 0.13 |
| credit_only | 0.78 ± 0.03 | 4.06 ± 0.20 | 0.65 ± 0.05 | 4.88 ± 0.35 | 4.74 ± 0.20 |
| self_taught | 0.78 ± 0.02 | 4.64 ± 0.19 | 0.70 ± 0.06 | 5.81 ± 0.36 | 4.93 ± 0.18 |
| untaught | 0.71 ± 0.03 | 6.59 ± 0.31 | 0.82 ± 0.04 | 6.06 ± 0.39 | 6.53 ± 0.17 |

## Honesty: the ideas it kept in the exam

| Robot | Sure → right | Unsure → right | Sure but not right (of all kept) |
|---|---|---|---|
| relentless | 100% (235) | 40% (5) | 0% (240) |
| no_tests | 100% (231) | 67% (9) | 0% (240) |
| imagine_all | 97% (240) | - | 3% (240) |
| humble | 74% (65) | 81% (161) | 8% (226) |
| taught | 80% (87) | 85% (145) | 7% (232) |
| credit_only | 73% (73) | 82% (151) | 9% (224) |
| self_taught | 67% (101) | 84% (133) | 14% (234) |
| untaught | 100% (12) | 78% (213) | 0% (225) |

## Per force in the exam: found the force

| Robot | rubbing | water drag | dry friction | spring | tight spring | stiff spring | swing | slope | thick oil | valley |
|---|---|---|---|---|---|---|---|---|---|---|
| relentless | 100% | 100% | 100% | 90% | 100% | 100% | 95% | 100% | 100% | 100% |
| no_tests | 100% | 100% | 100% | 90% | 100% | 100% | 95% | 100% | 100% | 100% |
| imagine_all | 85% | 100% | 100% | 85% | 100% | 100% | 90% | 100% | 100% | 100% |
| humble | 65% | 80% | 95% | 75% | 90% | 85% | 35% | 95% | 50% | 85% |
| taught | 85% | 100% | 100% | 85% | 90% | 90% | 30% | 95% | 55% | 90% |
| credit_only | 55% | 85% | 95% | 60% | 90% | 95% | 55% | 90% | 48% | 82% |
| self_taught | 60% | 70% | 100% | 60% | 95% | 95% | 45% | 95% | 52% | 88% |
| untaught | 50% | 70% | 90% | 50% | 80% | 85% | 50% | 90% | 72% | 92% |

## What the relentless robots did (exam, per world)

| Robot | Pushes of its own | Rivals beaten | Changed its mind (all worlds) | Said "sure" | Right when it said "sure" | Said "not sure" | Right when it said "not sure" |
|---|---|---|---|---|---|---|---|
| relentless | 3.25 ± 0.08 | 10.17 ± 0.08 | 13 | 98% (240) | 100% (235) | 2% (240) | 40% (5) |
| no_tests | 0.00 ± 0.00 | 10.15 ± 0.08 | 13 | 96% (240) | 100% (231) | 4% (240) | 67% (9) |
| imagine_all | 0.00 ± 0.00 | 0.00 ± 0.00 | 0 | 100% (240) | 97% (240) | 0% (240) | - |

## What it says: the relentless robot's exam, seed 41

- **thick oil** (truth: cubic with speed). It is slowed a little when slow and very sharply when fast, by speed cubed. I am sure: I tested it against "growing with speed" and it won, and every other idea I can imagine fits worse. `a = 1.84·tanh(1.6u) − 2.26·v³`
- **spring** (truth: straight with position). It is pulled back toward the middle, harder the farther away it is, like a spring. I am sure: I tested it against "wave with position" and it won, and every other idea I can imagine fits worse. `a = 3.55·tanh(1.6u) − 4.64·x`
- **slope** (truth: a steady push). A steady push always leans it one way, like a slope. I am sure: nothing else I can imagine fits what I saw. `a = 1.23·tanh(1.6u) − 0.38·1`
- **tight spring** (truth: growing with position). It is pulled back toward the middle, much harder the farther it goes. I am sure: nothing else I can imagine fits what I saw. `a = 3.43·tanh(1.6u) − 10.85·x|x|`
- **rubbing** (truth: straight with speed). It is slowed in step with its speed, like rubbing. I am sure: I tested it against "wave with speed" and it won, and every other idea I can imagine fits worse. `a = 3.51·tanh(1.6u) − 1.42·v`
- **swing** (truth: wave with position). It is pulled back the way a swing is: by the sine of how far it has gone. I am sure: I tested it against "straight with position" and it won, and every other idea I can imagine fits worse. `a = 3.67·tanh(1.6u) − 11.24·sin(x)`
- **valley** (truth: steps with position). It is pushed toward the middle by the same amount on either side, like a valley. I am sure: nothing else I can imagine fits what I saw. `a = 4.21·tanh(1.6u) − 1.62·tanh(x/0.05)`
- **stiff spring** (truth: cubic with position). It is pulled back gently near the middle and very hard far away. I am sure: nothing else I can imagine fits what I saw. `a = 4.04·tanh(1.6u) − 14.40·x³`
- **thick oil** (truth: cubic with speed). It is slowed a little when slow and very sharply when fast, by speed cubed. I am sure: I tested it against "growing with speed" and it won, and every other idea I can imagine fits worse. `a = 1.50·tanh(1.6u) − 0.64·v³`
- **water drag** (truth: growing with speed). It is slowed more and more as it goes faster, by speed times speed, like water. I am sure: nothing else I can imagine fits what I saw. `a = 1.63·tanh(1.6u) − 1.12·v|v|`
- **dry friction** (truth: steps with speed). It is slowed by the same amount whenever it moves, like dry friction. I am sure: nothing else I can imagine fits what I saw. `a = 1.40·tanh(1.6u) − 0.52·tanh(v/0.05)`
- **valley** (truth: steps with position). It is pushed toward the middle by the same amount on either side, like a valley. I am sure: nothing else I can imagine fits what I saw. `a = 1.40·tanh(1.6u) − 0.80·tanh(x/0.05)`
