"""Golden for truth-v2 (docs/B4_GROWTH.md, B4-4): on base families, every number the judge computes must be identical
to truth-v1's. Run the same measurements under both code trees and compare.

  python scripts/golden_v2.py --v1 (review notes, not published) --out D:/ai/tools/tmp/golden
Measured per world (sera.worlds levels 1-2, seed 1, indices 0-3, 3 situations): every base family's prequential Q and
MLE log-likelihood; the leader's certificate: rival e-values, nested intervals, band, adequacy, log prior; the alarm.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

MEASURE = r'''
import json, sys
import numpy as np
from ccops5.core import grammar, truth
from sera import worlds as SW
out = {}
for level in (1, 2):
    for i in range(4):
        w = SW.make(1, i, level, situations=3)
        led = truth.Ledger(grammar.space(), w.sigma)
        for t in w.throws:
            led.add(t)
        fams = led.families
        rec = {'Q': {repr(f): led.Q[f] for f in fams}, 'mle': {repr(f): led.mle(f).loglik for f in fams}}
        leader = led.best_family()
        c = truth.certify(led, leader, 0.2)
        rec['cert'] = dict(family=repr(leader), accepted=bool(c.accepted), rivals={repr(k): v for k, v in c.rivals.items()},
                           nested={repr(k): v for k, v in c.nested.items()}, band=c.band, adequacy=c.adequacy,
                           log_prior=c.log_prior, reasons=list(c.reasons))
        rec['alarm'] = list(truth.something_else(led, leader))
        out[f'L{level}-{i}'] = rec
from ccops5.core import curriculum
for kind, term in (('x*v force', ('product', 'straight', 'straight')), ('v^p drag', None), ('motor', None)):
    w = curriculum.make_world(1, kind, 600, situations=3)
    term = term or w.hidden_terms[0]
    led = truth.Ledger(grammar.space(inventions=(term,)), w.sigma)
    for t in w.throws:
        led.add(t)
    fams = led.families
    out['T5-' + kind] = {'Q': {repr(f): led.Q[f] for f in fams}, 'mle': {repr(f): led.mle(f).loglik for f in fams},
                         'log_prior': {repr(f): grammar.log_prior(f) for f in fams if any(x not in grammar.IDEAS for x in f)}}
json.dump(out, open(sys.argv[1], 'w'), default=float)
'''


def run(tree, path):
    env = dict(os.environ, PYTHONPATH=str(tree), PYTHONHASHSEED='0', NUMBA_CACHE_DIR=str(Path(path).parent / ('nc-' + Path(tree).name)))
    subprocess.run([sys.executable, '-c', MEASURE, str(path)], env=env, cwd=str(tree), check=True)
    return json.loads(Path(path).read_text())


def compare(a, b, where=''):
    diffs = []
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                diffs.append(f'{where}/{k}: missing')
            else:
                diffs += compare(a[k], b[k], f'{where}/{k}')
    elif isinstance(a, list):
        if len(a) != len(b):
            return [f'{where}: length']
        for i, (x, y) in enumerate(zip(a, b)):
            diffs += compare(x, y, f'{where}[{i}]')
    elif a != b:
        diffs.append(f'{where}: {a} != {b}')
    return diffs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--v1', required=True)
    ap.add_argument('--out', default='D:/ai/tools/tmp/golden')
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    v2 = Path(__file__).resolve().parents[1]
    g1 = run(Path(a.v1), out / 'v1.json')
    g2 = run(v2, out / 'v2.json')
    shifts = []                                  # T5-kind worlds: open families' log prior moves by exactly -log 2
    for k in [k for k in g1 if k.startswith('T5-')]:
        for f, lp1 in g1[k].pop('log_prior').items():
            lp2 = g2[k]['log_prior'].get(f)
            shifts.append(None if lp2 is None else lp2 - lp1)
        g2[k].pop('log_prior')
    import math
    bad = [s for s in shifts if s is None or abs(s + math.log(2)) > 1e-12]
    print(f'{len(shifts)} open families on T5-kind worlds: log prior shift -log 2 exactly in {len(shifts) - len(bad)}')
    diffs = compare(g1, g2)
    print(f'{len(diffs)} differences' + (':\n' + '\n'.join(diffs[:40]) if diffs else ' (bit-identical on base families)'))
    (out / 'diffs.txt').write_text('\n'.join(diffs))


if __name__ == '__main__':
    main()
