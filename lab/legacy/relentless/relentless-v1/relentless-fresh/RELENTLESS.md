# The relentless robot in school

Seeds [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]. Every robot lived the same 40 practice worlds and the same 12-world exam. Numbers are averages over lives, ± one standard error.

- **Tries:** explanations it imagined before and including the right one (1 is best; 12 means never).
- **Sure:** for the relentless robots, every rival was beaten; for the others, the hunch felt strong (0.6 or more), as in the school.

## Exam

| Robot | Familiar: found | Familiar: tries | New: found | New: tries | Ideas imagined per world |
|---|---|---|---|---|---|
| relentless | 0.98 ± 0.01 | 3.21 ± 0.12 | 1.00 ± 0.00 | 3.67 ± 0.24 | 15.11 ± 0.32 |
| no_tests | 0.98 ± 0.01 | 3.17 ± 0.11 | 1.00 ± 0.00 | 3.74 ± 0.24 | 15.11 ± 0.32 |
| imagine_all | 0.98 ± 0.01 | 3.17 ± 0.10 | 1.00 ± 0.00 | 3.61 ± 0.26 | 15.11 ± 0.32 |
| humble | 0.74 ± 0.02 | 4.31 ± 0.17 | 0.80 ± 0.05 | 4.31 ± 0.32 | 4.99 ± 0.13 |
| taught | 0.81 ± 0.02 | 4.22 ± 0.13 | 0.80 ± 0.05 | 4.61 ± 0.42 | 4.32 ± 0.15 |
| credit_only | 0.81 ± 0.03 | 4.03 ± 0.22 | 0.76 ± 0.05 | 4.29 ± 0.37 | 4.34 ± 0.12 |
| self_taught | 0.74 ± 0.03 | 4.69 ± 0.23 | 0.75 ± 0.05 | 5.35 ± 0.40 | 4.58 ± 0.11 |
| untaught | 0.74 ± 0.04 | 6.83 ± 0.38 | 0.76 ± 0.04 | 6.54 ± 0.44 | 6.31 ± 0.24 |

## Honesty: the ideas it kept in the exam

| Robot | Sure → right | Unsure → right | Sure but not right (of all kept) |
|---|---|---|---|
| relentless | 100% (222) | 83% (18) | 0% (240) |
| no_tests | 100% (220) | 85% (20) | 0% (240) |
| imagine_all | 99% (239) | 100% (1) | 1% (240) |
| humble | 81% (59) | 79% (169) | 5% (228) |
| taught | 79% (72) | 83% (163) | 6% (235) |
| credit_only | 79% (75) | 81% (162) | 7% (237) |
| self_taught | 58% (88) | 90% (142) | 16% (230) |
| untaught | 100% (13) | 75% (221) | 0% (234) |

## Per force in the exam: found the force

| Robot | rubbing | water drag | dry friction | spring | tight spring | stiff spring | swing | slope | thick oil | valley |
|---|---|---|---|---|---|---|---|---|---|---|
| relentless | 90% | 100% | 100% | 100% | 100% | 100% | 95% | 100% | 100% | 100% |
| no_tests | 90% | 100% | 100% | 100% | 100% | 100% | 95% | 100% | 100% | 100% |
| imagine_all | 90% | 100% | 100% | 100% | 100% | 100% | 95% | 100% | 100% | 100% |
| humble | 55% | 75% | 95% | 80% | 95% | 85% | 15% | 90% | 65% | 95% |
| taught | 65% | 85% | 95% | 90% | 100% | 90% | 20% | 100% | 65% | 95% |
| credit_only | 50% | 90% | 100% | 90% | 95% | 95% | 30% | 100% | 57% | 95% |
| self_taught | 65% | 60% | 90% | 55% | 95% | 95% | 45% | 90% | 55% | 95% |
| untaught | 45% | 55% | 95% | 50% | 90% | 95% | 60% | 100% | 57% | 95% |

## What the relentless robots did (exam, per world)

| Robot | Pushes of its own | Rivals beaten | Changed its mind (all worlds) | Said "sure" | Right when it said "sure" | Said "not sure" | Right when it said "not sure" |
|---|---|---|---|---|---|---|---|
| relentless | 1.24 ± 0.12 | 0.97 ± 0.13 | 9 | 92% (240) | 100% (222) | 8% (240) | 83% (18) |
| no_tests | 0.00 ± 0.00 | 0.96 ± 0.13 | 9 | 92% (240) | 100% (220) | 8% (240) | 85% (20) |
| imagine_all | 0.00 ± 0.00 | 0.00 ± 0.00 | 0 | 100% (240) | 99% (239) | 0% (240) | 100% (1) |

## What it says: the relentless robot's exam, seed 11

- **swing** (truth: wave with position). It is pulled back the way a swing is: by the sine of how far it has gone. I am sure: I tested it against "straight with position" and it won. `a = 2.70·tanh(1.6u) − 6.94·sin(x)`
- **valley** (truth: steps with position). It is pushed toward the middle by the same amount on either side, like a valley. I am sure: nothing else I can imagine fits what I saw. `a = 2.12·tanh(1.6u) − 1.50·tanh(x/0.05)`
- **thick oil** (truth: cubic with speed). It is slowed a little when slow and very sharply when fast, by speed cubed. I am sure: nothing else I can imagine fits what I saw. `a = 1.56·tanh(1.6u) − 1.26·v³`
- **valley** (truth: steps with position). It is pushed toward the middle by the same amount on either side, like a valley. I am sure: nothing else I can imagine fits what I saw. `a = 1.37·tanh(1.6u) − 0.74·tanh(x/0.05)`
- **thick oil** (truth: cubic with speed). It is slowed a little when slow and very sharply when fast, by speed cubed. I am sure: I tested it against "straight with speed", "steps with speed", "straight with position", "wave with speed", "growing with speed", "wave with position", "steps with position" and it won. `a = 3.02·tanh(1.6u) − 1.46·v³`
- **water drag** (truth: growing with speed). It is slowed more and more as it goes faster, by speed times speed, like water. I am sure: nothing else I can imagine fits what I saw. `a = 1.99·tanh(1.6u) − 1.37·v|v|`
- **slope** (truth: a steady push). A steady push always leans it one way, like a slope. I am sure: nothing else I can imagine fits what I saw. `a = 3.15·tanh(1.6u) − 1.55·1`
- **stiff spring** (truth: cubic with position). It is pulled back gently near the middle and very hard far away. I am sure: nothing else I can imagine fits what I saw. `a = 1.67·tanh(1.6u) − 8.09·x³`
- **rubbing** (truth: straight with speed). It is slowed by the sine of its speed. I am not sure: "straight with speed" explains what I saw as well, and none of my pushes could tell them apart. `a = 1.60·tanh(1.6u) − 0.61·sin(v)`
- **spring** (truth: straight with position). It is pulled back toward the middle, harder the farther away it is, like a spring. I am sure: I tested it against "wave with position" and it won. `a = 2.53·tanh(1.6u) − 5.91·x`
- **dry friction** (truth: steps with speed). It is slowed by the same amount whenever it moves, like dry friction. I am sure: nothing else I can imagine fits what I saw. `a = 1.48·tanh(1.6u) − 0.54·tanh(v/0.05)`
- **tight spring** (truth: growing with position). It is pulled back toward the middle, much harder the farther it goes. I am sure: nothing else I can imagine fits what I saw. `a = 1.61·tanh(1.6u) − 2.25·x|x|`
