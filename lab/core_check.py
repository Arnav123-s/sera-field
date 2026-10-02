"""M1 checks for the one-mind core (written before the code; see M1_DESIGN.md §5).

Step M1a covers the truth layer: C1 honest noise, C6 humility sweep, C8 omitted mechanism, C10 (the API form:
"sure" needs an accepted certificate) and C11 the independent checker. C2-C5, C7 and C9 are added with M1b-M1d.

"Sure and wrong" = an accepted certificate whose family is not the world's true family, or whose bound on a
nested term excludes the true value (0), or whose "something else" band is smaller than the force it left out.

    python core_check.py --seed 1                 one dev seed, all M1a checks
    python core_check.py --seed 1 --checks C1 C11
    python core_check.py --seeds 11 12 ... 20     fresh seeds (run once, after the design is frozen)
    python core_check.py --seed 1 --twice         run twice; the two results must match (D5)
"""
import argparse
import copy
import dataclasses
import json
import os
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import numpy as np

from ccops5.core import checker, grammar, truth, worlds

ALPHA = DELTA = 1e-3
EPS = 0.1
FORCE_WORLDS = ('rubbing', 'water drag', 'dry friction', 'thick oil', 'spring', 'tight spring', 'stiff spring',
                'swing', 'valley', 'slope')
OUTSIDE = ('v^1.5 drag', 'x*v force', 'motor')   # forces no family in the grammar can express
# (the motor, a force that swings in time, was added during M1b: it makes C8 stricter)
WORKERS = int(os.environ.get('CORE_WORKERS', '12'))   # 16 CPUs here; 4 left for other work (was 8)


def _world_job(spec):
    """One world in a worker process: (world, accepted certificates, alarms). `eps` may be a tuple: the world's
    ledger is then built once and every family is certified at each eps (same numbers as separate worlds)."""
    seed, force, index, noise, tricks, eps = spec
    w = worlds.make(seed, force, index=index, noise=noise, tricks=tricks)
    _, accepted, alarms = run_world(w, eps=eps)
    return w, accepted, alarms


def _pool_map(fn, items):
    with Pool(WORKERS) as pool:
        return pool.map(fn, items)


def run_many(specs):
    return _pool_map(_world_job, specs)


def run_world(world, try_all=True, eps=EPS):
    """Feed the world's throws to a ledger one situation at a time. At the end of each situation, attempt to
    certify every family in the idea space (the strongest adversary: validity may not depend on which
    families the mind happens to try). Returns every accepted certificate and the last alarm. With a tuple of
    eps, `accepted` is a dict eps -> accepted certificates."""
    ledger = truth.Ledger(grammar.space(), world.sigma)
    many = isinstance(eps, tuple)
    epss = eps if many else (eps,)
    accepted, alarms = {e: [] for e in epss}, []
    for sit in world.situations():
        for throw in sit:
            ledger.add(throw)
        families = grammar.space() if try_all else [world.truth]
        for e in epss:
            for fam in families:
                cert = truth.certify(ledger, fam, eps=e, alpha=ALPHA, delta=DELTA)
                if cert.accepted:
                    accepted[e].append(cert)
        best = ledger.best_family()
        alarms.append(truth.something_else(ledger, best, alpha=ALPHA)[0])
    return ledger, (accepted if many else accepted[eps]), alarms


def wrong(cert, world):
    """Is this accepted certificate sure and wrong about this world?"""
    if any(term[0] in ('cell', 'shape') for term in cert.family):   # truth-v2 (B4-5): a curve (Decision 12: or SERA's own shape) is never the exact law; it
        if any(not truth.zero_inside(iv) for iv in cert.nested.values()):     # is wrong when the true force outside
            return True                                                        # it exceeds eps where it looked
        return world.residual_outside(cert) > cert.eps
    if world.truth is not None and tuple(cert.family) != tuple(world.truth):
        return True
    if any(not truth.zero_inside(iv) for iv in cert.nested.values()):
        return True
    return world.residual_outside(cert) > cert.eps      # a force it left out exceeds its band


# ---------------------------------------------------------------- C1: honest noise
def _coverage_job(spec):
    """(readings inside the 95% interval, readings) for one force world's held-out throws."""
    seed, force, i = spec
    w = worlds.make(seed, force, index=i, tricks=0.0)
    ledger = truth.Ledger(grammar.space(), w.sigma)
    for throw in w.throws:
        ledger.add(throw)
    inside = total = 0
    for throw in w.held_out:
        lo, hi = ledger.interval(w.truth, throw, level=0.95)
        y = np.concatenate([throw.x, throw.v])
        inside += int(np.sum((y >= lo) & (y <= hi)))
        total += y.size
    return inside, total


