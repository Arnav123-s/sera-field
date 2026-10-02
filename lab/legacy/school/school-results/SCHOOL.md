# ccops5 school results

Seeds [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]: every learner lived the same 40 practice worlds and the same 12-world exam. In the exam nobody gets help and nobody learns.

- **Right idea was number:** how many explanations it imagined before (and including) the right one. 1 is best; 12 means it never imagined it.
- **Found at situation:** when it kept the right idea, out of 10 situations per world; 11 means never.
- **Calibration:** how far its confidence was from the truth (0 is perfect, lower is better).

## Practice: getting better at discovering

Right idea was number (average), per block of 8 practice worlds. For `taught`, the teacher showed the answer in block 1 and gave fading hints in blocks 2 and 3.

| Learner | worlds 1-8 | worlds 9-16 | worlds 17-24 | worlds 25-32 | worlds 33-40 |
|---|---|---|---|---|---|
| humble | 1.00 | 3.91 | 4.85 | 4.36 | 4.84 |
| taught | 1.00 | 4.16 | 4.42 | 4.45 | 4.78 |
| credit_only | 5.69 | 5.49 | 5.40 | 4.70 | 5.08 |
| self_taught | 6.05 | 5.60 | 5.60 | 4.91 | 5.38 |
| untaught | 6.65 | 6.45 | 6.66 | 6.54 | 6.50 |

## Final exam: all 12 exam worlds

| Learner | Found the force | Right idea was number | Found at situation | Partly-right ideas kept | Wrong ideas kept | Guess miss (median) | Calibration |
|---|---|---|---|---|---|---|---|
| humble | 78% | 4.27 | 5.12 | 0.17 | 0.00 | 0.392 | 0.206 |
| taught | 80% | 4.19 | 5.08 | 0.17 | 0.01 | 0.357 | 0.259 |
| credit_only | 78% | 4.47 | 5.29 | 0.17 | 0.01 | 0.403 | 0.227 |
| self_taught | 78% | 5.02 | 5.47 | 0.19 | 0.00 | 0.413 | 0.245 |
| untaught | 73% | 6.99 | 6.80 | 0.19 | 0.01 | 0.550 | 0.141 |

## Final exam: the 8 kinds of force it practised

| Learner | Found the force | Right idea was number | Found at situation | Partly-right ideas kept | Wrong ideas kept | Guess miss (median) | Calibration |
|---|---|---|---|---|---|---|---|
| humble | 78% | 4.40 | 5.08 | 0.19 | 0.00 | 0.392 | 0.190 |
| taught | 81% | 3.84 | 4.86 | 0.15 | 0.00 | 0.357 | 0.216 |
| credit_only | 79% | 4.22 | 5.17 | 0.19 | 0.00 | 0.403 | 0.214 |
| self_taught | 79% | 4.81 | 5.21 | 0.19 | 0.00 | 0.413 | 0.235 |
| untaught | 68% | 7.49 | 7.17 | 0.25 | 0.01 | 0.550 | 0.132 |

## Final exam: the 4 worlds with forces it was never shown

| Learner | Found the force | Right idea was number | Found at situation | Partly-right ideas kept | Wrong ideas kept | Guess miss (median) | Calibration |
|---|---|---|---|---|---|---|---|
| humble | 80% | 4.00 | 5.22 | 0.15 | 0.00 | 0.510 | 0.239 |
| taught | 78% | 4.90 | 5.53 | 0.20 | 0.03 | 0.570 | 0.346 |
| credit_only | 78% | 4.95 | 5.53 | 0.15 | 0.03 | 0.530 | 0.252 |
| self_taught | 78% | 5.42 | 5.97 | 0.20 | 0.00 | 0.530 | 0.266 |
| untaught | 85% | 6.00 | 6.05 | 0.07 | 0.00 | 0.604 | 0.159 |

## Doubt: how sure it was about the ideas it kept (exam)

| Learner | Kept after one check (sure) | ...of those, right | Kept after two checks (unsure) | ...of those, right |
|---|---|---|---|---|
| humble | 42 | 83% | 73 | 81% |
| taught | 46 | 74% | 71 | 87% |
| credit_only | 41 | 80% | 75 | 81% |
| self_taught | 52 | 71% | 65 | 88% |
| untaught | 7 | 100% | 105 | 77% |

## Per force in the exam: found the force

| Learner | rubbing | water drag | dry friction | spring | tight spring | stiff spring | swing | slope | thick oil | valley |
|---|---|---|---|---|---|---|---|---|---|---|
| humble | 50% | 80% | 90% | 80% | 90% | 100% | 30% | 100% | 65% | 95% |
| taught | 80% | 90% | 90% | 90% | 80% | 100% | 20% | 100% | 55% | 100% |
| credit_only | 80% | 100% | 90% | 70% | 90% | 100% | 0% | 100% | 60% | 95% |
| self_taught | 60% | 70% | 100% | 80% | 90% | 80% | 50% | 100% | 60% | 95% |
| untaught | 30% | 60% | 90% | 60% | 90% | 90% | 20% | 100% | 75% | 95% |
