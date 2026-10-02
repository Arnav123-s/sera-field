"""Talk with SERA (2026-09-30; the author: "I want to be able to converse with it"). An interface, not an ability:
nothing here answers or chooses - SERA does (sera.one.Sera.reply), from its Field.

- A statement is read into its Field (its memory) and kept as this conversation's story (with --memory-only it is
  not kept: its Field alone remembers).
- A question (a line ending in '?') is pressed on its Field; the proven idea that rings loudest for it answers, on
  the situation - the question, the latest it was told, and what comes to mind - in its words, or it says it does not
  know (another idea's word is not an answer to this question). Which idea a question calls for its Field learns in a
  talk with a teacher (sera.one.Sera.converse, scripts/sera_converse.py); the interface only shows it.
- Scope (S06 F5-F7, reviewer): words in, words out; only ideas that take a situation; numbers and symbols in a question
  are not read yet.
- '/about X': what X is to it (its ideas of things: what it is like, what goes on with it, its dreams).
- '/ideas': the ideas it has and its words for them.
- '/code <question>': how it answers that question, as Python (the idea that rings, printed); '/code' alone: all
  its proven ideas as a Python module (sera.pyprint, the observer's printer).

  python scripts/sera_talk.py --field F [--script FILE] [--book WORDNET] [--memory-only] [--save F2]
  (without --script: type; an empty line ends)
"""
import argparse
import os
import re
import sys
from pathlib import Path

os.environ.setdefault('CCOPS5_SHAPES', 'library')
os.environ.setdefault('CCOPS5_CLAIM', 'functional')
os.environ.setdefault('CCOPS5_BAND', 'claim')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

from sera import dictionary as DICT, lang as LG, one as ONE, phi as PH, pyprint as PP, tasks as TS, talk as TK  # noqa: E402,E501


def words(ws):
    return ' '.join(TS.text(w) for w in ws)


def situation(sera, told, q):
    """The situation as it takes a question in: the question, the latest it was told that fits what its language can
    hold (S06 F7), and what comes to mind for what the question names that it was not told."""
    ideas = sera._ideas()
    told = list(told)[-(LG.MAX_LEN // 2):]                 # the latest it was told, first (S07 F8, reviewer: a fact that
    missing = [w for w in q if w not in {t for s in told for t in s}]   # fell out of the window still held back
    came = tuple(s[:LG.MAX_LEN] for s in ideas.comes_to_mind(missing) if s not in told)[:LG.MAX_LEN // 2] \
        if missing else ()                                               # its memory of what it names)
    room = LG.MAX_LEN - 1 - len(came)
    g = (tuple(q)[:LG.MAX_LEN],) + tuple(s[:LG.MAX_LEN] for s in told[max(0, len(told) - room):]) + came
    return g, came


def answer(sera, told, q):
    """SERA's reply: (its words or None, its word for the idea that answered or None, [(idea's word, loudness)] of
    what rang, what came to mind)."""
    g, came = situation(sera, told, q)
    got, cid, rang = sera.reply(g, tuple(q))
    names = sera.field.names()
    said = None if got is None else (words(got) if isinstance(got, tuple) else TS.text(got))
    return said, (names.get(cid, cid) if cid is not None else None), [(names.get(c, c), v) for c, v in rang], came


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--field', required=True)
    ap.add_argument('--script', default=None)
    ap.add_argument('--book', default=None)
    ap.add_argument('--memory-only', action='store_true', help='answer from its Field alone, not the told story')
    ap.add_argument('--save', default=None, help='save its Field after the talk')
    a = ap.parse_args()
    TK.BOOK = DICT.load(a.book)
    field = PH.Field.load(a.field)
    sera = ONE.Sera(1, field)
    ideas = sera._ideas()
    rng = np.random.default_rng([1, 30])
    lines = open(a.script, encoding='utf-8').read().splitlines() if a.script else iter(lambda: input('you: '), '')
    told = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if a.script:
            print(f'you: {line}')
        if line.startswith('/about'):
            import sera_ideas as SI
            for ln in SI.describe(ideas, line.split(None, 1)[1].strip().lower(), rng):
                print(ln)
            continue
        if line.startswith('/code'):                    # how it answers, as Python: the idea that rings for the
            q = tuple(TS.sym(w) for w in re.findall(r'[a-z]+', line[5:].lower()))   # question, printed (sera.pyprint)
            if not q:
                print(PP.module(field))
                continue
            said, idea, rang, came = answer(sera, told, q)
            if idea is None:
                print('SERA: nothing I have proven rings for that question, so I have no program for it yet.')
                continue
            cid = next(c for c in sera._situation_ideas() if field.names().get(c, c) == idea)
            print(f"SERA: for that I use my idea '{idea}'; as Python (g is the question, then the story):")
            print(PP.to_python(LG.node('c', LG.node('var', payload='g'), payload=cid), field.concept_table(),
                               field.names(), arg='g', words=True).split(PP.HELPERS, 1)[-1].strip())
            continue
        if line.startswith('/ideas'):
            names = field.names()
            print('SERA: my ideas:', ', '.join(f"{names.get(c['id'], c['id'])} = "
                                               f"{LG.show(c['body'], names)[:40]}" for c in field.concepts))
            continue
        toks = tuple(TS.sym(w) for w in re.findall(r'[a-z]+', line.lower()))
        if not toks:
            continue
        if line.endswith('?'):
            said, idea, rang, came = answer(sera, told, toks)
            if came:
                print(f"      (comes to mind: {' / '.join(words(s) for s in came[:2])})")
            also = ', '.join(f'{n} {v:.2f}' for n, v in rang[1:3])
            if idea is None:
                print("SERA: I do not know. Nothing I have proven rings for this question; a talk with a teacher "
                      "would teach me which of my ideas it calls for.")
            elif said is None:
                print(f"SERA: I do not know. My idea '{idea}' rings for it (loudness {rang[0][1]:.2f}), but gives no "
                      f"answer here." + (f"  (also rings: {also})" if also else ''))
            else:
                print(f"SERA: {said}      (my idea '{idea}', loudness {rang[0][1]:.2f}"
                      + (f"; also rings: {also}" if also else '') + ')')
        else:
            ideas.read(toks, 'you')
            if not a.memory_only:                           # the story as told, besides its Field - or its Field
                told.append(toks)                           # alone (S06 F7: what it remembers, not the transcript)
            print('SERA: (I take it in.)')
    if a.save:
        field.save(a.save)
        print(f'(its Field, with this conversation in it, saved to {a.save})')


if __name__ == '__main__':
    main()
