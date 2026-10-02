"""Stage 5's code door (plan revision 5, B3 Stage 5): small list-program tasks, solved by SERA's loop on code
(sera.synth, G2's machinery: imagine every program up to a size, ask the question that splits them, keep the shortest
survivor, then its anytime audit on fresh inputs decides).

A task is a hidden program of the code domain (sera.general), drawn from the same space SERA searches, up to 5 nodes,
never a constant or the identity. SERA sees 3 examples, may ask up to 6 questions, and claims a program only if the
audit accepts it: 1/(1 - eps)^n >= 1/(delta 2^-bits), so P(ever accepting a program wrong on eps of inputs) <= delta.
The observer then runs the claim against the hidden program on 100 fresh inputs: a claim accepted and wrong there is
the code door's tripwire, as a sure-and-wrong law is physics'.

SERA's code library: every accepted program, with how often it was met; a program met again is recognized ("I have
solved this before"). The library does not change the search yet (library learning, new primitives, is the next step
and is not built).
"""
import numpy as np

from . import synth as S

MAX_SIZE = 5
CHECK_N = 100


class CodeWorld:
    def __init__(self, seed, n):
        rng = np.random.default_rng([seed, 71, n])
        self.seed, self.index = seed, 7000 + n
        probe = [S.random_input(rng) for _ in range(12)]
        space = S.Space(probe, max_size=MAX_SIZE)
        typ = ('list', 'int')[int(rng.integers(2))]
        cands = [p for p, _ in space.programs(typ) if _interesting(p, probe)]
        self.program = cands[int(rng.integers(len(cands)))]
        self.out_type = typ
        self.rng_seed = [seed, 73, n]

    def target(self, x):
        return S._out(self.program, x)


def _interesting(p, probe):
    outs = [S._safe(p, {'input': list(x)}) for x in probe]
    if any(o is None for o in outs):
        return False
    if len(set(outs)) <= 1:                                 # a constant
        return False
    return any(o != tuple(x) for o, x in zip(outs, probe))  # not the identity


def code_world(seed, n):
    return CodeWorld(seed, n)


def solve(world):
    """SERA's loop on the task (sera.synth.synthesize, active questions)."""
    return S.synthesize(world.target, world.out_type, np.random.default_rng(world.rng_seed), max_size=MAX_SIZE)


def grade(world, res):
    """The observer's verdict: the claim against the hidden program on CHECK_N fresh inputs."""
    rng = np.random.default_rng([world.seed, 79, world.index])
    p = res.get('program')
    agree = p is not None and all(S._out(p, x) == world.target(x)
                                  for x in (S.random_input(rng) for _ in range(CHECK_N)))
    if res.get('accepted'):
        return 'proven right' if agree else 'SURE AND WRONG'
    return 'right, unsure' if agree else 'unsure, wrong'


def name(p):
    """A program in words-like text: map(λe. iadd(e, 1), input)."""
    if p is None:
        return None
    sym, payload, kids = p[0], p[1], p[2:]
    if sym == 'lit':
        return str(payload)
    if sym in ('lam_int', 'lam_bool'):
        return 'λe. ' + name(kids[0])
    if not kids:
        return sym
    return f"{sym}({', '.join(name(k) for k in kids)})"
