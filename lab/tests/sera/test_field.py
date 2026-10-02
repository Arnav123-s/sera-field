"""SERA v4's Field, the exact part (docs/SERA_FIELD_THEORY.md v1.1 §3-5): belief over every law on one fidelity-0
scale, the floor outside the joint, and the faded Polya-tree memory. Written before the code.
  - each law's evidence equals the direct Gaussian marginal (explicit covariance) - exact, not an estimate;
  - belief is normalized, and on a clean world the true law leads;
  - the floor: p_F(h) >= eta * pi0(h) however the memory leans, and Proposition 2's odds bound holds;
  - the memory is normalized at every node, equals pi0 with no counts, and fades by the weight law
    w_k = g^k C / (a0 + g^k C); a far context leaves it unchanged;
  - a refuted law's belief falls by the evidence (no trace code).
"""
import math

import numpy as np

from ccops5.core import grammar, paths, worlds as W
from sera import compact as C, field as F

SIGMA = (0.001, 0.001)


def _synthetic(n=30, seed=0):
    rng = np.random.default_rng(seed)
    Phi = rng.normal(size=(n, 3))
    d = rng.uniform(0.5, 2.0, size=n)
    z = Phi[:, :2] @ np.array([1.5, -0.7]) + rng.normal(size=n) * np.sqrt(d)
    return Phi, d, z


def _direct(Phi, d, z, idx, s_c):
    S = Phi[:, idx]
    cov = np.diag(d) + s_c ** 2 * S @ S.T
    sign, logdet = np.linalg.slogdet(cov)
    return -0.5 * (len(z) * math.log(2 * math.pi) + logdet + z @ np.linalg.solve(cov, z))


def test_the_evidence_is_the_exact_gaussian_marginal():
    Phi, d, z = _synthetic()
    st = F.Stats.from_arrays(Phi, d, z)
    for idx in ([], [0], [2], [0, 1], [1, 2]):
        assert abs(F.log_marginal(st, idx) - _direct(Phi, d, z, idx, F.S_C)) < 1e-8, idx


def _throws(family, coef, situations=4, pushes=(1.0, -0.6, 0.6), seed=2):
    kk, aa, bb = grammar.codes(family)
    rng = np.random.default_rng(seed)
    out, mu = [], {}
    for k in range(situations):
        m = float(rng.uniform(0.6, 2.5))
        mu[k] = 1 / m
        for j, u in enumerate(pushes):
            xs, vs = paths.simulate(W.hand(u), 1 / m, kk, aa, bb, np.array(coef), 1.0, 1.0, 0.0, 0.0)
            nr = np.random.default_rng([seed, k, j])
            out.append(W.Throw(k, len(out), W.push_of(u), xs + nr.normal(0, 1e-3, xs.size),
                               vs + nr.normal(0, 1e-3, vs.size)))
    return out, mu


def test_belief_is_normalized_and_the_truth_leads_on_a_clean_world():
    truth = grammar.canonical((('position', 'straight'), ('speed', 'straight')))
    throws, mu = _throws(truth, [-2.0, -0.8])
    log_b = F.belief(F.evidence(throws, mu), F.prior_logp())
    assert len(log_b) == 3175
    assert abs(np.logaddexp.reduce(list(log_b.values()))) < 1e-9
    best = max(log_b, key=log_b.get)
    assert best == truth, grammar.name(best)


def test_the_floor_holds_however_the_memory_leans():
    laws = F.LAWS
    lean = {h: (50.0 if h == laws[5] else 0.0) for h in laws}      # a memory sure of one law
    p = F.with_floor(F.normalize(lean))
    pi0 = F.prior_logp()
    assert all(p[h] >= math.log(F.ETA) + pi0[h] - 1e-12 for h in laws)
    assert abs(np.logaddexp.reduce(list(p.values()))) < 1e-9


def test_proposition_2_odds_bound():
    truth = grammar.canonical((('position', 'straight'), ('speed', 'straight')))
    throws, mu = _throws(truth, [-2.0, -0.8])
    st = F.evidence(throws, mu)
    laws = F.LAWS
    wrong = laws[7]
    lean = {h: (80.0 if h == wrong else 0.0) for h in laws}        # a memory that strongly prefers a wrong law
    p = F.with_floor(F.normalize(lean))
    log_b = F.belief(st, p)
    lm = {h: F.law_log_marginal(st, h) for h in (truth, wrong)}
    pi0 = F.prior_logp()
    bound = lm[truth] - lm[wrong] - (-math.log(F.ETA) - pi0[truth])
    assert log_b[truth] - log_b[wrong] >= bound - 1e-6


def test_the_memory_is_normalized_and_starts_at_pi0():
    mem = F.Memory()
    p = mem.log_prior(context=np.zeros(F.CONTEXT_DIM))
    assert abs(np.logaddexp.reduce(list(p.values()))) < 1e-9
    pi0 = F.normalize(F.prior_logp())
    assert max(abs(p[h] - pi0[h]) for h in F.LAWS) < 1e-9


