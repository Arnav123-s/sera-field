"""US3b: prefix batching, the live single-read path, and scoped exact geometry."""
import copy
from dataclasses import replace
import math

import numpy as np
import pytest
import torch
from torch.func import functional_call

from sera import crutches as CR, lang as LG, phi as PH
from sera_u import SeraU
from sera_u.field.native_owner import NativeConfig
from sera_u.field.unified_energy import UnifiedEnergy
from sera_u.mind import arm_settings, global_rng
from sera_u.ports import PortBudget, TaskView
from sera_u.proposer import FieldOwner


@pytest.fixture(autouse=True)
def deterministic(monkeypatch):
    torch.set_num_threads(1)
    torch.manual_seed(3)
    monkeypatch.setattr(CR, 'ON', set())
    monkeypatch.setattr(CR, 'OFF', {'lesson_words'})
    monkeypatch.setattr(LG, 'DEADLINE', [math.inf])
    LG.forget_searches()
    yield
    LG.forget_searches()


def public():
    return TaskView((('x', 'num'),), 'num', (((('x', 1),), 2),),
                    queries=((('x', 3),),))


def candidates():
    shown = public()
    return [replace(shown, hypotheses=((('hypothetical-candidate', j),),)*count)
            for j, count in enumerate((1, 1, 2, 1))]


def cheap(monkeypatch, owner):
    """All-coordinate state/masking fixture; keep real source encoding."""
    calls = dict(observe=0, rows=0, conditional=0, batches=[])
    original_many = owner.observe_sources_many

    def observe(state, source, **kwargs):
        calls['observe'] += 1
        calls['rows'] += len(source)
        value = source.mean((1, 2))
        result = {}
        for key, coordinate in state.items():
            if coordinate.is_floating_point():
                result[key] = .75*coordinate+.25*value.reshape(
                    -1, *([1]*(coordinate.ndim-1)))
            else:
                result[key] = coordinate+1
        return result, {'energy_defect': source.new_zeros(len(source))}

    def conditional(state, source, **kwargs):
        calls['conditional'] += 1
        value = (source+state['fast']).mean((1, 2))+state['reservoir']
        return value[:, None, None].expand(-1, 3, 64), {
            'path_probabilities': value[:, None].expand(-1, 3).softmax(-1)}

    def many(sources, **kwargs):
        calls['batches'].append(tuple(map(len, sources)))
        return original_many(sources, **kwargs)

    monkeypatch.setattr(owner, 'observe', observe)
    monkeypatch.setattr(owner, 'conditional', conditional)
    monkeypatch.setattr(owner, 'observe_sources_many', many)
    monkeypatch.setattr(owner, 'remembered', lambda state: state['fast'])
    return calls


def close_read(left, right):
    for a, b in zip(left[:2], right[:2]):
        torch.testing.assert_close(a, b, atol=1e-6, rtol=1e-6)
    assert left[2].keys() == right[2].keys()
    for key, value in left[2].items():
        if value.is_floating_point():
            torch.testing.assert_close(value, right[2][key], atol=1e-6, rtol=1e-6)
        else:
            assert torch.equal(value, right[2][key]), key


@pytest.mark.parametrize('groups', [(0, 1, 2, 3), (0, 0, 0, 0), (0, 0, 1, 1)])
@pytest.mark.parametrize('grow', [False, True])
def test_distinct_prefixes_use_one_batch_and_match_full_reads(monkeypatch, groups, grow):
    owner = FieldOwner(NativeConfig(nodes=3, rounds=1))
    calls = cheap(monkeypatch, owner)
    views = candidates()
    rings = [torch.full((2048,), .01*group) for group in groups]
    with torch.no_grad():
        states = [owner.empty(1) for _ in views]
        for state in states:
            state['fast'].add_(.02)
            state['reservoir'].add_(.03)
        original = copy.deepcopy(states)
        got = owner.read_features_many(views, states=states, rings=rings, grow=grow)
        count = len(public().records())
        assert calls['batches'] == [(count,)*len(sorted(set(groups))), (1, 1, 2, 1)]
        assert calls['observe'] == count+2  # independent of the number of groups
        assert calls['rows'] == count*len(sorted(set(groups)))+8
        if len(sorted(set(groups))) == len(views):
            assert calls['rows'] == len(views)*max(len(v.records()) for v in views)
        expected = owner.task_features_many(views, states=states, rings=rings,
                                            grow=grow, memory_read=True)
        for left, right in zip(expected, got):
            close_read(left, right)
        for before, after in zip(original, states):
            for key in before:
                assert torch.equal(before[key], after[key]), key
        previous = copy.deepcopy(calls)
        repeated = owner.read_features_many(views, states=states, rings=[r.clone() for r in rings], grow=grow)
        assert calls == previous
        assert all(a is b for a, b in zip(got, repeated))


