import copy

import pytest
import torch

from sera_field.gauge import adjoint_rotations
from sera_field.history_owner import extend_history, history_identity
from sera_field.model import weight_hash
from sera_field.perfect_tensor_memory import pauli_word
from sera_field.semantic_owner import SemanticOwner


def parent():
    torch.manual_seed(1604)
    return SemanticOwner(width=8, nodes=4)


def propose(owner):
    transport = adjoint_rotations(owner.field.links).transpose(-1, -2)
    return owner.field.continuum.advance(owner.field.continuum.empty(1),
        torch.randn(1, 4, 3) * .2, torch.tensor([.2]), transport)[0]


def event(proposal, predictor):
    return {'accepted': True, 'outcome': {'verified': True, 'goal': 'g', 'decision': 'd',
        'predictor': predictor, 'policy_before': predictor, 'evidence_id': 'e',
        'assessment_id': 'a', 'source_sha256': 'human-source', 'verifier_sha256': 'test-verifier',
        'assumptions_id': 'test-scope', 'evidence_kind': 'human_assessment',
        'intended_intervention': history_identity(proposal), 'observed_intervention': history_identity(proposal),
        'before_loss': .5, 'after_loss': .4}}


def test_exact_initial_parent_and_connected_conditional_memory():
    original = parent(); owner = extend_history(original)
    texts = (['A reader holds a book.'], ['A person is reading.'])
    with torch.no_grad():
        expected = original.semantic(*texts)
        assert torch.equal(owner.semantic(*texts), expected)
        for name, p in original.named_parameters():
            assert torch.equal(p, dict(owner.named_parameters())[name])
        owner.field.raw_history_gain.fill_(.4)
        owner.field.history_preview = propose(owner)
        actual = owner.semantic(*texts)
        assert not torch.equal(actual, expected)
        assert int(owner.field.history_events) == 0 and not owner.field.history_code_ready
        owner.field.history_preview = None
        assert torch.equal(owner.semantic(*texts), expected)


def test_exact_proposal_credit_protected_storage_and_restart():
    owner = extend_history(parent()); proposal = propose(owner)
    owner.field.active_history_goal = 'g'
    predictor = weight_hash(owner); evidence = event(proposal, predictor); proposal_id = history_identity(proposal)
    bad = {k: v.clone() if isinstance(v, torch.Tensor) else v for k, v in proposal.items()}
    bad['slow'][0, 0, 0] += .1
    with pytest.raises(ValueError, match='changed after'):
        owner.field.commit_history(bad, evidence, predictor=predictor, decision_policy=predictor, proposal_id=proposal_id)
    assert not owner.field.history_code_ready
    owner.field.commit_history(proposal, evidence, predictor=predictor, decision_policy=predictor, proposal_id=proposal_id)
    clean = owner.field.factual_state()
    corrupted = owner.field.history_code @ pauli_word('IIYII').T
    recovered = owner.field.factual_state(code=corrupted)
    for name in ('fast', 'slow', 'marks', 'bulk', 'flow_context'):
        assert torch.allclose(clean[name], recovered[name], atol=1e-6)
    restored = extend_history(parent()); restored.load_state_dict(copy.deepcopy(owner.state_dict()))
    assert weight_hash(restored) == weight_hash(owner)
    assert history_identity(restored.field.factual_state()) == history_identity(clean)
    with pytest.raises(ValueError, match='already been consumed'):
        owner.field.commit_history(proposal, evidence, predictor=predictor, decision_policy=predictor, proposal_id=proposal_id)
    with torch.no_grad():
        owner.field.continuum.raw_fast.add_(.1)
    with pytest.raises(ValueError, match='different flow'):
        owner.field.factual_state()


def test_retained_history_is_goal_scoped_and_rejects_stale_owner():
    owner = extend_history(parent()); proposal = propose(owner)
    texts = (['A reader holds a book.'], ['A person is reading.'])
    owner.field.raw_history_gain.data.fill_(.4)
    expected = owner.semantic(*texts).detach()
    predictor = weight_hash(owner); evidence = event(proposal, predictor)
    with pytest.raises(ValueError, match='original goal'):
        owner.retain_history(proposal, evidence, proposal_id=history_identity(proposal))
    owner.field.active_history_goal = 'g'
    owner.retain_history(proposal, evidence, proposal_id=history_identity(proposal))
    assert not torch.equal(owner.semantic(*texts).detach(), expected)
    owner.field.active_history_goal = 'different-goal'
    assert torch.equal(owner.semantic(*texts).detach(), expected)
    with pytest.raises(ValueError, match='Stale predictor'):
        owner.retain_history(proposal, evidence, proposal_id=history_identity(proposal))


def test_boundary_annotation_signal_teaches_actual_history_path():
    owner = extend_history(parent())
    owner.field.track_boundary_credit = True
    logits = owner.semantic(['A reader holds a book.'], ['A person holds something.'])
    loss = -logits.softmax(-1).mean(1)[0, 0].log()
    derivative, = torch.autograd.grad(loss, owner.field.last_boundary)
    signal = -derivative.detach().mean(0, keepdim=True)
    signal = signal / (.1 + signal.square().sum((-2, -1), keepdim=True).sqrt())
    state = owner.field.continuum.empty(1)
    transport = adjoint_rotations(owner.field.links).transpose(-1, -2)
    proposed, diagnostics = owner.field.continuum.advance(state, signal, torch.zeros(1), transport)
    owner.field.history_preview = proposed
    assessed = owner.semantic(['A person carries a bag.'], ['Someone carries an object.'])
    query_loss = -assessed.softmax(-1).mean(1)[0, 0].log() + .0001 * diagnostics['reverse_kl'].mean()
    query_loss.backward()
    assert owner.field.raw_history_gain.grad.abs() > 0
    assert not owner.field.history_code_ready


def test_query_label_never_enters_history_and_episode_teaches_only_new_parameters():
    from sera_field.history_training import episode
    owner = extend_history(parent())
    record = {'id': 'episode', 'query': {'id': 'q', 'source_group': 'qg', 'target': 0,
        'premise': 'A person carries a bag.', 'hypothesis': 'Someone carries an object.'},
        'supports': [{'id': str(i), 'source_group': str(i), 'target': i % 3,
            'premise': 'A reader holds a book.', 'hypothesis': 'The reader is seated.'} for i in range(4)]}
    protected = {n: p.detach().clone() for n, p in owner.named_parameters() if not p.requires_grad}
    loss, result, state = episode(owner, record)
    changed = copy.deepcopy(record); changed['query']['target'] = 2
    _, _, other_state = episode(owner, changed)
    assert history_identity(state) == history_identity(other_state)
    assert result['original_goal_returned'] and len(result['supports']) == 4
    optimizer = torch.optim.AdamW([p for p in owner.parameters() if p.requires_grad], lr=.001)
    initial = weight_hash(owner); optimizer.zero_grad(); loss.backward(); optimizer.step()
    assert weight_hash(owner) != initial
    assert all(torch.equal(value, dict(owner.named_parameters())[name]) for name, value in protected.items())
    assert not owner.field.history_code_ready and owner.field.history_preview is None
