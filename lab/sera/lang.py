"""SERA's one language (plan revision 6; the author, 2026-09-27: "one SERA, one mind that's adaptive, not modules of
each separate field or task"; "do not give it a predefined set of words, sentences, formulas - teach it").

Everything SERA thinks in any subject - a force law, a list program, a number rule - is an expression in this one
language. What is innate is only mechanism:
- numbers: zero, one, add, sub, mul (the same for whole numbers and measured quantities);
- comparing and choosing: lt, eq, if;
- lists: nil, cons, head, tail, range (1..n), and iterating over a list: map, filter, fold. A list may hold numbers
  or lists (2026-09-28, the author: "i want sera to build the abilities it needs, not us building every smallest
  thing"): a list of lists is as much a value as a list of numbers, and every list mechanism works at every depth.
  Nothing about grids, rows or pictures is here; a grid is only a list of lists to it;
- the task's inputs (a world says what it shows: the position, speed and time of a thing; a list; a number);
- the free curve: a curve of one measured input whose values SERA shapes from its own measurements (a physics world
  gives it strengths to fit; it is how a new shape is first seen).
Nothing else is given. Spring, drag, sum, reverse, square, triangle numbers - none is here. Each is taught (a teacher's
examples and words) or discovered, and then kept as a concept: a named function of the language, usable in every
subject whose types fit (a square learned from numbers can shape a force).

Types: 'num', 'bool', 'real', and lists: 'list' holds numbers, 'list(list)' holds lists of numbers, and so on. In a
signature, T and U stand for anything a list can hold here. A concept's type is the most general its body allows
(inferred, 2026-09-28): a reverse learned on a list of lists reverses a list of numbers too.

An expression is a tuple (symbol, payload, *children). Lambdas are ('lam', kind, body): kind 'e' binds the element
(map, filter), kind 'ae' binds the accumulator and the element (fold). A concept is ('c', id, child): the concept's body
applied to its one argument.

Search: every expression of a type up to a size, bottom-up, one per behaviour on the task's probe inputs (observational
equivalence: two expressions that do the same on every probe are one to it; the shorter kept). Each expression's values
are made from its parts' values (2026-09-28: nothing is evaluated twice). Description length: each node costs log2 of
the language's size (innate symbols + concepts): a prefix code over the whole language (Kraft), so a concept - one
node - makes every expression that uses it shorter. That is what invention buys.
"""
import itertools
import math
import os
import re
import sys
import time

import numpy as np

INNATE = {
    'zero': ((), 'num'), 'one': ((), 'num'),
    'add': (('num', 'num'), 'num'), 'sub': (('num', 'num'), 'num'), 'mul': (('num', 'num'), 'num'),
    'lt': (('num', 'num'), 'bool'), 'eq': (('num', 'num'), 'bool'),
    'if': (('bool', 'num', 'num'), 'num'),
    'nil': ((), 'list(T)'), 'cons': (('T', 'list(T)'), 'list(T)'), 'head': (('list(T)',), 'T'),
    'tail': (('list(T)',), 'list(T)'),
    'range': (('num',), 'list'),
    'map': (('lam:e>U', 'list(T)'), 'list(U)'), 'filter': (('lam:e>bool', 'list(T)'), 'list(T)'),
    'rone': ((), 'real'),                                                     # 2026-09-28: measured quantities -
    'radd': (('real', 'real'), 'real'), 'rsub': (('real', 'real'), 'real'),   # real numbers, their own type (a list or
    'rmul': (('real', 'real'), 'real'), 'rdiv': (('real', 'real'), 'real'),   # number task never pays for them)
    'sqrt': (('real',), 'real'), 'exp': (('real',), 'real'), 'log': (('real',), 'real'),
    'sin': (('real',), 'real'), 'cos': (('real',), 'real'),
    'mapi': (('lam:ie>U', 'list(T)'), 'list(U)'), 'filteri': (('lam:ie>bool', 'list(T)'), 'list(T)'),   # 2026-09-28:
                                                                             # with each element's place, from 1
    'foldn': (('lam:ae>num', 'num', 'list(T)'), 'num'), 'foldl': (('lam:ae>list(U)', 'list(U)', 'list(T)'), 'list(U)'),
}
MAX_INT = 10 ** 6
MAX_LEN = 64
MAX_STEPS = 20000
EXECUTION_COUNTS = None             # opt-in U1 measurements; never read by search or credit


class Bad(Exception):
    pass


BAD = (Bad, RecursionError, ZeroDivisionError, OverflowError, TypeError, IndexError)


def node(sym, *kids, payload=None):
    return (sym, payload) + tuple(kids)


def size(p):
    return 1 + sum(size(k) for k in p[2:])


def alphabet_size(concepts):
    """Symbols of the language: the innate ones, the inputs a world may give (counted as one class), the numbers it
    perceives in a task (one class), and concepts."""
    return len(INNATE) + 3 + len(concepts)


def bits(p, concepts):
    """Description length in bits: every node log2 of the language's size (a prefix code: Kraft holds). A λ that sees
    the input around it (sees) pays for that: each input it sees is said twice - 'around', then which one (S01, reviewer:
    a captured input was priced as the λ's own element)."""
    return (size(p) + _captured(p)) * math.log2(alphabet_size(concepts))


def _captured(p, inside=False):
    if p[0] == 'var':
        return 1 if inside and p[1] not in _BOUND else 0
    inside = inside or p[0] == 'lam'
    return sum(_captured(k, inside) for k in p[2:])


