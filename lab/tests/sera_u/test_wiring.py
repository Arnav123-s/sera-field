"""U14 hop contracts. Real Exact certificates; no planted proof in the learner."""
import math
import time
import numpy as np
import pytest
import torch

from sera import crutches as CR, lang as LG, phi as PH
from sera_u import SeraU
from sera_u.discovery import CRUTCHES as U9, Certification, wiring_report, wiring_snapshot
from sera_u.einstein import CRUTCHES as U10
from sera_u.scientists import CRUTCHES as U11
from sera_u.darwin import CRUTCHES as U12
from sera_u.roadmap import CRUTCHES as U13
from sera_u.field.native_owner import NativeConfig
from sera_u.mind import U_CRUTCHES, U14_CRUTCHES
from sera_u.ports import digest
from sera_u.sleep import family
from scripts.sera_u_discovery import WorldPool
from scripts.sera_u_scientists import ScientistsPool


@pytest.fixture(autouse=True)
def clean(monkeypatch):
    torch.set_num_threads(1)
    monkeypatch.setattr(CR, 'ON', set())
    monkeypatch.setattr(CR, 'OFF', set())
    monkeypatch.setattr(LG, 'DEADLINE', [math.inf])
    LG.forget_searches()
    yield
    LG.forget_searches()


def fixture(memory):
    switches = dict.fromkeys(U_CRUTCHES, True)
    switches['abstain_bar'] = False
    if not memory:
        switches.update(memory_layer_a=False, memory_layer_b=False,
                        field_understanding=False, memory_choice=False)
    mind = SeraU(3, config=NativeConfig(nodes=3, rounds=1), crutches=switches,
        discovery=dict.fromkeys(U9, True), einstein=dict.fromkeys(U10, True),
        scientists=dict.fromkeys(U11, True), darwin=dict.fromkeys(U12, True),
        roadmap=dict.fromkeys(U13, True), wiring=True, u14=dict.fromkeys(U14_CRUTCHES, True))
    # Three bodies are the actual prerequisite of a lineage tree. The law is
    # acquired through the identical real observer check in every body.
    p = LG.node('add', LG.node('var', payload='x'), LG.node('lit', payload=2))
    manifest = dict(schema='u9-discovery-1', worlds=[dict(id='w'+str(j), form='exact',
        program=p, tin='num', tout='num', seed=3, index=9100+j, family=family(p, {})) for j in range(3)])
    pool = ScientistsPool(manifest)
    mind.discovery.register_worlds(pool.public())
    return mind, pool, p


