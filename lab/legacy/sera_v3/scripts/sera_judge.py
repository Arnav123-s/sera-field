"""The judge's office (plan revision 5.1, sera.proofs): its workers prove the claims SERA's lives submit.

  python legacy/sera_v3/scripts/sera_judge.py --root /content/judge --workers 6 [--band claim]

Each worker is one process: it claims the oldest queued job, runs the full certificate and then the independent
checker on the job's ledger (truth.certify, checker.check: the calls the mind made inline), writes the result and
takes the next. The judge's policy is set here before the judge is imported, exactly as legacy/sera_v3/scripts/sera_life.py sets it
(--band must match the lives'); a job made under another policy is refused, never judged. One proof per process
(CCOPS5_AUDIT_WORKERS=0): the workers are the parallelism. Stops when <root>/STOP exists.
"""
import argparse
import multiprocessing as mp
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[2]))  # the repo root
sys.path.insert(0, str(ROOT.parents[2] / 'scripts'))  # governor, heat_guard


def worker(root, i):
    from legacy.sera_v3 import proofs as PR
    while not (Path(root) / 'STOP').exists():
        res = PR.work_one(root)
        if res is None:
            time.sleep(2.0)
            continue
        cert = res['cert']
        verdict = ('refused: ' + res['why']) if cert is None else \
            ('proven' if res['verified'] else 'accepted, checker refused' if cert.accepted else
             'refused: ' + (cert.reasons[0] if cert.reasons else '?'))
        print(f"office {i}: {res['key']} | {verdict} | cpu {res['cpu']}s wall {res['wall']}s", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--band', default='claim', choices=('claim', 'ui'))
    args = ap.parse_args()
    os.environ['CCOPS5_BAND'] = args.band
    os.environ['CCOPS5_AUDIT_WORKERS'] = '0'
    os.environ.setdefault('PYTHONHASHSEED', '0')
    from legacy.sera_v3 import proofs as PR
    root = Path(args.root)
    for d in ('queue', 'work', 'done'):
        (root / d).mkdir(parents=True, exist_ok=True)
    (root / 'STOP').unlink(missing_ok=True)
    PR.recover(root)
    print(f'office: {args.workers} workers on {root}, policy {PR.policy()}', flush=True)
    ctx = mp.get_context('fork' if os.name != 'nt' else 'spawn')
    procs = [ctx.Process(target=worker, args=(str(root), i)) for i in range(args.workers)]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    print('OFFICE STOPPED', flush=True)


if __name__ == '__main__':
    main()
