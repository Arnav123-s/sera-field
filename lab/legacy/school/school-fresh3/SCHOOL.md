# ccops5 school results

Seeds [41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60]: every learner lived the same 40 practice worlds and the same 12-world exam. In the exam nobody gets help and nobody learns.

- **Right idea was number:** how many explanations it imagined before (and including) the right one. 1 is best; 12 means it never imagined it.
- **Found at situation:** when it kept the right idea, out of 10 situations per world; 11 means never.
- **Calibration:** how far its confidence was from the truth (0 is perfect, lower is better).

## Practice: getting better at discovering

Right idea was number (average), per block of 8 practice worlds. For `taught`, the teacher showed the answer in block 1 and gave fading hints in blocks 2 and 3.

| Learner | worlds 1-8 | worlds 9-16 | worlds 17-24 | worlds 25-32 | worlds 33-40 |
|---|---|---|---|---|---|
| humble | 1.00 | 3.89 | 4.68 | 4.54 | 4.94 |
| taught | 1.00 | 4.05 | 4.83 | 4.79 | 4.83 |
| credit_only | 6.10 | 5.78 | 5.59 | 4.83 | 5.09 |
| self_taught | 6.47 | 5.43 | 5.94 | 5.11 | 4.78 |
| untaught | 6.48 | 7.26 | 6.89 | 7.58 | 7.08 |

## Final exam: all 12 exam worlds

| Learner | Found the force | Right idea was number | Found at situation | Partly-right ideas kept | Wrong ideas kept | Guess miss (median) | Calibration |
|---|---|---|---|---|---|---|---|
| humble | 74% | 4.30 | 5.62 | 0.20 | 0.00 | 0.425 | 0.220 |
| taught | 80% | 4.61 | 5.25 | 0.16 | 0.00 | 0.428 | 0.256 |
| credit_only | 74% | 4.33 | 5.62 | 0.20 | 0.00 | 0.415 | 0.265 |
| self_taught | 75% | 5.03 | 5.74 | 0.22 | 0.00 | 0.446 | 0.270 |
| untaught | 75% | 6.42 | 6.60 | 0.17 | 0.02 | 0.591 | 0.154 |

## Final exam: the 8 kinds of force it practised

| Learner | Found the force | Right idea was number | Found at situation | Partly-right ideas kept | Wrong ideas kept | Guess miss (median) | Calibration |
|---|---|---|---|---|---|---|---|
| humble | 78% | 4.03 | 5.22 | 0.18 | 0.01 | 0.425 | 0.209 |
| taught | 84% | 4.21 | 4.79 | 0.13 | 0.00 | 0.428 | 0.231 |
| credit_only | 78% | 4.06 | 5.16 | 0.17 | 0.00 | 0.415 | 0.234 |
| self_taught | 78% | 4.64 | 5.30 | 0.21 | 0.00 | 0.446 | 0.243 |
| untaught | 71% | 6.59 | 6.79 | 0.20 | 0.02 | 0.591 | 0.153 |

## Final exam: the 4 worlds with forces it was never shown

| Learner | Found the force | Right idea was number | Found at situation | Partly-right ideas kept | Wrong ideas kept | Guess miss (median) | Calibration |
|---|---|---|---|---|---|---|---|
| humble | 68% | 4.86 | 6.40 | 0.23 | 0.00 | 0.563 | 0.241 |
| taught | 72% | 5.41 | 6.17 | 0.21 | 0.01 | 0.528 | 0.306 |
| credit_only | 65% | 4.88 | 6.54 | 0.25 | 0.00 | 0.514 | 0.327 |
| self_taught | 70% | 5.81 | 6.61 | 0.25 | 0.01 | 0.571 | 0.323 |
| untaught | 82% | 6.06 | 6.22 | 0.11 | 0.03 | 0.643 | 0.154 |

## Doubt: how sure it was about the ideas it kept (exam)

| Learner | Kept after one check (sure) | ...of those, right | Kept after two checks (unsure) | ...of those, right |
|---|---|---|---|---|
| humble | 65 | 74% | 161 | 81% |
| taught | 87 | 80% | 145 | 85% |
| credit_only | 73 | 73% | 151 | 82% |
| self_taught | 101 | 67% | 133 | 84% |
| untaught | 12 | 100% | 213 | 78% |

## Per force in the exam: found the force

| Learner | rubbing | water drag | dry friction | spring | tight spring | stiff spring | swing | slope | thick oil | valley |
|---|---|---|---|---|---|---|---|---|---|---|
| humble | 65% | 80% | 95% | 75% | 90% | 85% | 35% | 95% | 50% | 85% |
| taught | 85% | 100% | 100% | 85% | 90% | 90% | 30% | 95% | 55% | 90% |
| credit_only | 55% | 85% | 95% | 60% | 90% | 95% | 55% | 90% | 48% | 82% |
| self_taught | 60% | 70% | 100% | 60% | 95% | 95% | 45% | 95% | 52% | 88% |
| untaught | 50% | 70% | 90% | 50% | 80% | 85% | 50% | 90% | 72% | 92% |
