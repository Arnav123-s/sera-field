"""the reviewer's S09 (2026-10-01), item 4: in a program world the examples' verdict reaches the Field. Its doubt is relative
- "0.0 nats" while its best idea fits no example - so whether any idea fits is told apart, fresh on every pass."""
from unittest.mock import patch

from sera import lang as L, one as O, phi as P, tasks as T

N = L.node


def _run(hyps, ranks=None, steps=3, task=None):
    """Live a number world (x + 1) with the given ideas; returns what each moment saw and which leaders were tried."""
    s = O.Sera(1, P.Field(1))
    t = task or T.number_task('s09 fit', lambda x: x + 1, 1, 4)
    seen, tried = [], []
    real_layers = s.field.layers

    def layers(kind, ctx, hparts, logE, bits):
        out = list(real_layers(kind, ctx, hparts, logE, bits))
        if ranks is not None:                           # the Field's own ranking, forced (a wrong idea first)
            out[3] = {h: ranks.get(h, -50.0) for h in logE}
        return tuple(out)

    def choose(kind, moment, est, available, rng):
        seen.append(dict(misfit=moment['misfit'], grow=est['grow'], prove='prove' in available))
        return (['prove'] if 'prove' in available else ['grow']), {f: (1., 1.) for f in ('prove', 'grow')}

    def prove(task, law, cs, lib, st, speak):
        st['tested'].add((law, len(task.data)))
        tried.append(law)
        return False

    with patch.object(s, '_generate', side_effect=lambda *a: list(hyps)), \
            patch.object(s, '_moves_available', return_value=set()), \
            patch.object(s.field, 'layers', side_effect=layers), \
            patch.object(s.field.loop, 'choose', side_effect=choose), \
            patch.object(s, '_prove', side_effect=prove), \
            patch.object(s, '_doubt_after', return_value=0.), \
            patch.object(s, '_finish', side_effect=lambda *a: dict(st=a[5])):
        r = s.live(t, max_steps=steps)
    return r['st'], seen, tried


RIGHT = N('add', N('var', payload='n'), N('one'))
WRONG = N('one')


def test_a_lone_wrong_idea_is_a_misfit_though_its_relative_doubt_is_nought():
    st, seen, tried = _run([WRONG])
    assert st['none_fit'] and st['leader_misfits']      # it knows, though its relative doubt is nought


def test_a_wrong_leader_gives_way_to_an_idea_that_fits():
    st, seen, tried = _run([WRONG, RIGHT], ranks={WRONG: 0.0, RIGHT: -5.0})
    assert not st['none_fit'] and st['leader_misfits']
    assert tried and tried[0] == RIGHT                    # the one that fits is proven, not the one it ranks first


def test_a_right_idea_raises_no_false_alarm():
    st, seen, tried = _run([RIGHT])
    assert not st['none_fit'] and not st['leader_misfits']


def test_a_new_example_is_seen_on_the_next_pass():
    lucky = N('if', N('lt', N('var', payload='n'), N('lit', payload=5)), RIGHT, N('zero'))   # right below 5 only
    t = T.number_task('s09 fresh', lambda x: x + 1, 1, 4)
    st, seen, tried = _run([lucky], task=t)
    assert not st['none_fit']                                   # it fits the examples it has
    t = T.number_task('s09 fresh', lambda x: x + 1, 1, 4)
    t.data.append((7, 8))                                       # an audit's counterexample, now an example
    st, seen, tried = _run([lucky], task=t)
    assert st['none_fit']                                       # seen on the pass that has it


def test_the_teacher_shows_a_step_when_none_of_its_ideas_fits():
    """The general SERA's 'where' (2026-10-01): sure of an idea that fits no example (0 nats of doubt), it was never
    shown the step that finds the answer in 68 s. The teacher sees what fits: none fits once thinking bigger is no
    longer cheap - a step, then a wish, and imagining over the default; before that level, or while an idea fits and
    it is sure, nothing new is shown."""
    moment = dict(doubt=0.0, misfit=0.0, proven=0.0)
    moves = {'step', 'wish', 'compose'}
    st = dict(level=O.NOFIT_LEVEL - 1, judge_short=0.0, none_fit=True, explored=0)
    assert O.Sera.teacher_method(moment, moves, st) is None     # a bigger search is still the quick way
    st['level'] = O.NOFIT_LEVEL
    assert O.Sera.teacher_method(moment, moves, st) == ('step',)
    assert O.Sera.teacher_method(moment, {'wish', 'compose'}, st) == ('wish',)
    assert O.Sera.teacher_way(moment, {'imagine', 'grow', 'ask'}, st, ('step',)) == ['imagine']
    st['none_fit'] = False
    assert O.Sera.teacher_method(moment, moves, st) is None
    assert O.Sera.teacher_way(moment, {'imagine', 'grow', 'ask'}, st, None) != ['imagine']


