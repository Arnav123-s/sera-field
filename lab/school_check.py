"""Checks for the teaching layer (M1_DESIGN.md §4d), written before the School code (2026-09-24).

They read saved School lives (`school_run.py` writes `life-seed<S>-<arm>.json`) and one live world, and apply the
pass bars fixed in advance (Architecture §12, T3; the plan's C12 and C13):

C9  zero-shot (T3)  taught arms against `untaught`, on the same seeds:
    (a) hints reach 0: no hinted world in the last 20 practice worlds with the teacher, in >= 90% of taught lives;
    (b) after the teacher leaves, tries keep falling: the slope of tries over the teacher-free worlds, pooled over
        lives with a per-life intercept, is below 0 with a 95% interval (reported for every taught arm; passes if
        the best taught arm passes);
    (c) never-shown kinds (exam): right-first share of the best taught arm >= untaught + 15 points.
C12 words           (a) the ledger and the certificate are identical with words on and off (one live world);
                    (b) filler words ground in 0 lives;
                    (c) a regime word heard in >= 8 checked worlds grounds in >= 90% of such (word, life) pairs;
                    (d) on exam worlds of practised kinds where the word was said, first-try right with the
                        word prior >= without it + 15 points (timed-words arms);
                    (e) registered prediction, reported, not a bar: timed words ground in fewer worlds than
                        random-time words.
C13 board           (a) the evidence is identical with the board on and off (one live world);
                    (b) deposits without a checked source are refused (claim not in the library, unregistered
                        correction, alarm below threshold);
                    (c) placement reads only the board: the same board state gives the same template whatever the
                        world's hidden truth;
                    (d) the thin trace: after 200 evaporations every trail is still >= its floor.
Every check also counts sure-and-wrong over all saved worlds; any sure-and-wrong fails the check.

    python school_check.py --results core-results/school-dev
"""
import argparse
import json
import math
import os
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import numpy as np

TAUGHT = ('answer', 'why', 'why+timed', 'why+random', 'why+trails', 'full')
TIMED = ('why+timed', 'full')
RANDOM = ('why+random',)
FILLERS = ('look', 'nice', 'oops', 'again')


def load(folder):
    lives = {}
    for p in sorted(Path(folder).glob('life-seed*-*.json')):
        d = json.loads(p.read_text(encoding='utf-8'))
        lives[(d['seed'], d['arm_name'])] = d
    return lives


def sure_and_wrong(lives):
    return sum(w.get('sure_and_wrong', False) for d in lives.values() for w in d['worlds'])


def _slope_ci(points):
    """Slope of y on x with a per-life intercept (within-life centring), and its 95% interval."""
    xs, ys = [], []
    for life in points:
        if len(life) < 3:
            continue
        x = np.array([p[0] for p in life], float)
        y = np.array([p[1] for p in life], float)
        xs.append(x - x.mean())
        ys.append(y - y.mean())
    if not xs:
        return None
    x, y = np.concatenate(xs), np.concatenate(ys)
    sxx = float(x @ x)
    if sxx == 0:
        return None
    b = float(x @ y) / sxx
    resid = y - b * x
    dof = max(len(x) - len(xs) - 1, 1)
    se = math.sqrt(float(resid @ resid) / dof / sxx)
    return b, b - 1.96 * se, b + 1.96 * se


def check_c9(lives):
    arms = sorted({a for _, a in lives})
    seeds = sorted({s for s, _ in lives})
    detail = {'arms': arms, 'seeds': seeds, 'by_arm': {}}
    if 'untaught' not in arms:
        return False, {**detail, 'why': 'no untaught arm'}

    def never_shown_first(arm):
        hits = [w['rank'] == 1 for s in seeds if (s, arm) in lives for w in lives[(s, arm)]['worlds']
                if w['phase'] == 'exam' and w['never_shown']]
        return (sum(hits) / len(hits)) if hits else None

    base = never_shown_first('untaught')
    best = None
    for arm in arms:
        if arm not in TAUGHT:
            continue
        runs = [lives[(s, arm)] for s in seeds if (s, arm) in lives]
        hint_free = [not any(w['hinted'] for w in [w for w in d['worlds'] if w['phase'] == 'taught'][-20:])
                     for d in runs]
        slope = _slope_ci([[(w['n'], w['rank']) for w in d['worlds'] if w['phase'] == 'alone'] for d in runs])
        zs = never_shown_first(arm)
        row = {'lives': len(runs), 'hint_free_share': round(sum(hint_free) / max(len(runs), 1), 3),
               'alone_slope': None if slope is None else [round(v, 4) for v in slope],
               'never_shown_right_first': None if zs is None else round(zs, 3)}
        row['a'] = row['hint_free_share'] >= 0.9
        row['b'] = slope is not None and slope[2] < 0
        row['c'] = zs is not None and base is not None and zs - base >= 0.15
        detail['by_arm'][arm] = row
        if best is None or (zs or 0) > (detail['by_arm'][best]['never_shown_right_first'] or 0):
            best = arm
    detail['untaught_never_shown_right_first'] = None if base is None else round(base, 3)
    detail['best_arm'] = best
    wrong = sure_and_wrong(lives)
    detail['sure_and_wrong'] = wrong
    ok = best is not None and all(detail['by_arm'][best][k] for k in 'abc') and wrong == 0
    return ok, detail


