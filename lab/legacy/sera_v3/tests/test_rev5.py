"""Plan revision 5's new pure parts (fast; the whole agent is exercised by the smoke life, not here):
- words: the lexicon posterior equals brute-force enumeration; one sentence moves two laws' odds by at most
  words.MAX_SHIFT; a flat lexicon moves nothing;
- vocabulary: the base vocabulary is the 67 base laws; a known term adds itself alone and with each idea; the full
  vocabulary is v4's LAWS;
- memory format 2: fixed size; a taught lesson raises the named law here and a graded-wrong one lowers the believed
  law; a part-right lesson raises every law under its node; the vocabulary and the words grow only at consolidation;
- the stop rule: stops when the proof stops coming closer, never while the leader or its blocker changes;
- the curriculum: every door gets its optimism until tried, then learning progress decides.
"""
import itertools
import math
import types

import numpy as np

from ccops5.core import grammar
from ccops5.core.worlds import Action
from legacy.sera_v3 import credit as CR, doors as DR, field as F, memory as M, mind as SM, words as W

SPRING = (('position', 'straight'),)
DRAG = (('speed', 'straight'),)
XV = ('product', 'straight', 'straight')


def test_the_lexicon_posterior_is_exact():
    rng = np.random.default_rng(0)
    laws = [SPRING, DRAG, (XV,), (('nothing', 'steady'),), (('drive', 'sin', 2.0),)]
    heard = [(W.SLOTS[int(rng.integers(3))], int(rng.integers(5))) for _ in range(12)]
    law = laws[2]
    logp = W.learn(W.flat(), heard, law)
    for k, slot in enumerate(W.SLOTS):                    # brute force over the 120 bijections
        tv = W.truth(slot, law)
        n = sum(tv)
        brute = np.zeros(W.N_PERMS)
        for i, perm in enumerate(itertools.permutations(range(5))):
            for s, w in heard:
                if s == slot:
                    brute[i] += math.log((1 - W.EPS) * tv[perm[w]] / n + W.EPS / 5) if n else math.log(1 / 5)
        brute -= np.logaddexp.reduce(brute)
        assert np.allclose(logp[k], brute, atol=1e-12)


def test_one_sentence_moves_odds_at_most_the_bound_and_a_flat_lexicon_moves_nothing():
    laws = list(F.Vocab(()).laws)
    flat = W.factor(W.flat(), [('depends on', 1)], laws)
    assert max(flat.values()) - min(flat.values()) < 1e-12
    sharp = W.flat()
    for _ in range(40):                                   # the lexicon learned: "how fast" names speed
        sharp = W.learn(sharp, [('depends on', 1)], DRAG)
        sharp = W.learn(sharp, [('depends on', 0)], SPRING)
    f = W.factor(sharp, [('depends on', 1)], laws)
    assert max(f.values()) - min(f.values()) <= W.MAX_SHIFT + 1e-9
    assert f[DRAG] - f[SPRING] > 3.0                      # grounded: hearing it moves belief toward speed laws


def test_the_vocabulary():
    base = F.Vocab(())
    assert len(base.laws) == 67 and set(base.laws) == set(grammar.space())
    one = base.with_terms([XV])
    assert len(one.laws) == 67 + 12 and (XV,) in one.laws and XV in one and XV not in base
    assert F.FULL.laws == F.LAWS and len(F.LAWS) == 3175
    piece = base.with_terms([('piece', 'speed', 'abs', 0.0)])
    assert (('piece', 'speed', 'abs', 0.0),) in piece.laws and piece.paths[(('piece', 'speed', 'abs', 0.0),)][0] == 'v'


def _ctx(v=0.0):
    c = np.zeros(F.CONTEXT_DIM)
    c[0] = v
    return c


def _episode(m, credit, ctx=None):
    ctx = _ctx() if ctx is None else ctx
    snap = m.begin(ctx)
    m.consolidate(snap, M.Tags(), ctx, 'physics', False, credit=credit)


