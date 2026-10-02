"""S25: cheap observer schema/switch checks and contrastive gate witnesses; no real rail judge."""
import json
import math

import pytest

from sera import lang as L, one as O, phi as P, tasks as T
from scripts import sera_ring_diagnostic as D


def _tiny_live(monkeypatch, tmp_path, enabled):
    monkeypatch.setattr(O, 'ONE_FIELD', enabled)
    monkeypatch.setattr(P, 'FIELD_ECHO', True)
    monkeypatch.setattr(O, 'MAX_WALL', math.inf)
    task = T.Exact('math', 'tiny ring', lambda n: n + 1, {'n': 'num'}, 'num',
                   [7, 7], [], lambda rng: 7)
    raw = L.node('add', L.node('var', payload='n'), L.node('one'))
    mind = O.Sera(1, P.Field(1))
    monkeypatch.setattr(mind, '_generate', lambda *a, **k: [raw])
    monkeypatch.setattr(mind, '_moves_available', lambda *a, **k: [])
    monkeypatch.setattr(mind, '_max_level', lambda task: 0)
    monkeypatch.setattr(mind.field.loop, 'choose', lambda kind, moment, est, available, rng:
                        (['prove'] if 'prove' in available else ['leave'],
                         {f: (1., 0.) for f in available}))
    key = mind._idea_key(task, raw)
    mind._ideas().bind(7, key, 1.)
    # The rail-independent cue has a sentence frequency and thus presses the existing decoder.
    mind._ideas().of.setdefault(7, {}).update(seen=1, sentences=1)
    mind._ideas().read_n = 2
    path = tmp_path / 'ring.jsonl'
    rec = mind.live(task, max_steps=2, ring_log=path)
    return mind, rec, path


def test_world_observer_schema_and_event_credit_join(monkeypatch, tmp_path):
    mind, rec, path = _tiny_live(monkeypatch, tmp_path, True)
    rows = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]
    assert len(rows) == 1 and rows[0] == rec['ring_observer']
    log = rows[0]
    assert log['schema_version'] == 1 and log['initial_context'] and log['initial_cues'] == [7]
    assert log['trigger_complete'] and log['projection_complete']
    assert rec['proven'] and rec['verdict'] == 'proven right'
    assert len(log['candidates']) == len(log['selected']) == 1
    candidate, thought = log['candidates'][0], log['selected'][0]
    assert candidate['identity'][0] == 'idea' and candidate['identity_repr']
    assert candidate['score'] > candidate['threshold'] > candidate['noise'] >= 0
    assert thought['used'] and thought['led'] and thought['accepted'] and thought['proof_attempts'] == 1
    assert thought['refutations'] == []
    assert thought['terminal_amount'] == 1 and thought['written']
    assert [e['event'] for e in log['events']] == ['attempted', 'judge_result']
    obj = log['credited_object']
    assert obj['credited'] and obj['certified'] == []  # exact proof, not a physics certificate
    assert len(log['writes']) == 1 and log['writes'][0]['amount'] == 1
    assert thought['content_identity'] == log['writes'][0]['content_identity']
    assert thought['identity'] != thought['terminal_identity']  # invention renamed the original expression
    assert {'phases', 'wall', 'cpu', 'thinking_cpu', 'finish_cpu'} <= log['costs'].keys()
    assert 'ring_observer' not in vars(mind.field)
    assert all('ring_observer' not in r for r in mind.field.log)


def test_no_observer_file_or_payload_when_one_field_is_off(monkeypatch, tmp_path):
    mind, rec, path = _tiny_live(monkeypatch, tmp_path, False)
    assert rec['proven'] and not path.exists() and 'ring_observer' not in rec
    assert mind._ring_observer is None


def test_projection_observation_keeps_below_noise_scores_and_selection_unchanged():
    ideas = P.Ideas()
    cue = ('sense', 'strengths', 0, 0.)
    keys = [('idea', (('position', 'curve', k),)) for k in (9, 17)]
    for key in keys:
        ideas._at(key)
    ideas.bind(cue, keys[0], 1.)
    ideas.bind(cue, keys[1], -1.)
    ideas.perceive_world([cue])
    before = ideas.evoked([cue], keys, deadline=math.inf)
    seen = []
    after = ideas.evoked([cue], keys, deadline=math.inf,
                         observe=lambda scores, noise, threshold: seen.append((scores, noise, threshold)))
    assert after == before and len(seen) == 1
    scores, noise, threshold = seen[0]
    assert [k for k, _ in scores] == keys and threshold > noise >= 0
    assert any(v <= threshold for _, v in scores)


