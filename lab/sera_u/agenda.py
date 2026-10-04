"""Public questions and continuations; never a world, grade, or callback."""
from .ports import TaskView, digest
from .discovery import Readout


class Agenda:
    def __init__(self):
        self.items, self.order, self.events = {}, [], []
        self.policy, self.teacher_shown = Readout(), False

    def ask(self, question, source, count, *, outside=True, parent=None):
        if type(question) not in (TaskView, str) or type(source) is not str or not source:
            raise TypeError('Only a public TaskView or heard text and an explicit source')
        key = digest((source, question.identity if type(question) is TaskView else question))
        if key in self.items:
            raise ValueError('Question already asked in this life')
        self.items[key] = dict(id=key, question=question, source=source, outside=outside,
            parent=parent, status='open', first_work=count, work=0, attempts=0,
            first_answer=None, answer=None, not_yet=False)
        self.order.insert(0 if outside else len(self.order), key)
        self.events.append(dict(kind='asked', id=key, outside=outside, at_work=count))
        return key

    def next(self, mind, *, priority=False, allowed=None):
        open_items = [k for k in self.order if self.items[k]['status'] == 'open' and
                      (allowed is None or k in allowed)]
        if not open_items:
            return None
        if priority:
            fresh = [k for k in open_items if self.items[k]['outside'] and not self.items[k]['not_yet']]
            if fresh:
                self.policy.pick(('outside',), mind.choice_features(), mind.numpy)
                return fresh[0]
        return self.policy.pick(open_items, mind.choice_features(), mind.numpy)

    @staticmethod
    def features():
        import numpy as np
        return np.r_[1., np.zeros(64)]

    def demonstrate(self, *, phase, origin):
        if phase not in ('lesson', 'study', 'test1') or origin != 'taught':
            raise ValueError('No agenda teaching on discovery/assessment worlds')
        if self.teacher_shown:
            return False
        self.policy.demonstrate('outside', self.features(), phase)
        self.teacher_shown = True
        return True

    def settle(self, key, answer, spent, at_work, *, features=None):
        item = self.items[key]
        if item['status'] != 'open':
            raise ValueError('Question already answered')
        item['attempts'] += 1
        item['work'] += spent
        if answer is None:
            item['not_yet'] = True
            self.events.append(dict(kind='not-yet', id=key, work=item['work'], at_work=at_work))
            self.order.remove(key)
            self.order.append(key)
        else:
            item.update(status='answered', answer=answer, first_answer=answer, answered_work=at_work)
            self.events.append(dict(kind='late-answer' if item['not_yet'] else 'answer', id=key,
                                    answer=answer, work=item['work'], at_work=at_work))
        self.policy.learn(key, self.features() if features is None else features,
                          float(answer is not None), max(1, spent))
        return dict(id=key, status=item['status'], answer=item['answer'], work=item['work'],
                    late=answer is not None and item['not_yet'])

    def learning_state(self):
        return {k: v for k, v in self.__dict__.items() if k != 'events'}

    def validate(self):
        if set(self.__dict__) != {'items', 'order', 'events', 'policy', 'teacher_shown'}:
            raise ValueError('Unknown agenda shape')
        required = {'id', 'question', 'source', 'outside', 'parent', 'status', 'first_work',
                    'work', 'attempts', 'first_answer', 'answer', 'not_yet'}
        for key, item in self.items.items():
            if not required <= set(item) or set(item)-required-{'answered_work'} or item['id'] != key:
                raise ValueError('Unknown question shape')
            if type(item['question']) not in (TaskView, str) or item['status'] not in ('open', 'answered'):
                raise ValueError('Nonpublic question state')
        if len(set(self.order)) != len(self.order) or set(self.order) != set(self.items):
            raise ValueError('Invalid agenda order')
