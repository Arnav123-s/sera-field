"""SERA's first words (plan revision 5, WP3): three slots of five words, each heard without its meaning.

The caretaker (sera.caretaker) says one word from a slot about the law of the world SERA is in. SERA must learn
which word names which property of a law, the way the playroom design does it (docs/SERA_PLAYROOM.md §2-3, reviewed by
independent review):
- **Slots and properties** (each word names one of its slot's five properties, a function of the law alone):

  | slot | words (their order is not their meaning) | the five properties |
  |---|---|---|
  | depends on | where, how fast, when, both, nothing | uses position; uses speed; uses time; uses position and speed; uses nothing |
  | shape | straight, growing, steps, cubic, wave | has a part of that shape (an idea, or a factor of a product) |
  | kind | plain, times, power, rhythm, steady | only simple ideas; a product; a power; a time drive; a steady push |

- **The caretaker's likelihood is exact by construction:** it says a word uniformly among the words true of the law
  under the true lexicon, and with slip rate EPS a uniformly random word of the slot; with no true word, a uniformly
  random word. So p(w | L, h) = (1 - EPS) 1[L(w) true of h] / N_true(h) + EPS / 5, and N_true(h) (the number of the
  slot's properties true of h) does not depend on L, because L is a bijection.
- **The lexicon** of a slot is one of the 5! = 120 bijections words -> properties. Its posterior is exact (a finite
  sum). SERA learns it from sentences heard about a law it is later told (Stage 1: the caretaker names the law).
- **Words act on belief, never on the judge.** A sentence heard during a world multiplies the Field's belief over laws
  by sum_L p(L) prod_j p(w_j | L, h), exactly (all sentences of the slot at once). One sentence moves the odds between
  two laws by at most log((1 - EPS + EPS/5) * 5 / EPS) = 4.6 nats; an ungrounded word (a flat lexicon) by nothing.
"""
import itertools
import math

import numpy as np

from ccops5.core import grammar
from . import field as F

EPS = 0.05
SLOTS = ('depends on', 'shape', 'kind')
WORDS = {'depends on': ('where', 'how fast', 'when', 'both', 'nothing'),
         'shape': ('straight', 'growing', 'steps', 'cubic', 'wave'),
         'kind': ('plain', 'times', 'power', 'rhythm', 'steady')}
MEANINGS = {'depends on': ('position', 'speed', 'time', 'position and speed', 'nothing'),
            'shape': grammar.SHAPES,
            'kind': ('only simple ideas', 'a product', 'a power', 'a push that swings in time', 'a steady push')}
PERMS = tuple(itertools.permutations(range(5)))           # perm[w] = the property word w names
N_PERMS = len(PERMS)                                       # 120
_PERM_ARR = np.array(PERMS)
MAX_SHIFT = math.log((1 - EPS + EPS / 5) * 5 / EPS)       # 4.6 nats: the most one sentence can move two laws' odds


def _shapes_of(term):
    if term in grammar.IDEAS:
        return {term[1]} if term[0] in ('position', 'speed') else set()
    if term[0] == 'product':
        return {term[1], term[2]}
    if term[0] == 'pprod':
        return {p for p in term[1:] if p in grammar.SHAPES}
    return set()


def truth(slot, law):
    """The five properties of the slot, true or false, for a law (a tuple of terms)."""
    law = grammar.canonical(law)
    if slot == 'depends on':
        ins = F._inputs(law)
        return ('x' in ins, 'v' in ins, 't' in ins, 'x' in ins and 'v' in ins, ins == 'none')
    if slot == 'shape':
        shapes = set().union(*[_shapes_of(t) for t in law]) if law else set()
        return tuple(s in shapes for s in grammar.SHAPES)
    if slot == 'kind':
        opens = [t for t in law if t not in grammar.IDEAS]
        return (not opens, any(t[0] in ('product', 'pprod') for t in opens), any(t[0] == 'power' for t in opens),
                any(t[0] == 'drive' for t in opens), ('nothing', 'steady') in law)
    raise ValueError(slot)


def flat():
    """The lexicon before any word is heard: every bijection equally likely, per slot (3, 120) log probabilities."""
    return np.full((len(SLOTS), N_PERMS), -math.log(N_PERMS))


def _loglik_matrix(tv, words):
    """log p(words | L, h) for every bijection L: (120,) for one law's truth vector tv (5 bools)."""
    n = int(sum(tv))
    if n == 0 or not words:
        return np.full(N_PERMS, len(words) * math.log(1 / 5))
    tv = np.asarray(tv, float)
    out = np.zeros(N_PERMS)
    for w in words:
        out += np.log((1 - EPS) * tv[_PERM_ARR[:, w]] / n + EPS / 5)
    return out


def learn(logp, sentences, law):
    """The exact posterior over bijections after hearing `sentences` [(slot, word index)] about `law` (told)."""
    logp = np.array(logp, float, copy=True)
    for k, slot in enumerate(SLOTS):
        ws = [w for s, w in sentences if s == slot]
        if ws:
            logp[k] += _loglik_matrix(truth(slot, law), ws)
            logp[k] -= np.logaddexp.reduce(logp[k])
    return logp


def factor(logp, sentences, laws):
    """{law: log sum_L p(L) prod_j p(w_j | L, law)} over every slot heard: the exact word factor on the Field's
    belief (the lexicon's uncertainty kept, not averaged per sentence)."""
    out = {h: 0.0 for h in laws}
    for k, slot in enumerate(SLOTS):
        ws = [w for s, w in sentences if s == slot]
        if not ws:
            continue
        cache = {}
        for h in laws:
            tv = truth(slot, h)
            if tv not in cache:
                cache[tv] = float(np.logaddexp.reduce(logp[k] + _loglik_matrix(tv, ws)))
            out[h] += cache[tv]
    return out


def meanings(logp):
    """{slot: {word: (the property it most likely names, that probability)}}."""
    out = {}
    for k, slot in enumerate(SLOTS):
        p = np.exp(logp[k] - np.logaddexp.reduce(logp[k]))
        out[slot] = {}
        for w, word in enumerate(WORDS[slot]):
            m = np.zeros(5)
            np.add.at(m, _PERM_ARR[:, w], p)
            j = int(np.argmax(m))
            out[slot][word] = (MEANINGS[slot][j], float(m[j]))
    return out


def grounded(logp, level=0.95):
    """The words whose meaning SERA holds with at least `level` probability: [(slot, word, meaning, p)]."""
    return [(slot, word, mean, p) for slot, ws in meanings(logp).items() for word, (mean, p) in ws.items()
            if p >= level]
