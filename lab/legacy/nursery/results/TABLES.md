# ccops5 lab results

Lives: seeds [1, 2, 3]. Each number is the average over seeds of that life's median, with the lowest and highest seed in brackets.
A miss of 0 is a perfect guess of where the thing goes; 1 is as bad as guessing it never moves.

## The connected learner, stage by stage

| Stage | Guess before touching | Guess after its own pushes | Pushes used | Situations that checked out |
|---|---|---|---|---|
| 0 own hand | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 2.00 (2.00 to 2.00) | 0.33 (0.33 to 0.33) |
| 1 toys on ice | 0.005 (0.004 to 0.005) | 0.004 (0.004 to 0.005) | 2.00 (2.00 to 2.00) | 0.94 (0.92 to 1.00) |
| 2 toys on carpet | 0.006 (0.004 to 0.008) | 0.006 (0.005 to 0.008) | 2.00 (2.00 to 2.00) | 0.79 (0.76 to 0.83) |
| 3 toys in water | 0.015 (0.006 to 0.025) | 0.007 (0.005 to 0.010) | 2.00 (2.00 to 2.00) | 0.75 (0.74 to 0.79) |
| 4 springs | 0.178 (0.086 to 0.227) | 0.012 (0.008 to 0.016) | 2.06 (2.00 to 2.12) | 0.67 (0.67 to 0.67) |
| 5 swings | 0.023 (0.015 to 0.039) | 0.021 (0.014 to 0.030) | 2.04 (2.00 to 2.08) | 0.96 (0.96 to 0.96) |
| 6 new toys, words only | 0.141 (0.076 to 0.189) | 0.005 (0.005 to 0.005) | 2.02 (2.00 to 2.06) | 1.00 (1.00 to 1.00) |
| 7 stuck together | 0.007 (0.006 to 0.008) | 0.009 (0.006 to 0.012) | 2.50 (2.25 to 2.69) | 1.00 (1.00 to 1.00) |
| 8 final check | 0.004 (0.003 to 0.005) | 0.004 (0.003 to 0.005) | 2.00 (2.00 to 2.00) | 1.00 (1.00 to 1.00) |

## What it discovered by itself

Depends on: the inputs the learner chose for the law. Most like: which hidden shape the new part of the law resembles (correlation), judged only for this report.

| Seed | Law | Kept during | Situations of that stage before keeping it | Depends on | Most like |
|---|---|---|---|---|---|
| 1 | law 1 | 0 own hand | 8 | push | push command (the hand) (1.000) |
| 1 | law 2 | 2 toys on carpet | 7 | speed | speed (rubbing) (1.000) |
| 1 | law 3 | 3 toys in water | 8 | speed | speed squared (water drag) (0.999) |
| 1 | law 4 | 4 springs | 8 | position, push | position (spring) (1.000) |
| 2 | law 1 | 0 own hand | 8 | speed, push | push command (the hand) (1.000) |
| 2 | law 2 | 2 toys on carpet | 8 | speed | speed (rubbing) (1.000) |
| 2 | law 3 | 3 toys in water | 9 | speed | speed squared (water drag) (0.999) |
| 2 | law 4 | 4 springs | 8 | position | position (spring) (1.000) |
| 3 | law 1 | 0 own hand | 8 | push | push command (the hand) (1.000) |
| 3 | law 2 | 2 toys on carpet | 8 | speed | speed (rubbing) (1.000) |
| 3 | law 3 | 3 toys in water | 11 | speed | speed squared (water drag) (0.996) |
| 3 | law 4 | 4 springs | 8 | position | position (spring) (1.000) |

Law proposals in all: 4.0 (4.0 to 4.0); rejected by the check: 0.0 (0.0 to 0.0).

## Switching one connection off at a time

