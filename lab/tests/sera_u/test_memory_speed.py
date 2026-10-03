"""US2: short CPU contracts for exact scheduling, cache validity and restart."""
import copy
from collections import Counter
from dataclasses import replace
import math

import numpy as np
import pytest
import torch

from sera import crutches as CR, lang as LG, one as ONE, phi as PH, tasks as TS
from sera_u import SeraU
from sera_u.field.native_owner import NativeConfig
from sera_u.memory import memory_records
from sera_u.mind import arm_settings
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


def entity(**switches):
    return SeraU(3, config=NativeConfig(nodes=3, rounds=1),
                 crutches={**arm_settings('full'), **switches})


def view():
    return TaskView((('x', 'num'),), 'num', (((('x', 1),), 2),),
                    measurements=(('m', 1), ('m', 2), ('m', 1)))


def close(a, b):
    # Same float32 rounding allowance as US's CPU read/gradient parity tests.
    torch.testing.assert_close(a, b, atol=1e-6, rtol=1e-6)


def state_close(a, b):
    assert a.keys() == b.keys()
    for key in a:
        if a[key].is_floating_point():
            close(a[key], b[key])
        else:
            assert torch.equal(a[key], b[key])


def cheap_observe(monkeypatch, mind):
    """Keep event order and source dependence; avoid the coupled settle in cache tests."""
    def observe(state, source, **kwargs):
        return {**state, 'fast': .75*state['fast']+.25*source,
                'events': state['events']+1}, {'energy_defect': source.new_zeros(len(source))}
    monkeypatch.setattr(mind.owner, 'observe', observe)
    monkeypatch.setattr(mind.owner, 'remembered', lambda state: state['fast'])


@pytest.mark.parametrize('grow', [True, False])
def test_record_encoding_matches_singles_allocation_edges_and_gradients(grow):
    single = FieldOwner(NativeConfig(nodes=3, rounds=1))
    batch = copy.deepcopy(single)
    rows = memory_records(view())+( (('role:heard', 0., 0., 1.), ('unicode é', 0., 0., 1.)), )
    expected = torch.cat([single.encode_record(row, grow=grow) for row in rows], 0)
    got = batch.encode_records(rows, grow=grow)
    assert single.token_ids == batch.token_ids
    close(expected, got)
    expected.square().mean().backward()
    got.square().mean().backward()
    for name in ('words.weight', 'raw_port.weight', 'local.weight', 'text_source.weight'):
        close(dict(single.named_parameters())[name].grad, dict(batch.named_parameters())[name].grad)


def test_encoding_groups_exact_lengths_with_bounded_batches():
    owner = FieldOwner(NativeConfig(nodes=3, rounds=1))
    row = (('role:heard', 0., 0., 1.), ('one', 0., 0., 1.))
    shapes = []
    hook = owner.local.register_forward_pre_hook(lambda module, args: shapes.append(tuple(args[0].shape)))
    try:
        got = owner.encode_records([row]*257)
    finally:
        hook.remove()
    assert got.shape == (257, 3, 3)
    assert [s[0] for s in shapes] == [256, 1]
    assert [s[-1] for s in shapes] == [2, 2]
    assert owner.encode_records([]).shape == (0, 3, 3)
    oversized = (('é'*129, 0., 0., 1.),)
    with pytest.raises(PortBudget, match='Byte fallback'):
        owner.encode_records([oversized], grow=False)


