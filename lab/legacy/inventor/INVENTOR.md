# The inventor robot in school

Seeds [11, 12, 13, 14, 15, 16, 17, 18, 19, 20]. Numbers are averages over lives, ± one standard error.

## Exam Force Check

Are the worlds a fair test? Computed by `(review notes, not published)`: the true idea must explain the world, nothing may run away, and every product force must beat every old idea and every sum of two old ideas by decisive evidence over one world.

Seeds [1, 2, 3], normal moments only. Evidence as the robot weighs it (decisive = 9.0, capped at 6.0 per moment; alarm at surprise 1.8).

| Force | Truth explains | Largest acceleration | Worlds where the truth beats every old idea or pair decisively | Median evidence | Best old rival fails in | Usual best old rival |
|---|---|---|---|---|---|---|
| cubic drag | 100% | 4.2 | 100% of 6 | 38.3 | 46% of moments | straight with position + growing with position |
| dry friction | 100% | 3.6 | - | - | - | - |
| growing drag | 100% | 4.2 | 100% of 15 | 42.8 | 41% of moments | cubic with position + wave with position |
| rubbing | 100% | 4.3 | - | - | - | - |
| rubbing valley | 100% | 4.3 | 100% of 15 | 60.0 | 83% of moments | straight with position |
| slope | 100% | 6.6 | - | - | - | - |
| spring | 100% | 4.9 | - | - | - | - |
| stiff spring | 100% | 9.6 | - | - | - | - |
| swing | 100% | 6.0 | - | - | - | - |
| thick oil | 100% | 4.1 | - | - | - | - |
| tight spring | 100% | 5.6 | - | - | - | - |
| valley | 91% | 4.4 | - | - | - | - |
| water drag | 100% | 3.9 | - | - | - | - |
| wave drag | 100% | 4.2 | 100% of 6 | 54.0 | 87% of moments | straight with position |
| weakening spring | 100% | 4.6 | 100% of 15 | 44.0 | 42% of moments | cubic with position + wave with position |

NOTE A: old force "valley" (unchanged from the school) is explained in 91% of moments

## Exam

| Robot | Old: found | Old: kept nothing | Old: tries | Practised Inv: found | Practised Inv: kept nothing | Practised Inv: tries | New Sing: found | New Sing: kept nothing | New Sing: tries | New Prod: found | New Prod: kept nothing | New Prod: tries | Ideas imagined per world | Guess miss (median) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| inventor | 0.91 ± 0.03 | 0.09 ± 0.03 | 7.17 ± 0.77 | 0.47 ± 0.10 | 0.20 ± 0.11 | 8.27 ± 0.81 | 0.97 ± 0.02 | 0.03 ± 0.02 | 10.40 ± 1.42 | 0.38 ± 0.12 | 0.40 ± 0.08 | 11.20 ± 0.51 | 12.25 ± 1.12 | 0.333 |
| menu | 0.97 ± 0.02 | 0.00 ± 0.00 | 4.51 ± 0.33 | 0.00 ± 0.00 | 0.63 ± 0.08 | 12.00 ± 0.00 | 1.00 ± 0.00 | 0.00 ± 0.00 | 5.92 ± 0.37 | 0.00 ± 0.00 | 1.00 ± 0.00 | 12.00 ± 0.00 | 12.98 ± 0.48 | 0.382 |
| inventor_untaught | 0.84 ± 0.03 | 0.15 ± 0.04 | 10.81 ± 0.54 | 0.60 ± 0.08 | 0.03 ± 0.03 | 9.03 ± 0.87 | 0.97 ± 0.02 | 0.03 ± 0.02 | 10.65 ± 0.94 | 0.33 ± 0.09 | 0.42 ± 0.07 | 12.25 ± 0.52 | 13.71 ± 0.76 | 0.389 |

## Honesty: the ideas it kept in the exam

| Robot | Old: Sure → right | Old: Unsure → right | Old: Sure but not right | Practised Inv: Sure → right | Practised Inv: Unsure → right | Practised Inv: Sure but not right | New Sing: Sure → right | New Sing: Unsure → right | New Sing: Sure but not right | New Prod: Sure → right | New Prod: Unsure → right | New Prod: Sure but not right |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| inventor | 100% (56) | 100% (3) | 0% (59) | 100% (6) | 47% (17) | 0% (23) | 100% (27) | - | 0% (27) | 100% (7) | 0% (7) | 0% (14) |
| menu | 100% (68) | 100% (2) | 0% (70) | 0% (7) | 0% (1) | 88% (8) | 100% (34) | - | 0% (34) | - | - | - |
| inventor_untaught | 100% (51) | 100% (2) | 0% (53) | 100% (7) | 50% (18) | 0% (25) | 100% (25) | - | 0% (25) | 100% (6) | 17% (12) | 0% (18) |

## The final check before "sure"

Before saying "sure", every robot weighs its idea against every idea it can form. The check never changes what it keeps.

| Robot | Exam worlds where a kept idea was wrong | ...and it named the right idea as a rival it could not rule out | Worlds where an idea it never imagined fitted decisively better |
|---|---|---|---|
| inventor | 19 of 190 | 19 of 19 | 9 of 190 |
| menu | 13 of 190 | 2 of 13 | 0 of 190 |
| inventor_untaught | 22 of 190 | 22 of 22 | 11 of 190 |

## What it says: the inventor robot's exam, seed 11

