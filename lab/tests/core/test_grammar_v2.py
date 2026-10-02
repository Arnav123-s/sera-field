"""truth-v2 grammar (B4, docs/B4_GROWTH.md revisions 1-3), written before the code.

Pre-registered prior split: base families 0.9 (unchanged), truth-v1's invented terms 0.05 (each old open family's
log prior shifts by exactly -log 2), cells 0.03, new pieces and x-v piece products 0.02. The total over the whole
space is exactly 1 (Kraft). A cell term expands to K coefficients.
"""
import math

import numpy as np
import pytest

from ccops5.core import grammar

V1_OPEN = [t for t in grammar.OPEN_TERMS if t[0] in ('product', 'power', 'drive')]


def test_base_priors_unchanged_and_old_open_shift_by_log2():
    for fam in grammar.space():
        assert math.isclose(grammar.log_prior(fam), math.log(0.9 / 67), rel_tol=0, abs_tol=1e-12)
    for t in V1_OPEN[::7]:
        lone = grammar.log_prior((t,))
        v1 = math.log(0.1) + math.log(0.5) + grammar._open_term_log_prior(t)
        assert math.isclose(lone, v1 - math.log(2), abs_tol=1e-12)


def test_new_terms_are_claimable_and_expand():
    cell = ('cell', 'speed', 17)
    piece = ('piece', 'speed', 'tanh', 0.3)
    prod = ('pprod', 'straight', 'abs')
    for t in (cell, piece, prod, ('piece', 'position', 'abs', 0.0), ('piece', 'time', 'bell', 1.0)):
        assert t in grammar.GROWN_TERMS
        assert math.isfinite(grammar.log_prior((t,)))
        assert math.isfinite(grammar.log_prior((t, ('position', 'straight'))))
    k, a, b = grammar.codes((cell,))
    assert list(k) == [7] * 17 and list(a) == [1] * 17 and list(b) == [100 + i for i in range(17)]
    assert grammar.n_coef((cell, ('position', 'straight'))) == 18
    k, a, b = grammar.codes((piece,))
    assert (list(k), list(a), list(b)) == ([8], [1], [16 + 2])
    k, a, b = grammar.codes((prod,))
    assert (list(k), list(a), list(b)) == ([9], [0], [5])
    assert not math.isfinite(grammar.log_prior((cell, piece)))                     # at most one grown term


def test_duplicates_of_old_terms_are_excluded():
    """R2: a new product whose two parts are old shapes is the old 'product' term, so it is not a new term."""
    assert ('pprod', 'straight', 'straight') not in grammar.GROWN_TERMS
    assert ('pprod', 'cubic', 'wave') not in grammar.GROWN_TERMS


def test_total_prior_is_one():
    total = 0.0
    for fam in grammar.space():
        total += math.exp(grammar.log_prior(fam))
    for t in grammar.OPEN_TERMS + grammar.GROWN_TERMS:
        total += math.exp(grammar.log_prior((t,)))
        total += sum(math.exp(grammar.log_prior((t, i))) for i in grammar.IDEAS)
    assert math.isclose(total, 1.0, abs_tol=1e-9)
