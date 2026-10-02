"""T-D8 (docs/D8_BAND_TEST.md section 5, pre-registered 2026-09-26 in 5bd45bd): (a) the band ratio 'claim' / 'ui' on
the 15 saved P2 ledgers (bar: median <= 0.85); (b) planted-spring coverage over seeds 1-200 (bar: 200/200).
  python scripts/t_d8.py a <out.json>     |   python scripts/t_d8.py b <out.json> [first last]"""
import json
import math
import statistics
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ccops5.core import grammar, paths, truth, worlds as W        # noqa: E402

UNITS = Path('D:/ai/labs/ccops5-sera-lab/sera-runs/b3-dev2/units')
DELTA = 1e-3 / 67
EPS = 0.2


def _names():
    from sera import field as F
    out = {grammar.name(f): f for f in grammar.space()}
    out.update({grammar.name(f): f for f in F.LAWS})
    return out


def part_a(out):
    names, rows = _names(), []
    for p in sorted(UNITS.glob('*-sera31.json')):
        d = json.loads(p.read_text())
        if 'ledger_throws' not in d:
            continue
        ns = {'Throw': W.Throw, 'Action': W.Action, 'array': np.array}
        throws = [eval(t, ns) for t in d['ledger_throws']]           # the lab's own saved reprs
        fam = names[d['claim']]
        sigma = tuple(d.get('sigma', (1e-3, 1e-3)))
        scope = truth.scope_of(throws)
        ui = truth.band_of(throws, fam, sigma, scope, DELTA)
        q_a = truth.prequential(truth.model_of(fam), throws, sigma)[0]
        cl = truth.band_of(throws, fam, sigma, scope, DELTA, q_ref=q_a)
        rows.append(dict(unit=p.name[:-12], claim=d['claim'], right=bool(d['right']), band_ui=ui, band_claim=cl,
                         ratio=cl / ui if ui and math.isfinite(ui) and math.isfinite(cl) else None))
        print(json.dumps(rows[-1]), flush=True)
    ratios = [r['ratio'] for r in rows if r['ratio'] is not None]
    med = statistics.median(ratios)
    summary = dict(n=len(rows), median_ratio=med, bar='median <= 0.85', passed=med <= 0.85,
                   below_eps_ui=sum(r['band_ui'] <= EPS for r in rows),
                   below_eps_claim=sum(r['band_claim'] <= EPS for r in rows))
    print(json.dumps(summary), flush=True)
    Path(out).write_text(json.dumps(dict(rows=rows, summary=summary), indent=1))


def _spring_throws(k, seed, situations=3, pushes=(4.0, -2.5, 1.5, -4.0)):
    fam = grammar.canonical((('speed', 'straight'), ('position', 'straight')))
    kk, aa, bb = grammar.codes(fam)
    coef = np.array([-0.5 if t == ('speed', 'straight') else k for t in fam])
    rng = np.random.default_rng(seed)
    out = []
    for s in range(situations):
        m = float(rng.uniform(0.8, 2.0))
        for j, u in enumerate(pushes):
            act = W.Action(((0.0, 1.2, float(u)),))
            xs, vs = paths.simulate_program(*act.arrays(), 1 / m, kk, aa, bb, coef, 1.0, 1.0, 0.0, 0.0)
            nr = np.random.default_rng([seed, s, j])
            out.append(W.Throw(s, len(out), act, xs + nr.normal(0, 1e-3, xs.size), vs + nr.normal(0, 1e-3, vs.size)))
    return out


def part_b(out, first=1, last=200):
    drag = grammar.canonical((('speed', 'straight'),))
    sigma, rows = (1e-3, 1e-3), []
    for seed in range(first, last + 1):
        rng = np.random.default_rng([8, seed])
        probe = _spring_throws(0.0, seed)
        sc = truth.scope_of(probe)
        xs = np.linspace(sc['x'][0], sc['x'][1], truth.GRID)
        k = float(rng.uniform(1.0, 3.0)) * EPS / max(abs(xs[i]) for i, _ in sc['cells']) * float(rng.choice([-1, 1]))
        throws = _spring_throws(k, seed)
        scope = truth.scope_of(throws)
        xs = np.linspace(scope['x'][0], scope['x'][1], truth.GRID)
        planted = max(abs(k * xs[i]) for i, _ in scope['cells'])
        q_a = truth.prequential(truth.model_of(drag), throws, sigma)[0]
        band = truth.band_of(throws, drag, sigma, scope, DELTA, q_ref=q_a)
        rows.append(dict(seed=seed, k=k, planted=planted, band=band, covered=bool(band >= planted)))
        print(json.dumps(rows[-1]), flush=True)
    summary = dict(n=len(rows), covered=sum(r['covered'] for r in rows), bar='all covered',
                   passed=all(r['covered'] for r in rows))
    print(json.dumps(summary), flush=True)
    Path(out).write_text(json.dumps(dict(rows=rows, summary=summary), indent=1))


if __name__ == '__main__':
    if sys.argv[1] == 'a':
        part_a(sys.argv[2])
    else:
        part_b(sys.argv[2], *(int(x) for x in sys.argv[3:5]))
