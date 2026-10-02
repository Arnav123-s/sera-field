"""The list-function benchmark's scores: SERA against people and published program learners, on the same trials.

  python scripts/sera_bench_report.py --data DIR --sera OUT/predictions.csv [--md report.md]

Accuracy is the share of trials whose output was predicted exactly, over trials 2-11 (after at least one example) and
over all 11. People: every participant's answers (predictions.csv, 250 functions). Programs (the first 100 functions,
as published): a reference model (greedy and pass@50), RobustFill, Metagol, enumeration and Fleet. Every table is computed here from
those files; nothing is typed.
"""
import argparse
import ast
import csv
from collections import defaultdict
from pathlib import Path

import numpy as np


def _same(a, b):
    try:
        return ast.literal_eval(str(a)) == ast.literal_eval(str(b))
    except (ValueError, SyntaxError):
        return str(a).strip() == str(b).strip()


def _truth(v):
    """An accuracy value as the files write it: 1/0, TRUE/FALSE, True/False; None when missing (NA)."""
    v = str(v).strip()
    if v.lower() in ('true', 't'):
        return 1.0
    if v.lower() in ('false', 'f'):
        return 0.0
    try:
        return float(v)
    except ValueError:
        return None


def scores(rows, key_trial, correct):
    """{(id, trial): mean correctness} over rows (missing values skipped)."""
    acc = defaultdict(list)
    for r in rows:
        c = correct(r)
        if c is not None:
            acc[(r['id'], int(r[key_trial]))].append(c)
    return {k: float(np.mean(v)) for k, v in acc.items()}


def summarize(sc, ids, trials):
    vals = [np.mean([sc[(i, t)] for t in trials if (i, t) in sc]) for i in ids
            if any((i, t) in sc for t in trials)]
    return (float(np.mean(vals)), len(vals)) if vals else (float('nan'), 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True)
    ap.add_argument('--sera', required=True)
    ap.add_argument('--md', default=None)
    a = ap.parse_args()
    D = Path(a.data)
    sera_rows = list(csv.DictReader(open(a.sera, encoding='utf-8')))
    learners = {'SERA': scores(sera_rows, 'trial', lambda r: int(r['correct']))}
    people = list(csv.DictReader(open(D / 'predictions.csv', encoding='utf-8')))
    learners['people'] = scores(people, 'block_trial', lambda r: _truth(r['accuracy']))
    runs = []
    if (D / 'comparison.csv').exists():                   # reference runs, by the labels their file uses
        for src in sorted({r['source'] for r in csv.DictReader(open(D / 'comparison.csv', encoding='utf-8'))}):
            runs.append((f'reference model ({src})', 'comparison.csv', lambda r, src=src: r['source'] == src))
    runs += [('RobustFill', 'robustfill.csv', None), ('Metagol', 'metagol.csv', None),
             ('enumeration', 'enumeration.csv', None), ('Fleet', 'fleet.csv', None)]
    for name, file, filt in runs:
        p = D / file
        if not p.exists():
            continue
        rows = [r for r in csv.DictReader(open(p, encoding='utf-8')) if filt is None or filt(r)]
        if not rows:
            continue
        corr = (lambda r: _truth(r['accuracy'])) if 'accuracy' in rows[0] \
            else (lambda r: float(_same(r['response'], r['output'])))
        learners[name] = scores(rows, 'trial', corr)
    sera_ids = sorted({r['id'] for r in sera_rows})
    first100 = [i for i in sera_ids if int(i[1:]) <= 100]
    out = ['# The list-function benchmark: SERA against people and program learners', '',
           f'SERA answered {len(sera_ids)} functions ({len(sera_rows)} trials). Accuracy: the share of trials whose '
           'output was predicted exactly, averaged per function, then over functions.', '']
    for title, ids in (('Every function SERA answered', sera_ids), ('The first 100 (where the programs were run)',
                                                                       first100)):
        out.append(f'## {title}')
        out.append('| learner | functions | trials 2-11 | all 11 trials |')
        out.append('|---|---|---|---|')
        for name, sc in learners.items():
            m2, n = summarize(sc, ids, range(2, 12))
            m1, _ = summarize(sc, ids, range(1, 12))
            if n:
                out.append(f'| {name} | {n} | {m2:.3f} | {m1:.3f} |')
        out.append('')
    solved = [i for i in sera_ids if all(learners['SERA'].get((i, t), 0) == 1 for t in range(6, 12))]
    out.append(f'SERA had trials 6-11 all right on {len(solved)} of {len(sera_ids)} functions.')
    text = '\n'.join(out)
    if a.md:
        Path(a.md).write_text(text, encoding='utf-8')
    print(text)


if __name__ == '__main__':
    main()
