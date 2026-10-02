"""truth-v3 T2, Decision 9 (premise S; docs/SERA_FIELD_THEORY.md §14.1, independent review's rulings of 2026-09-25): before
"sure", a claim must rule out every claimable law that does not contain it, not only the laws in the ledger's space.
Written before the code.

The lemma: a claimable rival B (at most one non-base term t, at most one base idea beside it) that does not contain the
claim A lacks some term a of A, so B is inside U(t, -a) = {t} + (IDEAS - {a}); a nested model's best fit is at least
each member's, so Q_A - sup U >= thr rules out every such B at once. Stage 1 (independent review's cell ruling): every
claimable term except the cells (their families are left out, and the certificate says so).
  - the tree covers every rival and no node contains the claim (exhaustive, no fitting);
  - the claim's own invented term is audited too (independent review 1b: claim {t_A, i}, truth {t_A, j});
  - a superset's computed best fit is never below a member's (independent review 2: warm starts);
  - an out-of-ledger look-alike blocks a base claim that truth-v2 certified (forward pushes make |v| = v);
  - with pushes both ways the same claim certifies, and the audit's CPU is reported;
  - the checker refuses a certificate made without the audit or with a hole in its coverage.
"""
import dataclasses
import time

import numpy as np
import pytest

from ccops5.core import checker, grammar, likelihood as L, paths, truth, worlds as W

SIGMA = (0.001, 0.001)
DRAG = (('speed', 'straight'),)
TWIN = ('piece', 'speed', 'abs', 0.0)          # |v|: the same law as v when every reading has v >= 0


def _stage1_universe():
    base = grammar.space()
    fams = list(base)
    for t in truth.UNIVERSE_TERMS:
        fams.append((t,))
        fams += [grammar.canonical((t, i)) for i in grammar.IDEAS]
    return base, [f for f in dict.fromkeys(fams) if grammar.log_prior(f) > -np.inf]


CLAIMS = [(('position', 'straight'), ('speed', 'straight')),                       # base pair
          (('speed', 'straight'),),                                                  # base single
          grammar.canonical((('power', 'speed', 1.5), ('position', 'straight'))),    # invented term + idea
          (('drive', 'sin', 2.3),),                                                  # lone invented term
          grammar.canonical((('piece', 'speed', 'tanh', 0.5), ('position', 'cubic'))),   # grown piece + idea
          grammar.canonical((('pprod', 'bell1', 'straight'),))]


def test_the_universe_is_every_claimable_non_cell_law():
    base, fams = _stage1_universe()
    assert len(base) == 67
    assert len(truth.UNIVERSE_TERMS) == 259 + 57 + 551
    assert not any(t[0] == 'cell' for t in truth.UNIVERSE_TERMS)
    assert len(fams) == 67 + 12 * (259 + 57 + 551)


@pytest.mark.parametrize('claim', CLAIMS, ids=lambda c: grammar.name(c))
def test_the_tree_covers_every_rival_and_no_node_contains_the_claim(claim):
    base, fams = _stage1_universe()
    rivals = [b for b in fams if b != claim and not grammar.contains(b, claim)]
    nodes = {a: truth.audit_tree(claim, a) for a in claim}
    for a, roots in nodes.items():
        leaves = []
        stack = list(roots)
        while stack:
            node = stack.pop()
            U = truth.audit_superset(node, a)
            assert not grammar.contains(U, claim), (a, node)
            assert a not in U
            kids = truth.audit_children(node)
            if kids:
                assert sorted(sum((list(k) for k in kids), []), key=grammar._key) == sorted(node, key=grammar._key)
                stack += kids
            else:
                leaves.append(node)
        assert all(len(x) == 1 for x in leaves)
        assert sorted(x[0] for x in leaves) == sorted(t for t in truth.UNIVERSE_TERMS if t != a)
    for b in rivals:
        if b in base:
            continue                                   # t = none: a base law, always in the ledger's space
        t = next(x for x in b if x not in grammar.IDEAS)
        covering = [a for a in claim if a not in b and t != a
                    and set(b) <= set(truth.audit_superset((t,), a))]
        assert covering, grammar.name(b)


def test_the_claims_own_invented_term_is_audited():
    """independent review 1b: claim {t_A, i}; the rival {t_A, j} lacks i and lives only in U(t_A, -i)."""
    t_a = ('power', 'speed', 1.5)
    claim = grammar.canonical((t_a, ('position', 'straight')))
    leaves = []
    stack = list(truth.audit_tree(claim, ('position', 'straight')))
    while stack:
        node = stack.pop()
        kids = truth.audit_children(node)
        stack += kids if kids else []
        if not kids:
            leaves.append(node[0])
    assert t_a in leaves
    rival = grammar.canonical((t_a, ('position', 'cubic')))
    assert set(rival) <= set(truth.audit_superset((t_a,), ('position', 'straight')))


def _world(pushes, family=DRAG, coef=(-0.8,), seed=3, situations=6, hold=None):
    """Throws of `family`; each push is the teacher's 0.4 s push, or held for `hold` seconds when given."""
    kk, aa, bb = grammar.codes(family)
    rng = np.random.default_rng(seed)
    throws = []
    for k in range(situations):
        m = float(rng.uniform(0.6, 2.5))
        for j, u in enumerate(pushes):
            act = W.push_of(u) if hold is None else W.Action(((0.0, hold, float(u)),))
            xs, vs = paths.simulate_program(*act.arrays(), 1 / m, kk, aa, bb, np.array(coef), 1.0, 1.0, 0.0, 0.0)
            nr = np.random.default_rng([seed, k, j])
            throws.append(W.Throw(k, len(throws), act, xs + nr.normal(0, 1e-3, xs.size),
                                  vs + nr.normal(0, 1e-3, vs.size)))
    return throws


