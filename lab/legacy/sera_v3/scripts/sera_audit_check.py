"""T-S (truth-v3 Decision 9, premise S; plan revision 3 T2; docs/SERA_FIELD_THEORY.md v1.1 §14): is SERA ever sure of
a wrong law when the true law's invented term was never imagined?

  python legacy/sera_v3/scripts/sera_audit_check.py --arm universe-1 --out D:/ai/labs/ccops5-sera-lab/sera-runs/ts-dev
  python legacy/sera_v3/scripts/sera_audit_check.py --arm wide       --out D:/ai/labs/ccops5-sera-lab/sera-runs/ts-dev
  python legacy/sera_v3/scripts/sera_audit_check.py --report         --out D:/ai/labs/ccops5-sera-lab/sera-runs/ts-dev

Pre-registered 2026-09-25 by development review, before any T-S run (only the audit's unit tests and a timing probe on three
teacher-throw ledgers were run before):
  worlds    dev seeds 1..10, split 'dream', start index 9101; the first N_WORLDS = 60 whose true law holds exactly one
            invented term that is not a cell (stage 1), taken level by level in turn over the levels 1..7 that yield
            such worlds (a fixed scan: seed-major, then index, then level).
  mind      SERA v4 (branch sera-v4: mind v3.2 + truth-v2 + the audit), imagination imagine-v1, eps 0.2, budget
            3 x situations, design on; mask = the true invented term and its one-step neighbours (MASK below), so the
            imagination can never propose it. The judge's audit is not masked.
  arms      'universe-1' (the policy under test) and 'wide' (truth-v2's T2 only: the control that shows what premise S
            cost), on the same worlds, each in its own process (the policy is read at import).
  bars      universe-1 arm only:
              (V) 0 sure claims contradicted: sure of A while the truth G does not contain A (grammar.contains);
              (C) the median CPU of the universe audit in the accepting certificate call <= 300 s.
            Every accepted certificate is re-checked by checker.check; a refusal counts against the arm.
  reported  sure and contradicted per arm; how often a rival the audit could not rule out joined the ledger ('new
            rival') and how often SERA then certified the truth; audit CPU per call; worlds with a narrow scope (x or v
            box below the arm's median width) separately (independent review: the 10-idea superset mimics more there).
Units are saved per world as JSON (a checkpoint); the report is generated from them.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

N_WORLDS = 60
SEEDS = range(1, 11)
START = 9101
LEVELS = range(1, 8)
EPS = 0.2
MODEL = 'imagine-v1'
RUNS = Path(os.environ.get('SERA_RUNS', 'D:/ai/labs/ccops5-sera-lab/sera-runs'))   # SERA_RUNS: another machine (Colab)


def _step(values, x):
    """The index distance of x from its neighbours on a sorted grid (None if not on it)."""
    return values.index(x) if x in values else None


def neighbours(term, universe, grammar):
    """MASK: the term and every universe term one grid step from it (same kind and inputs): a power's exponent, a
    drive's frequency, a piece's constant, or one part of a piece product one step of its constant."""
    out = {term}
    for u in universe:
        if u[0] != term[0] or u == term:
            continue
        if term[0] == 'power' and u[1] == term[1] and abs(u[2] - term[2]) <= 0.1 + 1e-9:
            out.add(u)
        elif term[0] == 'drive' and u[1] == term[1] and abs(u[2] - term[2]) <= 0.1 + 1e-9:
            out.add(u)
        elif term[0] == 'piece' and u[1] == term[1] and u[2] == term[2] and term[2] != 'abs':
            if abs(_step(grammar.PIECE_C, u[3]) - _step(grammar.PIECE_C, term[3])) == 1:
                out.add(u)
        elif term[0] == 'pprod':
            diff = [(a, b) for a, b in zip(u[1:], term[1:]) if a != b]
            if len(diff) == 1:
                a, b = diff[0]
                pa, pb = grammar.PART_NAMES.index(a), grammar.PART_NAMES.index(b)
                if a[:4] == b[:4] and a[:4] in ('tanh', 'bell') and abs(pa - pb) == 1:
                    out.add(u)
    return out


def _eligible(job):
    """One candidate of the scan: (seed, index, level) if its true law holds exactly one non-cell invented term."""
    import sys as _sys
    _sys.path.insert(0, os.getcwd())
    from ccops5.core import grammar as _g
    from legacy.sera_v3 import worlds as _SW
    seed, index, lv = job
    try:
        w = _SW.make(seed, index, lv, 'dream')
    except (RuntimeError, ValueError):
        return False
    opens = [t for t in w.spec.family if t not in _g.IDEAS]
    return len(opens) == 1 and opens[0][0] != 'cell'


def pick_worlds(SW, grammar, workers=None):
    """The fixed scan (see the docstring). A world build takes about 20 s, and the scan builds up to 280 per seed, so
    (2026-09-26) every T-S process spent hours picking worlds before its first life: SERA_WORLDS names a file holding
    the list (written by --scan), read instead of scanning; --scan runs the same scan with `workers` processes, each
    seed's candidates in the loop's order, so the list is the one the one-process scan gives."""
    cached = os.environ.get('SERA_WORLDS')
    if cached and os.path.exists(cached):
        return [tuple(x) for x in json.loads(Path(cached).read_text())]
    by_level = {lv: [] for lv in LEVELS}
    pool = None
    if workers and workers > 1:
        import multiprocessing as mp
        pool = mp.get_context('spawn' if os.name == 'nt' else 'fork').Pool(workers)
    for seed in SEEDS:
        jobs = [(seed, START + i, lv) for i in range(40) for lv in LEVELS]
        ok = pool.map(_eligible, jobs) if pool else [_eligible(j) for j in jobs]
        for job, good in zip(jobs, ok):
            if good:
                by_level[job[2]].append(job)
        levels = [lv for lv in LEVELS if by_level[lv]]
        if levels and min(len(by_level[lv]) for lv in levels) * len(levels) >= N_WORLDS:
            break
    if pool:
        pool.close()
    levels = [lv for lv in LEVELS if by_level[lv]]
    chosen, k = [], 0
    while len(chosen) < N_WORLDS:
        lv = levels[k % len(levels)]
        j = k // len(levels)
        if j < len(by_level[lv]):
            chosen.append(by_level[lv][j])
        k += 1
        if k > 100 * N_WORLDS:
            break
    return chosen


def _write_list(path, worlds):
    """Write the world list so a process reading it (SERA_WORLDS) never sees it half-written: every parallel process
    writes the same list at its start (2026-09-26: a plain write_text truncates first, so a reader could crash)."""
    text = json.dumps(worlds)
    if path.exists() and path.read_text() == text:
        return
    tmp = path.with_name(f'{path.name}.{os.getpid()}.tmp')
    tmp.write_text(text)
    os.replace(tmp, path)


def _claim(path):
    """Take the world whose unit is `path` for this process: True unless another process took it first. The claim
    file is created with O_EXCL (atomic), so K processes pulling from the one list take each world exactly once and
    none sits idle while another still has a fixed share left. A launcher clears *.claim before starting (a process
    that died leaves its claim; that world then shows as missing in the report)."""
    try:
        os.close(os.open(str(path.with_suffix('.claim')), os.O_CREAT | os.O_EXCL | os.O_WRONLY))
        return True
    except FileExistsError:
        return False


def run(arm, out, only=None, shard=None):
    os.environ['CCOPS5_AUDIT'] = arm
    import torch
    from ccops5.core import checker, grammar, truth
    from legacy.sera_v3 import imagine as I, mind as SM, worlds as SW
    assert truth.AUDIT == arm
    audit_cpu = []
    real = truth.universe_audit

    def timed(ledger, family, thr):
        t0 = time.process_time()
        try:
            return real(ledger, family, thr)
        finally:
            audit_cpu.append(time.process_time() - t0)

    truth.universe_audit = timed
    model = I.Imagination()
    model.load_state_dict(torch.load(RUNS / MODEL / 'model.pt', map_location='cpu'))
    model = model.float().eval()
    out = Path(out) / arm
    out.mkdir(parents=True, exist_ok=True)
    worlds = pick_worlds(SW, grammar)
    _write_list(out.parent / 'worlds.json', worlds)
    for seed, index, level in worlds:
        name = f's{seed}-i{index}-L{level}'
        if only and name not in only:
            continue
        path = out / f'{name}.json'
        if path.exists():
            continue
        if shard and not _claim(path):                                  # parallel processes: one shared queue
            continue
        w = SW.make(seed, index, level, 'dream')
        truth_fam = grammar.canonical(w.spec.family)
        t_g = next(t for t in truth_fam if t not in grammar.IDEAS)
        mask = neighbours(t_g, truth.UNIVERSE_TERMS, grammar)
        audit_cpu.clear()
        t0 = time.process_time()
        r = SM.Mind(model, w.sigma, eps=EPS, budget=3 * w.n_situations, design=True, mask=mask).live(w)
        cpu = time.process_time() - t0
        claim = grammar.canonical(r.claim)
        ok, why = (checker.check(r.certificate, r.ledger.throws, w.sigma) if r.sure else (None, []))
        unit = dict(world=name, level=level, truth=grammar.name(truth_fam), masked=len(mask),
                    claim=grammar.name(claim), sure=bool(r.sure),
                    contradicted=bool(r.sure and not grammar.contains(truth_fam, claim)),
                    right=bool(claim == truth_fam), checker_ok=ok, checker_why=list(why),
                    reasons=list(r.reasons), events=[str(e) for _, e in r.events],
                    truth_joined=any(t in mask for f in r.ledger.families for t in f),
                    audit_cpu=list(audit_cpu), cpu=cpu, throws=r.throws, scope=_scope(r.certificate),
                    audit=getattr(r.certificate, 'audit', None))
        path.write_text(json.dumps(unit, indent=1))
        print(f'{arm} {name}: truth {unit["truth"]}; claim {unit["claim"]} sure={unit["sure"]} '
              f'contradicted={unit["contradicted"]} audit {sum(audit_cpu):.0f}s total {cpu:.0f}s', flush=True)


def _scope(cert):
    s = cert.scope
    return {'x': list(s['x']), 'v': list(s['v']), 'not_audited': s.get('not_audited')}


def report(out):
    import statistics
    out = Path(out)
    lines = ['# T-S: the universe audit on masked-term dev worlds (generated by legacy/sera_v3/scripts/sera_audit_check.py)', '']
    for arm in ('universe-1', 'wide'):
        units = [json.loads(p.read_text()) for p in sorted((out / arm).glob('*.json'))]
        if not units:
            continue
        sure = [u for u in units if u['sure']]
        bad = [u for u in sure if u['contradicted']]
        refused = [u for u in sure if u['checker_ok'] is False]
        accept_cpu = [u['audit_cpu'][-1] for u in sure if u['audit_cpu']]
        widths = [u['scope']['x'][1] - u['scope']['x'][0] for u in units]
        med_w = statistics.median(widths) if widths else 0.0
        narrow = [u for u in units if u['scope']['x'][1] - u['scope']['x'][0] < med_w]
        lines += [f'## arm {arm}: {len(units)} worlds', '',
                  '| measure | value |', '|---|---|',
                  f'| sure | {len(sure)} |',
                  f'| sure and contradicted (bar V: 0) | {len(bad)} |',
                  f'| checker refusals of accepted certificates | {len(refused)} |',
                  f'| right law named | {sum(u["right"] for u in units)} |',
                  f'| a masked term joined the ledger (audit found it) | {sum(u["truth_joined"] for u in units)} |',
                  f'| ... and SERA then certified the truth | '
                  f'{sum(u["truth_joined"] and u["sure"] and u["right"] for u in units)} |',
                  f'| median audit CPU in the accepting call, s (bar C: <= 300) | '
                  f'{statistics.median(accept_cpu) if accept_cpu else float("nan"):.0f} |',
                  f'| median audit CPU per world (all calls), s | '
                  f'{statistics.median([sum(u["audit_cpu"]) for u in units]):.0f} |',
                  f'| narrow-scope worlds: sure / contradicted | {sum(u["sure"] for u in narrow)} / '
                  f'{sum(u["contradicted"] for u in narrow)} |', '']
        for u in bad:
            lines.append(f'- contradicted: {u["world"]} truth {u["truth"]}, claimed {u["claim"]}')
        lines.append('')
    (out / 'TS_REPORT.md').write_text('\n'.join(lines), encoding='utf-8')
    print('\n'.join(lines))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', choices=('universe-1', 'wide'))
    ap.add_argument('--out', default=str(RUNS / 'ts-dev'))
    ap.add_argument('--only', nargs='*')
    ap.add_argument('--shard', help='k/K: process k of K sharing one work queue (each takes the next world no process '
                    'has claimed; each world is its own life and unit, so the results do not depend on the split)')
    ap.add_argument('--report', action='store_true')
    ap.add_argument('--scan', type=int, default=0, help='N: run the world scan with N processes and write the '
                    'list to --out/worlds.json (then set SERA_WORLDS to it)')
    a = ap.parse_args()
    if a.scan:
        from ccops5.core import grammar as G
        from legacy.sera_v3 import worlds as W_
        Path(a.out).mkdir(parents=True, exist_ok=True)
        chosen = pick_worlds(W_, G, workers=a.scan)
        _write_list(Path(a.out) / 'worlds.json', chosen)
        print(f'{len(chosen)} worlds written to {Path(a.out) / "worlds.json"}')
    elif a.report:
        report(a.out)
    else:
        run(a.arm, a.out, a.only, tuple(int(x) for x in a.shard.split('/')) if a.shard else None)