def parts(p):
    """The parts an expression is made of: its symbols and concepts (for understanding: which parts explained what)."""
    out = []
    stack = [p]
    while stack:
        q = stack.pop()
        tag = ('concept', q[1]) if q[0] == 'c' else ('var', q[1]) if q[0] == 'var' else ('sym', q[0])
        if q[0] != 'lam':
            out.append(tag)
        stack.extend(q[2:])
    return tuple(dict.fromkeys(out))


def show(p, names=None):
    """An expression as text (its own names for its concepts)."""
    sym, pay, kids = p[0], p[1], p[2:]
    if sym == 'var':
        return str(pay)
    if sym == 'c':
        nm = (names or {}).get(pay, f'c{pay}')
        return f'{nm}({show(kids[0], names)})'
    if sym == 'lam':
        return {'e': 'λe. ', 'ie': 'λi,e. '}.get(pay, 'λa,e. ') + show(kids[0], names)
    if sym == 'lit':
        return str(pay)
    if not kids:
        return {'zero': '0', 'one': '1', 'nil': '[]', 'rone': '1'}.get(sym, sym)
    return f"{sym}({', '.join(show(k, names) for k in kids)})"


# --- types ---
_TVAR = re.compile(r'\b[A-Z]\b')


def list_of(t):
    """The type of a list that holds t ('list' holds numbers)."""
    return 'list' if t == 'num' else f'list({t})'


def elem(t):
    """What a list type holds; None when t is not a list."""
    if t == 'list':
        return 'num'
    if t.startswith('list(') and t.endswith(')'):
        return t[5:-1]
    return None


def is_list(t):
    return elem(t) is not None


def depth(t):
    n = 0
    while is_list(t):
        t, n = elem(t), n + 1
    return n


def universe(types, lists=True):
    """The types a search works in: numbers, truths and measured quantities; with lists, a list of numbers and every
    list type given (an input's, the answer's) with the types of what it holds."""
    ls = set()
    if lists:
        ls.add('list')
        for t in types:
            while t is not None and is_list(t):
                ls.add(t)
                t = elem(t)
    return ['num', 'bool'] + sorted(ls, key=depth) + ['real']


def _subst(t, sub):
    if t.startswith('lam:'):
        head, out = t.split('>')
        return f'{head}>{_subst(out, sub)}'
    if t in sub:
        return sub[t]
    e = elem(t)
    if e is not None and e != 'num':
        return list_of(_subst(e, sub))
    return t


def _known(t, types):
    return t.split('>')[1] in types if t.startswith('lam:') else t in types


def instances(args, ret, types):
    """Every way the type variables of a signature (T, U ...) can stand for what lists hold in this universe:
    [(argument types, result type, {variable: type})], every type in the universe."""
    args = tuple(args)
    names = sorted({v for t in args + (ret,) for v in _TVAR.findall(t)})
    if not names:
        return [(args, ret, {})] if all(_known(t, types) for t in args + (ret,)) else []
    held = [t for t in types if list_of(t) in types]
    out = []
    for combo in itertools.product(held, repeat=len(names)):
        sub = dict(zip(names, combo))
        a = tuple(_subst(t, sub) for t in args)
        r = _subst(ret, sub)
        if all(_known(t, types) for t in a + (r,)):
            out.append((a, r, sub))
    return out


def fits(sig, arg, ret):
    """Can a concept of this signature take an `arg` and give a `ret`?"""
    return any(a == (arg,) and r == ret for a, r, _ in instances((sig[0],), sig[1], universe([arg, ret])))


def infer(body, concepts, arg='_'):
    """The most general type of a concept's body as a function of its argument (2026-09-28): (argument type, result
    type), with T, U ... for what the body leaves open - a reverse learned on a list of lists reverses any list. None
    when the body has no type."""
    sub, count = {}, [0]
    sigs = concepts.get('_sig') or {}

    def fresh():
        count[0] += 1
        return count[0]

    def parse(t, vs):
        if len(t) == 1 and t.isupper():
            if t not in vs:
                vs[t] = fresh()
            return vs[t]
        e = elem(t)
        return ('list', parse(e, vs)) if e is not None else t

    def walk(t):
        while isinstance(t, int) and t in sub:
            t = sub[t]
        return t

    def occurs(v, t):
        t = walk(t)
        return t == v if isinstance(t, int) else isinstance(t, tuple) and occurs(v, t[1])

    def unify(a, b):
        a, b = walk(a), walk(b)
        if a == b:
            return
        if isinstance(a, int):
            if occurs(a, b):
                raise Bad('no type')
            sub[a] = b
        elif isinstance(b, int):
            unify(b, a)
        elif isinstance(a, tuple) and isinstance(b, tuple):
            unify(a[1], b[1])
        else:
            raise Bad('no type')

    def go(p, env):
        sym, pay, kids = p[0], p[1], p[2:]
        if sym == 'var':
            if pay not in env:
                raise Bad('no type')
            return env[pay]
        if sym in ('zero', 'one', 'lit'):
            return 'num'
        if sym == 'rone':
            return 'real'
        if sym == 'tab':
            unify(go(kids[0], env) if kids else env.get('_', 'num'), 'num')
            return 'num'
        if sym == 'c':
            if pay not in sigs:
                raise Bad('no type')
            vs = {}
            a, r = parse(sigs[pay][0], vs), parse(sigs[pay][1], vs)
            unify(go(kids[0], env), a)
            return r
        if sym not in INNATE:
            raise Bad('no type')
        args, ret = INNATE[sym]
        vs = {}
        if args and args[0].startswith('lam'):
            kind, out = args[0][4:].split('>')
            body_t = parse(out, vs)
            rest = [parse(t, vs) for t in args[1:]]
            r = parse(ret, vs)
            for k, t in zip(kids[1:], rest):
                unify(go(k, env), t)
            inner = dict(env, e=vs['T'])
            if kind == 'ie':
                inner['i'] = 'num'
            if kind == 'ae':
                inner['a'] = rest[0]
            unify(go(kids[0][2], inner), body_t)
            return r
        ts = [parse(t, vs) for t in args]
        r = parse(ret, vs)
        if sym == 'head':                   # its payload says what it gives (an empty list's head: 0 or ()), so a
            unify(vs['T'], parse(pay or 'num', {}))      # head of lists is not a head of anything (S02, reviewer)
        for k, t in zip(kids, ts):
            unify(go(k, env), t)
        return r

    try:
        x = fresh()
        r = go(body, {arg: x})
    except (Bad, KeyError, IndexError, ValueError, RecursionError):
        return None
    names = {}

    def fmt(t):
        t = walk(t)
        if isinstance(t, int):
            if t not in names:
                names[t] = 'TUVWXYZ'[min(len(names), 6)]
            return names[t]
        if isinstance(t, tuple):
            return list_of(fmt(t[1]))
        return t
    return fmt(x), fmt(r)


