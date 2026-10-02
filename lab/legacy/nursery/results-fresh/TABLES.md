# ccops5 lab results

Lives: seeds [4, 5, 6]. Each number is the average over seeds of that life's median, with the lowest and highest seed in brackets.
A miss of 0 is a perfect guess of where the thing goes; 1 is as bad as guessing it never moves.

## The connected learner, stage by stage

| Stage | Guess before touching | Guess after its own pushes | Pushes used | Situations that checked out |
|---|---|---|---|---|
| 0 own hand | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 2.00 (2.00 to 2.00) | 0.33 (0.33 to 0.33) |
| 1 toys on ice | 0.018 (0.005 to 0.040) | 0.018 (0.009 to 0.031) | 2.00 (2.00 to 2.00) | 0.94 (0.89 to 0.97) |
| 2 toys on carpet | 0.027 (0.011 to 0.054) | 0.019 (0.013 to 0.023) | 2.00 (2.00 to 2.00) | 0.78 (0.74 to 0.81) |
| 3 toys in water | 0.027 (0.017 to 0.040) | 0.024 (0.011 to 0.047) | 2.01 (2.00 to 2.02) | 0.76 (0.71 to 0.81) |
| 4 springs | 0.273 (0.175 to 0.395) | 0.029 (0.018 to 0.045) | 2.04 (2.00 to 2.08) | 0.64 (0.58 to 0.67) |
| 5 swings | 0.032 (0.015 to 0.050) | 0.041 (0.016 to 0.077) | 2.03 (2.00 to 2.08) | 0.90 (0.79 to 1.00) |
| 6 new toys, words only | 0.106 (0.078 to 0.148) | 0.012 (0.006 to 0.018) | 2.02 (2.00 to 2.06) | 0.98 (0.94 to 1.00) |
| 7 stuck together | 0.012 (0.006 to 0.020) | 0.016 (0.011 to 0.023) | 2.44 (2.31 to 2.56) | 1.00 (1.00 to 1.00) |
| 8 final check | 0.010 (0.005 to 0.013) | 0.010 (0.007 to 0.013) | 2.00 (2.00 to 2.00) | 1.00 (1.00 to 1.00) |

## What it discovered by itself

Depends on: the inputs the learner chose for the law. Most like: which hidden shape the new part of the law resembles (correlation), judged only for this report.

| Seed | Law | Kept during | Situations of that stage before keeping it | Depends on | Most like |
|---|---|---|---|---|---|
| 4 | law 1 | 0 own hand | 8 | push | push command (the hand) (1.000) |
| 4 | law 2 | 2 toys on carpet | 8 | speed | speed (rubbing) (1.000) |
| 4 | law 3 | 3 toys in water | 13 | speed | speed squared (water drag) (0.993) |
| 4 | law 4 | 4 springs | 8 | position, push | position (spring) (1.000) |
| 5 | law 1 | 0 own hand | 8 | speed, push | push command (the hand) (1.000) |
| 5 | law 2 | 2 toys on carpet | 7 | speed | speed (rubbing) (1.000) |
| 5 | law 3 | 3 toys in water | 15 | speed | speed squared (water drag) (0.999) |
| 5 | law 4 | 4 springs | 8 | position, push | position (spring) (1.000) |
| 6 | law 1 | 0 own hand | 8 | push | push command (the hand) (1.000) |
| 6 | law 2 | 2 toys on carpet | 8 | speed | speed (rubbing) (1.000) |
| 6 | law 3 | 3 toys in water | 14 | speed | speed squared (water drag) (1.000) |
| 6 | law 4 | 4 springs | 8 | position | position (spring) (1.000) |

Law proposals in all: 4.0 (4.0 to 4.0); rejected by the check: 0.0 (0.0 to 0.0).

## Switching one connection off at a time

