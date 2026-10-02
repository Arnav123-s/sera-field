"""Checks for the evidence cache's mechanics: one computation per key, stale locks cleared, keys kept apart.

The slow computation (the mind plus the checker) is replaced by a counter here. That the cached run gives the same
life as the uncached one is checked on a real smoke life (`school_run.py --quick`, cache none vs cold vs warm).
"""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ccops5.core import evidence as EV


class World:
    sigma = (0.01, 0.02)


def fake_compute(calls):
    def compute(world, eps, budget, check_sigma):
        calls.append((eps, budget))
        return {'report': ('report', eps), 'events': [(0, 'start'), (0, 'end')], 'verdict': True}
    return compute


class EvidenceCacheTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.calls = []
        patcher = mock.patch.object(EV, '_compute', fake_compute(self.calls))
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.tmp.cleanup)

    def live(self, cache, key=('k',), eps=0.5):
        heard = []
        out = cache.live(key, World(), eps=eps, budget=2, check_sigma=(0.01,), on_event=lambda k, e: heard.append(e))
        return out, heard

    def test_computed_once_then_replayed_with_events_in_order(self):
        first = EV.Cache(self.tmp.name)
        a, heard_a = self.live(first)
        b, heard_b = self.live(EV.Cache(self.tmp.name))
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(a, b)
        self.assertEqual(heard_a, ['start', 'end'])
        self.assertEqual(heard_a, heard_b)

    def test_keys_and_settings_kept_apart(self):
        cache = EV.Cache(self.tmp.name)
        self.live(cache, key=('a',))
        self.live(cache, key=('b',))
        self.live(cache, key=('a',), eps=0.3)
        self.assertEqual(len(self.calls), 3)

    def test_off_computes_every_time_and_stores_nothing(self):
        cache = EV.Cache(None)
        self.live(cache)
        self.live(cache)
        self.assertEqual(len(self.calls), 2)
        self.assertEqual(list(Path(self.tmp.name).iterdir()), [])

    def test_clear_stale_removes_dead_workers_locks(self):
        cache = EV.Cache(self.tmp.name)
        (cache.dir / 'dead.lock').touch()
        (cache.dir / 'dead.123.tmp').touch()
        cache.clear_stale()
        self.assertEqual(sorted(p.name for p in cache.dir.iterdir()), [])

    def test_fingerprint_names_the_folder(self):
        self.assertEqual(EV.Cache(self.tmp.name).dir.name, EV.fingerprint())


if __name__ == '__main__':
    unittest.main()
