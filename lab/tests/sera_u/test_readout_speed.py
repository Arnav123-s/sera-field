"""US3: CPU prefix/read equivalence, content invalidation, RNG and lived restart."""
import copy
from dataclasses import replace
import math

import numpy as np
import pytest
import torch

from sera import crutches as CR, lang as LG, one as ONE, phi as PH, tasks as TS
from sera_u import SeraU
from sera_u.field.native_owner import NativeConfig
from sera_u.memory import memory_records
from sera_u.mind import Engine, U3_CRUTCHES, U6_CRUTCHES, U7_CRUTCHES, arm_settings, global_rng
from sera_u.ports import TaskView


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


def entity(a=True, b=True, **switches):
    mask = {**arm_settings('full'), **{k: True for k in U3_CRUTCHES+U6_CRUTCHES+U7_CRUTCHES},
            'memory_layer_a': a, 'memory_layer_b': b, 'field_understanding': a or b, **switches}
    return SeraU(3, config=NativeConfig(nodes=3, rounds=1), crutches=mask)


def public(lists=False):
    return (TaskView((('x', 'list'),), 'list', (((('x', (1, -2)),), (-2, 1)),),
                     queries=((('x', (0, 3)),),)) if lists else
            TaskView((('x', 'num'),), 'num', (((('x', 1),), 2),), queries=((('x', 3),),)))


def candidates(shown):
    # Unequal suffix lengths exercise frozen absent rows and complete mean order.
    return [shown, Engine._u_candidate_view(shown, ('one', None), (2,)),
            Engine._u_candidate_view(shown, ('other', None), (3, 4)), shown]


def close_read(left, right):
    for a, b in zip(left[:2], right[:2]):
        torch.testing.assert_close(a, b, atol=1e-6, rtol=1e-6)
    if len(left) == 3:
        assert left[2].keys() == right[2].keys()
        for key, value in left[2].items():
            if value.is_floating_point():
                torch.testing.assert_close(value, right[2][key], atol=1e-6, rtol=1e-6)
            else:
                assert torch.equal(value, right[2][key]), key


def padded(lengths):
    """Rows observe_sources_many settles for a batch: every row padded to the longest."""
    return len(lengths)*max(lengths)


def cheap(monkeypatch, mind):
    """Deterministic source/state dependent cache fixture, with actual encoding."""
    calls = dict(observe=0, rows=0, conditional=0)
    def observe(state, source, **kwargs):
        calls['observe'] += 1
        calls['rows'] += len(source)
        return {**state, 'fast': .75*state['fast']+.25*source,
                'events': state['events']+1}, {'energy_defect': source.new_zeros(len(source))}
    def conditional(state, source, **kwargs):
        calls['conditional'] += 1
        value = (source+state['fast']).mean((1, 2))
        return value[:, None, None].expand(-1, 3, 64), {
            'path_probabilities': value[:, None].expand(-1, 3).softmax(-1)}
    monkeypatch.setattr(mind.owner, 'observe', observe)
    monkeypatch.setattr(mind.owner, 'conditional', conditional)
    monkeypatch.setattr(mind.owner, 'remembered', lambda state: state['fast'])
    return calls


@pytest.mark.parametrize('a,b', [(True, True), (True, False), (False, True), (False, False)])
@pytest.mark.parametrize('lists', [True, False])
def test_candidate_prefix_matches_full_reads_all_memory_layers(a, b, lists):
    reference, fast = entity(a, b), entity(a, b)
    views = candidates(public(lists))
    with reference.scope(), fast.scope(), torch.no_grad():
        for mind in (reference, fast):
            if mind.proposer.memory is not None:
                mind.memory.begin(views[0])
        expected = reference.owner.task_features_many(
            list(dict.fromkeys(views)), states=[reference.state if a else reference.owner.empty(1)]*3,
            rings=[reference.memory.ring(v) if (a or b) else None for v in dict.fromkeys(views)],
            memory_read=True)
        original = {k: v.clone() for k, v in fast.state.items()}
        before = fast.field.ideas._M[:fast.field.ideas._n].copy()
        got = fast.engine._u_reads(views)
        for left, right in zip(expected, got[:3]):
            close_read(left[:2], right)
        assert got[0][0] is got[3][0]
        for key in original:
            assert torch.equal(fast.state[key], original[key]), key
        np.testing.assert_array_equal(before, fast.field.ideas._M[:fast.field.ideas._n])
        assert fast.owner.token_ids == reference.owner.token_ids
        # Compare every coordinate of the optimized rollout as well as features.
        actual = fast.owner.read_features_many(list(dict.fromkeys(views)),
            states=[fast.state if a else fast.owner.empty(1)]*3,
            rings=[fast.memory.ring(v) if (a or b) else None for v in dict.fromkeys(views)],
            context=('memory', a, b) if (a or b) else ('proposer', a))
        for left, right in zip(expected, actual):
            close_read(left, right)