def test_the_memory_fades_by_the_weight_law():
    mem = F.Memory(alpha0=1.0, half_life=2.0)
    c = np.zeros(F.CONTEXT_DIM)
    law = F.LAWS[100]
    onehot = {h: (0.0 if h == law else -math.inf) for h in F.LAWS}
    for _ in range(5):
        mem.add_world(c, onehot)
    node = F.path(law)[:1]
    C0 = mem.count(node, c)
    g = 2 ** (-1 / 2.0)
    for k in range(1, 6):
        mem.fade()
        assert abs(mem.count(node, c) - g ** k * C0) < 1e-9 * max(1.0, C0)
        w = mem.weight(node, c)
        assert abs(w - g ** k * C0 / (1.0 + g ** k * C0)) < 1e-9


def test_a_far_context_is_unchanged():
    mem = F.Memory()
    near, far = np.zeros(F.CONTEXT_DIM), np.full(F.CONTEXT_DIM, 100.0)
    law = F.LAWS[100]
    mem.add_world(near, {h: (0.0 if h == law else -math.inf) for h in F.LAWS})
    p_far = mem.log_prior(context=far)
    pi0 = F.normalize(F.prior_logp())
    assert abs(p_far[law] - pi0[law]) < 1e-9
    assert mem.log_prior(context=near)[law] > pi0[law] + 0.1


def test_a_refuted_law_falls_by_the_evidence():
    truth = grammar.canonical((('position', 'straight'), ('speed', 'straight')))
    throws, mu = _throws(truth, [-2.0, -0.8])
    rival = grammar.canonical((('position', 'cubic'), ('speed', 'straight')))
    early = F.belief(F.evidence(throws[:2], mu), F.prior_logp())
    late = F.belief(F.evidence(throws, mu), F.prior_logp())
    assert late[rival] - late[truth] < early[rival] - early[truth]
    assert late[rival] - late[truth] < -20


# --- dreams, curiosity and the action language (§6-8) ---

def test_dreams_follow_the_belief_and_the_posterior():
    truth = grammar.canonical((('position', 'straight'), ('speed', 'straight')))
    throws, mu = _throws(truth, [-2.0, -0.8])
    st = F.evidence(throws, mu)
    log_b = F.belief(st, F.prior_logp())
    ds = F.dreams(np.random.default_rng(0), st, log_b, 64)
    assert sum(h == truth for h, _ in ds) >= 60
    m, _ = F.posterior(st, truth)
    assert np.allclose(np.mean([c for h, c in ds if h == truth], axis=0), m, atol=0.05)
    fuzzy = F.dreams(np.random.default_rng(0), st, log_b, 64, beta=0.0)          # beta 0: the prior's spread
    assert len({h for h, _ in fuzzy}) > 30


def test_box_hill_is_zero_for_twins_and_grows_with_the_gap_a_refit_cannot_close():
    y = np.zeros(82)
    small = np.zeros((82, 82))
    assert F.box_hill([(y, small), (y, small)], [0.5, 0.5], SIGMA) < 1e-9
    y2 = y.copy()
    y2[:41] += 0.01                                                   # 10 sigma apart in position
    d_far = F.box_hill([(y, small), (y2, small)], [0.5, 0.5], SIGMA)
    assert d_far > 1.0
    u = (y2 - y) / np.linalg.norm(y2 - y)
    refit = 1e-3 * np.outer(u, u)                  # both laws' strengths are uncertain along the gap: either can
    assert F.box_hill([(y, refit), (y2, refit)], [0.5, 0.5], SIGMA) < 0.2 * d_far       # re-fit to the other


def test_the_action_code_satisfies_kraft_and_programs_stay_in_the_language():
    n_t = int(round(2.0 / F.T_STEP)) + 1
    kraft = sum((n_t * n_t * len(F.U_LEVELS)) ** k * 2.0 ** -F.code_length(
        W.Action(tuple((0.0, 0.1, F.U_LEVELS[0]) for _ in range(k)))) for k in range(1, F.MAX_SEGMENTS + 1))
    assert kraft <= 1.0
    rng = np.random.default_rng(3)
    def disjoint(p):                               # independent review review: overlapping segments add past the hand's |u| <= 1
        s = sorted(p.segments)
        return all(s[i][1] <= s[i + 1][0] for i in range(len(s) - 1))
    for p in F.sample_programs(rng, 200):
        assert 1 <= len(p.segments) <= F.MAX_SEGMENTS
        assert all(0.0 <= s[0] < s[1] <= 2.0 and s[2] in F.U_LEVELS for s in p.segments) and disjoint(p)
        for _ in range(5):
            q = F.mutate(rng, p)
            assert 1 <= len(q.segments) <= F.MAX_SEGMENTS and all(0.0 <= s[0] < s[1] <= 2.0 for s in q.segments)
            assert disjoint(q)


def test_the_truths_predictive_matches_the_simulator():
    truth = grammar.canonical((('position', 'straight'), ('speed', 'straight')))
    throws, mu = _throws(truth, [-2.0, -0.8])
    st = F.evidence(throws, mu)
    a = W.Action(((0.0, 0.4, 1.0),))
    y, S = F.predictive(st, truth, a, mu[0])
    xs, vs = paths.simulate_program(*a.arrays(), mu[0], *grammar.codes(truth), np.array([-2.0, -0.8]), 1.0, 1.0,
                                    0.0, 0.0)
    assert np.max(np.abs(y - np.concatenate([xs, vs]))) < 0.01
    assert S.shape == (82, 82) and np.all(np.linalg.eigvalsh(S) > -1e-12)
