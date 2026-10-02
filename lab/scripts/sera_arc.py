"""ARC (Chollet's Abstraction and Reasoning Corpus, ARC-AGI-1: 400 training and 400 evaluation puzzles): SERA builds
the abilities it needs itself, then is tested once.

  python scripts/sera_arc.py practice --data ARC-AGI/data --out RUN [--hours 10] [--visit 30] [--seed 1]
  python scripts/sera_arc.py test --data ARC-AGI/data --out RUN/test-practised --field RUN/field.pkl [--set evaluation]
         [--workers 5] [--wall 120]            (no --field: a newborn SERA, the control)
  python scripts/sera_arc.py report --out RUN [--tests RUN/test-practised,RUN/test-newborn]

The author, 2026-09-28: "i want sera to build the abilities it needs, not us building every smallest thing". Nothing
about grids is given. SERA's language has numbers, lists (a list may hold lists: to it a grid is a list of rows),
iteration and its own concepts; every grid ability it ends with - a flip, a mirror, a turn, a tile, a crop - it made
itself, as a concept, from a puzzle it proved, and it may build the next one on it.

A puzzle is a world. SERA sees the example pairs (input grid, output grid) and the test input; its answer is a program
of its language; its judge accepts a program that gives every example's output exactly and a grid on the test input
(the only proof ARC gives: nothing can be asked). The test outputs are the observer's alone: SERA never sees them, in
practice or in the test.

Practice (the training puzzles): in its first visits (--teach) the teacher shows its way of working and of imagining
- to grow, and, when nothing it can say fits, to wish for the ability it lacks, build it and use it - never an
answer; after that SERA works its own way. SERA chooses what to work on next - its own estimate of where its time pays most (its
record so far, up for puzzles that look like ones it has proved, down for a puzzle it failed with the language it has
now) - and each visit is time-boxed by this program (the box doubles each time it comes back to a puzzle; no puzzle is
closed for good). What it proves becomes a concept of its language. Its Field is saved after every visit.

Test (the evaluation puzzles, once): every puzzle from the same practised SERA, keeping nothing between them (frozen),
and a newborn SERA on the same puzzles (the control: what practice built). Two attempts per test input (the ARC Prize
rule): its leading program, and its next idea that also fits every example and answers differently.
"""
import argparse
import json
import math
import multiprocessing as mp
import os
import pickle
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

from sera import lang as LG, one as ONE, phi as PH, tasks as TS  # noqa: E402

GRID, is_grid, Puzzle = TS.GRID, TS.is_grid, TS.Puzzle


def load(data, which):
    d = Path(data) / which
    return {p.stem: json.loads(p.read_text(encoding='utf-8')) for p in sorted(d.glob('*.json'))}


def attempts(task, rec, concepts):
    """Its two answers per test input: its leading program's, and its next idea's that also fits every example and
    answers differently (None when there is none)."""
    first = rec.get('answer')
    a1 = task.answers(first, concepts) if first is not None else None
    a2 = None
    for e in rec.get('others') or ():
        if task.consistent(e, concepts):
            v = task.answers(e, concepts)
            if v != a1 and all(is_grid(x) for x in v):
                a2 = v
                break
    return a1, a2


def score(task, a1, a2):
    """The ARC score of a puzzle: the share of its test inputs answered right in either attempt."""
    if not task._answers:
        return 0.0
    ok = [(a1 is not None and a1[i] == y) or (a2 is not None and a2[i] == y) for i, y in enumerate(task._answers)]
    return float(np.mean(ok))


# ============================================================ practice
def proved_contexts(field, kind, d=7):
    return np.asarray([e['context'] for e in field.understood
                       if e['kind'] == kind and e['proven'] and len(e['context']) == d], float).reshape(-1, d)


def familiar(proved, ctx):
    """How much a puzzle looks like one it proved (the Field's own kernel over what it understood)."""
    if not len(proved):
        return 0.0
    return float(np.max(np.exp(-np.sum((proved - np.asarray(ctx, float)) ** 2, axis=1) / 2)))


