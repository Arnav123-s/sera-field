"""US: short, one-thread CPU parity, padding, shared credit and exact restart."""
import copy
from dataclasses import replace
import math

import numpy as np
import pytest
import torch

from sera import lang as LG, one as ONE, phi as PH, tasks as TS
from sera_u import SeraU
from sera_u.field.native_owner import NativeConfig
from sera_u.mind import U2_CRUTCHES, arm_settings
from sera_u.ports import TaskView
from sera_u.proposer import FieldOwner
from sera_u.sleep import Receipt, program_log_probability, program_log_probabilities


@pytest.fixture(autouse=True)
def deterministic(monkeypatch):
    torch.set_num_threads(1)
    torch.manual_seed(3)
    LG.forget_searches()
    monkeypatch.setattr(LG, 'DEADLINE', [math.inf])
    yield
    LG.forget_searches()


def program():
    return LG.node('add', LG.node('var', payload='x'), LG.node('one'))


def view():
    return TaskView((('x', 'num'),), 'num',
                    tuple((((('x', x),)), x+1) for x in (-2, 0, 1, 4)))


def entity(*, batched_reads=True, u2=False, **switches):
    crutches = {**arm_settings('full'), **{k: u2 for k in U2_CRUTCHES}, **switches}
    return SeraU(3, config=NativeConfig(nodes=3, rounds=1), crutches=crutches,
                 batched_reads=batched_reads)


def admit(mind, shown=None, *, source='fixture', origin='taught'):
    receipt = Receipt.make(view() if shown is None else shown, (program(),), {},
                           scope='dream-self-task' if origin == 'dream' else 'exact-audit',
                           origin=origin, source=source)
    # Explicit derivative fixture, as in preflight; no experimental teaching evidence.
    if origin != 'dream':
        mind.checked_wake.add(receipt.id)
    mind.sleep.admit(receipt, {})
    return receipt


def exact(a, b):
    if isinstance(a, torch.Tensor):
        assert torch.equal(a, b)
    elif isinstance(a, np.ndarray):
        np.testing.assert_array_equal(a, b)
    elif isinstance(a, dict):
        assert a.keys() == b.keys()
        for key in a:
            exact(a[key], b[key])
    elif isinstance(a, (list, tuple)):
        assert len(a) == len(b)
        for x, y in zip(a, b):
            exact(x, y)
    else:
        assert a == b


def close(a, b):
    # Float32 GEMM/reductions and multi-RHS solves can round differently by batch size. A few float32 steps relative
    # to the value as well: on Colab's AMD EPYC (2026-10-02) the batched loss 7.3562975 against 7.3562989 differed by
    # 1.43e-6 absolute, 1.9e-7 relative (float32 resolves 1.2e-7), which a pure 1e-6 absolute bound refuses.
    torch.testing.assert_close(a, b, atol=1e-6, rtol=1e-6)


TIMED = {'wall', 'cpu', 'timing', 'thinking_wall', 'thinking_cpu', 'finish_cpu', 'peak_mb', 'peak_mb_by', 'gain_rate',
         'load_wall', 'memory_mb', 'phases'}


def close_learning(a, b):
    """Two entities' learned state across execution paths: floats within close()'s rounding, everything else exact.
    (Bit-identical hashes hold within one path; batched and single reads may round differently on other CPUs.)"""
    def walk(x, y):
        if isinstance(x, torch.Tensor) and x.is_floating_point():
            close(x, y)
        elif isinstance(x, np.ndarray) and x.dtype.kind == 'f':
            np.testing.assert_allclose(x, y, rtol=1e-5, atol=1e-6)
        elif isinstance(x, (torch.Tensor, np.ndarray)):
            exact(x, y)
        elif isinstance(x, np.random.Generator):
            assert x.bit_generator.state == y.bit_generator.state
        elif isinstance(x, (PH.Field, PH.Ideas)):
            sx, sy = x.__getstate__(), y.__getstate__()
            walk({k: v for k, v in sx.items() if k != 'gen'}, {k: v for k, v in sy.items() if k != 'gen'})
        elif isinstance(x, dict):
            assert x.keys() == y.keys()
            for key in x:
                if key not in TIMED:                 # measurements, e.g. the Field log's wall seconds
                    walk(x[key], y[key])
        elif isinstance(x, (list, tuple)):
            assert len(x) == len(y)
            for p, q in zip(x, y):
                walk(p, q)
        elif hasattr(x, '__dict__') and not isinstance(x, type):
            walk(vars(x), vars(y))
        else:
            assert x == y
    pa, pb = a._payload(), b._payload()
    for key in ('owner', 'optimizer', 'field', 'state', 'token_ids', 'production_ids', 'checked_wake', 'updates'):
        walk(pa[key], pb[key])


