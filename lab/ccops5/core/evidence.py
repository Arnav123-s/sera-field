"""Evidence cache for the School: speed only, every number stays the same.

The mind's run on a world and the checker's verdict on its certificate depend only on the world and the mind's
settings. They never depend on the School arm (teacher, words, board, gut): that is check C13a. So each world's
evidence is computed once, stored, and replayed for every arm and every later run. The stored items are:
  - the mind's report, with its ledger;
  - its public events, which the caretaker then hears in the same order. The caretaker reads only fixed facts of
    the world (its force, its masses), so hearing the events after the run is the same as hearing them during it;
  - the checker's verdict on the certificate.

The key holds the world's recipe and the mind's settings. The folder name is a hash of the source of every module
the evidence depends on. Change any of them and the cache misses, so an old answer is never served for new code.
Workers of one run share the folder. A lock file makes a second worker wait for the first instead of computing
the same world twice.
"""
import hashlib
import os
import pickle
import time
from pathlib import Path

import numpy as np

from . import checker, mind as M

_MODULES = ('checker', 'curriculum', 'gaps', 'grammar', 'likelihood', 'mind', 'paths', 'truth', 'worlds')
WAIT_LIMIT = 30 * 60          # seconds a worker waits for another worker's lock before computing itself


def fingerprint():
    """A hash of everything the evidence depends on: the source of those modules, the legacy physics, numpy."""
    here = Path(__file__).resolve().parent
    h = hashlib.sha256()
    for name in _MODULES:
        h.update((here / f'{name}.py').read_bytes())
    h.update((here.parent / 'puzzles.py').read_bytes())
    h.update(np.__version__.encode())
    return h.hexdigest()[:16]


def _compute(world, eps, budget, check_sigma):
    events = []
    report = M.Mind(world.sigma, eps=eps, budget=budget, on_event=lambda k, e: events.append((k, e))).live(world)
    verdict = bool(report.sure and checker.check(report.certificate, report.ledger.throws, check_sigma)[0])
    return {'report': report, 'events': events, 'verdict': verdict}


class Cache:
    """`folder=None` switches caching off (everything is computed, nothing is stored)."""

    def __init__(self, folder=None):
        self.dir = Path(folder) / fingerprint() if folder else None
        if self.dir is not None:
            self.dir.mkdir(parents=True, exist_ok=True)
        self.hits = self.misses = 0

    def clear_stale(self):
        """Remove locks and half-written files left by killed workers. Call once, before any worker starts:
        otherwise a relaunch would wait WAIT_LIMIT on every world a dead worker had locked."""
        if self.dir is not None:
            for p in [*self.dir.glob('*.lock'), *self.dir.glob('*.tmp')]:
                p.unlink(missing_ok=True)

    def live(self, key, world, *, eps, budget, check_sigma, on_event=None):
        """The mind lives `world`: (report, verdict). verdict = the checker accepts the report's certificate under
        check_sigma (False when the mind is not sure). Events go to on_event after the run, in their order."""
        item = self._get(key, world, eps, budget, check_sigma)
        if on_event is not None:
            for k, event in item['events']:
                on_event(k, event)
        return item['report'], item['verdict']

    def _get(self, key, world, eps, budget, check_sigma):
        if self.dir is None:
            self.misses += 1
            return _compute(world, eps, budget, check_sigma)
        name = hashlib.sha256(repr((key, tuple(world.sigma), eps, budget, tuple(check_sigma))).encode()).hexdigest()
        path, lock = self.dir / f'{name}.pkl', self.dir / f'{name}.lock'
        item = self._load(path)
        if item is not None:
            self.hits += 1
            return item
        try:
            os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            owner = True
        except FileExistsError:
            owner = False
        if not owner:
            started = time.monotonic()
            while lock.exists() and time.monotonic() - started < WAIT_LIMIT:
                time.sleep(2.0)
            item = self._load(path)
            if item is not None:
                self.hits += 1
                return item
        self.misses += 1
        item = _compute(world, eps, budget, check_sigma)
        tmp = path.with_suffix(f'.{os.getpid()}.tmp')
        tmp.write_bytes(pickle.dumps(item, protocol=pickle.HIGHEST_PROTOCOL))
        os.replace(tmp, path)
        if owner:
            try:
                lock.unlink()
            except FileNotFoundError:
                pass
        return item

    @staticmethod
    def _load(path):
        try:
            return pickle.loads(path.read_bytes())
        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            return None
