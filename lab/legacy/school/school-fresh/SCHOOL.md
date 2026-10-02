# ccops5 school results

Seeds [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]: every learner lived the same 40 practice worlds and the same 12-world exam. In the exam nobody gets help and nobody learns.

- **Right idea was number:** how many explanations it imagined before (and including) the right one. 1 is best; 12 means it never imagined it.
- **Found at situation:** when it kept the right idea, out of 10 situations per world; 11 means never.
- **Calibration:** how far its confidence was from the truth (0 is perfect, lower is better).

## Practice: getting better at discovering

Right idea was number (average), per block of 8 practice worlds. For `taught`, the teacher showed the answer in block 1 and gave fading hints in blocks 2 and 3.

| Learner | worlds 1-8 | worlds 9-16 | worlds 17-24 | worlds 25-32 | worlds 33-40 |
|---|---|---|---|---|---|
| humble | 1.00 | 3.91 | 5.09 | 3.98 | 4.21 |
| taught | 1.00 | 3.52 | 4.96 | 4.70 | 5.03 |
| credit_only | 6.11 | 5.38 | 5.04 | 4.75 | 5.26 |
| self_taught | 6.24 | 5.49 | 5.85 | 5.35 | 5.59 |
| untaught | 7.28 | 6.80 | 7.28 | 6.40 | 6.42 |

## Final exam: all 12 exam worlds

| Learner | Found the force | Right idea was number | Found at situation | Partly-right ideas kept | Wrong ideas kept | Guess miss (median) | Calibration |
|---|---|---|---|---|---|---|---|
| humble | 77% | 4.18 | 5.33 | 0.18 | 0.01 | 0.470 | 0.227 |
| taught | 82% | 3.94 | 4.82 | 0.15 | 0.02 | 0.402 | 0.231 |
| credit_only | 77% | 4.33 | 5.37 | 0.20 | 0.03 | 0.403 | 0.242 |
| self_taught | 72% | 5.07 | 5.92 | 0.23 | 0.01 | 0.374 | 0.317 |
| untaught | 75% | 6.62 | 6.63 | 0.22 | 0.03 | 0.520 | 0.143 |

## Final exam: the 8 kinds of force it practised

| Learner | Found the force | Right idea was number | Found at situation | Partly-right ideas kept | Wrong ideas kept | Guess miss (median) | Calibration |
|---|---|---|---|---|---|---|---|
| humble | 75% | 4.11 | 5.34 | 0.19 | 0.00 | 0.470 | 0.214 |
| taught | 82% | 3.91 | 4.67 | 0.17 | 0.00 | 0.374 | 0.199 |
| credit_only | 78% | 4.30 | 5.22 | 0.19 | 0.03 | 0.374 | 0.215 |
| self_taught | 71% | 4.72 | 5.69 | 0.23 | 0.01 | 0.374 | 0.283 |
| untaught | 75% | 6.80 | 6.66 | 0.24 | 0.01 | 0.520 | 0.137 |

## Final exam: the 4 worlds with forces it was never shown

| Learner | Found the force | Right idea was number | Found at situation | Partly-right ideas kept | Wrong ideas kept | Guess miss (median) | Calibration |
|---|---|---|---|---|---|---|---|
| humble | 80% | 4.33 | 5.33 | 0.17 | 0.03 | 0.559 | 0.255 |
| taught | 82% | 4.00 | 5.10 | 0.10 | 0.05 | 0.752 | 0.296 |
| credit_only | 75% | 4.38 | 5.65 | 0.23 | 0.03 | 0.630 | 0.294 |
| self_taught | 72% | 5.75 | 6.38 | 0.25 | 0.00 | 0.575 | 0.385 |
| untaught | 75% | 6.28 | 6.58 | 0.17 | 0.05 | 0.662 | 0.155 |

## Doubt: how sure it was about the ideas it kept (exam)

| Learner | Kept after one check (sure) | ...of those, right | Kept after two checks (unsure) | ...of those, right |
|---|---|---|---|---|
| humble | 30 | 80% | 85 | 80% |
| taught | 36 | 86% | 83 | 82% |
| credit_only | 41 | 76% | 78 | 78% |
| self_taught | 40 | 48% | 75 | 89% |
| untaught | 9 | 100% | 110 | 74% |

## Per force in the exam: found the force

| Learner | rubbing | water drag | dry friction | spring | tight spring | stiff spring | swing | slope | thick oil | valley |
|---|---|---|---|---|---|---|---|---|---|---|
| humble | 50% | 80% | 100% | 80% | 90% | 80% | 30% | 90% | 65% | 95% |
| taught | 70% | 90% | 100% | 90% | 100% | 90% | 20% | 100% | 70% | 95% |
| credit_only | 50% | 90% | 100% | 90% | 90% | 90% | 10% | 100% | 55% | 95% |
| self_taught | 50% | 60% | 90% | 40% | 90% | 100% | 50% | 90% | 50% | 95% |
| untaught | 50% | 50% | 100% | 60% | 100% | 90% | 50% | 100% | 55% | 95% |
