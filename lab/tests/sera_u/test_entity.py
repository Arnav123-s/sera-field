"""Short CPU contracts for the U1 entity and S28's six engineering groups."""
import copy
from dataclasses import replace
import io
import math
import os
from pathlib import Path
import random
import sys
import time

import numpy as np
import pytest
import torch

from sera import crutches as CR, lang as LG, one as ONE, phi as PH, tasks as TS
from sera_u import SeraU
from sera_u.field.core_owner import CoreOwner
from sera_u.field.native_owner import NativeConfig
from sera_u.mind import ARMS, U3_CRUTCHES, U6_CRUTCHES, U7_CRUTCHES, AssessmentTask, arm_settings
from sera_u.ports import TaskView, PortBudget
from sera_u.proposer import FieldOwner, Proposer
from sera_u.sleep import Receipt, independent, family, program_log_probability


@pytest.fixture(autouse=True)
def deterministic(monkeypatch):
    torch.set_num_threads(1)
    torch.manual_seed(3)
    LG.forget_searches()
    monkeypatch.setattr(LG, 'DEADLINE', [math.inf])
    yield
    LG.forget_searches()


def example_view():
    return TaskView((('x', 'num'),), 'num', tuple((((('x', x),)), x+1) for x in (-2, 0, 1, 4)),
                    queries=((('x', 6),),))


def program():
    return LG.node('add', LG.node('var', payload='x'), LG.node('one'))


def qualified(mind):
    # A real independent audit qualifies this explicit test fixture. Production
    # code accepts wake receipts only through its bound live-task seam.
    task = TS.Exact('math', 'fixture', lambda x: x+1, {'x': 'num'}, 'num', [-2, 0, 1, 4],
                    [], lambda rng: int(rng.integers(-8, 9)))
    assert task.verify(program(), {}, LG.bits(program(), []), np.random.default_rng(3))[0]
    receipt = Receipt.make(example_view(), (program(),), {}, scope='exact-audit', origin='taught', source='fixture')
    mind.checked_wake.add(receipt.id)
    mind.sleep.admit(receipt, {})
    return receipt


def assert_nested_equal(a, b):
    if isinstance(a, torch.Tensor):
        assert torch.equal(a.cpu(), b.cpu())
    elif isinstance(a, np.ndarray):
        np.testing.assert_array_equal(a, b)
    elif isinstance(a, dict):
        assert a.keys() == b.keys()
        for key in a:
            assert_nested_equal(a[key], b[key])
    elif isinstance(a, (tuple, list)):
        assert len(a) == len(b)
        for x, y in zip(a, b):
            assert_nested_equal(x, y)
    else:
        assert a == b


def test_pinned_copy_matches_original_outputs_and_gradients():
    pinned_source = os.environ.get('SERA_FIELD_PINNED_SOURCE')
    if not pinned_source:
        pytest.skip('Set SERA_FIELD_PINNED_SOURCE to the read-only pinned original')
    source = Path(pinned_source)
    if not (source/'sera_field/core_owner.py').exists():
        pytest.skip('Read-only pinned original unavailable on this machine')
    sys.path.insert(0, str(source))
    bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        from sera_field.core_owner import CoreOwner as Original
        from sera_field.native_owner import NativeConfig as OriginalConfig
        torch.manual_seed(91)
        copied = CoreOwner(NativeConfig(nodes=4, rounds=1))
        torch.manual_seed(91)
        original = Original(OriginalConfig(nodes=4, rounds=1))
        assert_nested_equal(copied.state_dict(), original.state_dict())
        for owner in (copied, original):
            semantic = owner.semantic(['one actual observation'], ['another question'])
            support = torch.tensor([[[.2, -.3, .4], [.1, .2, -.1]]])
            physical = owner.physical(support, torch.tensor([[[.4, -.2]]]))
            owner.zero_grad(set_to_none=True)
            (semantic.square().sum()+physical.square().sum()).backward()
            owner._parity_outputs = (semantic.detach(), physical.detach())
        assert_nested_equal(copied._parity_outputs, original._parity_outputs)
        for (name, p), (other_name, q) in zip(copied.named_parameters(), original.named_parameters()):
            assert name == other_name
            assert (p.grad is None) == (q.grad is None)
            if p.grad is not None:
                assert torch.equal(p.grad, q.grad), name
    finally:
        sys.dont_write_bytecode = bytecode
        sys.path.remove(str(source))