@pytest.mark.parametrize('ports', [True, False])
def test_refresh_preserves_duplicate_schedule_b_state_and_reads(monkeypatch, ports):
    single, batch = entity(field_input_ports=ports), entity(field_input_ports=ports)
    for mind in (single, batch):
        cheap_observe(monkeypatch, mind)
    # Reference encode one source at a time, including native hashed text ports.
    def singles(rows):
        return [(single.owner.encode_record(row) if ports else single.owner.encode_texts(
            [' '.join(t[0] for t in row)])) for row in rows]
    monkeypatch.setattr(single.memory, 'encode_rows', singles)
    schedules = []
    original = batch.memory.write_record
    def record(row, **kwargs):
        schedules.append(row)
        return original(row, **kwargs)
    monkeypatch.setattr(batch.memory, 'write_record', record)
    shown = view()
    grown = replace(shown, examples=shown.examples+(((('x', 3),), 4),),
                    measurements=shown.measurements+(('m', 1),))
    for mind in (single, batch):
        with mind.scope(), torch.no_grad():
            mind.memory.begin(shown)
            mind.memory.refresh(grown)
            before = mind.state['events'].clone()
            mind.memory.refresh(grown)
            assert torch.equal(before, mind.state['events'])
            mind._test_read = mind.memory.features(grown)
    first, later = Counter(memory_records(shown)), Counter(memory_records(grown))
    expected = [row for row, n in first.items() for _ in range(n)]
    expected += [row for row, n in later.items() for _ in range(max(0, n-first[row]))]
    assert schedules == expected
    state_close(single.state, batch.state)
    assert single.owner.token_ids == batch.owner.token_ids
    a, b = single.field.ideas, batch.field.ideas
    assert a._row == b._row and a.of == b.of and a.read_n == b.read_n and a.rev == b.rev
    np.testing.assert_array_equal(a._M[:a._n], b._M[:b._n])
    np.testing.assert_array_equal(a._E[:a._n], b._E[:b._n])
    close(single._test_read[0], batch._test_read[0])
    close(single._test_read[1], batch._test_read[1])
    state_close(single._test_read[2], batch._test_read[2])


def test_real_sequential_settle_from_batched_encoding_matches_single_encoding(monkeypatch):
    single, batch = entity(), entity()
    monkeypatch.setattr(single.memory, 'encode_rows', lambda rows: [single.owner.encode_record(r) for r in rows])
    shown = replace(view(), measurements=())          # two real settled observations
    for mind in (single, batch):
        with mind.scope(), torch.no_grad():
            mind.memory.begin(shown)
            mind._test_read = mind.memory.features(shown)
    state_close(single.state, batch.state)
    assert single.owner.token_ids == batch.owner.token_ids
    left, right = single.field.ideas, batch.field.ideas
    assert left._row == right._row and left.of == right.of
    np.testing.assert_array_equal(left._M[:left._n], right._M[:right._n])
    close(single._test_read[0], batch._test_read[0])
    close(single._test_read[1], batch._test_read[1])


@pytest.mark.parametrize('a', [True, False])
def test_ring_cache_matches_fresh_after_all_supported_changes(monkeypatch, a):
    mind = entity(memory_layer_a=a)
    cheap_observe(monkeypatch, mind)
    original, calls = mind.memory._compute_ring, []
    def compute(shown):
        calls.append(shown)
        return original(shown)
    monkeypatch.setattr(mind.memory, '_compute_ring', compute)
    with mind.scope(), torch.no_grad():
        shown = view()
        mind.memory.begin(shown)
        def check(v):
            before = len(calls)
            cached = mind.memory.ring(v)
            assert len(calls) == before+1
            assert torch.equal(cached, original(v))
            assert mind.memory.ring(v) is cached
            assert len(calls) == before+1
        check(shown)
        mind.field.ideas._at('structural-only')
        check(shown)
        mind.field.ideas._idea('structural-only')
        check(shown)
        PH.Ideas.read(mind.field.ideas, ('new', 'idea'))  # B-only write, no A event
        check(shown)
        mind.field.ideas.bind('new', ('idea', 1), .75, perceived=False)
        check(shown)
        mind.field.ideas.bind_pattern(('u-part', ('scope', 'part')), np.ones(PH.IDEA_DIM), .2)
        check(shown)
        mind.field.ideas.redirect({('idea', 1): ('concept', 9)})
        check(shown)
        mind.field.ideas._came = {('new', 'idea'): {'new': 1.}}
        mind.field.ideas.consolidate(.25, lambda *args: True)
        check(shown)
        mind.owner.memory_projection.weight.add_(.01)
        check(shown)
        if a:
            mind.memory.write_record((('role:heard', 0., 0., 1.), ('observed', 0., 0., 1.)), write_b=False)
            check(shown)
            mind.state['fast'].add_(.1)                 # in-place A edit
            check(shown)
            # Same content in new tensors is the same reading: the state is keyed by content, not identity (a freed
            # tensor's id/address are reused, so identity keys could make a stale ring look current).
            mind.state = {k: v.clone() for k, v in mind.state.items()}
            before = len(calls)
            assert torch.equal(mind.memory.ring(shown), original(shown)) and len(calls) == before
        check(replace(shown, words=('new public view',)))
        mind.crutches['memory_layer_b'] = False
        assert mind.memory.ring(shown) is None