def test_prefix_is_settled_once_across_calls_and_new_hypothetical_tokens(monkeypatch):
    mind = entity(False, False)
    calls = cheap(monkeypatch, mind)
    base, first, second, _ = candidates(public())
    with mind.scope(), torch.no_grad():
        mind.proposer.memory_a_enabled = True  # explicit retained-state path without a Memory adapter
        mind.engine._u_reads([base])
        public_rows = len(memory_records(base))
        assert calls['rows'] == public_rows
        mind.engine._u_reads([first, second])
        # The public prefix is not settled again; the two suffixes are settled as one batch padded to the longer
        # (observe_sources_many: the absent row is computed and masked out, never kept).
        assert calls['rows'] == public_rows+padded([len(first.hypotheses), len(second.hypotheses)])
        count = calls.copy()
        again = mind.engine._u_reads([replace(first), replace(second), base])
        assert calls == count  # no observe, conditional, or new state on identical reads
        mind.proposer.retained = {k: v.clone() for k, v in mind.proposer.retained.items()}
        close_read(again[0], mind.engine._u_reads([first])[0])
        assert calls == count  # state-content clones are hits, not tensor-ID misses
    assert not mind.owner._readout_cache and not mind.owner._prefix_cache


def test_grow_false_byte_fallback_reads_keep_prefix_and_allocation_order(monkeypatch):
    mind = entity(False, False)
    calls = cheap(monkeypatch, mind)
    views = candidates(public())[:3]
    with torch.no_grad():
        got = mind.owner.read_features_many(views, grow=False)
        # The prefix once, then the nonempty suffixes as one batch padded to the longest (masked, never kept).
        assert calls['rows'] == len(memory_records(views[0]))+padded([len(v.hypotheses) for v in views[1:]])
        assert mind.owner.token_ids == {}
        count = calls.copy()
        again = mind.owner.read_features_many(views, grow=False)
        assert calls == count
        expected = mind.owner.task_features_many(views, grow=False, memory_read=True)
        for left, right, repeated in zip(expected, got, again):
            close_read(left, right)
            assert right is repeated
        assert mind.owner.token_ids == {}


def test_memory_ring_snapshot_detects_in_place_ad_hoc_ring_changes(monkeypatch):
    mind = entity()
    calls = cheap(monkeypatch, mind)
    ring, shown = torch.zeros(2048), public()
    monkeypatch.setattr(mind.memory, 'ring', lambda view: ring)
    with mind.scope(), torch.no_grad():
        mind.memory.begin(shown)
        mind.memory.features_many([shown])
        count = calls.copy()
        mind.memory.features_many([shown])
        assert calls == count
        ring.add_(.01)
        changed = mind.memory.features_many([shown])[0]
        assert calls['conditional'] == count['conditional']+1
        fresh = mind.owner.task_features_many([shown], states=[mind.state], rings=[ring], memory_read=True)[0]
        close_read(changed, fresh)


def test_reopened_vocabulary_capacity_cannot_skip_a_new_allocation(monkeypatch):
    mind = entity(False, False)
    calls = cheap(monkeypatch, mind)
    capacity = mind.owner.words.num_embeddings-257
    mind.owner.token_ids = {'filler:'+str(j): j+257 for j in range(capacity)}
    with torch.no_grad():
        mind.owner.read_features_many([public()])
        assert 'role:schema' not in mind.owner.token_ids
        count = calls.copy()
        mind.owner.token_ids.pop('filler:0')
        changed = mind.owner.read_features_many([public()])[0]
        assert 'role:schema' in mind.owner.token_ids
        assert calls['conditional'] == count['conditional']+1
        close_read(changed, mind.owner.task_features_many([public()], memory_read=True)[0])


def test_different_rings_cannot_share_prefix_and_each_result_matches_full(monkeypatch):
    mind = entity(False, False)
    calls = cheap(monkeypatch, mind)
    views = candidates(public())[1:3]
    rings = [torch.zeros(2048), torch.ones(2048)*.01]
    with torch.no_grad():
        got = mind.owner.read_features_many(views, rings=rings)
        # No shared prefix across rings: both whole views, settled as one padded batch.
        assert calls['rows'] == padded([len(memory_records(v)) for v in views])
        expected = mind.owner.task_features_many(views, rings=rings, memory_read=True)
        for left, right in zip(expected, got):
            close_read(left, right)
        previous = calls.copy()
        mind.owner.read_features_many(views, rings=[r.clone() for r in rings])
        assert calls == previous
        rings[0].add_(.01)
        changed = mind.owner.read_features_many([views[0]], rings=[rings[0]])[0]
        assert calls['conditional'] == previous['conditional']+1
        close_read(changed, mind.owner.task_features_many([views[0]], rings=[rings[0]], memory_read=True)[0])