# S28 group 1: teacher/observer isolation.
def test_hidden_targets_names_answers_and_grades_never_change_neural_inputs():
    task = TS.number_task('hidden name', lambda x: x+1, 3, 0)
    view = TaskView.from_task(task)
    task.name, task.subject = 'unrelated answer name', 'unrelated subject'
    task._target = lambda x: 999
    task._truth_words = {'hidden-answer'}
    task.grade = lambda *a, **k: {'verdict': 'SURE AND WRONG'}
    assert view == TaskView.from_task(task)
    owner = FieldOwner(NativeConfig(nodes=3, rounds=1))
    proposer = Proposer(owner, PH.Field(3))
    with torch.no_grad():
        a, wa, _ = owner.task_features(view)
        b, wb, _ = owner.task_features(TaskView.from_task(task))
        assert torch.equal(a, b) and torch.equal(wa, wb)
        assert proposer.beam(view, {}, nodes=3, width=4) == proposer.beam(TaskView.from_task(task), {}, nodes=3, width=4)


def test_example_permutation_is_invariant_and_list_order_is_visible():
    owner = FieldOwner(NativeConfig(nodes=3, rounds=1))
    view = TaskView((('x', 'list'),), 'list', (((('x', (1, 2)),), (2, 1)), ((('x', ()),), ())))
    assert view.records() == replace(view, examples=tuple(reversed(view.examples))).records()
    changed = replace(view, examples=(((('x', (2, 1)),), (2, 1)), ((('x', ()),), ())))
    assert view.records() != changed.records()
    with torch.no_grad():
        assert torch.equal(owner.task_features(view)[0], owner.task_features(replace(view, examples=tuple(reversed(view.examples))))[0])


def test_assessment_cannot_learn_from_audit_counterexample():
    task = TS.number_task('hidden', lambda x: x+1, 3, 0)
    wrapper = AssessmentTask(task)
    before = copy.deepcopy(wrapper.data)
    assert not wrapper.verify(LG.node('zero'), {}, 3, np.random.default_rng(3))[0]
    assert wrapper.data == before and wrapper.actions() == []
    assert wrapper.grade(LG.node('zero'), {}, True) == {'verdict': 'proven right'}
    # a proof it names in its own words records its false words without a teacher (the U2 pilot's crash, 2026-10-02)
    assert wrapper.teacher_truth('w') is False is task.teacher_truth('w')


def test_assessment_leaves_entity_learning_state_unchanged(monkeypatch):
    monkeypatch.setattr(ONE, 'MAX_WALL', .25)
    mind = SeraU(3, arm='no-proposer', config=NativeConfig(nodes=3, rounds=1))
    before = mind.learning_hash()
    row = mind.assess(TS.number_task('tiny', lambda x: x, 3, 0), task_wall=.25, max_steps=1)
    assert row['before'] == row['after'] == before == mind.learning_hash()


# S28 group 2: stable growing vocabulary and typed/bounded values.
def test_concept_rename_reorder_growth_unknown_and_unproven_ids():
    field = PH.Field(3)
    body = LG.node('add', LG.node('var', payload='_'), LG.node('one'))
    first = field.invent(body, ('num', 'num'), 'math', 'checked', LG.parts(body))
    second = field.invent(LG.node('mul', LG.node('var', payload='_'), LG.node('var', payload='_')),
                          ('num', 'num'), 'math', 'checked', ())
    proposer = Proposer(FieldOwner(NativeConfig(nodes=3, rounds=1)), field)
    prior = proposer.prior(example_view(), field.concept_table())
    revision = field.library_revision()
    first['name'] = 'renamed'
    field.concepts.reverse()
    assert revision == field.library_revision()
    assert proposer.prior(example_view(), field.concept_table()) == prior
    new = field.invent(LG.node('sub', LG.node('var', payload='_'), LG.node('one')),
                       ('num', 'num'), 'math', 'checked', ())
    assert ('c', new['id']) in proposer.prior(example_view(), field.concept_table())
    assert first['id'] != second['id'] != new['id']
    with pytest.raises(ValueError):
        proposer.concepts({'_sig': {1234: ('num', 'num')}})
    wished = field.invent(body, ('num', 'num'), 'math', 'unproven (wished)', ())
    with pytest.raises(ValueError, match='Unproven'):
        proposer.concepts(field.concept_table())
    field.audited_by(wished['id'], 'audit')
    proposer.concepts(field.concept_table())


