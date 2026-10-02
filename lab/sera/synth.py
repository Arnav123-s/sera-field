"""G2 machinery (plan revision 4, R4-5; docs/SERA_GENERAL.md section 4): SERA's loop on code - imagine programs, ask the
question that splits them, revise, and let a verifier decide - in the shared language of sera.general.

- Imagine: every program of the code domain up to a size, built bottom-up from the language's symbols; programs that
  give the same outputs on every input known so far are one (the shortest spelling kept: observational equivalence,
  a search economy only). Lambda bodies use the element e, literals and integer operations (not the whole input).
- Question: among a pool of inputs, ask the one whose answer splits the surviving programs most (entropy of the
  output partition, programs weighted by their prior 2^-L). The baseline asks pool inputs in a fixed random order.
- Revise: keep the programs that agree with every answer.
- Verify (the code audit, docs/SERA_GENERAL.md 3): the shortest survivor is frozen, then run on n fresh IID inputs;
  accepted only if all pass and n reaches the anytime bar 1/(1 - eps)^n >= 1/(delta pi0(p)), so
  P(some program is ever accepted whose error rate under D is >= eps) <= delta. Questions never count toward the audit.
"""
import itertools
import math

import numpy as np

from . import general as G

E_PROBE = tuple(range(-8, 9))
EPS, DELTA = 0.05, 0.01


def random_input(rng, max_len=6):
    return [int(v) for v in rng.integers(-8, 9, size=int(rng.integers(0, max_len + 1)))]


def audit_size(bits, eps=EPS, delta=DELTA):
    """The smallest n with 1/(1 - eps)^n >= 1/(delta 2^-bits)."""
    return math.ceil((math.log(1 / delta) + bits * math.log(2)) / -math.log(1 - eps))


def _safe(p, env):
    try:
        v = G.evaluate(p, env)
    except (ValueError, OverflowError, IndexError, TypeError):
        return None
    if isinstance(v, bool) or isinstance(v, int):
        return v if abs(int(v)) <= 10 ** 6 else None
    if isinstance(v, list):
        return tuple(v) if len(v) <= 64 and all(abs(x) <= 10 ** 6 for x in v) else None
    return None


def _lambda_bodies(max_size):
    """{('int'|'bool'): [(body, bits, values over E_PROBE)]}, deduped by values, shortest kept."""
    table = {'int': {}, 'bool': {}}
    by_size = {1: {'int': [], 'bool': []}}
    leaves = [G.node('e')] + [G.node('lit', payload=k) for k in G.LITS]
    for p in leaves:
        _add(table, by_size[1], 'int', p, True)
    ops2 = {'iadd': 'int', 'isub': 'int', 'imul': 'int', 'lt': 'bool', 'eq': 'bool', 'and': 'bool', 'or': 'bool'}
    for s in range(2, max_size + 1):
        by_size[s] = {'int': [], 'bool': []}
        for sym, out in ops2.items():
            a = G.SYMBOLS[sym][0]
            for k in range(1, s - 1):
                for x in by_size.get(k, {}).get(a[0], []):
                    for y in by_size.get(s - 1 - k, {}).get(a[1], []):
                        _add(table, by_size[s], out, G.node(sym, x, y), True)
        for x in by_size[s - 1]['bool']:
            _add(table, by_size[s], 'bool', G.node('not', x), True)
    return {t: sorted(v.values(), key=lambda r: r[1]) for t, v in table.items()}


def _add(table, level, typ, p, bound, env_list=None):
    if env_list is None:
        vals = tuple(_safe(p, {'e': e}) for e in E_PROBE)
    else:
        vals = tuple(_safe(p, env) for env in env_list)
    if any(v is None for v in vals):
        return
    bits = G.code_length(p, 'code', typ, bound)
    old = table[typ].get(vals)
    if old is None or bits < old[1]:
        table[typ][vals] = (p, bits, vals)
        level[typ].append(p)


