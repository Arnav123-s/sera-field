"""The crutch ledger (plan Phase 3.3): every registered crutch has a switch in SERA's code, the switches read the
environment, and a switched-off crutch is SERA as it was before it."""
import re
from pathlib import Path

import pytest

from sera import crutches as CR, one as O, tasks as T

SERA = Path(__file__).resolve().parents[2] / 'sera'
SERA_U = SERA.parent / 'sera_u'


def test_every_registered_crutch_has_a_switch_in_the_code():
    code = '\n'.join(p.read_text(encoding='utf-8') for p in SERA.glob('*.py'))
    used = set(re.findall(r"CR\.on\('(\w+)'\)", code))
    # SERA-U's crutches are switched by its arm (sera_u/mind.py arm_settings) and read as crutches['name']
    u_code = '\n'.join(p.read_text(encoding='utf-8') for p in SERA_U.glob('*.py'))
    used |= set(re.findall(r"crutches\['(\w+)'\]", u_code))
    # U3's switches are read through the entity's _u_on(name), by name or over its declared U*_CRUTCHES tuples
    used |= set(re.findall(r"_u_on\('(\w+)'\)", u_code))
    for names in re.findall(r"^U\d*_CRUTCHES = \(([^)]*)\)", u_code, re.M):
        used |= set(re.findall(r"'(\w+)'", names))
    assert used == set(CR.REGISTRY)
    assert all(c['status'] in ('fixed', 'taught', 'learned') for c in CR.REGISTRY.values())


def test_switches_read_the_environment(monkeypatch):
    monkeypatch.setenv('SERA_CRUTCH_OFF', 'talk_tally,way_back')
    assert CR._off() == {'talk_tally', 'way_back'}
    monkeypatch.setenv('SERA_CRUTCH_OFF', 'no_such_crutch')
    with pytest.raises(ValueError):
        CR._off()
    with pytest.raises(KeyError):
        CR.on('no_such_crutch')
    g = dict(BACK_ON=True, TALK_RATE=0.25, STEP_TRY=8)
    monkeypatch.setenv('SERA_KNOBS', 'BACK_ON=0,TALK_RATE=0.5,STEP_TRY=4')
    assert CR.set_knobs(g) == ['BACK_ON', 'TALK_RATE', 'STEP_TRY']
    assert g == dict(BACK_ON=False, TALK_RATE=0.5, STEP_TRY=4)
    monkeypatch.setenv('SERA_KNOBS', 'NOPE=1')
    with pytest.raises(ValueError):
        CR.set_knobs(g)


def test_a_crutch_off_is_sera_before_it(monkeypatch):
    st = dict(none_fit=True, level=O.NOFIT_LEVEL)
    assert O.Sera._none_fit_late(st)
    monkeypatch.setattr(CR, 'OFF', {'teacher_none_fits'})
    assert not O.Sera._none_fit_late(st)
    story = T.Story.__new__(T.Story)                   # the lesson words: offered, or not
    story.words = ['is', 'mary', 'in']
    story.data = [((('mary', 'went'),), 1)]
    monkeypatch.setattr(CR, 'OFF', set())
    assert story.numbers() == [T.sym(w) for w in story.words]
    monkeypatch.setattr(CR, 'OFF', {'lesson_words'})
    monkeypatch.setattr(T.Exact, 'numbers', lambda self, most=6: ['seen'])
    assert story.numbers() == ['seen']
