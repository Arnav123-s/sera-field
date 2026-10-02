import os
for key, val in dict(CCOPS5_SHAPES='library', CCOPS5_CLAIM='functional', CCOPS5_BAND='claim',
                     CCOPS5_NUMERATOR='laplace', CCOPS5_KNOCK='throw').items():
    os.environ[key] = val
import sys
sys.path.insert(0, r'.')
import numpy as np
from ccops5.core import grammar as G, truth as T, checker as CK
from sera import tasks as TS, lang as LG
G.use_library(())
N = LG.node
s = N('var', payload='s')
cube = N('mul', s, N('mul', s, s))
w, signs = TS.rail_world(3, 80301, (('position', 'cubic'),), 1)
task = TS.Rail(w, 's10 shifted cubic', (), signs)
for e in (cube, N('add', N('one'), cube), N('add', s, cube)):
    fam = task.claim_family((('position', 'expr', e),), {}, ())
    cert = T.certify(task.ledger([fam]), fam, TS.EPS, claim='functional')
    line = f'{LG.show(e)} {fam} accepted={cert.accepted} band={cert.band}'
    if cert.accepted:
        ok, why = CK.check(cert, task.throws, task.sigma)
        line += f' checker={ok} observer={task.grade(cert, ok)}'
    else:
        line += f' {cert.reasons[:1]}'
    print(line, flush=True)
