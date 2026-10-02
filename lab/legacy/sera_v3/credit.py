"""The credit system, wired into the mind that uses it (plan revision 5, WP3).

The verification of 2026-09-27 found that the credit ladder (sera.grade) trained only the imagination network, which
the Field mind never reads, and memory v3 learned only from its own proofs: the newest mind could not be taught (the
School failure of 2026-09-24, again). Here every grade becomes writes to memory v3, the long-term state the Field mind
does read (through its frozen per-world prior, its candidate experiments and its vocabulary). The writes are applied in
the world's one consolidation (sera.memory.Memory.consolidate).

| grade | memory write |
|---|---|
| proven (checker-verified) | knowledge (memory's own proof path) and the law's terms join the vocabulary (discovered) |
| the caretaker names the law (Stages 1-2), not proven | a lesson for the named law here (taught, source caretaker) |
| its leader was not the law | a lesson against its leader here (graded wrong, source caretaker) |
| part right | a lesson for the deepest lattice node its leader shared with the law ("depends on speed") |
| named law's terms | they join the vocabulary (taught) |
| its best question (rung 5) | the push that gained the most evidence against the rival becomes a candidate skill |
| its biggest band cut | the push after which the band shrank most becomes a candidate skill |
| a demonstration | the demonstrated push becomes an active skill (source caretaker) |
| Stage 3, its own grade | if its self-grader is trusted: a lesson for (believed) or against (doubted) its unproven leader |

Weights (nats of prior bias, capped by memory.B_MAX): the ladder's order - taught 1.5 > graded wrong 1.0 > part 0.5 -
fixed before any run. Knowledge stays proofs only, as the author designed it. The judge reads none of this.
"""
import math

from ccops5.core import grammar
from ccops5.core.worlds import Action
from . import field as F

W_TAUGHT, W_WRONG, W_PART, W_SELF = 1.5, 1.0, 0.5, 0.75
MIN_QUESTION = 2.0               # nats: a push's evidence gain must reach this to be kept as a skill
MIN_BAND_CUT = 0.05              # log units: a band cut must reach this
SELF_SURE, SELF_DOUBT = 0.9, 0.1


def _shared_node(leader, law):
    """The deepest lattice node (inputs, operator, subtype) the two laws share, or None (below the full law)."""
    a, b = F.UNIVERSE_PATHS.get(leader), F.UNIVERSE_PATHS.get(law)
    if a is None or b is None:
        return None
    node = None
    for lv in range(1, 4):
        if a[:lv] != b[:lv]:
            break
        node = a[:lv]
    return node


def best_question(report):
    fs = [f for f in (report.foresight or []) if f.get('gain') is not None and f.get('program')]
    if not fs:
        return None
    f = max(fs, key=lambda f: f['gain'])
    return f if f['gain'] >= MIN_QUESTION else None


def best_band_cut(report):
    """(the push after which the band shrank most, the cut in log units) from consecutive certify calls."""
    calls = [c for c in (report.calls or []) if c.get('band')]
    fs = report.foresight or []
    best, cut = None, 0.0
    for c1, c2 in zip(calls, calls[1:]):
        if c2['own'] == c1['own'] + 1 and c1['own'] < len(fs) and fs[c1['own']].get('program'):
            d = math.log(c1['band']) - math.log(c2['band'])
            if d > cut:
                best, cut = fs[c1['own']], d
    return (best, cut) if best is not None and cut >= MIN_BAND_CUT else (None, 0.0)


def _action(program):
    return Action(tuple(tuple(float(x) for x in s) for s in program))


def credit(report, stage, verified, named_law=None, self_p=None, trust_self=False):
    """The memory writes of one graded world (sera.memory.Memory.consolidate's `credit`)."""
    leader = grammar.canonical(report.claim)
    lessons, skills, vocab = [], [], []
    if verified and report.sure:
        vocab += [(t, 'discovered') for t in leader if t not in grammar.IDEAS and t[0] != 'cell']
    if named_law is not None:
        law = grammar.canonical(named_law)
        proven_right = verified and report.sure and leader == law
        if not proven_right:
            lessons.append(dict(law=law, reason='taught', source='caretaker', weight=W_TAUGHT))
            if leader != law and not grammar.contains(law, leader):
                lessons.append(dict(law=leader, reason='graded wrong', source='caretaker', weight=W_WRONG))
            if leader != law:
                node = _shared_node(leader, law)
                if node is not None:
                    lessons.append(dict(node=node, reason='part right', source='caretaker', weight=W_PART))
        vocab += [(t, 'taught') for t in law if t not in grammar.IDEAS and t[0] != 'cell']
    elif stage == 'alone' and trust_self and self_p is not None and not report.sure:
        if self_p >= SELF_SURE:
            lessons.append(dict(law=leader, reason='believed', source='self', weight=W_SELF))
        elif self_p <= SELF_DOUBT:
            lessons.append(dict(law=leader, reason='doubted', source='self', weight=W_SELF))
    q = best_question(report)
    if q is not None:
        skills.append(dict(program=_action(q['program']), gain=q['gain'], law=leader, source='self'))
    b, cut = best_band_cut(report)
    if b is not None:
        skills.append(dict(program=_action(b['program']), gain=cut, law=leader, source='self'))
    for d in report.demos or []:
        skills.append(dict(program=_action(d['program']), gain=0.0,
                           law=named_law if named_law is not None else leader, active=True, source='caretaker'))
    return dict(lessons=lessons, skills=skills, vocab=vocab, sentences=list(report.heard or []),
                named_law=grammar.canonical(named_law) if named_law is not None else None)