# --- values and evaluation ---
def freeze(v):
    """A value as the language holds it: a list as a tuple, at every depth."""
    if isinstance(v, list):
        return tuple(freeze(x) for x in v)
    return v


def _num(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise Bad('not a number')
    if isinstance(v, float) and not math.isfinite(v):
        raise Bad('not finite')
    if abs(v) > MAX_INT:
        raise Bad('too large')
    return v


def _real(v):
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise Bad('not a number')
    v = float(v)
    if not math.isfinite(v) or abs(v) > 1e12:
        raise Bad('not finite')
    return v


def _lst(v):
    if not isinstance(v, tuple):
        raise Bad('not a list')
    if len(v) > MAX_LEN:
        raise Bad('too long')
    return v


def _held(v):
    """What a list may hold: a number or a list."""
    return _lst(v) if isinstance(v, tuple) else _num(v)


def _prim(sym, pay, a, b=None):
    """A symbol of the language on its arguments' values (all but choosing, iterating and concepts)."""
    if EXECUTION_COUNTS is not None:
        EXECUTION_COUNTS['primitive_calls'] += 1
    if sym in ('add', 'sub', 'mul'):
        a, b = _num(a), _num(b)
        return _num(a + b if sym == 'add' else a - b if sym == 'sub' else a * b)
    if sym in ('lt', 'eq'):
        a, b = _num(a), _num(b)
        return a < b if sym == 'lt' else a == b
    if sym == 'cons':
        return _lst((_held(a),) + _lst(b))
    if sym == 'head':
        xs = _lst(a)
        return xs[0] if xs else (0 if pay is None else ())
    if sym == 'tail':
        return _lst(a)[1:]
    if sym == 'range':
        n = _num(a)
        if not float(n).is_integer() or n > MAX_LEN:
            raise Bad('no such range')
        return tuple(range(1, int(n) + 1))
    if sym in ('radd', 'rsub', 'rmul', 'rdiv'):          # real numbers (2026-09-28): out of range is Bad
        a, b = _real(a), _real(b)
        if sym == 'rdiv' and b == 0.0:
            raise Bad('no division by 0')
        return _real(a + b if sym == 'radd' else a - b if sym == 'rsub' else a * b if sym == 'rmul' else a / b)
    if sym in ('sqrt', 'exp', 'log', 'sin', 'cos'):
        a = _real(a)
        if (sym == 'sqrt' and a < 0) or (sym == 'log' and a <= 0) or (sym == 'exp' and a > 700):
            raise Bad('out of range')
        return _real({'sqrt': math.sqrt, 'exp': math.exp, 'log': math.log, 'sin': math.sin, 'cos': math.cos}[sym](a))
    raise Bad(f'unknown symbol {sym}')


def _each(sym, xs, body_at):
    """map, filter, mapi, filteri over the values xs; body_at(i, x) is the λ's body at the element x (its place i, from
    1)."""
    out = []
    keep = sym in ('filter', 'filteri')
    for i, x in enumerate(xs, 1):
        y = body_at(i, x)
        if not keep:
            out.append(_held(y))
        elif not isinstance(y, bool):
            raise Bad('not a truth')
        elif y:
            out.append(x)
    return tuple(out)


def _fold(sym, acc, xs, body_at):
    for x in xs:
        acc = body_at(acc, x)
        acc = _num(acc) if sym == 'foldn' else _lst(acc)
    return acc


def evaluate(p, env, concepts):
    """The value of p in env ({name: value}); concepts: {id: (body, argument name)}. Raises Bad on anything out of
    range (a value too large, a list too long, a type error, too many steps)."""
    st = [0]
    return _ev(p, {k: freeze(v) for k, v in env.items()}, concepts, st)


def _ev(p, env, cs, st):
    if EXECUTION_COUNTS is not None:
        EXECUTION_COUNTS['interpreter_calls'] += int(st[0] == 0)
        EXECUTION_COUNTS['interpreter_steps'] += 1
    st[0] += 1
    if st[0] > MAX_STEPS:
        raise Bad('too many steps')
    sym, pay = p[0], p[1]
    if sym == 'var':
        if pay not in env:
            raise Bad(f'no {pay}')
        return env[pay]
    if sym == 'zero':
        return 0
    if sym == 'one':
        return 1
    if sym == 'lit':                                    # a number it perceives in the task (2026-09-28)
        return pay
    if sym == 'rone':
        return 1.0
    if sym == 'nil':
        return ()
    if sym == 'if':
        c = _ev(p[2], env, cs, st)
        if not isinstance(c, bool):
            raise Bad('not a truth')
        return _ev(p[3] if c else p[4], env, cs, st)
    if sym in ('map', 'filter', 'mapi', 'filteri'):
        body = p[2][2]
        xs = _lst(_ev(p[3], env, cs, st))
        if sym in ('mapi', 'filteri'):
            return _each(sym, xs, lambda i, x: _ev(body, dict(env, e=x, i=i), cs, st))
        return _each(sym, xs, lambda i, x: _ev(body, dict(env, e=x), cs, st))
    if sym in ('foldn', 'foldl'):
        body = p[2][2]
        acc = _ev(p[3], env, cs, st)
        xs = _lst(_ev(p[4], env, cs, st))
        return _fold(sym, acc, xs, lambda a, x: _ev(body, dict(env, a=a, e=x), cs, st))
    if sym == 'tab':                                    # a concept shaped from measurements: its knots, joined
        grid, knots = pay                               # by straight lines, flat beyond the ends (a free curve's form)
        x = _num(_ev(p[2], env, cs, st)) if len(p) > 2 else _num(env['_'])   # of its input (a kept foothold's own)
        return float(np.interp(x, grid, knots))
    if sym == 'c':
        body, arg = cs[pay]
        x = _ev(p[2], env, cs, st)
        return _ev(body, {arg: x}, cs, st)
    if len(p) == 3:
        return _prim(sym, pay, _ev(p[2], env, cs, st))
    if len(p) == 4:
        return _prim(sym, pay, _ev(p[2], env, cs, st), _ev(p[3], env, cs, st))
    raise Bad(f'unknown symbol {sym}')


def seen_as(v):
    """A value as a behaviour is told apart by (a measured number to 9 decimals)."""
    return round(v, 9) if isinstance(v, float) else v


def safe(p, env, concepts):
    try:
        v = evaluate(p, env, concepts)
    except BAD:
        return None
    return seen_as(v)


# --- search: every behaviour up to a size ---
def probe_values(t, role='e'):
    """Values of a type that tell a λ's bodies apart (a λ is a function of what it binds; two bodies that agree on
    these are one to it). Numbers as they always were; lists of every depth, short and varied."""
    if t == 'num':
        return {'e': (-3, -1, 0, 1, 2, 5), 'ie': (-2, 0, 1, 3, 7), 'ae': (-2, 0, 1, 3), 'acc': (-1, 0, 2, 7)}[role]
    if t == 'list':
        return ((), (1,), (2, -1), (0, 3, 3)) if role == 'acc' else ((), (1,), (2, -1), (0, 3, 3), (5, 1, 4, 2))
    inner = probe_values(elem(t), 'e')
    return ((), (inner[1],), (inner[2], inner[3]), (inner[3], inner[1], inner[2]), (inner[4], inner[4]))


_BOUND = ('e', 'i', 'a')          # what a λ binds (a world input of the same name is hidden inside it)


def _held_of(v, t, out, most=64):
    """Up to `most` values of type t held anywhere in v (the elements a λ over part of v can meet)."""
    if len(out) >= most:
        return out
    if t == 'num' and isinstance(v, int) and not isinstance(v, bool):
        if v not in out:
            out.append(v)
    elif isinstance(v, tuple):
        if is_list(t) and depth(t) == _depth_of(v) and v not in out:
            out.append(v)
        for u in v:
            _held_of(u, t, out, most)
    return out


def _depth_of(v):
    n = 0
    while isinstance(v, tuple):
        n += 1
        v = next((u for u in v if isinstance(u, tuple)), v[0] if v else None)
    return n


def lambda_bodies(kind, out, max_size, acc_type='num', probes=None, concepts=None, constants=(), elem_type='num',
                  sees=(), work=None, order=None, namespace=None, chunk=None):
    """[(body, size)] for a lambda binding e (kind 'e'), i, e (kind 'ie': the element's place, from 1) or a, e (kind
    'ae'), one per behaviour on probe values; `constants`: the numbers it perceives in the task; `elem_type`: what the
    list it iterates over holds.
    sees: [(name, type, values)] - what around the λ it may see besides what it binds (a way of seeing SERA grows for
    itself, 2026-09-28, sera.one): the world's inputs, each with its value at every probe of the search. Then each of
    the λ's own probes meets each of those values (with elements that value really holds among its probes), and only
    bodies that use what they see are returned - the others are the λ's it has without seeing.
    work: as in _grow - a body size cut by the bound continues when asked again with a larger one (S10, reviewer: without
    it a size cut at MAX_WORK lost its rest for good, however long SERA thought)."""
    concepts = concepts or {}
    lits = [('num', node('lit', payload=k)) for k in constants]
    if kind == 'e':
        envs = [dict(e=e) for e in (probes or probe_values(elem_type, 'e'))]
        leaves = [(elem_type, node('var', payload='e'))] + lits
    elif kind == 'ie':
        envs = [dict(i=i, e=e) for i in (1, 2, 3, 5, 8) for e in (probes or probe_values(elem_type, 'ie'))]
        leaves = [('num', node('var', payload='i')), (elem_type, node('var', payload='e'))] + lits
    else:
        es = probes or probe_values(elem_type, 'ae')
        accs = probe_values(acc_type, 'acc')
        envs = [dict(a=a, e=e) for a in accs for e in es]
        leaves = [(elem_type, node('var', payload='e')), (acc_type, node('var', payload='a'))] + lits
    sees = [sv for sv in sees if sv[0] not in _BOUND]          # a bound name hides an input of the same name
    if sees:
        own = envs
        rests = []                                     # the λ's own probes without the element (its place, its
        for env in own:                                # accumulator), once each
            r = {k: v for k, v in env.items() if k != 'e'}
            if r not in rests:
                rests.append(r)
        envs = []
        for j in range(len(sees[0][2])):
            around = {name: freeze(vals[j]) for name, _, vals in sees}
            real = []
            for v in around.values():
                _held_of(v, elem_type, real)
            envs += [dict(around, **env) for env in own]            # what the λ binds comes first
            envs += [dict(around, **r, e=x) for x in real for r in rests]
        leaves = leaves + [(t, node('var', payload=name)) for name, t, _ in sees]
    lists = is_list(acc_type) or kind == 'ae' or is_list(elem_type) or any(is_list(t) for _, t, _ in sees)
    types = universe([t for t, _ in leaves] + [out], lists)
    table = _grow(leaves, envs, max_size, concepts, allow_lists=lists, types=types, work=work,
                  order=order, namespace=namespace, chunk=chunk)
    names = {name for name, _, _ in sees}
    return [(p, s) for p, s, _ in table.get(out, [])
            if not names or any(q == ('var', n) for q in parts(p) for n in names)]


def sees(p):
    """Does an expression hold a λ that sees beyond what it binds (the input around it)?"""
    if p[0] == 'lam':
        stack = [p[2]]
        while stack:
            q = stack.pop()
            if q[0] == 'var' and q[1] not in _BOUND:
                return True
            stack.extend(q[2:])
    return any(sees(k) for k in p[2:])


_TABLES = {}                     # a search kept per task (inputs, probes, concepts): a bigger one continues it
TABLE_BUDGET = 1_500_000         # behaviours and memoized bodies all kept searches may hold together (2026-09-29: the
                                 # laptop ran out of memory on 'where is' - a table per level, per wish view and per
                                 # concept set, each holding stories, and none let go); the least recently used go
                                 # first, and a search asked again is rebuilt with the same results


MEMORY_SHARE = 0.4               # of the machine's memory a SERA's searches may take before it stops thinking bigger
MEMORY_FREE = 0.15               # and it stops thinking bigger when less than this share of the machine is free (other
#                                  SERAs, other programs: its wall counts the machine, not only itself; the laptop
#                                  runs with about 30% free, so the floor is under that)
MEMORY_STOPS = [0]               # how often a search stopped at that wall (a world's record reads it)
COMPLETE = [False]               # did the last search look through every size it was asked for (no bound, time or
                                 # memory wall cut it)? A 'no' from a search that did not is no evidence (S03, reviewer)
_MEMORY = {}


def _win_counters():
    """The process's memory counters on Windows (one ctypes setup for every caller), or None."""
    import ctypes
    from ctypes import wintypes
    if 'info' not in _MEMORY:
        class Counters(ctypes.Structure):
            _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
                (n, ctypes.c_size_t) for n in ('PeakWorkingSetSize', 'WorkingSetSize', 'QPPPU', 'QPPU', 'QPNPPU',
                                               'QNPPU', 'PagefileUsage', 'PeakPagefileUsage')]
        k = ctypes.WinDLL('kernel32', use_last_error=True)          # its own handle: no shared argtypes
        k.GetCurrentProcess.restype = wintypes.HANDLE
        f = k.K32GetProcessMemoryInfo
        f.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
        f.restype = wintypes.BOOL
        _MEMORY['info'] = (f, k.GetCurrentProcess(), Counters)
    f, proc, counters = _MEMORY['info']
    c = counters()
    c.cb = ctypes.sizeof(c)
    return c if f(proc, ctypes.byref(c), c.cb) else None