def test_a_step_cut_short_with_steps_untried_may_be_taken_up_again():
    """S10 (reviewer): a step chained after another move had only what was left, and its attempt was then "made already" -
    the general SERA's 'where' was never stepped again. Cut by time with steps it has not tried, it may take them up
    again; looked through (or nothing left to try), it is made."""
    s = O.Sera(1, P.Field(1))
    t = T.number_task('s10 cut', lambda x: x + 1, 1, 4)
    wrong = N('one')
    st = dict(level=O.NOFIT_LEVEL, none_fit=True, judge_short=0.0, moved=set(), thought=set())
    s._open_steps = []

    def cut(open_steps):
        def step(*a, **kw):
            s._step_cut = True
            s._open_steps = list(open_steps)
            return []
        return step

    key = s._attempt('step', t, {}, st)
    with patch.object(s, '_step', side_effect=cut([dict(step=N('zero'), type='num', features=None)])):
        s._move('step', t, O.kind_of(t), wrong, {}, (), None, st, [wrong], {}, lambda *a, **kw: None)
    assert key not in st['moved']                               # steps left untried: not spent
    with patch.object(s, '_step', side_effect=cut([])):
        s._move('step', t, O.kind_of(t), wrong, {}, (), None, st, [wrong], {}, lambda *a, **kw: None)
    assert key in st['moved']                                   # nothing left to take up: spent


def test_lambda_bodies_cut_by_the_work_bound_continue_and_lose_nothing():
    """S10 (reviewer): λ bodies were searched with no work bound, so a size cut at MAX_WORK lost its rest for good. With
    the search's bound, a cut size continues when asked again with a larger one, and ends as the whole search does."""
    L.forget_searches()
    L.DEADLINE[0] = float('inf')
    full = {repr(p) for p, _ in L.lambda_bodies('e', 'num', 5)}
    L.forget_searches()
    first = L.lambda_bodies('e', 'num', 5, work=50)
    assert not L.COMPLETE[0] and len(first) < len(full)           # cut: what it has is less, and it knows
    again = {repr(p) for p, _ in L.lambda_bodies('e', 'num', 5, work=10 ** 9)}
    assert L.COMPLETE[0] and again == full                         # taken up again: nothing lost
    L.forget_searches()


def test_its_physics_expression_reaches_the_judge_said_exactly(monkeypatch):
    """Items 1-2 (S09's smallest step: the judge's own priced language, no new judge): stiff 2's cubic, which was sent
    as a 9-knot curve that missed by hundreds of sensor sigmas, now goes as the cubic dimension and is accepted. The
    judge's policies as the runs set them (Decisions 8, 12, 13), here, not by whichever test ran first (S10, reviewer)."""
    from ccops5.core import checker, grammar, truth
    monkeypatch.setattr(grammar, 'SHAPES_POLICY', 'library')
    monkeypatch.setattr(grammar, 'SHAPE_WEIGHT', 0.01)
    monkeypatch.setattr(truth, 'BAND', 'claim')
    monkeypatch.setattr(truth, 'CLAIM', 'functional')
    w, signs = T.rail_world(3, 80301, (('position', 'cubic'),), 1)
    task = T.Rail(w, 'rail: stiff 2', (), signs)
    s = N('var', payload='s')
    part = ('position', 'expr', N('mul', s, N('mul', s, s)))
    fam = task.claim_family((part,), {}, ())
    assert fam == (('cell', 'dim:x.x.x.mul.mul@4', 9),)
    led = task.ledger([fam])
    cert = truth.certify(led, fam, T.EPS, claim='functional')
    assert cert.accepted and cert.band <= T.EPS
    assert checker.check(cert, task.throws, task.sigma)[0]
    assert task.grade(cert, True)['verdict'] == 'proven right'
    lit = ('position', 'expr', N('mul', N('lit', payload=3), s))         # a literal the dimensions cannot say:
    assert task.claim_family((lit,), {}, ()) == (('cell', 'position', 33),)   # the full curve, never coarser
    sq = {1: (N('mul', N('var', payload='_'), N('var', payload='_')), '_'), '_sig': {1: ('num', 'num')}}
    viac = ('position', 'expr', N('mul', s, N('c', s, payload=1)))      # a concept, written out
    assert task._as_dimension(viac, sq) == 'dim:x.x.x.mul.mul@4'