def test_prefixes_with_different_public_lengths_and_states_are_batched_and_masked(monkeypatch):
    owner = FieldOwner(NativeConfig(nodes=3, rounds=1))
    calls = cheap(monkeypatch, owner)
    views = [public(), replace(public(), words=('heard',)), candidates()[2]]
    with torch.no_grad():
        states = [owner.empty(1) for _ in views]
        states[2]['fast'].add_(.1)  # same public rows, different retained state
        got = owner.read_features_many(views, states=states)
        assert calls['batches'] == [(3, 4, 3), (2,)]
        full = owner.task_features_many(views, states=states, memory_read=True)
        for a, b in zip(full, got):
            close_read(a, b)


def test_prefix_eviction_cannot_discard_a_group_needed_by_this_call(monkeypatch):
    owner = FieldOwner(NativeConfig(nodes=3, rounds=1))
    calls = cheap(monkeypatch, owner)
    with torch.no_grad():
        # Cache a first group before a batch large enough to evict it.
        hit = owner.read_features_many([public()], rings=[torch.zeros(2048)])[0]
        views = [candidates()[1]]*66
        rings = [torch.full((2048,), .001*j) for j in range(66)]
        calls['batches'].clear()
        got = owner.read_features_many(views, rings=rings)
        assert calls['batches'] == [(3,)*65, (1,)*66]
        assert len(owner._prefix_cache) <= 64
        full = owner.task_features_many(views, rings=rings, memory_read=True)
        for a, b in zip(full, got):
            close_read(a, b)
        assert hit[2]['events'].item() == 3


@pytest.mark.parametrize('memory', [False, True])
def test_live_proposer_single_read_reuses_batch_then_invalidates(monkeypatch, memory):
    mask = {**arm_settings('full'), 'memory_layer_a': memory,
            'memory_layer_b': memory, 'field_understanding': memory}
    mind = SeraU(3, config=NativeConfig(nodes=3, rounds=1), crutches=mask)
    calls = cheap(monkeypatch, mind.owner)
    with mind.scope(), torch.no_grad():
        if memory:
            mind.memory.begin(public())
        else:
            mind.proposer.memory_a_enabled = True  # exercise retained reads without the adapter
        shown = candidates()[1]

        def check(view=shown):
            expected = mind.proposer.features_many([view], [{}], memory_read=True)[0]
            previous = copy.deepcopy(calls)
            # Proposer.features is the single-read path used by mind.live.
            got = mind.proposer.features(view, {})
            assert calls == previous
            for a, b in zip(expected, got):
                assert a is b

        check()
        changes = [lambda: mind.owner.raw_port.weight.add_(.01),
                   lambda: mind.state['fast'].add_(.1),
                   lambda: mind.owner.fusion.braid_operators[0, 0, 0].add_(.01),
                   lambda: setattr(mind.owner, 'config', replace(mind.owner.config, rounds=2)),
                   lambda: setattr(mind.owner, 'port_enabled', False),
                   lambda: mind.owner.eval()]
        if memory:
            changes += [lambda: PH.Ideas.read(mind.field.ideas, ('role:schema', 'new association')),
                        lambda: mind.crutches.__setitem__('memory_layer_b', False),
                        lambda: mind.crutches.__setitem__('memory_layer_a', False)]
        else:
            changes += [lambda: setattr(mind.proposer, 'memory_a_enabled', False)]
        for change in changes:
            previous = calls['conditional']
            change()
            mind.proposer.features(shown, {})
            assert calls['conditional'] == previous+1
            check()
        previous = calls['conditional']
        changed = replace(shown, words=('changed view',))
        mind.proposer.features(changed, {})
        assert calls['conditional'] == previous+1
        check(changed)


