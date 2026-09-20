import torch

from sera_field.inquiry_owner import InquiryOwner
from sera_field.semantic_owner import curvature_tags, rotation, extend_semantic


def test_true_holonomy_tag_is_locally_covariant_and_zero_on_flat_zero_input():
    torch.manual_seed(1501)
    source = torch.randn(2, 5, 3, dtype=torch.float64) * .3
    links = rotation(torch.randn(5, 3, dtype=torch.float64) * .2)
    frames = rotation(torch.randn(5, 3, dtype=torch.float64))
    tag, loops = curvature_tags(source, links, .2)
    transformed_source = torch.einsum('nij,bnj->bni', frames, source)
    transformed_links = frames.roll(-1, 0) @ links @ frames.transpose(-1, -2)
    actual, changed_loops = curvature_tags(transformed_source, transformed_links, .2)
    assert torch.allclose(actual, torch.einsum('nij,bnj->bni', frames, tag), atol=1e-12)
    assert torch.allclose(changed_loops, frames[None] @ loops @ frames.transpose(-1, -2)[None], atol=1e-12)
    flat, _ = curvature_tags(source * 0, torch.eye(3, dtype=torch.float64).repeat(5, 1, 1), .2)
    assert torch.equal(flat, torch.zeros_like(flat))


def test_curvature_derivatives_and_semantics_use_the_existing_field():
    torch.manual_seed(1502)
    source = (torch.randn(1, 3, 3, dtype=torch.float64) * .1).requires_grad_()
    links = rotation(torch.randn(3, 3, dtype=torch.float64) * .1)
    assert torch.autograd.gradcheck(lambda x: curvature_tags(x, links, .2)[0], (source,))
    parent = InquiryOwner(width=8, nodes=4)
    owner = extend_semantic(parent)
    for name, parameter in parent.named_parameters():
        assert torch.equal(parameter, dict(owner.named_parameters())[name])
    logits = owner.semantic(['A person holds a book.'], ['Someone holds an object.'])
    assert logits.shape == (1, 3, 3) and torch.isfinite(logits).all()
    loss = -logits.log_softmax(-1)[..., 0].mean()
    loss.backward()
    assert owner.semantic_observed.weight.grad.abs().sum() > 0
    assert owner.semantic_proposed.weight.grad.abs().sum() > 0
    assert owner.field.links.grad.abs().sum() > 0
    assert owner.field.last_curvature.shape == (3, 4, 3)


def test_conditional_curvature_capture_changes_semantics_without_writing_memory():
    torch.manual_seed(1503)
    owner = extend_semantic(InquiryOwner(width=8, nodes=4))
    texts = (['A person holds a book.'], ['Someone holds an object.'])
    with torch.no_grad():
        before = owner.semantic(*texts)
        tag = owner.field.last_curvature[0]
        preview = owner.field.curvature_memory.propose(tag)
        owner.field.curvature_preview = preview
        after = owner.semantic(*texts)
        owner.field.curvature_preview = None
    assert (before - after).abs().max() > 0
    assert not owner.field.curvature_memory.active.any()
    assert int(owner.field.curvature_memory.cursor) == 0


def test_real_semantic_update_capture_and_resume_are_exact(tmp_path):
    from sera_field.semantic_training import SemanticEngine
    from sera_field.model import weight_hash
    from sera_field.records import write_json

    class Bank:
        offsets = list(range(100))
        reserved = list(range(12))

        def get(self, indices):
            return [{'id': f'{i:064x}', 'source_group': str(i),
                'premise': 'A person holds a book.',
                'hypothesis': ('Someone holds an object.', 'Nobody holds anything.', 'The book is red.')[i % 3],
                'target': i % 3} for i in indices]

    torch.manual_seed(1504)
    owner = extend_semantic(InquiryOwner(width=8, nodes=4))
    engine = SemanticEngine(owner, Bank(), {}, [], 'test-human-annotation-source')
    initial = weight_hash(owner)
    engine.update()
    assert weight_hash(owner) != initial
    saved = engine.snapshot(tmp_path)
    write_json(tmp_path / 'SELECTION.json', {**saved, 'accuracy': 0., 'loss': 2.})
    engine.update(); expected_event = engine.capture_practice()
    expected = weight_hash(owner)
    restored_owner = extend_semantic(InquiryOwner(width=8, nodes=4))
    restored = SemanticEngine(restored_owner, Bank(), {}, [], 'test-human-annotation-source')
    restored.resume(tmp_path); restored.update(); actual_event = restored.capture_practice()
    assert weight_hash(restored_owner) == expected
    assert actual_event == expected_event
    assert restored.cursor == engine.cursor and restored.exposures == engine.exposures


def test_rehearsal_preserves_different_views_with_repeated_source_ids(tmp_path):
    import json
    from sera_field.semantic_training import legacy_data
    for kind in ('reading', 'math', 'pairs'):
        rows = [{'id': 'same-source', 'track': 'test', 'view': i} for i in range(3)]
        (tmp_path / f'train-{kind}.jsonl').write_text(
            ''.join(json.dumps(r) + '\n' for r in rows), encoding='utf-8')
    result = legacy_data(tmp_path)
    for rows in (result['reading'], result['math'], result['pairs']['test']):
        assert sorted(r['view'] for r in rows) == [0, 1, 2]
    assert result == legacy_data(tmp_path)