@pytest.mark.parametrize('ports', [True, False])
@pytest.mark.parametrize('grow', [True, False])
def test_batch_rows_equal_singles_with_padding_and_retained_state(ports, grow):
    single = FieldOwner(NativeConfig(nodes=3, rounds=1))
    batch = copy.deepcopy(single)
    single.port_enabled = batch.port_enabled = ports
    views = [replace(view(), examples=()),
             replace(view(), queries=((('x', 6),),), words=('heard',)),
             TaskView((('x', 'list'),), 'list',
                      tuple(((('x', xs),), tuple(reversed(xs))) for xs in ((2, -2, 0),)))]
    with torch.no_grad():
        initial, _ = single.observe(single.empty(1), single.encode_texts(['retained history']))
        # Preserve identical starting dictionaries, including grow=False byte fallback.
        batch.token_ids = dict(single.token_ids)
        originals = {k: v.clone() for k, v in initial.items()}
        ring = torch.linspace(-.01, .01, 2048) if ports else None
        expected = [single.task_features(v, grow=grow, state=initial, ring=ring) for v in views]
        got = batch.task_features_many(views, grow=grow, states=[initial]*len(views),
                                       rings=[ring]*len(views))
    assert single.token_ids == batch.token_ids
    exact(initial, originals)
    for shown, a, b in zip(views, expected, got):
        close(a[0], b[0])
        close(a[1], b[1])
        for key in a[2]:
            if a[2][key].is_floating_point():
                close(a[2][key], b[2][key])
            else:
                exact(a[2][key], b[2][key])
        assert b[2]['events'].item() == initial['events'].item()+(len(shown.records()) if ports else 1)


@pytest.mark.parametrize('u2', [False, True])
def test_batched_mean_loss_and_input_core_readout_gradients_match_single_steps(u2):
    old, new = entity(batched_reads=False, u2=u2), entity(u2=u2)
    shown = replace(view(), queries=((('x', 7),),), words=('longer',))
    rows = [(view(), (program(), program()), {}),
            (shown, (program(),), {}), (view(), (program(),), {})]
    for mind, batching in ((old, False), (new, True)):
        with mind.scope():
            if u2:
                mind.memory.begin(replace(view(), examples=()))
            mind.optimizer.zero_grad(set_to_none=True)
            if batching:
                reads = mind.proposer.features_many([v for v, _, _ in rows], [c for _, _, c in rows])
                loss = -torch.stack([program_log_probability(mind.proposer, v, ps, c, read=read)
                                     for (v, ps, c), read in zip(rows, reads)]).mean()
            else:
                reads = [None]*len(rows)
                loss = -program_log_probabilities(mind.proposer, rows, batched_reads=False).mean()
            if u2:
                loss = loss+torch.stack([mind.memory.checked_loss(v, LG.parts(program()), read=read)
                                        for (v, _, _), read in zip(rows, reads)]).mean()
            if batching:
                close(old_loss, loss)
            else:
                old_loss = loss.detach()
            loss.backward()
    assert old.owner.token_ids == new.owner.token_ids
    assert old.owner.production_ids == new.owner.production_ids
    assert old.owner.understanding_ids == new.owner.understanding_ids
    for name in ('words.weight', 'core.links', 'production_query.weight'):
        a, b = dict(old.owner.named_parameters())[name], dict(new.owner.named_parameters())[name]
        assert a.grad is not None and b.grad is not None
        assert a.grad.abs().sum() > 0
        close(a.grad, b.grad)


