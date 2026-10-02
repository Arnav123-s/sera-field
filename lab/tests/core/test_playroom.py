"""T4b step 1 (docs/SERA_PLAYROOM.md v0.1 §1-2, sera-v3 5588f76): the room and the caretaker. Written before the code.
  - rooms are deterministic; things have visible looks (codes, never words) and hidden masses by kind: iron > wood >
    rubber > foam, big heavier by 0.4 in log mass, shape carrying no mass;
  - the room-law words are a total function: 'nothing' exactly when no other word is true; known regimes give the
    known words;
  - the caretaker's words follow §2's likelihood exactly (templates uniform over all, uniform over true words, slip
    eps, a uniform word when none is true);
  - R-P: what it says after throw n depends only on the room and the throws so far - never on their noise.
"""
import collections
import math
from types import SimpleNamespace

import numpy as np

from ccops5.core import playroom as R


def test_rooms_are_deterministic():
    a, b = R.make_room(1, 0), R.make_room(1, 0)
    assert a.regime == b.regime and a.coefs == b.coefs
    assert [(t.material, t.size, t.shape, t.mass, t.bump) for t in a.things] == \
           [(t.material, t.size, t.shape, t.mass, t.bump) for t in b.things]
    assert 4 <= len(a.things) <= 6


def test_things_have_looks_not_words_and_masses_by_kind():
    rooms = [R.make_room(1, i) for i in range(400)]
    things = [t for r in rooms for t in r.things]
    words = {w for ws in R.WORDS.values() for w in ws}
    assert all(isinstance(c, int) for t in things for c in t.look)
    assert not any(str(c) in words for t in things for c in t.look)
    logm = collections.defaultdict(list)
    for t in things:
        logm[t.material].append(math.log(t.mass) - R.BIG * (t.size == 'big'))
    means = {m: float(np.mean(v)) for m, v in logm.items()}
    assert means['iron'] > means['wood'] > means['rubber'] > means['foam'], means
    for m, v in logm.items():
        assert abs(means[m] - R.A_MATERIAL[m]) < 0.05, (m, means[m])
    big = np.mean([math.log(t.mass) - R.A_MATERIAL[t.material] for t in things if t.size == 'big'])
    small = np.mean([math.log(t.mass) - R.A_MATERIAL[t.material] for t in things if t.size == 'small'])
    assert abs((big - small) - R.BIG) < 0.05
    ball = np.mean([math.log(t.mass) - R.A_MATERIAL[t.material] - R.BIG * (t.size == 'big')
                    for t in things if t.shape == 'ball'])
    block = np.mean([math.log(t.mass) - R.A_MATERIAL[t.material] - R.BIG * (t.size == 'big')
                     for t in things if t.shape == 'block'])
    assert abs(ball - block) < 0.05                                  # shape is the distractor: no mass in it


def test_the_room_words_are_a_total_function_and_right_on_known_regimes():
    known = {'spring': {'pull back'}, 'rubbing': {'slow down'}, 'slope': {'push along'}, 'none': {'nothing'},
             'rubbing+spring': {'pull back', 'slow down'}, 'swing': {'pull back', 'wave'}}
    for regime in R.REGIMES:
        terms, coefs = R.regime_law(regime, np.random.default_rng(0))
        truth = R.room_words(terms, coefs)
        assert set(truth) == set(R.WORDS['room'])
        assert truth['nothing'] == (not any(v for w, v in truth.items() if w != 'nothing')), regime
        if regime in known:
            assert {w for w, v in truth.items() if v} == known[regime], (regime, truth)


def _past(n, situation, noise=0.0):
    return [SimpleNamespace(situation=situation, x=np.full(41, noise), v=np.full(41, noise)) for _ in range(n + 1)]


def test_the_caretaker_speaks_by_its_likelihood():
    room = R.make_room(3, 0, n_things=5)                             # 5 things: the median one is neither heavy nor light
    care = R.Caretaker(room)
    counts, spoken, total, past = collections.Counter(), collections.Counter(), 0, []
    for n in range(100_000):
        k = n % len(room.things)
        past.append(k)
        s = care.speak(past)
        total += 1
        if s is None:
            continue
        counts[(s.template, s.topic, s.word)] += 1
        spoken[(s.template, s.topic)] += 1
    assert abs(sum(spoken.values()) / total - R.P_SPEAK) < 0.01
    per_template = collections.Counter()
    for (tpl, _), c in spoken.items():
        per_template[tpl] += c
    for tpl in R.TEMPLATES:                                          # uniform over ALL templates, whatever is true
        assert abs(per_template[tpl] / sum(per_template.values()) - 1 / len(R.TEMPLATES)) < 0.01, tpl
    for (tpl, topic), n_cell in spoken.items():
        for w in R.WORDS[tpl]:
            p = care.likelihood(tpl, topic, w)
            got = counts[(tpl, topic, w)] / n_cell
            se = math.sqrt(p * (1 - p) / n_cell)
            assert abs(got - p) <= 5 * se + 1e-9, (tpl, topic, w, got, p)
    median = sorted(range(5), key=lambda i: room.things[i].mass)[2]
    assert care.true_words('property', median) == ()
    assert all(abs(care.likelihood('property', median, w) - 0.5) < 1e-12 for w in R.WORDS['property'])


def test_the_caretaker_never_uses_throw_noise():
    room = R.make_room(4, 2)
    a, b = R.Caretaker(room), R.Caretaker(room)
    for n in range(300):
        k = (7 * n) % len(room.things)
        quiet, loud = _past(n, k, 0.0), _past(n, k, 5.0)            # same throws so far, different readings
        assert a.speak(tuple(t.situation for t in quiet)) == b.speak(tuple(t.situation for t in loud))
    import inspect                                                  # structural (C1): it is given situations only
    assert list(inspect.signature(R.Caretaker.speak).parameters) == ['self', 'situations']


def test_room_words_refuse_unknown_term_kinds():
    import pytest
    with pytest.raises(ValueError):
        R.room_words((('piece', 'speed', 'abs', 0.0),), (-1.0,))


def test_throws_are_the_rail_with_the_things_knock():
    room = R.make_room(5, 1)
    from ccops5.core import worlds as W
    t1 = room.throw(0, W.Action(((0.0, 0.4, 1.0),)), 0)
    t2 = room.throw(0, W.Action(((0.0, 0.4, 1.0),)), 0)
    assert np.array_equal(t1.x, t2.x) and t1.situation == 0         # deterministic by throw number
    t3 = room.throw(0, W.Action(((0.0, 0.4, 1.0),)), 1)
    assert not np.array_equal(t1.x, t3.x)                           # fresh noise per throw number
