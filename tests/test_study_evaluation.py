"""Independent engineering fixtures; never use production sealed source rows."""
from fractions import Fraction
import json

import numpy as np
import pytest
import torch

from sera_field.learned_motion import rollout
from sera_field.records import write_json
from sera_field.study_registration import freeze_identity, registered_candidate
from sera_field.study_evaluation import (cohort, completed_stage, expression_proposals,
                                         reading_evaluation, math_evaluation)
from sera_field.study_world import Environment, trajectory


def test_learned_trajectory_matches_closed_form_and_independent_damping():
    constant = np.array([[1., 0., 0., 0.]] * 3)
    result = rollout(constant, velocity=2., force_per_mass=3., duration=1.5)
    np.testing.assert_allclose(result['position_velocity_mean'], [6.375, 6.5], atol=1e-12)
    drag = np.array([[.8, -.4, -.12, .1]] * 3)
    learned = rollout(drag, -1., 1.3, 1.)
    checked = trajectory(Environment(.8, .4, .12, .1), velocity=-1., force_per_mass=1.3, duration=1.)
    np.testing.assert_allclose(learned['position_velocity_mean'], checked, atol=1e-6)
    with pytest.raises(ValueError):
        rollout(constant, float('nan'), 1., 1.)


def test_divergent_imagination_is_retained_as_a_failure():
    with np.errstate(over='ignore', invalid='ignore'):
        result = rollout(np.array([[0., 0., 100., 0.]] * 3), 3., 0., 1.)
    assert result['status'] == 'diverged'
    assert 'position_velocity_mean' not in result


class ArithmeticFixture:
    def math_logits(self, questions, inventories):
        logits = torch.full((1, 4, 3, 3), -10.)
        logits[0, 0, 0, 1] = 5.
        logits[0, 0, 1, 0] = 4.
        logits[0, 1, 0, 1] = 3.
        return logits


def test_proposals_deduplicate_aliases_but_keep_distinct_operations():
    results = expression_proposals(ArithmeticFixture(), 'a fixture', ['5', '3', '1'])
    assert len(results) == len({json.dumps(r['program']) for r in results}) == 5
    assert Fraction(results[0]['result']) == 8
    assert Fraction(results[1]['result']) == 2
    rows = [{'id': 'fixture', 'source': 'a'*64, 'question': 'a fixture', 'values': ['5','3','1'],
             'target': [0, 0, 1], 'answer': '8', 'teacher_forced_steps': 0, 'original_one_step': True}]
    summary, raw = math_evaluation(ArithmeticFixture(), rows)
    assert summary['original_one_step']['human_expression_top1'] == 1.
    assert raw[0]['numeric_matches'][0]


def test_final_component_resume_reuses_verified_bytes_and_preserves_partial_attempt(tmp_path):
    calls = []
    def produce():
        calls.append(1)
        return {'n': 1}, [{'evidence': 'fixture'}]
    (tmp_path/'item.jsonl').write_text('interrupted fixture\n')
    assert completed_stage(tmp_path, 'item', produce) == {'n': 1}
    assert completed_stage(tmp_path, 'item', produce) == {'n': 1}
    assert calls == [1]
    assert len(list((tmp_path/'incomplete').glob('*/item.jsonl'))) == 1
    (tmp_path/'item.jsonl').write_text('altered evidence')
    with pytest.raises(ValueError, match='records changed'):
        completed_stage(tmp_path, 'item', produce)


def test_registration_detects_checkpoint_and_transitive_source_changes(tmp_path):
    training, rewards, data = [tmp_path/p for p in ('training','rewards','data')]
    write_json(training/'SELECTION.json', {'weights': 'fixture'})
    for arm in ('verified_reward', 'reward_disconnected'):
        write_json(rewards/arm/'revisions/CURRENT.json', {'weights': 'fixture'})
    write_json(data/'MANIFEST.json', {'fixture': True})
    write_json(data/'SPLIT_AUDIT.json', {'fixture': True})
    identity = freeze_identity(training, rewards, data)
    assert 'study_training' in identity['runtime_sources']
    registry = tmp_path/'registry.json'
    write_json(registry, {'candidates': {'fixture': identity}})
    assert registered_candidate(training, rewards, data, registry) == identity
    write_json(training/'SELECTION.json', {'weights': 'changed'})
    with pytest.raises(ValueError, match='registration'):
        registered_candidate(training, rewards, data, registry)


def test_group_cohort_ignores_input_order_and_keeps_groups_contiguous():
    rows = [{'id': str(i), 'group': str(i//3)} for i in range(24)]
    selected = cohort(rows, 10, 'fixture')
    assert selected == cohort(list(reversed(rows)), 10, 'fixture')
    assert len({r['group'] for r in selected}) == 4
