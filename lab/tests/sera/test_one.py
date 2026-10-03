"""One SERA (plan revision 6): its one language, its words, its Field and loop, and one mind living worlds of two
subjects - a list task proven and invented, then a number task that uses the invention (one mind, across subjects).
"""
import math

import numpy as np

from sera import lang as LG, one as ONE, phi as PH, talk as TK, tasks as TS


def test_the_language_finds_a_sum_by_folding_and_nothing_is_given():
    assert 'sum' not in LG.INNATE and 'reverse' not in LG.INNATE and 'square' not in LG.INNATE
    probes = [{'l': l} for l in ([1, 2, 3], [], [5, -1], [2, 2, 7, 0])]
    found = [e for e, _ in LG.search({'l': 'list'}, 'num', probes, 7)]
    sums = [e for e in found if all(LG.safe(e, p, {}) == sum(p['l']) for p in probes)]
    assert sums, 'no expression sums the list'


def test_a_concept_is_a_function_of_the_language_and_a_table_draws_a_curve():
    sq = (LG.node('mul', LG.node('var', payload='_'), LG.node('var', payload='_')), '_')
    tab = (LG.node('tab', payload=((0.0, 1.0, 2.0), (0.0, 1.0, 0.0))), '_')
    cs = {1: sq, 2: tab, '_sig': {1: ('num', 'num'), 2: ('num', 'num')}}
    assert LG.safe(LG.node('c', LG.node('var', payload='n'), payload=1), {'n': 7}, cs) == 49
    assert LG.safe(LG.node('c', LG.node('var', payload='s'), payload=2), {'s': 1.5}, cs) == 0.5
    probes = [{'n': n} for n in range(6)]
    found = [e for e, _ in LG.search({'n': 'num'}, 'num', probes, 3, cs)]
    assert any(e[0] == 'c' for e in found)                           # its concepts are part of its search


def test_words_are_learned_across_situations():
    lex = TK.Lexicon(0)
    for k in range(4):
        lex.hear(['spring', 'far', 'back'], [('concept', 1), ('input', 'position'), ('sign', -1)])
        lex.hear(['drag', 'fast', 'back'], [('concept', 2), ('input', 'speed'), ('sign', -1)])
        lex.hear(['stiff', 'far', 'back'], [('concept', 3), ('input', 'position'), ('sign', -1)])
        lex.hear(['rub', 'fast', 'back'], [('concept', 4), ('input', 'speed'), ('sign', -1)])   # 'fast' without 'drag'
    assert lex.word_for(('sign', -1)) == 'back'
    assert lex.word_for(('input', 'position')) == 'far'
    assert lex.word_for(('concept', 2)) == 'drag'
    coined = lex.word_for(('concept', 9), coin=True)
    assert coined and coined not in lex.heard                        # its own name for a new idea


def test_the_layers_pool_understanding_laws_and_beliefs():
    F = PH.Field(0)
    hyps = {'a': (('sym', 'add'),), 'b': (('sym', 'mul'),)}
    logU, logL, logB, phi, tension = F.layers('k', [0.0], hyps, {'a': 0.0, 'b': 0.0}, {'a': 4.0, 'b': 4.0})
    assert abs(math.exp(phi['a']) - 0.5) < 1e-9
    F.understand('k', [0.0], 'x', (('sym', 'mul'),), True, 1.0, 't')
    _, _, _, phi, _ = F.layers('k', [0.0], hyps, {'a': 0.0, 'b': 0.0}, {'a': 4.0, 'b': 4.0})
    assert phi['b'] > phi['a']                                       # understood parts weigh more


def test_the_loop_is_taught_then_its_own():
    loop = PH.LoopField()
    rng = np.random.default_rng(0)
    moment = dict(doubt=1.0, misfit=0.0)
    est = {f: 0.0 for f in PH.FACULTIES}
    for _ in range(30):
        loop.teach('k', moment, est, set(PH.FACULTIES), ['ask'])
    counts = {}
    for _ in range(50):
        config, _ = loop.choose('k', moment, est, set(PH.FACULTIES), rng)
        counts[config[0]] = counts.get(config[0], 0) + 1
    assert max(counts, key=counts.get) == 'ask'                     # what it was shown
    for _ in range(40):
        loop.learn('grow', loop.features(moment, est, 'grow'), 5.0)  # its own evidence: growing pays here
        loop.learn('ask', loop.features(moment, est, 'ask'), -2.0)
    counts = {}
    for _ in range(50):
        config, _ = loop.choose('k', moment, est, set(PH.FACULTIES), rng)
        counts[config[0]] = counts.get(config[0], 0) + 1
    assert max(counts, key=counts.get) == 'grow'                    # then its own way


