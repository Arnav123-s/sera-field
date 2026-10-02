"""Decision 6 (2026-09-25; found in B3 world L1-07, verified by independent review): the adequacy test counts misfit per
SITUATION, not per throw.

A world bump is drawn per situation and repeats on every push of that situation (worlds.World.push). So a mind that
keeps pushing one bumped object makes most THROWS misfit while the law is true. In L1-07, 24 of 26 throws on one
bumped situation gave log e = 23.2 >= log(67 / alpha) = 11.1, a false alarm on the true law. independent review computed
P(false alarm) = 5.8e-3 > alpha for M1's worst case under the per-throw count, and 3.9e-11 at 8 situations under the
per-situation count (bumps i.i.d. per situation, independent of the mind). Written before the fix."""
import math

import numpy as np

from ccops5.core import grammar, paths, truth, worlds as W

DRAG = (('speed', 'straight'),)
SIGMA = (0.001, 0.001)


def _throws(bumped, pushes_on_bumped, situations=8, seed=11):
    kk, aa, bb = grammar.codes(grammar.canonical(DRAG))
    rng = np.random.default_rng(seed)
    out = []
    for k in range(situations):
        m = float(rng.uniform(0.6, 2.5))
        n = pushes_on_bumped if k in bumped else 2
        for j in range(n):
            u = (1.0, -1.0, 0.6, -0.6)[j % 4]
            t0, amp = (0.8, 1.5) if k in bumped else (0.0, 0.0)
            xs, vs = paths.simulate(W.hand(u), 1 / m, kk, aa, bb, np.array([-1.0]), 1.0, 1.0, t0, amp)
            nr = np.random.default_rng([seed, k, j])
            out.append(W.Throw(k, len(out), W.push_of(u), xs + nr.normal(0, 1e-3, xs.size),
                               vs + nr.normal(0, 1e-3, vs.size)))
    return out


def _adequacy(throws):
    ledger = truth.Ledger(grammar.space(), SIGMA)
    for t in throws:
        ledger.add(t)
    return truth.adequacy(ledger, grammar.canonical(DRAG))


THRESHOLD = math.log(grammar.ADEQUACY_THRESHOLD_SPACE / 1e-3)


def test_one_knocked_object_pushed_many_times_is_no_alarm_on_the_true_law():
    assert _adequacy(_throws(bumped={6}, pushes_on_bumped=24)) < THRESHOLD


def test_most_objects_misfitting_still_fire():
    assert _adequacy(_throws(bumped={0, 1, 2, 3, 4, 5, 6, 7}, pushes_on_bumped=2)) >= THRESHOLD
