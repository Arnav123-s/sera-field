"""Understanding that does not depend on where a word sits (plan 7.11 step 3; review 8, design D), as an experiment:
the same SERA (a saved Field), two curricula of the same length, graded by the observer on the same questions.

- factored: small abilities first, each its own world (is a word among others - it, then true or false; the story
  rows about what the question names; the latest of them), then "where", asked in three ways with the name anywhere;
- direct: "where" asked in three ways, the whole time.
Then, if asked (--yesno-min), "is X in the P?" answered yes or no, the name and place anywhere.

Graded: its proven where-program (else its best idea) on 20 new stories x 4 frames (3 taught, 1 never taught),
then the same with names and places it never read - right and answered, per frame. Every program is SERA's own; the
lessons and the teacher's words are the teacher's.

  python scripts/sera_understand.py --field F --arm factored|direct --out DIR [--seed 3] [--helper-min 10]
                                    [--where-min 15] [--yesno-min 0] [--book WORDNET] [--save F2]
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault('CCOPS5_SHAPES', 'library')
os.environ.setdefault('CCOPS5_CLAIM', 'functional')
os.environ.setdefault('CCOPS5_BAND', 'claim')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sera import dictionary as DICT, lang as LG, one as ONE, phi as PH, tasks as TS, talk as TK  # noqa: E402
import sera_converse as SC  # noqa: E402

HELPERS = (TS.lesson_among, TS.lesson_is_among, TS.lesson_rows_about, TS.lesson_latest_row)


def live(sera, task, minutes, rows):
    ONE.MAX_WALL = 60.0 * minutes
    t0 = time.time()
    print(f'=== {task.name} (box {minutes:g} min) | words heard: {" ".join(task.words) or "-"}', flush=True)
    rec = sera.live(task, teaching=True, on_say=lambda s: print(f"    {s['text']}", flush=True)
                    if s['what'] in ('proven', 'refused', 'build') else None)
    names = sera.field.names()
    row = dict(world=task.name, proven=bool(rec.get('proven')), verdict=rec.get('verdict'),
               claim=LG.show(rec['answer'], names) if rec.get('answer') is not None else None,
               wall=round(time.time() - t0, 1), steps=rec.get('steps'), level=rec.get('level'),
               built=[b.get('words') for b in rec.get('built') or []], invented=[i.get('body') for i in rec.get(
                   'invented') or []], memory_stops=rec.get('memory_stops'))
    rows.append(row)
    print(f"  -> {row['verdict']} | {row['claim']} | {row['wall']} s | level {row['level']} | built {row['built']}",
          flush=True)
    return rec


def grade(sera, law, seed):
    """The observer: the program on the evaluation questions, per frame (right, answered, total)."""
    out = {}
    cs = sera.field.concept_table()
    for renamed in (False, True):
        for x, y, frame in TS.where_any_eval(seed, renamed=renamed):
            v = LG.safe(law, {'g': x}, cs) if law is not None else None
            k = out.setdefault(('new words: ' if renamed else '') + frame, [0, 0, 0])
            k[0] += int(v == y)
            k[1] += int(TS.is_words(v))
            k[2] += 1
    return {f: f'{a}/{c} (answered {b})' for f, (a, b, c) in out.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--field', required=True)
    ap.add_argument('--arm', choices=('factored', 'direct'), required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--seed', type=int, default=3)
    ap.add_argument('--helper-min', type=float, default=10.0)
    ap.add_argument('--where-min', type=float, default=15.0)
    ap.add_argument('--yesno-min', type=float, default=0.0)
    ap.add_argument('--book', default=None)
    ap.add_argument('--save', default=None)
    a = ap.parse_args()
    TK.BOOK = DICT.load(a.book)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    sera = ONE.Sera(a.seed, SC.load(a.field))
    rows, t0, stopped = [], time.time(), None
    if a.arm == 'factored':
        for build in HELPERS:
            rec = live(sera, build(a.seed), a.helper_min, rows)
            if not rec.get('proven'):
                stopped = rows[-1]['world']                # S08: stop at the first helper it cannot earn
                break
        where_min = a.where_min
    else:
        where_min = a.where_min + len(HELPERS) * a.helper_min   # the same length of teaching
    rec = None
    if stopped is None:
        rec = live(sera, TS.lesson_where_any(a.seed), where_min, rows)
    law = rec.get('answer') if rec is not None else None
    graded = grade(sera, law, a.seed + 900)
    print('GRADED where:', json.dumps(graded), flush=True)
    yesno = None
    if a.yesno_min > 0 and rec is not None and rec.get('proven'):
        yrec = live(sera, TS.lesson_is_in_any(a.seed), a.yesno_min, rows)
        yesno = dict(proven=bool(yrec.get('proven')), verdict=yrec.get('verdict'))
    (out / 'UNDERSTAND.json').write_text(json.dumps(dict(arm=a.arm, field=a.field, seed=a.seed, stopped_at=stopped,
                                                         worlds=rows, graded_where=graded, yesno=yesno,
                                                         total_s=round(time.time() - t0, 1)), indent=1),
                                        encoding='utf-8')
    if a.save:
        sera.field.save(a.save)
    print('UNDERSTAND DONE', a.arm, json.dumps(dict(stopped_at=stopped, graded=graded)), flush=True)


if __name__ == '__main__':
    main()
