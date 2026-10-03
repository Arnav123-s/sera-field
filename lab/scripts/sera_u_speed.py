"""US benchmark: audited old/new paths, preflight fixtures, one CPU thread."""
import argparse
from dataclasses import replace
import json
import math
import os
from pathlib import Path
import platform
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('CCOPS5_SHAPES', 'library')
os.environ.setdefault('CCOPS5_CLAIM', 'functional')
os.environ.setdefault('CCOPS5_BAND', 'claim')

import torch

from sera import lang as LG
from sera_u import SeraU
from sera_u.mind import U2_CRUTCHES, arm_settings
from sera_u.ports import TaskView
from sera_u.sleep import Receipt, program_log_probability


def fixtures():
    """Same number/list views and target as sera_u_rsi.timed_preflight."""
    numeric = TaskView((('x', 'num'),), 'num',
                       tuple((((('x', x),)), x+1) for x in (-2, 0, 1, 4)),
                       queries=tuple((('x', x),) for x in range(-8, 12)))
    xs = ((), tuple(range(8)), tuple(range(-8, 0)), (2, -2, 0, 3))
    lists = TaskView((('x', 'list'),), 'list',
                     tuple((((('x', x),)), tuple(reversed(x))) for x in xs),
                     queries=tuple((('x', xs[j % 4]),) for j in range(20)))
    target = LG.node('add', LG.node('var', payload='x'), LG.node('one'))
    return numeric, lists, target


def sync(device):
    if device == 'cuda':
        torch.cuda.synchronize()


def make_base(device, seed, *, u2):
    settings = {**arm_settings('full'), **{k: u2 for k in U2_CRUTCHES}}
    mind = SeraU(seed, device=device, crutches=settings)
    numeric, lists, target = fixtures()
    # Explicit derivative fixtures, just like preflight; not pilot wake evidence.
    receipt = Receipt.make(numeric, (target,), {}, scope='exact-audit', origin='taught',
                           source='preflight-fixture')
    mind.checked_wake.add(receipt.id)
    mind.sleep.admit(receipt, {})
    with mind.scope():
        loss = -program_log_probability(mind.proposer, numeric, (target,), {})
        mind.optimizer.zero_grad(set_to_none=True)
        loss.backward()
    with torch.no_grad():
        mind.owner.task_features(lists)
    return mind


def clone(snapshot, batching):
    mind = SeraU.loads(snapshot)
    mind.batched_reads = batching
    return mind


def measure(snapshot, operation, *, device, repeats, warmup):
    results, last = {}, {}
    for label, batching in (('old', False), ('new', True)):
        times = []
        for j in range(warmup+repeats):
            mind = clone(snapshot, batching)  # loading is deliberately outside the timer
            sync(device)
            start = time.perf_counter()
            output = operation(mind)
            sync(device)
            elapsed = time.perf_counter()-start
            if j >= warmup:
                times.append(elapsed)
            last[label] = (mind, output)
        results[label] = dict(seconds=times, median_seconds=statistics.median(times))
    results['speedup'] = results['old']['median_seconds']/max(results['new']['median_seconds'], 1e-12)
    return results, last


def read(mind, shown):
    with torch.no_grad():
        # The ordinary single-view read is deliberately unchanged and audited.
        return mind.owner.task_features(shown)


def dream_check(mind):
    with mind.scope():
        return mind.sleep.check_dreams()


