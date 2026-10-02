"""B3 gate: SERA's mind against the M1 mind on the same real worlds, judged by the frozen judge and checker.

  python legacy/sera_v3/scripts/sera_check.py --name b3-dev --model imagine-v1 --per-suite 8 --max-workers 3
Suites (seed 1, fresh indices 9000+, teacher throws plus each mind's own pushes): L1..L5 (dreamed kinds) and
L3-held, L4-held (structures never dreamed). Both minds: eps 0.2 (as T5), invention on, the same push budget
(M1: 3 per object; SERA: 3 x objects in total, spent wherever it helps).
Per world and mind (one resumable unit = one JSON file in sera-runs/<name>/units/):
  claim, sure, verified (the independent checker accepts), right (sure, verified, the exact true law),
  surface_ok (sure, not the exact law, but the true force outside the claim is within eps where it looked),
  wrong (sure and neither), throws, own pushes, certificate calls, families tracked, seconds.
A summary table per suite and mind is written to sera-runs/<name>/summary.json and .md.

Mind 'sera31' (plan revision 2, P2; pre-registered 2026-09-25 before any sera31 run). The mind:
- designed push programs;
- no pushes on disturbed objects;
- committed predictions (foresight).

Each unit also records:
- the grade;
- the self-report and every statement's check;
- coverage of the 95% predictive intervals on the world's held-out check throws (no mind ever sees them);
- unsure_but_right (not sure, but its claim is the true law).

P2 gate, dev seed 1, the same suites and worlds as b3-dev2:
- unsure-but-right at most half of v3.0's ('sera' in b3-dev2), summed over L1-L4;
- right >= max(v3.0, M1) in each of L1-L4;
- mean throws <= v3.0's;
- 0 sure-and-wrong (frozen);
- 0 false self-report statements;
- check-throw coverage 0.93-0.97 over all sure worlds.

Grid suites are reported only. L3 holds products only. L4-03 has no valid world under the current rule.
"""
import argparse
import glob
import json

import numpy as np
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[2]))  # the repo root
sys.path.insert(0, str(ROOT.parents[2] / 'scripts'))  # governor, heat_guard
sys.path.insert(0, str(ROOT))
RUNS = Path('D:/ai/labs/ccops5-sera-lab/sera-runs')
EPS = 0.2
SUITES = [(f'L{lv}', lv, 'dream') for lv in range(1, 6)] + [('L3-held', 3, 'held'), ('L4-held', 4, 'held'),
          ('L3-grid', 3, 'any'), ('L4-grid', 4, 'any')]
GRID_SUITES = ('L3-grid', 'L4-grid')      # powers and drives only; scored within one grid step (review coverage point)


def run_unit(unit):
    folder, model_name, mind_name, suite, level, split, i = unit
    path = Path(folder) / 'units' / f'{suite}-{i:02d}-{mind_name}.json'
    if path.exists():
        return
    import torch
    torch.set_num_threads(1)
    from ccops5.core import checker, grammar, mind as M1
    import core_check
    from legacy.sera_v3 import imagine as I, mind as SM, worlds as SW
    grid = suite in GRID_SUITES
    w = SW.make(1, 9000 + i, level, split, ops=('power', 'drive') if grid else ('product', 'power', 'drive'), grid=grid)
    truth = grammar.canonical(w.spec.family)
    t0 = time.perf_counter()
    if mind_name in ('sera', 'sera31'):                  # sera31: v3.1, designed push programs (sera.design)
        model = I.Imagination()
        model.load_state_dict(torch.load(RUNS / model_name / 'model.pt', map_location='cpu'))
        model.eval()
        r = SM.Mind(model, w.sigma, eps=EPS, budget=3 * w.n_situations, design=mind_name == 'sera31').live(w)
        cert, claim, sure, throws, own = r.certificate, r.claim, r.sure, r.throws, r.own_pushes
        extra = dict(certify_calls=r.certify_calls, families=r.families_tracked, gap=r.gap,
                     imagined_top3=[[grammar.name(f), round(p, 3)] for f, p in r.proposals[:3]],
                     truth_in_imagined=truth in [f for f, _ in r.proposals],
                     ledger_throws=r.ledger.throws)
    else:
        r = M1.Mind(w.sigma, eps=EPS, invent=True).live(w)
        cert, claim, sure, throws, own = r.certificate, tuple(r.claim), r.sure, r.throws, r.own_pushes
        led = r.ledger
        if not sure and r.invention is not None and r.invention['certificate'].accepted:
            cert, claim, sure = r.invention['certificate'], tuple(r.invention['family']), True
            led = r.invention['ledger']
            own += r.invention['own']
            throws = len(led.throws)
        extra = dict(families=len(led.families), ledger_throws=led.throws)
    seconds = time.perf_counter() - t0
    verified = bool(sure and checker.check(cert, extra.pop('ledger_throws'), w.sigma)[0])
    exact = grammar.canonical(claim) == truth
    if mind_name == 'sera31':                             # plan revision 2 measures (P2 gate)
        from legacy.sera_v3 import express as E, grade as G
        g = G.grade(r.ledger, cert, verified, q_start=r.q_start, alarm=r.alarm)
        said = E.self_report(r, g)
        false = [s.text for s in said if not E.check(s, r, g)[0]]
        cover = n_read = 0
        for th in w.held_out:                             # predictions for pushes no mind ever saw, scored now
            lo, hi = r.ledger.interval(grammar.canonical(claim), th)
            y = np.concatenate([th.x, th.v])
            cover += int(np.sum((y >= lo) & (y <= hi)))
            n_read += y.size
        extra.update(unsure_but_right=bool(not sure and exact), flaw=bool(not verified and exact),
                     statements=len(said), false_statements=false, self_report=E.words(said),
                     check_coverage=cover / n_read if n_read else None, check_readings=n_read,
                     foresight_median=(float(np.median([f['leader_rms'] for f in r.foresight])) if r.foresight else None),
                     disturbed=[k for k, e in r.events if e == 'disturbed'],
                     questions={grammar.name(f): round(v, 1) for f, v in g.questions.items()})
    outside = w.residual_outside(cert) if sure else None
    rec = dict(suite=suite, index=i, mind=mind_name, truth=grammar.name(truth), claim=grammar.name(claim), sure=sure,
               verified=verified, right=bool(verified and exact),
               wrong_frozen=bool(sure and core_check.wrong(cert, w)), sure_unverified=bool(sure and not verified),
               right_grid=bool(verified and (exact or SW.grid_twin(claim, truth))),
               wrong_grid=bool(sure and not (exact or SW.grid_twin(claim, truth))),
               surface_ok=bool(verified and not exact and outside is not None and outside <= EPS),
               wrong=bool(sure and not exact and (outside is None or outside > EPS)),
               throws=throws, own=own, seconds=round(seconds, 1), **extra)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(rec, default=str, indent=1), encoding='utf-8')
    os.replace(tmp, path)


