# Ball world invariants, live on seed 1

- PASS  A oracle: 40 throws (seed 1, every ball, every place): true law misses by 1.40 mm on average, 1.69 mm at most (limit 2 mm)
- PASS  A integration: imagining vs world at most 8.88e-13 mm; half time step moves a throw at most 6.10e-07 mm (limit 0.1 mm)
- PASS  A energy: vacuum and moon: largest gap from the exact parabola 8.7e-14 m (limit 1e-9); air, water and windy (riding with the air): largest change of energy between readings -7.63e-04 J/kg (must be below 0: it only ever falls)
- PASS  B law selection (concept): seed 1: vacuum: down, own throws 0, worst fit 0.17 SE; air: down+drag2, wind +0.00 in [-0.40, +0.40] (true +0.00), own throws 0, worst fit 0.58 SE; windy: down+drag2 moving, wind -1.00 in [-1.40, -0.60] (true -1.09), own throws 1, worst fit 0.42 SE; water: down+drag2, wind +0.00 in [-0.40, +0.40] (true +0.00), own throws 0, worst fit 0.36 SE; moon: down, own throws 0, worst fit 0.37 SE (each place: the true forces only, sure, numbers within 3 SE, wind range holds the truth)
- PASS  B law selection (per_place): seed 1: vacuum: down, own throws 0, worst fit 0.17 SE; air: down+drag2, wind +0.00 in [-0.40, +0.40] (true +0.00), own throws 0, worst fit 0.58 SE; windy: down+drag2 moving, wind -1.00 in [-1.40, -0.60] (true -1.09), own throws 1, worst fit 0.42 SE; water: down+drag2, wind +0.00 in [-0.40, +0.40] (true +0.00), own throws 0, worst fit 0.36 SE; moon: down, own throws 0, worst fit 0.37 SE (each place: the true forces only, sure, numbers within 3 SE, wind range holds the truth)
- PASS  C concept hierarchy: seed 1: evidence one number over no sharing 106.0, over size only 103.4, second number over one 1.3 (9 is decisive); powers chosen air/down 1 (none), air/drag2 2, vacuum/down 0 (none), water/down 3, water/drag2 2, windy/down 0 (none), windy/drag2 2; push number ranks mass 1.00 (near-ties the rail cannot tell apart, swapped: 0)
- PASS  C source: ballmind.py imports from the world only ['DT_OBS', 'DT_SIM', 'N_BALLS', 'N_OBS', 'PLACES', 'PUSH', 'SIGMA_POS', 'TRAINING']; reads keys none of 'mass', 'size', 'word'
- PASS  C what learners are given: keys handed to the learners: ['id', 'look', 'rail_speed', 'seen_size']
- PASS  E never sure and wrong: seed 1's balls, windy yard, wind set by hand, up to 6 own throws: +0.00: still [-0.40, +0.60] sure, 0 own; +0.10: still [-0.40, +0.60] sure, 0 own; -0.10: still [-0.60, +0.40] sure, 0 own; +0.25: moving [+0.00, +0.60] not sure, 3 own; -0.25: moving [-0.60, +0.00] not sure, 4 own; +0.50: moving [+0.20, +0.80] sure, 5 own; -0.50: moving [-0.80, -0.20] not sure, 2 own; +1.00: moving [+0.60, +1.60] sure, 0 own; -1.00: moving [-1.40, -0.60] sure, 1 own | sure and wrong at none
- PASS  E finds the wind: every wind of 0.5 m/s or more found (moving air, range holds the true wind): all found
- PASS  E not sure when it cannot throw: no own throws allowed, faint winds: +0.25: still [-0.20, +0.80] not sure, 0 own; -0.25: still [-0.80, +0.20] not sure, 0 own | not sure at [0.25, -0.25], sure and wrong at none
- PASS  E naming: seed 1: of 4 balls it was not told about, named 3 right, 0 wrong, 1 not sure

ALL PASS