@pytest.mark.parametrize('a,b', [(True, True), (True, False), (False, True), (False, False)])
def test_hits_invalidate_after_observation_parameter_idea_view_and_switch(monkeypatch, a, b):
    mind = entity(a, b)
    calls = cheap(monkeypatch, mind)
    shown = candidates(public())[1]
    with mind.scope(), torch.no_grad():
        if a or b:
            mind.memory.begin(public())
        def check(v=shown):
            got = mind.engine._u_reads([v])[0]
            count = calls.copy()
            close_read(got, mind.engine._u_reads([replace(v)])[0])
            assert calls == count
            expected = mind.owner.task_features_many([v],
                states=[mind.state if mind.proposer.memory_a_enabled else mind.owner.empty(1)],
                rings=[mind.memory.ring(v) if mind.proposer.memory is not None else None], memory_read=True)[0]
            close_read(got, expected[:2])
            return got
        check()
        # Observation uses the ordinary bridge/invalidation path.
        mind.memory.write_record((('role:heard', 0., 0., 1.), ('observed', 0., 0., 1.)))
        check()
        count = calls['conditional']
        # An optimizer update must invalidate even without proposer.changed().
        with torch.enable_grad():
            mind.optimizer.zero_grad(set_to_none=True)
            mind.owner.raw_port.weight.sum().backward()
            mind.optimizer.step()
        check()
        assert calls['conditional'] > count
        # B-only association writes (no A event) use the Ideas ledger version.
        PH.Ideas.read(mind.field.ideas, ('role:hypothetical', 'hypothetical-candidate'))
        check()
        check(replace(shown, queries=((('x', 7),),)))
        if a:
            mind.state['fast'].add_(.1)
            check()
        # Switch changes are rejected at new scope boundaries by SeraU. Within
        # an already active scope, the read cache still respects the actual layers.
        if mind.proposer.memory is not None:
            mind.crutches['memory_layer_a'] = not a
            mind.proposer.memory_a_enabled = not a
            check()
            mind.crutches['memory_layer_b'] = not b
            check()
        else:
            mind.proposer.memory_a_enabled = True
            check()
        mind.owner.port_enabled = False
        check()


def test_replacement_parameters_buffers_and_vocab_remapping_use_content(monkeypatch):
    mind = entity(False, False)
    calls = cheap(monkeypatch, mind)
    shown = public()
    with torch.no_grad():
        mind.owner.read_features_many([shown])
        before = calls.copy()
        mind.owner.raw_port.weight = torch.nn.Parameter(mind.owner.raw_port.weight.clone())
        mind.owner.read_features_many([shown])
        assert calls == before  # identical content despite a new allocation
        mind.owner.raw_port.weight.add_(.01)
        mind.owner.read_features_many([shown])
        assert calls['conditional'] == before['conditional']+1
        before = calls.copy()
        mind.owner.fusion.braid_operators = mind.owner.fusion.braid_operators.clone()
        mind.owner.read_features_many([shown])
        assert calls == before
        mind.owner.fusion.braid_operators[0, 0, 0].add_(.01)
        mind.owner.read_features_many([shown])
        assert calls['conditional'] == before['conditional']+1
        # Reassign a token without changing dict size: length/identity is insufficient.
        token = 'role:schema'
        mind.owner.token_ids[token] = 1
        changed = mind.owner.read_features_many([shown])[0]
        close_read(changed, mind.owner.task_features_many([shown], memory_read=True)[0])


def test_autograd_bypasses_both_detached_caches_on_every_call(monkeypatch):
    mind = entity(False, False)
    cheap(monkeypatch, mind)
    shown = candidates(public())[1]
    with torch.no_grad():
        detached = mind.owner.read_features_many([shown])[0]
    for _ in range(2):
        mind.optimizer.zero_grad(set_to_none=True)
        read = mind.owner.read_features_many([shown])[0]
        assert read is not detached and read[0].requires_grad
        read[0].square().mean().backward()
        assert mind.owner.words.weight.grad is not None
        assert mind.owner.words.weight.grad.abs().sum() > 0


