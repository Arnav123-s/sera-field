"""CPU fixtures only. Run with PYTHONHASHSEED=0."""
import copy
import math
import time
import hashlib
import json
import torch

from sera import lang as LG
from sera import crutches as CR, tasks as TS
from sera_u import SeraU
from sera_u.clock import Clock, activate
from sera_u.field.native_owner import NativeConfig
from sera_u.mind import U14_CRUTCHES


def entity():
    return SeraU(3, config=NativeConfig(nodes=3, rounds=1), clock='work',
                 u14={k: k == 'work_doubling' for k in U14_CRUTCHES})


def test_clock_pause_and_roundtrip(monkeypatch):
    c = Clock()
    c.start(10)
    c.charge('candidate', 3)
    state = c.state()
    monkeypatch.setattr(time, 'time', lambda: 10**15)
    resumed = Clock(state)
    assert resumed.limit-resumed.count == 7 and not resumed.expired()
    resumed.charge('batch', 7)
    assert resumed.expired() and c.state() == state


def test_deterministic_candidates_threads_and_load():
    results = []
    old_threads = torch.get_num_threads()
    try:
        for threads, load in ((1, 0), (2, 20000)):
            torch.set_num_threads(threads)
            m = entity()
            m.clock.start(260)
            # Artificial observer load cannot spend learner work.
            sum(j*j for j in range(load))
            with activate(m):
                rows = LG.search({'x': 'num'}, 'num', [{'x': n} for n in (-2, 0, 3)],
                                 5, {}, work=100000)
            results.append((m.learning_hash(), copy.deepcopy(m.clock.state()), rows))
        assert results[0] == results[1]
    finally:
        torch.set_num_threads(old_threads)


def test_work_checkpoint_and_default_wall_gate():
    torch.set_num_threads(1)
    m = entity()
    m.clock.start(1000)
    m.clock.charge('field_read', 2)
    clone = SeraU.loads(m.dumps())
    assert clone.clock.state() == m.clock.state()
    assert clone.learning_hash() == m.learning_hash()
    assert LG.WORK_CHARGE is None
    assert LG.DEADLINE_CHECK(-math.inf)


def test_failed_search_exposes_doubling():
    m = entity()
    m.clock.start(100000)
    m.clock.finish('proposal:w0', m, 256, 0.)
    assert m.clock.bounds['proposal:w0'] == 1
    # Both old and larger options exist, selected by the same neutral readout.
    assert m.clock.allowance('proposal:w0', m) in (256, 512)


def test_real_discovery_dream_train_and_resume_digests(monkeypatch):
    from sera_u.discovery import CRUTCHES
    from scripts.sera_u_discovery import WorldPool
    from sera_u.sleep import family
    monkeypatch.setattr(CR, 'ON', set())
    monkeypatch.setattr(CR, 'OFF', set())
    p = LG.node('add', LG.node('var', payload='x'), LG.node('one'))
    manifest = dict(worlds=[dict(id='w', form='exact', program=p, tin='num', tout='num',
                               seed=3, index=141, family=family(p, {}))])
    def body():
        m = SeraU(3, config=NativeConfig(nodes=3, rounds=1), clock='work',
            discovery=dict.fromkeys(CRUTCHES, True), wiring=True,
            u14=dict.fromkeys(U14_CRUTCHES, False))
        m.clock.start(4096)
        pool = WorldPool(manifest)
        with m.scope():
            d = m.discovery
            d.register_worlds(pool.public())
            d.observations['w'] = [pool.act('w', ('ask', x)) for x in (-2, 0, 1, 4)]
            cert = pool.certify('w', p, {}, tuple(d.observations['w']))
            assert cert.accepted
            d.admit(m, 'w', p, cert, m.choice_features(), 1.)
        return m, pool
    def normalized(value):
        if isinstance(value, dict):
            return {k: normalized(v) for k, v in value.items() if k not in ('seconds', 'wall')}
        if isinstance(value, (list, tuple)):
            return [normalized(v) for v in value]
        return value
    results = []
    old_threads = torch.get_num_threads()
    try:
        for threads, reload, load in ((1, False, 0), (2, False, 20000), (1, True, 0)):
            torch.set_num_threads(threads)
            m, pool = body()
            first = m.discover(pool)
            if reload:
                remaining = m.clock.limit-m.clock.count
                saved = m.dumps()
                m = SeraU.loads(saved)
                # A save and reload is byte-stable (strings and numpy dtypes are canonical in work checkpoints).
                assert m.dumps() == saved
                assert m.clock.limit-m.clock.count == remaining
            sum(j*j for j in range(load))
            with m.scope():
                m.sleep.dream(count=2, attempts=8, deadline=m.clock.bound('dream', m))
            m.train(1, 1)
            last = m.discover(pool)
            assert m.clock.counts['judge'] and m.clock.counts['dream'] and m.clock.counts['batch']
            results.append((hashlib.sha256(m.dumps()).hexdigest(), m.learning_hash(), m.clock.state(),
                            normalized([first, last])))
        # Threads and machine load change nothing, to the byte.
        assert results[0] == results[1]
        # A life resumed midway learns exactly what the unbroken one learns (weights, stores, every RNG state, work).
        # Its later checkpoint can still differ in pickle's sharing of equal immutable values (a constant tuple held
        # in two places), not in any value: the learning hash is the resume contract (development review, 2026-10-03).
        assert results[2][1:] == results[0][1:]
    finally:
        torch.set_num_threads(old_threads)