def test_training_reads_each_view_once_and_shares_understanding_credit(monkeypatch):
    mind = entity(u2=True)
    admit(mind)
    admit(mind, replace(view(), words=('second',)), source='second')
    counts = []
    original = mind.owner.task_features_many
    def record(views, **kwargs):
        counts.append(tuple(views))
        return original(views, **kwargs)
    monkeypatch.setattr(mind.owner, 'task_features_many', record)
    def unexpected(*args, **kwargs):
        raise AssertionError('A cached batch view was reread')
    monkeypatch.setattr(mind.owner, 'task_features', unexpected)
    mind.train(1, 8)
    assert len(counts) == 1 and len(counts[0]) == len(set(counts[0])) <= 2


@pytest.mark.parametrize('batching', [False, True])
def test_determinism_checkpoint_then_next_update_is_exact(batching, tmp_path):
    a, b = entity(batched_reads=batching, u2=True), entity(batched_reads=batching, u2=True)
    for mind in (a, b):
        admit(mind)
        admit(mind, replace(view(), words=('other',)), source='other')
        mind.train(1, 2)
    exact(a.owner.state_dict(), b.owner.state_dict())
    exact(a.optimizer.state_dict(), b.optimizer.state_dict())
    assert a.learning_hash() == b.learning_hash()
    checkpoint = tmp_path/'speed.pt'
    a.save(checkpoint)
    resumed = SeraU.load(checkpoint)
    assert resumed.batched_reads is batching
    for mind in (a, resumed):
        mind.train(1, 2)
    exact(a.owner.state_dict(), resumed.owner.state_dict())
    exact(a.optimizer.state_dict(), resumed.optimizer.state_dict())
    exact(a.state, resumed.state)
    exact(a.rngs, resumed.rngs)
    assert a.learning_hash() == resumed.learning_hash()
    assert not a.proposer._feature_cache and not resumed.proposer._feature_cache


def test_dream_diagnostic_batches_independent_views_without_factual_credit():
    a, b = entity(batched_reads=False), entity()
    for mind in (a, b):
        admit(mind, origin='dream')
        admit(mind, replace(view(), queries=((('x', 5),),)), origin='dream', source='other')
    before = copy.deepcopy(b.state)
    with a.scope(), torch.no_grad():
        expected = a.sleep.check_dreams()
    with b.scope(), torch.no_grad():
        got = b.sleep.check_dreams()
    close(expected, got)
    exact(before, b.state)
    assert b.updates == 0 and len(b.sleep.consumed) == 2


def test_assessment_preparation_preserves_each_clone_vocabulary_state_and_memory(monkeypatch):
    base = entity(u2=True)
    shown = [view(), replace(view(), words=('new token',), queries=((('x', 99),),),
                             measurements=(('m', 1), ('m', 2), ('m', 1)))]
    expected = [SeraU.loads(base.dumps()) for _ in shown]
    got = [SeraU.loads(base.dumps()) for _ in shown]
    reads = []
    for mind, v in zip(expected, shown):
        with mind.scope(), torch.no_grad():
            mind.memory.begin(v)
            reads.append(mind.memory.features(v))
    SeraU._prepare_assessments(got, shown)
    for a, b, v, read in zip(expected, got, shown, reads):
        assert a.owner.token_ids == b.owner.token_ids
        for key in a.state:
            if a.state[key].is_floating_point():
                close(a.state[key], b.state[key])
            else:
                exact(a.state[key], b.state[key])
        assert a.field.ideas._row == b.field.ideas._row
        np.testing.assert_array_equal(a.field.ideas._M[:a.field.ideas._n], b.field.ideas._M[:b.field.ideas._n])
        np.testing.assert_array_equal(a.field.ideas._E[:a.field.ideas._n], b.field.ideas._E[:b.field.ideas._n])
        cached = b.memory._feature_cache[(v, True)]
        close(read[0], cached[0])
        close(read[1], cached[1])
        with b.scope(), torch.no_grad():
            # Prepared begin neither adds events nor erases the prepared read.
            events = b.state['events'].clone()
            b.memory.begin(v)
            exact(events, b.state['events'])
            assert b.memory.features(v) is cached
            # A symbolic-only alias write must not leave an old ringing cached.
            changed_ring = b.memory.ring(v)+.001
            with monkeypatch.context() as patch:
                calls = []
                patch.setattr(b.memory, 'ring', lambda shown: changed_ring)
                def reread(shown, **kwargs):
                    calls.append(kwargs['ring'])
                    return cached
                patch.setattr(b.owner, 'task_features', reread)
                b.memory.features(v)
                assert len(calls) == 1 and calls[0] is changed_ring
                assert not b.memory._feature_cache
            b.memory.event('new evidence', 1)
            assert not b.memory._feature_cache and not b.proposer._feature_cache


