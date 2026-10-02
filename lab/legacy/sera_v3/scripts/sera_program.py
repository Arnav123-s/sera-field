"""The whole program of plan revision 5 after Stage 0, stage after stage, unattended (revision 5.1).

  python legacy/sera_v3/scripts/sera_program.py --life /content/sera-1 --seed 1 --office /content/judge [--after-pid PID]

Every stage is a legacy/sera_v3/scripts/sera_life.py process (the same code a stage runs alone), in this order:
  teach -> the Stage 1 check (2 shards) with the S1 yardstick on a snapshot (2 shards) -> practice (150 worlds in
  blocks of 30; before each block the teacher's rule re-weights the doors toward what SERA keeps failing) -> the S2
  yardstick -> alone (24 h or a plateau) -> the S3 yardstick -> the fresh-seed yardstick (seed 11, once) -> v3.1 on
  the same fresh worlds (the reference) -> Stage 5, new doors (rooms and code; the same SERA, on this machine, because
  its memory lives here).
A stage that halts on a tripwire (exit 3) stops the program; any other failure stops it too. Each finished stage is
recorded in <life>/PROGRAM.jsonl and never run again, so the driver can be restarted. --after-pid: wait for that
process (a stage already running) before starting. The judge's office must be running (legacy/sera_v3/scripts/sera_judge.py).
--deadline H (Colab: the machine's age in hours by which everything must be done; runtimes end near 24 h): Stage 3
gets the time left before it, less a reserve for the last yardsticks, at most --hours.

The teacher's rule (plan revision 5, Stage 2: "re-weight the door mix toward what SERA keeps failing"), fixed here
before any Stage 2 world: a door's weight is 0.1 + its failure share over the last block (1 - the share of its
judged worlds proven right or proven surface); a door not met in the block keeps its weight. The 0.1 keeps every
door, the easy one too (forgetting would show there).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # the repo root
PROVEN = ('proven right', 'proven, surface')
MIX0 = {'1': 0.2, '2': 0.35, '3': 0.15, '4': 0.2, '5': 0.1}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--life', required=True)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--office', required=True)
    ap.add_argument('--after-pid', type=int, default=None)
    ap.add_argument('--practice', type=int, default=150)
    ap.add_argument('--block', type=int, default=30)
    ap.add_argument('--hours', type=float, default=24.0)
    ap.add_argument('--fresh-seed', type=int, default=11)
    ap.add_argument('--deadline', type=float, default=None)
    ap.add_argument('--reserve', type=float, default=3.5, help='hours kept for S3, fresh and v3.1')
    ap.add_argument('--newdoors', type=float, default=4.0, help='hours kept for Stage 5 (0: none)')
    args = ap.parse_args()
    life = Path(args.life)
    base = life.parent
    logs = Path('/content/logs') if Path('/content').exists() else life / 'logs'
    logs.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONHASHSEED='0', PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1',
               OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', NUMBA_NUM_THREADS='1',
               PYTHONPATH=str(ROOT), SERA_RUNS=str(ROOT / 'sera-runs'))
    env.setdefault('NUMBA_CACHE_DIR', str(base / 'numba-cache'))
    record = life / 'PROGRAM.jsonl'
    life.mkdir(parents=True, exist_ok=True)
    done = set()
    if record.exists():
        done = {json.loads(l)['stage'] for l in record.read_text().splitlines() if l.strip()}

    def note(stage, **kw):
        with open(record, 'a') as f:
            f.write(json.dumps(dict(stage=stage, t=time.strftime('%Y-%m-%d %H:%M:%S'), **kw)) + '\n')
        done.add(stage)
        print(f'PROGRAM {stage} done {kw}', flush=True)

    def run(name, jobs):
        """Run sera_life.py processes in parallel: jobs = [(log name, [args...])]; stop the program unless all exit 0."""
        procs = []
        for log, a in jobs:
            cmd = [sys.executable, 'legacy/sera_v3/scripts/sera_life.py', '--office', args.office, '--seed', str(args.seed)] + a
            procs.append((log, subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=open(logs / f'{log}.log', 'a'),
                                                stderr=subprocess.STDOUT)))
            print(f'PROGRAM {name}: started {log}: {" ".join(a)}', flush=True)
        codes = {log: p.wait() for log, p in procs}
        if any(codes.values()):
            print(f'PROGRAM STOPPED at {name}: exit codes {codes} (3 = a tripwire; see the logs)', flush=True)
            raise SystemExit(1)

    def snapshot(label):
        d = base / f'yard-{label}'
        (d / 'units').mkdir(parents=True, exist_ok=True)
        shutil.copy(life / 'agent.pkl', d / 'agent.pkl')
        return d

    def yard(label, d, extra=()):
        return [(f'yard-{label}.{k}', ['--out', str(d), '--stage', 'yardstick', '--label', label, '--shard', f'{k}/2',
                                       *extra]) for k in range(2)]

    if args.after_pid:
        while Path(f'/proc/{args.after_pid}').exists():
            time.sleep(30)
    if 'teach' not in done:
        run('teach', [('prog-teach', ['--out', str(life), '--stage', 'teach'])])
        note('teach')
    if 'check+S1' not in done:
        d = snapshot('S1')
        run('check+S1', [(f'prog-check.{k}', ['--out', str(life), '--stage', 'check', '--shard', f'{k}/2'])
                         for k in range(2)] + yard('S1', d))
        check = json.loads((life / 'check.json').read_text()) if (life / 'check.json').exists() else None
        note('check+S1', check=check and check['verdict'])
    mix = dict(MIX0)
    if (life / 'mix.json').exists():
        mix = json.loads((life / 'mix.json').read_text())
    while f'practice-{args.practice}' not in done:
        n = max([0] + [int(s.split('-')[1]) for s in done if s.startswith('practice-')])
        target = min(n + args.block, args.practice)
        if n:                                               # the teacher's rule, from the last block's judged worlds
            last = [json.loads(p.read_text()) for p in sorted((life / 'units').glob('practice-*.json'))
                    if '-look' not in p.name and n - args.block <= int(p.stem.split('-')[1]) < n]
            for door in sorted({str(u['door']) for u in last}):
                us = [u for u in last if str(u['door']) == door]
                mix[door] = round(0.1 + 1 - sum(u['verdict'] in PROVEN for u in us) / len(us), 3)
        (life / 'mix.json').write_text(json.dumps(mix))
        run(f'practice-{target}', [('prog-practice', ['--out', str(life), '--stage', 'practice', '--worlds',
                                                      str(target), '--mix', str(life / 'mix.json')])])
        note(f'practice-{target}', mix=mix)
    if 'S2' not in done:
        run('S2', yard('S2', snapshot('S2')))
        note('S2')
    if 'alone' not in done:
        hours = args.hours
        if args.deadline is not None and Path('/proc/uptime').exists():
            age = float(Path('/proc/uptime').read_text().split()[0]) / 3600
            hours = round(max(0.5, min(args.hours, args.deadline - age - args.reserve - args.newdoors)), 2)
        run('alone', [('prog-alone', ['--out', str(life), '--stage', 'alone', '--hours', str(hours)])])
        note('alone', hours=hours)
    if 'S3' not in done:
        d = snapshot('S3')
        run('S3', yard('S3', d))
        note('S3')
    if 'fresh' not in done:
        d = snapshot('fresh')
        run('fresh', yard('fresh', d, ['--yard-seed', str(args.fresh_seed)]) +
            [(f'yard-v31.{k}', ['--out', str(base / 'yard-v31'), '--stage', 'yardstick', '--label', 'v31', '--mind',
                                'v31', '--yard-seed', str(args.fresh_seed), '--shard', f'{k}/2']) for k in range(2)])
        note('fresh')
    if args.newdoors > 0 and 'newdoors' not in done:
        hours = args.newdoors
        if args.deadline is not None and Path('/proc/uptime').exists():
            age = float(Path('/proc/uptime').read_text().split()[0]) / 3600
            hours = round(max(0.5, args.deadline - age - 0.3), 2)
        run('newdoors', [('prog-newdoors', ['--out', str(life), '--stage', 'newdoors', '--hours', str(hours)])])
        note('newdoors', hours=hours)
    print('PROGRAM DONE', flush=True)


if __name__ == '__main__':
    main()
