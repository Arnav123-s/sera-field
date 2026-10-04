"""U14 work accounting. The clock has no wall-time dependency.

The adapter is scoped to the learner modules, never to ccops5's judge or the
observer. Old Sera/ONE executions retain their original time module and gate.
"""
from contextlib import contextmanager
import math
import sys

import numpy as np

BASE_WORK = 256                  # one existing language candidate chunk
CHECK_COST = 1                  # fixed cost, independent of judge seconds
KINDS = ('candidate', 'field_read', 'dream', 'batch', 'judge', 'tick', 'method', 'act')
CURRENT = None


def charge(kind, amount=1):
    if CURRENT is not None:
        CURRENT.clock.charge(kind, amount)


class Clock:
    def __init__(self, state=None):
        self.count = 0
        self.counts = dict.fromkeys(KINDS, 0)
        self.limit = None
        self.bounds = {}
        self.ceiling = math.inf     # transient call boundary, never learned/saved
        if state is not None:
            if set(state) != {'count', 'counts', 'limit', 'bounds'}:
                raise ValueError('Unknown clock shape')
            if set(state['counts']) != set(KINDS) or any(type(n) is not int or n < 0
                    for n in [state['count'], *state['counts'].values()]):
                raise ValueError('Invalid work counts')
            if state['count'] != sum(state['counts'].values()):
                raise ValueError('Inconsistent work ledger')
            if state['limit'] is not None and (type(state['limit']) is not int or state['limit'] < 0):
                raise ValueError('Invalid session limit')
            for key, value in state['bounds'].items():
                if type(key) is not str or type(value) is not int or value < 0:
                    raise ValueError('Unknown bound shape')
            self.count, self.counts = state['count'], dict(state['counts'])
            self.limit, self.bounds = state['limit'], dict(state['bounds'])

    def state(self):
        return dict(count=self.count, counts=dict(self.counts), limit=self.limit, bounds=dict(self.bounds))

    def start(self, work):
        if type(work) is not int or work < 0:
            raise ValueError('Session work must be a nonnegative integer')
        self.limit = self.count + work
        return self.limit

    def charge(self, kind, amount=1):
        if kind not in self.counts or type(amount) is not int or amount < 0:
            raise ValueError('Unknown work charge')
        self.count += amount
        self.counts[kind] += amount

    def expired(self, deadline=math.inf):
        return self.count >= min(deadline, self.ceiling, self.limit if self.limit is not None else math.inf)

    def allowance(self, name, mind):
        """Neutral Thompson choices; failed visits expose the next doubling.

        No upper lifetime cap: a repeated unsuccessful call eventually has a
        larger option. Only the observer's remaining session work clips it.
        """
        level = self.bounds.get(name, 0)
        if mind.u14.get('work_doubling', False):
            policy = mind.work_policy
            x = mind.choice_features()
            choices = tuple(str(j) for j in range(level+1))
            picked = int(policy.pick(choices, x, mind.numpy))
        else:
            picked = level
        amount = BASE_WORK * (2 ** picked)
        return min(amount, max(0, self.limit-self.count)) if self.limit is not None else amount

    def finish(self, name, mind, amount, gain):
        if not gain and mind.u14.get('work_doubling', False):
            self.bounds[name] = self.bounds.get(name, 0)+1
        if mind.u14.get('work_doubling', False):
            level = max(0, int(math.log2(max(BASE_WORK, amount)/BASE_WORK)))
            mind.work_policy.learn(str(level), mind.choice_features(), gain, max(1, amount))

    def bound(self, name, mind):
        return min(self.ceiling, self.count + self.allowance(name, mind))


class WorkStamp(float):
    """Legacy inner wall caps become choices of work, including inherited ONE.

    A literal number of seconds is deliberately not converted into work units.
    Every such continuation gets the same neutral doubling mechanism.
    """
    def __new__(cls, value):
        return float.__new__(cls, value)

    def __add__(self, unused_seconds):
        if CURRENT is None:
            return float(self) + unused_seconds
        clock, mind = CURRENT.clock, CURRENT
        if math.isinf(unused_seconds):
            return min(clock.ceiling, clock.limit if clock.limit is not None else math.inf)
        return clock.bound('continuation', mind)

    __radd__ = __add__


class WorkTime:
    def __init__(self, mind):
        self.mind = mind
        self.seen = None

    def time(self):
        clock = self.mind.clock
        if clock.count == self.seen:
            # Nothing was done since the clock was last read: a loop that only waits pays a chunk each look, as wall
            # time passes while it spins. Without it `_build`'s `while time.time() < until` spun at a frozen count when
            # the search deadline it passes down had already gone by (Colab, 2026-10-03 22:24: count 27,159 for minutes).
            clock.charge('tick', BASE_WORK)
        self.seen = clock.count
        if clock.limit is not None and clock.expired():
            # This operation's work is spent: its 'now' is past every deadline a loop in it can hold (each is at most
            # the session's), as when a time box ends. Without it `_grow_seeing`'s `while time.time() < until` waited
            # for the session's deadline while its searches, stopped at the operation's bound, charged nothing more:
            # levels grew forever, and every life held 6-12 GB (Colab, 2026-10-03 21:50, the author saw the RAM).
            return WorkStamp(max(clock.count, clock.limit))
        return WorkStamp(clock.count)

    def perf_counter(self):
        return self.mind.clock.count

    process_time = perf_counter