| Learner | What changed | Stages 1-5, guess before touching | Stages 1-5, after pushes | Final check, before touching | New toys from words | Stuck triples, before touching | Laws kept |
|---|---|---|---|---|---|---|---|
| full | everything connected | 0.028 (0.015 to 0.044) | 0.023 (0.016 to 0.034) | 0.010 (0.005 to 0.013) | 0.106 (0.078 to 0.148) | 0.011 (0.006 to 0.017) | 4.0 (4.0 to 4.0) |
| forget_kinds | keeps laws, forgets objects, words and places after each situation (like CORE-022) | 1.000 (1.000 to 1.000) | 0.015 (0.012 to 0.020) | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 4.0 (4.0 to 4.0) |
| reset_all | whole library wiped after every situation | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) | 0.0 (0.0 to 0.0) |
| ungated | keeps everything without checking it first | 0.017 (0.013 to 0.025) | 0.018 (0.012 to 0.028) | 0.011 (0.005 to 0.022) | 0.105 (0.084 to 0.144) | 0.012 (0.006 to 0.020) | 4.0 (4.0 to 4.0) |
| passive | same push every time (never throws again differently) | 0.025 (0.015 to 0.037) | 0.014 (0.009 to 0.022) | 0.011 (0.005 to 0.022) | 0.120 (0.096 to 0.154) | 0.019 (0.006 to 0.042) | 4.0 (4.0 to 4.0) |
| frozen_laws | learns its hand, then may not grow new laws | 1.000 (1.000 to 1.000) | 0.446 (0.327 to 0.536) | 0.713 (0.140 to 1.000) | 1.000 (1.000 to 1.000) | 0.011 (0.006 to 0.018) | 1.0 (1.0 to 1.0) |
| no_reuse | a law may only be used where it was found | 0.022 (0.013 to 0.035) | 0.017 (0.013 to 0.021) | 0.011 (0.007 to 0.013) | 0.108 (0.083 to 0.149) | 0.011 (0.006 to 0.017) | 5.0 (5.0 to 5.0) |
| baseline | ordinary neural network: knowledge only in its weights | 0.246 (0.165 to 0.325) | 0.036 (0.019 to 0.045) | 0.428 (0.257 to 0.599) | 0.410 (0.314 to 0.478) | 0.216 (0.154 to 0.255) | 0.0 (0.0 to 0.0) |
| baseline_parts | ordinary neural network, also shown the parts of glued things (added up) | 0.239 (0.158 to 0.296) | 0.034 (0.018 to 0.043) | 0.478 (0.330 to 0.599) | 0.395 (0.268 to 0.504) | 0.466 (0.257 to 0.822) | 0.0 (0.0 to 0.0) |
| baseline_sets | ordinary neural network that reads each part of a glued thing, then adds (deep sets) | 0.255 (0.157 to 0.322) | 0.032 (0.020 to 0.042) | 0.419 (0.353 to 0.511) | 0.383 (0.310 to 0.445) | 0.259 (0.139 to 0.416) | 0.0 (0.0 to 0.0) |
| baseline_words | ordinary neural network, not shown the look of brand-new toys (words only) | 0.246 (0.165 to 0.325) | 0.036 (0.019 to 0.045) | 0.343 (0.239 to 0.420) | 0.396 (0.217 to 0.523) | 0.220 (0.137 to 0.280) | 0.0 (0.0 to 0.0) |

## Words it was never told the meaning of

| New toy, never touched before | Miss |
|---|---|
| Guess from the place alone | 0.231 (0.193 to 0.270) |
| Guess from the caretaker's words | 0.106 (0.078 to 0.148) |
| Ordinary network, given the same words | 0.410 (0.314 to 0.478) |

## Math and proof: toys stuck together

Every rule it imagined, judged against what really happened to stuck toys:

| Rule it imagined | Miss when used to guess stuck toys |
|---|---|
| same as one part | 1.643 (1.445 to 1.825) |
| average of the parts | 1.733 (1.505 to 1.859) |
| parts added up | 5.986 (5.449 to 6.353) |
| parts multiplied | 1.346 (0.178 to 2.178) |
| one-overs added up | 0.010 (0.006 to 0.016) |
| largest part | 2.536 (1.924 to 2.860) |
| smallest part | 1.029 (0.881 to 1.213) |

| Learner | Rule it kept | Stuck situations it needed | Pairs, before touching | Triples (never seen), before touching |
|---|---|---|---|---|
| full | one-overs added up | 3.0 (3.0 to 3.0) | 0.023 (0.007 to 0.048) | 0.011 (0.006 to 0.017) |
| forget_kinds | None | - | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) |
| reset_all | None | - | 1.000 (1.000 to 1.000) | 1.000 (1.000 to 1.000) |
| ungated | one-overs added up | 1.0 (1.0 to 1.0) | 0.012 (0.007 to 0.022) | 0.012 (0.006 to 0.020) |
| passive | one-overs added up | 3.0 (3.0 to 3.0) | 0.023 (0.006 to 0.051) | 0.019 (0.006 to 0.042) |
| frozen_laws | one-overs added up | 3.0 (3.0 to 3.0) | 0.023 (0.007 to 0.048) | 0.011 (0.006 to 0.018) |
| no_reuse | one-overs added up | 3.0 (3.0 to 3.0) | 0.023 (0.007 to 0.048) | 0.011 (0.006 to 0.017) |
| baseline | None | - | 0.432 (0.343 to 0.534) | 0.216 (0.154 to 0.255) |
| baseline_parts | None | - | 0.488 (0.449 to 0.562) | 0.466 (0.257 to 0.822) |
| baseline_sets | None | - | 0.304 (0.160 to 0.396) | 0.259 (0.139 to 0.416) |
| baseline_words | None | - | 0.494 (0.390 to 0.624) | 0.220 (0.137 to 0.280) |

Full learner, stuck toys: guess from the place average 1.434 (1.269 to 1.542), worked out from its parts 0.010 (0.006 to 0.017).

## Springs and swings: one law, two looks

| Learner | New laws proposed during swings | Swings, after pushes | Spring law strength inside swings (coefficient / uncertainty) |
|---|---|---|---|
| full | 0.0 (0.0 to 0.0) | 0.041 (0.016 to 0.077) | 360.6 (351.2 to 372.5) |
| no_reuse | 1.0 (1.0 to 1.0) | 0.023 (0.018 to 0.030) | 0.0 (0.0 to 0.0) |

## Contradictions: someone secretly bumps the toy

| Learner | Bumped situations | Bumped situations stored as knowledge | Memories corrected | Final check on bumped toys, before touching |
|---|---|---|---|---|
| full | 7.7 (2.0 to 11.0) | 0.0 (0.0 to 0.0) | 0.0 (0.0 to 0.0) | 0.011 (0.004 to 0.014) |
| ungated | 7.7 (2.0 to 11.0) | 7.7 (2.0 to 11.0) | 0.0 (0.0 to 0.0) | 0.015 (0.007 to 0.021) |
