"""World v5.0, the playroom (docs/SERA_PLAYROOM.md v0.1 §1-2, sera-v3 5588f76; independent review reviewed the design).

Things with visible looks and hidden masses by kind, one law per room drawn from the curriculum's regimes, M-1 knocks;
and the caretaker - the caretaker's code, the author's delegated teacher - whose word probabilities are exactly §2's likelihood by
construction, and who sees only the room's hidden state and the throws so far, never their noise (condition R-P).

SERA sees a thing's LOOK: three integer codes (material, size, shape) through a fixed secret coding, never the words.
The words are tokens it must learn to connect to looks, masses and laws."""
import dataclasses
import math

import numpy as np

from .. import puzzles as P
from . import grammar, paths, worlds

MATERIALS = ('iron', 'wood', 'rubber', 'foam')
SIZES = ('small', 'big')
SHAPES = ('ball', 'block')
A_MATERIAL = {'iron': math.log(2.2), 'wood': math.log(1.2), 'rubber': math.log(0.9), 'foam': math.log(0.6)}
BIG = 0.4                        # log-mass offset of a big thing
MASS_SD = 0.15                   # log-mass spread within a kind and size
TRICKS = 0.05                    # the M-1 knock generator: one thing in 20, one of the same 8 knocks
KNOCK_T0 = (0.6, 0.8, 1.0, 1.2)
KNOCK_AMP = (-1.5, 1.5)
SIGMA = (0.001, 0.001)
_LOOK = {'material': {'iron': 2, 'wood': 0, 'rubber': 3, 'foam': 1},   # the fixed secret coding of looks
         'size': {'small': 1, 'big': 0}, 'shape': {'ball': 0, 'block': 1}}

# One law per room: the curriculum's regimes (ccops5.puzzles.FORCES), alone and in its three pairs.
REGIMES = ('none', 'rubbing', 'water drag', 'dry friction', 'thick oil', 'spring', 'tight spring', 'stiff spring',
           'swing', 'valley', 'slope', 'rubbing+spring', 'slope+dry friction', 'water drag+spring')

TEMPLATES = ('material', 'size', 'shape', 'property', 'room')
WORDS = {'material': MATERIALS, 'size': SIZES, 'shape': SHAPES, 'property': ('heavy', 'light'),
         'room': ('pull back', 'slow down', 'push along', 'wave', 'nothing')}
P_SPEAK = 0.5
EPS = 0.05                       # the caretaker's slip rate
REF_X = np.linspace(-3.0, 3.0, 601)          # the rail (§2: the room words' reference ranges)
REF_V = np.linspace(-6.0, 6.0, 1201)         # the cells' speed range


@dataclasses.dataclass(frozen=True)
class Thing:
    ident: str                   # a public ID, not a word; changes from room to room
    material: str                # hidden truth of the look (the evaluator's)
    size: str
    shape: str
    look: tuple                  # what SERA sees: (material code, size code, shape code)
    mass: float                  # hidden
    bump: tuple                  # hidden: None or the M-1 knock (t0, amplitude), on every throw of this thing


def regime_law(regime, rng):
    """The regime's law terms and strengths, drawn as curriculum._build draws them (strength = -sign * U(limits))."""
    if regime == 'none':
        return (), ()
    terms, coefs = [], []
    for name in regime.split('+'):
        idea, limits = P.FORCES[name]
        sign = float(rng.choice([-1.0, 1.0])) if idea[0] == 'nothing' else 1.0
        terms.append(idea)
        coefs.append(-sign * float(rng.uniform(*limits)))
    return tuple(terms), tuple(coefs)


def _inputs(term):
    """The inputs a term reads. Unknown kinds raise (independent review C2): a piece or cell term must never pass silently as a
    steady push."""
    if term[0] == 'nothing':
        return set()
    if term[0] == 'product':
        return {'x', 'v'}
    if term[0] == 'power':
        return {'x' if term[1] == 'position' else 'v'}
    if term[0] == 'drive':
        return {'t'}
    if term[0] in ('position', 'speed'):
        return {'x'} if term[0] == 'position' else {'v'}
    raise ValueError(f'room words are not defined for a {term[0]} term: {term}')


def _functional(term, which):
    """a_j (which = 'x') or b_j (which = 'v'): the integral of input * term over the reference range (trapezoid)."""
    k, a, b = grammar.code(term)
    grid = REF_X if which == 'x' else REF_V
    vals = np.array([paths.term_t(k, a, b, g if which == 'x' else 0.0, g if which == 'v' else 0.0, 0.0, 1.0, 1.0)
                     for g in grid])
    return float(np.trapezoid(grid * vals, grid))


