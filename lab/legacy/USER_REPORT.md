# ccops5 lab: status for you

Updated 2026-09-22. **The ball-world humility fix is done and confirmed on fresh seeds.** The details are in `legacy/RESULTS.md` (ball-throw world) and `README.md` (changes).

| Phase | State |
|---|---|
| 1. Look around, change nothing | Done |
| Your decisions | "Test at the edge" for humility; fresh seeds 21–30 for version 2; the mass-order check allows near-ties the rail cannot resolve |
| Record | Version 1's fresh seeds 11–20 committed as they were (`31c62f9`) |
| 2. Tests first | New `legacy/ball/ball_check.py` committed before any fix (`e4622c0`). It failed on version 1 as it should |
| 3. The fix | Version 2 (`4bca21d`), plus 2 fixes from the independent review (`4e7afa9`). Seed-1 invariants: all pass, the same on a second run |
| 4. Dev seeds 1–10 | Full audit A–H: all pass. Frozen (`e037891`) |
| 5. Fresh seeds 21–30 | Run once in a visible window. Read-only audit: all pass |
| 6. Write-up | README, RESULTS, (review notes, not published) and memory updated |

## The result in one breath

On brand-new balls and places, run once, the robot:
- kept the true law in all 50 places, including three faint winds (0.45, 0.72 and 0.84 m/s);
- said "not sure" only in those three windy lives, because there a steady sideways push on each ball looks the same through its eyes;
- was never sure and wrong: 0 of 94 sure claims.

Frozen version 1, run on the same seeds as a control, was sure and wrong once (seed 27: "sure: still air" in a 0.84 m/s wind, without a single throw of its own). Across its 20 fresh lives, version 1 was sure and wrong 3 times.

The idea of mass still carries the result. For balls in a place where they were never thrown, the concept robot missed by 1.6 cm, the robot without the idea of mass by 72.7 cm (47 times more), and the ordinary network by 56.1 cm (36 times more).

## What version 2 changes, in plain words

- **A hint stays open.** An idea that is the robot's idea plus something extra (moving air) must be followed up when it predicts new throws better by at least 1. That is the least evidence the robot ever counts. Version 1 let it go unless it won by 9.
- **It tests at the edge.** It throws where the strongest version of that idea the data still allow would show most. It tries both ends of the wind range, because a head wind can show more than a tail wind.
- **"Still air" comes with a bound**, for example "any wind lies between −0.4 and +0.4 m/s". A claim counts as true only if its bound holds the real wind.
- **Where your "test at the edge" had to be refined:** strictly, "sure" would need even the strongest allowed wind to be invisible on every throw. That can never happen within 6 throws: its best throw can always see a wind at the edge of what it has ruled out. So "sure" now means no hint is left, and the claim carries its bound.

## Open questions for next time

- **A lob.** A throw that changes speed a lot could tell a faint wind from a steady push. Its menu has no such throw, so it says "not sure" there.
- **Bounds.** In still air the bound comes from the teacher's throws alone (about ±0.6 to ±0.8 m/s). It could spend spare throws to tighten it.
- **Noise units.** Neighbouring measured accelerations share noise, so its evidence is cautious (fits sat within 0.6 SE of the truth). A correct noise model would make it far more decisive.
- **Helper scripts:** on hold until the author says they are ready.