@pytest.mark.parametrize('memory', [False, True])
def test_certified_law_hops(memory, monkeypatch):
    mind, pool, p = fixture(memory)
    d = mind.discovery
    with mind.scope():
        for wid in sorted(d.worlds):
            d.observations[wid] = [pool.act(wid, ('ask', x)) for x in (-2, 0, 1, 4)]
            verdict = pool.certify(wid, p, mind.field.concept_table(), tuple(d.observations[wid]))
            assert verdict.accepted
            key, fresh = d.admit(mind, wid, p, verdict, np.r_[1., np.zeros(64)], 1.)
            assert fresh and d.laws[key]['certificates'][wid] == verdict
        law = d.laws[key]
        assert len(law['coverage']) == 3 and law['concept_ids']
        assert len(mind.sleep.replay) == 3
        assert key in wiring_snapshot(mind)['memory'][0]
        assert (getattr(mind.field, 'field_understanding', False) is memory)
        if memory:
            assert mind.field.standing_counts(('discovered-law', key))[0] == 3
        else:
            assert mind.field.standing[('discovered-law', key)][0] == 3
        e = d.einstein
        assert key in dict(e.compatible(d, 'w0'))
        # Inspecting one law is a received hop, but cannot invent support.
        assert e.invariance(mind, d, 'w0') == 0
        pid = e.predict(mind, d, 'w0', ('ask', 17))
        assert pid is not None
        assert e.settle(mind, d, pid, pool.act('w0', ('ask', 17))) == 1
        failed = Certification(False, 'formula', (('own_prediction', True),), 'own-failure', True)
        d.anomaly(mind, 'w0', key, failed)
        assert any(key in q['laws'] for q in e.doubts.values())
        assert any(c['anomaly'] == key for c in d.scientists.chases.values())
        tree = d.darwin.tree(mind, d, d.darwin.region(d, 'w0'))
        assert tree is not None and len(tree['edges']) == 2
        cid = law['concept_ids'][0]
        d.roadmap.rebuild(mind, d, pool, deadline=time.time()+.1)
        rebuilt = next(r for r in d.roadmap.rebuilds.values() if r['original'] == cid)
        surface = LG.node('c', LG.node('var', payload='x'), payload=cid)
        d.roadmap.reused(surface, 'w0')
        assert rebuilt['original_reuse'] == 1
        view = d.view('w0')
        checks = d.syndromes(mind, view, (p,))
        assert checks
        assert mind.field.curiosity.last_checks
        # Supply the real prerequisites through the same certificate path,
        # never by inserting entries into self.laws or the concept table.
        x = LG.node('var', payload='x')
        square = LG.node('mul', x, x)
        programs = [LG.node('add', square, LG.node('lit', payload=n)) for n in (2, 4, 8)]
        programs += [LG.node('sub', LG.node('zero'), x), LG.node('add', x, x),
                     LG.node('mul', x, LG.node('lit', payload=2))]
        acquired = []
        for j, program in enumerate(programs):
            wid = 'prerequisite'+str(j)
            pool.specs[wid] = dict(id=wid, form='exact', program=program, tin='num', tout='num',
                                  seed=3, index=9200+j, family=family(program, {}))
            d.register_worlds(pool.public())
            d.observations[wid] = [pool.act(wid, ('ask', n)) for n in (-2, 0, 1, 4)]
            cert = pool.certify(wid, program, mind.field.concept_table(), tuple(d.observations[wid]))
            assert cert.accepted
            acquired.append(d.admit(mind, wid, program, cert, np.r_[1., np.zeros(64)], 1.)[0])
        assert e.invariance(mind, d, 'prerequisite0') >= 1
        assert any(set(acquired[:3]) <= set(q['laws']) for q in e.principles.values())
        # Fixtures limit search candidates, while the relation's actual
        # independent verifier and its normal acquisition/standing stay real.
        with monkeypatch.context() as seam:
            pattern = LG.node('add', LG.node('mul', x, LG.node('lit', payload=2)),
                              LG.node('lit', payload=2))
            seam.setattr(LG, 'search', lambda *args, **kw: [(pattern, LG.size(pattern))])
            assert d.scientists.gap(mind, d) >= 1
            assert any(q['parameter'] == 6 for q in d.scientists.predictions)
        with monkeypatch.context() as seam:
            seam.setattr(LG, 'search', lambda *args, **kw: [])
            assert d.scientists.conjecture(mind, d, pool, 'w0') == 1
            assert any(q['standing'] for q in d.scientists.relations.values())
        # Conservation consumes acquired executable concepts and fresh sensor
        # trajectories; an exact univariate law alone supplies no trajectories.
        from scripts.sera_u_scientists import throw_rows
        from ccops5.core.worlds import Action
        wid = 'motion'
        pool.specs[wid] = dict(id=wid, form='strengths', motion_sensor=True,
                              has_conserved=True, seed=3, index=9300)
        d.register_worlds(pool.public())
        d.observations[wid] = list(throw_rows([pool.body(wid).push(0, Action(((0., .5, f),)))
                                               for f in (-1., 1.)]))
        conserved = LG.node('rsub', LG.node('var', payload='v'), LG.node('var', payload='x'))
        with monkeypatch.context() as seam:
            seam.setattr(LG, 'search', lambda *args, **kw: [(conserved, LG.size(conserved))])
            assert d.scientists.conservation(mind, d, pool, wid) == 1
            assert d.scientists.conserved and not pool.audit_records[-1]['false_credit']
    for _ in range(3):
        row = mind.discover(pool)
        assert row is not None and 'wiring' in row
    saved = wiring_report(d.events)
    assert key in saved['habits']['einstein']['received']
    assert key in saved['habits']['darwin']['received']
    assert key in saved['habits']['scientists']['received']
    assert saved['habits']['memory']['received'] == sorted({key, *acquired})
    assert key in saved['habits']['holes']['received']
    for hop in ('symmetry_principles', 'doubt_assumptions', 'bold_predictions',
                'gap_predictions', 'number_conjectures', 'conserved_quantities',
                'anomaly_pursuit', 'lineage_trees', 'rederive_concepts', 'gap_syndromes'):
        assert saved['habits'][hop]['outputs'], hop


def test_wiring_report_records_only():
    rows = [dict(wiring=dict(observations=3, floor_worlds=[], proposals=0,
        candidates_audited=0, certified=0, admitted=0,
        habits={'memory': dict(received=[], outputs=[])}))]
    assert wiring_report(rows) == rows[0]['wiring']
