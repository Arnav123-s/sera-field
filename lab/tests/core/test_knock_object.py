"""truth-v3 T2, M-1 (Decision 10; S4 §C5; docs/SERA_FIELD_THEORY.md v1.1 §15): knocks per object, as the worlds make
them. A knock is a latent per object: none (prior 0.95) or one of 4 onsets x 2 signs (0.05/8 each), a push of +-1.5
for 0.2 s - exactly one more segment of the throw's program. Numerator: the predictive mixes over the object's knock
given its past throws (a sub-density: fewer branches only lower it). Denominator: the best knock per object (it
dominates the per-object model). Policy CCOPS5_KNOCK = 'object' (M-1) | 'throw' (per-throw outliers only, truth-v2).
Written before the code."""
import math

import numpy as np
import pytest

from ccops5.core import grammar, likelihood as L, paths, worlds as W

SIGMA = (0.001, 0.001)
LAW = (('position', 'straight'), ('speed', 'straight'))
COEF = np.array([-2.0, -0.8])
BUMP = (0.8, 1.5)


def _throws(bumped=None, situations=4, pushes=(1.0, -0.6), seed=5):
    kk, aa, bb = grammar.codes(LAW)
    rng = np.random.default_rng(seed)
    out, masses = [], []
    for k in range(situations):
        m = float(rng.uniform(0.6, 2.5))
        masses.append(m)
        t0, amp = BUMP if k == bumped else (0.0, 0.0)
        for j, u in enumerate(pushes):
            xs, vs = paths.simulate(W.hand(u), 1 / m, kk, aa, bb, COEF, 1.0, 1.0, t0, amp)
            nr = np.random.default_rng([seed, k, j])
            out.append(W.Throw(k, len(out), W.push_of(u), xs + nr.normal(0, 1e-3, xs.size),
                               vs + nr.normal(0, 1e-3, vs.size)))
    return out, masses


def test_the_knock_prior_is_proper_and_the_worlds_family():
    assert len(L.KNOCKS) == 8 and set(L.KNOCKS) == {(t, a) for t in (0.6, 0.8, 1.0, 1.2) for a in (-1.5, 1.5)}
    assert abs(sum(math.exp(x) for x in L.KNOCK_LOGP) - 1.0) < 1e-12
    assert abs(math.exp(L.KNOCK_LOGP[0]) - 0.95) < 1e-12


def test_a_knock_is_one_more_segment():
    throws, masses = _throws(bumped=0)
    model = L.Model(*grammar.codes(LAW))
    t = throws[0]
    j = 1 + L.KNOCKS.index(BUMP)
    kt = L.knocked(t, j)
    y = L._sim(model, COEF, 1 / masses[0], kt)
    xs, vs = paths.simulate(W.hand(t.u), 1 / masses[0], model.kind, model.a, model.b, COEF, 1.0, 1.0, *BUMP)
    assert np.max(np.abs(y - np.concatenate([xs, vs]))) < 1e-12
    assert L.knocked(t, 0) is t and kt.situation == t.situation and kt.action.segments == t.action.segments


def _prequential(model, throws, policy, monkeypatch):
    monkeypatch.setattr(L, 'KNOCK', policy)
    post, q = L.empty_post(model), 0.0
    for t in throws:
        dq, post = L.step(model, post, t, SIGMA)
        q += dq
    return q, post


def test_a_clean_object_drops_its_knock_branches_after_one_throw(monkeypatch):
    throws, _ = _throws()
    model = L.Model(*grammar.codes(LAW))
    _, post = _prequential(model, throws[:1], 'object', monkeypatch)
    lp = post.knock[0]
    assert lp[0] > -1e-6 and max(lp[1:]) < L.KNOCK_KEEP


def test_a_knocked_object_is_recognized_and_teaches_the_law(monkeypatch):
    throws, masses = _throws(bumped=1)
    model = L.Model(*grammar.codes(LAW))
    q_obj, post = _prequential(model, throws, 'object', monkeypatch)
    lp = post.knock[1]
    assert int(np.argmax(lp)) == 1 + L.KNOCKS.index(BUMP)
    assert 1 in post.order                                       # its mass is learned: its throws teach the law
    mu = post.mean[model.n_coef + post.order.index(1)]
    assert abs(mu - 1 / masses[1]) < 0.01 / masses[1]
    q_thr, _ = _prequential(model, throws, 'throw', monkeypatch)
    assert q_obj > q_thr + 100                                   # the knocked throws are now predicted


