"""T2 (independent review review of truth-v2, 20:50): a grown formula claim must rule out every law of one wide term (alone or
with one base idea) sharing a part with it, not only the few rivals in the formula ledger. Written before the fix.

  duplicate world: force -1.5 * exp(-x^2) * v, every push forward, so v >= 0 on every reading and
                   exp(-x^2) * |v| is the same law there -> the claim exp(-x^2) * v must NOT be certified
                   (on bcc4081 nothing outside the ledger is weighed, so no rival stands in the way)
  control world:   the same law with pushes both ways (|v| and v differ) -> the claim certifies
Also: the wide rivals' fits start where the robust likelihood is flat (every throw a bump), so a lone start could
understate a rival's best fit; sup_fit must reach the ledger's own best fit of the true law.
"""
import numpy as np
import pytest

from ccops5.core import grammar, likelihood as L, paths, truth, worlds as W

CLAIM = ('pprod', 'bell1', 'straight')
TWIN = ('pprod', 'bell1', 'abs')
SIGMA = (0.001, 0.001)


def _world(pushes, seed=5, situations=6, coef=-1.5):
    kk, aa, bb = grammar.codes((CLAIM,))
    rng = np.random.default_rng(seed)
    throws = []
    for k in range(situations):
        m = float(rng.uniform(0.6, 2.5))
        for j, u in enumerate(pushes):
            xs, vs = paths.simulate(W.hand(u), 1 / m, kk, aa, bb, np.array([coef]), 1.0, 1.0, 0.0, 0.0)
            nr = np.random.default_rng([seed, k, j])
            throws.append(W.Throw(k, len(throws), W.push_of(u), xs + nr.normal(0, 1e-3, xs.size),
                                  vs + nr.normal(0, 1e-3, vs.size)))
    return throws


def _ledger(throws):
    ledger = truth.Ledger(grammar.space() + [(CLAIM,)], SIGMA)
    for t in throws:
        ledger.add(t)
    return ledger


def test_the_twin_is_a_wide_rival():
    assert TWIN in truth.wide_terms((CLAIM,))
    assert CLAIM not in truth.wide_terms((CLAIM,))


@pytest.mark.slow
def test_sup_fit_reaches_the_best_fit_from_a_flat_start():
    ledger = _ledger(_world((1.0, 0.6, -1.0, -0.6)))
    best = ledger.mle((CLAIM,))
    far = {s: 1.0 for s in best.mu}                         # every throw starts as a bump under these masses
    got = L.sup_fit(truth.model_of((CLAIM,)), ledger.throws, SIGMA, far)
    assert got.loglik >= best.loglik - 1.0, (got.loglik, best.loglik)


@pytest.mark.slow
def test_an_exact_twin_outside_the_ledger_blocks_the_claim():
    ledger = _ledger(_world((1.0, 0.6, 1.5, 0.8)))
    assert min(float(t.v.min()) for t in ledger.throws) > -0.01           # forward only (up to sensor noise)
    cert = truth.certify(ledger, (CLAIM,), 0.2)
    assert not cert.accepted
    assert any('abs of speed' in r for r in cert.reasons), cert.reasons


@pytest.mark.slow
def test_control_with_both_signs_certifies():
    # Speeds must reach where v and 2 tanh(v/2) part. 2026-09-24: with pushes of +-1 / +-0.6, then +-2 / +-1.2 (|v| <=
    # 1.16), the rival cubic(v) + exp(-x^2) * tanh(v/2) fitted within noise (per-throw RMS 1.02 sigma against 0.98):
    # its MLE was 52 nats behind the claim, while the claim's prequential score pays 63 nats of regret (1 coefficient
    # + 6 masses), so log E = -11.6. The power cost of universal inference, not a validity issue: the judge was right.
    # With +-4 / +-2.5 and 8 objects it still held: every throw starts at rest at x = 0 and the drag (-1.5) slows it
    # inside the bell, so |v| <= 1.18 wherever exp(-x^2) > 0.5 (1,212 of 1,312 readings). FROZEN here (independent review): a
    # weaker drag (-0.5) lets the pushes carry |v| to about 2.7 inside the bell, where v and 2 tanh(v/2) part.
    cert = truth.certify(_ledger(_world((4.0, 2.5, -4.0, -2.5), situations=8, coef=-0.5)), (CLAIM,), 0.2)
    assert cert.accepted, cert.reasons