def check_c1(seed):
    """(a) 95% predictive intervals of held-out readings under the true family's fitted numbers cover 93-97%.
    (b) Pure-noise worlds (the hand only, bumps on): no force term is ever certified, the alarm never fires."""
    counts = _pool_map(_coverage_job, [(seed, force, i) for i, force in enumerate(FORCE_WORLDS)])
    inside, total = sum(c[0] for c in counts), sum(c[1] for c in counts)
    coverage = inside / total
    noise_certs, noise_alarms = 0, 0
    for w, accepted, alarms in run_many([(seed, 'none', 100 + i, 1.0, 0.05, EPS) for i in range(8)]):
        noise_certs += sum(1 for c in accepted if len(c.family) > 0)
        noise_alarms += sum(alarms)
    ok = 0.93 <= coverage <= 0.97 and noise_certs == 0 and noise_alarms == 0
    return ok, {'coverage': round(coverage, 4), 'readings': total,
                'noise_worlds_force_certified': noise_certs, 'noise_worlds_alarms': noise_alarms}


# ---------------------------------------------------------------- C6: humility sweep
def check_c6(seed):
    """As the signal weakens (more sensor noise, tighter tolerance), the share of worlds it is sure about falls,
    and it is never sure and wrong."""
    sure_share, n_wrong = {}, 0
    # Fixture changed 2026-09-24 (seed-1 run on d5b3b48): with eps 0.2/0.1/0.05 and the teacher's pushes only, the
    # bands (0.16-0.45) never fit, so every share was 0 and the check passed vacuously. The eps grid now spans the
    # bands, and the check also requires a non-zero share at the strongest signal (a stricter assertion).
    noises, epss = (1.0, 2.0, 4.0, 8.0), (0.8, 0.5, 0.3)
    settings = [(noise, eps) for noise in noises for eps in epss]
    forces = ('rubbing', 'water drag', 'spring', 'slope')
    # One ledger per (noise, world), certified at the three eps (2026-09-24: before, each eps rebuilt the same world).
    specs = [(seed, force, 200 + i, noise, 0.05, epss) for noise in noises for i, force in enumerate(forces)]
    results = dict(zip([(noise, i) for noise in noises for i in range(len(forces))], run_many(specs)))
    for noise, eps in settings:
        sure = 0
        for i in range(len(forces)):
            w, accepted_by_eps, _ = results[(noise, i)]
            accepted = accepted_by_eps[eps]
            n_wrong += sum(wrong(c, w) for c in accepted)
            sure += any(tuple(c.family) == tuple(w.truth) for c in accepted)
        sure_share[f'noise x{noise:g}, eps {eps:g}'] = sure / len(forces)
    shares = np.array(list(sure_share.values())).reshape(4, 3)
    monotone = bool(np.all(np.diff(shares, axis=0) <= 1e-9) and np.all(np.diff(shares, axis=1) <= 1e-9))
    not_vacuous = bool(shares[0, 0] > 0)
    return monotone and not_vacuous and n_wrong == 0, {'sure_share': sure_share, 'sure_and_wrong': n_wrong,
                                                       'not_vacuous': not_vacuous}


# ---------------------------------------------------------------- C8: omitted mechanism
def check_c8(seed):
    """A force no family can express: it says "something else is here" in >= 95% of the worlds where that force
    exceeds eps over the scope, and it is never sure and wrong."""
    fired = eligible = n_wrong = 0
    for w, accepted, alarms in run_many([(seed, OUTSIDE[i % len(OUTSIDE)], 300 + i, 1.0, 0.05, EPS) for i in range(12)]):
        n_wrong += sum(wrong(c, w) for c in accepted)
        if w.effect_size() > EPS:
            eligible += 1
            fired += int(alarms[-1])
    rate = fired / max(eligible, 1)
    return rate >= 0.95 and n_wrong == 0, {'alarm_rate': round(rate, 3), 'eligible_worlds': eligible,
                                            'sure_and_wrong': n_wrong}


