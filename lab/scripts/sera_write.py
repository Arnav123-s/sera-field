"""Ask SERA to write a program (2026-09-30; the author: "I want it to be able to code"; plan 7.11 step 5, its second
half, first form). You describe a job by examples - input -> output - and in words if you like; SERA lives it as
any world (its search, imagination, steps and wishes, its own ideas first), proves a program right on your examples
(some held back as its audit: it cannot ask anyone else), and writes it as Python (the observer's printer). What it
proves becomes one of its abilities, called by your words (--save keeps it).

  python scripts/sera_write.py --field F --job "double each" --examples "[1,2,3] -> [2,4,6]; [5] -> [10]; ..."
                               [--minutes 5] [--held K] [--save F2] [--seed 1]
  (no --field: a newborn SERA)
"""
import argparse
import ast
import os
import sys
import time
from pathlib import Path

os.environ.setdefault('CCOPS5_SHAPES', 'library')
os.environ.setdefault('CCOPS5_CLAIM', 'functional')
os.environ.setdefault('CCOPS5_BAND', 'claim')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sera import lang as LG, one as ONE, phi as PH, pyprint as PP, tasks as TS  # noqa: E402
import sera_converse as SC  # noqa: E402


def examples(text):
    """'[1,2] -> [2,4]; 3 -> 6' as [(x, y)] (lists become tuples, as its language holds them)."""
    out = []
    for part in text.split(';'):
        if part.strip():
            x, y = part.split('->')
            out.append((LG.freeze(ast.literal_eval(x.strip())), LG.freeze(ast.literal_eval(y.strip()))))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--field', default=None)
    ap.add_argument('--job', default='')
    ap.add_argument('--examples', required=True)
    ap.add_argument('--minutes', type=float, default=5.0)
    ap.add_argument('--held', type=int, default=None)
    ap.add_argument('--save', default=None)
    ap.add_argument('--seed', type=int, default=1)
    a = ap.parse_args()
    field = SC.load(a.field) if a.field else PH.Field(a.seed)
    sera = ONE.Sera(a.seed, field)
    task = TS.Given(a.job or 'a job', examples(a.examples), words=a.job.split(), held=a.held)
    print(f"you: {a.job or '(no words)'} - {len(task.data)} examples to learn from, {task.held} held back as its check")
    ONE.MAX_WALL = 60 * a.minutes
    t0 = time.time()
    rec = sera.live(task, teaching=False,
                    on_say=lambda s: print(f"  SERA: {s['text']}") if s['what'] in ('proven', 'refused', 'build')
                    else None)
    if not rec.get('proven'):
        print(f"SERA: I could not prove a program for this in {time.time() - t0:.0f} s. My best idea: "
              f"{LG.show(rec['answer'], field.names()) if rec.get('answer') is not None else 'none'}.")
        return
    law = rec['answer']
    print(f"SERA: here is my program, right on all {len(task.data)} examples it learned from and the {task.held} "
          f"held back ({time.time() - t0:.0f} s):\n")
    print(PP.to_python(law, field.concept_table(), field.names(), arg=task.var).split(PP.HELPERS, 1)[-1].strip())
    if rec.get('said'):
        print(f"\n(its word for it: {rec['said'][0]})")
    if a.save:
        field.save(a.save)


if __name__ == '__main__':
    main()