def _rss_mb():
    """This process's memory in use now, in MB (Linux, Windows; None if unknown)."""
    try:
        if sys.platform == 'win32':
            c = _win_counters()
            return c.WorkingSetSize / 2 ** 20 if c is not None else None
        with open('/proc/self/statm') as fh:
            return int(fh.read().split()[1]) * os.sysconf('SC_PAGE_SIZE') / 2 ** 20
    except (OSError, AttributeError, ValueError):
        return None


def _memory_limit_mb():
    """MEMORY_SHARE of the machine's memory, in MB (None if unknown)."""
    if 'limit' not in _MEMORY:
        total = None
        try:
            if sys.platform == 'win32':
                import ctypes

                class Status(ctypes.Structure):
                    _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong)] + [
                        (n, ctypes.c_ulonglong) for n in ('total', 'avail', 'tpf', 'apf', 'tv', 'av', 'aev')]
                st = Status()
                st.dwLength = ctypes.sizeof(st)
                if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st)):
                    total = st.total / 2 ** 20
            else:
                total = os.sysconf('SC_PHYS_PAGES') * os.sysconf('SC_PAGE_SIZE') / 2 ** 20
        except (OSError, AttributeError, ValueError):
            total = None
        _MEMORY['limit'] = total * MEMORY_SHARE if total else None
    return _MEMORY['limit']


