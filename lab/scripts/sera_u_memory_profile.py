"""US2 public-memory CPU profile; no teacher targets enter the timing fixtures."""
import argparse
import copy
from contextlib import ExitStack
from dataclasses import replace
import json
import os
from pathlib import Path
import platform
import statistics
import sys
import time
from unittest.mock import patch

# Set these before importing NumPy/Torch, including on Colab.
for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMBA_NUM_THREADS'):
    os.environ[name] = '1'
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('CCOPS5_SHAPES', 'library')
os.environ.setdefault('CCOPS5_CLAIM', 'functional')
os.environ.setdefault('CCOPS5_BAND', 'claim')

import numpy as np
import torch

from scripts.sera_one import teaching
from sera import tasks as TS
from sera_u import SeraU
from sera_u.memory import Memory, memory_records
from sera_u.mind import arm_settings
from sera_u.ports import TaskView
from sera_u.proposer import FieldOwner


def fixtures(seed):
    lessons = [(name, build()) for name, build in teaching(seed)
               if name.startswith(('number:', 'list:'))]
    generated = []
    for i in range(8):
        generated.append((f'generated:number:{i}', TS.number_task(
            f'profile number {i}', lambda x, i=i: (i+1)*x+i, seed, 1000+i, words=())))
        generated.append((f'generated:list:{i}', TS.list_task(
            f'profile list {i}', lambda xs, i=i: [x+i for x in xs[::-1]],
            'list', seed, 1000+i, words=())))
    return lessons, lessons+generated


def reference_refresh(self, view):
    """Pre-US2 schedule, including duplicates grouped at first occurrence."""
    from collections import Counter
    if type(view) is not TaskView:
        raise TypeError('Only public TaskView observations can enter memory')
    now = Counter(memory_records(view))
    for row in memory_records(view):
        if now[row] > self.seen_records[row]:
            for _ in range(now[row]-self.seen_records[row]):
                self.write_record(row)
            self.seen_records[row] = now[row]
    self.current = view


def reference_features(self, view, *, grow=True):
    cached = self._feature_cache.get((view, grow)) if not torch.is_grad_enabled() else None
    ring = self.ring(view)
    if cached is not None:
        previous = self._feature_rings[(view, grow)]
        if (ring is None and previous is None) or (
                ring is not None and previous is not None and torch.equal(ring, previous)):
            return cached
        self._feature_cache.pop((view, grow))
        self._feature_rings.pop((view, grow))
    state = self.mind.state if self.a else self.mind.owner.empty(1)
    return self.mind.owner.task_features(view, grow=grow, state=state, ring=ring, memory_read=True)


def reference_features_many(self, views, *, grow=True):
    views = tuple(views)
    owner = self.mind.owner
    states = [self.mind.state if self.a else owner.empty(1) for _ in views]
    return owner.task_features_many(views, grow=grow, states=states,
                                    rings=[self.ring(view) for view in views], memory_read=True)


def implementation(mode):
    """Reproduce old scheduling/encoding/cache behavior in the same source tree.

    This is a timing control, not an old-code checkpoint compatibility claim.
    Native mode also runs when only this script has been copied onto the base.
    """
    stack = ExitStack()
    if mode == 'reference':
        stack.enter_context(patch.object(Memory, 'refresh', reference_refresh))
        stack.enter_context(patch.object(Memory, 'features', reference_features))
        stack.enter_context(patch.object(Memory, 'features_many', reference_features_many))
        if hasattr(Memory, '_compute_ring'):
            stack.enter_context(patch.object(Memory, 'ring', Memory._compute_ring))
        if hasattr(FieldOwner, 'encode_records'):
            def singles(self, rows, *, grow=True):
                return torch.cat([self.encode_record(row, grow=grow) for row in rows], 0)
            stack.enter_context(patch.object(FieldOwner, 'encode_records', singles))
    return stack


def summary(values):
    return dict(samples_seconds=values, median_seconds=statistics.median(values),
                p95_seconds=float(np.percentile(values, 95)))