@pytest.mark.parametrize('memory_read', [False, True])
def test_direct_single_reads_share_the_reader_and_keep_training_graphs(monkeypatch, memory_read):
    owner = FieldOwner(NativeConfig(nodes=3, rounds=1))
    calls = cheap(monkeypatch, owner)
    shown = public()
    with torch.no_grad():
        read = owner.read_features_many([shown], memory_read=True)[0]
        previous = copy.deepcopy(calls)
        assert owner.task_features(shown, memory_read=memory_read) is read
        assert calls == previous
        owner.token_ids['role:schema'] = 1
        fresh = owner.task_features(shown, memory_read=memory_read)
        assert fresh is not read
        assert calls['conditional'] == previous['conditional']+1
        # Layer/caller context is still part of the key.
        context_read = owner.task_features(shown, memory_read=memory_read, context=('a-only',))
        assert context_read is not fresh
    for _ in range(2):
        owner.zero_grad(set_to_none=True)
        graph = owner.task_features(shown, memory_read=memory_read)
        assert graph[0].requires_grad
        graph[0].square().mean().backward()
        assert owner.words.weight.grad is not None
        assert owner.words.weight.grad.abs().sum() > 0
    assert owner.core._read_geometry_cache is None


def test_direct_single_read_invalidates_an_in_place_ring_and_grow_change(monkeypatch):
    owner = FieldOwner(NativeConfig(nodes=3, rounds=1))
    calls = cheap(monkeypatch, owner)
    ring = torch.zeros(2048)
    with torch.no_grad():
        read = owner.read_features_many([public()], rings=[ring])[0]
        assert owner.task_features(public(), ring=ring, memory_read=True) is read
        previous = calls['conditional']
        ring.add_(.01)
        changed = owner.task_features(public(), ring=ring, memory_read=True)
        assert calls['conditional'] == previous+1
        close_read(changed, owner.task_features_many([public()], rings=[ring], memory_read=True)[0])
        previous = calls['conditional']
        owner.task_features(public(), ring=ring, memory_read=True, grow=False)
        assert calls['conditional'] == previous+1


def test_single_read_still_checks_the_original_port_budget_before_a_cache_hit(monkeypatch):
    owner = FieldOwner(NativeConfig(nodes=3, rounds=1))
    cheap(monkeypatch, owner)
    shown = replace(public(), examples=public().examples*5)
    with torch.no_grad():
        owner.task_features(shown, memory_read=True)
        with pytest.raises(PortBudget, match='four public examples'):
            owner.task_features(shown)


def test_geometry_matches_pinned_bits_for_native_and_echo_dtypes_and_parameter_step(monkeypatch):
    owner = FieldOwner(NativeConfig(nodes=3, rounds=1))
    pinned = UnifiedEnergy.geometry
    computed = []

    def geometry(core):
        computed.append(core.links.dtype)
        return pinned(core)

    monkeypatch.setattr(UnifiedEnergy, 'geometry', geometry)
    with torch.no_grad():
        version = owner.readout_version()
        with owner.geometry_reads(version):
            first = owner.core.geometry()
            assert owner.core.geometry() is first
            assert all(torch.equal(a, b) for a, b in zip(first, pinned(owner.core)))
            assert not any(v.requires_grad for v in first)
            # Exercise the same parameter substitution used by core_echo,
            # including enable_grad for independent coordinate derivatives.
            state = {k: v.double() for k, v in owner.core.empty(1).items()}
            source = torch.full((1, 3, 3), .01, dtype=torch.float64)
            parameters = {k: v.double() for k, v in owner.core.named_parameters()}
            with torch.enable_grad():
                q = state['q'].detach().requires_grad_(True)
                value = functional_call(owner.core, parameters, ({**state, 'q': q}, source))[0]
                derivative = torch.autograd.grad(value.sum(), q)[0]
                value_again = functional_call(owner.core, parameters, ({**state, 'q': q}, source))[0]
                torch.testing.assert_close(value, value_again, atol=0, rtol=0)
            assert computed == [torch.float32, torch.float64]
            assert len(owner._geometry_cache) == 2
        assert owner.core._read_geometry_cache is None
        # Compare the substituted geometry and coordinate derivative against
        # the original class with the exact same tensors and double arithmetic.
        baseline = copy.deepcopy(owner.core)
        baseline.__class__ = UnifiedEnergy
        baseline.double()
        expected_geometry = pinned(baseline)
        double_geometry = [pair for pair in owner._geometry_cache.values() if pair[0].dtype == torch.float64][0]
        assert all(torch.equal(a, b) for a, b in zip(double_geometry, expected_geometry))
        with torch.enable_grad():
            expected_q = state['q'].detach().requires_grad_(True)
            expected_value = baseline.energy({**state, 'q': expected_q}, source)[0]
            expected_derivative = torch.autograd.grad(expected_value.sum(), expected_q)[0]
        torch.testing.assert_close(value, expected_value, atol=0, rtol=0)
        torch.testing.assert_close(derivative, expected_derivative, atol=0, rtol=0)
    optimizer = torch.optim.SGD(owner.parameters(), lr=.01)
    owner.core.links.sum().backward()
    optimizer.step()
    with torch.no_grad(), owner.geometry_reads(owner.readout_version()):
        changed = owner.core.geometry()
        assert changed is not first
        assert len(owner._geometry_cache) == 1
        assert all(torch.equal(a, b) for a, b in zip(changed, pinned(owner.core)))
    # The outer training path gets a fresh parameter graph on every call.
    for _ in range(2):
        owner.zero_grad(set_to_none=True)
        rotations = owner.core.geometry()
        assert all(v.requires_grad for v in rotations)
        rotations[0].sum().backward()
        assert owner.core.links.grad is not None
        assert owner.core.links.grad.abs().sum() > 0