def _machine_free_share():
    """The share of the machine's memory still free for new work (Linux MemAvailable, Windows ullAvailPhys), or None."""
    try:
        if sys.platform == 'win32':
            import ctypes

            class Status(ctypes.Structure):
                _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong)] + [
                    (n, ctypes.c_ulonglong) for n in ('total', 'avail', 'tpf', 'apf', 'tv', 'av', 'aev')]
            st = Status()
            st.dwLength = ctypes.sizeof(st)
            return st.avail / st.total if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(st)) else None
        info = {}
        with open('/proc/meminfo') as fh:
            for line in fh:
                k, v = line.split(':', 1)
                info[k] = float(v.split()[0])
        return info['MemAvailable'] / info['MemTotal']
    except (OSError, AttributeError, ValueError, KeyError, ZeroDivisionError):
        return None


def _over_memory():
    """Is this process past its share of the machine's memory, or is the machine itself short (less than
    MEMORY_FREE of it free)? (2026-09-29: on 'where is' at size 11 one search held 4.6 GB, and the laptop's run was
    stopped for lack of memory; a wall like the time box, not a crash. Later that day, the author: "colab run is showing
    ram spikes" - two SERAs side by side, 17 GB each, and each wall counted only itself: now the machine counts too.)"""
    limit = _memory_limit_mb()
    if limit is None:
        return False
    now = _rss_mb()
    if now is not None and now > limit:
        return True
    free = _machine_free_share()
    return free is not None and free < MEMORY_FREE


