"""Memory v3 (sera.memory; plan revision 4, R4-3b; pre-registered in the plan, written before the mind uses it):
- the serialized state is exactly MEMORY_BYTES after any number of episodes; at most K_CAPTURE lessons per episode;
- the long-term state is frozen during an episode (the snapshot's digest), and only consolidate() grows it;
- a lesson fades by half every LESSON_HALF episodes;
- a refusal that says the law is wrong lowers that law's proposal weight in that context only; a refusal for want of
  evidence does not count against the law; the floor keeps every law proposable (the recall sentinel);
- a checker-verified proof in a lesson's context resolves the lesson and becomes knowledge; an unverified one does
  not; the settling program becomes a skill, active after helping in 2 distinct episodes;
- anchors never move and never come within RADIUS of each other (memories never merge); domains never mix."""
import math
import types

import numpy as np
import pytest

from ccops5.core import grammar
from ccops5.core.worlds import Action
from legacy.sera_v3 import field as F, memory as M

X, Y, Z = F.LAWS[5], F.LAWS[40], F.LAWS[400]
PROGRAM = Action(((0.0, 1.2, -1.0),))


def _ctx(v=0.0, d=0):
    c = np.zeros(F.CONTEXT_DIM)
    c[d] = v
    return c


def _refused(law, why='something else is here: the law misfits more objects than bumps explain', rival=None, e=3.0):
    return types.SimpleNamespace(family=law, accepted=False, rivals={rival: e} if rival else {}, reasons=(why,),
                                 adequate=12.0, band=None, eps=0.2, alpha=1e-3)


def _proved(law):
    return types.SimpleNamespace(family=law, accepted=True, rivals={Z: 60.0}, reasons=(), adequate=0.0, band=0.1,
                                 eps=0.2, alpha=1e-3)


def _episode(m, context, certs=(), verified=False, program=None, domain='physics'):
    snap = m.begin(context)
    tags = M.Tags()
    for c in certs:
        tags.certificate(c, program)
    return m.consolidate(snap, tags, context, domain, verified)


def test_the_memory_is_always_exactly_its_size_and_captures_at_most_k():
    rng = np.random.default_rng(0)
    m = M.Memory()
    for ep in range(1000):
        c = rng.normal(0, 2, F.CONTEXT_DIM)
        laws = [F.LAWS[int(i)] for i in rng.integers(len(F.LAWS), size=20)]
        certs = [_refused(h, 'extra terms needed' if i % 2 else 'something else is here') for i, h in enumerate(laws)]
        if ep % 7 == 0:
            certs.append(_proved(F.LAWS[int(rng.integers(len(F.LAWS)))]))
        n = _episode(m, c, certs, verified=ep % 7 == 0, program=PROGRAM)
        assert n <= M.K_CAPTURE
        assert len(m.to_bytes()) == M.MEMORY_BYTES
    print('memory bytes', M.MEMORY_BYTES)


def test_the_long_term_state_is_frozen_during_an_episode():
    m = M.Memory()
    _episode(m, _ctx(), [_refused(X)])
    snap = m.begin(_ctx())
    for _ in range(5):
        snap.log_prior(_ctx())
        snap.lessons(_ctx())
        snap.skill_programs(_ctx())
    assert snap.digest == M.Snapshot(m.to_bytes()).digest            # reading never writes
    other = m.begin(_ctx())
    _episode(m, _ctx(), [_refused(Y)])                                 # the next version grows ...
    assert other.digest == snap.digest and M.Snapshot(other.raw).digest == snap.digest   # ... the old one is intact
    with pytest.raises(AssertionError):
        m.consolidate(snap, M.Tags(), _ctx())                          # a stale snapshot cannot write


def test_a_lesson_halves_every_half_life():
    m = M.Memory()
    _episode(m, _ctx(), [_refused(X)])
    w0 = float(m.lessons['weight'][m.lessons['status'] == M.OPEN][0])
    for k in range(int(M.LESSON_HALF)):
        _episode(m, _ctx(50.0 + 10 * k, 1))                            # far away: nothing refreshes it
    w = float(m.lessons['weight'][m.lessons['status'] == M.OPEN][0])
    assert abs(w / w0 - 0.5) < 1e-5, (w0, w)


def test_a_refusal_against_the_law_lowers_it_here_only_and_the_floor_keeps_it():
    base = M.Memory().log_prior(_ctx())
    m = M.Memory()
    _episode(m, _ctx(), [_refused(X)])
    here, far = m.log_prior(_ctx()), m.log_prior(_ctx(10.0))
    assert here[X] < base[X] - 0.5                                    # remembered: tried here, the judge said wrong
    assert abs(far[X] - base[X]) < 1e-6                               # elsewhere nothing changes
    floor = F.with_floor(here)
    pi0 = F.prior_logp()
    assert floor[X] >= math.log(F.ETA) + pi0[X] - 1e-9                # never forgotten: still proposable


