"""Actual-owner label isolation and assessment purity; run under supervision."""
from copy import deepcopy
import torch

from scripts.assess_core022_choices import assess_owner
from scripts.core022_assessment_views import choice_views, identity, role
from sera_field.core_owner import CoreOwner
from sera_field.native_owner import NativeConfig
from sera_field.model import weight_hash


def test_assessment_queries_actual_owner_without_target_or_weight_changes(monkeypatch):
    # The test suite's outer runner supplies the CPU/memory restriction. This
    # marker permits a unit call in that same process; it launches no subprocess.
    monkeypatch.setenv('SERA_FIELD_SUPERVISED', 'core-choice-fixture')
    torch.set_num_threads(1)
    torch.manual_seed(22403)
    groups = [str(i) for i in range(200) if role(str(i)) == 'development'][:2]
    rows = [{'id': 'fixture-' + str(i), 'group': group, 'track': 'fixture',
             'question': question, 'answer': answer}
            for i, (group, question, answer) in enumerate(zip(groups,
                ['Where was the flower seen?', 'Where was the book read?'],
                ['In the garden.', 'In the library.']))]
    views = choice_views(rows, partition='development')
    owner = CoreOwner(NativeConfig(nodes=4, rounds=2), program_slots=8)
    owner.train()
    before = weight_hash(owner)
    result = assess_owner(owner, views)
    assert result['scored_cases'] == 2
    assert result['optimizer_updates'] == 0 and result['model_initializations'] == 0
    assert all(len(case['probabilities']) == 2 for case in result['cases'])
    assert weight_hash(owner) == before and owner.training
    assert all(parameter.grad is None for parameter in owner.parameters())

    # Change only assessor-side labels, preserving exactly the public inputs.
    # Identical predictions verify that target indices never enter the owner.
    altered = deepcopy(views)
    for view in altered:
        view['target'] = 1 - view['target']
        view['identity'] = identity({k: v for k, v in view.items() if k != 'identity'})
    other = assess_owner(owner, altered)
    assert [c['probabilities'] for c in other['cases']] == [c['probabilities'] for c in result['cases']]
    assert [c['correct'] for c in other['cases']] == [not c['correct'] for c in result['cases']]
    assert weight_hash(owner) == before and owner.training

    single = choice_views([rows[0]], partition='development')
    unscored = assess_owner(owner, single)
    assert unscored['accuracy'] is None and unscored['mean_chance'] is None
    assert unscored['scored_cases'] == 0 and unscored['unscored_cases'] == 1