@pytest.mark.parametrize('value', [(), ((), (1,)), True, None, 0, -3, 1.25])
def test_nested_empty_boolean_missing_real_and_exact_numeric_senses(value):
    view = TaskView((('x', 'list(list)'),), 'num', (((('x', value),), 0),))
    assert view.records()


def test_port_overflow_and_byte_fallback_are_explicit():
    with pytest.raises(PortBudget):
        TaskView((('x', 'list'),), 'num', (((('x', tuple(range(9))),), 0),)).records()
    owner = FieldOwner(NativeConfig(nodes=3, rounds=1))
    owner.token_ids = {str(j): j+257 for j in range(owner.words.num_embeddings-257)}
    assert owner.token_indices('new word') == [b+1 for b in b'new word']
    with pytest.raises(PortBudget):
        owner.encode_record((('x'*257, 0., 0., 1.),))


def test_captured_lambda_nested_lists_and_words_are_not_python(tmp_path):
    p = LG.node('map', LG.node('lam', LG.node('add', LG.node('var', payload='e'),
                                             LG.node('head', LG.node('var', payload='x'))), payload='e'),
                LG.node('var', payload='x'))
    assert LG.infer(p, {}, arg='x') == ('list', 'list')
    assert independent(p, {'x': (2, 5)}, {}) == LG.evaluate(p, {'x': (2, 5)}, {}) == (4, 7)
    marker = tmp_path/'executed'
    view = replace(example_view(), words=(f"__import__('pathlib').Path('{marker}').touch()",))
    FieldOwner(NativeConfig(nodes=3, rounds=1)).task_features(view)
    assert not marker.exists()
    with pytest.raises(ValueError):
        independent(('c', 99, LG.node('one')), {}, {99: (('c', 99, LG.node('one')), '_')})


# S28 group 3: internal scheduling, persistent fallback and truthful completion.
def exhaust(order=None, namespace=None, chunk=None):
    found = []
    for work in range(1, 300):
        found = LG.search({'x': 'real'}, 'real', [{'x': -.25}, {'x': 2.}], 3,
                          work=work, order=order, namespace=namespace, chunk=chunk)
        if LG.COMPLETE[0]:
            return found
    pytest.fail('Tiny exhaustive search did not complete')


def test_internal_order_changes_first_candidate_but_not_complete_behaviors():
    ordinary = exhaust(namespace='old')
    preferred = exhaust({('rmul', None): 100.}, 'learned', chunk=3)
    values = lambda rows: {tuple(LG.evaluate(p, {'x': x}, {}) for x in (-.25, 2.)) for p, _ in rows}
    assert values(ordinary) == values(preferred)
    assert len(LG._TABLES) >= 2


def test_reordered_lambda_bodies_keep_their_own_captured_inputs(monkeypatch):
    monkeypatch.setattr(LG, 'INNATE', {k: LG.INNATE[k] for k in ('map', 'mapi')})
    e = LG.node('var', payload='e')
    body_x = LG.node('add', e, LG.node('head', LG.node('var', payload='x')))
    body_y = LG.node('add', e, LG.node('head', LG.node('var', payload='y')))
    lambdas = [('map', body_x, LG.size(body_x), ('list',), 'list', ('x',)),
               ('mapi', body_y, LG.size(body_y), ('list',), 'list', ('y',))]
    leaves = [('list', LG.node('var', payload=k)) for k in ('x', 'y')]
    envs = [dict(x=(1, 2), y=(10, 20))]
    def behaviors(order, namespace):
        rows = LG._grow(leaves, envs, 7, {}, lambdas=lambdas,
                        types=LG.universe(['list']), work=1000, order=order, namespace=namespace)
        assert LG.COMPLETE[0]
        return {tuple(values) for _, _, values in rows['list']}
    ordinary = behaviors(None, 'captures-old')
    reordered = behaviors({('mapi', None): 10.}, 'captures-ordered')
    assert ordinary == reordered
    assert ((11, 12),) in reordered and ((20, 30),) in reordered


