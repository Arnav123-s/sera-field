"""One hypothesis language for every domain (plan revision 4, R4-5 G1; research RG, (review notes, not published) Design A).

A hypothesis is a typed program: a tree whose inner nodes are SHARED constructors (add, mul, neg, compare, and, or,
not, if, map, filter, ...) and whose leaves are a domain's primitives. A physics law, a list function and a word's
meaning are all programs in this one language; only the primitives, the evaluator's inputs and the verifier differ:
    physics   real-valued programs of the world state (x, v, t): a law is sum_j coef_j * primitive_j, a primitive
              being a grammar term (its values from the judge's own simulator code, paths.term_t);
    code      programs from an input list of integers to an integer, a list or a truth value;
    words     truth-valued programs of a thing (its visible features), e.g. "heavy" as a predicate.

Search prior: a prefix code over programs. A program is written in preorder, one symbol per node, each chosen from
the symbols whose result type is the one the slot needs (and allowed in the domain and scope); integer literals and
primitives carry their index in a fixed table. Its code length L(p) is the sum of log2 of those alphabet sizes, and
pi0(p) = 2^-L(p) sums to at most 1 over all programs (a branching process: Kraft). This prior guides search only.
Proof prices never change: a physics claim keeps the judge's frozen D9 prior (price_physics), so the judge and
every certificate are untouched.
"""
import math
from functools import lru_cache

import numpy as np

from ccops5.core import grammar, paths

# --- the language: symbol -> (argument types, result type, domains). Leaves have no arguments. ---
ALL = ('physics', 'code', 'words')
SYMBOLS = {
    # shared constructors
    'add': (('real', 'real'), 'real', ('physics',)),
    'mul': (('real', 'real'), 'real', ('physics',)),
    'neg': (('real',), 'real', ('physics',)),
    'iadd': (('int', 'int'), 'int', ('code',)),
    'isub': (('int', 'int'), 'int', ('code',)),
    'imul': (('int', 'int'), 'int', ('code',)),
    'lt': (('int', 'int'), 'bool', ('code',)),
    'eq': (('int', 'int'), 'bool', ('code',)),
    'and': (('bool', 'bool'), 'bool', ALL[1:]),
    'or': (('bool', 'bool'), 'bool', ALL[1:]),
    'not': (('bool',), 'bool', ALL[1:]),
    'if': (('bool', 'int', 'int'), 'int', ('code',)),
    'map': (('fn_int', 'list'), 'list', ('code',)),
    'filter': (('fn_bool', 'list'), 'list', ('code',)),
    'lam_int': (('int',), 'fn_int', ('code',)),          # binds 'e' (an element) in its body
    'lam_bool': (('bool',), 'fn_bool', ('code',)),
    # physics leaves
    'zero': ((), 'real', ('physics',)),                  # no force (the empty law)
    'coef': ((), 'real', ('physics',)),                  # the next strength (numbered in preorder)
    'prim': ((), 'real', ('physics',)),                  # payload: a grammar term
    # code leaves and list primitives
    'input': ((), 'list', ('code',)),
    'e': ((), 'int', ('code',)),                         # only inside a lam_*
    'lit': ((), 'int', ('code',)),                       # payload: an integer in LITS
    'head': (('list',), 'int', ('code',)),
    'last': (('list',), 'int', ('code',)),
    'len': (('list',), 'int', ('code',)),
    'sum': (('list',), 'int', ('code',)),
    'max': (('list',), 'int', ('code',)),
    'rev': (('list',), 'list', ('code',)),
    'tail': (('list',), 'list', ('code',)),
    'sort': (('list',), 'list', ('code',)),
    'take': (('int', 'list'), 'list', ('code',)),
    'drop': (('int', 'list'), 'list', ('code',)),
    'cons': (('int', 'list'), 'list', ('code',)),
    # words leaves
    'is': ((), 'bool', ('words',)),                      # payload: (feature, value) in FEATURES
}
LITS = tuple(range(-8, 9))
FEATURES = tuple((f, v) for f, vs in (('material', ('iron', 'wood', 'rubber', 'foam')), ('size', ('small', 'big')),
                                      ('shape', ('ball', 'block'))) for v in vs)