def summarize(folder):
    rows = [json.loads(Path(f).read_text(encoding='utf-8')) for f in glob.glob(str(Path(folder) / 'units' / '*.json'))]
    table = {}
    for r in rows:
        k = (r['suite'], r['mind'])
        t = table.setdefault(k, dict(n=0, right=0, surface_ok=0, wrong=0, wrong_frozen=0, sure_unverified=0, sure=0,
                                     throws=0, own=0, seconds=0.0, truth_imagined=0, max_calls=0))
        t['n'] += 1
        for key in ('right', 'surface_ok', 'wrong', 'wrong_frozen', 'sure_unverified', 'sure'):
            t[key] += int(bool(r.get(key)))
        t['max_calls'] = max(t['max_calls'], r.get('certify_calls', 0))
        t['throws'] += r['throws']
        t['own'] += r['own']
        t['seconds'] += r['seconds']
        t['truth_imagined'] += int(bool(r.get('truth_in_imagined')))
    lines = ['| suite | mind | worlds | right (exact, verified) | sure and wrong (frozen) | sure, checker refused | '
             'surface ok | mean throws | mean own pushes | mean seconds | truth among imagined 16 | max certificate calls |',
             '|' + '---|' * 12]
    order = [s for s, _, _ in SUITES]
    for (suite, mind), t in sorted(table.items(), key=lambda kv: (order.index(kv[0][0]), kv[0][1])):
        n = t['n']
        lines.append(f"| {suite} | {mind} | {n} | {t['right']}/{n} | {t['wrong_frozen']} | {t['sure_unverified']} | "
                     f"{t['surface_ok']} | {t['throws'] / n:.1f} | {t['own'] / n:.1f} | {t['seconds'] / n:.0f} | "
                     f"{t['truth_imagined'] if mind != 'm1' else '-'} | {t['max_calls'] if mind != 'm1' else '-'} |")
    (Path(folder) / 'summary.json').write_text(json.dumps({f'{s}|{m}': t for (s, m), t in table.items()}, indent=1))
    (Path(folder) / 'summary.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return '\n'.join(lines)


def main(argv=None):
    import governor
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', default='b3-dev')
    ap.add_argument('--model', default='imagine-v1')
    ap.add_argument('--per-suite', type=int, default=8)
    ap.add_argument('--max-workers', type=int, default=3)
    ap.add_argument('--minds', nargs='+', default=['sera', 'm1'])
    a = ap.parse_args(argv)
    folder = RUNS / a.name
    (folder / 'units').mkdir(parents=True, exist_ok=True)
    units = [(str(folder), a.model, m, s, lv, sp, i) for s, lv, sp in SUITES for i in range(a.per_suite)
             for m in a.minds if not (folder / 'units' / f'{s}-{i:02d}-{m}.json').exists()]
    print(f'{len(units)} units to run in {folder}', flush=True)
    if units:
        governor.run_units(run_unit, units, a.max_workers, log=lambda s: print(s, flush=True))
    print(summarize(folder), flush=True)


if __name__ == '__main__':
    main()
