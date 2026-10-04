import json
import torch
import pytest

from sera import lang as LG, tasks as TS
from sera_u import SeraU
from sera_u.field.native_owner import NativeConfig
from sera_u.mind import U14_CRUTCHES
from sera_u.ports import TaskView
from scripts.sera_u_rsi import fresh_exam, queue_exam, grade_question


def entity():
    torch.set_num_threads(1)
    return SeraU(3, config=NativeConfig(nodes=3, rounds=1), clock='work',
        u14={k: k == 'questions_first' for k in U14_CRUTCHES})


def test_front_not_yet_checkpoint_late_answer(monkeypatch):
    m = entity()
    task = TS.number_task('outside', lambda x: x+1, 3, 1)
    view = TaskView.from_task(task)
    own = m.agenda.ask('an own question', 'own', 0, outside=False)
    asked = m.ask(view, 'outside')
    assert m.agenda.order[0] == asked
    assert m.agenda.next(m, priority=True) == asked
    answer = LG.node('add', LG.node('var', payload='x'), LG.node('one'))
    def pending(self, body, **kwargs):
        self.clock.charge('candidate', 11)
        return dict(proven=False, answer=None)
    monkeypatch.setattr(SeraU, 'live', pending)
    first = m.work_question(asked, body=task)
    assert first['status'] == 'open' and first['answer'] is None and first['work'] >= 11
    m = SeraU.loads(m.dumps())
    assert m.agenda.items[asked]['not_yet'] and own in m.agenda.items
    def solved(self, body, **kwargs):
        self.clock.charge('candidate', 7)
        return dict(proven=True, answer=answer)
    monkeypatch.setattr(SeraU, 'live', solved)
    late = m.work_question(asked, body=task)
    assert late['late'] and late['work'] >= first['work']+7 and late['answer'] == answer
    assert m.agenda.events[-1]['kind'] == 'late-answer'
    with pytest.raises(ValueError, match='already asked'):
        m.ask(view, 'outside')


def test_exam_once_per_life_and_grades_observer_only():
    p = LG.node('add', LG.node('var', payload='x'), LG.node('one'))
    spec = dict(name='e0', tin='num', tout='num', source='opaque', family='f', program=p,
                examples=(-2, 0, 1, 4), pool=(5, 6))
    m = entity()
    state = dict(protocol={'seed': 3})
    queue_exam(m, {'assessment': [spec]}, state, None, None, 0)
    queue_exam(m, {'assessment': [spec]}, state, None, None, 1)
    assert len(m.agenda.items) == 2
    assert len({q['public_digest'] for q in state['exam_items'].values()}) == 2
    assert all(type(q['question']) is TaskView for q in m.agenda.items.values())
    before = m.learning_hash()
    item = next(iter(state['exam_items'].values()))
    from scripts.sera_u_rsi import build_task
    grade_question(item, dict(answer=None, work=4, late=False), build_task(item['spec']), 3)
    assert item['status'] == 'not-yet' and item['right_at_first_answer'] is None
    grade_question(item, dict(answer=p, work=9, late=True), build_task(item['spec']), 3)
    assert item['answered_eventually'] and item['right_at_first_answer']
    assert item['late'] and item['work_to_answer'] == 9
    assert m.learning_hash() == before
    assert 'grade' not in repr(m.agenda.learning_state())


def test_agenda_demonstration_never_on_exam():
    m = entity()
    assert m.agenda.demonstrate(phase='lesson', origin='taught')
    assert not m.agenda.demonstrate(phase='lesson', origin='taught')
    with pytest.raises(ValueError):
        m.agenda.demonstrate(phase='test3', origin='alone')
