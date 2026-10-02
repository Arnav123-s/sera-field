"""The key claims of the S09 diagnostic under the runs' own judge settings (only CCOPS5_SHAPES/CLAIM/BAND set, as
sera_one.py and sera_steps_ab.py set them; every other policy at its default), on stiff 2's first 16 throws, with
the checker and the observer."""
import os
import sys
for k in ('CCOPS5_NUMERATOR', 'CCOPS5_KNOCK', 'CCOPS5_AUDIT'):
    os.environ.pop(k, None)
os.environ.update(CCOPS5_SHAPES='library', CCOPS5_CLAIM='functional', CCOPS5_BAND='claim')
sys.path.insert(0, r'.')
from ccops5.core import grammar as G, truth as T, checker as CK  # noqa: E402
from sera import tasks as TS, lang as LG  # noqa: E402

w, signs = TS.rail_world(3, 80301, (('position', 'cubic'),), 1)
task = TS.Rail(w, 'rail: stiff 2', (), signs)
s = LG.node('var', payload='s')
part = ('position', 'expr', LG.node('mul', s, LG.node('mul', s, s)))
sent = task.claim_family((part,), {}, ())
print('what SERA sends for its cubic:', sent, flush=True)
for label, fam in (('what SERA sends', sent), ('free curve 33 knots', (('cell', 'position', 33),)),
                   ('cubic dimension r=4', (('cell', 'dim:x.x.x.mul.mul@4', 9),))):
    fam = G.canonical(fam)
    led = task.ledger([fam])
    cert = T.certify(led, fam, TS.EPS, claim='functional')
    line = f'{label:22s} accepted={cert.accepted} band={None if cert.band is None else round(float(cert.band), 4)}'
    if cert.accepted:
        ok, why = CK.check(cert, task.throws, task.sigma)
        line += f' checker={ok} observer={task.grade(cert, ok)}'
    else:
        line += f' {cert.reasons[:1]}'
    print(line, flush=True)
