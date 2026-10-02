"""T-S2 (plan revision 4, R4-1), redesigned after the reviewer's review ((review notes, not published)): a judge-level stress test of the
universe audit (premise S). T-S never exercised the audit: in all 60 masked worlds an earlier certificate step refused
first. Here every world is chosen so that a WRONG base-space law passes every certificate step before the audit, and the
true law, outside the base space, is a live witness against it. Then only the audit stands between the judge and a
wrong "sure".

Pre-registered 2026-09-26 by development review, before any run of this script, and changed once, still before any run, after
the reviewer's review ((review notes, not published), "run with changes"): 8 objects, not 6 (with 6 the adequacy gate could never
refuse: its largest statistic is 9.0 < log(67/0.001) = 11.1); each refusal's first weak rival recorded as data and
attributed; a direct audit fit of the true law beside its witness; PASS fails closed; resumes are checked.
  worlds    constructed candidates, seeds 1..N_CAND = 400, each from its seed alone: a true law of one invented power
            term (input position or speed, exponent in LOOK = 0.8, 0.9, 1.1, 1.2, 2.8, 2.9, 3.1, 3.2 - near the base
            space's straight and cubic shapes), coefficient -U(0.5, 2) (restoring or damping), and with probability
            1/2 one base idea (a random one of the 11, coefficient -U(0.2, 1)); 8 objects, masses U(0.6, 2.5); two
            teacher pushes each (command +-0.5 or +-1, held 0.4, 0.8 or 1.2 s); sensor noise sigma in 0.003, 0.01,
            0.03 (both channels). A candidate whose paths leave |x| <= 5, |v| <= 10 is skipped.
  selection the judge and the truth only (never SERA), under the 'wide' audit policy (for a base-space claim it runs no
            audit, so it checks exactly the steps before the audit): the base ledger (grammar.space()) on the
            teacher's throws; its leader B (the ledger's own rule) is kept when
              (a) the truth does not contain B (a sure B would be contradicted);
              (b) certify(B, eps 0.2) accepts it (every in-ledger rival ruled out, adequacy, nested intervals, band);
              (c) truth.challenge refutes that certificate with the true law at its generating numbers (a live
                  witness: the true law's robust log-likelihood exceeds Q_B - thr(B)).
            Up to the first N_SEL = 30 kept, in seed order.
  test      on each kept world, a fresh ledger on the same throws, certify(B, eps 0.2, audit='universe-1').
  bars      (V) 0 of the kept worlds accepted under 'universe-1';
            (P) power: at least 10 worlds kept among the 400 candidates, else the verdict is "the construction cannot
                supply the challenge" (never "pass"). The verdict is valid with 10 to 30 kept.
            PASS fails closed: every kept world tested, exactly one audit call in each, the fresh ledger's leader and
            throws' digest equal to the selection's; anything else is INCONCLUSIVE, never PASS.
  reported  kept counts by term kind, exponent and noise (over the kept worlds only); for each test call its reasons,
            the audit's first weak rival and its reason code as data, attributed as: the true law / holds the true
            power term / unrelated / a fit failed; the witness margin; a direct audit fit of the true law (its gap
            Q_B - fit against thr(B): if the audit's own fit of the true law would rule it out, premise U failed
            there); the audit CPU (ordinary median over the refusing calls; bar C of T-S concerns accepting calls and
            is unassessed here). V = 0 with every refusal unrelated or failed is reported as "true-term detection
            unassessed". By construction the 'wide' policy accepts every kept world: that is the construction, not an
            independent result.
  python scripts/ts2_challenge.py <out folder> [workers]     (units per candidate; resumes only a folder whose
                                                              manifest matches this code and these constants)
"""
import json
import math
import os
import sys
import time
from pathlib import Path

os.environ['CCOPS5_AUDIT'] = 'wide'                     # the selection's policy; the test asks for universe-1 itself
os.environ['CCOPS5_AUDIT_WORKERS'] = '0'                # the one-process audit walk: the outer pool owns the processes,
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np                                      # noqa: E402

from ccops5.core import grammar, paths, truth, worlds as W   # noqa: E402

assert truth.AUDIT_WORKERS == 0                         # and process_time() then counts all of the audit's CPU

N_CAND, N_SEL, N_MIN, EPS, N_OBJ = 400, 30, 10, 0.2, 8
SCHEMA = 2
LOOK = (0.8, 0.9, 1.1, 1.2, 2.8, 2.9, 3.1, 3.2)
SIGMAS = (0.003, 0.01, 0.03)


