# Independent Review of the Relentless Robot

## 1. What was built
An independent evaluation of the "relentless robot" claims. This includes a code audit for bugs and leaks, and a re-run of the experiments on fresh seeds (31–35) to verify the claims made in `RESULTS.md`.

## 2. Exact commands
```powershell
mkdir -Force validation-check/normal
mkdir -Force validation-check/gentle
$env:PYTHONDONTWRITEBYTECODE=1; D:/ai/labs/sera-field/.venv/Scripts/python.exe relentless_run.py --seeds 31 32 33 34 35 --results validation-check/normal --others --workers 3
$env:PYTHONDONTWRITEBYTECODE=1; D:/ai/labs/sera-field/.venv/Scripts/python.exe relentless_run.py --gentle --seeds 31 32 33 34 35 --results validation-check/gentle --others --workers 3
```

## 3. Bugs and Leaks found

### A. The sure/unsure bookkeeping has a major hole
When an idea (the `leader`) is beaten by a `rival` (the `winner`), the `winner` takes its place. However, the `winner`'s new list of rivals is constructed *only* from the currently unbeaten rivals of the `leader`. The rivals that the `leader` had already beaten (stored in `d['beaten']`) are discarded. They are not moved to the `winner`'s rivals, nor to its beaten list, nor to `ruled_out`. Because they are not in `ruled_out` or `kept`, they become `allowed` again for the next surprise, BUT if the `winner` explains the data (`surprise <= SURPRISE`), no new ideas are imagined. Thus, the `winner` becomes "sure" because its current rival list is empty, *without ever having beaten the rivals that the leader beat*.
**File:** `ccops5/relentless.py`, lines 223–242 (in `resolve()`).

### B. The comparison with the older robots is unfair
The relentless robot is unfairly advantaged in two ways:
1. **Unfair definition of "sure"**: For the older robots, "sure" is defined as `kept['confidence'] >= 0.6` at the *moment the idea is proposed* by the hunch (before any tests). For the relentless robot, "sure" means it has explicitly tested the idea against every rival and beaten them all. Comparing an initial gut feeling to a thoroughly tested conclusion and claiming the older robots are "sure and wrong" is an apples-to-oranges comparison.
   **File:** `relentless_run.py`, lines 61–64 (in `is_sure()`).
2. **Extra tests**: The relentless robot is allowed up to 3 extra tests (pushes) *per situation* (`TESTS = 3`), amounting to up to 30 extra data-gathering actions per world to distinguish rivals. The older robots never get to make extra tests; they only observe the default 2 pushes per situation.
   **File:** `ccops5/relentless.py`, lines 181–196 (in `doubt()`).

### C. "Found" counts something it shouldn't
"Found" is defined as `truth in kept`. However, `kept` is a list, and it can grow. If the robot keeps a completely wrong idea and later *also* appends the true idea to `kept` (without replacing the wrong one), `found` will still be True, even though the robot's state of belief is cluttered with wrong ideas. This inflates the "found" metric because there is no penalty in "found" for also believing false laws simultaneously.
**File:** `ccops5/relentless.py`, lines 287-288 (appending to `kept`), line 377 (`'found': truth in kept`).

## 4. Compare the claims (Seeds 31-35 vs 1-30)

We ran 5 fresh lives. At 12 exam worlds per life, that is 60 worlds. The results generally align but with some noticeable drops. Differences of a few percentage points are within chance (~13% standard error for 5 lives).

- **Found rates**:
  - *Claim*: Normal worlds familiar 98%, new 100%.
  - *Fresh*: Familiar 97% ± 2%, new 100% ± 0%. **Held up.**
- **"Sure → right"**:
  - *Claim*: 100% (222 of 222) in normal, 100% in gentle.
  - *Fresh*: In normal, it was 98% (58 of 60) — it was sure and wrong twice! In gentle, it was 100% (55 of 55). **Did not completely hold up.** (The bookkeeping hole mentioned above likely allowed it to be "sure and wrong").
- **Springs and swings in gentle worlds**:
  - *Claim*: Pushing where the idea could break finds the truth. Springs 100%, swings 95%.
  - *Fresh*: Springs 100%, swings 100% (vs 80% and 60% without tests). **Held up.**
- **Changes of mind**:
  - *Claim*: 37 times against 5 for the robot without tests (in gentle).
  - *Fresh*: 9 times against 1 for `no_tests`. **Held up** directionally (testing causes it to change its mind more often).

## 5. List of changes made after looking at results
No code changes were made to the lab files, as instructed. New folders `validation-check/normal` and `validation-check/gentle` were created to hold the fresh evaluation results.

## 6. Example self-explanations (from gentle, seed 31)
1. **dry friction (truth: steps with speed)**: "It is slowed by the same amount whenever it moves, like dry friction. I am sure: I tested it against "straight with speed", "wave with speed" and it won." `a = 1.25·tanh(1.6u) − 0.30·tanh(v/0.05)`
2. **swing (truth: wave with position)**: "It is pulled back the way a swing is: by the sine of how far it has gone. I am sure: I tested it against "straight with position" and it won." `a = 3.92·tanh(1.6u) − 13.62·sin(x)`
3. **stiff spring (truth: cubic with position)**: "It is pulled back gently near the middle and very hard far away. I am sure: nothing else I can imagine fits what I saw." `a = 4.70·tanh(1.6u) − 31.23·x³`

## 7. List of files
- `validation-check/REPORT.md` (this report)
- `validation-check/normal/` (contains JSON results and `RELENTLESS.md` for the normal run on seeds 31-35)
- `validation-check/gentle/` (contains JSON results and `RELENTLESS.md` for the gentle run on seeds 31-35)
