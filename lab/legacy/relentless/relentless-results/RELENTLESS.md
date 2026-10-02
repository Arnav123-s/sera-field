# The relentless robot in school

Seeds [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]. Every robot lived the same 40 practice worlds and the same 12-world exam. Numbers are averages over lives, ± one standard error.

- **Tries:** explanations it imagined before and including the right one (1 is best; 12 means never).
- **Sure:** for the relentless robots, every rival was beaten; for the others, the hunch felt strong (0.6 or more), as in the school.

## Exam

| Robot | Familiar: found | Familiar: tries | New: found | New: tries | Ideas imagined per world |
|---|---|---|---|---|---|
| relentless | 0.99 ± 0.01 | 2.98 ± 0.11 | 1.00 ± 0.00 | 3.77 ± 0.31 | 15.22 ± 0.38 |
| no_tests | 0.99 ± 0.01 | 2.96 ± 0.14 | 1.00 ± 0.00 | 3.80 ± 0.33 | 15.22 ± 0.38 |
| imagine_all | 0.99 ± 0.01 | 3.16 ± 0.15 | 1.00 ± 0.00 | 3.98 ± 0.31 | 15.22 ± 0.38 |
| humble | 0.78 ± 0.04 | 4.40 ± 0.37 | 0.80 ± 0.03 | 4.00 ± 0.45 | 5.02 ± 0.18 |
| taught | 0.81 ± 0.03 | 3.84 ± 0.22 | 0.78 ± 0.06 | 4.90 ± 0.54 | 4.51 ± 0.22 |
| credit_only | 0.79 ± 0.03 | 4.22 ± 0.20 | 0.78 ± 0.06 | 4.95 ± 0.45 | 4.48 ± 0.20 |
| self_taught | 0.79 ± 0.03 | 4.81 ± 0.40 | 0.78 ± 0.06 | 5.42 ± 0.59 | 5.06 ± 0.23 |
| untaught | 0.68 ± 0.03 | 7.49 ± 0.25 | 0.85 ± 0.06 | 6.00 ± 0.47 | 6.44 ± 0.18 |

## Honesty: the ideas it kept in the exam

| Robot | Sure → right | Unsure → right | Sure but not right (of all kept) |
|---|---|---|---|
| relentless | 100% (118) | 50% (2) | 0% (120) |
| no_tests | 100% (118) | 50% (2) | 0% (120) |
| imagine_all | 99% (120) | - | 1% (120) |
| humble | 83% (42) | 81% (73) | 6% (115) |
| taught | 74% (46) | 87% (71) | 10% (117) |
| credit_only | 80% (41) | 81% (75) | 7% (116) |
| self_taught | 71% (52) | 88% (65) | 13% (117) |
| untaught | 100% (7) | 77% (105) | 0% (112) |

## Per force in the exam: found the force

| Robot | rubbing | water drag | dry friction | spring | tight spring | stiff spring | swing | slope | thick oil | valley |
|---|---|---|---|---|---|---|---|---|---|---|
| relentless | 100% | 100% | 100% | 100% | 100% | 100% | 90% | 100% | 100% | 100% |
| no_tests | 100% | 100% | 100% | 100% | 100% | 100% | 90% | 100% | 100% | 100% |
| imagine_all | 100% | 100% | 100% | 100% | 100% | 100% | 90% | 100% | 100% | 100% |
| humble | 50% | 80% | 90% | 80% | 90% | 100% | 30% | 100% | 65% | 95% |
| taught | 80% | 90% | 90% | 90% | 80% | 100% | 20% | 100% | 55% | 100% |
| credit_only | 80% | 100% | 90% | 70% | 90% | 100% | 0% | 100% | 60% | 95% |
| self_taught | 60% | 70% | 100% | 80% | 90% | 80% | 50% | 100% | 60% | 95% |
| untaught | 30% | 60% | 90% | 60% | 90% | 90% | 20% | 100% | 75% | 95% |

## What the relentless robots did (exam, per world)

| Robot | Pushes of its own | Rivals beaten | Changed its mind (all worlds) | Said "sure" | Right when it said "sure" | Said "not sure" | Right when it said "not sure" |
|---|---|---|---|---|---|---|---|
| relentless | 3.43 ± 0.15 | 10.08 ± 0.08 | 4 | 98% (120) | 100% (118) | 2% (120) | 50% (2) |
| no_tests | 0.00 ± 0.00 | 10.12 ± 0.10 | 3 | 98% (120) | 100% (118) | 2% (120) | 50% (2) |
| imagine_all | 0.00 ± 0.00 | 0.00 ± 0.00 | 0 | 100% (120) | 99% (120) | 0% (120) | - |

## What it says: the relentless robot's exam, seed 1

- **spring** (truth: straight with position). It is pulled back toward the middle, harder the farther away it is, like a spring. I am sure: I tested it against "wave with position" and every other idea I can imagine fits worse, and it won. `a = 2.85·tanh(1.6u) − 6.33·x`
- **swing** (truth: wave with position). It is pulled back the way a swing is: by the sine of how far it has gone. I am sure: I tested it against "straight with position" and every other idea I can imagine fits worse, and it won. `a = 1.63·tanh(1.6u) − 3.86·sin(x)`
- **thick oil** (truth: cubic with speed). It is slowed a little when slow and very sharply when fast, by speed cubed. I am sure: nothing else I can imagine fits what I saw. `a = 2.98·tanh(1.6u) − 2.02·v³`
- **slope** (truth: a steady push). A steady push always leans it one way, like a slope. I am sure: nothing else I can imagine fits what I saw. `a = 3.18·tanh(1.6u) + 0.82·1`
- **dry friction** (truth: steps with speed). It is slowed by the same amount whenever it moves, like dry friction. I am sure: nothing else I can imagine fits what I saw. `a = 1.40·tanh(1.6u) − 0.42·tanh(v/0.05)`
- **thick oil** (truth: cubic with speed). It is slowed a little when slow and very sharply when fast, by speed cubed. I am sure: nothing else I can imagine fits what I saw. `a = 1.45·tanh(1.6u) − 0.12·v³`
- **valley** (truth: steps with position). It is pushed toward the middle by the same amount on either side, like a valley. I am sure: nothing else I can imagine fits what I saw. `a = 3.66·tanh(1.6u) − 1.66·tanh(x/0.05)`
- **rubbing** (truth: straight with speed). It is slowed in step with its speed, like rubbing. I am sure: I tested it against "wave with speed" and every other idea I can imagine fits worse, and it won. `a = 1.47·tanh(1.6u) − 0.41·v`
- **valley** (truth: steps with position). It is pushed toward the middle by the same amount on either side, like a valley. I am sure: nothing else I can imagine fits what I saw. `a = 1.78·tanh(1.6u) − 0.98·tanh(x/0.05)`
- **stiff spring** (truth: cubic with position). It is pulled back gently near the middle and very hard far away. I am sure: nothing else I can imagine fits what I saw. `a = 1.83·tanh(1.6u) − 9.66·x³`
- **tight spring** (truth: growing with position). It is pulled back toward the middle, much harder the farther it goes. I am sure: nothing else I can imagine fits what I saw. `a = 1.60·tanh(1.6u) − 1.86·x|x|`
- **water drag** (truth: growing with speed). It is slowed more and more as it goes faster, by speed times speed, like water. I am sure: I tested it against "straight with speed", "steps with speed", "cubic with speed", "wave with speed", "steps with position" and every other idea I can imagine fits worse, and it won. `a = 1.25·tanh(1.6u) − 0.78·v|v|`
