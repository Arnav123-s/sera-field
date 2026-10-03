"""US3: one-thread CPU live/read profile, including a pre-US3 scheduling control."""
import argparse
import copy
from contextlib import ExitStack
import json
import os
from pathlib import Path
import platform
import statistics
import sys
import time
from unittest.mock import patch

for name in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'NUMBA_NUM_THREADS'):
    os.environ[name] = '1'
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('CCOPS5_SHAPES', 'library')
os.environ.setdefault('CCOPS5_CLAIM', 'functional')
os.environ.setdefault('CCOPS5_BAND', 'claim')

import numpy as np
import torch

from sera import tasks as TS
from sera_u import SeraU
from sera_u.mind import Engine, U2_CRUTCHES, U3_CRUTCHES, U6_CRUTCHES, U7_CRUTCHES, arm_settings
from sera_u.memory import Memory, memory_records, public_context
from sera_u.ports import PortBudget


def reference_version(self, *, ring_only=False):
    """US2 invalidation cost, preserved here only as the profiling control."""
    owner, ideas = self.mind.owner, self.mind.field.ideas
    def versions(items):
        return tuple((key, id(value), value._version, value.data_ptr(), value.dtype, value.device,
                      tuple(value.shape)) for key, value in items)
    vocabulary = () if ring_only else (owner.port_enabled, id(owner.token_ids), len(owner.token_ids))
    return (self.a, self.b, vocabulary,
            id(ideas), ideas.rev, ideas._n, len(ideas._row), len(ideas.of),
            id(ideas._row), id(ideas.of), id(ideas._M), id(ideas._E),
            self._state_fingerprint(self.mind.state.items()) if self.a else (),
            versions(owner.named_parameters()), versions(owner.named_buffers()))


def reference_memory_checks(self, view, tags):
    with torch.no_grad():
        f, w, _ = self.proposer.owner.task_features(view, state=self.memory.mind.state,
                                                   ring=None, memory_read=True)
        a = self.proposer.owner.familiarity_readout(f, w, tuple(('part', tag) for _, tag in tags))
        kind, public = public_context(view)
        b, _ = self.field.familiarity(kind, public, tuple(tag for _, tag in tags), (),
                                     version='u2-public-v1' if view.form == 'exact' else 'context-v1')
        return [(part, float(value), b.get(tag, 0.)) for (part, tag), value in zip(tags, a)]


def fixtures(seed):
    # Fixed public tasks. Private world functions are used only by the world/judge.
    return [(f'number:{i}', TS.number_task(f'profile number {i}',
             lambda x, i=i: (i+1)*x+i, seed, 1000+i, words=())) for i in range(4)] + [
            (f'list:{i}', TS.list_task(f'profile list {i}',
             lambda xs, i=i: [x+i for x in xs[::-1]], 'list', seed, 1000+i, words=()))
            for i in range(4)]


def distribution(values):
    return dict(samples=values, median=statistics.median(values) if values else None,
                p95=float(np.percentile(values, 95)) if values else None)


def instrument(mind, reads, operations):
    """Inclusive API times overlap; actual observe rows are charged to the innermost read.

    Calls, requested views, and actual observed rows distinguish a cache hit from
    a shorter prefix/suffix read. Caller comes from the Python stack, not a label
    inferred from the task. Factual observations appear only in operations.
    """
    stack, active = ExitStack(), []
    def caller():
        frame, nearest = sys._getframe(2), None
        try:
            while frame is not None:
                filename, function = frame.f_code.co_filename, frame.f_code.co_name
                if filename.endswith(('mind.py', 'sleep.py')):
                    label = Path(filename).name + ':' + function
                    nearest = label if nearest is None else nearest
                    if function not in ('_u_reads', '_u_candidate_inputs', '_u_talk_inputs'):
                        return label
                frame = frame.f_back
            return nearest or 'other'
        finally:
            del frame
    def wrap_read(obj, name, many):
        original = getattr(obj, name)
        def measured(shown, *args, **kwargs):
            views = tuple(shown) if many else (shown,)
            row = dict(api=type(obj).__name__+'.'+name, caller=caller(), views=len(views),
                       records_requested=[len(memory_records(v)) for v in views],
                       records_observed=0, observe_calls=0, seconds=0.)
            reads.append(row)
            active.append(row)
            started = time.perf_counter()
            try:
                return original(views if many else shown, *args, **kwargs)
            finally:
                row['seconds'] = time.perf_counter()-started
                active.pop()
        # Proposer.__dict__ enters live()'s rollback checkpoint. Patch its CLASS
        # so local instrumentation closures never enter a serialized instance.
        original_class = getattr(type(obj), name)
        def dispatch(instance, shown, *args, **kwargs):
            if instance is obj:
                return measured(shown, *args, **kwargs)
            return original_class(instance, shown, *args, **kwargs)
        stack.enter_context(patch.object(type(obj), name, dispatch))
    # Capture demand, Memory single calls, and direct U6 A-only reads too.
    wrap_read(mind.proposer, 'features_many', True)
    wrap_read(mind.proposer, 'features', False)
    wrap_read(mind.memory, 'features', False)
    wrap_read(mind.owner, 'task_features', False)
    wrap_read(mind.owner, 'task_features_many', True)
    if hasattr(mind.owner, 'read_features_many'):
        wrap_read(mind.owner, 'read_features_many', True)
    for name in ('observe', 'conditional', 'encode_records', 'encode_record'):
        original = getattr(mind.owner, name)
        def measured(*args, _original=original, _name=name, **kwargs):
            if _name == 'observe' and active:
                active[-1]['records_observed'] += int(args[1].shape[0])
                active[-1]['observe_calls'] += 1
            started = time.perf_counter()
            try:
                return _original(*args, **kwargs)
            finally:
                operations.setdefault(_name, []).append(time.perf_counter()-started)
        stack.enter_context(patch.object(mind.owner, name, measured))
    return stack


