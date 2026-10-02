"""A life must never crash on a posterior that cannot be inverted (T-S on Colab, 2026-09-26: world s1-i9107-L3 died
with LinAlgError 'Singular matrix' in likelihood._laplace; the same life ran clean on the laptop, so it hangs on
floating-point rounding). The cause: when the update prec2 could not be solved, the old code kept the old mean but
stored the singular prec2, and the object's next throw inverted it. Now:
- an update that cannot be solved teaches nothing: the posterior stays as it was (mean and precision);
- a clean forecast that cannot be formed (a posterior that cannot be inverted, or a non-finite Laplace score) is a
  ZERO clean component (log q_clean = -inf), never a small constant. the reviewer's review V395 ((review notes, not published)): the
  first version returned -1e12 for every reading y, and (1-rho) e^-1e12 + rho phi(y) integrates to infinity over
  the unbounded readings, so it was not a sub-density; the far-reading test below fails on that version.
- a failed mass option, knock branch or exact-numerator component drops out of its mixture; when every component
  fails, the throw is scored by the outlier density alone and the posterior is left unchanged."""
import math

import numpy as np

from ccops5.core import grammar, likelihood as L, paths, truth, worlds as W

SIGMA = (0.001, 0.001)
DRAG = (('speed', 'straight'),)


def _throw(k=0, u=4.0, coef=(-0.5,), m=1.3, seed=7):
    kk, aa, bb = grammar.codes(DRAG)
    act = W.Action(((0.0, 1.2, u),))
    xs, vs = paths.simulate_program(*act.arrays(), 1 / m, kk, aa, bb, np.array(coef), 1.0, 1.0, 0.0, 0.0)
    rng = np.random.default_rng(seed)
    return W.Throw(k, 0, act, xs + rng.normal(0, 1e-3, xs.size), vs + rng.normal(0, 1e-3, vs.size))


def _far(throw, by=5e5):
    """The same throw with readings so far off that the outlier density is below e^-1e12 (about e^-1e13 here, where
    floating point still resolves hundredths of a nat)."""
    return W.Throw(throw.situation, throw.index, throw.action, throw.x + by, throw.v + by)


def _singular(model, known=(0,)):
    nc = model.n_coef
    n = nc + len(known)
    return L.Post(np.concatenate([[-0.5] * nc, [0.8] * len(known)]), np.zeros((n, n)), list(known))


def test_an_update_that_cannot_be_solved_keeps_the_whole_posterior(monkeypatch):
    model = truth.model_of(DRAG)
    post = L.empty_post(model)
    throw = _throw()

    def fail(*a, **k):
        raise np.linalg.LinAlgError('Singular matrix')
    monkeypatch.setattr(L.np.linalg, 'solve', fail)
    log_q, updated = L._laplace(model, post, throw, SIGMA, None, 30)
    prior = np.diag([L.COEF_PRIOR_SD ** -2] * model.n_coef + [L.MU_PRIOR[1] ** -2])
    assert np.isfinite(log_q)                             # the forecast was formed; only the update failed
    assert np.array_equal(updated.prec, prior)            # before: prior + the throw's information, singular or not
    assert np.array_equal(updated.mean, np.array([0.0] * model.n_coef + [L.MU_PRIOR[0]]))   # the augmented prior
    assert updated.order == [throw.situation]


def test_a_retained_failed_update_is_followed_by_an_ordinary_throw(monkeypatch):
    model = truth.model_of(DRAG)

    def fail(*a, **k):
        raise np.linalg.LinAlgError('Singular matrix')
    monkeypatch.setattr(L.np.linalg, 'solve', fail)
    _, post1 = L._laplace(model, L.empty_post(model), _throw(), SIGMA, None, 30)    # the failed update, retained
    monkeypatch.undo()
    assert post1.order == [0]
    q2, post2 = L.step(model, post1, _throw(seed=8), SIGMA)
    assert np.isfinite(q2) and post2.order == [0]
    assert np.all(np.linalg.eigvalsh(post2.prec) > 0)