def test_lambda_chunks_resume_and_cache_policy_inputs_library_invalidate(monkeypatch):
    rows = []
    for work in range(1, 100):
        rows = LG.lambda_bodies('e', 'num', 3, work=work, chunk=1, namespace='lambda')
        if LG.COMPLETE[0]:
            break
    assert LG.COMPLETE[0] and any(p[0] == 'mul' for p, _ in rows)
    count = len(LG._TABLES)
    LG.lambda_bodies('e', 'num', 3, work=200, order={('mul', None): 5.}, namespace='lambda')
    assert len(LG._TABLES) > count
    count = len(LG._TABLES)
    LG.search({'x': 'real'}, 'real', [{'x': 99.}], 3, work=1)
    assert len(LG._TABLES) > count
    LG.DEADLINE[0] = -math.inf
    LG.search({'x': 'real'}, 'real', [{'x': 102.}], 3, work=20)
    assert not LG.COMPLETE[0]
    LG.DEADLINE[0] = math.inf
    monkeypatch.setattr(LG, '_over_memory', lambda: True)
    LG.search({'x': 'real'}, 'real', [{'x': 103.}], 20, work=100_000)
    assert not LG.COMPLETE[0]


def test_early_frontier_is_visible_before_full_enumeration_and_fallback_runs():
    mind = SeraU(3, config=NativeConfig(nodes=3, rounds=1))
    view = TaskView((('x', 'real'),), 'real', queries=((('x', 2.),), (('x', -1.),)))
    chunks = mind.proposer.chunks(view, {'x': 'real'}, 'real', [dict(q) for q in view.queries],
                                 3, {}, deadline=time.time()+10, chunk=1, lambda_size=1)
    first = next(chunks)
    assert first and not LG.COMPLETE[0]
    # This is the judge's early seam: execute/accept a frontier before next(chunk).
    assert any(LG.evaluate(p, {'x': 2.}, {}) == 2. for p, _, _ in first)
    for _ in chunks:
        pass
    cursor = next(iter(mind.proposer.cursors.values()))
    assert cursor['fallback'] > 0 and cursor['preferred'] > 0
    assert cursor['done']['fallback'] and cursor['done']['preferred']


# S28 group 4: independently checked dreams/replay and provenance/scope.
def test_replay_scope_corruption_duplicates_alias_marginal_and_reserved_families():
    mind = SeraU(3, config=NativeConfig(nodes=3, rounds=1))
    receipt = qualified(mind)
    with pytest.raises(ValueError, match='Duplicate'):
        mind.sleep.admit(receipt, {})
    with pytest.raises(ValueError, match='Corrupted'):
        replace(receipt, id='forged').check({})
    with pytest.raises(ValueError, match='Reserved'):
        receipt.check({}, reserved=(family(program(), {}),))
    with pytest.raises(ValueError):
        Receipt.make(receipt.view, (program(),), {}, scope='curve-only', origin='alone', source='rail')
    with torch.no_grad():
        a = program_log_probability(mind.proposer, receipt.view, (program(),), {})
        b = program_log_probability(mind.proposer, receipt.view, (program(), program()), {})
    assert torch.equal(a, b)
    assert replace(receipt, view=replace(receipt.view, examples=(((('x', 1),), 999),))).id == receipt.id
    with pytest.raises(ValueError):
        replace(receipt, view=replace(receipt.view, examples=(((('x', 1),), 999),))).check({})