def run(args):
    torch.set_num_threads(1)
    torch.set_num_interop_threads(1)
    torch.use_deterministic_algorithms(True)
    result = dict(mode=args.mode, seed=args.seed, device='cpu', threads=1,
                  python=platform.python_version(), torch=torch.__version__, platform=platform.platform(),
                  task_wall=args.task_wall, max_steps=args.max_steps,
                  history='fresh identical entity for each item; no bootstrap training',
                  units='seconds except counts and records', attribution='inclusive API seconds overlap', cases={})
    for readouts in (False, True):
        for memory in (False, True):
            mask = {**arm_settings('full'), **{k: memory for k in U2_CRUTCHES},
                    **{k: readouts for k in U3_CRUTCHES+U6_CRUTCHES+U7_CRUTCHES}}
            base = SeraU(args.seed, device='cpu', crutches=mask)
            snapshot = base.dumps()
            rows = []
            for name, task in fixtures(args.seed):
                for repeat in range(args.warmup+args.repeats):
                    mind = SeraU.loads(snapshot)
                    # This engineering control retains all US/US2 behavior. On
                    # the base without US3, setting the attribute has no effect.
                    mind.owner.readout_reuse_enabled = args.mode != 'reference'
                    reads, operations = [], {}
                    reader = mind.proposer
                    before = reader.stats['inference']
                    rec, failure = None, None
                    with ExitStack() as stack:
                        if args.mode == 'reference':
                            stack.enter_context(patch.object(Memory, '_read_version', reference_version))
                            stack.enter_context(patch.object(Engine, '_u_memory_checks', reference_memory_checks))
                        stack.enter_context(instrument(mind, reads, operations))
                        started = time.perf_counter()
                        try:
                            rec = mind.live(copy.deepcopy(task), task_wall=args.task_wall, max_steps=args.max_steps)
                        except PortBudget as exc:
                            failure = str(exc)
                        elapsed = time.perf_counter()-started
                    if repeat >= args.warmup:
                        counts = {}
                        for read in reads:
                            by_api = counts.setdefault(read['caller'], {})
                            by_api[read['api']] = by_api.get(read['api'], 0)+1
                        rows.append(dict(name=name, repeat=repeat-args.warmup, wall=elapsed,
                                         inference=reader.stats['inference']-before,
                                         proven=bool(rec and rec['proven']), steps=rec['steps'] if rec else None,
                                         failure=failure, reads=reads, read_counts_by_caller=counts,
                                         operations={k: distribution(v) for k, v in operations.items()}))
                print(f'readouts={readouts} memory={memory} {name}', flush=True)
            callers = sorted({(r['caller'], r['api']) for item in rows for r in item['reads']})
            by_caller = []
            for who, api in callers:
                selected = [r for item in rows for r in item['reads'] if (r['caller'], r['api']) == (who, api)]
                by_caller.append(dict(caller=who, api=api, calls=len(selected),
                    seconds_per_read=distribution([r['seconds'] for r in selected]),
                    records_observed_per_read=distribution([r['records_observed'] for r in selected]),
                    requested_views=sum(r['views'] for r in selected)))
            result['cases'][f'readouts-{int(readouts)}-memory-{int(memory)}'] = dict(
                crutches=mask, items=rows, wall=distribution([r['wall'] for r in rows]),
                inference=distribution([r['inference'] for r in rows]), reads_by_caller=by_caller)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False)+'\n', encoding='utf-8')
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
