"""G2 machinery (sera.synth): the loop on code finds small list functions, questions split the survivors, and the audit
accepts a right program and refuses a wrong one. Machinery tests only; the pre-registered G2 experiment comes later."""
import numpy as np

from sera import general as G, synth as S


def test_the_loop_finds_small_list_functions_and_the_audit_accepts_them():
    tasks = {
        'reverse': (lambda x: tuple(x[::-1]), 'list'),
        'sum': (lambda x: sum(x), 'int'),
        'add one to each': (lambda x: tuple(v + 1 for v in x), 'list'),
        'keep the positives': (lambda x: tuple(v for v in x if v > 0), 'list'),
    }
    for i, (name, (f, typ)) in enumerate(tasks.items()):
        r = S.synthesize(f, typ, np.random.default_rng(i), max_size=6)   # map/filter with a 3-node body are 6 nodes
        assert r['accepted'], (name, r)


def test_a_wrong_program_is_refused_by_the_audit():
    rng = np.random.default_rng(5)
    p = G.node('rev', G.node('input'))                             # claims "reverse" for a "sort" task
    bits = G.code_length(p, 'code', 'list')
    n = S.audit_size(bits)
    target = lambda x: tuple(sorted(x))
    assert not all(S._out(p, x) == target(x) for x in (S.random_input(rng) for _ in range(n)))
    assert n >= 90                                                 # (log 100 + bits ln 2) / -ln 0.95


def test_a_question_splits_the_survivors():
    a, b = G.node('rev', G.node('input')), G.node('sort', G.node('input'))
    surv = [(a, 3.0), (b, 3.0)]
    assert S._split(surv, [3, 1, 2]) > S._split(surv, [3, 2, 1]) == 0.0       # reversed [3, 2, 1] is sorted