# ---------------------------------------------------------------- C10: "sure" needs an accepted certificate
def check_c10(seed):
    """The API form (the temptation world with credit comes in M1d): a claim becomes "sure" only through the
    library, which runs the checker; there is no other way to set it."""
    w = worlds.make(seed, 'rubbing', index=400, tricks=0.0)
    ledger = truth.Ledger(grammar.space(), w.sigma)
    for throw in w.throws[:2]:                      # far too little data to be sure
        ledger.add(throw)
    cert = truth.certify(ledger, w.truth, eps=EPS, alpha=ALPHA, delta=DELTA)
    tempted = dataclasses.replace(cert, accepted=True)          # a learner that simply declares itself sure
    library = truth.Library(w.sigma)
    refused = not library.record(tempted, w.throws[:2])
    try:
        claim = library.claims[-1] if library.claims else None
        if claim is not None:
            claim.sure = True                        # the flag must not be writable from outside
        writable = claim is not None and claim.sure
    except (AttributeError, dataclasses.FrozenInstanceError, TypeError):
        writable = False
    return refused and not writable, {'forged_sure_refused': refused, 'sure_flag_writable': writable}


# ---------------------------------------------------------------- C11: the independent checker
def forgeries(cert, throws):
    """Twenty ways to lie in a certificate, each with the stored throws it would be checked against."""
    f = []

    def alt(**kw):
        return dataclasses.replace(cert, **kw)

    rivals = dict(cert.rivals)
    some = sorted(rivals)[0]
    f.append(('missing rival', alt(rivals={k: v for k, v in rivals.items() if k != some}), throws))
    f.append(('inflated e-value', alt(rivals={**rivals, some: rivals[some] + 50.0}), throws))
    f.append(('laxer alpha', alt(alpha=0.2), throws))
    f.append(('smaller eps than band', alt(eps=cert.band * 0.5), throws))
    f.append(('band understated', alt(band=cert.band * 0.2), throws))
    f.append(('no band at all', alt(band=None), throws))
    if cert.nested:
        k0 = sorted(cert.nested)[0]
        lo, hi = cert.nested[k0]
        f.append(('narrower nested interval', alt(nested={**cert.nested, k0: (lo / 4, hi / 4)}), throws))
        f.append(('dropped nested term', alt(nested={k: v for k, v in cert.nested.items() if k != k0}), throws))
    else:
        f.append(('invented nested term', alt(nested={('speed', 'cubic'): (0.0, 0.0)}), throws))
        f.append(('invented nested term 2', alt(nested={('position', 'wave'): (-1e-9, 1e-9)}), throws))
    # widen the ranges only (fixed 2026-09-24, session 2: since D10 the scope also holds the visited 'cells', a list,
    # and unpacking it as a range crashed C11 before any forgery was checked)
    wide = {k: ((v[0] - 5.0, v[1] + 5.0) if k in ('x', 'v') else v) for k, v in cert.scope.items()}
    f.append(('widened scope', alt(scope=wide), throws))
    # A family that really is another one (fixed 2026-09-24: the fixed pick ('speed', 'growing') was the water-drag
    # fixture's own true family, so this "forgery" was the genuine certificate and was rightly accepted).
    other = next(f for f in grammar.space() if f and f != grammar.canonical(cert.family)
                 and not grammar.contains(f, cert.family))
    f.append(('other family', alt(family=other), throws))
    f.append(('empty family', alt(family=()), throws))
    tampered = copy.deepcopy(throws)
    tampered[3].x[10] += 0.05
    f.append(('altered reading', cert, tampered))
    f.append(('dropped throw', cert, throws[:-1]))
    f.append(('reordered throws', cert, throws[1:] + throws[:1]))
    f.append(('added throw', cert, throws + [copy.deepcopy(throws[0])]))
    f.append(('digest of other data', alt(digest='0' * len(cert.digest)), throws))
    f.append(('delta laxer', alt(delta=0.3), throws))
    f.append(('accepted flag without numbers', alt(rivals={}, nested={}, band=None), throws))
    f.append(('claims all rivals at threshold 0', alt(rivals={k: 0.0 for k in rivals}), throws))
    f.append(('scope from no data', alt(scope={}), throws))
    # D10 (2026-09-24): the scope is the visited cells; a claim may not speak for cells it never visited.
    if cert.scope.get('cells'):
        cells = list(cert.scope['cells'])
        extra = next(((i, j) for i in range(truth.GRID) for j in range(truth.GRID) if (i, j) not in set(cells)), None)
        if extra is not None:
            f.append(('unvisited cell added', alt(scope={**cert.scope, 'cells': tuple(sorted(cells + [extra]))}), throws))
        f.append(('cells dropped', alt(scope={**cert.scope, 'cells': tuple(cells[: len(cells) // 2])}), throws))
    # D9 (2026-09-24): the claim's prior is recomputed by the checker from the grammar.
    f.append(('prior overstated', alt(log_prior=cert.log_prior + 2.0), throws))
    f.append(('prior missing', alt(log_prior=None), throws))
    return f


def _check_job(spec):
    cert, throws, sigma = spec
    return checker.check(cert, throws, sigma)


def check_c11(seed):
    """The checker accepts a real certificate, rejects every forgery, and cannot be reached from learner code."""
    # Fixture (changed 2026-09-22 after the first runs, assertions unchanged): 20 situations and eps 0.5, so a
    # genuine certificate exists to forge. With 10 situations the band was 0.3-0.5, above the old eps 0.2.
    w = worlds.make(seed, 'water drag', index=500, situations=20, tricks=0.0)
    ledger = truth.Ledger(grammar.space(), w.sigma)
    for throw in w.throws:
        ledger.add(throw)
    cert = truth.certify(ledger, w.truth, eps=0.5, alpha=ALPHA, delta=DELTA)
    forged = forgeries(cert, w.throws)              # checked in parallel: each checker call is independent
    jobs = [(cert, w.throws, w.sigma)] + [(c, data, w.sigma) for _, c, data in forged] + [(cert, w.throws, w.sigma)]
    verdicts = _pool_map(_check_job, jobs)           # the real certificate first and last (the repeat check)
    real_ok, why = verdicts[0]
    results = {name: acc for (name, _, _), (acc, _) in zip(forged, verdicts[1:-1])}
    passed_forgeries = [n for n, acc in results.items() if acc]
    # The checker imports no learner module, and learner code cannot change what it will say.
    probe = subprocess.run([sys.executable, '-c',
                            'import sys; sys.dont_write_bytecode = True; import ccops5.core.checker; '
                            'print(",".join(sorted(m for m in sys.modules if m.startswith("ccops5"))))'],
                           capture_output=True, text=True, cwd=ROOT, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    loaded = set(filter(None, probe.stdout.strip().split(',')))
    learner = sorted(m for m in loaded if any(m.endswith(x) for x in ('.mind', '.gut', '.credit', '.teacher')))
    again = verdicts[-1][0]
    ok = real_ok and cert.accepted and not passed_forgeries and not learner and again == real_ok
    return ok, {'real_certificate_accepted': real_ok, 'why_if_not': why if not real_ok else [],
                'forgeries': len(results), 'forgeries_accepted': passed_forgeries, 'learner_modules_loaded': learner}


# ---------------------------------------------------------------- T5: growth by invention (B3; written before the code)
T5_EPS = 0.2


def _term_matches(term, hidden):
    """An invented term is right if it is the hidden term's operator and input (or sin/cos), with its number
    (exponent or frequency) within 0.15; products must match exactly."""
    if term[0] != hidden[0] or term[1] != hidden[1]:
        return False
    if term[0] == 'product':
        return term[2] == hidden[2]
    return abs(float(term[2]) - float(hidden[2])) <= 0.15


def _t5_job(spec):
    from ccops5.core import curriculum, mind
    seed, kind, index = spec
    w = curriculum.make_world(seed, kind, index, situations=8, tricks=0.05)
    r = mind.Mind(w.sigma, eps=T5_EPS, budget=2, invent=True).live(w)
    inv = r.invention
    accepted = False
    if inv is not None and inv['certificate'].accepted:
        accepted = truth.Library(w.sigma).record(inv['certificate'], inv['ledger'].throws)
    family = tuple(inv['family']) if inv is not None else ()
    invented = [t for t in family if t not in grammar.IDEAS]
    hidden = tuple(getattr(w, 'hidden_terms', ()) or ())
    right = bool(accepted and hidden and len(invented) == 1 and _term_matches(invented[0], hidden[0]))
    return {'kind': kind, 'index': index, 'effect': float(w.effect_size()) if kind != 'none' else 0.0,
            'alarm': bool(r.alarm), 'invented': grammar.name(family) if inv is not None else None,
            'accepted': bool(accepted), 'right': right, 'wrong': bool(accepted and not right),
            'proposals': [p['name'] for p in (inv['proposals'] if inv else [])][:3],
            'own_pushes': r.own_pushes + (inv['own'] if inv else 0)}


def check_t5(seed):
    """Growth (Architecture §12, T5): in worlds whose force no base family can express (effect > eps), it invents
    and certifies the missing term in >= 90%; in pure-noise worlds it never certifies an invention; never sure and
    wrong. Invention runs only when the alarm fires."""
    from ccops5.core import curriculum
    specs = [(seed, kind, 600 + i) for kind in curriculum.SURPRISES for i in range(4)]
    specs += [(seed, 'none', 700 + i) for i in range(6)]
    rows = _pool_map(_t5_job, specs)
    eligible = [r for r in rows if r['kind'] != 'none' and r['effect'] > T5_EPS]
    grown = sum(r['right'] for r in eligible)
    noise_growth = sum(r['accepted'] for r in rows if r['kind'] == 'none')
    wrong = sum(r['wrong'] for r in rows)
    rate = grown / max(len(eligible), 1)
    ok = bool(eligible) and rate >= 0.9 and noise_growth == 0 and wrong == 0
    return ok, {'eligible': len(eligible), 'grown_right': grown, 'rate': round(rate, 3),
                'noise_growth': noise_growth, 'sure_and_wrong': wrong, 'worlds': rows}


CHECKS = {'C1': check_c1, 'C6': check_c6, 'C8': check_c8, 'C10': check_c10, 'C11': check_c11, 'T5': check_t5}


def commit_of_code():
    try:
        return subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True,
                              cwd=ROOT).stdout.strip() or 'unknown'
    except OSError:
        return 'unknown'


def run(seed, names, folder=None, pass_no=1, resume=False, commit='unknown'):
    """Each check's result is saved the moment it finishes (a killed run loses at most the check it was in).
    With `resume`, a saved result is reused only if the same commit produced it."""
    out = {}
    for name in names:
        part = None if folder is None else Path(folder) / f'core_check_seed{seed}.{name}.pass{pass_no}.json'
        if resume and part is not None and part.exists():
            saved = json.loads(part.read_text(encoding='utf-8'))
            if saved.get('commit') == commit and commit != 'unknown':
                out[name] = saved['result']
                print(f'seed {seed} {name}: {"PASS" if saved["result"]["pass"] else "FAIL"} (pass {pass_no}, '
                      f'saved by {commit}, not re-run)', flush=True)
                continue
        started = time.perf_counter()
        ok, detail = CHECKS[name](seed)
        out[name] = {'pass': bool(ok), 'detail': detail, 'seconds': round(time.perf_counter() - started, 1)}
        print(f'seed {seed} {name}: {"PASS" if ok else "FAIL"}  {json.dumps(detail, default=str)}', flush=True)
        if part is not None:
            part.write_text(json.dumps({'commit': commit, 'result': out[name]}, indent=1, default=str),
                            encoding='utf-8')
    return out


def strip_times(res):
    return {k: {kk: vv for kk, vv in v.items() if kk != 'seconds'} for k, v in res.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seed', type=int)
    ap.add_argument('--seeds', type=int, nargs='+')
    ap.add_argument('--checks', nargs='+', default=list(CHECKS))
    ap.add_argument('--twice', action='store_true')
    ap.add_argument('--out', default='core-results')
    ap.add_argument('--resume', action='store_true', help='reuse checks already saved by this same commit')
    a = ap.parse_args()
    if os.environ.get('PYTHONHASHSEED') != '0':
        sys.exit('set PYTHONHASHSEED=0 first (decision D5)')
    seeds = a.seeds or [a.seed if a.seed is not None else 1]
    Path(a.out).mkdir(parents=True, exist_ok=True)
    commit = commit_of_code()
    all_pass = True
    for seed in seeds:
        res = run(seed, a.checks, a.out, 1, a.resume, commit)
        if a.twice:
            again = run(seed, a.checks, a.out, 2, a.resume, commit)
            same = json.dumps(strip_times(res), sort_keys=True, default=str) == \
                json.dumps(strip_times(again), sort_keys=True, default=str)
            print(f'seed {seed}: two runs {"MATCH" if same else "DIFFER"}')
            all_pass &= same
        all_pass &= all(r['pass'] for r in res.values())
        (Path(a.out) / f'core_check_seed{seed}.json').write_text(
            json.dumps({**res, '_run': {'commit': commit, 'twice': a.twice}}, indent=1, default=str), encoding='utf-8')
    print('ALL PASS' if all_pass else 'SOME CHECKS FAIL (read the numbers above, not just this line)')
    sys.exit(0 if all_pass else 1)


if __name__ == '__main__':
    main()
