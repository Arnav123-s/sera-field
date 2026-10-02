"""The list-function benchmark (Rule, Tenenbaum and Piantadosi; the 250 functions and people's answers from OSF
project gq2hj): one SERA against people and published program learners.

  python scripts/sera_bench_lists.py --data DIR --out OUT [--field FIELD.pkl] [--ids c001,c002] [--workers 6] [--wall 60]

The protocol is the human experiment's. Each function's 11 trials come in the order people saw them. At trial t SERA
has seen trials 1 .. t-1 (inputs and outputs) and the input of trial t, and it predicts that output: the output of its
leading program. It may not ask about other inputs (the benchmark gives only these examples), so its judge can only
check a program against the examples it has. It starts every trial of every function from the same mind (a copy of
FIELD, or a newborn one) and keeps nothing between them: a frozen test of what it knows. The functions' programs and
the outputs still to come are the grader's alone.

Writes OUT/predictions.csv (one row per trial) and prints a summary; scripts/sera_bench_report.py compares.
"""
import argparse
import ast
import csv
import json
import multiprocessing as mp
import os
import pickle
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

from sera import lang as LG, one as ONE, phi as PH, tasks as TS  # noqa: E402


class ListBench(TS.Exact):
    """A benchmark function at one trial: its examples so far, and the input to answer. No oracle: no asking, and the
    judge is agreement with every example it has."""

    def __init__(self, name, examples, query, seed=0):
        self.subject, self.name = 'code', name
        self._target = None
        self.inputs, self.out = {'l': 'list'}, 'list'
        self.var = 'l'
        self.data = [(tuple(x), tuple(y)) for x, y in examples]
        self.pool = []
        rng = np.random.default_rng([seed, len(examples)])
        self._probe_inputs = ([tuple(x) for x, _ in examples] + [tuple(query)]
                              + [tuple(int(v) for v in rng.integers(0, 100, size=int(rng.integers(0, 11))))
                                 for _ in range(6)])
        self._fresh = None
        self.words = []
        self._truth_words = set()
        self.asked = 0

    def actions(self, rng, exprs, weights, concepts):
        return []

    def verify(self, e, concepts, bits, rng):
        return self.consistent(e, concepts), len(self.data), None

    def grade(self, e, concepts, accepted, n=200, seed=0):
        return dict(verdict='proven right' if accepted else 'not proven')      # the benchmark grades the answer

    def teacher_truth(self, word):
        return True


def load(data):
    trials = {}
    for r in csv.DictReader(open(Path(data) / 'stimuli.csv', encoding='utf-8')):
        trials.setdefault(r['id'], []).append((int(r['trial']), ast.literal_eval(r['input']),
                                               ast.literal_eval(r['output'])))
    return {k: [(x, y) for _, x, y in sorted(v)] for k, v in trials.items()}


def run_function(args):
    fid, trials, field_path, wall = args
    ONE.MAX_WALL = wall
    rows = []
    for t in range(1, len(trials) + 1):
        field = pickle.load(open(field_path, 'rb')) if field_path else PH.Field(1)
        sera = ONE.Sera(1, field)
        task = ListBench(f'{fid} trial {t}', trials[:t - 1], trials[t - 1][0])
        t0 = time.time()
        try:
            rec = sera.live(task, teaching=False)
            ans = rec.get('answer')
            concepts = sera.field.concept_table()
            pred = LG.safe(ans, {'l': list(trials[t - 1][0])}, concepts) if ans is not None else None
            shown = LG.show(ans, sera.field.names()) if ans is not None else ''
            err = ''
        except Exception as e:                                            # a crash is a wrong answer, recorded
            rec, pred, shown, err = {}, None, '', repr(e)[:200]
        truth = tuple(trials[t - 1][1])
        rows.append(dict(id=fid, trial=t, input=json.dumps(trials[t - 1][0]), truth=json.dumps(list(truth)),
                         prediction=json.dumps(list(pred) if isinstance(pred, tuple) else pred),
                         correct=int(pred == truth), answer=shown[:200], consistent=int(bool(rec.get('proven'))),
                         steps=rec.get('steps', 0), wall=round(time.time() - t0, 2), error=err))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--field', default=None, help="a saved Field (SERA after teaching); default: a newborn SERA")
    ap.add_argument('--ids', default=None)
    ap.add_argument('--workers', type=int, default=6)
    ap.add_argument('--wall', type=float, default=60.0, help='seconds per trial (its own loop decides within it)')
    a = ap.parse_args()
    trials = load(a.data)
    ids = a.ids.split(',') if a.ids else sorted(trials)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    done = set()
    path = out / 'predictions.csv'
    if path.exists():
        done = {r['id'] for r in csv.DictReader(open(path, encoding='utf-8'))}
    todo = [(i, trials[i], a.field, a.wall) for i in ids if i not in done]
    fields = ['id', 'trial', 'input', 'truth', 'prediction', 'correct', 'answer', 'consistent', 'steps', 'wall',
              'error']
    new = not path.exists()
    f = open(path, 'a', encoding='utf-8', newline='')
    w = csv.DictWriter(f, fieldnames=fields)
    if new:
        w.writeheader()
    t0, n_done, right = time.time(), 0, []
    with mp.get_context('fork').Pool(a.workers) as pool:
        for rows in pool.imap_unordered(run_function, todo):
            w.writerows(rows)
            f.flush()
            n_done += 1
            acc = np.mean([r['correct'] for r in rows[1:]])
            right.append(acc)
            print(f"{rows[0]['id']}: {acc:.2f} of trials 2-11 right | last answer {rows[-1]['answer'][:70]} | "
                  f"{sum(r['wall'] for r in rows):.0f} s | {n_done}/{len(todo)} done, mean so far {np.mean(right):.3f}"
                  f" | {time.time() - t0:.0f} s", flush=True)
    f.close()
    print('BENCH DONE', json.dumps(dict(functions=n_done, mean_accuracy_trials_2_11=float(np.mean(right)) if right
                                        else None)), flush=True)


if __name__ == '__main__':
    main()
