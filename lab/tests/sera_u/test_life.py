import hashlib
import io
import json
import torch
import pytest

from sera_u import SeraU
from sera_u.field.native_owner import NativeConfig
from sera_u.life import Life
from sera_u.mind import U14_CRUTCHES
from scripts.sera_u_rsi import commit, recover


def entity():
    torch.set_num_threads(1)
    return SeraU(3, config=NativeConfig(nodes=3, rounds=1), clock='work',
                 u14=dict.fromkeys(U14_CRUTCHES, False))


def test_one_life_and_shared_parent_forks(tmp_path):
    life = Life(tmp_path/'life')
    first, parent = life.open(entity)
    assert parent is None
    first.clock.charge('dream', 7)
    life.born(first)
    def forbidden_birth():
        raise AssertionError('Second bootstrap')
    resumed, parent = Life(tmp_path/'life').open(forbidden_birth)
    assert resumed.clock.count == 7
    row = life.begin(resumed, 100, parent)
    for arm in ('full', 'no-dreams'):
        clone = SeraU.load(life.path)
        clone.arm = arm
        life.finish_arm(row, clone, dict(arm=arm), complete=True)
    assert {f['parent_digest'] for f in row['forks'].values()} == {parent}
    assert list((tmp_path/'life').glob('*.pt')) == [life.path]
    assert list(life.fork_path(row['id'], 'full').glob('*.pt')) == [life.fork_path(row['id'], 'full')/'sera.pt']


def test_rolling_retention_and_crash_journal(tmp_path):
    m = entity()
    state = dict(stage='arms', active_arm='full', generation=0, protocol={}, checkpoints={})
    for j in range(9):
        m.clock.charge('dream')
        commit(tmp_path, state, m, 'full-g0-train'+str(j)+'.pt')
    assert len(list(tmp_path.glob('*.pt'))) == 1
    commit(tmp_path, state, m, 'full-g0.pt')
    state['checkpoints']['full:0'] = dict(file='full-g0.pt', sha256=state['checkpoint_sha256'])
    commit(tmp_path, state, m, 'full-g0-assessed.pt')
    assert sorted(p.name for p in tmp_path.glob('*.pt')) == ['full-g0.pt', 'full-rolling.pt']
    stale = json.loads((tmp_path/'state.json').read_text())
    m.clock.charge('dream')
    commit(tmp_path, state, m, 'full-next.pt')
    # Crash after checkpoint replace, before state replace: journal reconciles it.
    (tmp_path/'state.json').write_text(json.dumps(stale))
    restored = recover(tmp_path, stale)
    assert restored.clock.count == m.clock.count


def repack(payload):
    inner = io.BytesIO()
    torch.save(payload, inner)
    data = inner.getvalue()
    outer = io.BytesIO()
    torch.save(dict(schema='sera-u-2', sha256=hashlib.sha256(data).hexdigest(), payload=data), outer)
    return outer.getvalue()


def test_carry_changed_code_and_refuse_unknown_shape(tmp_path):
    m = entity()
    payload = m._payload()
    payload['code'] = 'older-code'
    path = tmp_path/'old.pt'
    path.write_bytes(repack(payload))
    with pytest.raises(ValueError, match='learner changed'):
        SeraU.load(path)
    carried = SeraU.carry(path)
    assert carried.learning_hash() == m.learning_hash()
    manifest = carried.carry_manifest
    assert set(manifest['carried']) | {'schema', 'code', 'source', 'runtime', 'progress'} == set(payload)
    assert manifest['renamed'] == [] and manifest['dropped'] == ['progress (observer runner cursor)']
    payload['unknown_learned_part'] = {'opaque': 1}
    path.write_bytes(repack(payload))
    with pytest.raises(ValueError, match='Unknown carry payload'):
        SeraU.carry(path)


def test_carry_refuses_tensor_resize(tmp_path):
    m = entity()
    p = m._payload()
    key = sorted(p['state'])[0]
    p['state'][key] = torch.zeros(123)
    path = tmp_path/'unknown.pt'
    path.write_bytes(repack(p))
    with pytest.raises(ValueError, match='tensor shape'):
        SeraU.carry(path)


def test_carry_refuses_unknown_nested_field_shape(tmp_path):
    m = entity()
    payload = m._payload()
    payload['field'].ideas.unrecognized_carried_shape = object()
    path = tmp_path/'nested.pt'
    path.write_bytes(repack(payload))
    with pytest.raises(ValueError, match='nested carry shape'):
        SeraU.carry(path)


def test_stop_before_first_lesson_retains_the_newborn(tmp_path):
    life = Life(tmp_path/'life')
    m, parent = life.open(entity)
    row = life.begin(m, 100, parent)
    life.finish(row, 'observer_stop')
    resumed, parent = Life(life.root).open(lambda: pytest.fail('Second birth'))
    assert not life.ledger['born'] and resumed.learning_hash() == m.learning_hash()