def test_credit_reaches_the_prior_the_vocabulary_and_the_words():
    vocab = F.Vocab([XV])
    base = M.Memory().log_prior(_ctx(), vocab=vocab)
    m = M.Memory()
    _episode(m, dict(lessons=[dict(law=(XV,), reason='taught', source='caretaker', weight=1.5),
                              dict(law=SPRING, reason='graded wrong', source='caretaker', weight=1.0),
                              dict(node=('v',), reason='part right', source='caretaker', weight=0.5)],
                     vocab=[(XV, 'taught')], sentences=[('kind', 1)], named_law=(XV,)))
    here = m.log_prior(_ctx(), vocab=vocab)
    assert here[(XV,)] - base[(XV,)] > 1.0                # taught: raised here
    assert here[SPRING] - base[SPRING] < -0.5             # graded wrong: lowered here
    assert here[DRAG] - base[DRAG] > here[SPRING] - base[SPRING] + 0.5    # part right: every speed law raised
    assert m.vocab_terms() == (XV,) and m.vocab_terms('taught') == (XV,)
    assert m.lex['heard'][0][2] == 1 and len(m.to_bytes()) == M.MEMORY_BYTES
    far = m.log_prior(_ctx(10.0), vocab=vocab)
    assert abs(far[(XV,)] - base[(XV,)]) < 1e-6           # elsewhere nothing changes
    floor = F.with_floor(here, vocab)
    assert floor[SPRING] >= math.log(F.ETA) + F.prior_logp(vocab)[SPRING] - 1e-9 - 0.1   # still proposable


def test_a_demonstration_is_an_active_skill_at_once():
    m = M.Memory()
    prog = Action(((0.0, 0.8, 1.0),))
    _episode(m, dict(skills=[dict(program=prog, law=SPRING, active=True, source='caretaker')]))
    assert m.skill_programs(_ctx()) == [prog]


def _h(own, leader, kind, short):
    return dict(own=own, leader=leader, kind=kind, short=short, blocker=None)


def test_the_stop_rule():
    rule = SM.StopRule()
    flat = [_h(i, SPRING, 'band', 1.0 - 0.001 * i) for i in range(5)]
    assert rule.check(flat, 4, 24) == 'no progress'
    moving = [_h(i, SPRING if i % 2 else DRAG, 'band', 1.0) for i in range(5)]
    assert rule.check(moving, 4, 24) is None
    slow = [_h(i, SPRING, 'rival', 30.0 - 0.6 * i) for i in range(5)]
    assert rule.check(slow, 4, 24) == 'too slow'          # 27.6 nats left at 0.6 per push > 20 pushes left
    fast = [_h(i, SPRING, 'rival', 10.0 - 2 * i) for i in range(5)]
    assert rule.check(fast, 4, 24) is None
    assert rule.check(flat[:4], 3, 24) is None            # too early to judge


def test_the_curriculum_tries_every_door_then_follows_learning_progress():
    cur = DR.Curriculum(seed=0)
    assert all(cur.lp(d) == DR.OPTIMISM for d in cur.doors)
    for d in cur.doors:
        for i in range(16):
            cur.record(d, (d == 2 and i >= 8))            # door 2: 0 of 8, then 8 of 8 -> LP 1
    assert cur.lp(2) == 1.0 and cur.lp(1) == 0.0
    picks = [cur.choose()[0] for _ in range(200)]
    assert picks.count(2) > 100


def test_credit_finds_the_best_question_and_band_cut():
    r = types.SimpleNamespace(
        claim=SPRING, sure=False, foresight=[dict(gain=0.5, program=[[0.0, 0.4, 1.0]]),
                                             dict(gain=7.0, program=[[0.0, 1.2, -1.0]]),
                                             dict(gain=1.0, program=[[0.0, 0.8, 0.6]])],
        calls=[dict(own=0, band=0.5), dict(own=1, band=0.3), dict(own=2, band=0.29)], demos=[], heard=[])
    c = CR.credit(r, 'practice', False, named_law=DRAG)
    assert np.allclose([s['gain'] for s in c['skills']], [7.0, math.log(0.5 / 0.3)])
    assert {l['reason'] for l in c['lessons']} == {'taught', 'graded wrong'}      # spring and drag share no node
    assert CR._shared_node(grammar.canonical(SPRING + DRAG), DRAG) is None
    assert CR._shared_node((('speed', 'growing'),), DRAG) == ('v', 'base', 'base')


def _cert(family, accepted=True, reasons=()):
    return types.SimpleNamespace(family=tuple(family), accepted=accepted, reasons=tuple(reasons), rivals={},
                                 alpha=1e-3, adequacy=None, band=None, eps=0.2, audit='universe-1')


def test_the_office_queue_proves_each_job_once_and_survives_a_stopped_worker(tmp_path, monkeypatch):
    from legacy.sera_v3 import proofs as PR
    monkeypatch.setattr(PR, 'policy', lambda: dict(audit='universe-1', band='claim', numerator='laplace', knock='throw'))
    calls = []

    def fake(job):
        calls.append(job['key'])
        return dict(key=job['key'], cert=_cert(job['family']), verified=True, why=None, cpu=1.0, wall=1.0)

    monkeypatch.setattr(PR, 'prove', fake)
    office = PR.Office(tmp_path)
    ledger = types.SimpleNamespace(audit_shared={'fit': 1})
    office.submit('a', ledger, (XV,), 0.2, world='w')
    office.submit('b', ledger, SPRING, 0.2)
    assert ledger.audit_shared is None and office.waiting() == 2 and not office.ready('a')
    stuck = PR.claim(tmp_path)                            # a worker claims a job and stops before proving it
    PR.recover(tmp_path)                                  # the office restarts: the job goes back to the queue
    assert stuck is not None and office.waiting() == 2
    assert PR.work_one(tmp_path)['key'] in ('a', 'b') and PR.work_one(tmp_path) is not None
    assert PR.work_one(tmp_path) is None and sorted(calls) == ['a', 'b'] and office.waiting() == 0
    res, job = office.take('a')
    assert res['verified'] and job['world'] == 'w' and job['family'] == (XV,)


