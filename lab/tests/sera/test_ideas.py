"""What comes to mind (sera.phi.Ideas.comes_to_mind): what the Field rings back - its memory is the Field's own state,
superposed, with no record kept and no recall step (2026-09-29 night, the author)."""
import pickle

from sera import phi as PH


def _read(ideas, *sentences):
    for s in sentences:
        ideas.read(tuple(s.split()))


def test_a_common_word_alone_brings_nothing_and_a_rare_name_does():
    ideas = PH.Ideas()
    _read(ideas, *[f'w{k} is here' for k in range(100)], 'finn is in the kitchen')
    assert ideas.comes_to_mind(['is']) == []
    assert ideas.comes_to_mind(['finn']) == [tuple('finn is in the kitchen'.split())]


def test_what_it_read_long_ago_still_comes_to_mind():
    """ideas-4 (2026-09-29): after two more books, a psychology definition had faded to nothing. In the Field only a
    thing's own later sentences dilute what it holds; the rest of what it reads does not wear it away."""
    ideas = PH.Ideas()
    _read(ideas, 'phobia is an irrational fear', *[f'w{k} went home' for k in range(2000)])
    assert tuple('phobia is an irrational fear'.split()) in ideas.comes_to_mind(['what', 'is', 'phobia'])


def test_nothing_is_kept_as_a_record():
    ideas = PH.Ideas()
    _read(ideas, *[f'w{k} slept' for k in range(20)], 'zork is a blue fish', 'zork swam home')
    assert all('situations' not in d for d in ideas.of.values())
    assert ideas.comes_to_mind(['zork']) == [tuple('zork swam home'.split()), tuple('zork is a blue fish'.split())]


def test_the_latest_rings_loudest():
    ideas = PH.Ideas()
    _read(ideas, 'finn went to the kitchen', *[f'w{k} slept' for k in range(50)], 'finn went to the garden')
    assert ideas.comes_to_mind(['where', 'is', 'finn'], most=1) == [tuple('finn went to the garden'.split())]
    assert ideas.comes_to_mind(['finn']) == [tuple('finn went to the garden'.split()),
                                             tuple('finn went to the kitchen'.split())]


def test_a_saved_field_keeps_its_memory_and_an_older_one_is_laid_in():
    ideas = PH.Ideas()
    _read(ideas, *[f'w{k} slept' for k in range(30)], 'mira went to the office')
    again = pickle.loads(pickle.dumps(ideas))
    assert again.comes_to_mind(['mira']) == [tuple('mira went to the office'.split())]
    old = PH.Ideas()                                     # as a SERA saved before the Field held its memory
    for k in range(30):
        old.read((f'w{k}', 'slept'))
    old.read(('mira', 'went', 'to', 'the', 'office'))
    for d in old.of.values():
        d['situations'] = []
    old.of['mira']['situations'] = [(('mira', 'went', 'to', 'the', 'office'), 0, '', 31)]
    for k in ('_E', '_M', '_row', '_n'):
        delattr(old, k)
    old._field_state()
    assert old.comes_to_mind(['mira']) == [tuple('mira went to the office'.split())]
    assert all('situations' not in d for d in old.of.values())


def test_a_long_sentence_comes_to_mind_as_much_as_its_language_can_hold():
    """A memory longer than the language's lists (lang.MAX_LEN) would make every program on the situation fail."""
    from sera import lang as LG, tasks as TS
    world = TS.closed_where(1)
    x = world.data[0][0]
    name = x[0][-1]
    ideas = PH.Ideas()
    for k in range(20):                                  # other things read, so the name is rare enough to tell
        ideas.read((TS.sym(f'w{k}'), TS.sym('slept')))
    ideas.read(tuple([name] + [TS.sym('went')] * 100))
    ideas.read(tuple([name, TS.sym('went'), TS.sym('to'), TS.sym('the'), TS.sym('kitchen')]))
    world.mind = ideas
    seen = world.perceive(x)
    assert len(seen) > len(x) and all(len(s) <= LG.MAX_LEN for s in seen[len(x):])


def test_a_proven_idea_rings_back_from_its_situation():
    """The automatic trigger: an idea laid into a situation's things rings back when a situation like it is met."""
    ideas = PH.Ideas()
    _read(ideas, *[f'w{k} went to the kitchen' for k in range(40)])
    for t in ('where', 'is', 'w1'):
        ideas.bind(t, ('concept', 7), 1.0)
    rang = ideas.evoked(['where', 'is', 'w5'], [('concept', k) for k in range(3, 12)])
    assert rang and rang[0][0] == ('concept', 7)
    assert ideas.evoked(['w6', 'went'], [('concept', k) for k in range(3, 12)]) == []


def test_what_a_confirmed_answer_rested_on_is_strengthened():
    ideas = PH.Ideas()
    _read(ideas, *[f'w{k} slept' for k in range(30)], 'mira went to the office', 'mira went to the garden')
    came = ideas.comes_to_mind(['mira'])
    assert came[0] == tuple('mira went to the garden'.split())
    n = ideas.consolidate(1.0, lambda sent, cues: 'office' in sent and set(cues) <= {'mira'})   # the confirmed
    #                                                                         answer, about the question's mira
    assert n == 1
    assert ideas.comes_to_mind(['mira'])[0] == tuple('mira went to the office'.split())


def test_ideas_laid_into_question_words_do_not_blur_what_comes_to_mind():
    """ideas-7 (2026-09-29): ideas bound into 'where' (a word met only in questions, so as rare as can be) pressed on
    every recall and cut 'n7 went to the office' to 'n7 went'. Only what it has read brings sentences to mind."""
    ideas = PH.Ideas()
    for k in range(30):
        ideas.read((f'n{k}', 'went', 'to', 'the', ('kitchen', 'office', 'garden')[k % 3]))
    for t in ('where', 'is'):
        for c in range(5):
            ideas.bind(t, ('concept', c), 1.0)
    assert ideas.comes_to_mind(['where', 'is', 'n7'])[:1] == [('n7', 'went', 'to', 'the', 'office')]


def test_the_echo_credits_what_took_part_and_a_refutation_weakens_it():
    """The echo (the author's HEB + e-prop, adapted): a traced method of imagining is credited by a proof and weakened,
    more softly, by a refutation; a trace is spent once echoed."""
    import numpy as np
    moment = {'doubt': 1.0}
    x = PH.MethodField.features(moment)

    def value(f):
        return float(f.methods._post('k', ('compose',))[0] @ x)

    up, down = PH.Field(1), PH.Field(1)
    base = value(up)
    for f, signal in ((up, 1.0), (down, -0.25)):
        f.trace(('method', 'k', ('compose',), moment))
        assert f.echo(signal) == 1
        assert f.echo(signal) == 0                          # spent
    assert value(up) > base > value(down)
    assert np.isfinite(value(down))
