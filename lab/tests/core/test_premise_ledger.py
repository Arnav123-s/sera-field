"""truth-v3 T2 item 4 (plan revision 3; docs/SERA_FIELD_THEORY.md v1.1 §15): every certificate says which premises of
Theorem A its "sure" rests on, and how each stands - proven, computed, measured or assumed - and the checker recomputes
the ledger from the policy (a certificate that overstates a premise is refused). Written before the code."""
import dataclasses

from ccops5.core import checker, truth

KEYS = ('P', 'M', 'N', 'U', 'S', 'F', 'Q')


def test_the_ledger_names_every_premise_with_a_status():
    led = truth.premise_ledger('universe-1', 'laplace')
    assert tuple(k for k, _, _ in led) == KEYS
    assert all(s in ('proven', 'computed', 'measured', 'assumed') for _, s, _ in led)
    assert all(isinstance(why, str) and why for _, _, why in led)


def test_s_is_computed_only_with_the_universe_audit():
    status = lambda audit: dict((k, s) for k, s, _ in truth.premise_ledger(audit, 'laplace'))
    assert status('universe-1')['S'] == 'computed'
    assert status('wide')['S'] == 'assumed'
    assert 'cells' in dict((k, w) for k, _, w in truth.premise_ledger('universe-1', 'laplace'))['S']


def test_n_depends_on_the_numerator():
    why = lambda num: dict((k, w) for k, _, w in truth.premise_ledger('universe-1', num))['N']
    assert why('laplace') != why('lattice')


def test_the_checker_refuses_an_overstated_ledger():
    cert = truth.Certificate(family=(), alpha=1e-3, delta=1e-3, eps=0.2, n_space=67, inventions=(), digest='x',
                             rivals={}, nested={}, band=None, adequacy=None, scope={}, accepted=False, reasons=(),
                             audit=truth.AUDIT, premises=truth.premise_ledger(truth.AUDIT, truth.NUMERATOR))
    assert checker.premise_reason(cert) is None
    rosy = tuple((k, 'proven', w) for k, _, w in cert.premises)
    assert checker.premise_reason(dataclasses.replace(cert, premises=rosy)) is not None
    assert checker.premise_reason(dataclasses.replace(cert, premises=())) is not None