| Learner | What changed | Stages 1-5, guess before touching | Stages 1-5, after pushes | Final check, before touching | New toys from words | Stuck triples, before touching | Laws kept |
|---|---|---|---|---|---|---|---|
| full | everything connected | 0.011 (0.009 to 0.014) | 0.008 (0.007 to 0.009) | 0.004 (0.003 to 0.005) | 0.141 (0.076 to 0.189) | 0.007 (0.006 to 0.008) | 4.0 (4.0 to 4.0) |
| forget_kinds | keeps laws, forgets objects, words and places after each situation (like CORE-022) | 1.000 (1.000 to 1.000) | 0.007 (0.005 to 0.007) | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 4.0 (4.0 to 4.0) |
| reset_all | whole library wiped after every situation | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.0 (0.0 to 0.0) |
| ungated | keeps everything without checking it first | 0.012 (0.009 to 0.014) | 0.008 (0.007 to 0.010) | 0.004 (0.004 to 0.005) | 0.138 (0.063 to 0.176) | 0.006 (0.005 to 0.008) | 4.0 (4.0 to 4.0) |
| passive | same push every time (never throws again differently) | 0.013 (0.009 to 0.016) | 0.009 (0.007 to 0.012) | 0.004 (0.003 to 0.005) | 0.139 (0.076 to 0.189) | 0.007 (0.006 to 0.008) | 4.0 (4.0 to 4.0) |
| frozen_laws | learns its hand, then may not grow new laws | 1.000 (1.000 to 1.000) | 0.451 (0.320 to 0.641) | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.007 (0.006 to 0.008) | 1.0 (1.0 to 1.0) |
| no_reuse | a law may only be used where it was found | 0.010 (0.008 to 0.012) | 0.008 (0.007 to 0.010) | 0.004 (0.003 to 0.005) | 0.136 (0.068 to 0.189) | 0.007 (0.006 to 0.008) | 5.0 (5.0 to 5.0) |
| baseline | ordinary neural network: knowledge only in its weights | 0.267 (0.234 to 0.315) | 0.031 (0.027 to 0.039) | 0.386 (0.262 to 0.502) | 0.418 (0.338 to 0.569) | 0.252 (0.155 to 0.414) | 0.0 (0.0 to 0.0) |
| baseline_parts | ordinary neural network, also shown the parts of glued things (added up) | 0.225 (0.198 to 0.261) | 0.036 (0.030 to 0.046) | 0.411 (0.390 to 0.434) | 0.460 (0.414 to 0.539) | 0.343 (0.233 to 0.495) | 0.0 (0.0 to 0.0) |
| baseline_sets | ordinary neural network that reads each part of a glued thing, then adds (deep sets) | 0.247 (0.232 to 0.271) | 0.035 (0.028 to 0.045) | 0.426 (0.386 to 0.458) | 0.376 (0.341 to 0.408) | 0.282 (0.145 to 0.521) | 0.0 (0.0 to 0.0) |
| baseline_words | ordinary neural network, not shown the look of brand-new toys (words only) | 0.267 (0.234 to 0.315) | 0.031 (0.027 to 0.039) | 0.433 (0.417 to 0.457) | 0.328 (0.285 to 0.409) | 0.256 (0.195 to 0.351) | 0.0 (0.0 to 0.0) |

## Words it was never told the meaning of

| New toy, never touched before | Miss |
|---|---|
| Guess from the place alone | 0.222 (0.184 to 0.247) |
| Guess from the caretaker's words | 0.141 (0.076 to 0.189) |
| Ordinary network, given the same words | 0.418 (0.338 to 0.569) |

## Math and proof: toys stuck together

Every rule it imagined, judged against what really happened to stuck toys:

| Rule it imagined | Miss when used to guess stuck toys |
|---|---|
| same as one part | 1.622 (1.490 to 1.864) |
| average of the parts | 1.778 (1.575 to 1.983) |
| parts added up | 6.037 (5.663 to 6.376) |
| parts multiplied | 0.822 (0.192 to 1.378) |
| one-overs added up | 0.006 (0.005 to 0.008) |
| largest part | 2.462 (1.957 to 2.929) |
| smallest part | 1.022 (0.877 to 1.156) |

| Learner | Rule it kept | Stuck situations it needed | Pairs, before touching | Triples (never seen), before touching |
|---|---|---|---|---|
| full | one-overs added up | 3.0 (3.0 to 3.0) | 0.007 (0.006 to 0.010) | 0.007 (0.006 to 0.008) |
| forget_kinds | None | - | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) |
| reset_all | None | - | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) |
| ungated | one-overs added up | 1.0 (1.0 to 1.0) | 0.006 (0.005 to 0.008) | 0.006 (0.005 to 0.008) |
| passive | one-overs added up | 3.0 (3.0 to 3.0) | 0.007 (0.006 to 0.010) | 0.007 (0.006 to 0.008) |
| frozen_laws | one-overs added up | 3.0 (3.0 to 3.0) | 0.007 (0.006 to 0.010) | 0.007 (0.006 to 0.008) |
| no_reuse | one-overs added up | 3.0 (3.0 to 3.0) | 0.007 (0.006 to 0.010) | 0.007 (0.006 to 0.008) |
| baseline | None | - | 0.305 (0.211 to 0.448) | 0.252 (0.155 to 0.414) |
| baseline_parts | None | - | 0.350 (0.192 to 0.624) | 0.343 (0.233 to 0.495) |
| baseline_sets | None | - | 0.228 (0.148 to 0.294) | 0.282 (0.145 to 0.521) |
| baseline_words | None | - | 0.148 (0.118 to 0.172) | 0.256 (0.195 to 0.351) |

Full learner, stuck toys: guess from the place average 1.509 (1.254 to 1.679), worked out from its parts 0.006 (0.005 to 0.008).

## Springs and swings: one law, two looks

| Learner | New laws proposed during swings | Swings, after pushes | Spring law strength inside swings (coefficient / uncertainty) |
|---|---|---|---|
| full | 0.0 (0.0 to 0.0) | 0.021 (0.014 to 0.030) | 279.9 (264.5 to 303.0) |
| no_reuse | 1.0 (1.0 to 1.0) | 0.017 (0.015 to 0.020) | 0.0 (0.0 to 0.0) |

## Contradictions: someone secretly bumps the toy

| Learner | Bumped situations | Bumped situations stored as knowledge | Memories corrected | Final check on bumped toys, before touching |
|---|---|---|---|---|
| full | 7.3 (6.0 to 10.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.006 (0.004 to 0.009) |
| ungated | 7.3 (6.0 to 10.0) | 7.3 (6.0 to 10.0) | 0.0 (0.0 to 0.0) | 0.010 (0.009 to 0.012) |
