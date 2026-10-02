"""G1 (plan revision 4, R4-5; research RG Design A): one typed program language for physics, code and words.
Pre-registered gate (RG section 6, Design A): every claimable law round-trips (3,175 of the Field's laws and the 67
base families), keeps its D9 price, has one canonical spelling, and computes the judge's own force; the search code
satisfies Kraft (sum of 2^-L <= 1); ill-typed programs are refused; the same constructors serve list functions and
word meanings."""
import math

import numpy as np
import pytest

from ccops5.core import grammar, paths
from sera import field as F, general as G


def _laws():
    return list(dict.fromkeys(list(F.LAWS) + list(grammar.space())))


def test_every_law_round_trips_with_its_price_and_one_spelling():
    seen = set()
    laws = _laws()
    for h in laws:
        p = G.encode_law(h)
        assert G.typecheck(p, 'physics', 'real') == 'real'
        assert G.decode_law(p) == grammar.canonical(h)
        assert G.price_physics(p) == grammar.log_prior(h)
        b = G.encode(p)
        assert b not in seen
        seen.add(b)
    assert len(seen) == len(laws) >= 3175
    print('laws round-tripped:', len(laws))


def test_a_law_program_computes_the_judges_own_force():
    rng = np.random.default_rng(0)
    laws = _laws()
    for i in rng.choice(len(laws), 300, replace=False):
        h = grammar.canonical(laws[int(i)])
        coef = rng.normal(0, 1, len(h))
        x, v, t = rng.normal(0, 1.5), rng.normal(0, 2.5), rng.uniform(0, 2)
        want = sum(c * sum(paths.term_t(k, a, b, x, v, t, 1.0, 1.0) for k, a, b in grammar.term_codes(term))
                   for c, term in zip(coef, h))
        got = G.evaluate(G.encode_law(h), dict(x=x, v=v, t=t, coef=coef))
        assert got == want, (h, got, want)


@pytest.mark.parametrize('typ,domain', [('real', 'physics'), ('int', 'code'), ('list', 'code'), ('bool', 'code'),
                                        ('bool', 'words')])
def test_the_search_code_satisfies_kraft(typ, domain):
    s = G.kraft_sum(typ, domain, 4)
    assert 0 < s <= 1 + 1e-12, s


def test_ill_typed_programs_are_refused():
    bad = [
        G.node('add', G.node('input'), G.node('coef')),                    # a list where a number goes
        G.node('rev', G.node('e')),                                        # e outside a lambda
        G.node('lit', payload=99),                                         # a literal outside its table
        G.node('prim', payload=('power', 'speed', 0.95)),                  # not a term of the grammar
        G.node('head', G.node('input'), G.node('input')),                  # wrong arity
    ]
    for p, dom in zip(bad, ('physics', 'code', 'code', 'physics', 'code')):
        with pytest.raises(ValueError):
            G.typecheck(p, dom)


def test_the_same_constructors_write_list_functions_and_word_meanings():
    inp = G.node('input')
    e, one, zero = G.node('e'), G.node('lit', payload=1), G.node('lit', payload=0)
    progs = {
        'reverse': (G.node('rev', inp), [3, -1, 2], [2, -1, 3]),
        'sum of positives': (G.node('sum', G.node('filter', G.node('lam_bool', G.node('lt', zero, e)), inp)),
                             [3, -1, 2], 5),
        'add one to each': (G.node('map', G.node('lam_int', G.node('iadd', e, one)), inp), [3, -1, 2], [4, 0, 3]),
        'first or 0': (G.node('head', inp), [], 0),
    }
    for name, (p, x, want) in progs.items():
        G.typecheck(p, 'code')
        assert G.evaluate(p, {'input': x}) == want, name
    iron_ball = G.node('and', G.node('is', payload=('material', 'iron')), G.node('is', payload=('shape', 'ball')))
    assert G.typecheck(iron_ball, 'words', 'bool') == 'bool'
    assert G.evaluate(iron_ball, {'thing': {'material': 'iron', 'shape': 'ball', 'size': 'big'}})
    assert not G.evaluate(iron_ball, {'thing': {'material': 'wood', 'shape': 'ball', 'size': 'big'}})
    once = G.node('rev', inp)
    assert G.code_length(once, 'code', 'list') < G.code_length(G.node('rev', once), 'code', 'list')
    assert math.isclose(sum(2.0 ** -G.code_length(G.node(s), 'code', 'list') for s in ('input',)),
                        1 / len(G.alphabet('list', 'code')))