def test_a_posterior_that_cannot_be_inverted_is_a_zero_clean_component():
    model = truth.model_of(DRAG)
    post = _singular(model)
    throw = _throw()
    log_q, updated = L._laplace(model, post, throw, SIGMA, None, 30)          # before 395ad6b: LinAlgError
    assert log_q == -math.inf and updated is post
    q, kept = L.step(model, post, throw, SIGMA)
    assert q == L.log_outlier(throw) and kept is post


def test_far_readings_are_scored_by_the_outlier_density_alone():
    """V395's critical case: a constant clean floor would dominate here (395ad6b gave log(1-rho) - 1e12)."""
    model = truth.model_of(DRAG)
    far = _far(_throw())
    b = L.log_outlier(far)
    assert b < math.log(1 - L.RHO) - 1e12
    q, kept = L.step(model, _singular(model), far, SIGMA)
    assert q == b


def test_a_failed_mass_option_drops_out_of_the_new_object_mixture(monkeypatch):
    model = truth.model_of(DRAG)
    _, post = L.step(model, L.empty_post(model), _throw(k=0), SIGMA)         # one object met: two options for a new one
    new = _throw(k=1, seed=9)
    real = L._laplace

    def only_broad(model_, post_, throw_, sigma_, mu_prior, iters):
        if mu_prior is not None:
            return -math.inf, post_                   # the familiar-mass option cannot be formed
        return real(model_, post_, throw_, sigma_, mu_prior, iters)
    monkeypatch.setattr(L, '_laplace', only_broad)
    clean, updated = L._clean_step(model, post, new, SIGMA, 30)
    q_broad, broad = real(model, post, new, SIGMA, None, 30)
    n_familiar = sum(n for _, n in L.familiar_masses(model, post))
    assert clean == math.log(1.0 / (1.0 + n_familiar)) + q_broad
    assert updated.order == broad.order and np.array_equal(updated.mean, broad.mean)


def test_every_mass_option_failing_gives_no_clean_density_and_no_nan():
    model = truth.model_of(DRAG)
    post = _singular(model)                          # object 0 met; a throw of object 1 has two options, both fail
    new = _throw(k=1)
    clean, updated = L._clean_step(model, post, new, SIGMA, 30)
    assert clean == -math.inf and updated is post
    q, kept = L.step(model, post, new, SIGMA)
    assert q == L.log_outlier(new) and kept is post


def test_failed_knock_branches_carry_only_the_outlier_density(monkeypatch):
    monkeypatch.setattr(L, 'KNOCK', 'object')
    model = truth.model_of(DRAG)
    post = _singular(model)
    far = _far(_throw())
    q, kept = L.step(model, post, far, SIGMA)
    kept_w = np.array([w for w in L.KNOCK_LOGP if w >= L.KNOCK_KEEP])
    assert abs(q - (L.log_outlier(far) + float(np.log(np.exp(kept_w).sum())))) <= 0.01
    assert q < math.log(1 - L.RHO) - 1e12                  # no clean floor survives in any branch
    assert kept.mean is post.mean and kept.prec is post.prec


def test_a_failed_knock_branch_beside_a_working_one(monkeypatch):
    """V395b: branch 0 (no knock) forms its forecast; every knocked branch fails and carries only the outlier."""
    monkeypatch.setattr(L, 'KNOCK', 'object')
    model = truth.model_of(DRAG)
    _, post = L.step(model, L.empty_post(model), _throw(), SIGMA)
    throw = _throw(seed=8)
    real = L._clean_step
    calls = []

    def only_first(model_, post_, throw_, sigma_, iters):
        calls.append(1)
        return real(model_, post_, throw_, sigma_, iters) if len(calls) == 1 else (-math.inf, post_)
    monkeypatch.setattr(L, '_clean_step', only_first)
    q, kept = L.step(model, post, throw, SIGMA)
    clean0, _ = real(model, post, L.knocked(throw, 0), SIGMA, 30)
    lp = post.knock.get(throw.situation, L.KNOCK_LOGP)
    b = L.log_outlier(throw)
    parts = [lp[0] + L._lse2(math.log(1 - L.RHO) + clean0, b)] + [w + b for w in lp[1:] if w >= L.KNOCK_KEEP]
    assert np.isfinite(q) and abs(q - float(np.logaddexp.reduce(parts))) <= 1e-9
    assert all(np.isfinite(v) or v == -math.inf for v in kept.knock[throw.situation])