def assert_rng_equal(left, right):
    assert left['python'] == right['python']
    assert left['numpy'][0] == right['numpy'][0]
    np.testing.assert_array_equal(left['numpy'][1], right['numpy'][1])
    assert left['numpy'][2:] == right['numpy'][2:]
    assert torch.equal(left['cpu'], right['cpu'])
    assert len(left['cuda']) == len(right['cuda'])
    for a, b in zip(left['cuda'], right['cuda']):
        assert torch.equal(a, b)


@pytest.mark.parametrize('a,b', [(True, True), (True, False), (False, True), (False, False)])
def test_real_full_prefix_and_cached_reads_draw_no_randomness(a, b):
    mind = entity(a, b)
    views = candidates(public())[1:3]
    with mind.scope(), torch.no_grad():
        if a or b:
            mind.memory.begin(public())
        before = global_rng()
        private = (mind.random.getstate(), copy.deepcopy(mind.numpy.bit_generator.state),
                   mind.torch_generator.get_state().clone())
        mind.engine._u_reads(views)
        assert_rng_equal(before, global_rng())
        mind.engine._u_reads(views)
        assert_rng_equal(before, global_rng())
        mind.owner.task_features_many(views, states=[mind.state if a else mind.owner.empty(1)]*2,
            rings=[mind.memory.ring(v) if (a or b) else None for v in views], memory_read=True)
        assert_rng_equal(before, global_rng())
        assert private[0] == mind.random.getstate()
        assert private[1] == mind.numpy.bit_generator.state
        assert torch.equal(private[2], mind.torch_generator.get_state())


def live_task():
    return TS.Exact('math', 'short identity', lambda x: x, {'x': 'num'}, 'num', [0, 1], [],
                    lambda rng: int(rng.integers(0, 3)))


def identity_program():
    return LG.node('var', payload='x')


def generate_identity(self, task, level, concepts):
    return [identity_program()]


def choose_answer(self, kind, x, probability, available, rng, spent=0.):
    # Exercise a real U7 draw while keeping the lived fixture one proof long.
    f = self.choice_features(x, probability, spent)
    rng.multivariate_normal(np.zeros(2), np.eye(2))
    chosen = 'answer' if 'answer' in available else sorted(available)[0]
    return chosen, f, {a: (float(a == chosen), float(a == chosen)) for a in sorted(available)}


def test_three_lived_u3_u6_u7_sequences_same_seed_hash_and_exact_resume(monkeypatch):
    # U7 and methods deliberately learn CPU-second returns. Supply a fixed
    # clock to test determinism of learning, never erase time-derived weights.
    monkeypatch.setattr(ONE.time, 'process_time', lambda: 0.)
    monkeypatch.setattr(Engine, '_generate', generate_identity)
    monkeypatch.setattr(Engine, '_evoke', lambda *args, **kwargs: None)
    monkeypatch.setattr(PH.NotYetWays, 'pick', choose_answer)
    hashes = []
    for repeat in range(3):
        mind = entity(field_proposer=False)
        first = mind.live(live_task(), task_wall=math.inf, max_steps=1)
        assert first['proven'] and first['u7']['state'] == 'right'
        restored = SeraU.loads(mind.dumps())
        assert mind.learning_hash() == restored.learning_hash()
        assert not restored.owner._readout_cache and not restored.owner._prefix_cache
        for learner in (mind, restored):
            record = learner.live(live_task(), task_wall=math.inf, max_steps=1)
            assert record['proven']
        assert mind.learning_hash() == restored.learning_hash()
        assert_rng_equal(mind.rngs, restored.rngs)
        for key in mind.owner.state_dict():
            assert torch.equal(mind.owner.state_dict()[key], restored.owner.state_dict()[key]), key
        hashes.append(mind.learning_hash())
        # Measurement changes must not enter the hash.
        mind.field.log[-1]['wall'] = 98765.+repeat
        assert mind.learning_hash() == hashes[-1]
    assert len(set(hashes)) == 1


def test_profile_instrumentation_can_checkpoint_and_attributes_observations():
    from scripts.sera_u_step_profile import instrument
    mind = entity(False, False)
    reads, operations = [], {}
    with instrument(mind, reads, operations):
        # live() checkpoints before work; no local profiler closure may be saved.
        mind.dumps()
        with mind.scope(), torch.no_grad():
            mind.engine._u_reads([public()])
    assert sum(r['records_observed'] for r in reads) == len(memory_records(public()))
    assert any(r['caller'] == 'mind.py:_u_reads' for r in reads)
    assert 'observe' in operations and 'conditional' in operations