def choose(sera, book, ctxs, visit, tie):
    """Where its time pays most, by its own estimate: the chance it proves a puzzle now, per second of the visit.
    The chance: its record (puzzles proved of those visited, with one of each imagined: Laplace), up to twice that for a
    puzzle like one it proved, halved for every visit it failed with the language it has now (a puzzle waits until its
    language grows); a visit's box doubles each time it comes back. A proved puzzle is done."""
    visited = [b for b in book.values() if b['visits']]
    base = (sum(b['proven'] for b in visited) + 1) / (len(visited) + 2)
    lang = len(sera.field.concepts)
    proved = proved_contexts(sera.field, f'exact:{GRID}->{GRID}')
    best, best_v = None, -1.0
    for pid, b in book.items():
        if b['proven']:
            continue
        stale = b['stale'] if b['language'] == lang else 0
        p = base * (1 + familiar(proved, ctxs[pid])) / 2 ** stale
        v = p / (visit * 2 ** b['failed']) * (1 + 1e-6 * tie[pid])
        if v > best_v:
            best, best_v = pid, v
    return best


def practice(a):
    puzzles = load(a.data, 'training')
    out = Path(a.out)
    (out / 'visits').mkdir(parents=True, exist_ok=True)
    ck, bk = out / 'field.pkl', out / 'book.json'
    field = PH.Field.load(ck) if ck.exists() else PH.Field(a.seed)
    sera = ONE.Sera(a.seed, field)
    book = (json.loads(bk.read_text(encoding='utf-8')) if bk.exists() else
            {pid: dict(visits=0, failed=0, stale=0, language=-1, proven=False, right=False, verdict=None, wall=0.0)
             for pid in puzzles})
    ctxs = {pid: Puzzle(pid, p).context() for pid, p in puzzles.items()}
    rng = np.random.default_rng([a.seed, 29])
    tie = {pid: float(rng.random()) for pid in sorted(puzzles)}          # its own order among equals, fixed
    deadline = time.time() + 3600 * a.hours
    log = open(out / 'visits.jsonl', 'a', encoding='utf-8')
    t_start = time.time()
    n = sum(b['visits'] for b in book.values())
    while time.time() < deadline - 10:
        pid = choose(sera, book, ctxs, a.visit, tie)
        if pid is None:
            break
        b = book[pid]
        box = a.visit * 2 ** b['failed']
        ONE.MAX_WALL = max(5.0, min(box, deadline - time.time()))
        task = Puzzle(pid, puzzles[pid])
        lang0 = len(sera.field.concepts)
        t0 = time.time()
        try:
            rec = sera.live(task, teaching=n < a.teach)                  # the teacher shows its way of working
            err = None                                                   # (and of wishing) at first; no answers
        except Exception as e:                                           # a crash is a failed visit, recorded
            rec, err = dict(proven=False, answer=None, others=None, steps=0, level=0, invented=[], reused=[]), repr(e)[:300]
        LG._TABLES.clear()
        concepts = sera.field.concept_table()
        a1, a2 = attempts(task, rec, concepts) if rec.get('answer') is not None else (None, None)
        sc = score(task, a1, a2)
        n += 1
        b['visits'] += 1
        b['wall'] = round(b['wall'] + time.time() - t0, 1)
        proven = bool(rec.get('proven'))
        if proven:
            b['proven'], b['right'] = True, sc == 1.0
        else:
            b['failed'] += 1
            b['stale'] = (b['stale'] + 1) if b['language'] == lang0 else 1
        b['language'] = len(sera.field.concepts) if proven else lang0
        b['verdict'] = rec.get('verdict')
        names = sera.field.names()
        row = dict(n=n, pid=pid, visit=b['visits'], box=round(box, 1), wall=round(time.time() - t0, 1),
                   proven=proven, verdict=rec.get('verdict'), score=sc, level=rec.get('level'), steps=rec.get('steps'),
                   answer=LG.show(rec['answer'], names)[:300] if rec.get('answer') is not None else None,
                   invented=[dict(i, name=names.get(i['id'])) for i in rec.get('invented') or []],
                   reused=rec.get('reused'), language=len(sera.field.concepts), error=err,
                   serendipity=rec.get('serendipity'), imagined_by=rec.get('imagined_by'), said=rec.get('said'),
                   t=round(time.time() - t_start, 1))
        log.write(json.dumps(row, default=str) + '\n')
        log.flush()
        (out / 'visits' / f'{n:05d}-{pid}.json').write_text(json.dumps(dict(row, say=[s['text'] for s in rec.get('say', [])],
                                                                               configs=rec.get('configs')), default=str,
                                                                          indent=1), encoding='utf-8')
        sera.field.save(ck)
        bk.write_text(json.dumps(book), encoding='utf-8')
        done = sum(x['proven'] for x in book.values())
        print(f"[{n}] {pid} visit {b['visits']} ({box:.0f} s box): {rec.get('verdict')} in {row['wall']:.0f} s, level "
              f"{rec.get('level')} | {row['answer'] or '-'} | proved {done}, right on the test "
              f"{sum(x['right'] for x in book.values())} | language {len(sera.field.concepts)}"
              + (f" | NEW {[i.get('name') or i['id'] for i in row['invented']]}" if row['invented'] else '')
              + (f" | ERROR {err}" if err else ''), flush=True)
    log.close()
    print('PRACTICE DONE', json.dumps(dict(visits=n, proven=sum(x['proven'] for x in book.values()),
                                           right=sum(x['right'] for x in book.values()),
                                           concepts=len(sera.field.concepts))), flush=True)