@contextmanager
def activate(mind):
    if getattr(mind, 'clock_mode', 'wall') != 'work' or getattr(mind, '_clock_active', False):
        yield
        return
    from sera import lang as LG
    from sera import tasks as TS, phi as PH
    # Load helpers before installing the adapter. A helper first imported
    # mid-operation would otherwise retain a real-time deadline.
    import importlib
    for module in ('sera.compact', 'sera.synth', 'sera.design'):
        importlib.import_module(module)
    import torch
    adapter = WorkTime(mind)
    saved = []
    # Only learner modules, including inherited ONE and its Field/search
    # helpers. WorldPool and ccops5 remain on real observer time.
    for name, module in sorted(sys.modules.items()):
        if (name.startswith('sera.') or name.startswith('sera_u.')) and hasattr(module, 'time'):
            saved.append((module, module.time))
            module.time = adapter
    gate, charge, memory_gate = LG.DEADLINE_CHECK, LG.WORK_CHARGE, LG._over_memory
    deadline, threads = LG.DEADLINE[0], torch.get_num_threads()
    global CURRENT
    previous_current = CURRENT
    CURRENT = mind
    hooks = []
    def counted(cls, name, kind):
        original = getattr(cls, name)
        def call(*args, **kwargs):
            mind.clock.charge(kind, CHECK_COST if kind == 'judge' else 1)
            return original(*args, **kwargs)
        hooks.append((cls, name, original))
        setattr(cls, name, call)
    counted(TS.Exact, 'verify', 'judge')
    counted(TS.Rail, 'verify', 'judge')
    counted(PH.Ideas, 'evoked', 'field_read')
    original_search = LG.search
    def work_search(*args, **kwargs):
        if LG.WORK_CHARGE is not None and kwargs.get('chunk') is None:
            # Legacy per-size candidate caps must not override the Field's
            # selected bound. Deterministic chunks retain their motor grain.
            kwargs['work'] = None
        return original_search(*args, **kwargs)
    LG.search = work_search
    mind._clock_active = True
    try:
        torch.set_num_threads(1)  # CPU reductions use the same order on both machines
        LG.forget_searches()
        LG.DEADLINE_CHECK = mind.clock.expired
        # 'candidate' work counts evaluations: a candidate tried on n probes costs n (see LG.WORK_TABLE_VALUES).
        LG.WORK_CHARGE = lambda amount=1: mind.clock.charge('candidate', amount)
        LG._over_memory = lambda: False  # machine pressure is an observer stop
        LG.DEADLINE[0] = mind.clock.limit if mind.clock.limit is not None else math.inf
        yield
    finally:
        LG.DEADLINE_CHECK, LG.WORK_CHARGE, LG._over_memory = gate, charge, memory_gate
        LG.DEADLINE[0] = deadline
        LG.search = original_search
        for module, original in saved:
            module.time = original
        for cls, name, original in hooks:
            setattr(cls, name, original)
        CURRENT = previous_current
        torch.set_num_threads(threads)
        mind._clock_active = False


def work_constructor(function):
    """Initialization reductions must obey the same CPU order as later work."""
    from functools import wraps
    @wraps(function)
    def run(mind, *args, **kwargs):
        if kwargs.get('clock', 'wall') != 'work':
            return function(mind, *args, **kwargs)
        import torch
        threads = torch.get_num_threads()
        try:
            torch.set_num_threads(1)
            return function(mind, *args, **kwargs)
        finally:
            torch.set_num_threads(threads)
    return run


def operation(function):
    """Keep all cost-based learning inside one work scope, including setup."""
    from functools import wraps
    @wraps(function)
    def run(mind, *args, **kwargs):
        if getattr(mind, 'clock_mode', 'wall') != 'work':
            return function(mind, *args, **kwargs)
        import time as wall
        started, count = wall.perf_counter(), mind.clock.count
        ceiling = mind.clock.ceiling
        bound = mind.clock.bound(function.__name__, mind)
        if function.__name__ in ('discover', 'work_hole', 'train'):
            kwargs['deadline'] = min(kwargs.get('deadline', math.inf), bound)
        mind.clock.ceiling = bound
        try:
            with activate(mind):
                result = function(mind, *args, **kwargs)
            spent = mind.clock.count-count
            gain = float(bool(result and isinstance(result, dict) and
                         (result.get('proven') or result.get('discovered'))))
            if function.__name__ == 'train' and result and len(result) > 1:
                gain = max(0., result[0]['objective']-result[-1]['objective'])
            mind.clock.finish(function.__name__, mind, spent, gain)
            mind.clock.finish('continuation', mind, spent, gain)
            spent = mind.clock.count-count
            if isinstance(result, dict):
                result['work'] = spent
                result['seconds'] = wall.perf_counter()-started
                result['cost_unit'] = 'work'
                if 'sera_u' in result:
                    result['sera_u']['wall'] = result['seconds']
            return result
        finally:
            mind.clock.ceiling = ceiling
    return run