def test_geometry_scope_restores_after_a_read_failure(monkeypatch):
    owner = FieldOwner(NativeConfig(nodes=3, rounds=1))
    def fail(*args, **kwargs):
        assert owner.core._read_geometry_cache is owner._geometry_cache
        owner.core.geometry()
        raise RuntimeError('read failed')
    monkeypatch.setattr(owner, 'observe', fail)
    with torch.no_grad(), pytest.raises(RuntimeError, match='read failed'):
        owner.read_features_many([public()])
    assert owner.core._read_geometry_cache is None
    assert owner.core.geometry()[0].requires_grad


@pytest.mark.parametrize('groups', [(0, 1, 2), (0, 0, 0), (0, 0, 1)])
def test_real_settle_matches_uncached_full_reads_and_draws_nothing(groups):
    owner = FieldOwner(NativeConfig(nodes=3, rounds=1))
    reference = copy.deepcopy(owner)
    reference.readout_reuse_enabled = False
    shown = TaskView((('x', 'num'),), 'num')
    views = [replace(shown, hypotheses=((('hypothetical-candidate', j),),)*count)
             for j, count in enumerate((0, 1, 2))]
    rings = [torch.full((2048,), .01*group) for group in groups]
    with torch.no_grad():
        before = global_rng()
        expected = reference.task_features_many(views, rings=rings, memory_read=True)
        got = owner.read_features_many(views, rings=rings)
        for a, b in zip(expected, got):
            close_read(a, b)
        assert owner.token_ids == reference.token_ids
        assert len(owner._geometry_cache) == 2  # actual float32 + echo float64
        owner.task_features(views[0], ring=rings[0], memory_read=True)
        after = global_rng()
    assert before['python'] == after['python']
    assert before['numpy'][0] == after['numpy'][0]
    np.testing.assert_array_equal(before['numpy'][1], after['numpy'][1])
    assert before['numpy'][2:] == after['numpy'][2:]
    assert torch.equal(before['cpu'], after['cpu'])
    assert len(before['cuda']) == len(after['cuda'])
    assert all(torch.equal(a, b) for a, b in zip(before['cuda'], after['cuda']))


def test_geometry_and_read_caches_are_not_checkpointed_or_hashed(monkeypatch):
    mind = SeraU(3, config=NativeConfig(nodes=3, rounds=1), crutches=arm_settings('full'))
    cheap(monkeypatch, mind.owner)
    with torch.no_grad():
        # Avoid vocabulary growth so filling caches is the only difference.
        mind.owner.read_features_many([public()], grow=False)
        with mind.owner.geometry_reads(mind.owner.readout_version()):
            mind.owner.core.geometry()
        before = mind.learning_hash()
        restored = SeraU.loads(mind.dumps())
        assert restored.learning_hash() == before
        assert not restored.owner._readout_cache
        assert not restored.owner._prefix_cache
        assert not restored.owner._geometry_cache
        assert restored.owner._geometry_version is None
        assert restored.owner.core._read_geometry_cache is None
        mind.owner.clear_readouts()
        assert mind.learning_hash() == before
        assert not mind.owner._geometry_cache