def test_a_dream_the_port_cannot_carry_is_skipped_not_a_stop(monkeypatch):
    # A dream's own outputs can outgrow the port (a list longer than eight): its receipt is refused and the dream is
    # skipped like any failed attempt (the U2 A/B's memory-off case stopped on "A list exceeds length eight", 2026-10-02).
    import sera_u.sleep as SL
    mind = SeraU(3, config=NativeConfig(nodes=3, rounds=1))
    qualified(mind)
    count_up = LG.node('range', LG.node('var', payload='x'))
    view = TaskView((('x', 'num'),), 'list', tuple((((('x', x),)), tuple(range(1, x+1))) for x in (1, 2, 3, 9)))
    with pytest.raises(PortBudget):
        Receipt.make(view, (count_up,), {}, scope='dream-self-task', origin='dream', source='dream:fixture')

    def too_long(*args, **kwargs):
        raise PortBudget('A list exceeds length eight')
    monkeypatch.setattr(SL.Receipt, 'make', too_long)
    assert mind.sleep.dream(2, attempts=10) == [] and not mind.sleep.dreams
    monkeypatch.undo()                                # an input type it cannot sample: also a failed attempt
    def unsupported(*args, **kwargs):
        raise ValueError('Unsupported dream input type')
    monkeypatch.setattr(SL, 'sample_input', unsupported)
    assert mind.sleep.dream(2, attempts=10) == [] and not mind.sleep.dreams


def test_executable_dreams_are_not_factual_observations_and_no_dreams_has_none():
    mind = SeraU(3, config=NativeConfig(nodes=3, rounds=1))
    qualified(mind)
    before = copy.deepcopy(mind.state)
    made = mind.sleep.dream(2, attempts=10)
    assert made
    for receipt in made:
        assert receipt.scope == 'dream-self-task' and receipt.origin == 'dream'
        receipt.check({})
    assert_nested_equal(before, mind.state)
    mind.crutches['program_dreams'] = False
    assert mind.sleep.dream(2) == []


# S28 group 5: shared-owner learning and exact checkpoint/RNG/optimizer restart.
def test_one_batch_reaches_input_core_readout_and_replay_earns_no_new_credit():
    mind = SeraU(3, config=NativeConfig(nodes=3, rounds=1))
    qualified(mind)
    evidence = len(mind.sleep.consumed)
    logs = mind.train(1, 2)
    assert logs[0]['parameter_change'] > 0
    assert all(value > 0 for value in logs[0]['gradient'].values())
    assert logs[0]['portfolio_credit'] == 0 and len(mind.sleep.consumed) == evidence


def test_save_load_exact_next_update_and_every_rng(tmp_path):
    mind = SeraU(3, config=NativeConfig(nodes=3, rounds=1))
    qualified(mind)
    mind.train(1, 2)
    path = tmp_path/'mind.pt'
    mind.save(path)
    reference = SeraU.load(path)
    assert mind.learning_hash() == reference.learning_hash()
    for entity in (mind, reference):
        entity.train(1, 2)
    assert_nested_equal(mind.owner.state_dict(), reference.owner.state_dict())
    assert_nested_equal(mind.optimizer.state_dict(), reference.optimizer.state_dict())
    assert_nested_equal(mind.rngs, reference.rngs)
    assert mind.random.random() == reference.random.random()
    np.testing.assert_array_equal(mind.numpy.normal(size=4), reference.numpy.normal(size=4))
    assert torch.equal(torch.rand(4, generator=mind.torch_generator), torch.rand(4, generator=reference.torch_generator))
    blob = torch.load(path, weights_only=False)
    blob['payload'] += b'corruption'
    stream = io.BytesIO()
    torch.save(blob, stream)
    with pytest.raises(ValueError, match='Corrupt'):
        SeraU.loads(stream.getvalue())