def instrument(mind, costs):
    """Inclusive attribution (nested times overlap); sequential observe stays visible."""
    stack = ExitStack()
    for obj, name in ((mind.owner, 'encode_record'), (mind.owner, 'encode_records'),
                      (mind.owner, 'observe'), (mind.memory, 'ring'),
                      (mind.memory, '_compute_ring')):
        if not hasattr(obj, name):
            continue
        original = getattr(obj, name)
        def timed(*args, _fn=original, _name=name, **kwargs):
            start = time.perf_counter()
            try:
                return _fn(*args, **kwargs)
            finally:
                row = costs.setdefault(_name, dict(calls=0, seconds=0.))
                row['calls'] += 1
                row['seconds'] += time.perf_counter()-start
        stack.enter_context(patch.object(obj, name, timed))
    return stack


def run(args):
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    lessons, tasks = fixtures(args.seed)
    result = dict(seed=args.seed, implementation=args.mode, device='cpu', threads=1,
                  python=platform.python_version(), torch=torch.__version__,
                  platform=platform.platform(), task_wall=args.task_wall, max_steps=args.max_steps,
                  history='public bootstrap observations only; no bootstrap training',
                  repeats=args.repeats, warmup=args.warmup, cases={})
    operations = ('begin', 'refresh', 'ring', 'ring_cached', 'features', 'features_cached',
                  'features_many', 'live')
    with implementation(args.mode):
        for case, enabled in (('on', True), ('off', False)):
            settings = {**arm_settings('full'), 'memory_layer_a': enabled, 'memory_layer_b': enabled}
            base = SeraU(args.seed, device='cpu', crutches=settings)
            # Both cases see the same public lesson views, in bootstrap order.
            for _, task in lessons:
                with base.scope(), torch.no_grad():
                    base.memory.begin(TaskView.from_task(task))
            snapshot = base.dumps()
            rows, totals = [], {name: [] for name in operations}
            for name, task in tasks:
                view = TaskView.from_task(task)
                grown = replace(view, words=view.words+('profile new public observation',))
                item = dict(name=name, view_identity=view.identity,
                            records=len(memory_records(view)), operations={})
                for operation in operations:
                    values, attributions = [], []
                    for repeat in range(args.warmup+args.repeats):
                        mind = SeraU.loads(snapshot)   # load/build costs outside every micro timer
                        costs = {}
                        if operation == 'live':
                            fresh = copy.deepcopy(task)
                            with instrument(mind, costs):
                                start = time.perf_counter()
                                mind.live(fresh, teaching=False, task_wall=args.task_wall,
                                          max_steps=args.max_steps)
                                elapsed = time.perf_counter()-start
                        else:
                            with mind.scope(), torch.no_grad():
                                if operation != 'begin':
                                    mind.memory.begin(view)
                                if operation == 'ring_cached':
                                    mind.memory.ring(view)
                                if operation == 'features_cached':
                                    read = mind.memory.features(view)
                                    # The old path only filled its cache during assessment preparation.
                                    mind.memory._feature_cache[(view, True)] = read
                                    mind.memory._feature_rings[(view, True)] = mind.memory.ring(view)
                                with instrument(mind, costs):
                                    start = time.perf_counter()
                                    if operation == 'begin':
                                        mind.memory.begin(view)
                                    elif operation == 'refresh':
                                        mind.memory.refresh(grown)
                                    elif operation.startswith('ring'):
                                        mind.memory.ring(view)
                                    elif operation == 'features_many':
                                        mind.memory.features_many([view, grown])
                                    else:
                                        mind.memory.features(view)
                                    elapsed = time.perf_counter()-start
                        if repeat >= args.warmup:
                            values.append(elapsed)
                            attributions.append(costs)
                    item['operations'][operation] = {**summary(values), 'attribution': attributions}
                    totals[operation].extend(values)
                rows.append(item)
                print(f'{case}: {name}', flush=True)
            result['cases'][case] = dict(crutches=base.crutches, items=rows,
                                        aggregate={k: summary(v) for k, v in totals.items()})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf-8')
    print(args.out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--mode', choices=('native', 'reference'), default='native')
    parser.add_argument('--seed', type=int, default=3)
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--warmup', type=int, default=1)
    parser.add_argument('--task-wall', type=float, default=10.)
    parser.add_argument('--max-steps', type=int, default=8)
    args = parser.parse_args()
    if args.repeats < 1 or args.warmup < 0 or args.task_wall <= 0 or args.max_steps < 0:
        parser.error('Positive repeats/wall and nonnegative warmup/steps required')
    run(args)


if __name__ == '__main__':
    main()
