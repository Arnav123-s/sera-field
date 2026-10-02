"""T3-b4 (plan rev 3, T3 item 3; the author approved 2026-09-26): the universe audit's roots walked in parallel
processes and merged in the tree's order record exactly what the one-process walk records - the same rivals in the
same order, every e-value bit for bit, the same first law not ruled out and reason - on a world where the claim passes
(drag, pushes both ways), one where it is refused (forward pushes: |v| is v), and for a two-term claim (where a member
can come up under both terms and must be skipped the second time)."""
import numpy as np
import pytest

from ccops5.core import grammar, paths, truth, worlds as W

SIGMA = (0.001, 0.001)
DRAG = (('speed', 'straight'),)
SPRING_DRAG = grammar.canonical((('position', 'straight'), ('speed', 'straight')))
CASES = {'drag both ways': (DRAG, (-0.5,), (4.0, 0.3, -4.0, -0.3), DRAG),
         'drag forward only': (DRAG, (-0.5,), (4.0, 0.8, 0.3, 1.5), DRAG),
         'spring and drag': (SPRING_DRAG, (-2.0, -0.5), (4.0, -4.0), SPRING_DRAG)}


def _ledger(family, coef, pushes, seed=3, situations=3, hold=1.2):
    kk, aa, bb = grammar.codes(family)
    rng = np.random.default_rng(seed)
    ledger = truth.Ledger(grammar.space(), SIGMA)
    for k in range(situations):
        m = float(rng.uniform(0.6, 2.5))
        for j, u in enumerate(pushes):
            act = W.Action(((0.0, hold, float(u)),))
            xs, vs = paths.simulate_program(*act.arrays(), 1 / m, kk, aa, bb, np.array(coef), 1.0, 1.0, 0.0, 0.0)
            nr = np.random.default_rng([seed, k, j])
            ledger.add(W.Throw(k, len(ledger.throws), act, xs + nr.normal(0, 1e-3, xs.size),
                               vs + nr.normal(0, 1e-3, vs.size)))
    return ledger


def _committed_walk(ledger, family, thr):
    """universe_audit as committed in f14cb0c (one stack over all roots), verbatim but for module prefixes: the
    reference the refactored walk (_walk_root, root by root) must equal."""
    import math
    T = truth
    family = grammar.canonical(family)
    space = set(ledger.families)
    q_a = ledger.q_claim(family)
    mu = ledger.mle(family).mu
    bar = q_a - thr + 1e-6
    rivals = {}
    for a in family:
        stack = list(reversed(T.audit_tree(family, a)))
        while stack:
            node = stack.pop()
            U = T.audit_superset(node, a)
            if T.AUDIT_FAST:
                best = T._best_member(ledger, U, family)
                s = None if best is not None and best[1].loglik > bar else T.audit_fit(ledger, U, mu, family, bar)
            else:
                s = T.audit_fit(ledger, U, mu, family)
            if s is not None and T._usable(s) and q_a - s.loglik >= thr:
                rivals[U] = q_a - s.loglik
                continue
            kids = T.audit_children(node)
            if kids:
                stack += list(reversed(kids))
                continue
            for f in T.audit_members(node[0], a):
                if f in space or f in rivals or grammar.log_prior(f) == -math.inf or grammar.contains(f, family):
                    continue
                s = T.audit_fit(ledger, f, mu, family)
                if not T._usable(s):
                    rivals[f] = -math.inf
                    return rivals, f, 'failed'
                rivals[f] = q_a - s.loglik
                if rivals[f] < thr:
                    return rivals, f, 'weak'
    return rivals, None, None


def _fold_roots(ledger, family, thr):
    """Fold the extracted walk in canonical claim-term and original root order."""
    family = grammar.canonical(family)
    space = set(ledger.families)
    q_a = ledger.q_claim(family)
    mu = ledger.mle(family).mu
    bar = q_a - thr + 1e-6
    rivals = {}
    for a in family:
        known = frozenset(rivals)  # snapshot BEFORE this term, shared by all its roots
        for root in truth.audit_tree(family, a):
            part, weak, why = truth._walk_root(ledger, family, a, root, mu, q_a, thr, bar, space, known)
            rivals.update(part)
            if weak is not None:
                return rivals, weak, why
    return rivals, None, None


def _assert_outcome(case, weak, why):
    if case == 'drag forward only':
        assert weak == (('piece', 'speed', 'abs', 0.0),), (weak, why)
        assert why == 'weak', why
    else:
        assert (weak, why) == (None, None), (case, weak, why)


def _compare_refactored(case):
    family, coef, pushes, claim = CASES[case]
    claim = grammar.canonical(claim)
    thr = grammar.log_threshold(claim, 1e-3)
    ref = _committed_walk(_ledger(family, coef, pushes), claim, thr)
    new = _fold_roots(_ledger(family, coef, pushes), claim, thr)
    assert list(new[0]) == list(ref[0]) and all(new[0][b] == ref[0][b] for b in ref[0]), case
    assert new[1:] == ref[1:], case
    _assert_outcome(case, *new[1:])


@pytest.mark.parametrize('case', list(CASES))
def test_the_refactored_walk_equals_the_committed_one(case, small_audit_universe):
    _compare_refactored(case)


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.parametrize('case', list(CASES))
def test_full_universe_refactored_walk_equivalence(case, full_audit_universe):
    _compare_refactored(case)


def _compare_parallel(case):
    family, coef, pushes, claim = CASES[case]
    claim = grammar.canonical(claim)
    thr = grammar.log_threshold(claim, 1e-3)
    one = truth.universe_audit(_ledger(family, coef, pushes), claim, thr, workers=0)
    many = truth.universe_audit(_ledger(family, coef, pushes), claim, thr, workers=4)
    (r1, w1, y1), (r4, w4, y4) = one, many
    assert list(r4) == list(r1), case
    assert all(r4[b] == r1[b] for b in r1), case
    assert (w4, y4) == (w1, y1), case
    _assert_outcome(case, w4, y4)
    print(f'{case}: {len(r1)} rivals; first not ruled out: {grammar.name(w1) if w1 else None} ({y1})')


@pytest.mark.parametrize('case', list(CASES))
def test_the_parallel_walk_records_exactly_what_one_process_does(case, small_audit_universe):
    _compare_parallel(case)  # workers=4 above: real processes, no pool stub


@pytest.mark.slow
@pytest.mark.integration
@pytest.mark.parametrize('case', list(CASES))
def test_full_universe_parallel_walk_equivalence(case, full_audit_universe):
    _compare_parallel(case)
