# The ball-throw world

Seeds [21, 22, 23, 24, 25, 26, 27, 28, 29, 30]. Numbers are averages over lives ± one standard error. Misses are in centimetres: the typical distance between where it guessed the ball would be and where it was, over a 2-second throw.

## Predicting throws

| Robot | New throws of balls it has seen in that place | Balls in a place it never saw them in | Throw to a target, seen ball | Throw to a target, ball never thrown in air |
|---|---|---|---|---|
| concept | 1.4 ± 0.0 | 1.6 ± 0.1 | 0.7 ± 0.1 | 0.5 ± 0.2 |
| per_place | 1.4 ± 0.0 | 72.7 ± 13.9 | 0.7 ± 0.1 | 7.7 ± 2.1 |
| baseline | 4.8 ± 0.4 | 56.1 ± 9.5 | 2.1 ± 0.5 | 7.4 ± 1.8 |

Balls in a place it never saw them in, by place:

| Robot | vacuum | air | windy | water |
|---|---|---|---|---|
| concept | 1.2 ± 0.4 | 1.4 ± 0.5 | 1.7 ± 0.3 | 1.9 ± 0.4 |
| per_place | 0.6 ± 0.1 | 32.3 ± 6.2 | 44.6 ± 9.6 | 213.2 ± 51.9 |
| baseline | 11.3 ± 2.6 | 24.4 ± 6.6 | 13.4 ± 3.0 | 175.1 ± 40.8 |

## The moon (never shown until the exam)

| Robot | Surprise on the first moon throw (noise units; 1.8 is surprising) | Miss for a ball never thrown on the moon, after 1 moon throw | after 2 | after 4 |
|---|---|---|---|---|
| concept | 6.0 ± 0.0 | 1.3 ± 0.3 | 1.0 ± 0.2 | 0.7 ± 0.2 |
| per_place | 6.0 ± 0.0 | 1.3 ± 0.3 | 1.0 ± 0.2 | 0.7 ± 0.2 |
| baseline | - | 412.0 ± 81.8 | 393.1 ± 45.7 | 319.0 ± 57.0 |

## Laws of each place (the concept robot; the per-place robot finds the same)

| Place | Kept the true law | Sure | Sure, and the claim is true (its wind range included) | Throws of its own | Width of the wind range it states (m/s) |
|---|---|---|---|---|---|
| vacuum | 100% (10) | 100% (10) | 100% (10) | 0.0 ± 0.0 | - |
| air | 100% (10) | 100% (10) | 100% (10) | 0.0 ± 0.0 | 1.68 ± 0.13 |
| windy | 100% (10) | 70% (10) | 100% (7) | 0.7 ± 0.3 | 1.28 ± 0.07 |
| water | 100% (10) | 100% (10) | 100% (10) | 0.0 ± 0.0 | 0.70 ± 0.05 |
| moon | 100% (10) | 100% (10) | 100% (10) | 0.0 ± 0.0 | - |

Sure and wrong, both loop robots, every place: 0 of 94 sure claims. Not sure (concept robot): 3 of 50 place-lives (seed 21 windy, seed 27 windy, seed 30 windy).

## Galileo in the vacuum room

- It said every ball falls the same, heavy or light: 100% (10).
- Evidence for one shared pull over a pull per ball: 0.1 ± 0.0 (−9 or less would mean mass matters).
- Spread of the pull it measured across balls: 0.014 ± 0.001 m/s²; correlation of that pull with the push number: -0.10 ± 0.15.
- Throws per ball behind the comparison: at least 2; largest difference between the two models' numbers: 0.037 ± 0.002.

## The concept: one hidden number per ball

- It kept the concept in 100% (10) of lives. It predicted new (ball, place) pairs with: R0 in 0, Rs in 0, R1 in 10, R2 in 0 lives (R0 no sharing, Rs size only, R1 one hidden number, R2 two).
- Evidence (9 is decisive), predicting each ball in each place from all the others: over 'no sharing' 98.4 ± 3.2; over 'size only' 89.8 ± 4.2; a second hidden number over the concept -20.6 ± 3.5.
- The push number ranks the balls' true masses (rank correlation): 1.00 ± 0.00.

| Place / term | Where the number clearly depends on the ball | Power of size it chose there | True power |
|---|---|---|---|
| air/down | 0 of 10 lives | - | none (same for every ball) |
| air/drag2 | 10 of 10 lives | 2: 10 | 2 |
| vacuum/down | 0 of 10 lives | - | none (same for every ball) |
| water/down | 10 of 10 lives | 3: 10 | 3 |
| water/drag2 | 10 of 10 lives | 2: 10 | 2 |
| windy/down | 0 of 10 lives | - | none (same for every ball) |
| windy/drag2 | 10 of 10 lives | 2: 10 | 2 |

## Naming

The caretaker said "heavy" or "light" for half the balls. For the other half, from their push numbers, it named 22 of 40 right and 0 wrong, and said "not sure" for 18: those balls lay between the heaviest ball called light and the lightest ball called heavy.

## What it says (concept robot, seed 21)

- In the vacuum: pulled down by 9.807, the same for every ball. Every ball falls the same, heavy or light. I am sure: every other idea I tried fits worse, and no bigger idea predicts new throws better.
- In the air: pulled down by 9.793, the same for every ball; slowed by |v|·v times 0.050·size²/mass; the air seems still (any flow lies between -0.6 and +0.6 m/s). I am sure: every other idea I tried fits worse, and no bigger idea predicts new throws better.
- In the windy: pulled down by 9.787, the same for every ball; slowed by |v|·v times 0.051·size²/mass; the air moves sideways at -0.6 m/s (somewhere from -1.2 to -0.2). I am not sure: a steady pull down + a steady push sideways + drag in step with speed + drag with speed squared, a steady pull down + a steady push sideways + drag with speed squared fits as well.
- In the water: pulled down by 9.790 − 9.867·size³/mass; slowed by |v|·v times 0.303·size²/mass; the water seems still (any flow lies between -0.4 and +0.2 m/s). I am sure: every other idea I tried fits worse, and no bigger idea predicts new throws better.
- In the moon: pulled down by 1.606. I am sure: every other idea I tried fits worse, and no bigger idea predicts new throws better.
- One hidden number per ball, how hard it is to push (its mass), explains how every place treats it. I am sure: it predicted each ball in each place from the others better than 'no sharing' (evidence 102) and 'size only' (88), and a second hidden number did not help (-3; 9 is decisive).