# independent review of ab56937 (m1b 4ad835c): T2-A (a failed fit counted as ruled out), T2-B (an unconverged fit
# counted), T2-C (embedded starts). Written before the fix.
import math                                                   # noqa: E402


class _FakeLedger:
    """What wide_rivals reads, with every wide rival's fit replaced by `fit`."""

    def __init__(self, fit):
        self.families = grammar.space() + [(CLAIM,)]
        self.Q = {f: -1e9 for f in self.families}                   # a real ledger scores every family it holds
        self.Q[(CLAIM,)] = 0.0
        self._mle = {}
        self._fit = fit

    def mle(self, family):
        return L.Fit(np.zeros(grammar.n_coef(family)), {0: 1.0}, None, [0], -1e9, True, True)

    def best_family(self):
        return (CLAIM,)

    def q_claim(self, family):                                     # truth-v2 N-2: the claim's numerator
        return self.Q[grammar.canonical(family)]

    def sup(self, family, mu, starts=()):
        return self._fit


def test_a_failed_rival_fit_never_rules_it_out():
    failed = L.Fit(np.zeros(1), {0: 1.0}, None, [0], -math.inf, False, False)
    rivals, f, why = truth.wide_rivals(_FakeLedger(failed), (CLAIM,), 18.5)
    assert why == 'failed' and f is not None and rivals[f] == -math.inf


def test_an_unconverged_rival_fit_never_rules_it_out():
    stalled = L.Fit(np.zeros(1), {0: 1.0}, None, [0], -1e9, True, False)     # would look ruled out by 1e9 units
    rivals, f, why = truth.wide_rivals(_FakeLedger(stalled), (CLAIM,), 18.5)
    assert why == 'failed'


def test_an_embedded_start_keeps_a_rival_at_least_as_good_as_the_law_it_contains():
    ledger = truth.Ledger([(CLAIM,)], SIGMA)
    for t in _world((1.0, 0.6, -1.0, -0.6)):
        ledger.add(t)
    inner = ledger.mle((CLAIM,))
    outer = grammar.canonical((CLAIM, ('speed', 'cubic')))
    got = ledger.sup(outer, inner.mu, truth.embedded_starts(ledger, outer))
    assert got.ok and got.loglik >= inner.loglik - 1e-6, (got.loglik, inner.loglik)



def test_embedded_starts_depend_on_the_throws_only():
    """independent review R-1: the starts (hence the wide-rival e-values) must not depend on which fits earlier calls left in
    the ledger's cache, or the mind's certificate and the checker's fresh re-derivation could disagree."""
    throws = _world((1.0, 0.6, -1.0, -0.6))
    fresh, used = _ledger(throws), _ledger(throws)
    for f in used.families[:25]:                                    # unrelated fits first
        used.mle(f)
    outer = grammar.canonical((CLAIM, ('speed', 'cubic')))
    a, b = truth.embedded_starts(fresh, outer), truth.embedded_starts(used, outer)
    assert len(a) == len(b) and all(np.array_equal(x.mean, y.mean) and x.order == y.order for x, y in zip(a, b))


def test_a_fit_already_at_its_optimum_counts_as_converged():
    """independent review R-3: restarting at the optimum, every step is float noise; that is stationary, not 'failed'."""
    ledger = truth.Ledger([(CLAIM,)], SIGMA)
    for t in _world((1.0, 0.6, -1.0, -0.6)):
        ledger.add(t)
    best = ledger.mle((CLAIM,))
    again = L.fit(truth.model_of((CLAIM,)), ledger.throws, SIGMA,
                  start=L.Post(np.concatenate([best.coef, [best.mu[s] for s in best.order]]),
                               np.eye(1 + len(best.order)), best.order), iters=40)
    assert again.ok and again.converged and abs(again.loglik - best.loglik) < 1e-6
