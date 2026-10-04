import math
import numpy as np
import pytest
import torch

from sera import crutches as CR, lang as LG
from sera_u import SeraU
from sera_u.discovery import CRUTCHES as U9, Certification
from sera_u.field.native_owner import NativeConfig
from sera_u.mind import U14_CRUTCHES
from sera_u.sleep import family
from scripts.sera_u_holes import HolesPool, freeze_holes, report_holes


def entity(monkeypatch):
    torch.set_num_threads(1)
    monkeypatch.setattr(CR, 'ON', set())
    monkeypatch.setattr(CR, 'OFF', set())
    m = SeraU(3, config=NativeConfig(nodes=3, rounds=1), discovery=dict.fromkeys(U9, True),
              u14=dict.fromkeys(U14_CRUTCHES, True), wiring=True)
    monkeypatch.setattr(m.holes.policy, 'pick', lambda choices, x, rng:
        'retire' if 'retire' in choices else sorted(k for k in choices if k != 'continue')[0])
    return m


def test_real_free_constant_hole_and_chain(monkeypatch):
    m = entity(monkeypatch)
    x = LG.node('var', payload='x')
    p = LG.node('add', x, LG.node('lit', payload=2))
    q = LG.node('mul', x, LG.node('lit', payload=2))
    manifest = dict(schema='u9-discovery-1', worlds=[dict(id=wid, form='exact', program=program,
        tin='num', tout='num', seed=3, index=140000+j, family=family(program, {}))
        for j, (wid, program) in enumerate((('w0', p), ('w1', q)))])
    pool = HolesPool(manifest)
    d = m.discovery
    d.register_worlds(pool.public())
    with m.scope():
        for wid, program in (('w0', p), ('w1', q)):
            d.observations[wid] = [pool.act(wid, ('ask', v)) for v in (-2, 0, 1, 4)]
            certificate = pool.certify(wid, program, {}, tuple(d.observations[wid]))
            assert certificate.accepted
            key, _ = d.admit(m, wid, program, certificate, np.r_[1., np.zeros(64)], 1.)
            if wid == 'w0':
                source = key
                constant = next(r for r in m.holes.questions.values() if r['reason'] == 'constant')
                assert constant['law'] == source and constant['status'] == 'open'
                assert not m.agenda.items[constant['agenda']]['outside']
        assert constant['status'] == 'answered' and constant['answered_by'] == key
        assert any(r['parent'] == constant['id'] and r['depth'] == 2 for r in m.holes.questions.values())


def test_retired_world_reopened_by_anomaly(monkeypatch):
    m = entity(monkeypatch)
    from sera_u.discovery import WorldView
    d = m.discovery
    d.register_worlds((WorldView('w0', 'exact'),))
    p = LG.node('var', payload='x')
    d.observations['w0'] = [(v, v) for v in (-2, 0, 1, 4)]
    # Retirement unit is about the state transition; the hop test separately
    # requires real WorldPool certification before admission.
    d.laws['law'] = dict(hypothesis=p, form='exact', signature=('num', 'num'),
        coverage={'w0': (32., 0.)}, bits=1., concept_ids=[])
    m.holes.visit(m, 'w0')
    m.holes.visit(m, 'w0')
    assert 'w0' in m.holes.retired and m.holes.zero_progress_repeats == 1
    d.anomaly(m, 'w0', 'law', Certification(False, 'formula', (('own', True),), 'anomaly', True))
    assert 'w0' not in m.holes.retired
    assert any(r['kind'] == 'reopened' for r in m.holes.events)


def test_freeze_once_disjoint_and_direct_mass_measurement():
    suite = {k: [] for k in ('assessment', 'wake', 'retention')}
    manifest = freeze_holes(suite, 3)
    assert manifest['holes_suite'] == 'u14-holes-1'
    assert manifest['observer_links'][0]['direct_measurement']
    public = HolesPool(manifest).public()
    assert public[0].object_ids == public[1].object_ids
    assert all('observer_links' not in repr(w) for w in public)
    assert manifest == freeze_holes(suite, 3)


def test_unlinked_answer_never_earns_suite_hit():
    manifest = {'observer_links': [dict(reason='constant', source='a', target='b')]}
    records = [dict(kind='hole', id='q', reason='constant', source_world='a'),
               dict(kind='hole-answer', id='q', law='k', depth=1)]
    rows = [dict(arm='full', generation=0, holes=dict(found=1, answered=1, chain_depth=1,
        distinct_laws=1, zero_progress_repeat_visits=0, records=records),
        admission_records=[dict(law='k', world='unrelated')])]
    assert report_holes(rows, manifest)['arms']['full']['linked_answers'] == 0


def test_reuse_does_not_spawn_endless_domain_questions(monkeypatch):
    m = entity(monkeypatch)
    monkeypatch.setattr('sera_u.holes.sample_input', lambda *args: 127)
    p = LG.node('add', LG.node('var', payload='x'), LG.node('lit', payload=2))
    manifest = dict(worlds=[dict(id='w', form='exact', program=p, tin='num', tout='num',
                               seed=3, index=142, family=family(p, {}))])
    pool = HolesPool(manifest)
    d = m.discovery
    d.register_worlds(pool.public())
    with m.scope():
        d.observations['w'] = [pool.act('w', ('ask', x)) for x in (-2, 0, 1, 4)]
        verdict = pool.certify('w', p, {}, tuple(d.observations['w']))
        key, _ = d.admit(m, 'w', p, verdict, m.choice_features(), 1.)
        domains = [q for q in m.holes.questions.values() if q['reason'] == 'domain']
        assert len(domains) == 1
        for _ in range(3):
            d.admit(m, 'w', p, verdict, m.choice_features(), 1., law_key=key)
        assert [q for q in m.holes.questions.values() if q['reason'] == 'domain'] == domains
