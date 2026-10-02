# The ball-throw world

Seeds [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]. Numbers are averages over lives ± one standard error. Misses are in centimetres: the typical distance between where it guessed the ball would be and where it was, over a 2-second throw.

## Predicting throws

| Robot | New throws of balls it has seen in that place | Balls in a place it never saw them in | Throw to a target, seen ball | Throw to a target, ball never thrown in air |
|---|---|---|---|---|
| concept | 1.7 ± 0.2 | 1.9 ± 0.3 | 0.6 ± 0.1 | 0.5 ± 0.1 |
| per_place | 1.7 ± 0.2 | 84.1 ± 14.1 | 0.6 ± 0.1 | 9.7 ± 3.1 |
| baseline | 6.1 ± 0.8 | 58.1 ± 9.1 | 1.3 ± 0.2 | 3.6 ± 1.1 |

Balls in a place it never saw them in, by place:

| Robot | vacuum | air | windy | water |
|---|---|---|---|---|
| concept | 0.6 ± 0.1 | 1.6 ± 0.5 | 2.6 ± 0.6 | 2.7 ± 0.5 |
| per_place | 0.6 ± 0.1 | 29.2 ± 2.9 | 28.8 ± 6.9 | 277.6 ± 51.6 |
| baseline | 12.0 ± 2.3 | 14.0 ± 2.6 | 15.9 ± 2.8 | 190.5 ± 34.2 |

## The moon (never shown until the exam)

| Robot | Surprise on the first moon throw (noise units; 1.8 is surprising) | Miss for a ball never thrown on the moon, after 1 moon throw | after 2 | after 4 |
|---|---|---|---|---|
| concept | 6.0 ± 0.0 | 1.5 ± 0.3 | 0.8 ± 0.1 | 0.5 ± 0.1 |
| per_place | 6.0 ± 0.0 | 1.5 ± 0.3 | 0.8 ± 0.1 | 0.5 ± 0.1 |
| baseline | - | 453.3 ± 68.1 | 280.1 ± 56.9 | 213.2 ± 53.6 |

## Laws of each place (the concept robot; the per-place robot finds the same)

| Place | Kept the true law | Sure | Sure and right | Throws of its own |
|---|---|---|---|---|
| vacuum | 100% (10) | 100% (10) | 100% (10) | 0.0 ± 0.0 |
| air | 100% (10) | 100% (10) | 100% (10) | 0.0 ± 0.0 |
| windy | 80% (10) | 100% (10) | 80% (10) | 0.0 ± 0.0 |
| water | 100% (10) | 100% (10) | 100% (10) | 0.0 ± 0.0 |
| moon | 100% (10) | 100% (10) | 100% (10) | 0.0 ± 0.0 |

## Galileo in the vacuum room

- It said every ball falls the same, heavy or light: 100% (10).
- Evidence for one shared pull over a pull per ball: 0.1 ± 0.0 (−9 or less would mean mass matters).
- Spread of the pull it measured across balls: 0.012 ± 0.001 m/s²; correlation of that pull with the push number: -0.15 ± 0.11.
- Throws per ball behind the comparison: at least 2; largest difference between the two models' numbers: 0.034 ± 0.003.

## The concept: one hidden number per ball

- It kept the concept in 100% (10) of lives. It predicted new (ball, place) pairs with: R0 in 0, Rs in 0, R1 in 10, R2 in 0 lives (R0 no sharing, Rs size only, R1 one hidden number, R2 two).
- Evidence (9 is decisive), predicting each ball in each place from all the others: over 'no sharing' 97.6 ± 2.3; over 'size only' 94.5 ± 4.0; a second hidden number over the concept -19.9 ± 2.5.
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

The caretaker said "heavy" or "light" for half the balls. For the other half, from their push numbers, it named 29 of 40 right and 0 wrong, and said "not sure" for 11: those balls lay between the heaviest ball called light and the lightest ball called heavy.

## What it says (concept robot, seed 11)

- In the vacuum: pulled down by 9.802, the same for every ball. Every ball falls the same, heavy or light. I am sure: every other idea I tried fits worse or adds nothing.
- In the air: pulled down by 9.803, the same for every ball; slowed by |v|·v times 0.050·size²/mass. I am sure: every other idea I tried fits worse or adds nothing.
- In the windy: pulled down by 9.865, the same for every ball; slowed by |v|·v times 0.051·size²/mass; the air moves sideways at -2.0 m/s. I am sure: every other idea I tried fits worse or adds nothing.
- In the water: pulled down by 9.774 − 9.678·size³/mass; slowed by |v|·v times 0.299·size²/mass. I am sure: every other idea I tried fits worse or adds nothing.
- In the moon: pulled down by 1.626. I am sure: every other idea I tried fits worse or adds nothing.
- One hidden number per ball, how hard it is to push (its mass), explains how every place treats it. I am sure: it predicted each ball in each place from the others better than 'no sharing' (evidence 103) and 'size only' (108), and a second hidden number did not help (-13; 9 is decisive).