def candidate(seed):
    """(true family, {term: coefficient}, masses, sigma, throws) from the seed alone, or None if paths run away."""
    rng = np.random.default_rng([2, 2, seed])
    term = ('power', str(rng.choice(['position', 'speed'])), float(rng.choice(LOOK)))
    coef = {term: -float(rng.uniform(0.5, 2.0))}
    if rng.random() < 0.5:
        idea = grammar.IDEAS[int(rng.integers(len(grammar.IDEAS)))]
        coef[idea] = -float(rng.uniform(0.2, 1.0))
    fam = grammar.canonical(tuple(coef))
    sig = float(rng.choice(SIGMAS))
    sigma = (sig, sig)
    masses = [float(rng.uniform(0.6, 2.5)) for _ in range(N_OBJ)]
    kk, aa, bb = grammar.codes(fam)
    c = np.array([coef[t] for t in fam])
    throws = []
    for k, m in enumerate(masses):
        for _ in range(2):
            act = W.Action(((0.0, float(rng.choice([0.4, 0.8, 1.2])), float(rng.choice([-1.0, -0.5, 0.5, 1.0]))),))
            xs, vs = paths.simulate_program(*act.arrays(), 1.0 / m, kk, aa, bb, c, 1.0, 1.0, 0.0, 0.0)
            if not (np.all(np.isfinite(xs)) and np.abs(xs).max() <= 5 and np.abs(vs).max() <= 10):
                return None
            throws.append(W.Throw(k, len(throws), act, xs + rng.normal(0, sig, xs.size),
                                  vs + rng.normal(0, sig, vs.size)))
    return fam, coef, masses, sigma, throws


def select(seed):
    """The selection (a)-(c) for one candidate: a dict saying why it is kept or not."""
    made = candidate(seed)
    if made is None:
        return dict(seed=seed, kept=False, why='paths leave the box')
    fam, coef, masses, sigma, throws = made
    unit = dict(seed=seed, truth=grammar.name(fam), sigma=sigma[0],
                term=[list(t) for t in fam if t not in grammar.IDEAS][0])
    led = truth.Ledger(grammar.space(), sigma)
    for t in throws:
        led.add(t)
    b = led.best_family()
    unit['leader'] = grammar.name(b)
    unit['digest'] = truth.digest(throws)
    if grammar.contains(fam, b):
        return dict(unit, kept=False, why='(a) the truth contains the leader')
    cert = truth.certify(led, b, EPS, audit='wide')
    if not cert.accepted:
        return dict(unit, kept=False, why='(b) ' + (cert.reasons[0] if cert.reasons else 'refused'))
    refuted, margin = truth.challenge(cert, fam, [coef[t] for t in fam], {k: 1.0 / m for k, m in enumerate(masses)},
                                      throws, sigma)
    if not isinstance(margin, float):
        return dict(unit, kept=False, why=f'(c) the witness is not admissible: {margin}')
    if not refuted:
        return dict(unit, kept=False, why=f'(c) no live witness (margin {margin:.3g})')
    return dict(unit, kept=True, why='kept', witness_margin=margin)


def test(seed):
    """The test on a kept world: the universe-1 certificate of the same leader on a fresh ledger, with the audit's
    first weak rival and reason code recorded as data (VTS2b 3) and a direct audit fit of the true law."""
    fam, coef, masses, sigma, throws = candidate(seed)
    led = truth.Ledger(grammar.space(), sigma)
    for t in throws:
        led.add(t)
    b = led.best_family()
    calls = []
    real = truth.universe_audit

    def recorded(*a, **k):
        t0 = time.process_time()
        out = None
        try:
            out = real(*a, **k)
            return out
        finally:
            weak = None if out is None else out[1]
            calls.append(dict(cpu=time.process_time() - t0, weak=None if weak is None else grammar.name(weak),
                              weak_family=None if weak is None else [list(x) for x in weak],
                              why=None if out is None else out[2]))
    truth.universe_audit = recorded
    try:
        cert = truth.certify(led, b, EPS, audit='universe-1')
    finally:
        truth.universe_audit = real
    term = [t for t in fam if t not in grammar.IDEAS][0]
    weak = tuple(tuple(x) for x in calls[0]['weak_family']) if len(calls) == 1 and calls[0]['weak_family'] else None
    if not calls:
        kind = 'no audit call'
    elif calls[0]['why'] == 'failed':
        kind = 'a fit failed'
    elif weak is None:
        kind = 'no weak rival (accepted)'
    elif grammar.canonical(weak) == fam:
        kind = 'the true law'
    elif term in weak:
        kind = 'holds the true power term'
    else:
        kind = 'unrelated'
    thr = grammar.log_threshold(b, 1e-3)
    fit = truth.audit_fit(led, fam, led.mle(b).mu, b)
    direct = led.q_claim(b) - fit.loglik if truth._usable(fit) else None
    return dict(seed=seed, leader=grammar.name(b), digest=truth.digest(throws), accepted=bool(cert.accepted),
                reasons=list(cert.reasons), audit_calls=calls, audit_cpu=[c['cpu'] for c in calls], first_weak=kind,
                thr=thr, direct_gap_true_law=direct,
                direct_fit_rules_out_truth=None if direct is None else bool(direct >= thr))