def run(args):
    if args.device == 'cuda' and not torch.cuda.is_available():
        raise ValueError('Requested CUDA device is unavailable')
    torch.set_num_threads(1)
    torch.use_deterministic_algorithms(True)
    if args.device == 'cuda':
        torch.cuda.reset_peak_memory_stats()
    base = make_base(args.device, args.seed, u2=args.u2)
    snapshot = base.dumps()
    numeric, lists, _ = fixtures()
    options = dict(device=args.device, repeats=args.repeats, warmup=args.warmup)
    result = dict(schema='sera-u-speed-1', seed=args.seed, device=args.device,
                  threads=torch.get_num_threads(), source=base.source, code=base.code,
                  u2=args.u2, audit='unchanged pinned audited Field on every path',
                  runtime=dict(machine=platform.platform(), processor=platform.processor(),
                               torch=torch.__version__),
                  fixtures='preflight: four examples, twenty queries; lists through length eight',
                  repeats=args.repeats, warmup=args.warmup,
                  clone_load_in_timing=False, measurements={})
    for label, shown in (('one_number_read', numeric), ('one_list_read', lists)):
        timing, outputs = measure(snapshot, lambda m: read(m, shown), **options)
        for a, b in zip(outputs['old'][1][:2], outputs['new'][1][:2]):
            torch.testing.assert_close(a, b, atol=1e-6, rtol=0.)
        result['measurements'][label] = timing
    # Exactly preflight's train(1, 8): eight draws of its sole numeric fixture.
    timing, outputs = measure(snapshot, lambda m: m.train(1, 8), **options)
    old_mind, old_rows = outputs['old']
    new_mind, new_rows = outputs['new']
    for key in ('program', 'objective'):
        if not math.isclose(old_rows[0][key], new_rows[0][key], abs_tol=1e-6, rel_tol=0.):
            raise ValueError('Training objective parity failed: '+key)
    result['measurements']['train_1_8'] = timing
    result['train_parameter_max_abs_difference'] = max(
        float((p-dict(new_mind.owner.named_parameters())[name]).abs().max())
        for name, p in old_mind.owner.named_parameters())
    result['cpu_train_target_seconds'] = 12.
    result['cpu_train_target_met'] = (timing['new']['median_seconds'] <= 12.
                                      if args.device == 'cpu' else None)
    # Check a batch of distinct dream views, not just repeated replay slots.
    with base.scope():
        made = base.sleep.dream(8, attempts=512)
    if not made:
        raise ValueError('No independently checked dreams in the preflight fixture')
    dream_snapshot = base.dumps()
    timing, outputs = measure(dream_snapshot, dream_check, **options)
    torch.testing.assert_close(outputs['old'][1], outputs['new'][1], atol=1e-6, rtol=0.)
    result['measurements']['dream_check'] = timing
    result['dream_check_count'] = len(made)
    result['dream_check_scope'] = 'optional Field log-probability diagnostic; no factual evidence'
    # Generation itself remains symbolic, with no Field observations or reads.
    def generate(mind):
        with mind.scope():
            return mind.sleep.dream(8, attempts=512)
    timing, outputs = measure(snapshot, generate, **options)
    if outputs['old'][1] != outputs['new'][1]:
        raise ValueError('Symbolic dream generation changed')
    result['measurements']['symbolic_dream_generation'] = timing
    result['gpu_batching_gained'] = (result['measurements']['train_1_8']['speedup'] > 1.
                                   and result['measurements']['dream_check']['speedup'] > 1.
                                   if args.device == 'cuda' else None)
    result['gpu_peak_bytes'] = torch.cuda.max_memory_allocated() if args.device == 'cuda' else 0
    # Supplemental variety: replay from eight unique copies of the numeric view,
    # differing only in public query counts, so padding is included in the timing.
    varied = clone(snapshot, True)
    _, _, target = fixtures()
    for j in range(7):
        shown = replace(numeric, queries=numeric.queries[:j+1])
        receipt = Receipt.make(shown, (target,), {}, scope='exact-audit', origin='taught',
                               source='preflight-variety:'+str(j))
        varied.checked_wake.add(receipt.id)
        varied.sleep.admit(receipt, {})
    timing, _ = measure(varied.dumps(), lambda m: m.train(1, 8), **options)
    result['measurements']['train_1_8_varied_queries'] = timing
    path = Path(args.out)
    if path.suffix.lower() != '.json':
        path = path/'speed.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False)+'\n', encoding='utf-8')
    print(json.dumps(dict(path=str(path), measurements=result['measurements'],
                          cpu_train_target_met=result['cpu_train_target_met'],
                          gpu_batching_gained=result['gpu_batching_gained']), sort_keys=True), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--device', choices=('cpu', 'cuda'), default='cpu')
    parser.add_argument('--seed', type=int, default=3)
    parser.add_argument('--out', default=None, help='Output directory or speed.json path')
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--warmup', type=int, default=1)
    parser.add_argument('--u2', action='store_true', help='Also enable A, B and Field understanding')
    args = parser.parse_args()
    if args.repeats < 1 or args.warmup < 0:
        parser.error('repeats >= 1 and warmup >= 0 required')
    if args.out is None:
        args.out = 'sera-runs/us-speed-'+args.device+('-u2' if args.u2 else '')
    run(args)


if __name__ == '__main__':
    main()
