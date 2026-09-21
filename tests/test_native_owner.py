"""Native memory must participate before any prior checkpoint or lesson exists."""
import copy
import io

import pytest
import torch

from sera_field.model import weight_hash
from sera_field.native_owner import NativeOwner, detached_state, split_text
from sera_field.native_data import physical_episode, independent_outcome


def owner():
    torch.manual_seed(19119)
    return NativeOwner()


def test_first_lesson_reaches_input_geometry_memory_and_answer_weights():
    model = owner()
    logits = model.semantic(['A child is carrying a red flower.', 'Two people walk through the garden.'],
                            ['Someone holds a flower.', 'Nobody is outdoors.'])
    loss = torch.nn.functional.cross_entropy(logits.mean(1), torch.tensor([0, 1]))
    loss.backward()
    for prefix in ('words.', 'local.', 'text_source.', 'field.links', 'observation_write.',
                   'memory.flow.', 'memory.raw_fast', 'memory.raw_slow',
                   'memory.raw_activity', 'memory.raw_readout', 'meaning.'):
        values = [p.grad for n, p in model.named_parameters() if n.startswith(prefix) and p.grad is not None]
        assert values and sum(float(v.abs().sum()) for v in values) > 1e-14, prefix
        assert all(bool(torch.isfinite(v).all()) for v in values)


def test_shared_numeric_and_text_routes_reach_same_geometry_and_memory():
    model = owner()
    episodes = [physical_episode('native-unit-test', i) for i in range(2)]
    supports = torch.tensor([r['support'] for r in episodes])
    queries = torch.tensor([r['queries'] for r in episodes])
    predicted = model.physical(supports, queries)
    predicted.square().mean().backward()
    assert model.field.links.grad.abs().sum() > 0
    assert model.memory.raw_fast.grad.abs() > 0
    assert model.number_source[0].weight.grad.abs().sum() > 0
    assert predicted.shape == (2, 3, 3)


def test_conditional_branches_do_not_change_observed_state_or_owner():
    model = owner().eval()
    state, _ = model.remember_texts(['A flower is beside the window.'])
    before = detached_state(state); weights = weight_hash(model)
    source = model.encode_texts(['The flower is outside.'])
    result = model.imagine(state, source)
    model.imagine(state, source * -1)
    assert torch.equal(result, model.imagine(state, source))
    for key, value in before.items():
        assert torch.equal(state[key], value) if isinstance(value, torch.Tensor) else state[key] == value
    assert weight_hash(model) == weights


def test_history_is_the_only_observation_route_and_has_an_initial_effect():
    model = owner().eval()
    premises = ['A boy carries flowers.', 'An empty machine sits outside.']
    hypotheses = ['Something is being carried.'] * 2
    empty = model.semantic(premises, hypotheses, memory=False)
    # Compare changed discarded observations at fixed batch positions exactly.
    # Identical rows at different GEMM positions can differ by float32 roundoff.
    changed = model.semantic(list(reversed(premises)), hypotheses, memory=False)
    explicit = model.meaning(model.imagine(model.empty(2), model.encode_texts(hypotheses)))
    assert torch.equal(empty, changed) and torch.equal(empty, explicit)
    torch.testing.assert_close(empty[0], empty[1], rtol=0., atol=torch.finfo(empty.dtype).eps)
    retained = model.semantic(premises, hypotheses)
    assert not torch.equal(retained[0], retained[1])
    assert not torch.equal(retained, empty)


def test_simple_trace_control_retains_observations_before_richer_memory():
    model = owner().eval()
    premises = ['A boy carries flowers.', 'An empty machine sits outside.']
    hypotheses = ['Something is being carried.'] * 2
    trace = model.semantic(premises, hypotheses, ablation='simple_trace')
    assert not torch.equal(trace[0], trace[1])
    state, _ = model.remember_texts(premises, simple_trace=True)
    assert state['fast'].abs().sum() > 0
    assert not state['slow'].count_nonzero() and not state['bulk'].count_nonzero()
    from sera_field.native_training import training_ablation, selected_ablation
    assert training_ablation('delayed', 4095) == 'simple_trace'
    assert training_ablation('delayed', 4096) is None
    assert selected_ablation('delayed', 4096) == 'simple_trace'
    assert selected_ablation('delayed', 5120) is None


def test_atomic_roundtrip_preserves_next_joint_update_exactly():
    original = owner()
    optimizer = torch.optim.AdamW(original.parameters(), lr=.001)
    args = (['The river runs through the city.'], ['There is water in the city.'])
    def update(m, o):
        o.zero_grad(); loss = m.semantic(*args).square().mean(); loss.backward(); o.step()
        return loss.detach()
    update(original, optimizer)
    buffer = io.BytesIO()
    torch.save({'owner': original.state_dict(), 'optimizer': optimizer.state_dict()}, buffer); buffer.seek(0)
    saved = torch.load(buffer, weights_only=True)
    restored = owner(); restored.load_state_dict(saved['owner'])
    second = torch.optim.AdamW(restored.parameters(), lr=.001); second.load_state_dict(saved['optimizer'])
    assert torch.equal(update(original, optimizer), update(restored, second))
    assert weight_hash(original) == weight_hash(restored)


def test_memory_rate_gradient_matches_central_difference():
    model = owner().double()
    # A direct vector source avoids the intentionally float32 text input indices.
    source = torch.linspace(-.2, .3, 48, dtype=torch.float64).reshape(2, 8, 3)
    def f():
        first, _ = model.observe(model.empty(2), source)
        second, _ = model.observe(first, source * .7)
        return model.imagine(second, source * -.3).square().mean()
    value = f(); derivative, = torch.autograd.grad(value, model.memory.raw_slow)
    old = float(model.memory.raw_slow.detach()); h = 1e-4
    with torch.no_grad():
        model.memory.raw_slow.fill_(old + h); plus = f()
        model.memory.raw_slow.fill_(old - h); minus = f()
        model.memory.raw_slow.fill_(old)
    assert torch.allclose(derivative, (plus-minus)/(2*h), atol=1e-8, rtol=2e-3)


def test_source_slices_are_exhaustive_and_absent_input_is_not_a_measurement():
    for text in ('A flower.', '', 'word', '  Words\n and punctuation!  '):
        assert ''.join(split_text(text)) == text
    model = owner()
    state = model.empty(1); after, _ = model.remember_texts(['   '], state)
    for key in state:
        assert torch.equal(state[key], after[key]) if isinstance(state[key], torch.Tensor) else state[key] == after[key]
    mixed, _ = model.remember_texts(['  ', 'A flower.', 'word'])
    assert mixed['events'].tolist() == [0, 2, 1]
    empty = model.empty(1)
    for key, value in mixed.items():
        assert torch.equal(value[:1], empty[key])


def test_independent_simulator_check_and_teacher_separation():
    for i in range(12):
        episode = physical_episode('native-unit-independent', i)
        for (force, velocity), target in zip(episode['queries'], episode['targets']):
            assert abs(independent_outcome(episode['teacher_only'], force, velocity)-target) < 1e-12
    with pytest.raises(ValueError, match='no answer'):
        owner().physical_query(owner().empty(1), torch.zeros(1, 3, 3))