def test_a_reading_beyond_floating_point_scores_zero_not_nan(monkeypatch):
    """V395b: readings near 1e155 overflow y @ y, so the outlier part is -inf too; the throw must score -inf (q = 0),
    never nan, and leave the posterior unchanged - in both knock modes and through the ledger."""
    model = truth.model_of(DRAG)
    post = _singular(model)
    huge = _far(_throw(), by=1e155)
    assert L.log_outlier(huge) == -math.inf
    q, kept = L.step(model, post, huge, SIGMA)
    assert q == -math.inf and kept is post
    fam = grammar.canonical(DRAG)
    led = truth.Ledger([fam], SIGMA)
    led.post[fam] = post
    led.add(huge)
    assert led.Q[fam] == -math.inf
    monkeypatch.setattr(L, 'KNOCK', 'object')
    q, kept = L.step(model, post, huge, SIGMA)
    assert q == -math.inf and kept is post


def test_the_exact_numerator_drops_a_component_it_cannot_form():
    model = truth.model_of(DRAG)
    post = _singular(model)
    new = _throw(k=1)                                # before: _local_prior's inverse raised, or order.index did
    for how in ('lattice', 'mu'):
        q, kept = L.step_exact(model, post, new, SIGMA, how)
        assert q == L.log_outlier(new) and kept is post, how


def test_the_ledger_path_scores_a_failed_forecast_by_the_outlier_density():
    fam = grammar.canonical(DRAG)
    led = truth.Ledger([fam], SIGMA)
    led.post[fam] = _singular(led._models[fam])
    far = _far(_throw())
    led.add(far)
    assert led.Q[fam] == L.log_outlier(far)


def test_a_zero_clean_part_never_selects_its_update(monkeypatch):
    """V395c 1: when the clean part is zero but _clean_step still hands back a DIFFERENT updated posterior, and the
    outlier part is zero too, both knock modes score -inf and keep the original posterior."""
    model = truth.model_of(DRAG)
    post = L.empty_post(model)
    other = L.Post(np.ones(model.n_coef + 1), np.eye(model.n_coef + 1), [0])
    monkeypatch.setattr(L, '_clean_step', lambda *a, **k: (-math.inf, other))
    monkeypatch.setattr(L, 'log_outlier', lambda t: -math.inf)
    for knock in ('throw', 'object'):
        monkeypatch.setattr(L, 'KNOCK', knock)
        q, kept = L.step(model, post, _throw(), SIGMA)
        assert q == -math.inf, knock
        assert kept.mean is post.mean and kept.order == post.order, knock


def test_the_exact_numerator_drops_an_unextended_guide(monkeypatch):
    """V395c 2: with the past invertible (_local_prior succeeds) but _laplace unable to extend the posterior to a new
    object, both exact modes drop that component, so the throw is scored by the outlier density alone."""
    model = truth.model_of(DRAG)
    post = L.empty_post(model)
    new = _throw(k=3)
    real = L._laplace
    monkeypatch.setattr(L, '_laplace', lambda m, p, t, s, prior, it: (real(m, p, t, s, prior, it)[0], p))
    for how in ('lattice', 'mu'):
        q, _ = L.step_exact(model, post, new, SIGMA, how)
        assert q == L.log_outlier(new), how


def test_a_huge_reading_through_prequential_and_the_rival_evidence():
    """V395c 3: a reading beyond floating point scores -inf (not nan) through truth.prequential, and a rival whose
    best fit breaks down on it is never ruled out (log E = -inf, not +inf or nan)."""
    fam = grammar.canonical(DRAG)
    huge = _far(_throw(), by=1e155)
    q, _ = truth.prequential(truth.model_of(fam), [huge], SIGMA)
    assert q == -math.inf
    rival = grammar.canonical((('position', 'straight'),))
    led = truth.Ledger([fam, rival], SIGMA)
    led.add(huge)
    assert led.log_e(fam, rival) == -math.inf