@pytest.mark.skipif(not torch.cuda.is_available(), reason='GPU derivative/device preflight on Colab only')
@pytest.mark.parametrize('batch', [1, 8])
def test_gpu_device_complex_branches_echo_and_cpu_loss_agreement(batch):
    cpu = SeraU(3, config=NativeConfig(nodes=3, rounds=1))
    gpu = SeraU(3, device='cuda', config=NativeConfig(nodes=3, rounds=1))
    gpu.owner.load_state_dict(cpu.owner.state_dict())
    a = -program_log_probability(cpu.proposer, example_view(), (program(),), {})
    b = -program_log_probability(gpu.proposer, example_view(), (program(),), {})
    assert torch.allclose(a, b.cpu(), atol=2e-4, rtol=2e-4)
    a.backward(); b.backward()
    for name in ('core.links', 'words.weight', 'production_query.weight'):
        pa = dict(cpu.owner.named_parameters())[name]
        pb = dict(gpu.owner.named_parameters())[name]
        assert torch.allclose(pa.grad, pb.grad.cpu(), atol=5e-4, rtol=5e-3)
    with torch.no_grad():
        texts = ['a question']*batch
        logits = gpu.owner.semantic(texts, texts)
        assert logits.device.type == 'cuda' and bool(torch.isfinite(logits).all())
        state = gpu.owner.empty(batch)
        _, diagnostics = gpu.owner.conditional(state, gpu.owner.encode_texts(texts))
        assert diagnostics['density'].is_complex() and diagnostics['density'].device.type == 'cuda'


def test_search_cursor_restores_frontier_without_serializing_generators():
    mind = SeraU(3, config=NativeConfig(nodes=3, rounds=1))
    view = TaskView((('x', 'real'),), 'real', queries=((('x', 2.),),))
    def chunks(entity):
        return entity.proposer.chunks(view, {'x': 'real'}, 'real', [{'x': 2.}], 3, {},
                                      deadline=time.time()+10, chunk=1, lambda_size=1)
    generator = chunks(mind)
    next(generator)
    generator.close()
    restored = SeraU.loads(mind.dumps())
    reference_generator = chunks(mind)
    expected = next(reference_generator)
    reference_generator.close()
    actual_generator = chunks(restored)
    actual = next(actual_generator)
    actual_generator.close()
    assert expected == actual


# S28 group 6: arms, fixed denominator, no neural checkpoint for the old engine.
def test_all_control_masks_and_parameter_limit_are_explicit():
    assert all(not CR.REGISTRY[k]['default_on'] for k in arm_settings('full'))
    for arm in ARMS:
        mind = SeraU(3, arm=arm, config=NativeConfig(nodes=3, rounds=1))
        assert mind.proposer.enabled == arm_settings(arm)['field_proposer']
        assert mind.engine.library_enabled == arm_settings(arm)['sleep_library']
        assert sum(p.numel() for p in mind.owner.parameters()) <= 1_200_000
    old = ONE.Sera(3)
    assert old.proposer is None
    assert not any(k in CR.settings()['crutches_effective'] for k in arm_settings('full'))
    assert sum(p.numel() for p in SeraU(3).owner.parameters()) <= 1_200_000


def test_custom_crutch_ablation_round_trips_without_default_lab_switches():
    off = {name: False for name in arm_settings('full')}
    mind = SeraU(3, crutches=off, config=NativeConfig(nodes=3, rounds=1))
    restored = SeraU.loads(mind.dumps())
    # A U1/U2 mask normalizes to all U3, U6 and U7 switches off.
    assert restored.crutches == {**off, **{k: False for k in U3_CRUTCHES+U6_CRUTCHES+U7_CRUTCHES}} and not restored.owner.port_enabled
    with restored.scope():
        assert all(not CR.on(name) for name in off)
        assert not restored.engine.library_enabled and not restored.proposer.enabled


def test_source_manifest_matches_every_copy_and_declared_change():
    import hashlib
    import json
    root = Path(__file__).resolve().parents[2]/'sera_u/field'
    manifest = json.loads((root/'SOURCE.json').read_text(encoding='utf-8-sig'))
    assert manifest['commit'].startswith('c67ed27')
    assert len(manifest['files']) == 34
    assert {p.name for p in root.glob('*.py')} == {entry['path'] for entry in manifest['files']}
    for entry in manifest['files']:
        sha = hashlib.sha256((root/entry['path']).read_bytes()).hexdigest()
        assert sha == entry['vendored_sha256']
        assert entry['changed'] == (entry['source_sha256'] != sha)