def _ledger(throws):
    ledger = truth.Ledger(grammar.space(), SIGMA)
    for t in throws:
        ledger.add(t)
    return ledger


@pytest.mark.slow
def test_a_superset_fit_is_never_below_a_member():
    ledger = _ledger(_world((1.0, 0.6, -1.0, -0.6)))
    mu = ledger.mle(DRAG).mu
    member = grammar.canonical((TWIN, ('position', 'straight')))
    node = (TWIN, ('piece', 'speed', 'tanh', 0.5))
    a = ('speed', 'straight')
    U = truth.audit_superset(node, a)
    s_member = truth.audit_fit(ledger, member, mu, DRAG)
    s_super = truth.audit_fit(ledger, U, mu, DRAG)
    assert truth._usable(s_member) and truth._usable(s_super)
    assert s_super.loglik >= s_member.loglik - 1e-6, (s_super.loglik, s_member.loglik)


# ua-slow3 (2026-09-25): forward throws visit half the speed axis, so the size bound is wider here - 0.354, measured
# with truth-v2 at eps 0.2, which refused on size and never reached the audit. The claim is asked at eps 0.4; the
# audit's threshold (grammar.log_threshold) does not depend on eps, so the audit decides as it would at 0.2.
LOOK_EPS = 0.4


@pytest.mark.slow
def test_an_out_of_ledger_look_alike_blocks_a_base_claim():
    ledger = _ledger(_world(FORWARD, coef=WEAK, situations=8, hold=HOLD))
    assert min(float(t.v.min()) for t in ledger.throws) > -0.01            # forward only: |v| = v on every reading
    old = truth.certify(ledger, DRAG, LOOK_EPS, audit='wide')
    assert old.accepted, old.reasons                                       # premise S failing silently (truth-v2)
    new = truth.certify(ledger, DRAG, LOOK_EPS)
    assert new.audit == 'universe-1'
    assert not new.accepted
    assert any('piece' in r or '|v|' in r or 'not ruled out' in r for r in new.reasons), new.reasons


# Speeds must span where v parts from cubic(v) + a speed wave (independent review, ua-slow 2026-09-25: with pushes of 1 / 0.6
# and drag -0.8 that pair fitted within noise, so the base claim never cleared the in-space screen and the audit never
# ran). As truth-v2's frozen T2 control: weaker drag, 8 objects, pushes from gentle to full (hand 1.4 to 3.0).
# 2026-09-25 (ua-slow2): still refused. sin(v) + v^3/6 = v + O(v^5), so the in-space pair cubic(v) + wave(v) mimics
# drag to v^5/120 - about 0.27 at |v| = 2, the most a 0.4 s push reaches here. Pushes held 1.2 s carry |v| to 4-5,
# where they part by several force units.
HOLD = 1.2
WEAK = (-0.5,)
FORWARD = (4.0, 0.8, 0.3, 1.5)
BOTH = (4.0, 0.3, -4.0, -0.3)


@pytest.fixture(scope='module')
def control():
    ledger = _ledger(_world(BOTH, coef=WEAK, situations=8, hold=HOLD))
    wide = truth.certify(ledger, DRAG, 0.2, audit='wide')
    assert wide.accepted, ('the control world must clear the in-space screen first', wide.reasons)
    t0 = time.process_time()
    cert = truth.certify(ledger, DRAG, 0.2)
    return ledger, cert, time.process_time() - t0


@pytest.mark.slow
def test_the_control_world_certifies_with_the_audit(control):
    ledger, cert, cpu = control
    print(f'universe audit: {len(cert.rivals)} rival entries, {cpu:.0f} s CPU for the certificate')
    assert cert.accepted, cert.reasons
    assert cert.audit == 'universe-1'
    assert truth.audit_gaps(cert.family, cert.rivals, ledger.families) == []
    assert 'cells' in cert.scope.get('not_audited', '')


@pytest.mark.slow
def test_the_checker_refuses_a_certificate_without_the_audit(control):
    ledger, cert, _ = control
    ok, why = checker.check(cert, ledger.throws, SIGMA)
    assert ok, why
    space = set(ledger.families)
    bare = dataclasses.replace(cert, rivals={b: e for b, e in cert.rivals.items() if b in space}, audit='none')
    ok, why = checker.check(bare, ledger.throws, SIGMA)
    assert not ok and any('audit' in r for r in why), why
    holed = dict(cert.rivals)
    holed.pop(next(b for b in holed if b not in space))
    ok, why = checker.check(dataclasses.replace(cert, rivals=holed), ledger.throws, SIGMA)
    assert not ok, why


def test_audit_gaps_finds_a_hole():
    claim = DRAG
    a = claim[0]
    rivals = {truth.audit_superset(node, a): 20.0 for node in truth.audit_tree(claim, a)}
    assert truth.audit_gaps(claim, rivals, grammar.space()) == []
    first = truth.audit_superset(truth.audit_tree(claim, a)[0], a)
    rivals.pop(first)
    gaps = truth.audit_gaps(claim, rivals, grammar.space())
    assert gaps and all(g[0] == a for g in gaps)