def test_clean_evidence_changes_only_by_the_knock_prior(monkeypatch):
    throws, _ = _throws()
    model = L.Model(*grammar.codes(LAW))
    q_obj, _ = _prequential(model, throws, 'object', monkeypatch)
    q_thr, _ = _prequential(model, throws, 'throw', monkeypatch)
    k = len({t.situation for t in throws})
    assert abs((q_obj - q_thr) - k * math.log(0.95)) < 0.1, (q_obj - q_thr, k * math.log(0.95))


@pytest.mark.slow
def test_the_denominator_dominates_and_finds_the_knock(monkeypatch):
    throws, masses = _throws(bumped=2)
    model = L.Model(*grammar.codes(LAW))
    _, post = _prequential(model, throws, 'object', monkeypatch)
    fit = L.fit(model, throws, SIGMA, start=post)        # as the ledger does: from the running posterior
    assert fit.ok and fit.knocks.get(2) == 1 + L.KNOCKS.index(BUMP)
    truth_ll = 0.0                                               # the per-object model's likelihood at the truth
    for k in range(4):
        ts = [t for t in throws if t.situation == k]
        per = []
        for j, lp in enumerate(L.KNOCK_LOGP):
            s = lp
            for t in ts:
                a = math.log(1 - L.RHO) + L.throw_loglik(model, COEF, 1 / masses[k], L.knocked(t, j), SIGMA)
                s += np.logaddexp(a, L.log_outlier(t))
            per.append(s)
        truth_ll += float(np.logaddexp.reduce(per))
    assert fit.loglik >= truth_ll - 1e-6, (fit.loglik, truth_ll)
    mix = 0.0                          # independent review item 2: at the fitted numbers, EVERY object's full 9-knock mixture
    for k in range(4):                 # (none dropped) lies below the denominator - exactly, not by a bound
        ts = [t for t in throws if t.situation == k]
        per = [lp + sum(np.logaddexp(math.log(1 - L.RHO) + L.throw_loglik(model, fit.coef, fit.mu[k],
                                                                          L.knocked(t, j), SIGMA), L.log_outlier(t))
                        for t in ts) for j, lp in enumerate(L.KNOCK_LOGP)]
        mix += float(np.logaddexp.reduce(per))
    assert fit.loglik >= mix - 1e-9, (fit.loglik, mix)


@pytest.mark.slow
def test_clean_evidence_ratios_move_only_by_the_knock_prior(monkeypatch):
    """independent review (M-1 item 1): on a clean world, log E(A:B) of the true law against each of its top rivals moves from
    the per-throw judge by exactly K log(0.95) +- 0.1 (the numerator pays the knock prior per object; the denominator,
    which drops mixture weights as truth-v1 drops 1 - RHO, is unchanged) - unless the rival's best fit takes a knock,
    which only raises its denominator (a rival explaining its misfit as a knock: power, not validity)."""
    throws, _ = _throws()
    k = len({t.situation for t in throws})
    law = grammar.canonical(LAW)
    q = {}
    for pol in ('throw', 'object'):
        q[pol] = {}
        for f in grammar.space():
            if f == law or not grammar.contains(f, law):
                q[pol][f] = _prequential(L.Model(*grammar.codes(f)), throws, pol, monkeypatch)
    rivals = sorted((f for f in q['throw'] if f != law), key=lambda f: -q['throw'][f][0])[:4]
    assert abs((q['object'][law][0] - q['throw'][law][0]) - k * math.log(0.95)) < 0.1
    for b in rivals:
        den = {}
        for pol in ('throw', 'object'):
            monkeypatch.setattr(L, 'KNOCK', pol)
            den[pol] = L.fit(L.Model(*grammar.codes(b)), throws, SIGMA, start=q[pol][b][1])
        assert den['throw'].ok and den['object'].ok
        assert den['object'].loglik >= den['throw'].loglik - 1e-6, grammar.name(b)
        d_e = (q['object'][law][0] - den['object'].loglik) - (q['throw'][law][0] - den['throw'].loglik)
        print(f'{grammar.name(b)}: log E {q["throw"][law][0] - den["throw"].loglik:.2f} -> '
              f'{q["object"][law][0] - den["object"].loglik:.2f} (knocks {den["object"].knocks})')
        if not den['object'].knocks:
            assert abs(den['object'].loglik - den['throw'].loglik) < 1e-6, grammar.name(b)
            assert abs(d_e - k * math.log(0.95)) < 0.1, (grammar.name(b), d_e)
        else:
            assert d_e <= k * math.log(0.95) + 0.1, (grammar.name(b), d_e)