def _one(args):
    kind, seed, out = args
    path = Path(out) / f'{kind}-{seed:03d}.json'
    if path.exists():                                   # a resume keeps only this code's row for this seed (VTS2b 5)
        r = json.loads(path.read_text())
        if r.get('seed') == seed and r.get('schema') == SCHEMA:
            return r
    r = dict(select(seed) if kind == 'sel' else test(seed), schema=SCHEMA)
    path.write_text(json.dumps(r))
    return r


def _manifest():
    import hashlib
    code = b''.join(Path(p).read_bytes() for p in (__file__, truth.__file__, truth.L.__file__, grammar.__file__))
    return dict(schema=SCHEMA, code_sha256=hashlib.sha256(code).hexdigest(), n_cand=N_CAND, n_sel=N_SEL, n_min=N_MIN,
                eps=EPS, n_obj=N_OBJ, look=list(LOOK), sigmas=list(SIGMAS), audit=truth.AUDIT, band=truth.BAND,
                numerator=truth.NUMERATOR, knock=truth.L.KNOCK, audit_workers=truth.AUDIT_WORKERS)


def _median(xs):
    xs = sorted(xs)
    n = len(xs)
    return None if not n else (xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2]))


def main(out, workers=1):
    Path(out).mkdir(parents=True, exist_ok=True)
    man, mpath = _manifest(), Path(out, 'manifest.json')
    if mpath.exists() and json.loads(mpath.read_text()) != man:
        sys.exit(f'{out} was made by other code or constants: use a fresh folder')
    mpath.write_text(json.dumps(man, indent=1))
    pool = None
    try:
        if workers > 1:
            import multiprocessing as mp
            pool = mp.get_context('spawn' if os.name == 'nt' else 'fork').Pool(workers)
        run = (lambda jobs: pool.map(_one, jobs, chunksize=1)) if pool else (lambda jobs: [_one(j) for j in jobs])
        sel, seen = [], 0
        for lo in range(1, N_CAND + 1, 40):              # in blocks of 40 seeds, stopping once N_SEL are kept
            rows = run([('sel', s, out) for s in range(lo, min(lo + 40, N_CAND + 1))])
            seen += len(rows)
            sel += rows
            print(f'{time.strftime("%H:%M")} candidates {seen}, kept {sum(r["kept"] for r in sel)}', flush=True)
            if sum(r['kept'] for r in sel) >= N_SEL:
                break
        kept_rows = sorted((r for r in sel if r['kept']), key=lambda r: r['seed'])[:N_SEL]
        tests = run([('test', r['seed'], out) for r in kept_rows]) if kept_rows else []
    finally:
        if pool:
            pool.close()
            pool.join()
    by_seed = {t['seed']: t for t in tests}
    accepted = [t['seed'] for t in tests if t['accepted']]
    problems = [r['seed'] for r in kept_rows if r['seed'] not in by_seed
                or len(by_seed[r['seed']]['audit_calls']) != 1 or by_seed[r['seed']]['leader'] != r['leader']
                or by_seed[r['seed']]['digest'] != r['digest']]
    kinds = {}
    for t in tests:
        kinds[t['first_weak']] = kinds.get(t['first_weak'], 0) + 1
    if len(kept_rows) < N_MIN:
        verdict = f'the construction cannot supply the challenge (fewer than {N_MIN} kept)'
    elif accepted:
        verdict = f'FAIL: universe-1 accepted wrong laws in worlds {accepted}'
    elif problems:
        verdict = f'INCONCLUSIVE: incomplete or mismatched tests in worlds {problems}'
    else:
        found = kinds.get('the true law', 0) + kinds.get('holds the true power term', 0)
        verdict = 'PASS (V: 0 accepted)' + ('' if found else
                                            '; true-term detection unassessed (every refusal unrelated or failed)')
    why = {}
    for r in sel:
        k = r['why'].split(':')[0].split(' (margin')[0][:60]
        why[k] = why.get(k, 0) + 1
    terms = sorted({f'{r["term"][1]} {r["term"][2]}' for r in kept_rows})
    summary = dict(candidates_seen=seen, kept=len(kept_rows), tested=len(tests),
                   accepted_under_universe_1=len(accepted), verdict=verdict, why_not_kept=why,
                   first_weak_rival=kinds,
                   kept_by_sigma={str(s): sum(1 for r in kept_rows if r.get('sigma') == s) for s in SIGMAS},
                   kept_by_term={k: sum(1 for r in kept_rows if f'{r["term"][1]} {r["term"][2]}' == k) for k in terms},
                   direct_fit_rules_out_truth=sum(1 for t in tests if t['direct_fit_rules_out_truth']),
                   direct_fit_failed=sum(1 for t in tests if t['direct_gap_true_law'] is None),
                   median_refusing_audit_cpu=_median([sum(t['audit_cpu']) for t in tests if not t['accepted']]))
    Path(out, 'TS2_REPORT.json').write_text(json.dumps(dict(summary=summary, manifest=man, selected=kept_rows,
                                                            tests=tests), indent=1))
    print(json.dumps(summary, indent=1), flush=True)


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 1)
