"""SERA v3.1 designed experiments (sera.design): richer push programs within the same hand, chosen by imagining the
futures of the leading law and of what blocks it. Written before the module.

B3 dev (b3-dev2 units, 2026-09-24): 7 of the 8 L1/L2 worlds SERA was not sure of had the truth as its best guess,
blocked by a look-alike (sin x against x + x^3, straight + cubic against cubic + wave). Both minds chose from the same
16 single pushes. The world accepts any program within the hand (|force| <= 1 inside the 2 s of a throw)."""
import numpy as np
import pytest

from ccops5.core import grammar, likelihood as L, mind as M1, paths
from legacy.sera_v3 import design as D


def _model(*family):
    k, a, b = grammar.codes(grammar.canonical(family))
    return L.Model(k, a, b)


def _force_at(action, t):
    return sum(u for t0, t1, u in action.segments if t0 - 1e-9 <= t < t1 - 1e-9)


def test_every_program_stays_within_the_hand():
    spring = _model(('position', 'straight'))
    for program in D.programs(spring, np.array([-2.0]), 0.8, np.random.default_rng(0)):
        assert all(0.0 <= t0 < t1 <= paths.T_END + 1e-9 for t0, t1, _ in program.segments), program
        assert all(abs(_force_at(program, t)) <= D.HAND + 1e-9 for t in np.arange(0, paths.T_END, paths.DT_SIM))


def test_a_data_fitted_look_alike_is_separated_far_better_than_by_the_menu():
    """Replaces two first tests (2026-09-25; research R2, reviewer):
    - "reach 1.5x the menu": a proxy, and ill-founded for a 2 s throw on springs with 3-5 s periods;
    - a look-alike NOT fitted to data: its raw gap was large for every program.

    Now the look-alike is fitted to teacher throws of a sin world, and both laws may re-fit (surviving_gap, T-optimal).
    The bar stays 5x: the best designed program must add at least 5 times the evidence of the best menu push."""
    from ccops5.core import likelihood as L
    from ccops5.core.worlds import Throw, hand, push_of
    wave, sc = _model(('position', 'wave')), _model(('position', 'straight'), ('position', 'cubic'))
    sigma = (1e-3, 1e-3)
    rng = np.random.default_rng(4)
    throws = []
    for k, mu in enumerate((0.6, 0.9, 1.3, 1.7)):
        for u in (1.0, -0.6):
            xs, vs = paths.simulate(hand(u), mu, wave.kind, wave.a, wave.b, np.array([-2.0]), 1.0, 1.0, 0.0, 0.0)
            throws.append(Throw(k, len(throws), push_of(u), xs + rng.normal(0, 1e-3, xs.size),
                                vs + rng.normal(0, 1e-3, vs.size)))
    mus = {k: mu for k, mu in enumerate((0.6, 0.9, 1.3, 1.7))}

    def pooled(m):                      # truth-v2's pooled start (not on this branch): one regression of every
        rows, ys, order = [], [], []    # acceleration per unit of push on the family's columns; the fit then decides
        for t in throws:
            order += [t.situation] if t.situation not in order else []
            xm, vm = .5 * (t.x[:-1] + t.x[1:]), .5 * (t.v[:-1] + t.v[1:])
            mid = (np.arange(xm.size) + 0.5) * paths.DT_OBS
            push = sum(np.where((mid >= s0) & (mid < s1), f, 0.0) for s0, s1, f in zip(*t.action.arrays()))
            rows.append(np.array([[paths.term(m.kind[j], m.a[j], m.b[j], x, v, m.sx, m.sv) for j in range(m.n_coef)]
                                  for x, v in zip(xm, vm)]))
            ys.append((t.v[1:] - t.v[:-1]) / paths.DT_OBS / mus[t.situation] - push)
        coef = np.linalg.lstsq(np.vstack(rows), np.concatenate(ys), rcond=None)[0]
        return L.Post(np.concatenate([coef, [mus[s] for s in order]]), np.eye(m.n_coef + len(order)), order)

    fits = {name: L.fit(m, throws, sigma, start=pooled(m), iters=60) for name, m in (('wave', wave), ('sc', sc))}
    assert all(f.ok for f in fits.values())

    def numbers(name, m, k, action):
        f = fits[name]
        idx = list(range(m.n_coef)) + [m.n_coef + f.order.index(k)]
        P = np.linalg.pinv(f.cov[np.ix_(idx, idx)])
        y, J = L._jac(m, f.coef, f.mu[k], Throw(k, -1, action, np.zeros(paths.N_OBS), np.zeros(paths.N_OBS)))
        return y, J, P

    def gap(k, action):
        fa, ja, pa = numbers('wave', wave, k, action)
        fb, jb, pb = numbers('sc', sc, k, action)
        return D.surviving_gap(fa, fb, ja, jb, pa, pb, sigma)

    k = 3
    menu = max(gap(k, a) for a in M1.menu(wave, fits['wave'].coef, fits['wave'].mu[k]))
    designed = max(gap(k, a) for a in D.programs(wave, fits['wave'].coef, fits['wave'].mu[k], np.random.default_rng(0)))
    assert designed >= 5.0 * menu, (designed, menu)