# ============================================================ the test (frozen)
_FIELD = None


def _init(field_bytes):
    global _FIELD
    _FIELD = field_bytes


def test_one(job):
    pid, puzzle, wall, seed = job
    field = pickle.loads(_FIELD) if _FIELD is not None else PH.Field(seed)   # the same SERA every puzzle
    sera = ONE.Sera(seed, field)
    ONE.MAX_WALL = wall
    task = Puzzle(pid, puzzle)
    t0 = time.time()
    try:
        rec = sera.live(task, teaching=False)
        err = None
    except Exception as e:
        rec, err = dict(proven=False, answer=None, others=None), repr(e)[:300]
    LG._TABLES.clear()
    concepts = sera.field.concept_table()
    a1, a2 = attempts(task, rec, concepts) if rec.get('answer') is not None else (None, None)
    names = sera.field.names()
    return dict(pid=pid, proven=bool(rec.get('proven')), verdict=rec.get('verdict'), score=score(task, a1, a2),
                first_right=score(task, a1, None), level=rec.get('level'), steps=rec.get('steps'),
                answer=LG.show(rec['answer'], names)[:300] if rec.get('answer') is not None else None,
                reused=rec.get('reused'), wall=round(time.time() - t0, 1), error=err)


def test(a):
    puzzles = load(a.data, a.set)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    path = out / 'results.jsonl'
    done = {json.loads(l)['pid'] for l in path.read_text(encoding='utf-8').splitlines() if l.strip()} \
        if path.exists() else set()
    field_bytes = Path(a.field).read_bytes() if a.field else None
    jobs = [(pid, p, a.wall, a.seed) for pid, p in puzzles.items() if pid not in done]
    f = open(path, 'a', encoding='utf-8')
    t0, rows = time.time(), []
    with mp.get_context('fork').Pool(a.workers, initializer=_init, initargs=(field_bytes,), maxtasksperchild=8) as pool:
        for r in pool.imap_unordered(test_one, jobs):
            f.write(json.dumps(r, default=str) + '\n')
            f.flush()
            rows.append(r)
            print(f"{r['pid']}: {r['verdict']} score {r['score']:.2f} | {r['answer'] or '-'} | {r['wall']:.0f} s | "
                  f"{len(rows)}/{len(jobs)}, score so far {sum(x['score'] for x in rows):.1f} | "
                  f"{time.time() - t0:.0f} s", flush=True)
    f.close()
    print('TEST DONE', json.dumps(dict(puzzles=len(rows), score=sum(x['score'] for x in rows))), flush=True)


