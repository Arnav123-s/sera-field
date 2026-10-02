"""Independent held-out source-choice construction; no model or corpus import.

An assessor supplies an explicitly opened cohort. Distractors stay in that same
partition and subject. A missing alternative becomes an unscored case, never a
one-choice success. The task is attributed source-answer selection, not a claim
that every other human sentence is semantically false.
"""
import hashlib
import json
import random
import unicodedata

from scripts.audit_core022_course import SPLIT_KEY, rank


def role(group):
    bucket = int(rank(SPLIT_KEY, group)[:8], 16) % 20
    return 'final' if bucket == 0 else 'development' if bucket == 1 else 'train'


def normalized(value):
    return ' '.join(unicodedata.normalize('NFC', value).split())


def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def choice_views(rows, *, partition):
    if partition not in ('development', 'final'):
        raise ValueError('An explicitly identified assessment partition is required')
    seen = set()
    for row in rows:
        for key in ('id', 'group', 'track', 'question', 'answer'):
            if not isinstance(row.get(key), str) or not row[key].strip():
                raise ValueError('Complete attributed source-pair record required')
        if row['id'] in seen or role(row['group']) != partition:
            raise ValueError('Duplicate identity or source outside the assessment partition')
        seen.add(row['id'])
    result = []
    for row in rows:
        answer = normalized(row['answer'])
        available = [candidate for candidate in rows if candidate['track'] == row['track']
                     and candidate['group'] != row['group'] and normalized(candidate['answer']) != answer]
        available.sort(key=lambda candidate: rank('CORE-022-assessment-options|' + row['id'], candidate['id']))
        selected = [row]
        answers = {answer}
        for candidate in available:
            key = normalized(candidate['answer'])
            if key not in answers:
                selected.append(candidate)
                answers.add(key)
            if len(selected) == 4:
                break
        order = list(range(len(selected)))
        random.Random(int(rank('CORE-022-assessment-position|', row['id']), 16)).shuffle(order)
        choice = {'id': row['id'], 'group': row['group'], 'track': row['track'],
                  'partition': partition, 'context': row['question'],
                  'options': [selected[i]['answer'] for i in order], 'target': order.index(0),
                  'option_sources': [{'id': selected[i]['id'], 'group': selected[i]['group']} for i in order],
                  'scored': len(selected) >= 2,
                  'unscored_reason': None if len(selected) >= 2 else 'no distinct other-group answer in this subject and partition',
                  'scope': 'selection of the supplied human source answer among attributed alternatives'}
        choice['identity'] = identity(choice)
        result.append(choice)
    return result


def score_choices(views, predictions):
    if len(predictions) != len(views):
        raise ValueError('One assessment prediction per source view required')
    result = []
    for view, prediction in zip(views, predictions):
        if identity({k: v for k, v in view.items() if k != 'identity'}) != view['identity']:
            raise ValueError('Assessment view changed after commitment')
        if view['scored']:
            if type(prediction) is not int or not 0 <= prediction < len(view['options']):
                raise ValueError('Invalid candidate index; missing answers are not silently dropped')
            correct = prediction == view['target']
        else:
            if prediction is not None:
                raise ValueError('Unscored single-choice cases require an explicit absent prediction')
            correct = None
        result.append({'view': view['identity'], 'id': view['id'], 'group': view['group'],
                       'track': view['track'], 'scored': view['scored'],
                       'options': len(view['options']), 'prediction': prediction,
                       'target': view['target'], 'correct': correct,
                       'chance': 1 / len(view['options']) if view['scored'] else None,
                       'unscored_reason': view['unscored_reason']})
    return result