def test_v31_stops_pushing_a_knocked_object():
    """B3 world L1-07: situation 6 carries a knock (a world bump) that every push of it repeats. SERA v3.0 pushed it
    about 16 times; 26 of 40 throws misfit and the "something else" alarm fired on the true law. v3.1 sees from its
    own committed predictions that both laws miss by far more than the noise, and pushes that object no more."""
    import torch
    from legacy.sera_v3 import imagine as I, mind as SM, worlds as SW
    w = SW.make(1, 9007, 1, 'dream')
    model = I.Imagination()
    import os
    runs = os.environ.get('SERA_RUNS', 'D:/ai/labs/ccops5-sera-lab/sera-runs')
    model.load_state_dict(torch.load(f'{runs}/imagine-v1/model.pt', map_location='cpu'))
    model = model.float().eval()    # as the runners do: ccops5.laws sets torch's default dtype to float64 at import
    r = SM.Mind(model, w.sigma, eps=0.2, budget=3 * w.n_situations, design=True).live(w)
    knocked = sum(1 for k, e in r.events if e == 'disturbed')
    pushes_on_6 = sum(1 for f in r.foresight if f['situation'] == 6)
    assert knocked >= 1 and pushes_on_6 <= 2, (knocked, pushes_on_6)
    assert not r.alarm, r.gap


@pytest.mark.slow
def test_a_missing_idea_is_not_blamed_on_the_objects():
    """R4-1 (T-S on Colab, 2026-09-26): in masked-term worlds the old rule flagged an object on every one of SERA's 24
    pushes (s1-i9101-L3: 24 'disturbed' events), because a law missing a term misses on every object. Now a miss only
    makes the object a suspect, and the next push, on another object, decides. Every object SERA calls disturbed must
    carry a real knock (the world's own bumps, known to the test, never to SERA)."""
    import os
    import sys
    import torch
    from ccops5.core import truth
    from legacy.sera_v3 import imagine as I, mind as SM, worlds as SW
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
    import sera_audit_check as TS
    w = SW.make(1, 9101, 3, 'dream')
    t_g = next(t for t in grammar.canonical(w.spec.family) if t not in grammar.IDEAS)
    mask = TS.neighbours(t_g, truth.UNIVERSE_TERMS, grammar)
    model = I.Imagination()
    runs = os.environ.get('SERA_RUNS', 'D:/ai/labs/ccops5-sera-lab/sera-runs')
    model.load_state_dict(torch.load(f'{runs}/imagine-v1/model.pt', map_location='cpu'))
    model = model.float().eval()
    r = SM.Mind(model, w.sigma, eps=0.2, budget=3 * w.n_situations, design=True, mask=mask).live(w)
    flagged = {k for k, e in r.events if e == 'disturbed'}
    knocked = {k for k, b in enumerate(w.spec.bumps) if b is not None}
    assert flagged <= knocked, (flagged, knocked, [e for _, e in r.events])


def test_a_gap_the_rival_can_absorb_is_not_counted():
    """R2: two drag laws that differ only in their coefficient part far apart at today's estimates, but if the earlier
    throws do not pin the coefficient, the rival re-fits and the push tells them apart by almost nothing. With the
    coefficients pinned, the surviving gap equals the raw one."""
    from ccops5.core import likelihood as L
    from ccops5.core.worlds import Throw
    drag = _model(('speed', 'straight'))
    act = M1.menu(drag, np.array([-1.0]), 1.0)[3]
    th = Throw(0, -1, act, np.zeros(paths.N_OBS), np.zeros(paths.N_OBS))
    fa, ja = L._jac(drag, np.array([-1.0]), 1.0, th)
    fb, jb = L._jac(drag, np.array([-1.2]), 1.0, th)
    sigma = (1e-3, 1e-3)
    raw = D.surviving_gap(fa, fb, ja, jb, np.eye(2) * 1e12, np.eye(2) * 1e12, sigma)
    free = D.surviving_gap(fa, fb, ja, jb, np.zeros((2, 2)), np.zeros((2, 2)), sigma)
    naive = D.separation(drag, np.array([-1.0]), drag, np.array([-1.2]), 1.0, act, sigma)
    assert abs(raw - naive) <= 1e-4 * naive                         # pinned at a finite precision (1e12)
    assert free <= 0.05 * naive                                  # up to the linearization (second order in the shift)
