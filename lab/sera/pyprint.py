"""The observer's printer (2026-09-30; the author: "I want it to be able to code"; plan 7.11 step 5): SERA's programs -
expressions of its own language - written as Python, faithfully. Nothing here is SERA's: it shows what SERA made, in a
language people run. Its test is exact: on every input where SERA's program gives an answer, the printed function
returns that answer (sera.lang.safe), words shown as words. Where its program gives none (a value out of its range, a
list too long, comparing lists), the Python may answer or fail: its language's limits are not printed.

  to_python(program, concepts, names, arg='x', words=False) -> Python source: the helpers its language's meanings need
  (a head of nothing is 0, a range counts from 1), one def per idea it uses (its own word for it), then `answer`.
"""
from . import lang as LG
from . import tasks as TS

HELPERS = '''from functools import reduce
import math


def head(xs):                 # its language: the first of a list; of nothing, 0
    return xs[0] if xs else 0


def head_list(xs):            # the first of a list of lists; of nothing, the empty list
    return xs[0] if xs else ()


def count_to(n):              # 1, 2, ..., n
    return tuple(range(1, int(n) + 1))
'''


class NotPrintable(Exception):
    pass


TAKEN = {'head', 'head_list', 'count_to', 'reduce', 'math', 'answer', 'tuple', 'enumerate', 'range', 'e', 'i', 'a',
         'x', 'g'}


def _name(s, used):
    """Its own word for an idea, as a Python name: not a keyword (its idea 'in'), not a helper's, not another idea's."""
    import keyword
    s = ''.join(ch if ch.isalnum() else '_' for ch in str(s))
    s = s if s and not s[0].isdigit() else 'idea_' + s
    while keyword.iskeyword(s) or s in TAKEN or s in used:
        s += '_'
    return s


def _var(v):
    return 'x' if v == '_' else str(v)


class _Printer:
    def __init__(self, concepts, names, words):
        self.concepts, self.names, self.words = concepts, names, words
        self.defs = {}                                    # concept id -> python name, in the order first met

    def lit(self, v):
        if self.words and isinstance(v, int) and not isinstance(v, bool) and v in TS.WORDS:
            return repr(TS.text(v))
        if isinstance(v, (int, float)):
            return repr(v)
        raise NotPrintable(f'a literal {v!r}')

    def ex(self, p):
        sym, pay, kids = p[0], p[1], p[2:]
        if sym == 'var':
            return _var(pay)
        if sym == 'zero':
            return '0'
        if sym == 'one':
            return '1'
        if sym == 'rone':
            return '1.0'
        if sym == 'nil':
            return '()'
        if sym == 'lit':
            return self.lit(pay)
        if sym == 'if':
            return f'({self.ex(kids[1])} if {self.ex(kids[0])} else {self.ex(kids[2])})'
        if sym in ('map', 'filter', 'mapi', 'filteri'):
            body, xs = self.ex(kids[0][2]), self.ex(kids[1])
            each = 'i, e' if sym in ('mapi', 'filteri') else 'e'
            src = f'enumerate({xs}, 1)' if sym in ('mapi', 'filteri') else xs
            if sym in ('map', 'mapi'):
                return f'tuple({body} for {each} in {src})'
            return f'tuple(e for {each} in {src} if {body})'
        if sym in ('foldn', 'foldl'):
            return f'reduce(lambda a, e: {self.ex(kids[0][2])}, {self.ex(kids[2])}, {self.ex(kids[1])})'
        if sym == 'c':
            if pay not in self.defs:
                self.defs[pay] = _name(self.names.get(pay, f'c{pay}'), set(self.defs.values()))
                self.define(pay)
            return f'{self.defs[pay]}({self.ex(kids[0])})'
        if sym == 'head':
            return f'{"head" if pay is None else "head_list"}({self.ex(kids[0])})'
        if sym == 'tail':
            return f'{self.ex(kids[0])}[1:]'
        if sym == 'cons':
            return f'(({self.ex(kids[0])},) + {self.ex(kids[1])})'
        if sym == 'range':
            return f'count_to({self.ex(kids[0])})'
        ops = {'add': '+', 'sub': '-', 'mul': '*', 'lt': '<', 'eq': '==', 'radd': '+', 'rsub': '-', 'rmul': '*',
               'rdiv': '/'}
        if sym in ops:
            return f'({self.ex(kids[0])} {ops[sym]} {self.ex(kids[1])})'
        if sym in ('sqrt', 'exp', 'log', 'sin', 'cos'):
            return f'math.{sym}({self.ex(kids[0])})'
        raise NotPrintable(f'the symbol {sym}')

    def define(self, cid):
        body, arg = self.concepts[cid]
        self.defs_src = getattr(self, 'defs_src', [])
        src = self.ex(body)                               # the ideas it is made of are defined first
        self.defs_src.append(f'def {self.defs[cid]}({_var(arg)}):\n    return {src}\n')


def to_python(program, concepts, names, arg='x', words=False):
    """Python source for a program of its language: the helpers, its ideas used (each a def, named by its own word),
    and `answer(<arg>)`. Raises NotPrintable for what Python cannot say faithfully here (a drawn curve)."""
    pr = _Printer(concepts, names, words)
    main = pr.ex(program)
    parts = [HELPERS] + getattr(pr, 'defs_src', []) + [f'def answer({_var(arg)}):\n    return {main}\n']
    return '\n\n'.join(parts)


def module(field):
    """All its proven ideas (Field.proven_ideas) as one Python module: the helpers, then each idea as a def named by
    its own word, with where it learned it; words shown as words in the ideas of language. An idea Python cannot say
    faithfully (a drawn curve) is listed as a comment."""
    concepts, names = field.concept_table(), field.names()
    proven = field.proven_ideas()
    pr = _Printer(concepts, names, False)
    notes = []
    for c in field.concepts:
        if c['id'] not in proven or c['id'] in pr.defs:
            continue
        pr.words = c.get('subject') == 'language'
        try:
            pr.ex(LG.node('c', LG.node('var', payload='x'), payload=c['id']))
        except NotPrintable as e:
            notes.append(f"# {names.get(c['id'], c['id'])}: not printed ({e}; learned in {c.get('born')})")
    born = {pr.defs[c['id']]: c for c in field.concepts if c['id'] in pr.defs}
    out = []
    for src in getattr(pr, 'defs_src', []):
        name = src.split('(', 1)[0][4:]
        c = born.get(name)
        if c is not None:
            out.append(f"# its idea '{names.get(c['id'], c['id'])}': {c.get('sig')[0]} -> {c.get('sig')[1]}, "
                       f"learned in '{c.get('born')}' ({c.get('subject')})\n{src}")
    head = '"""SERA\'s proven ideas, written in Python by the observer\'s printer (sera.pyprint)."""\n'
    return '\n\n'.join([head + HELPERS] + out + notes) + '\n'


def as_words(v):
    """A value of its language as people read it (words as words)."""
    if isinstance(v, tuple):
        return tuple(as_words(u) for u in v)
    if isinstance(v, int) and not isinstance(v, bool) and v in TS.WORDS:
        return TS.text(v)
    return v


def run(source, x):
    """Run printed source on an input (the observer checks the printer with it)."""
    space = {}
    exec(compile(source, '<sera>', 'exec'), space)
    return space['answer'](x)
