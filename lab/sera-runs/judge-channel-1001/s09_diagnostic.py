"""review 9's diagnostic ((review notes, not published) section 7), as given: the stiff-2 world's first throws; per-object residuals
and certificates for whole-range free curves, the tied cubic drawing, the cubic dimension (Decision 15), and an
in-memory analytic proxy priced as the proposed expression code. Research adapter only - no judge is changed."""
import os
import sys
for k, v in dict(CCOPS5_SHAPES='library', CCOPS5_CLAIM='functional',
                 CCOPS5_BAND='claim', CCOPS5_NUMERATOR='laplace',
                 CCOPS5_KNOCK='throw', CCOPS5_AUDIT='universe-1').items():
    os.environ[k] = v
sys.path.insert(0, r'.')
import numpy as np  # noqa: E402
from unittest.mock import patch  # noqa: E402
from ccops5.core import grammar as G, truth as T, likelihood as L, checker as CK  # noqa: E402
from sera import tasks as TS, lang as LG  # noqa: E402

w, signs = TS.rail_world(3, 80301, (('position', 'cubic'),), 1)
task = TS.Rail(w, 'rail: stiff 2', (), signs)
s = LG.node('var', payload='s')
cube = LG.node('mul', s, LG.node('mul', s, s))
part = ('position', 'expr', cube)
print('actual unregistered claim:', task.claim_family((part,), {}, ()), flush=True)
sh = G.shape_term('position', 33, 1, TS.draw_knots(part, {}))
G.use_library((sh,))  # frozen before any ledger; synthetic fixture, not learned provenance
analytic = (('position', 'cubic'),)


def fresh(fam):
    led = T.Ledger([fam], task.sigma)
    for th in task.throws:
        led.add(th)
    return led


def report(label, fam):
    cached, led = task.ledger([fam]), fresh(fam)
    assert cached.Q[fam] == led.Q[fam]
    assert np.array_equal(cached.post[fam].mean, led.post[fam].mean)
    fit = led.mle(fam)
    model = led._models[fam]
    rms = {}
    for th in task.throws:
        kt = L.knocked(th, (fit.knocks or {}).get(th.situation, 0))
        r = (L._obs(th) - L._sim(model, fit.coef, fit.mu[th.situation], kt)) * L._scale(task.sigma)
        rms.setdefault(th.situation, []).append(float(np.sqrt(np.mean(r * r))))
    print(label, 'fit', fit.ok, fit.converged, 'LL', round(float(fit.loglik), 2),
          'object max RMS', {k: round(max(v), 2) for k, v in rms.items()}, flush=True)
    cert = T.certify(led, fam, TS.EPS, claim='functional')
    print('   certificate', cert.accepted, cert.adequacy, None if cert.band is None else round(float(cert.band), 4),
          cert.reasons[:1], flush=True)
    if cert.accepted:
        ok, why = CK.check(cert, task.throws, task.sigma)
        print('   checker', ok, why, 'observer', task.grade(cert, ok), flush=True)


for K in (9, 17, 33):
    report('whole free ' + str(K), (('cell', 'position', K),))
report('whole tied cubic', (sh,))
for r in (3, 4):
    report('cubic dimension ' + str(r), (('cell', 'dim:x.x.x.mul.mul@' + str(r), 9),))
old_term, old_checks = T._functional_term, T.functional_checks
with patch.object(T, '_functional_term', side_effect=lambda t: (1 / 1024) / 3 * 7 ** -6 if t == analytic[0] else old_term(t)), \
        patch.object(T, 'functional_checks', side_effect=lambda f: [('hats', 'position', 33, ())] if G.canonical(f) == analytic else old_checks(f)):
    report('analytic-proxy', analytic)