def test_proposer_off_reproduces_old_tiny_exact_record(monkeypatch):
    monkeypatch.setattr(ONE, 'MAX_WALL', 10.)
    original = ONE.Sera(3)
    off = ONE.Sera(3, proposer=Proposer(FieldOwner(NativeConfig(nodes=3, rounds=1)), PH.Field(3), enabled=False))
    a = original.live(TS.number_task('identity', lambda x: x, 3, 0), teaching=True, max_steps=3)
    b = off.live(TS.number_task('identity', lambda x: x, 3, 0), teaching=True, max_steps=3)
    # Machine wall/CPU/allocator counters are measurements, not deterministic records.
    volatile = {'wall', 'cpu', 'timing', 'peak_mb', 'peak_mb_by', 'choices', 'tension',
                'thinking_wall', 'thinking_cpu', 'finish_cpu', 'gain_rate'}
    assert {k: v for k, v in a.items() if k not in volatile} == {k: v for k, v in b.items() if k not in volatile}


def test_report_missing_timeout_rows_score_zero_and_denominator_never_shrinks(tmp_path):
    from scripts.sera_u_rsi import report, write
    write(tmp_path/'state.json', dict(protocol=dict(eval_tasks=48, generations=3), stage='arms',
                                   retention_count=1, rows=[dict(arm='full', generation=0, suite='assessment',
                                                               task='h0', domain='num', solved=False, search=10.)]))
    result = report(tmp_path)
    assert result['curves']['full'][0]['N'] == 48 and result['curves']['full'][0]['g'] == 0
    assert result['missing_rows'] == 767 and not result['complete'] and not result['behavioral_signal']


def test_grown_view_is_a_recorded_miss_and_rollback_survives_a_changed_wall(monkeypatch):
    # A taught task can gain examples while it is lived (teacher or world); past the pilot port budget the proposer
    # steps aside and the unchanged search runs (S28 §2: a recorded budget miss, never a truncated view).
    mind = SeraU(3, config=NativeConfig(nodes=3, rounds=1))
    task = TS.Exact('math', 'grown', lambda x: x+1, {'x': 'num'}, 'num', [-2, 0, 1, 4, 5],
                    [], lambda rng: int(rng.integers(-8, 9)))
    with mind.scope():
        assert mind.proposer.preferred(task, {}, (1,)) == []
        assert mind.proposer.order_steps(task, [(program(), 1)], {}) == [(program(), 1)]
    assert mind.proposer.stats['budget_misses'] == 2
    # An error inside a lived task rolls back to the snapshot taken before it, even though live() had set the
    # task's own wall (a lab knob the exact-resume check compares); the task's own error is what surfaces.
    def fail(*args, **kwargs):
        raise PortBudget('fixture')
    monkeypatch.setattr(type(mind.engine), 'live', fail)
    before, wall = mind.learning_hash(), ONE.MAX_WALL
    with pytest.raises(PortBudget, match='fixture'):
        mind.live(TS.number_task('tiny', lambda x: x, 3, 0), task_wall=wall+1.)
    assert mind.learning_hash() == before and ONE.MAX_WALL == wall


def _proven_by_fixture(self, task, **kwargs):
    return dict(proven=True, answer=program(), verdict='proven right')


def test_a_wake_proof_on_a_reserved_family_is_never_replayed_and_the_run_goes_on(monkeypatch):
    # SERA's own proof of a wake task can land on a family the observer reserved for assessment (the U2 A/B's g1
    # wake, 2026-10-02): the receipt is refused for replay and the overlap recorded, instead of stopping the run.
    mind = SeraU(3, config=NativeConfig(nodes=3, rounds=1))
    monkeypatch.setattr(type(mind.engine), 'live', _proven_by_fixture)
    mind.sleep.reserved = {family(program(), {})}
    task = TS.Exact('math', 'wake', lambda x: x+1, {'x': 'num'}, 'num', [-2, 0, 1, 4],
                    [], lambda rng: int(rng.integers(-8, 9)))
    rec = mind.live(task)
    assert rec['reserved_overlap'] == [family(program(), {})]
    assert mind.sleep.replay == [] and not mind.sleep.consumed and not mind.checked_wake
    mind.sleep.reserved = set()                       # unreserved, the same proof is replayed
    rec = mind.live(task)
    assert 'reserved_overlap' not in rec and len(mind.sleep.replay) == 1
    three = TS.Exact('math', 'three examples', lambda x: x+1, {'x': 'num'}, 'num', [-2, 0, 1],
                     [], lambda rng: int(rng.integers(-8, 9)))
    rec = mind.live(three)                            # a proof on a view of three examples stands, without a label
    assert rec['receipt_skipped'].startswith('Pilot program receipts require four') and len(mind.sleep.replay) == 1


