"""Markdown table of School lives per arm (one seed), generated from saved life files (never typed by hand).

Also counts, world by world, how many worlds each arm lived exactly like the untaught arm (same throws, own pushes,
claim and outcome): the test of whether teaching changes what the mind does.
Usage: python scripts/school_lives_table.py <results folder> [seed]
"""
import glob
import json
import statistics as S
import sys
from pathlib import Path


def main(folder, seed=1):
    lives = {}
    for f in sorted(glob.glob(str(Path(folder) / f'life-seed{seed}-*.json'))):
        d = json.loads(Path(f).read_text(encoding='utf-8'))
        lives[d['arm_name']] = d
    base = lives['untaught']['worlds']
    same_key = lambda w: (w['throws'], w['own'], w['claim'], w['correct'])
    print(f'| arm | worlds | truth rank taught | rank alone, 1st half | rank alone, 2nd half | rank exam | right alone | '
          f'right exam | sure and wrong | help given | worlds lived exactly as untaught (alone+exam) | grounded words |')
    print('|' + '---|' * 12)
    for arm, d in sorted(lives.items()):
        W = d['worlds']
        ph = lambda p: [w for w in W if w['phase'] == p]
        t, a, e = ph('taught'), ph('alone'), ph('exam')
        m = lambda ws, k: round(S.mean(w[k] for w in ws), 2)
        fr = lambda ws, k: round(sum(bool(w[k]) for w in ws) / len(ws), 2)
        later = [(w, b) for w, b in zip(W, base) if w['phase'] != 'taught']
        same = sum(same_key(w) == same_key(b) for w, b in later)
        print(f"| {arm} | {len(W)} | {m(t, 'rank')} | {m(a[:len(a) // 2], 'rank')} | {m(a[len(a) // 2:], 'rank')} | "
              f"{m(e, 'rank')} | {fr(a, 'correct')} | {fr(e, 'correct')} | {sum(w['sure_and_wrong'] for w in W)} | "
              f"{sum(w['help'] for w in t)} | {same}/{len(later)} | {', '.join(d['lexicon']['grounded']) or '-'} |")


if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 1)