def test_content_identity_joins_independent_ids_without_merging_formula_and_curve():
    expr = L.node('var', payload='_')
    a = O.Sera._ring_content(('idea', (('position', 'concept', 1),)), {1: expr})
    b = O.Sera._ring_content(('idea', (('position', 'concept', 99),)), {99: expr})
    raw = O.Sera._ring_content(('idea', (('position', 'expr', L.node('var', payload='s')),)), {})
    curve = O.Sera._ring_content(('idea', (('position', 'curve', 9),)), {})
    assert a == b == raw and a != curve


GOOD = ('idea', (('nothing', 'expr', ('var', 's')),))
BAD = ('idea', (('time', 'expr', ('var', 's')),))
UNSURE = ('idea', (('position', 'curve', 33),))


def _row(name, good=True, bad=False):
    events = []
    chosen = []
    if good:
        chosen.append(dict(identity=GOOD, led=True, used=True))
        events += [dict(event='attempted', identity=GOOD),
                   dict(event='judge_result', identity=GOOD, accepted=True)]
    if bad:
        chosen.append(dict(identity=BAD, led=True, used=True))
        events += [dict(event='attempted', identity=BAD),
                   dict(event='refuted', identity=BAD, reason='misfit')]
    events.append(dict(event='judge_result', identity=UNSURE, accepted=False,
                       reason='band too wide', band=2., eps=1.))
    return dict(id=name, status='done', input_sha256='identical full input',
                unit=dict(verdict='proven right'), ring=dict(selected=chosen, events=events,
                writes=[dict(identity=BAD, amount=-.25)] if bad else [],
                credited_object=dict(credited=good, amounts=[dict(identity=GOOD, amount=1)] if good else [])))


def _evidence():
    rows = {name: _row(name, bad=name in ('teach', 'before'))
            for name in ('teach', 'before', 'after', 'old-before', 'old-after')}
    return rows, [('before', 'after', ['teach'])], [('old-before', 'old-after')]


def test_gate_pass_requires_all_four_witnesses():
    rows, pairs, old = _evidence()
    result = D.evaluate(rows, pairs, old, True)
    assert result['verdict'] == 'PASS'
    assert all(result['outcomes'][k] == 'PASS' for k in D.OUTCOMES)
    assert D.evaluate(rows, pairs, old, False)['verdict'] == 'INCOMPLETE'
    rows['before']['ring']['selected'] = []
    assert D.evaluate(rows, pairs, old, True)['verdict'] == 'INCOMPLETE'


@pytest.mark.parametrize('failure', ['lost_help', 'unchanged_harm', 'uncertainty_penalty', 'lost_old', 'wrong'])
def test_gate_fails_witnessed_violation(failure):
    rows, pairs, old = _evidence()
    if failure == 'lost_help':
        rows['after']['ring']['credited_object']['amounts'] = []
    elif failure == 'unchanged_harm':
        rows['after'] = _row('after', bad=True)
    elif failure == 'uncertainty_penalty':
        rows['after']['ring']['writes'].append(dict(identity=UNSURE, amount=-.25))
    elif failure == 'lost_old':
        rows['old-after']['unit']['verdict'] = 'not proven'
        rows['old-after']['status'] = 'capped'
    else:
        rows['after']['unit']['verdict'] = 'SURE AND WRONG'
    assert D.evaluate(rows, pairs, old, True)['verdict'] == 'FAIL'


def test_censoring_and_missing_uncertainty_never_pass():
    rows, pairs, old = _evidence()
    rows['after'] = dict(id='after', status='censored')
    assert D.evaluate(rows, pairs, old, True)['verdict'] == 'INCOMPLETE'
    rows, pairs, old = _evidence()
    for row in rows.values():
        row['ring']['events'] = [e for e in row['ring']['events'] if e.get('identity') != UNSURE]
    assert D.evaluate(rows, pairs, old, True)['verdict'] == 'INCOMPLETE'
    rows['extra'] = dict(id='extra', status='error')
    rows['after']['ring']['writes'].append(dict(identity=UNSURE, amount=-.25))
    assert D.evaluate(rows, pairs, old, True)['verdict'] == 'FAIL'


def test_development_seed_contract():
    for seed in (1, 2, 3):
        D.validate_spec(dict(seed=seed))
    with pytest.raises(ValueError, match='seeds 1-3'):
        D.validate_spec(dict(seed=4))