T2_ARMS = {'checked': 'why', 'outside': 'credit-outside', 'self': 'credit-self', 'none': 'credit-none'}


def check_t2(lives):
    """T2 credit (Architecture §12), on teacher-free worlds (alone and exam), the same seeds for every arm:
    0 sure-and-wrong; checked credit needs no more tries (mean rank of the truth) than outside credit; checked credit
    is better calibrated than self credit: the paired Brier difference (checked - self, paired by seed and world
    number) has a 95% interval below 0."""
    seeds = sorted({s for s, _ in lives})
    detail = {'seeds': seeds, 'by_credit': {}}
    free = {}
    for mode, arm in T2_ARMS.items():
        if not all((s, arm) in lives for s in seeds):
            return False, {**detail, 'why': f'arm {arm} missing for some seed'}
        free[mode] = {(s, w['n']): w for s in seeds for w in lives[(s, arm)]['worlds'] if w['phase'] != 'taught'}
        ranks = [w['rank'] for w in free[mode].values()]
        briers = [w['brier'] for w in free[mode].values()]
        detail['by_credit'][mode] = {'arm': arm, 'worlds': len(ranks), 'mean_tries': round(float(np.mean(ranks)), 3),
                                     'mean_brier': round(float(np.mean(briers)), 4)}
    pairs = sorted(set(free['checked']) & set(free['self']))
    d = np.array([free['checked'][k]['brier'] - free['self'][k]['brier'] for k in pairs], float)
    se = float(d.std(ddof=1) / math.sqrt(len(d))) if len(d) > 1 else float('inf')
    ci = (float(d.mean()) - 1.96 * se, float(d.mean()) + 1.96 * se) if len(d) else (float('nan'),) * 2
    wrong = sure_and_wrong({k: v for k, v in lives.items() if k[1] in T2_ARMS.values()})
    tries_ok = detail['by_credit']['checked']['mean_tries'] <= detail['by_credit']['outside']['mean_tries']
    calib_ok = len(d) > 1 and ci[1] < 0
    detail.update({'brier_checked_minus_self': {'pairs': len(d), 'mean': round(float(d.mean()), 4) if len(d) else None,
                                                'ci95': [round(v, 4) for v in ci]},
                   'tries_ok': tries_ok, 'calibration_ok': calib_ok, 'sure_and_wrong': wrong})
    return wrong == 0 and tries_ok and calib_ok, detail


def check_c12(lives, live_world=True):
    detail = {}
    # (a) words never touch the evidence
    if live_world:
        from ccops5.core import caretaker, curriculum, mind
        w1 = curriculum.make_world(1, 'rubbing', 900, situations=3, tricks=0.0)
        w2 = curriculum.make_world(1, 'rubbing', 900, situations=3, tricks=0.0)
        talk = caretaker.Caretaker('timed', 1)
        r1 = mind.Mind(w1.sigma, eps=0.5, budget=1).live(w1)
        r2 = mind.Mind(w2.sigma, eps=0.5, budget=1,
                       on_event=lambda k, e: talk.on_event(0, w2, k, e) if e != 'end' else talk.on_situation(0, w2, k)
                       ).live(w2)
        same = (r1.claim == r2.claim and r1.certificate.rivals == r2.certificate.rivals
                and r1.certificate.band == r2.certificate.band and r1.throws == r2.throws)
        detail['a_evidence_identical'] = bool(same)
        detail['a_words_said'] = len(talk.log)
    else:
        detail['a_evidence_identical'] = True
    # (b) fillers never ground
    grounded_fillers = sum(1 for d in lives.values() for f in FILLERS if f in d['lexicon']['grounded'])
    detail['b_filler_groundings'] = grounded_fillers
    # (c) regime words heard in >= 8 checked worlds ground
    pairs = [(d['lexicon'], w) for d in lives.values() if d['arm_name'] in TIMED
             for w, n in d['lexicon']['heard_checked'].items() if n >= 8 and w not in FILLERS
             and w not in ('heavy', 'light')]
    rate = (sum(w in lex['grounded'] for lex, w in pairs) / len(pairs)) if pairs else None
    detail['c_pairs'] = len(pairs)
    detail['c_grounded_share'] = None if rate is None else round(rate, 3)
    # (d) word prior helps on exam worlds of practised kinds where the word was said
    with_w, without_w = [], []
    for d in lives.values():
        if d['arm_name'] not in TIMED:
            continue
        for w in d['worlds']:
            if w['phase'] == 'exam' and not w['never_shown'] and w['word_only']:
                with_w.append(w['rank'] == 1)
                without_w.append(w['rank_no_words'] == 1)
    n = len(with_w)
    diff = (sum(with_w) - sum(without_w)) / n if n else None
    detail['d_exam_worlds'] = n
    detail['d_right_first_with_minus_without'] = None if diff is None else round(diff, 3)
    # (e) prediction: timed words ground sooner than random-time words
    def speed(arms):
        vals = [v for d in lives.values() if d['arm_name'] in arms for v in d['lexicon']['grounded_at'].values()]
        return (float(np.median(vals)), len(vals)) if vals else (None, 0)
    detail['e_median_world_grounded_timed'], detail['e_n_timed'] = speed(TIMED)
    detail['e_median_world_grounded_random'], detail['e_n_random'] = speed(RANDOM)
    wrong = sure_and_wrong(lives)
    detail['sure_and_wrong'] = wrong
    ok = (detail['a_evidence_identical'] and grounded_fillers == 0 and rate is not None and rate >= 0.9
          and diff is not None and diff >= 0.15 and wrong == 0)
    return ok, detail