def room_words(terms, coefs):
    """§2: the room words' truth, a frozen total function of the law. 'pull back' / 'slow down': the position-only /
    speed-only force points back / against the motion on average over the reference range (the sign of one linear
    functional of the strengths); 'push along': a term with neither position nor speed (a steady push or a drive);
    'wave': a wave-shaped position or speed term; 'nothing': none of these. Cross terms count toward none."""
    pull = sum(c * _functional(t, 'x') for t, c in zip(terms, coefs) if _inputs(t) == {'x'})
    slow = sum(c * _functional(t, 'v') for t, c in zip(terms, coefs) if _inputs(t) == {'v'})
    out = {'pull back': any(_inputs(t) == {'x'} for t in terms) and pull < 0,
           'slow down': any(_inputs(t) == {'v'} for t in terms) and slow < 0,
           'push along': any(not (_inputs(t) & {'x', 'v'}) for t in terms),
           'wave': any(t[0] in ('position', 'speed') and t[1] == 'wave' for t in terms)}
    out['nothing'] = not any(out.values())
    return out


@dataclasses.dataclass
class Room:
    seed: int
    index: int
    regime: str
    terms: tuple                 # the law's terms in draw order (simulator order) and their strengths
    coefs: tuple
    things: list
    sigma: tuple = SIGMA

    @property
    def family(self):
        return grammar.canonical(self.terms)

    def throw(self, k, action, n):
        """Throw number n (fresh noise per n): thing k under the push program `action`, with the thing's knock."""
        kinds = np.array([grammar.code(t)[0] for t in self.terms], np.int64)
        a = np.array([grammar.code(t)[1] for t in self.terms], np.int64)
        b = np.array([grammar.code(t)[2] for t in self.terms], np.int64)
        t0, amp = self.things[k].bump or (0.0, 0.0)
        xs, vs = paths.simulate_program(*action.arrays(), 1.0 / self.things[k].mass, kinds, a, b,
                                        np.array(self.coefs, float), 1.0, 1.0, t0, amp)
        nr = np.random.default_rng([self.seed, 11, self.index, n])
        return worlds.Throw(k, n, action, xs + nr.normal(0, self.sigma[0], xs.size),
                            vs + nr.normal(0, self.sigma[1], vs.size), 'play')


def make_room(seed, index, n_things=None):
    rng = np.random.default_rng([seed, 13, index])
    regime = REGIMES[int(rng.integers(len(REGIMES)))]
    terms, coefs = regime_law(regime, rng)
    n = n_things or int(rng.integers(4, 7))
    things = []
    for i in range(n):
        mat = MATERIALS[int(rng.integers(len(MATERIALS)))]
        size = SIZES[int(rng.integers(len(SIZES)))]
        shape = SHAPES[int(rng.integers(len(SHAPES)))]
        mass = math.exp(A_MATERIAL[mat] + BIG * (size == 'big') + MASS_SD * float(rng.normal()))
        bump = None
        if rng.random() < TRICKS:
            bump = (float(rng.choice(KNOCK_T0)), float(rng.choice(KNOCK_AMP)))
        ident = 'obj-' + ''.join(chr(97 + int(c)) for c in rng.integers(0, 26, size=3))
        things.append(Thing(ident, mat, size, shape,
                            (_LOOK['material'][mat], _LOOK['size'][size], _LOOK['shape'][shape]), mass, bump))
    return Room(seed, index, regime, terms, coefs, things)


@dataclasses.dataclass(frozen=True)
class Sentence:
    n: int                       # spoken after throw number n
    template: str
    topic: object                # the thing's index, or 'room'
    word: str


class Caretaker:
    """§2. R-P by construction (independent review C1): it holds only the room (the hidden state) and is given only the tuple
    of past throws' things - never a Throw, so never a reading - with its own random numbers per throw number."""

    def __init__(self, room):
        self._room = room

    def true_words(self, template, topic):
        room = self._room
        if template == 'room':
            truth = room_words(room.terms, room.coefs)
            return tuple(w for w in WORDS['room'] if truth[w])
        thing = room.things[topic]
        if template in ('material', 'size', 'shape'):
            return (getattr(thing, template),)
        masses = sorted(t.mass for t in room.things)
        med = float(np.median(masses))
        if thing.mass > med:                         # heavier than the median: its mu is below the median mu
            return ('heavy',)
        if thing.mass < med:
            return ('light',)
        return ()                                    # the median thing (odd count): neither

    def likelihood(self, template, topic, word):
        """§2's p(word | true lexicon, template, topic)."""
        words, true = WORDS[template], self.true_words(template, topic)
        if not true:
            return 1.0 / len(words)
        return (1 - EPS) * (word in true) / len(true) + EPS / len(words)

    def speak(self, situations):
        """What it says after the last throw, given `situations`: which thing each throw so far was (a tuple of ints).
        Returns a Sentence or None."""
        n = len(situations) - 1
        last = int(situations[-1])          # C1: which thing the last throw was - an int, never a throw (or its noise)
        rng = np.random.default_rng([self._room.seed, 17, self._room.index, n])
        if rng.random() >= P_SPEAK:
            return None
        template = TEMPLATES[int(rng.integers(len(TEMPLATES)))]
        topic = 'room' if template == 'room' else last
        words, true = WORDS[template], self.true_words(template, topic)
        slip = rng.random() < EPS
        if not true or slip:
            word = words[int(rng.integers(len(words)))]
        else:
            word = true[int(rng.integers(len(true)))]
        return Sentence(n, template, topic, word)
