"""Unit fixtures below are not corpus teaching or behavioral research evidence."""
import copy
import hashlib
import json

import torch

from sera_field.genre_owner import extend_genre
from sera_field.genre_training import GenreEngine, assess
from sera_field.model import weight_hash
from sera_field.records import write_json
from sera_field.semantic_owner import SemanticOwner
from sera_field.semantic_training import HumanBank


def data(tmp_path):
    records = [{'id': hashlib.sha256(str(i).encode()).hexdigest(), 'source_group': 'fixture:' + str(i),
        'premise': 'A reader holds a book.', 'hypothesis': 'A person holds an object.',
        'target': i % 3, 'genre': 'unit-fixture'} for i in range(65)]
    path = tmp_path / 'unit-only.jsonl'
    path.write_text(''.join(json.dumps(r) + '\n' for r in records), encoding='utf-8')
    return records, HumanBank(path)


def owner(noise=.03):
    torch.manual_seed(17105)
    return extend_genre(SemanticOwner(width=8, nodes=3, rounds=1, steps=4), teaching_noise=noise)


def test_stochastic_teaching_resumes_exactly_and_source_cursor_is_retained(tmp_path):
    rows, bank = data(tmp_path)
    first = GenreEngine(owner(), bank, {'pairs': {}}, bank, rows[:3], 'unit-source')
    first.history = [{'semantic_step': 0, 'accuracy': 0., 'loss': 2.}]
    first.update()
    root = tmp_path / 'checkpoint'
    pointer = first.snapshot(root)
    first.best = {**pointer, **first.history[-1]}
    write_json(root / 'SELECTION.json', first.best)
    expected_record = first.update(); expected_weights = weight_hash(first.owner)
    resumed = GenreEngine(owner(), bank, {'pairs': {}}, bank, rows[:3], 'unit-source')
    resumed.resume(root); actual_record = resumed.update()
    assert actual_record == expected_record
    assert weight_hash(resumed.owner) == expected_weights
    assert resumed.cursor == first.cursor == 64
    assert resumed.order == first.order


def test_development_and_action_ablation_are_deterministic_and_read_only(tmp_path):
    rows, _ = data(tmp_path); model = owner()
    with torch.no_grad(): model.field.ensemble_action.raw_gain.fill_(.4)
    model.train(); before = copy.deepcopy(model.state_dict()); original_hash = weight_hash(model)
    one = assess(model, rows[:4]); two = assess(model, rows[:4])
    assert one == two
    assert model.training and model.field.training
    original_mode = model.field.action_mode
    disabled = assess(model, rows[:4], ablation='no_action')
    assert model.field.action_mode == original_mode
    assert weight_hash(model) == original_hash
    assert all(torch.equal(v, model.state_dict()[k]) for k, v in before.items() if isinstance(v, torch.Tensor))
    assert one[1] != disabled[1]


def test_matched_arms_have_identical_starting_parameters(tmp_path):
    rows, bank = data(tmp_path)
    exact = owner(); clean = owner(0.)
    assert weight_hash(exact) == weight_hash(clean)
    a = GenreEngine(exact, bank, {'pairs': {}}, bank, rows[:3], 'same-source')
    b = GenreEngine(clean, bank, {'pairs': {}}, bank, rows[:3], 'same-source')
    assert a.order == b.order
    assert not any(p.requires_grad for n, p in a.owner.named_parameters()
                   if not n.startswith(('semantic_', 'field.ensemble_action.')))
