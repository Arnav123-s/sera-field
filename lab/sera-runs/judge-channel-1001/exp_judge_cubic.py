"""Does the judge accept the cubic SERA believes, where it refuses the free curve SERA must send? The stiff-2 world of
the general run (seed 3), the same throws; certify (a) free curves in position (9, 17 knots), (b) the cubic as a tied
shape - as it would be claimable had SERA registered it as one of its shapes before this world - then the same after
more pushes. Read-only: no Field is changed or saved."""
import os
import sys
import time

os.environ.setdefault('CCOPS5_SHAPES', 'library')
os.environ.setdefault('CCOPS5_CLAIM', 'functional')
os.environ.setdefault('CCOPS5_BAND', 'claim')
sys.path.insert(0, r'.')
import numpy as np  # noqa: E402

from ccops5.core import grammar, truth  # noqa: E402
from sera import lang as LG, phi as PH, tasks as TS  # noqa: E402

SEED, I, REP = 3, 3, 1                              # sera_one teaching: LAWS order (stiff is the 4th), 'stiff 2'
fam_true = (('position', 'cubic'),)
w, signs = TS.rail_world(SEED, 80_000 + 100 * I + REP, fam_true, 1)
task = TS.Rail(w, 'rail: stiff 2', (), signs)
f = PH.Field(1)
cube = LG.node('mul', LG.node('var', payload='_'), LG.node('mul', LG.node('var', payload='_'),
                                                            LG.node('var', payload='_')))
c = f.invent(cube, ('num', 'num'), 'math', 'cubic (test)', [])
table = f.concept_table()
knots = TS.draw_knots(('position', 'concept', c['id']), table)
shape = grammar.shape_term('position', TS.K_PART, 1, knots)
grammar.use_library([shape])                        # as if SERA had made it one of its shapes before this world
claims = {'free curve 9 knots': (('cell', 'position', 9),), 'free curve 17 knots': (('cell', 'position', 17),),
          'its cubic, as a shape': (shape,)}


def certify(label, fam):
    t0 = time.time()
    led = task.ledger([grammar.canonical(fam)])
    cert = truth.certify(led, grammar.canonical(fam), TS.EPS, claim='functional')
    band = getattr(cert, 'band', None)
    print(f'  {label:24s} accepted={cert.accepted!s:5s} band={band if band is None else round(float(band), 3)} '
          f'eps={TS.EPS} ({time.time() - t0:.0f} s){"  " + cert.reasons[0][:90] if cert.reasons else ""}',
          flush=True)


rng = np.random.default_rng([SEED, 99])
for round_ in range(3):
    print(f'throws: {len(task.throws)}', flush=True)
    for label, fam in claims.items():
        certify(label, fam)
    if round_ < 2:                                  # more pushes, chosen as SERA chooses them for its leading law
        led = task.ledger([grammar.canonical((shape,))])
        for _ in range(8):
            cand = task.actions(rng, led, [grammar.canonical((shape,))], [1.0])
            if not cand:
                break
            pick = max(cand, key=lambda a: a['info'])
            task.act(pick['action'])

print('--- the world\'s own law, from the grammar', flush=True)
grammar.use_library([])
for label, fam in (('true family (cubic)', fam_true), ('true family, as w.spec', w.spec.family)):
    try:
        certify(label, fam)
    except Exception as e:
        print('  ', label, 'ERROR', repr(e)[:160])
print('coefs', getattr(w.spec, 'coefs', None), 'sigma', w.sigma, 'masses', getattr(w.spec, 'masses', None))

print('--- through its lenses (the cubic drawn finer), on all 32 throws', flush=True)
pos = np.concatenate([t.x for t in task.throws])
print(f'positions visited: {pos.min():.2f} .. {pos.max():.2f}', flush=True)
for j in (1, 2):
    ch = grammar.lens_name('position', j, grammar.lens_origin('position', j))
    k = TS.draw_knots((ch, 'concept', c['id']), table)
    sh = grammar.shape_term(ch, TS.K_PART, 1, k)
    grammar.use_library([sh])
    print(ch, 'window', [round(v, 2) for v in grammar.input_range(ch)], flush=True)
    certify(f'its cubic on {ch}', (sh,))
    certify(f'free curve 17 on {ch}', (('cell', ch, 17),))
