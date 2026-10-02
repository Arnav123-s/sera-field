"""T-S runner (2026-09-26): parallel processes share one work queue, and the world list is written whole.
- 8 processes racing over the same 60 worlds take each world exactly once (claims are O_EXCL), so no world is run
  twice and none is left out; a world whose unit exists is never claimed.
- The list writer leaves the list whole and no temporary files, and does not rewrite an identical list (every
  parallel process writes it at its start while the others read it)."""
import importlib.util
import json
import multiprocessing as mp
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'sera_audit_check.py'
NAMES = [f's1-i{9101 + i}-L{1 + i % 7}' for i in range(60)]


def _runner():
    spec = importlib.util.spec_from_file_location('ts_runner', SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _take_all(folder):
    ts = _runner()
    taken = []
    for name in NAMES:
        path = Path(folder) / f'{name}.json'
        if path.exists():
            continue
        if ts._claim(path):
            taken.append(name)
    return taken


def test_parallel_processes_take_each_world_exactly_once(tmp_path):
    (tmp_path / f'{NAMES[5]}.json').write_text('{}')                     # already done: never claimed
    with mp.get_context('spawn').Pool(8) as pool:
        shares = pool.map_async(_take_all, [str(tmp_path)] * 8).get(timeout=60)
    taken = [n for s in shares for n in s]
    assert sorted(taken) == sorted(n for n in NAMES if n != NAMES[5])
    assert len(set(taken)) == len(taken)
    print('worlds taken per process:', [len(s) for s in shares])


def test_the_world_list_is_written_whole_and_once(tmp_path):
    ts = _runner()
    worlds = [[1, 9101 + i, 1 + i % 7] for i in range(60)]
    path = tmp_path / 'worlds.json'
    ts._write_list(path, worlds)
    assert json.loads(path.read_text()) == worlds
    assert [p.name for p in tmp_path.iterdir()] == ['worlds.json']
    stamp = path.stat().st_mtime_ns
    ts._write_list(path, worlds)
    assert path.stat().st_mtime_ns == stamp
    ts._write_list(path, worlds[:10])
    assert json.loads(path.read_text()) == worlds[:10]
    assert [p.name for p in tmp_path.iterdir()] == ['worlds.json']