def test_wall_disabled_record_bytes_and_absent_new_payload(monkeypatch):
    from sera_u.discovery import CRUTCHES, Discovery, generation_report
    from sera_u.mind import Engine
    from scripts.sera_u_discovery import WorldPool
    from sera_u.sleep import family
    monkeypatch.setattr(CR, 'ON', set())
    monkeypatch.setattr(CR, 'OFF', set())
    monkeypatch.setattr(Discovery, 'propose', lambda *args: ())
    monkeypatch.setattr(time, 'perf_counter', lambda: 10.)
    # Same frozen seam as U10/U11's existing default-off parity contracts.
    monkeypatch.setattr(Engine, '_u_reads', lambda self, views, concepts=None:
        [(torch.zeros(3, 64), torch.ones(3)/3) for _ in views])
    p = LG.node('var', payload='x')
    manifest = dict(worlds=[dict(id='w', form='exact', program=p, tin='num', tout='num',
                               seed=3, index=141, family=family(p, {}))])
    a = SeraU(3, config=NativeConfig(nodes=3, rounds=1), discovery=dict.fromkeys(CRUTCHES, True))
    b = SeraU(3, config=NativeConfig(nodes=3, rounds=1), discovery=dict.fromkeys(CRUTCHES, True),
              clock='wall', u14=dict.fromkeys(U14_CRUTCHES, False))
    rows = [m.discover(WorldPool(manifest)) for m in (a, b)]
    assert json.dumps(rows[0], sort_keys=True).encode() == json.dumps(rows[1], sort_keys=True).encode()
    assert generation_report(a.discovery.events) == generation_report(b.discovery.events)
    assert a.learning_hash() == b.learning_hash()
    assert not {'clock', 'u14', 'agenda', 'holes', 'wiring'} & set(b._payload())


def test_spent_operation_ends_a_loop_waiting_for_the_session_deadline():
    # Colab, 2026-10-03: `_grow_seeing` looped `while time.time() < until` with the session's deadline while its
    # searches had stopped at the operation's bound; the count froze below `until` and the levels grew forever.
    from sera import one as ONE
    m = entity()
    m.clock.start(10_000)
    m.clock.ceiling = m.clock.count + 100
    try:
        with activate(m):
            until = LG.DEADLINE[0]
            assert ONE.time.time() < until
            m.clock.charge('candidate', 100)
            assert not ONE.time.time() < until
            assert ONE.time.time() + 5 <= ONE.time.time()   # a new continuation is already over
    finally:
        m.clock.ceiling = math.inf


def test_search_work_counts_evaluations_and_a_counted_table_bound(monkeypatch):
    m = entity()
    m.clock.start(10**9)
    probes = [{'x': n} for n in (-2, 0, 3)]
    amounts = []
    with activate(m):
        charge = LG.WORK_CHARGE
        LG.WORK_CHARGE = lambda amount=1: (amounts.append(amount), charge(amount))
        LG.search({'x': 'num'}, 'num', probes, 4, {}, work=100000)
    # Every candidate is charged its evaluations (one per probe it is tried on), not one unit.
    assert amounts and min(amounts) >= len(probes) and sum(amounts) == m.clock.counts['candidate']
    stops = LG.MEMORY_STOPS[0]
    monkeypatch.setattr(LG, 'WORK_TABLE_ENTRIES', 20)
    m2 = entity()
    m2.clock.start(10**9)
    with activate(m2):
        LG.search({'x': 'num'}, 'num', [{'x': n} for n in (-5, 1, 7)], 6, {}, work=100000)
    assert LG.MEMORY_STOPS[0] > stops


def test_a_loop_that_only_waits_pays_its_way_to_its_deadline():
    # Colab, 2026-10-03 22:24: `_build` looped `while time.time() < until` while the search deadline it passes down had
    # gone by, so its searches charged nothing and the count stayed at 27,159 below `until` for minutes.
    from sera import one as ONE
    m = entity()
    m.clock.start(1_000_000)
    with activate(m):
        until = ONE.time.time() + 10      # a continuation: a work bound, not seconds
        LG.DEADLINE[0] = m.clock.count    # the search deadline below it has already passed
        polls = 0
        while ONE.time.time() < until:
            polls += 1
            assert polls < 10_000
            LG.search({'x': 'num'}, 'num', [{'x': n} for n in (1, 2)], 3, {}, work=100)
    assert m.clock.counts['tick'] > 0
