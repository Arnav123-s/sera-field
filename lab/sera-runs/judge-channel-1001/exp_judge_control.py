"""Control: the world's own law, exactly (the grammar's analytic cubic, CCOPS5_SHAPES=off), on the same stiff-2 world -
does the judge's misfit test accept the exact truth at the whole range, where the drawn cubic misfits?"""
import os
import sys
import time

os.environ['CCOPS5_SHAPES'] = 'off'
os.environ.setdefault('CCOPS5_CLAIM', 'functional')
os.environ.setdefault('CCOPS5_BAND', 'claim')
sys.path.insert(0, r'.')
import numpy as np  # noqa: E402

from ccops5.core import grammar, truth  # noqa: E402
from sera import tasks as TS  # noqa: E402

fam_true = grammar.canonical((('position', 'cubic'),))
w, signs = TS.rail_world(3, 80_000 + 300 + 1, fam_true, 1)
task = TS.Rail(w, 'rail: stiff 2', (), signs)


def certify(label, fam):
    t0 = time.time()
    led = task.ledger([grammar.canonical(fam)])
    cert = truth.certify(led, grammar.canonical(fam), TS.EPS, claim=CLAIM)
    band = getattr(cert, 'band', None)
    print(f'  {label:26s} accepted={cert.accepted!s:5s} band={band if band is None else round(float(band), 3)} '
          f'({time.time() - t0:.0f} s){"  " + cert.reasons[0][:90] if cert.reasons else ""}', flush=True)


CLAIM = 'exact'
rng = np.random.default_rng([3, 99])
for round_ in range(3):
    print(f'throws: {len(task.throws)}', flush=True)
    certify('exact cubic (the truth)', fam_true)
    certify('free curve 17 knots', (('cell', 'position', 17),))
    if round_ < 2:
        led = task.ledger([fam_true])
        for _ in range(8):
            cand = task.actions(rng, led, [fam_true], [1.0])
            if not cand:
                break
            task.act(max(cand, key=lambda a: a['info'])['action'])
