# The ball-throw world

Seeds [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]. Numbers are averages over lives ± one standard error. Misses are in centimetres: the typical distance between where it guessed the ball would be and where it was, over a 2-second throw.

## Predicting throws

| Robot | New throws of balls it has seen in that place | Balls in a place it never saw them in | Throw to a target, seen ball | Throw to a target, ball never thrown in air |
|---|---|---|---|---|
| concept | 1.2 ± 0.1 | 1.5 ± 0.2 | 0.5 ± 0.1 | 0.7 ± 0.2 |
| per_place | 1.2 ± 0.1 | 87.2 ± 11.2 | 0.5 ± 0.1 | 11.8 ± 3.3 |
| baseline | 5.9 ± 0.9 | 70.0 ± 10.4 | 1.4 ± 0.3 | 7.3 ± 1.7 |

Balls in a place it never saw them in, by place:

| Robot | vacuum | air | windy | water |
|---|---|---|---|---|
| concept | 1.1 ± 0.3 | 1.4 ± 0.4 | 1.3 ± 0.1 | 2.3 ± 0.4 |
| per_place | 0.7 ± 0.1 | 40.0 ± 4.7 | 28.5 ± 4.7 | 279.7 ± 41.2 |
| baseline | 16.3 ± 6.0 | 18.7 ± 3.0 | 18.6 ± 3.1 | 226.3 ± 37.3 |

## The moon (never shown until the exam)

| Robot | Surprise on the first moon throw (noise units; 1.8 is surprising) | Miss for a ball never thrown on the moon, after 1 moon throw | after 2 | after 4 |
|---|---|---|---|---|
| concept | 6.0 ± 0.0 | 1.5 ± 0.3 | 1.2 ± 0.3 | 0.7 ± 0.2 |
| per_place | 6.0 ± 0.0 | 1.5 ± 0.3 | 1.2 ± 0.3 | 0.7 ± 0.2 |
| baseline | - | 511.0 ± 72.1 | 331.8 ± 80.3 | 294.4 ± 85.8 |

## Laws of each place (the concept robot; the per-place robot finds the same)

| Place | Kept the true law | Sure | Sure and right | Throws of its own |
|---|---|---|---|---|
| vacuum | 100% (10) | 100% (10) | 100% (10) | 0.0 ± 0.0 |
| air | 100% (10) | 100% (10) | 100% (10) | 0.0 ± 0.0 |
| windy | 100% (10) | 100% (10) | 100% (10) | 0.3 ± 0.2 |
| water | 100% (10) | 100% (10) | 100% (10) | 0.0 ± 0.0 |
| moon | 100% (10) | 100% (10) | 100% (10) | 0.0 ± 0.0 |

## Galileo in the vacuum room

- It said every ball falls the same, heavy or light: 100% (10).
- Evidence for one shared pull over a pull per ball: 0.2 ± 0.1 (−9 or less would mean mass matters).
- Spread of the pull it measured across balls: 0.012 ± 0.001 m/s²; correlation of that pull with the push number: -0.15 ± 0.11.
- Throws per ball behind the comparison: at least 2; largest difference between the two models' numbers: 0.039 ± 0.004.

## The concept: one hidden number per ball

- It kept the concept in 100% (10) of lives. It predicted new (ball, place) pairs with: R0 in 0, Rs in 0, R1 in 10, R2 in 0 lives (R0 no sharing, Rs size only, R1 one hidden number, R2 two).
- Evidence (9 is decisive), predicting each ball in each place from all the others: over 'no sharing' 102.6 ± 1.5; over 'size only' 92.6 ± 2.9; a second hidden number over the concept -14.2 ± 2.9.
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

The caretaker said "heavy" or "light" for half the balls. For the other half, from their push numbers, it named 28 of 40 right and 0 wrong, and said "not sure" for 12: those balls lay between the heaviest ball called light and the lightest ball called heavy.

## What it says (concept robot, seed 1)

- In the vacuum: pulled down by 9.785, the same for every ball. Every ball falls the same, heavy or light. I am sure: every other idea I tried fits worse or adds nothing.
- In the air: pulled down by 9.824, the same for every ball; slowed by |v|·v times 0.050·size²/mass. I am sure: every other idea I tried fits worse or adds nothing.
- In the windy: pulled down by 9.780, the same for every ball; slowed by |v|·v times 0.050·size²/mass; the air moves sideways at -1.0 m/s. I am sure: every other idea I tried fits worse or adds nothing.
- In the water: pulled down by 9.809 − 9.818·size³/mass; slowed by |v|·v times 0.301·size²/mass. I am sure: every other idea I tried fits worse or adds nothing.
- In the moon: pulled down by 1.614. I am sure: every other idea I tried fits worse or adds nothing.
- One hidden number per ball, how hard it is to push (its mass), explains how every place treats it. I am sure: it predicted each ball in each place from the others better than 'no sharing' (evidence 106) and 'size only' (103), and a second hidden number did not help (1; 9 is decisive).
