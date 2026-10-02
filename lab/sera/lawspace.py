"""The law language of SERA v3, batch B1: the laws the frozen judge (tag truth-v1) can certify, spelled in pieces.

A law is a canonical ccops5 family (`ccops5.core.grammar`): at most two force terms, at most one of them invented.
  base idea  (input, shape)                  input position / speed, shape straight growing steps cubic wave;
                                             or ('nothing', 'steady'), a constant force
  product    ('product', shape_x, shape_v)   e.g. x*v = ('product', 'straight', 'straight')
  power      ('power', input, p)             |s|^p sign(s), p on grammar.P_GRID except 1, 2, 3
  drive      ('drive', 'sin' or 'cos', w)    a force swinging in time, w on grammar.W_GRID
The empty law () means "nothing but my hand".

The imagination writes a law as tokens, one choice per token, so a combination it never saw is spelled from pieces
it did see:   <bos> TERM TERM <eos>,  TERM = IDEA input shape | PROD shape shape | POW input p | DRV fn w
`Speller` enforces the grammar while decoding (only certifiable laws can be written; no term twice).
Later batches add pieces (library calls, grown cells); the judge must learn them first (decision D11).
"""
import math

from ccops5.core import grammar

SPECIAL = ('<pad>', '<bos>', '<eos>')
OPS = ('IDEA', 'PROD', 'POW', 'DRV')
INPUTS = ('position', 'speed', 'nothing')
SHAPES = grammar.SHAPES + ('steady',)
FNS = ('sin', 'cos')
P_VALUES = tuple(p for p in grammar.P_GRID if p not in (1.0, 2.0, 3.0))
W_VALUES = grammar.W_GRID
VOCAB = (SPECIAL + OPS + INPUTS + SHAPES + FNS + tuple(f'p{p:g}' for p in P_VALUES)
         + tuple(f'w{w:g}' for w in W_VALUES))
TOK = {name: i for i, name in enumerate(VOCAB)}
PAD, BOS, EOS = TOK['<pad>'], TOK['<bos>'], TOK['<eos>']
MAX_TERMS = 2
MAX_LEN = 1 + 3 * MAX_TERMS + 1          # <bos>, three tokens per term, <eos>


def is_open(term):
    return term[0] in ('product', 'power', 'drive')


def claimable(family):
    """True when the frozen judge can certify this family (D9 gives it a finite threshold)."""
    return grammar.log_prior(family) > -math.inf


def description_length(family):
    """-log pi(family) in nats under D9: the evidence price of claiming it, beyond log(1/alpha)."""
    return -grammar.log_prior(family)


def level(family):
    """The world level of a certifiable law: L0 none, L1 one idea, L2 two ideas, L3 one invented term alone,
    L4 one invented term with one idea. (L5+, beyond the frozen judge, is decided by the world generator.)"""
    fam = grammar.canonical(family)
    n_open = sum(is_open(t) for t in fam)
    if not fam:
        return 0
    if n_open == 0:
        return len(fam)
    return 3 if len(fam) == 1 else 4


def term_tokens(term):
    if term[0] == 'product':
        return ['PROD', term[1], term[2]]
    if term[0] == 'power':
        return ['POW', term[1], f'p{term[2]:g}']
    if term[0] == 'drive':
        return ['DRV', term[1], f'w{term[2]:g}']
    return ['IDEA', term[0], term[1]]


def encode(family):
    """Token ids of a family, terms in canonical order: [<bos>, ..., <eos>]."""
    fam = grammar.canonical(family)
    if not claimable(fam):
        raise ValueError(f'not certifiable by the frozen judge: {fam}')
    toks = ['<bos>'] + [tok for term in fam for tok in term_tokens(term)] + ['<eos>']
    return [TOK[t] for t in toks]


def decode(ids):
    """The family spelled by token ids (with or without <bos>; stops at <eos>). Raises on a malformed spelling."""
    names = [VOCAB[i] for i in ids]
    if names and names[0] == '<bos>':
        names = names[1:]
    terms, i = [], 0
    while i < len(names) and names[i] not in ('<eos>', '<pad>'):
        op, a, b = names[i:i + 3] if i + 3 <= len(names) else (names[i], None, None)
        if op == 'IDEA':
            terms.append((a, b))
        elif op == 'PROD':
            terms.append(('product', a, b))
        elif op == 'POW':
            terms.append(('power', a, float(b[1:])))
        elif op == 'DRV':
            terms.append(('drive', a, float(b[1:])))
        else:
            raise ValueError(f'bad spelling at {i}: {names}')
        i += 3
    fam = grammar.canonical(terms)
    if len(fam) != len(terms) or not claimable(fam):
        raise ValueError(f'not a certifiable family: {terms}')
    return fam


class Speller:
    """Grammar state while decoding one law: which tokens may come next."""

    def __init__(self):
        self.terms, self.part, self.done = [], [], False

    def allowed(self):
        """Names of the tokens allowed next."""
        if self.done:
            return ['<pad>']
        if not self.part:
            ops = []
            if len(self.terms) < MAX_TERMS:
                ops.append('IDEA')
                if not any(is_open(t) for t in self.terms):
                    ops += ['PROD', 'POW', 'DRV']
            return ops + ['<eos>']
        op = self.part[0]
        if len(self.part) == 1:
            return {'IDEA': list(INPUTS), 'PROD': list(grammar.SHAPES), 'POW': ['position', 'speed'],
                    'DRV': list(FNS)}[op]
        if op == 'IDEA':
            opts = ['steady'] if self.part[1] == 'nothing' else list(grammar.SHAPES)
            return [s for s in opts if (self.part[1], s) not in self.terms]
        if op == 'PROD':
            return [s for s in grammar.SHAPES if ('product', self.part[1], s) not in self.terms]
        if op == 'POW':
            return [f'p{p:g}' for p in P_VALUES]
        return [f'w{w:g}' for w in W_VALUES]

    def push(self, name):
        if name not in self.allowed():
            raise ValueError(f'{name} not allowed after {self.terms} {self.part}')
        if name == '<eos>':
            self.done = True
            return
        if name == '<pad>':
            return
        self.part.append(name)
        if len(self.part) == 3:
            op, a, b = self.part
            term = {'IDEA': lambda: (a, b), 'PROD': lambda: ('product', a, b),
                    'POW': lambda: ('power', a, float(b[1:])), 'DRV': lambda: ('drive', a, float(b[1:]))}[op]()
            self.terms.append(term)
            self.part = []

    def family(self):
        return grammar.canonical(self.terms)


def allowed_masks(ids):
    """For a token sequence starting with <bos>: one boolean list over VOCAB per position after <bos>, marking the
    tokens the grammar allowed at that position (used to train and sample with the grammar enforced)."""
    sp, masks = Speller(), []
    for i in ids[1:]:
        allowed = set(sp.allowed())
        masks.append([name in allowed for name in VOCAB])
        sp.push(VOCAB[i])
    return masks


def all_families():
    """Every family the frozen judge can certify (the full space the imagination writes in)."""
    base = grammar.space()
    opens = [(t,) for t in grammar.OPEN_TERMS] + [grammar.canonical((t, i)) for t in grammar.OPEN_TERMS
                                                 for i in grammar.IDEAS]
    return base + opens


def name(family):
    return grammar.name(grammar.canonical(family))