def check_c13(lives, live_world=True):
    from ccops5.core import board as B
    detail = {}
    if live_world:
        from ccops5.core import curriculum, mind
        w1 = curriculum.make_world(1, 'spring', 901, situations=3, tricks=0.0)
        w2 = curriculum.make_world(1, 'spring', 901, situations=3, tricks=0.0)
        brd = B.Board()
        brd.mark_lookalike((('position', 'straight'),), (('position', 'wave'),))
        r1 = mind.Mind(w1.sigma, eps=0.5, budget=1).live(w1)
        r2 = mind.Mind(w2.sigma, eps=0.5, budget=1, board=brd).live(w2)
        detail['a_evidence_identical'] = bool(r1.claim == r2.claim and r1.certificate.rivals == r2.certificate.rivals
                                             and r1.certificate.band == r2.certificate.band)
    else:
        detail['a_evidence_identical'] = True

    class _Lib:
        claims = ()

    class _Claim:
        family, sure = ((('speed', 'straight'),)), True
        certificate = type('C', (), {'digest': 'x'})()

    refused = 0
    brd = B.Board()
    for attempt in (lambda: brd.deposit_certificate(_Lib(), _Claim()),
                    lambda: brd.deposit_correction({'id': 'forged', 'family': (), 'issued_by': 'teacher'}),
                    lambda: brd.deposit_alarm(1.0, 11.1, [(0, 0)])):
        try:
            attempt()
        except ValueError:
            refused += 1
    detail['b_forged_deposits_refused'] = f'{refused}/3'
    from ccops5.core import curriculum
    b2 = B.Board()
    for _ in range(3):
        b2.mark_lookalike((('position', 'straight'),), (('position', 'wave'),))
    picks = set()
    for seed in (1, 2):
        cur = curriculum.Curriculum('ladder', seed)
        picks.add(cur.next_kind(board=b2, placement=True)[1])
    detail['c_template_from_board'] = sorted(picks)
    b3 = B.Board()
    for _ in range(200):
        b3.evaporate()
    floor_ok = min(b3.trails.values()) >= b3.tau_min - 1e-12
    detail['d_trails_min_after_200'] = round(min(b3.trails.values()), 4)
    wrong = sure_and_wrong(lives)
    detail['sure_and_wrong'] = wrong
    ok = detail['a_evidence_identical'] and refused == 3 and picks == {'large'} and floor_ok and wrong == 0
    return ok, detail


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--results', required=True)
    ap.add_argument('--checks', nargs='+', help='default: C9 C12 C13, plus T2 when the credit arms were run')
    ap.add_argument('--no-live', action='store_true', help='skip the one-world live parts (C12a, C13a)')
    a = ap.parse_args()
    if os.environ.get('PYTHONHASHSEED') != '0':
        sys.exit('set PYTHONHASHSEED=0 first (decision D5)')
    lives = load(a.results)
    print(f'{len(lives)} lives from {a.results}')
    fns = {'C9': lambda: check_c9(lives), 'C12': lambda: check_c12(lives, not a.no_live),
           'C13': lambda: check_c13(lives, not a.no_live), 'T2': lambda: check_t2(lives)}
    if a.checks is None:
        a.checks = ['C9', 'C12', 'C13'] + (['T2'] if any(arm in T2_ARMS.values() and arm != 'why'
                                                        for _, arm in lives) else [])
    out = {}
    for name in a.checks:
        ok, detail = fns[name]()
        out[name] = {'pass': bool(ok), 'detail': detail}
        print(f'{name}: {"PASS" if ok else "FAIL"}  {json.dumps(detail, default=str)}', flush=True)
    Path(a.results, 'school_check.json').write_text(json.dumps(out, indent=1, default=str), encoding='utf-8')
    print('ALL PASS' if all(v['pass'] for v in out.values()) else 'SOME CHECKS FAIL (read the numbers above)')


if __name__ == '__main__':
    main()
