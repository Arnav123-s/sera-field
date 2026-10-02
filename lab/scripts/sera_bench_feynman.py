"""The Feynman equations (Udrescu and Tegmark, AI Feynman; the list as kept by the PhySO repository): one SERA finds
physical laws from measurements.

  python scripts/sera_bench_feynman.py --data DIR --out OUT [--field FIELD.pkl] [--only 1,2,3] [--workers 4] [--wall 120]

For each of the 100 equations, the world is the equation (the grader's, never SERA's). SERA gets 10 measurements
(every input drawn uniformly in its range, as the benchmark specifies) and may ask the world about any inputs it
chooses. Its answer is an expression of its own language over the inputs (named x1, x2 ... - not the physics names)
times one strength it fits. Its judge is an audit on fresh measurements (the anytime bar of sera.synth, at a relative
error of TOL). The observer grades the answer on 200 more fresh measurements at the same tolerance. Nothing about
physics is given: the mechanisms are real-number arithmetic, square root, exp, log, sin and cos.

Writes OUT/answers.csv and prints a summary.
"""
import argparse
import csv
import json
import math
import multiprocessing as mp
import pickle
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

from sera import lang as LG, one as ONE, phi as PH, synth as S, tasks as TS  # noqa: E402

TOL = 1e-3                                  # relative error that counts as right, everywhere it is checked
NS = {'exp': np.exp, 'sqrt': np.sqrt, 'pi': np.pi, 'sin': np.sin, 'cos': np.cos, 'tan': np.tan, 'arcsin': np.arcsin,
      'arccos': np.arccos, 'arctan': np.arctan, 'tanh': np.tanh, 'ln': np.log, 'log': np.log, 'sinh': np.sinh,
      'cosh': np.cosh, 'abs': np.abs}


class Law(TS.Exact):
    """A measured quantity as a law of others: SERA's answer is an expression times one strength (fitted by least
    squares on what it has measured)."""
    subject = 'physics'

    def __init__(self, name, n, lows, highs, world, seed=0):
        self.subject, self.name = 'physics', name
        self._target = world
        self.inputs = {f'x{i + 1}': 'real' for i in range(n)}
        self.out = 'real'
        self.var = None
        self._lo, self._hi = lows, highs
        rng = np.random.default_rng(seed)
        examples = [self._draw(rng) for _ in range(10)]
        self.data = [(x, self._y(x)) for x in examples]
        self.pool = [self._draw(rng) for _ in range(40)]
        self._probe_inputs = examples
        self._fresh = self._draw
        self.words, self._truth_words, self.asked = [], set(), 0

    def _draw(self, rng):
        return tuple(float(rng.uniform(lo, hi)) for lo, hi in zip(self._lo, self._hi))

    def _y(self, x):
        return float(self._target(x))

    def _env(self, x):
        return {f'x{i + 1}': v for i, v in enumerate(x)}

    def probes(self):
        return [self._env(x) for x in self._probe_inputs]

    def numbers(self, most=6):
        return ()

    def strength(self, e, concepts, pairs=None):
        """(its best strength c, the largest relative error of c * e over pairs), or None if e cannot be evaluated."""
        pairs = self.data if pairs is None else pairs
        v = [LG.safe(e, self._env(x), concepts) for x, _ in pairs]
        if any(not isinstance(a, float) for a in v):
            return None
        v, y = np.asarray(v), np.asarray([b for _, b in pairs])
        if float(v @ v) <= 0:
            return None
        c = float(v @ y) / float(v @ v)
        return c, float(np.max(np.abs(c * v - y) / (np.abs(y) + 1e-12)))

    def consistent(self, e, concepts):
        f = self.strength(e, concepts)
        return f is not None and f[1] <= TOL

    def evidence(self, exprs, concepts):
        out = {}
        for e in exprs:
            f = self.strength(e, concepts)
            if f is None:
                continue
            c = f[0]
            miss = sum(1 for x, y in self.data
                       if abs(c * LG.safe(e, self._env(x), concepts) - y) > TOL * (abs(y) + 1e-12))
            out[e] = -TS.MISS_NATS * miss
        return out

    def actions(self, rng, exprs, weights, concepts):
        seen = {repr(x) for x, _ in self.data}
        out = []
        for x in self.pool:
            if repr(x) in seen:
                continue
            groups = {}
            for e, w in zip(exprs, weights):
                f = self.strength(e, concepts)
                v = LG.safe(e, self._env(x), concepts) if f is not None else None
                key = 'none' if v is None else f'{f[0] * v:.4g}'
                groups[key] = groups.get(key, 0.0) + w
            tot = sum(groups.values())
            info = -sum(p / tot * math.log(p / tot) for p in groups.values() if p > 0) if tot > 0 else 0.0
            out.append(dict(action=('ask', x), info=float(info), novel=0.0, predicted=None))
        return out

    def verify(self, e, concepts, bits, rng):
        f = self.strength(e, concepts)
        if f is None or f[1] > TOL:
            return False, 0, None
        n = S.audit_size(bits)
        for _ in range(n):
            x = self._draw(rng)
            y = self._y(x)
            v = LG.safe(e, self._env(x), concepts)
            if v is None or abs(f[0] * v - y) > TOL * (abs(y) + 1e-12):
                self.data.append((x, y))
                return False, n, (x, y)
        return True, n, None

    def grade(self, e, concepts, accepted, n=200, seed=0):
        f = self.strength(e, concepts)
        if f is None:
            return dict(verdict='not proven')
        rng = np.random.default_rng([seed, 997])
        pairs = [(x, self._y(x)) for x in (self._draw(rng) for _ in range(n))]
        g = self.strength(e, concepts, pairs)
        right = g is not None and max(abs(f[0] * LG.safe(e, self._env(x), concepts) - y) / (abs(y) + 1e-12)
                                      for x, y in pairs) <= TOL
        if accepted:
            return dict(verdict='proven right' if right else 'SURE AND WRONG')
        return dict(verdict='right, unsure' if right else 'not proven')

    def context(self):
        ys = [abs(y) for _, y in self.data]
        return [0.5, 0.0, float(np.log10(np.mean(ys) + 1e-12)) / 10, len(self.inputs) / 10, 0.0, 0.0, 0.0]

    def teacher_truth(self, word):
        return True