def _held_by(state):
    return len(state['seen']) + len(state['memo'])


def forget_searches():
    """Let go of every kept search (a new world: its probes are its own)."""
    _TABLES.clear()
MAX_WORK = 150_000               # candidate expressions tried per size (a bound on thinking, not on what exists)
IF_PART = 3                      # the parts of a choice are at most this big
DEADLINE = [math.inf]            # a world's time box (set by the mind): a size not finished by then is thought again
_MISS = object()
_KIND = {'map': 'e', 'filter': 'e', 'mapi': 'ie', 'filteri': 'ie', 'foldn': 'ae', 'foldl': 'ae'}


def _table_key(concepts):
    return repr(sorted(((k, v) for k, v in concepts.items() if k != '_sig'), key=lambda kv: repr(kv[0]))) + repr(
        sorted((concepts.get('_sig') or {}).items()))


def _values(p, envs, concepts):
    vals, steps = [], []
    for env in envs:
        st = [0]
        try:
            vals.append(_ev(p, env, concepts, st))
        except BAD:
            return None
        steps.append(st[0])
    return tuple(vals), tuple(steps)


def _grow(leaves, envs, max_size, concepts, allow_lists=True, lambdas=None, types=None, work=None, if_part=IF_PART,
          order=None, namespace=None, chunk=None):
    """Bottom-up search: {type: [(expression, size, values)]} with one expression per behaviour on envs. A search with
    the same inputs, probes, concepts and lambdas continues from the size it reached (growing never repeats work).
    Each expression's values (and its evaluation steps, bounded as in evaluate) are made from its parts' values: a
    symbol applied once, a λ's body once per element it has not met before (2026-09-28).
    work: candidates tried per size. None: at most MAX_WORK, then on to the next size (the rest of that size is never
    tried). A number (2026-09-28, ARC: a program cut off at 9 nodes was out of reach for good, however long SERA
    thought): a size is finished before a bigger one is begun; one cut by the bound continues where it stopped when the
    search is asked again with a larger bound - so everything its language can say is reached in time."""
    types = [t for t in (types or universe([t for t, _ in leaves], allow_lists)) if allow_lists or not is_list(t)]
    if order is not None:
        types = sorted(types, key=lambda t: (depth(t), t))
    tkey = (repr(leaves), repr(envs), _table_key(concepts), repr(lambdas), allow_lists, tuple(types), if_part)
    if order is not None or namespace is not None:
        tkey += (namespace, tuple(sorted((order or {}).items(), key=lambda kv: repr(kv[0]))))
    state = _TABLES.pop(tkey, None)
    if state is None:
        state = dict(seen={}, by={}, done=0, memo={})
    _TABLES[tkey] = state                          # the most recently used last
    held = sum(_held_by(t) for t in _TABLES.values())
    for k in list(_TABLES):
        if held <= TABLE_BUDGET or k == tkey:
            break
        held -= _held_by(_TABLES.pop(k))
    seen, by, memo = state['seen'], state['by'], state['memo']
    for s in range(1, max_size + 1):
        by.setdefault(s, {t: [] for t in types})
    envs = [{k: freeze(v) for k, v in env.items()} for env in envs]
    n = len(envs)

    def add(typ, p, s, vals, steps):
        key = (typ, tuple(seen_as(v) for v in vals))
        if key in seen:
            return
        seen[key] = (p, s, vals)
        by[s][typ].append((p, vals, steps))

    if state['done'] < 1:
        reals = any(t == 'real' for t, _ in leaves)
        base = leaves + ([('real', node('rone'))] if reals else []) + [('num', node('zero')), ('num', node('one'))]
        if allow_lists:
            base += [(t, node('nil')) for t in types if is_list(t)]
        if order is not None:
            base.sort(key=lambda q: (-order.get(('c', q[1][1]) if q[1][0] == 'c' else
                                               (q[1][0], q[1][1]), 0.), repr(q)))
        for typ, p in base:
            r = _values(p, envs, concepts)
            if r is not None:
                add(typ, p, 1, *r)
        state['done'] = 1
    unary, binary = [], []
    for name, (args, r) in INNATE.items():
        if len(args) not in (1, 2) or args[0].startswith('lam'):
            continue
        for a, rr, sub in instances(args, r, types):
            pay = sub['T'] if name == 'head' and sub.get('T', 'num') != 'num' else None
            (unary if len(args) == 1 else binary).append((name, a, rr, pay))
    cons_list = [(cid, a[0], r) for cid, sig in (concepts.get('_sig') or {}).items()
                 for a, r, _ in instances((sig[0],), sig[1], types)]
    lams = list(enumerate(lambdas or ()))
    if order is not None:
        rank = lambda name, pay=None: -order.get((name, pay), order.get((name, None), 0.))
        unary.sort(key=lambda q: (rank(q[0], q[3]), repr(q)))
        binary.sort(key=lambda q: (rank(q[0], q[3]), repr(q)))
        cons_list.sort(key=lambda q: (rank('c', q[0]), repr(q)))
        lams.sort(key=lambda q: (rank(q[1][0]), repr(q[1])))
    lams_by_id = dict(lams)                         # sorting never changes a body's captured environment

    def run(key, body, env, cnt):                      # a body (a λ's or a concept's) at one binding, once
        hit = memo.get(key, _MISS)
        if hit is _MISS:
            st = [0]
            try:
                hit = (_ev(body, env, concepts, st), st[0])
            except BAD:
                hit = None
            memo[key] = hit
        if hit is None:
            raise Bad('its body fails here')
        cnt[0] += hit[1]
        return hit[0]

    def around(lid, j):                                # what a λ that sees sees at probe j (else nothing)
        entry = lams_by_id[lid]
        names = entry[5] if len(entry) > 5 else ()
        return ({k: envs[j][k] for k in names}, j) if names else ({}, None)

    def each(name, lid, body, q):
        vals, steps = [], []
        ie = name in ('mapi', 'filteri')
        for j in range(n):
            cnt = [1 + q[2][j]]
            out_, at = around(lid, j)
            try:
                xs = _lst(q[1][j])
                if ie:
                    v = _each(name, xs, lambda i, x: run((lid, at, i, x), body, dict(out_, e=x, i=i), cnt))
                else:
                    v = _each(name, xs, lambda i, x: run((lid, at, x), body, dict(out_, e=x), cnt))
            except BAD:
                return None
            if cnt[0] > MAX_STEPS:
                return None
            vals.append(v)
            steps.append(cnt[0])
        return tuple(vals), tuple(steps)

    def fold(name, lid, body, q1, q2):
        vals, steps = [], []
        for j in range(n):
            cnt = [1 + q1[2][j] + q2[2][j]]
            out_, at = around(lid, j)
            try:
                v = _fold(name, q1[1][j], _lst(q2[1][j]),
                          lambda a, x: run((lid, at, a, x), body, dict(out_, a=a, e=x), cnt))
            except BAD:
                return None
            if cnt[0] > MAX_STEPS:
                return None
            vals.append(v)
            steps.append(cnt[0])
        return tuple(vals), tuple(steps)

    def prim1(name, pay, q):
        vals, steps = [], []
        for j in range(n):
            try:
                vals.append(_prim(name, pay, q[1][j]))
            except BAD:
                return None
            if q[2][j] >= MAX_STEPS:
                return None
            steps.append(1 + q[2][j])
        return tuple(vals), tuple(steps)

    def prim2(name, pay, q1, q2):
        vals, steps = [], []
        for j in range(n):
            try:
                vals.append(_prim(name, pay, q1[1][j], q2[1][j]))
            except BAD:
                return None
            c = 1 + q1[2][j] + q2[2][j]
            if c > MAX_STEPS:
                return None
            steps.append(c)
        return tuple(vals), tuple(steps)

    def concept(cid, q):
        body, arg = concepts[cid]
        vals, steps = [], []
        for j in range(n):
            cnt = [1 + q[2][j]]
            x = q[1][j]
            try:
                vals.append(run(('c', cid, x), body, {arg: x}, cnt))
            except BAD:
                return None
            if cnt[0] > MAX_STEPS:
                return None
            steps.append(cnt[0])
        return tuple(vals), tuple(steps)

    def choose(c, q1, q2):
        vals, steps = [], []
        for j in range(n):
            b = c[1][j]
            if not isinstance(b, bool):
                return None
            q = q1 if b else q2
            k = 1 + c[2][j] + q[2][j]
            if k > MAX_STEPS:
                return None
            vals.append(q[1][j])
            steps.append(k)
        return tuple(vals), tuple(steps)

    def lambda_family(s):
        for lid, (name, body, bsize, argtypes, ret, *_) in lams:   # iteration first: its forms are few and often needed
            rest = s - 1 - (1 + bsize)
            if rest < 1:
                continue
            lam = node('lam', body, payload=_KIND[name])
            if len(argtypes) == 1:
                for q in by[rest][argtypes[0]]:
                    r = each(name, lid, body, q)
                    if r is not None:
                        add(ret, node(name, lam, q[0]), s, *r)
                    yield
            else:
                for k in range(1, rest):
                    for q1 in by[k][argtypes[0]]:
                        for q2 in by[rest - k][argtypes[1]]:
                            r = fold(name, lid, body, q1, q2)
                            if r is not None:
                                add(ret, node(name, lam, q1[0], q2[0]), s, *r)
                            yield
    def unary_family(s):
        for name, (a,), r, pay in unary:
            for q in by[s - 1][a]:
                v = prim1(name, pay, q)
                if v is not None:
                    add(r, node(name, q[0], payload=pay), s, *v)
                yield
    def concept_family(s):
        for cid, a, r in cons_list:
            for q in by[s - 1][a]:
                v = concept(cid, q)
                if v is not None:
                    add(r, node('c', q[0], payload=cid), s, *v)
                yield
    def binary_family(s):
        for k in range(1, s - 1):                      # smaller parts first: the work bound keeps the simplest
            for name, (a1, a2), r, pay in binary:
                for q1 in by[k][a1]:
                    for q2 in by[s - 1 - k][a2]:
                        v = prim2(name, pay, q1, q2)
                        if v is not None:
                            add(r, node(name, q1[0], q2[0]), s, *v)
                        yield
    def choice_family(s):
        if s >= 4:                                     # choosing: a small condition, small branches
            for k in range(1, min(s - 2, if_part) + 1):
                for c in by[k]['bool']:
                    for k2 in range(1, min(s - 1 - k, if_part + 1)):
                        k3 = s - 1 - k - k2
                        if k3 < 1 or k3 > if_part:
                            continue
                        for q1 in by[k2]['num']:
                            for q2 in by[k3]['num']:
                                v = choose(c, q1, q2)
                                if v is not None:
                                    add('num', node('if', c[0], q1[0], q2[0]), s, *v)
                                yield

    def sized(s):
        families = [(lambda_family, [q[1][0] for q in lams]),
                    (unary_family, [q[0] for q in unary]),
                    (concept_family, [('c', q[0]) for q in cons_list]),
                    (binary_family, [q[0] for q in binary]), (choice_family, ['if'])]
        if order is not None:
            def family_rank(item):
                scores = [order.get(k if isinstance(k, tuple) else (k, None), 0.) for k in item[1]]
                return -max(scores, default=-math.inf)
            families.sort(key=family_rank)         # stable: the old family order breaks ties
        for family, _ in families:
            yield from family(s)                   # never sort/materialize a Cartesian product

    gens, spent = state.setdefault('gens', {}), state.setdefault('spent', {})
    chunk_spent = 0
    bound = MAX_WORK if work is None else work
    for s in range(state['done'] + 1, max_size + 1):
        if s not in gens:
            gens[s], spent[s] = sized(s), 0
        finished = late = False
        while spent[s] < bound:
            if chunk is not None and chunk_spent >= chunk:
                late = True
                break
            if not spent[s] & 255 and time.time() > DEADLINE[0]:
                late = True
                break
            if not spent[s] & 4095 and spent[s] and _over_memory():
                MEMORY_STOPS[0] += 1           # it thinks with what it has; this size waits, as at the time box
                late = True
                break
            try:
                next(gens[s])
            except StopIteration:
                finished = True
                break
            spent[s] += 1
            chunk_spent += 1
        state.setdefault('capped', {})[s] = not finished
        if late:
            break                                      # the time box ended inside this size: it continues next time
        if finished or work is None:                   # (no bound given: a size's rest is never tried, as always)
            del gens[s]
            state['done'] = s
            continue
        break                                          # cut by the bound: a bigger size waits until it is finished
    if len(memo) > 2_000_000:
        memo.clear()
    COMPLETE[0] = state['done'] >= max_size and not any(state.get('capped', {}).values())   # every size up to
    out = {}                                                                                  # max_size looked through
    for (typ, _), (p, s, vals) in seen.items():
        if s <= max_size:
            out.setdefault(typ, []).append((p, s, vals))
    for typ in out:
        out[typ].sort(key=lambda r: (r[1], repr(r[0])))
    return out