def test_a_refusal_for_want_of_evidence_does_not_count_against_the_law():
    base = M.Memory().log_prior(_ctx())
    m = M.Memory()
    _episode(m, _ctx(), [_refused(X, 'a rival family is not ruled out: y', rival=Y)])
    assert abs(m.log_prior(_ctx())[X] - base[X]) < 1e-9
    assert m.lessons_near(_ctx())[0][:2] == (X, M.REASONS['rival'])    # but it is remembered, and why


def test_a_verified_proof_resolves_the_lessons_here_and_becomes_knowledge_and_a_skill():
    base = M.Memory().log_prior(_ctx())
    m = M.Memory()
    _episode(m, _ctx(), [_refused(X)])
    _episode(m, _ctx(0.2), [_proved(Y)], verified=False, program=PROGRAM)          # not checker-verified: nothing
    assert m.lessons_near(_ctx()) and abs(m.log_prior(_ctx())[Y] - base[Y]) < 0.6
    before = m.log_prior(_ctx())[Y]
    _episode(m, _ctx(0.2), [_proved(Y)], verified=True, program=PROGRAM)
    assert m.lessons_near(_ctx()) == []                                # solved: the details are let go
    after = m.log_prior(_ctx())
    assert after[Y] > before + 0.5                                     # what it proved lingers
    twin = M.Memory()                                                  # the same episodes without the refusal
    _episode(twin, _ctx())
    _episode(twin, _ctx(0.2), [_proved(Y)], verified=False, program=PROGRAM)
    _episode(twin, _ctx(0.2), [_proved(Y)], verified=True, program=PROGRAM)
    assert abs(after[X] - twin.log_prior(_ctx())[X]) < 1e-9            # the resolved lesson leaves no trace
    assert m.skill_programs(_ctx()) == []                              # one success: still a candidate
    _episode(m, _ctx(0.1), [_proved(Y)], verified=True, program=PROGRAM)
    assert m.skill_programs(_ctx()) == [PROGRAM]                       # helped in 2 episodes: active
    assert m.skill_programs(_ctx(10.0)) == []


def test_anchors_never_move_or_merge():
    rng = np.random.default_rng(1)
    m = M.Memory()
    placed = {}
    for _ in range(1000):
        c = rng.normal(0, 1.5, F.CONTEXT_DIM)
        _episode(m, c, [_proved(Y)], verified=True)
        for i in np.flatnonzero(m.anchors['used']):
            key = m.anchors['key'][i].copy()
            assert np.array_equal(placed.setdefault(int(i), key), key)
    used = np.flatnonzero(m.anchors['used'])
    assert len(used) == M.P_ANCHORS
    d = min(np.linalg.norm(m.anchors['key'][i] - m.anchors['key'][j]) for i in used for j in used if i < j)
    assert d > M.RADIUS


def test_domains_do_not_mix():
    base = M.Memory().log_prior(_ctx())
    m = M.Memory()
    _episode(m, _ctx(), [_refused(X)], domain='code')
    assert abs(m.log_prior(_ctx())[X] - base[X]) < 1e-9
    assert m.lessons_near(_ctx()) == [] and m.lessons_near(_ctx(), 'code')


@pytest.mark.slow
def test_the_field_mind_grows_its_memory_once_per_world():
    """The mind reads a frozen snapshot all world long and consolidates once at its end."""
    import os
    import torch
    from legacy.sera_v3 import imagine as I, mind as SM, worlds as SW
    w = SW.make(1, 9007, 1, 'dream')
    model = I.Imagination()
    runs = os.environ.get('SERA_RUNS', 'D:/ai/labs/ccops5-sera-lab/sera-runs')
    model.load_state_dict(torch.load(f'{runs}/imagine-v1/model.pt', map_location='cpu'))
    model = model.float().eval()
    mem = M.Memory()
    mind = SM.Mind(model, w.sigma, eps=0.2, budget=w.n_situations, design=True, field=True, memory=mem)
    r = mind.live(w)
    assert mem.episode == 1 and len(mem.to_bytes()) == M.MEMORY_BYTES     # grown once, at the world's end
    assert mind._tags.items and r.certify_calls == len(mind._tags.items)  # every certificate call was tagged


def test_every_law_stays_proposable_after_many_refusals():
    rng = np.random.default_rng(2)
    m = M.Memory()
    for _ in range(200):
        laws = [F.LAWS[int(i)] for i in rng.integers(len(F.LAWS), size=8)]
        _episode(m, _ctx(float(rng.normal(0, 0.1))), [_refused(h) for h in laws])
    floor = F.with_floor(m.log_prior(_ctx()))
    pi0 = F.prior_logp()
    assert all(floor[h] >= math.log(F.ETA) + pi0[h] - 1e-9 for h in F.LAWS)
    assert grammar.canonical(X) == X