def test_a_judged_sentence_must_say_what_the_judge_decided():
    from legacy.sera_v3 import narrate as NR
    res = dict(cert=_cert((XV,), accepted=False, reasons=('a rival family is not ruled out: x',)), verified=False,
               why=None)
    s = NR.say('judged', -1, law=(XV,), world='w1', proven=False, why=NR.judged_reason(res))
    assert NR.check_judged(s, res, 'w1', (XV,))[0]
    lie = NR.say('judged', -1, law=(XV,), world='w1', proven=True, why='')
    assert not NR.check_judged(lie, res, 'w1', (XV,))[0]
    assert not NR.check_judged(s, res, 'w2', (XV,))[0]


def test_a_proof_from_the_office_is_knowledge_and_vocabulary_and_a_refusal_a_lesson():
    m = M.Memory()
    _episode(m, None)                                     # the world's own episode ended: then the verdict comes
    assert m.judged(_ctx(), _cert((XV,)), True, vocab=[XV])
    assert m.vocab_terms() == (XV,) and len(m.to_bytes()) == M.MEMORY_BYTES
    assert m.summary()['lessons_open'] == 0
    assert not m.judged(_ctx(), _cert((XV,), accepted=True), False)        # the checker refused: nothing written
    assert not m.judged(_ctx(), _cert(SPRING, accepted=False, reasons=('something else is here: x',)), False)
    assert m.summary()['lessons_open'] == 1 and len(m.to_bytes()) == M.MEMORY_BYTES


def test_kinds_predict_from_looks_after_weighing_and_shrink_toward_the_mean():
    from legacy.sera_v3 import rooms as RM
    k = RM.Kinds()
    assert k.predict((2, 0, 1)) == (None, 0)
    for m in (2.9, 3.1, 3.0):
        k.learn((2, 0, 1), m)
    for m in (0.5, 0.6):
        k.learn((1, 1, 0), m)
    heavy, n = k.predict((2, 0, 1))
    light, _ = k.predict((1, 1, 0))
    unseen, n0 = k.predict((0, 0, 0))
    assert n == 3 and n0 == 0 and light < unseen < heavy < 3.0     # shrunk toward the mean of all it weighed
    assert k.statements()[0].startswith('Things that look like [2, 0, 1] weigh about')


def test_a_room_is_a_world_with_looks_and_a_code_task_is_never_trivial():
    from legacy.sera_v3 import codedoor as CD, rooms as RM
    w = RM.room_world(1, 0)
    assert len(w.looks) == w.n_situations == len(w.room.things) and len(w.throws) == 2 * w.n_situations
    assert w.spec.family == grammar.canonical(w.room.terms)
    t = CD.code_world(1, 0)
    t2 = CD.code_world(1, 0)
    assert CD.name(t.program) == CD.name(t2.program)                  # deterministic
    from legacy.sera_v3 import general as GEN
    right = dict(program=t.program, accepted=True)
    off = (GEN.node('cons', GEN.node('lit', payload=8), t.program) if t.out_type == 'list'   # always one longer
           else GEN.node('iadd', t.program, GEN.node('lit', payload=1)))                    # always one more
    wrong = dict(program=off, accepted=True)
    assert CD.grade(t, right) == 'proven right' and CD.grade(t, wrong) == 'SURE AND WRONG'


def test_an_unbounded_band_is_said_as_no_bound_and_its_check_passes():
    from legacy.sera_v3 import express as EX
    cert = types.SimpleNamespace(family=SPRING, band=math.inf, eps=0.2, alpha=1e-3, rivals={}, scope=None,
                                 accepted=False)
    s = EX._say('band', dict(band=math.inf, eps=0.2))
    assert 'cannot put any bound' in s.text
    assert EX.check(s, types.SimpleNamespace(certificate=cert), types.SimpleNamespace(proven=None))[0]
    assert EX._close(-math.inf, -math.inf) and not EX._close(math.nan, math.nan) and not EX._close(math.inf, 1e300)
