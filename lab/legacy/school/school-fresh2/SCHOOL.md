# ccops5 school results

Seeds [21, 22, 23, 24, 25, 26, 27, 28, 29, 30]: every learner lived the same 40 practice worlds and the same 12-world exam. In the exam nobody gets help and nobody learns.

- **Right idea was number:** how many explanations it imagined before (and including) the right one. 1 is best; 12 means it never imagined it.
- **Found at situation:** when it kept the right idea, out of 10 situations per world; 11 means never.
- **Calibration:** how far its confidence was from the truth (0 is perfect, lower is better).

## Practice: getting better at discovering

Right idea was number (average), per block of 8 practice worlds. For `taught`, the teacher showed the answer in block 1 and gave fading hints in blocks 2 and 3.

| Learner | worlds 1-8 | worlds 9-16 | worlds 17-24 | worlds 25-32 | worlds 33-40 |
|---|---|---|---|---|---|
| humble | 1.00 | 3.96 | 3.89 | 4.91 | 4.72 |
| taught | 1.00 | 4.36 | 4.51 | 5.09 | 4.62 |
| credit_only | 6.22 | 4.85 | 5.15 | 5.30 | 4.31 |
| self_taught | 6.12 | 5.69 | 5.66 | 4.94 | 4.79 |
| untaught | 7.74 | 6.15 | 6.69 | 6.36 | 6.55 |

## Final exam: all 12 exam worlds

| Learner | Found the force | Right idea was number | Found at situation | Partly-right ideas kept | Wrong ideas kept | Guess miss (median) | Calibration |
|---|---|---|---|---|---|---|---|
| humble | 75% | 4.44 | 5.51 | 0.19 | 0.00 | 0.370 | 0.209 |
| taught | 78% | 4.77 | 5.32 | 0.17 | 0.02 | 0.376 | 0.233 |
| credit_only | 82% | 3.90 | 4.86 | 0.14 | 0.02 | 0.423 | 0.255 |
| self_taught | 78% | 4.76 | 5.41 | 0.17 | 0.01 | 0.387 | 0.284 |
| untaught | 74% | 6.83 | 6.68 | 0.22 | 0.00 | 0.569 | 0.143 |

## Final exam: the 8 kinds of force it practised

| Learner | Found the force | Right idea was number | Found at situation | Partly-right ideas kept | Wrong ideas kept | Guess miss (median) | Calibration |
|---|---|---|---|---|---|---|---|
| humble | 72% | 4.51 | 5.50 | 0.23 | 0.00 | 0.370 | 0.190 |
| taught | 79% | 4.54 | 5.11 | 0.17 | 0.03 | 0.376 | 0.220 |
| credit_only | 85% | 3.75 | 4.66 | 0.14 | 0.01 | 0.423 | 0.244 |
| self_taught | 78% | 4.66 | 5.20 | 0.19 | 0.00 | 0.387 | 0.265 |
| untaught | 72% | 6.85 | 6.64 | 0.25 | 0.00 | 0.569 | 0.142 |

## Final exam: the 4 worlds with forces it was never shown

| Learner | Found the force | Right idea was number | Found at situation | Partly-right ideas kept | Wrong ideas kept | Guess miss (median) | Calibration |
|---|---|---|---|---|---|---|---|
| humble | 80% | 4.30 | 5.53 | 0.12 | 0.00 | 0.408 | 0.246 |
| taught | 78% | 5.22 | 5.72 | 0.15 | 0.00 | 0.439 | 0.258 |
| credit_only | 78% | 4.20 | 5.25 | 0.15 | 0.03 | 0.439 | 0.277 |
| self_taught | 78% | 4.95 | 5.83 | 0.15 | 0.03 | 0.477 | 0.320 |
| untaught | 78% | 6.80 | 6.78 | 0.15 | 0.00 | 0.531 | 0.145 |

## Doubt: how sure it was about the ideas it kept (exam)

| Learner | Kept after one check (sure) | ...of those, right | Kept after two checks (unsure) | ...of those, right |
|---|---|---|---|---|
| humble | 29 | 83% | 84 | 79% |
| taught | 36 | 72% | 80 | 85% |
| credit_only | 34 | 82% | 84 | 85% |
| self_taught | 48 | 67% | 67 | 91% |
| untaught | 4 | 100% | 111 | 77% |

## Per force in the exam: found the force

| Learner | rubbing | water drag | dry friction | spring | tight spring | stiff spring | swing | slope | thick oil | valley |
|---|---|---|---|---|---|---|---|---|---|---|
| humble | 60% | 70% | 90% | 80% | 100% | 90% | 0% | 90% | 65% | 95% |
| taught | 60% | 80% | 90% | 90% | 100% | 90% | 20% | 100% | 60% | 95% |
| credit_only | 50% | 90% | 100% | 90% | 100% | 100% | 50% | 100% | 60% | 95% |
| self_taught | 80% | 60% | 90% | 70% | 100% | 90% | 40% | 90% | 60% | 95% |
| untaught | 40% | 60% | 90% | 40% | 80% | 100% | 70% | 100% | 60% | 95% |
