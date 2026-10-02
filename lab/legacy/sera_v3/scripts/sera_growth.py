"""B4 gate (docs/B4_GROWTH.md; plan row 1): SERA grows what its language lacks, and the judge certifies it or says no.

  python legacy/sera_v3/scripts/sera_growth.py --name b4-dev --per-suite 8 --max-workers 1
Suites (seed 1, indices 9500+, never dreamed: the imagination knows only truth-v1's laws):
  L6     one grown piece alone (|s|, tanh(s/C), exp(-s^2/C), piece products)
  L7     one grown piece with one base idea
  noise  L0 worlds (no force at all): growth must never certify anything grown there
One unit = one world lived by SERA's mind with growth on (sera.mind.Mind(grow=True)), then the independent checker.
Pre-registered (before any B4 number):
  - sure and wrong (frozen core_check.wrong, cells by their eps-surface meaning) = 0 everywhere; checker refusals = 0;
  - noise: 0 grown claims certified;
  - L6/L7: the share grown AND certified, formulas and cells counted separately (a cell is never a formula
    discovery); the plan's target is >= 90% for the two together. Grid neighbours of the truth (the next C on the grid,
    grown_twin) are reported apart, not counted right or wrong.
  - Resolution stated: a grown claim is bounded down to the 33-knot spacing inside the knot ranges; finer, only the
    adequacy test guards (revision 5, T3).
"""
import argparse
import glob
import json
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
SUITES = (('L6', 6), ('L7', 7), ('noise', 0))


def run_unit(unit):
    folder, model_name, suite, level, i = unit
    path = Path(folder) / 'units' / f'{suite}-{i:02d}.json'
    if path.exists():
        return
    import torch
    torch.set_num_threads(1)
    from ccops5.core import checker, grammar
    import core_check
    from legacy.sera_v3 import imagine as I, mind as SM, worlds as SW
    rec = dict(suite=suite, index=i)
    try:
        w = SW.make(1, 9500 + i, level, 'any')
    except RuntimeError as e:                                 # the generator found no valid world: recorded, not hidden
        rec.update(no_world=str(e)[:300])
        _write(path, rec)
        return
    truth = grammar.canonical(w.spec.family)
    model = I.Imagination()
    model.load_state_dict(torch.load(RUNS / model_name / 'model.pt', map_location='cpu'))
    model.eval()
    t0 = time.perf_counter()
    r = SM.Mind(model, w.sigma, eps=EPS, budget=3 * w.n_situations, grow=True).live(w)
    cert = r.certificate
    verified = bool(r.sure and checker.check(cert, r.ledger.throws, w.sigma)[0])
    grown = any(t[0] in ('cell', 'piece', 'pprod') for t in r.claim)
    twin = bool(r.sure and len(r.claim) == len(truth) and r.claim != truth and all(
        a == b or SW.grown_twin(a, b) for a, b in zip(r.claim, truth)))
    rec.update(truth=grammar.name(truth), claim=grammar.name(r.claim), stage=r.stage, sure=r.sure, verified=verified,
               sure_unverified=bool(r.sure and not verified), grown_claim=grown,
               right_formula=bool(verified and r.stage == 'formula' and tuple(r.claim) == truth),
               right_cell=bool(verified and r.stage == 'cell' and not core_check.wrong(cert, w)),
               grid_twin=twin, wrong_frozen=bool(r.sure and core_check.wrong(cert, w)),
               band=cert.band, reasons=list(cert.reasons), alarm=r.alarm, growth=r.growth, throws=r.throws,
               own=r.own_pushes, certify_calls=r.certify_calls, families=r.families_tracked, gap=r.gap,
               events=[e for _, e in r.events], seconds=round(time.perf_counter() - t0, 1))
    _write(path, rec)


def _write(path, rec):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(rec, indent=1, default=str), encoding='utf-8')
    os.replace(tmp, path)


def summarize(folder):
    rows = [json.loads(Path(f).read_text(encoding='utf-8')) for f in sorted(glob.glob(str(Path(folder) / 'units' / '*.json')))]
    lines = ['| suite | worlds | no valid world | formula right | cell right | grid twin | grown claims | '
             'sure and wrong | checker refused | mean throws | mean seconds |', '|' + '---|' * 11]
    for suite, _ in SUITES:
        rs = [r for r in rows if r['suite'] == suite]
        lived = [r for r in rs if 'no_world' not in r]
        n = len(lived)
        mean = lambda k: sum(r[k] for r in lived) / n if n else 0.0
        lines.append(f"| {suite} | {n} | {len(rs) - n} | {sum(r['right_formula'] for r in lived)} | "
                     f"{sum(r['right_cell'] for r in lived)} | {sum(r['grid_twin'] for r in lived)} | "
                     f"{sum(r['grown_claim'] and r['sure'] for r in lived)} | {sum(r['wrong_frozen'] for r in lived)} | "
                     f"{sum(r['sure_unverified'] for r in lived)} | {mean('throws'):.1f} | {mean('seconds'):.0f} |")
    text = '\n'.join(lines) + '\n'
    (Path(folder) / 'summary.md').write_text(text, encoding='utf-8')
    return text


def main(argv=None):
    import governor
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', default='b4-dev')
    ap.add_argument('--model', default='imagine-v1')
    ap.add_argument('--per-suite', type=int, default=8)
    ap.add_argument('--max-workers', type=int, default=1)
    ap.add_argument('--suites', nargs='+', default=[s for s, _ in SUITES])
    a = ap.parse_args(argv)
    folder = RUNS / a.name
    (folder / 'units').mkdir(parents=True, exist_ok=True)
    units = [(str(folder), a.model, s, lv, i) for s, lv in SUITES if s in a.suites for i in range(a.per_suite)
             if not (folder / 'units' / f'{s}-{i:02d}.json').exists()]
    print(f'{len(units)} units to run in {folder}', flush=True)
    if units:
        governor.run_units(run_unit, units, a.max_workers, log=lambda s: print(s, flush=True))
    print(summarize(folder), flush=True)


if __name__ == '__main__':
    main()