def test_observer_target_out_of_bounds_is_undefined_like_the_lab_executor():
    # An assessment world's value outside the independent interpreter's bounds is undefined (None), as LG.safe's is;
    # a candidate that is also out of bounds there agrees, and the pilot does not stop on the world's own limit.
    from scripts.sera_u_rsi import Target
    square = LG.node('mul', LG.node('var', payload='x'), LG.node('var', payload='x'))
    target = Target(square)
    assert target(7) == 49
    big = LG.MAX_INT
    assert target(big) is None
    assert LG.safe(square, {'x': big}, {}) is None
    count_up = LG.node('range', LG.node('var', payload='x'))   # past the longest list: undefined in both
    assert Target(count_up)(3) == (1, 2, 3)
    assert Target(count_up)(LG.MAX_LEN+1) is None is LG.safe(count_up, {'x': LG.MAX_LEN+1}, {})
    with pytest.raises(ValueError, match='Unknown/recursive concept'):
        Target(LG.node('c', LG.node('var', payload='x'), payload='nowhere'))(1)


def test_bootstrap_lessons_not_yet_proven_come_back_until_the_seed_gate(monkeypatch):
    # "Not yet" in the bootstrap: a lesson it has not yet proven comes back after the others have taught more, while
    # the seed gate is unmet and the revisit allocation lasts; proven lessons are not taught again (the U3 A/B's
    # bootstrap on a slower CPU, 2026-10-02).
    import itertools
    import scripts.sera_u_rsi as R

    class Lesson:
        def __init__(self, name):
            self.name, self.data, self.pool = name, [(1, 1)]*4, []

    def run(stubborn):
        tries = {}

        class Base:
            def live(self, task, **kwargs):
                tries[task.name] = tries.get(task.name, 0)+1
                return dict(proven=task.name not in stubborn or tries[task.name] > stubborn[task.name])

        clock = itertools.count(0, 10)                     # each lesson costs ten seconds
        monkeypatch.setattr(R.time, 'perf_counter', lambda: next(clock))
        state, saves = dict(bootstrap_index=0, costs=[], deadline=time.time()+100), []
        R.teach_bootstrap(Base(), [(n, lambda n=n: Lesson(n)) for n in 'abc'], state, saves.append)
        return tries, state, saves

    monkeypatch.setattr(R, 'BOOT_WALL', 30)
    monkeypatch.setattr(R, 'REVISIT_WALL', 20)
    monkeypatch.setattr(R, 'seed_programs', lambda base: [])
    monkeypatch.setattr(R, 'seed_gate', lambda seeds: False)
    tries, state, saves = run({'b': 1})                    # proven on its first revisit
    assert tries == {'a': 1, 'b': 2, 'c': 1} and state['bootstrap_proven'] == dict(a=True, b=True, c=True)
    assert state['bootstrap_schedule'] == [0, 1, 2, 1] and state['bootstrap_revisits'] == 1 and saves == [1, 2, 3, 4]
    assert [c.get('revisit', False) for c in state['costs']] == [False, False, False, True]
    tries, state, saves = run({'b': 9})                    # never proven: revisits stop when their allocation is spent
    assert tries == {'a': 1, 'b': 3, 'c': 1} and state['bootstrap_revisits'] == 2 and not state['bootstrap_proven']['b']
    monkeypatch.setattr(R, 'seed_gate', lambda seeds: True)
    tries, state, saves = run({'b': 9})                    # the gate is met: no revisits
    assert tries == {'a': 1, 'b': 1, 'c': 1} and 'bootstrap_revisits' not in state
