# Ball world checks (ball-results)

- PASS  A oracle: 120 throws (seeds 1-3, every ball, every place): true law misses by 1.40 mm on average, 1.69 mm at most (limit 2 mm)
- PASS  B integration: imagining vs world at most 3.55e-12 mm; half time step moves a throw at most 6.10e-07 mm (limit 0.1 mm)
- PASS  C source: ballmind.py imports from the world only ['DT_OBS', 'DT_SIM', 'N_BALLS', 'N_OBS', 'PLACES', 'PUSH', 'SIGMA_POS', 'TRAINING']; reads keys none of 'mass', 'size', 'word'
- PASS  E determinism: seed 1 again vs saved: concept same, per_place same, baseline same
- PASS  C what learners are given: keys handed to the learners: ['id', 'look', 'rail_speed', 'seen_size']
- PASS  C other size powers: world with drag ∝ size¹, lift ∝ size², water drag ∝ size³ (seed 1): chose {'air/drag2': 1, 'windy/drag2': 1, 'water/down': 2, 'water/drag2': 3}; concept kept True
- PASS  C forces ignore mass: world where no force depends on mass (seed 1): concept kept False, predicted with Rs; one-number-over-size-only evidence -88.4 (9 is decisive)
- PASS  F control: world where the pull grows 2% per unit of mass (seed 1): said same False, evidence for one shared pull -10.8 (−9 or less means mass matters), correlation of pull with push number 1.00
- PASS  D held out: 30 runs: kept-back pairs shown to a robot 0 times; runs with a moon throw before training ended: 0
- PASS  F Galileo not empty: 20 runs: fewest vacuum throws per ball 2; smallest difference between the two models' pulls 0.0158 m/s²; said same in 20 of 20
- PASS  G computed report: BALL.md regenerated from 30 saved runs: byte-identical

ALL PASS
