"""SERA v3 worlds: deterministic, valid, certifiable by the frozen judge, and the held-out split is respected."""
import numpy as np

from ccops5.core import grammar, truth
from sera import lawspace as LS, worlds as SW


def test_deterministic():
    a, b = SW.make(3, 5, 2), SW.make(3, 5, 2)
    assert a.spec.family == b.spec.family and a.spec.coefs == b.spec.coefs
    assert all(np.array_equal(s.x, t.x) and np.array_equal(s.v, t.v) for s, t in zip(a.throws, b.throws))


def test_levels_valid_and_certifiable():
    for level in range(6):
        for i in range(3):
            w = SW.make(2, i, level)
            assert SW.validate(w) == (True, 'ok')
            assert LS.claimable(w.spec.family)
            if level <= 4:
                assert LS.level(w.spec.family) == level
            assert tuple(w.truth) == tuple(w.spec.family)


def test_held_out_split():
    rng = np.random.default_rng(0)
    for level in (2, 3, 4):
        for _ in range(200):
            assert not SW.held_out(SW.sample_law(rng, level, 'dream'))
        for _ in range(20):
            assert SW.held_out(SW.sample_law(rng, level, 'held'))


def test_judge_ranks_the_truth_first_on_a_small_world():
    """The frozen judge's own evidence prefers the true law on a generated world (3 objects, 6 throws)."""
    w = SW.make(4, 0, 1, situations=3)
    ledger = truth.Ledger(grammar.space(), w.sigma)
    for t in w.throws:
        ledger.add(t)
    assert ledger.best_family() == grammar.canonical(w.spec.family)


def test_identifiability_rule():
    """Base laws: every sub-law misses by EFFECT; invented laws: every other certifiable law of no more terms does."""
    for level, split in ((2, 'dream'), (3, 'dream'), (4, 'held')):
        w = SW.make(3, 40, level, split)
        xs, vs, ts = SW._states(w)
        fam = tuple(w.spec.family)
        if level == 2:
            for i in range(len(fam)):
                assert w._best_fit_gap(fam[:i] + fam[i + 1:], xs, vs, ts) >= SW.EFFECT
        else:
            gaps = SW.rival_gaps(w, xs, vs, ts)
            assert min(gaps.values()) >= SW.EFFECT
            assert w._best_fit_gap(fam, xs, vs, ts) < 1e-6          # the truth itself fits exactly
