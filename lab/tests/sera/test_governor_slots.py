"""Machine-wide slots (after the second crash, 2026-09-24 22:02): never more busy processes than the limit."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
import governor  # noqa: E402


def test_slots_cap_reclaim_and_limit_file(tmp_path, monkeypatch):
    monkeypatch.setattr(governor, 'SLOTS', str(tmp_path))
    monkeypatch.setattr(governor, 'temperature', lambda: 70)
    held = [governor.take_slot('a', wait=False) for _ in range(governor.SLOTS_LIMIT)]
    assert all(held) and len(set(held)) == governor.SLOTS_LIMIT
    assert governor.take_slot('b', wait=False) is None                      # the machine is full
    governor.free_slot(held.pop())
    assert governor.take_slot('b', wait=False) is not None                  # a freed slot is taken again
    for p in governor.slots_in_use():
        os.remove(tmp_path / p)
    (tmp_path / 'slot-0.lock').write_text('999999 ghost 2026-09-24 22:02:17\n')   # a process that died holding it
    assert governor.take_slot('c', wait=False) is not None
    (tmp_path / 'limit.txt').write_text('1\n')
    for p in governor.slots_in_use():
        os.remove(tmp_path / p)
    assert governor.take_slot('d', wait=False) is not None
    assert governor.take_slot('e', wait=False) is None                      # the limit file lowers the cap


def test_hot_offers_one_slot_fewer_and_critical_none(tmp_path, monkeypatch):
    monkeypatch.setattr(governor, 'SLOTS', str(tmp_path))
    monkeypatch.setattr(governor, 'temperature', lambda: governor.HOT)
    held = [governor.take_slot('a', wait=False) for _ in range(governor.SLOTS_LIMIT - 1)]
    assert all(held) and governor.take_slot('b', wait=False) is None
    for p in held:
        governor.free_slot(p)
    monkeypatch.setattr(governor, 'temperature', lambda: governor.CRITICAL)
    assert governor.take_slot('c', wait=False) is None


def test_every_live_slot_counts_against_a_lowered_limit(tmp_path, monkeypatch):
    monkeypatch.setattr(governor, 'SLOTS', str(tmp_path))
    monkeypatch.setattr(governor, 'temperature', lambda: 70)
    held = [governor.take_slot('a', wait=False) for _ in range(3)]
    assert all(held)
    (tmp_path / 'limit.txt').write_text('2\n')                            # lowered while three are held
    governor.free_slot(held[0])                                           # the lowest index frees up
    assert governor.take_slot('b', wait=False) is None                   # still two live: no new work
    (tmp_path / 'limit.txt').write_text('3\n')
    assert governor.take_slot('c', wait=False) is not None



def test_no_slot_on_battery(tmp_path, monkeypatch):
    """independent review C1: the 22:02 crash began with the AC adapter dropping out under load."""
    monkeypatch.setattr(governor, 'SLOTS', str(tmp_path))
    monkeypatch.setattr(governor, 'temperature', lambda: 60)
    monkeypatch.setattr(governor, 'on_battery', lambda: True)
    assert governor.take_slot('a', wait=False) is None


def test_a_job_critical_for_longer_than_max_pause_is_stopped(tmp_path, monkeypatch):
    import sys as _sys
    import time as _time
    import slot_run
    monkeypatch.setattr(governor, 'SLOTS', str(tmp_path))
    monkeypatch.setattr(governor, 'temperature', lambda: 60)
    monkeypatch.setattr(governor, 'on_battery', lambda: False)
    t0 = _time.monotonic()
    code = slot_run.run([_sys.executable, '-c', 'import time; time.sleep(60)'], 'test', poll=1,
                        state=lambda: ('critical', 95, 100), max_pause=2)
    assert code == -9 and _time.monotonic() - t0 < 20
    assert governor.slots_in_use() == []                                  # its slot was freed


CHILD = "import time, sys\nf = open(sys.argv[1], 'w')\nfor i in range(60):\n    f.write(repr(time.time()) + chr(10)); f.flush(); time.sleep(0.1)\n"


def test_a_critical_machine_pauses_a_job_where_it_stands_and_resumes_it(tmp_path, monkeypatch):
    """2026-09-25, the author: heat must not cost progress. The job is frozen while critical (it writes nothing), then
    resumed, and finishes normally with its own exit code."""
    import sys as _sys
    import time as _time
    import slot_run
    monkeypatch.setattr(governor, 'SLOTS', str(tmp_path))
    monkeypatch.setattr(governor, 'temperature', lambda: 60)
    monkeypatch.setattr(governor, 'on_battery', lambda: False)
    out = tmp_path / 'ticks.txt'
    calls, window = [], []

    def state():
        calls.append(1)
        if len(calls) in (2, 5):
            window.append(_time.time())
        return ('critical', 95, 100) if 2 <= len(calls) <= 4 else ('ok', 70, 100)
    code = slot_run.run([_sys.executable, '-c', CHILD, str(out)], 'test', poll=1, state=state)
    ticks = [float(x) for x in out.read_text().split()]
    assert code == 0 and len(ticks) == 60
    frozen = [x for x in ticks if window[0] + 0.6 < x < window[1] - 0.3]
    assert not frozen, (window, frozen[:3])
    assert governor.slots_in_use() == []


def test_sensor_readings_are_shared_by_the_whole_machine(tmp_path, monkeypatch):
    """One nvidia-smi or PowerShell reading per SENSOR_TTL, not one per waiting job every 10-30 s."""
    monkeypatch.setattr(governor, 'SLOTS', str(tmp_path))
    reads = []
    monkeypatch.setattr(governor, '_temperature_raw', lambda: reads.append(1) or 71)
    now = [1000.0]
    monkeypatch.setattr(governor.time, 'time', lambda: now[0])
    assert [governor.temperature() for _ in range(5)] == [71] * 5 and len(reads) == 1
    now[0] += governor.SENSOR_TTL['temperature'] + 1
    assert governor.temperature() == 71 and len(reads) == 2


def test_a_broken_mutex_is_never_removed_by_its_old_holder(tmp_path, monkeypatch):
    """B H-4: a holder paused past 60 s has its mutex broken; when it resumes it must not delete the new holder's."""
    monkeypatch.setattr(governor, 'SLOTS', str(tmp_path))
    old = governor._mutex().__enter__()
    os.remove(tmp_path / 'mutex')                                   # broken as stale while it was paused
    new = governor._mutex().__enter__()
    old.__exit__(None, None, None)
    assert (tmp_path / 'mutex').exists() and new.owned()
    new.__exit__(None, None, None)
    assert not (tmp_path / 'mutex').exists()


def test_paused_work_resumes_only_below_hot_minus_the_margin():
    assert not governor.paused_ok('ok', governor.HOT - 1)
    assert governor.paused_ok('ok', governor.HOT - governor.RESUME_MARGIN - 1)
    assert not governor.paused_ok('hot', 60) and governor.paused_ok('cool', None)