def load(data):
    out = []
    for r in csv.DictReader(open(Path(data) / 'FeynmanEquations.csv', encoding='utf-8-sig')):
        if not r.get('Formula'):
            continue
        idx = [i for i in range(1, 11) if r.get(f'v{i}_name')]           # the named variables: the file's count is
        names = [r[f'v{i}_name'] for i in idx]                            # wrong on 6 rows (II.37.1 says 6 and names
        lows = [float(r[f'v{i}_low']) for i in idx]                       # 3; I.18.12 says 2 and names 3, theta)
        highs = [float(r[f'v{i}_high']) for i in idx]
        out.append(dict(number=int(float(r['Number'])), name=r['Filename'], formula=r['Formula'], names=names,
                        lows=lows, highs=highs))
    return out


def world_of(eq):
    code = compile(eq['formula'], eq['name'], 'eval')
    names = eq['names']
    return lambda x: eval(code, {'__builtins__': {}}, dict(NS, **dict(zip(names, x))))


def run_one(args):
    eq, field_path, wall = args
    ONE.MAX_WALL = wall
    field = pickle.load(open(field_path, 'rb')) if field_path else PH.Field(1)
    sera = ONE.Sera(1, field)
    t0 = time.time()
    try:                                            # one bad equation is its own row, never the end of the run
        task = Law(f"feynman {eq['name']}", len(eq['names']), eq['lows'], eq['highs'], world_of(eq), seed=eq['number'])
        rec = sera.live(task, teaching=False)
        ans = rec.get('answer')
        concepts = sera.field.concept_table()
        g = task.grade(ans, concepts, bool(rec.get('proven'))) if ans is not None else dict(verdict='no answer')
        f = task.strength(ans, concepts) if ans is not None else None
        shown = (f'{f[0]:.6g} * ' if f else '') + (LG.show(ans, sera.field.names()) if ans is not None else '')
        err = ''
    except Exception as e:
        rec, g, shown, err = {}, dict(verdict='crashed'), '', repr(e)[:200]
    return dict(number=eq['number'], name=eq['name'], formula=eq['formula'], variables=len(eq['names']),
                answer=shown[:200], verdict=g['verdict'], proven=int(bool(rec.get('proven'))),
                steps=rec.get('steps', 0), asked=rec.get('asked', 0), wall=round(time.time() - t0, 1), error=err)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--field', default=None)
    ap.add_argument('--only', default=None)
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--wall', type=float, default=120.0)
    a = ap.parse_args()
    eqs = load(a.data)
    if a.only:
        keep = {int(x) for x in a.only.split(',')}
        eqs = [e for e in eqs if e['number'] in keep]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    path = out / 'answers.csv'
    done = {int(r['number']) for r in csv.DictReader(open(path, encoding='utf-8'))} if path.exists() else set()
    todo = [(e, a.field, a.wall) for e in eqs if e['number'] not in done]
    fields = ['number', 'name', 'formula', 'variables', 'answer', 'verdict', 'proven', 'steps', 'asked', 'wall',
              'error']
    new = not path.exists()
    f = open(path, 'a', encoding='utf-8', newline='')
    w = csv.DictWriter(f, fieldnames=fields)
    if new:
        w.writeheader()
    t0, n, right = time.time(), 0, 0
    with mp.get_context('fork').Pool(a.workers) as pool:
        for row in pool.imap_unordered(run_one, todo):
            w.writerow(row)
            f.flush()
            n += 1
            right += row['verdict'] in ('proven right', 'right, unsure')
            print(f"{row['name']} ({row['variables']} inputs): {row['verdict']} | {row['answer'][:70]} | truth "
                  f"{row['formula'][:50]} | {row['wall']} s | {right}/{n} right | {time.time() - t0:.0f} s", flush=True)
    f.close()
    print('FEYNMAN DONE', json.dumps(dict(equations=n, right=right)), flush=True)


if __name__ == '__main__':
    main()