def test_one_mind_learns_a_list_task_then_uses_it_for_numbers():
    sera = ONE.Sera(1)
    t1 = TS.list_task('list: sum', sum, 'num', 1, 0, words=['sum'])
    r1 = sera.live(t1, teaching=True, max_steps=60)
    assert r1['proven'] and r1['verdict'] == 'proven right', r1
    assert r1['invented'], 'the proven sum became a concept'
    t2 = TS.number_task('number: triangle', lambda n: n * (n + 1) // 2, 1, 3, words=['triangle'])
    r2 = sera.live(t2, teaching=True, max_steps=60)
    assert r2['proven'] and r2['verdict'] == 'proven right', r2
    assert r1['invented'][0]['id'] in r2['reused']                  # the list's sum, used for a number rule


def test_a_steady_push_claimed_as_a_curve_in_time_is_banded(monkeypatch):
    """2026-09-28 (the first long run: 'wind 1' refused for two hours with a band of inf): the band's flexible fit,
    started only from its own prequential posterior, called six of the eight objects knocked and fitted far below the
    claim itself (loglik -618 against 7110), so every law on time failed closed. Started also from the claim's own
    best fit (truth.flexible_fit), it is never below that fit, and the steady wind is proven as a curve in time."""
    from ccops5.core import grammar, likelihood as L, truth
    monkeypatch.setattr(truth, 'BAND', 'claim')
    monkeypatch.setattr(truth, 'CLAIM', 'functional')                 # the program's policies (scripts/sera_one.py)
    w, signs = TS.rail_world(1, 80_200, (('nothing', 'steady'),), 1)
    task = TS.Rail(w, 'wind', [], signs)
    fam = (('cell', 'time', 9),)
    scope = truth.scope_of(task.throws)
    checks = truth.functional_checks(fam)
    base = truth.model_of(fam, extra_basis=True, scope=scope)
    extra = [c for cell in checks for c in grammar.term_codes(cell)]
    model = base.extended([c[0] for c in extra], [c[1] for c in extra], [c[2] for c in extra])
    post = truth.prequential_exact(model, task.throws, task.sigma, truth._band_numerator())[1]
    flex = truth.flexible_fit(model, task.throws, task.sigma, fam, post)
    cm = truth.model_of(fam)
    own = L.fit(cm, task.throws, task.sigma, start=truth.prequential_exact(cm, task.throws, task.sigma)[1], iters=40)
    assert flex.ok and flex.loglik >= own.loglik - 1e-6
    ok, cert, why = task.verify(fam)
    assert math.isfinite(cert.band)                  # was inf; 0.41 on the teacher's 16 throws alone (the force near a
    from sera import field as FD                     # throw's end barely shows in what is seen): more pushes prove it
    rng = np.random.default_rng(5)
    while len(task.throws) < 16 + 8 * 8:
        for k in range(8):
            task.act(('push', k, FD.sample_programs(rng, 1)[0]))
    ok, cert, why = task.verify(fam)
    assert ok, (why, cert.band)
    assert task.grade(cert, ok)['verdict'] == 'proven right'


def test_sera_looks_closer_where_its_idea_misses_and_can_write_new_dimensions():
    """Revision 6.2-6.3 (the author: "it can improve its own drawing and get more abilities to perceive"; "more
    dimensions"): on a rub (a step at zero speed), after its finest whole-speed curve, its own evidence picks a lens on
    speed around 0 - nothing about the world is given - and it can write new dimensions in its own language."""
    from ccops5.core import grammar
    w, signs = TS.rail_world(1, 80_400, (('speed', 'steps'),), 1)
    task = TS.Rail(w, 'rub', [], signs)
    sera = ONE.Sera(1)
    led = task.ledger([(('cell', 'speed', 33),)])
    mu = task.masses(led, (('cell', 'speed', 33),))
    look = sera._where_to_look(task, (('speed', 'curve', 33),), {}, mu)
    assert look is not None and grammar.is_lens(look[0]) and grammar.base_input(look[0]) == 'speed', look
    lo, hi = grammar.input_range(look[0])
    assert lo < 0 < hi and look[1] > ONE.LOOK_NATS
    dims = sera._dimensions(task)
    assert any(sorted(grammar.dim(d)[0]) == ['mul', 'v', 'x'] for d in dims)      # position times speed, its own
    e = LG.node('add', LG.node('var', payload='x'), LG.node('mul', LG.node('var', payload='v'), LG.node('one')))
    assert ONE._tokens(e) == ('x', 'v', '1', 'mul', 'add')


def test_its_methods_of_imagination_are_its_own_triggered_and_grow():
    """Revision 7 (the author: "teach it the methods of imagination and let it develop its own; keep it unbounded"; "let
    it make its own moves, as a superposition that can be triggered or influenced"): methods are drawn from a
    superposition whose worth depends on the moment; the one that pays in a moment is learned for that moment; a
    method whose idea was proven becomes a move of its own, and chains further."""
    M = PH.MethodField()
    moves = set(PH.MOVES)
    short = dict(doubt=1.0, short=1.0, level=0.7)                      # the judge finds a grown idea short
    calm = dict(doubt=0.1, level=0.3)
    assert ('keep', 'closer') in M.candidates()
    rng = np.random.default_rng(0)
    for _ in range(150):                                               # (more moves since 'wish': more to try)
        for moment, good in ((short, ('keep', 'closer')), (calm, ('recall',))):
            for m in M.choose('k', moves, moment, rng):
                M.learn('k', m, moment, 30.0 if m == good else -3.0)
    assert M.choose('k', moves, short, np.random.default_rng(1))[0] == ('keep', 'closer')
    assert M.choose('k', moves, calm, np.random.default_rng(1))[0] == ('recall',)
    assert M.triggers('k', ('keep', 'closer')).get('short', 0) > 0
    nid = M.name(('keep', 'closer'), 'a rub')
    assert nid == 1 and M.name(('keep', 'closer'), 'again') is None and M.named[0]['uses'] == 2
    assert ('#1',) in M.candidates() and ('#1', 'question') in M.candidates()      # its own move, chained further
    assert M.expand(('#1', 'question')) == ('keep', 'closer', 'question')
    M.teach('k', ('blend',), calm)
    before = float(M._post('k', ('blend',))[0] @ M.features(calm))
    for _ in range(10):
        M.end_task()                                                   # what it was taught fades
    assert float(M._post('k', ('blend',))[0] @ M.features(calm)) < before


def test_it_asks_what_mass_is_from_what_it_measured():
    """'Mass should not stay only mass' (the author): after a proof it asks how many kinds of mass there are, telling
    masses apart by their own uncertainty, and keeps the answer across worlds."""
    class Fit:
        pass
    f = Fit()
    f.order = list(range(8))
    f.coef = np.array([1.0])
    masses = [0.8, 1.6, 0.8, 2.4, 1.6, 0.8, 2.4, 1.6]
    f.mu = {i: 1.0 / m for i, m in enumerate(masses)}
    f.cov = np.eye(9) * 1e-6
    sera = ONE.Sera(1)

    class T:
        name = 'a rail'
    q = sera._what_is_mass(T(), f)
    assert q['things'] == 8 and q['kinds'] == 3 and q['masses'] == [0.8, 1.6, 2.4]
    assert 'only 3 kinds of mass' in q['text'] and sera.field.questions[-1]['what'] == 'mass'
    for _ in range(2):
        q = sera._what_is_mass(T(), f)
    assert 'In all 3 worlds' in q['text']


def test_units_are_found_only_where_masses_are_whole_multiples():
    sd = np.full(3, 1e-4)
    u = ONE.Sera._unit_of(np.array([0.5, 1.0, 1.5]), sd, [[0], [1], [2]])
    assert u is not None and abs(u[0] - 0.5) < 1e-6 and u[1] == [1, 2, 3]
    assert ONE.Sera._unit_of(np.array([0.9, 1.37, 2.21]), sd, [[0], [1], [2]]) is None
    assert ONE.Sera._unit_of(np.array([0.5, 1.0]), sd[:2], [[0], [1]]) is None     # two kinds always fit some unit


def test_it_can_see_through_a_sense_of_one_input_and_thinks_bigger_without_a_ceiling():
    """2026-09-28 (the author: "sera must not get stuck; if it's bad it must find the correct one"): no curve drawn in
    position passed the judge on the stiff spring, but it is a straight line in position cubed - a sense of one input it
    may now write (the input merely rescaled is nothing new) - and thinking bigger has no ceiling."""
    from ccops5.core import grammar
    w, signs = TS.rail_world(1, 80_300, (('position', 'cubic'),), 1)
    task = TS.Rail(w, 'stiff', [], signs)
    sera = ONE.Sera(1)
    toks = [grammar.dim(d)[0] for d in sera._dimensions(task)]
    assert any(sorted(t) == ['mul', 'mul', 'x', 'x', 'x'] for t in toks)
    assert not any(set(t) <= {'x', 'add', 'sub', '0', '1'} for t in toks)
    assert sera._max_level(task) == math.inf and ONE.part_size(5) > ONE.part_size(4) > ONE.part_size(3) == 8
    assert ONE.exact_size(9) > ONE.exact_size(8) > ONE.exact_size(7) == 12


def test_asking_us_with_no_idea_at_all_on_an_exact_task():
    # Out of time before any idea (SERA-U's 10 s assessment wall reached it): it asks about 'nothing', no crash.
    sera = ONE.Sera(3)
    task = TS.number_task('tiny', lambda x: x, 3, 0)
    said = []
    sera._ask_us(task, None, 0.0, dict(none_fit=True), lambda kind, text, **kw: said.append(text), cap=True)
    assert said and 'my best idea is nothing' in said[0]