PRIMS = tuple(dict.fromkeys(t for f in grammar.space() for t in f)) + tuple(
    t for t in grammar.OPEN_TERMS + grammar.PIECES + grammar.PPRODS if t not in grammar.IDEAS)
_PRIM_INDEX = {t: i for i, t in enumerate(PRIMS)}
PAYLOAD = {'prim': len(PRIMS), 'lit': len(LITS), 'is': len(FEATURES)}


def alphabet(typ, domain, bound=False):
    """The symbols that can fill a slot of type `typ` in `domain` ('e' only inside a lam_*)."""
    return tuple(s for s, (_, out, doms) in SYMBOLS.items()
                 if out == typ and domain in doms and (s != 'e' or bound))


# --- programs are nested tuples: (symbol, payload_or_None, child, child, ...) ---
def node(symbol, *children, payload=None):
    return (symbol, payload) + tuple(children)


def typecheck(p, domain, typ=None, bound=False):
    """The program's type, or ValueError. `typ`: the type its slot needs."""
    sym, payload, kids = p[0], p[1], p[2:]
    if sym not in SYMBOLS:
        raise ValueError(f'unknown symbol {sym}')
    args, out, doms = SYMBOLS[sym]
    if domain not in doms or (sym == 'e' and not bound):
        raise ValueError(f'{sym} is not allowed here')
    if typ is not None and out != typ:
        raise ValueError(f'{sym} gives {out}, the slot needs {typ}')
    if len(kids) != len(args):
        raise ValueError(f'{sym} takes {len(args)} arguments')
    if sym in PAYLOAD and not (payload is not None and 0 <= _payload_index(sym, payload) < PAYLOAD[sym]):
        raise ValueError(f'{sym} needs a payload from its table')
    inner = bound or sym in ('lam_int', 'lam_bool')
    for k, a in zip(kids, args):
        typecheck(k, domain, a, inner)
    return out


def _payload_index(sym, payload):
    if sym == 'prim':
        return _PRIM_INDEX.get(payload, -1)
    if sym == 'lit':
        return LITS.index(payload) if payload in LITS else -1
    if sym == 'is':
        return FEATURES.index(payload) if payload in FEATURES else -1
    return -1


def code_length(p, domain, typ, bound=False):
    """Bits of the program under the prefix code (preorder; per slot, log2 of its alphabet; payloads by table)."""
    sym, payload, kids = p[0], p[1], p[2:]
    bits = math.log2(len(alphabet(typ, domain, bound)))
    if sym in PAYLOAD:
        bits += math.log2(PAYLOAD[sym])
    args = SYMBOLS[sym][0]
    inner = bound or sym in ('lam_int', 'lam_bool')
    return bits + sum(code_length(k, domain, a, inner) for k, a in zip(kids, args))


def encode(p):
    """Canonical bytes (preorder): the same program always gives the same bytes, different programs differ."""
    out = []

    def walk(q):
        out.append(repr((q[0], q[1], len(q) - 2)))
        for k in q[2:]:
            walk(k)
    walk(p)
    return ';'.join(out).encode()


# --- evaluation ---
def evaluate(p, env):
    """The program's value. env: physics {'x','v','t','coef','sx','sv'} (coef consumed in preorder); code {'input'};
    words {'thing': {feature: value}}."""
    state = {'k': 0}
    return _ev(p, env, state)