# ============================================================ the report (generated)
def report(a):
    out = Path(a.out)
    rows = [json.loads(l) for l in (out / 'visits.jsonl').read_text(encoding='utf-8').splitlines() if l.strip()]
    field = PH.Field.load(out / 'field.pkl')
    names = field.names()
    print('### Practice: what it proved, in the order it chose\n')
    print('| Visit | Puzzle | Hours in | Its program (its own words) | New concept | Right on the test |')
    print('|---|---|---|---|---|---|')
    for r in rows:
        if r['proven']:
            new = ', '.join(i.get('name') or str(i['id']) for i in r['invented']) or '-'
            print(f"| {r['n']} | {r['pid']} | {r['t'] / 3600:.1f} | `{r['answer']}` | {new} | "
                  f"{'yes' if r['score'] == 1.0 else 'no'} |")
    print('\n### Its concepts (every ability it made; what each is built on)\n')
    print('| Concept | Type | Body | Built on | Born of | Used |')
    print('|---|---|---|---|---|---|')
    for c in field.concepts:
        on = [names.get(p[1], p[1]) for p in c['parts'] if p[0] == 'concept']
        print(f"| {names.get(c['id'])} | {c['sig'][0]} → {c['sig'][1]} | `{LG.show(c['body'], names)[:120]}` | "
              f"{', '.join(map(str, on)) or '-'} | {c['born']} | {c['uses']} |")
    hours = max((r['t'] for r in rows), default=0) / 3600
    print('\n### Practice over time\n')
    print('| Hours | Visits | Puzzles proved | Right on the test | Concepts |')
    print('|---|---|---|---|---|')
    marks = sorted({min(h, hours) for h in np.arange(1, math.ceil(hours) + 1)})
    proven, right = set(), set()
    k = 0
    for h in marks:
        while k < len(rows) and rows[k]['t'] <= h * 3600 + 1e-6:
            if rows[k]['proven']:
                proven.add(rows[k]['pid'])
                if rows[k]['score'] == 1.0:
                    right.add(rows[k]['pid'])
            k += 1
        lang = max([r['language'] for r in rows[:k]] or [0])
        print(f'| {h:.1f} | {k} | {len(proven)} | {len(right)} | {lang} |')
    for t in (a.tests.split(',') if a.tests else []):
        p = Path(t) / 'results.jsonl'
        if not p.exists():
            continue
        res = [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]
        print(f'\n### Test {t}: {len(res)} puzzles\n')
        print('| Score (2 attempts) | First attempt | Proven | Proven right | Accepted but wrong | Median wall s |')
        print('|---|---|---|---|---|---|')
        print(f"| {sum(r['score'] for r in res):.1f} ({sum(r['score'] for r in res) / max(len(res), 1):.1%}) | "
              f"{sum(r['first_right'] for r in res):.1f} | {sum(r['proven'] for r in res)} | "
              f"{sum(r['verdict'] == 'proven right' for r in res)} | "
              f"{sum(r['verdict'] == 'accepted, wrong on the test' for r in res)} | "
              f"{float(np.median([r['wall'] for r in res])) if res else 0:.0f} |")
        for r in sorted(res, key=lambda r: r['pid']):
            if r['score'] > 0:
                print(f"- {r['pid']}: `{r['answer']}` ({r['verdict']})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=('practice', 'test', 'report'))
    ap.add_argument('--data', default='ARC-AGI/data')
    ap.add_argument('--out', required=True)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--hours', type=float, default=10.0)
    ap.add_argument('--visit', type=float, default=30.0, help='seconds of a first visit (the box doubles on returns)')
    ap.add_argument('--teach', type=int, default=20, help='first visits in which the teacher shows how it works')
    ap.add_argument('--field', default=None)
    ap.add_argument('--set', default='evaluation')
    ap.add_argument('--workers', type=int, default=5)
    ap.add_argument('--wall', type=float, default=120.0)
    ap.add_argument('--tests', default=None)
    a = ap.parse_args()
    {'practice': practice, 'test': test, 'report': report}[a.mode](a)


if __name__ == '__main__':
    main()