def test_no_grad_feature_cache_avoids_ring_walk_and_reads_and_invalidates_weights(monkeypatch):
    mind = entity()
    cheap_observe(monkeypatch, mind)
    with mind.scope(), torch.no_grad():
        mind.memory.begin(view())
        ring_calls, read_calls = [], []
        ring_fn, read_fn = mind.memory._compute_ring, mind.owner.task_features
        def ring(v):
            ring_calls.append(v)
            return ring_fn(v)
        def read(v, **kwargs):
            read_calls.append(v)
            return read_fn(v, **kwargs)
        monkeypatch.setattr(mind.memory, '_compute_ring', ring)
        monkeypatch.setattr(mind.owner, 'task_features', read)
        cached = mind.memory.features(view())
        assert mind.memory.features(view()) is cached
        repeated = mind.memory.features_many([view(), view()])
        assert repeated[0] is cached and repeated[1] is cached
        assert len(ring_calls) == len(read_calls) == 1
        mind.owner.memory_gate.add_(.1)
        changed = mind.memory.features(view())
        assert changed is not cached and len(read_calls) == 2
        # B-only writes must also invalidate a cached neural read.
        PH.Ideas.read(mind.field.ideas, ('new', 'association'))
        assert mind.memory.features(view()) is not changed
        assert len(read_calls) == 3
    assert not mind.memory._ring_cache and not mind.memory._feature_versions


@pytest.mark.parametrize('a,b', [(True, True), (True, False), (False, True), (False, False)])
def test_memory_features_many_parity_and_factual_state_unchanged(a, b):
    single, batch = entity(memory_layer_a=a, memory_layer_b=b), entity(memory_layer_a=a, memory_layer_b=b)
    views = [view(), replace(view(), words=('new heard',), queries=((('x', 7),),)), view()]
    with single.scope(), batch.scope(), torch.no_grad():
        single.memory.begin(view())
        batch.memory.begin(view())
        before_state = copy.deepcopy(batch.state)
        before_b = batch.field.ideas._M[:batch.field.ideas._n].copy()
        expected = [single.memory.features(v) for v in views]
        got = batch.memory.features_many(views)
        assert got[0] is got[2]
        for x, y in zip(expected, got):
            close(x[0], y[0]); close(x[1], y[1]); state_close(x[2], y[2])
        state_close(before_state, batch.state)
        np.testing.assert_array_equal(before_b, batch.field.ideas._M[:batch.field.ideas._n])
        assert single.owner.token_ids == batch.owner.token_ids


@pytest.mark.parametrize('batching', [True, False])
def test_live_sequence_learning_hash_and_exact_resume_with_memory_on(monkeypatch, tmp_path, batching):
    monkeypatch.setattr(ONE.time, 'process_time', lambda: 0.)
    def task():
        return TS.Exact('math', 'identity', lambda x: x, {'x': 'num'}, 'num', [0, 1], [],
                        lambda rng: int(rng.integers(0, 3)))
    first, duplicate = entity(field_proposer=False), entity(field_proposer=False)
    for mind in (first, duplicate):
        mind.batched_reads = batching
        mind.live(task(), task_wall=math.inf, max_steps=0)
    assert first.learning_hash() == duplicate.learning_hash()
    checkpoint = tmp_path/'memory-speed.pt'
    first.save(checkpoint)
    restored = SeraU.load(checkpoint)
    assert first.learning_hash() == restored.learning_hash()
    assert not restored.memory._ring_cache and not restored.memory._feature_cache
    for mind in (first, duplicate, restored):
        mind.live(task(), task_wall=math.inf, max_steps=0)
    assert first.learning_hash() == duplicate.learning_hash() == restored.learning_hash()
    for key in first.state:
        assert torch.equal(first.state[key], restored.state[key]), key
    for key in first.owner.state_dict():
        assert torch.equal(first.owner.state_dict()[key], restored.owner.state_dict()[key]), key


def test_autograd_reads_never_reuse_detached_feature_cache(monkeypatch):
    mind = entity()
    cheap_observe(monkeypatch, mind)
    with mind.scope():
        mind.memory.begin(view())
        with torch.no_grad():
            detached = mind.memory.features(view())
        for _ in range(2):
            mind.optimizer.zero_grad(set_to_none=True)
            read = mind.memory.features_many([view(), view()])
            assert read[0] is read[1] and read[0] is not detached
            read[0][0].square().mean().backward()
            assert mind.owner.words.weight.grad is not None
            assert mind.owner.words.weight.grad.abs().sum() > 0