def test_batching_off_training_matches_explicit_pre_us_step(monkeypatch):
    old, reference = entity(batched_reads=False, u2=True), entity(batched_reads=False, u2=True)
    receipt = admit(old)
    admit(reference)
    def forbidden(*args, **kwargs):
        raise AssertionError('batched_reads=False entered the batch path')
    monkeypatch.setattr(old.owner, 'task_features_many', forbidden)
    with reference.scope():
        reference.optimizer.zero_grad(set_to_none=True)
        programs, understanding = [], []
        for _ in range(2):
            programs.append(-program_log_probability(reference.proposer, receipt.view, receipt.targets, {}))
            understanding.append(reference.memory.checked_loss(receipt.view, LG.parts(program())))
        ploss, uloss = torch.stack(programs).mean(), torch.stack(understanding).mean()
        loss = ploss+uloss
        loss.backward()
        norm = float(torch.nn.utils.clip_grad_norm_(reference.owner.parameters(), 1., error_if_nonfinite=True))
        reference.optimizer.step()
        reference.updates += 1
        reference.proposer.changed()
    row = old.train(1, 2)[0]
    assert row['program'] == float(ploss.detach())
    assert row['understanding'] == float(uloss.detach())
    assert row['objective'] == float(loss.detach()) and row['clip_input_norm'] == norm
    exact(old.owner.state_dict(), reference.owner.state_dict())
    exact(old.optimizer.state_dict(), reference.optimizer.state_dict())


def logical(value):
    # Wall/CPU/process-memory measurements cannot be identical between trials.
    omitted = {'wall', 'cpu', 'timing', 'thinking_wall', 'thinking_cpu', 'finish_cpu',
               'peak_mb', 'peak_mb_by', 'gain_rate', 'load_wall', 'search', 'inference', 'proposal',
               'judge', 'memory_mb'}
    if isinstance(value, dict):
        return {k: logical(v) for k, v in value.items() if k not in omitted}
    if isinstance(value, (tuple, list)):
        return type(value)(logical(v) for v in value)
    return value


def test_batching_off_u2_wake_and_assessment_records_keep_single_path(monkeypatch):
    monkeypatch.setattr(ONE.time, 'process_time', lambda: 0.)
    task = TS.Exact('math', 'identity', lambda x: x, {'x': 'num'}, 'num', [-2, 0, 1, 4],
                    [], lambda rng: int(rng.integers(-8, 9)))
    old, new = entity(batched_reads=False, u2=True, field_proposer=False), entity(u2=True, field_proposer=False)
    old_rec = old.live(copy.deepcopy(task), task_wall=math.inf, max_steps=0)
    new_rec = new.live(copy.deepcopy(task), task_wall=math.inf, max_steps=0)
    assert logical(old_rec) == logical(new_rec)
    close_learning(old, new)              # the two read paths may round differently on other CPUs
    # Off must call the original single assessment seam, even for several tasks.
    calls = []
    def single(task, **kwargs):
        calls.append(task)
        return {'task': task.name}
    monkeypatch.setattr(old, 'assess', single)
    assert list(old.assess_many([task, task])) == [{'task': 'identity'}]*2
    assert calls == [task, task]

def test_batched_assessment_keeps_trial_records_and_base_learning_isolated(monkeypatch):
    monkeypatch.setattr(ONE.time, 'process_time', lambda: 0.)
    task = TS.Exact('math', 'identity', lambda x: x, {'x': 'num'}, 'num', [-2, 0, 1, 4],
                    [], lambda rng: int(rng.integers(-8, 9)))
    old = entity(batched_reads=False, u2=True, field_proposer=False)
    new = entity(u2=True, field_proposer=False)
    before = new.learning_hash()
    expected = [old.assess(copy.deepcopy(task), task_wall=math.inf, max_steps=0) for _ in range(2)]
    got = list(new.assess_many([copy.deepcopy(task), copy.deepcopy(task)],
                               task_wall=math.inf, max_steps=0))
    assert logical(expected) == logical(got)
    assert new.learning_hash() == before == old.learning_hash()