- **wave drag** (truth: wave with speed and size with position). Something is still pushing it that I cannot explain. I do not know what it is yet. `a = 2.91·tanh(1.6u)`
- **tight spring** (truth: growing with position). It is pulled back toward the middle much more the farther it goes. I am sure: nothing else I can form fits what I saw. `a = 1.72·tanh(1.6u) − 5.60·x|x|`
- **cubic drag** (truth: cubic with speed and size with position).  `a = 3.87·tanh(1.6u)`
- **thick oil** (truth: cubic with speed). It is slowed very sharply when fast. I am sure: nothing else I can form fits what I saw. `a = 2.21·tanh(1.6u) − 1.76·v³`
- **cubic drag** (truth: cubic with speed and size with position). It is slowed very sharply when fast depending on distance. I am sure: nothing else I can form fits what I saw. `a = 2.29·tanh(1.6u) − 2.84·v³·|x|`
- **valley** (truth: steps with position). It is pulled back toward the middle equally anywhere it is. I am sure: nothing else I can form fits what I saw. `a = 4.44·tanh(1.6u) − 3.60·tanh(x/0.05)`
- **rubbing** (truth: straight with speed). It slows down. I am not sure: "wave with speed" explains what I saw as well, and none of my pushes could tell them apart. `a = 1.42·tanh(1.6u) − 0.48·v`
- **valley** (truth: steps with position). It is pulled back toward the middle equally anywhere it is. I am sure: nothing else I can form fits what I saw. `a = 1.49·tanh(1.6u) − 1.47·tanh(x/0.05)`
- **spring** (truth: straight with position). It is pulled back toward the middle the farther it is from the middle. I am sure: nothing else I can form fits what I saw. `a = 2.60·tanh(1.6u) − 7.09·x`
- **swing** (truth: wave with position). It is pulled back toward the middle wavy with distance. I am sure: nothing else I can form fits what I saw. `a = 1.98·tanh(1.6u) − 6.14·sin(x)`
- **slope** (truth: a steady push). A steady push always leans it one way, like a slope. I am sure: nothing else I can form fits what I saw. `a = 4.61·tanh(1.6u) − 1.97·1`
- **dry friction** (truth: steps with speed). It is slowed by the same amount whenever it moves. I am sure: nothing else I can form fits what I saw. `a = 2.88·tanh(1.6u) − 0.91·tanh(v/0.05)`
- **stiff spring** (truth: cubic with position). It is pulled back toward the middle very sharply when far away. I am sure: nothing else I can form fits what I saw. `a = 4.13·tanh(1.6u) − 22.79·x³`
- **water drag** (truth: growing with speed). Something is still pushing it that I cannot explain. I do not know what it is yet. `a = 2.70·tanh(1.6u)`
- **wave drag** (truth: wave with speed and size with position). Something is still pushing it that I cannot explain. I do not know what it is yet. `a = 3.12·tanh(1.6u)`
- **thick oil** (truth: cubic with speed). It is slowed very sharply when fast. I am sure: nothing else I can form fits what I saw. `a = 3.40·tanh(1.6u) − 1.59·v³`
- **growing drag** (truth: straight with speed and size with position). Something is still pushing it that I cannot explain. I do not know what it is yet. `a = 1.46·tanh(1.6u)`
- **rubbing valley** (truth: size with speed and steps with position). Something is still pushing it that I cannot explain. I do not know what it is yet. `a = 2.51·tanh(1.6u)`
- **weakening spring** (truth: size with speed and straight with position). Something is still pushing it that I cannot explain. I do not know what it is yet. `a = 1.60·tanh(1.6u)`

## Changes made

- Widened rivals in inventor.py to include every old idea, single-piece variations, and any idea imagined during the world.
- Fixed "sure" to mean the idea beat all these rivals.
- Split the 3x3 leftover grid feature into position-specific and speed-specific templates in `feelings`, so credit carries over correctly to unseen combos.
- Updated legacy/inventor/INVENTOR.md generation to include "kept nothing" metrics and the force checks.
- Replaced np.abs default fallback in _scalar with explicit size shape, changed all product forces to use size instead of growing/steps so they do not change sign with position.
- Fine-tuned product force strengths to match typical accelerations of old forces and stay well within the (-100, 100) clip range.
- Added a --quick flag to legacy/inventor/inventor_run.py for faster iterations.
- Categorized exam results into 4 categories: old forces, practised products, never-shown singles, never-shown products.
- Added sure/unsure/wrong metrics for each of the 4 categories.
- (development note) Round 3: the first product forces changed sign with position and ran away into the acceleration clip, so even the true idea explained only 2–34% of moments; they were replaced by stable ones.
- (development note) Round 3: the fairness check "median surprise of the best old idea >= 3" failed (1.1–3.8), because old ideas pass about half the moments. It was replaced, after seeing that, by the robot’s own rule: the true product must beat every old idea and pair by decisive evidence over a world, and the best old rival must fail at least 30% of moments.
- (development note) The held idea is no longer blamed for a moment that no idea can explain (hidden bump), as in the relentless robot.
- (development note) After dev seeds 1–10: "sure" was wrong for 22–42% of kept inventions, because the right idea was two part-swaps away and never became a rival (for example |x|·v kept for x·|v|). Before saying "sure", it now weighs its idea against every idea it can form, over everything it saw. This final check never changes what it keeps, so "found" still measures its own limited search.