def search(inputs, out_type, probes, max_size, concepts=None, lambda_size=3, constants=(), values=False, work=None,
           if_part=IF_PART, sees=False, order=None, namespace=None, chunk=None):
    """Every expression of `out_type` over the task's inputs ({name: type}) up to `max_size` nodes, one per behaviour on
    the probe environments. concepts: {id: (body, arg)} plus '_sig': {id: (arg type, result type)}. Returns
    [(expression, size)], shortest first; with values, [(expression, size, its values on the probes)]. work: the
    bound on candidates per size (_grow); if_part: the largest part of a choice (it may think bigger there too).
    sees: its λ's may also see the task's inputs around them (a way of seeing SERA grows itself, sera.one; with
    False the search is exactly as before). True: their bodies are as big as lambda_size; a number: as big as that (a
    λ that sees the whole problem does the program's work in its body)."""
    concepts = concepts or {}
    leaves = [(typ, node('var', payload=name)) for name, typ in inputs.items()]
    leaves += [('num', node('lit', payload=k)) for k in constants]          # numbers it perceives in the task
    uses_lists = any(is_list(t) for t in inputs.values()) or is_list(out_type)
    only_real = bool(inputs) and all(t == 'real' for t in inputs.values())
    types = universe(list(inputs.values()) + [out_type], not only_real)
    lambdas = []
    bodies_complete = True                     # were the λ bodies it drew from searched through too? (S04 R2, reviewer: a
    if uses_lists or any(t == 'num' for t in inputs.values()):                         # finished outer table over cut
        for name, (args, r) in INNATE.items():                                         # bodies is not a finished search)
            if not args or not args[0].startswith('lam'):
                continue
            for a, ret, sub in instances(args, r, types):
                kind, lam_out = a[0][4:].split('>')
                acc = a[1] if kind == 'ae' else 'num'
                bodies = lambda_bodies(kind, lam_out, lambda_size, acc_type=acc, concepts=concepts,
                                       constants=constants, elem_type=sub.get('T', 'num'), work=work,
                                       order=order, namespace=namespace, chunk=chunk)
                bodies_complete = bodies_complete and COMPLETE[0]
                for body, bsize in bodies:
                    lambdas.append((name, body, bsize, a[1:], ret))
                if sees:
                    around = [(k, t, [pr[k] for pr in probes]) for k, t in inputs.items() if k not in _BOUND]
                    sees_size = lambda_size if sees is True else int(sees)
                    bodies = lambda_bodies(kind, lam_out, sees_size, acc_type=acc, concepts=concepts,
                                           constants=constants, elem_type=sub.get('T', 'num'), sees=around, work=work,
                                           order=order, namespace=namespace, chunk=chunk)
                    bodies_complete = bodies_complete and COMPLETE[0]
                    for body, bsize in bodies:
                        lambdas.append((name, body, bsize, a[1:], ret, tuple(k for k in inputs if k not in _BOUND)))
    table = _grow(leaves, probes, max_size, concepts, allow_lists=not only_real,
                  lambdas=lambdas if max_size >= 4 else (), types=types, work=work, if_part=if_part,
                  order=order, namespace=namespace, chunk=chunk)
    COMPLETE[0] = COMPLETE[0] and bodies_complete
    found = table.get(out_type, [])
    return found if values else [(p, s) for p, s, _ in found]