class Space:
    """Every code-domain program up to `max_size` nodes (top level), deduped on `inputs` (the known ones)."""

    def __init__(self, inputs, max_size=5, lambda_size=3):
        self.inputs = [list(x) for x in inputs]
        envs = [{'input': x} for x in self.inputs]
        lam = _lambda_bodies(lambda_size)
        table = {'int': {}, 'bool': {}, 'list': {}}
        by_size = {s: {'int': [], 'bool': [], 'list': []} for s in range(1, max_size + 1)}
        _add(table, by_size[1], 'list', G.node('input'), False, envs)
        for k in G.LITS:
            _add(table, by_size[1], 'int', G.node('lit', payload=k), False, envs)
        unary = {s: v for s, v in G.SYMBOLS.items() if v[0] == ('list',)}
        binary_int_list = ('take', 'drop', 'cons')
        for s in range(2, max_size + 1):
            for sym, (args, out, _) in unary.items():
                for x in by_size[s - 1]['list']:
                    _add(table, by_size[s], out, G.node(sym, x), False, envs)
            for sym in binary_int_list:
                for k in range(1, s - 1):
                    for x in by_size[k]['int']:
                        for y in by_size[s - 1 - k]['list']:
                            _add(table, by_size[s], 'list', G.node(sym, x, y), False, envs)
            for sym in ('iadd', 'isub', 'imul'):
                for k in range(1, s - 1):
                    for x in by_size[k]['int']:
                        for y in by_size[s - 1 - k]['int']:
                            _add(table, by_size[s], 'int', G.node(sym, x, y), False, envs)
            for sym, lam_sym, typ in (('map', 'lam_int', 'int'), ('filter', 'lam_bool', 'bool')):
                for body, bbits, _ in lam[typ]:
                    bsize = _size(body)
                    k = s - 2 - bsize                       # map + lambda + body + list
                    if k < 1:
                        continue
                    for y in by_size[k]['list']:
                        _add(table, by_size[s], 'list', G.node(sym, G.node(lam_sym, body), y), False, envs)
        self.table = table

    def programs(self, typ):
        """(program, bits) of this output type, shortest first."""
        return sorted(((p, b) for p, b, _ in self.table[typ].values()), key=lambda r: r[1])


def _size(p):
    return 1 + sum(_size(k) for k in p[2:])


def synthesize(target, out_type, rng, n_examples=3, pool=30, queries=6, max_size=5, active=True, oracle=None):
    """SERA's loop on one task: examples, imagined programs, questions, the shortest survivor, the audit.
    `target(x)` is the oracle. Returns a dict: the chosen program, its bits, questions asked, audit n, accepted."""
    oracle = oracle or target
    known = [random_input(rng) for _ in range(n_examples)]
    pool_inputs = [random_input(rng) for _ in range(pool)]
    space = Space(known + pool_inputs, max_size=max_size)
    answers = {tuple(x): oracle(x) for x in known}
    survivors = [(p, b) for p, b in space.programs(out_type)
                 if all(_out(p, x) == answers[tuple(x)] for x in known)]
    asked = 0
    order = list(range(len(pool_inputs)))
    for _ in range(queries):
        if len(survivors) <= 1:
            break
        if active:
            q = max(order, key=lambda i: _split(survivors, pool_inputs[i]))
        else:
            q = order[0]
        order.remove(q)
        x = pool_inputs[q]
        y = oracle(x)
        answers[tuple(x)] = y
        survivors = [(p, b) for p, b in survivors if _out(p, x) == y]
        asked += 1
    if not survivors:
        return dict(program=None, bits=None, asked=asked, audit_n=0, accepted=False, why='no program fits')
    p, bits = survivors[0]
    n = audit_size(bits)
    passed = all(_out(p, x) == target(x) for x in (random_input(rng) for _ in range(n)))
    return dict(program=p, bits=bits, asked=asked, audit_n=n, accepted=passed, survivors=len(survivors),
                why='' if passed else 'the audit found an input it gets wrong')


def _out(p, x):
    v = G.evaluate(p, {'input': list(x)})
    return tuple(v) if isinstance(v, list) else v


def _split(survivors, x):
    """Entropy (bits) of the survivors' answers to x, each program weighted by 2^-bits."""
    w = {}
    for p, b in survivors:
        o = _out(p, x)
        w[o] = w.get(o, 0.0) + 2.0 ** -b
    tot = sum(w.values())
    return -sum(v / tot * math.log2(v / tot) for v in w.values() if v > 0)