def _ev(p, env, st):
    sym, payload, kids = p[0], p[1], p[2:]
    if sym == 'add':
        return _ev(kids[0], env, st) + _ev(kids[1], env, st)
    if sym == 'mul':
        return _ev(kids[0], env, st) * _ev(kids[1], env, st)
    if sym == 'neg':
        return -_ev(kids[0], env, st)
    if sym == 'zero':
        return 0.0
    if sym == 'coef':
        c = env['coef'][st['k']]
        st['k'] += 1
        return c
    if sym == 'prim':
        w = payload[4] if payload[0] == 'shape' else [1.0] * len(grammar.term_codes(payload))   # an invented shape's
        return sum(wk * paths.term_t(k, a, b, env['x'], env['v'], env['t'], env.get('sx', 1.0), env.get('sv', 1.0))
                   for wk, (k, a, b) in zip(w, grammar.term_codes(payload)))                       # knots
    if sym == 'is':
        return env['thing'].get(payload[0]) == payload[1]
    if sym in ('and', 'or'):
        a = _ev(kids[0], env, st)
        return (a and _ev(kids[1], env, st)) if sym == 'and' else (a or _ev(kids[1], env, st))
    if sym == 'not':
        return not _ev(kids[0], env, st)
    if sym == 'input':
        return list(env['input'])
    if sym == 'e':
        return env['e']
    if sym == 'lit':
        return payload
    if sym in ('iadd', 'isub', 'imul', 'lt', 'eq'):
        a, b = _ev(kids[0], env, st), _ev(kids[1], env, st)
        return {'iadd': a + b, 'isub': a - b, 'imul': a * b, 'lt': a < b, 'eq': a == b}[sym]
    if sym == 'if':
        return _ev(kids[1], env, st) if _ev(kids[0], env, st) else _ev(kids[2], env, st)
    if sym in ('map', 'filter'):
        body, xs = kids[0][2], _ev(kids[1], env, st)
        vals = [_ev(body, dict(env, e=x), st) for x in xs]
        return vals if sym == 'map' else [x for x, keep in zip(xs, vals) if keep]
    xs = _ev(kids[-1], env, st)                                      # the list primitives (total: defaults on empty)
    if sym == 'head':
        return xs[0] if xs else 0
    if sym == 'last':
        return xs[-1] if xs else 0
    if sym == 'len':
        return len(xs)
    if sym == 'sum':
        return sum(xs)
    if sym == 'max':
        return max(xs) if xs else 0
    if sym == 'rev':
        return xs[::-1]
    if sym == 'tail':
        return xs[1:]
    if sym == 'sort':
        return sorted(xs)
    k = _ev(kids[0], env, st)
    if sym == 'take':
        return xs[:max(k, 0)]
    if sym == 'drop':
        return xs[max(k, 0):]
    if sym == 'cons':
        return [k] + xs
    raise ValueError(sym)


# --- the physics adapter: every law of the judge's grammar, losslessly ---
def encode_law(family):
    """sum_j coef_j * term_j in canonical term order, as a program (left-nested adds); the empty family (no force
    beyond the hand) is 'zero'."""
    fam = grammar.canonical(family)
    if not fam:
        return node('zero')
    parts = [node('mul', node('coef'), node('prim', payload=t)) for t in fam]
    p = parts[0]
    for q in parts[1:]:
        p = node('add', p, q)
    return p


def decode_law(p):
    """The family a law program spells (its terms in order), or ValueError if it is not a law's spelling."""
    if p[0] == 'zero':
        return ()
    terms = []

    def walk(q):
        if q[0] == 'add':
            walk(q[2])
            walk(q[3])
        elif q[0] == 'mul' and q[2][0] == 'coef' and q[3][0] == 'prim':
            terms.append(q[3][1])
        else:
            raise ValueError('not a law')
    walk(p)
    fam = grammar.canonical(tuple(terms))
    if tuple(terms) != fam:
        raise ValueError('terms out of canonical order')
    return fam


def price_physics(p):
    """The proof price of a physics claim: the judge's frozen D9 prior, never the search code."""
    return grammar.log_prior(decode_law(p))


@lru_cache(maxsize=None)
def n_programs(typ, domain, depth, bound=False):
    """How many programs of this type fit within `depth` levels (for tests of the code)."""
    if depth == 0:
        return 0
    total = 0
    for s in alphabet(typ, domain, bound):
        args = SYMBOLS[s][0]
        inner = bound or s in ('lam_int', 'lam_bool')
        n = PAYLOAD.get(s, 1)
        for a in args:
            n *= n_programs(a, domain, depth - 1, inner)
        total += n
    return total


def kraft_sum(typ, domain, depth, bound=False):
    """sum over programs of depth <= `depth` of 2^-L(p) (<= 1: a sub-probability of the branching process)."""
    if depth == 0:
        return 0.0
    k = len(alphabet(typ, domain, bound))
    total = 0.0
    for s in alphabet(typ, domain, bound):
        args = SYMBOLS[s][0]
        inner = bound or s in ('lam_int', 'lam_bool')
        part = 1.0 / k
        for a in args:
            part *= kraft_sum(a, domain, depth - 1, inner)
        total += part                                    # a payload's table sums to 1 over its entries
    return total
