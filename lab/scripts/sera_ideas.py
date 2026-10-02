"""Ideas of things and closed-book reading (2026-09-29, the author: "today SERA understands procedures, not things ...
show sera a few examples in sentences of a kitchen or activities going on in a kitchen and see if sera understands
what a kitchen is or has an idea of a kitchen ... it can dream"; "let sera read the books or short stories and answer
in a closed book scenario; if it can't answer there might be a flaw in teaching or learning").

  python scripts/sera_ideas.py --out RUN [--book WORDNET] [--box 10]

1. Teach: first word, last word, who, where, what is - worked steps shown, the same SERA throughout.
2. Read and understand: sentences about a kitchen and other places; then, from its Field alone: what a kitchen is to
   it (what it is like, what goes on there), a word read once ('pantry'), and its dreams; a newborn beside it.
3. Closed book, stories: a passage read, then 'where is <name>?' with the passage gone - taught, then alone with new
   names.
4. Closed book, books: it reads the psychology book and the two philosophy books whole (every sentence into its
   memory); taught 'what is <term>?' on half the psychology terms the book defines once, then asked the other half and
   the philosophy books' terms with the books gone, by its own ability on what comes to mind. Measured controls (S03
   F12, reviewer): the same program without its memory, and a newborn with the same memory taught the same lesson.
5. REPORT.md: every number, and SERA's own lines verbatim.
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

os.environ.setdefault('CCOPS5_SHAPES', 'library')
os.environ.setdefault('CCOPS5_CLAIM', 'functional')
os.environ.setdefault('CCOPS5_BAND', 'claim')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402

from sera import dictionary as DICT, lang as LG, one as ONE, phi as PH, tasks as TS, talk as TK  # noqa: E402

KITCHEN = ['mary cooked dinner in the kitchen', 'john washed the dishes in the kitchen',
           'sandra ate breakfast in the kitchen', 'daniel made tea in the kitchen', 'mary baked bread in the kitchen',
           'john boiled water in the kitchen', 'sandra cut vegetables in the kitchen', 'daniel ate lunch in the kitchen']
OTHERS = ['mary watered the flowers in the garden', 'john planted a tree in the garden',
          'daniel dug the soil in the garden', 'sandra picked apples in the garden', 'sandra slept in the bedroom',
          'john made the bed in the bedroom', 'mary read a book in the bedroom', 'daniel wrote a letter in the office',
          'mary worked at the desk in the office', 'john read the report in the office',
          'john washed his hands in the bathroom', 'mary took a bath in the bathroom']
ONCE = ['sandra took the bread from the pantry']


def words(ws):
    return ' '.join(TS.text(w) for w in ws)


def describe(ideas, word, rng):
    """What a thing is to SERA, in the words it read - all from its Field (its ideas), nothing composed by us but the
    frame of the sentence."""
    s = TS.sym(word)
    if s not in ideas.of:
        return [f"SERA: I have no idea of '{word}'."]
    kind = [(TS.text(o), v) for o, v in ideas.kind(s, 5)]
    groups = [[TS.text(o) for o in g] for g in ideas.goes_on(s, 20, 8)]
    roles = sorted(ideas.of[s]['roles'].items(), key=lambda kv: -kv[1])
    lines = [f"SERA: '{word}' (met {int(ideas.of[s]['seen'])} times, sure {ideas.sure(s):.2f}):",
             f"  it is like: {', '.join(f'{w} ({v})' for w, v in kind) or 'nothing I know'}",
             f"  with it: " + ' | '.join(', '.join(g) for g in groups)]
    if roles:
        lines.append(f"  my abilities give it: {', '.join(f'{r} ({int(v)})' for r, v in roles)}")
    for sent, like in ideas.dream(s, rng, 3):
        lines.append(f"  I dream: '{words(sent)}' (as sure as it is like the thing I took it from: {like:.2f})")
    return lines


def teach(sera, out, box, log, skip=()):
    for name, build in (('first', TS.lesson_first), ('last', TS.lesson_last), ('who', TS.lesson_who),
                        ('where', TS.lesson_where), ('what is', TS.lesson_what_is)):
        if name in skip:
            log(f"taught {name}: already learned (its Field)")
            continue
        task = build(1 + len(name) * 100)
        task.name = name
        ONE.MAX_WALL = box
        t0 = time.time()
        rec = sera.live(task, teaching=True)
        log(f"taught {name}: {rec['verdict'] if rec.get('proven') else 'not proven'} | "
            f"{LG.show(rec['answer'], sera.field.names()) if rec.get('answer') is not None else '-'} | "
            f"{time.time() - t0:.0f} s | says {rec.get('said')}")


def closed(sera, build, label, box, log):
    task = build()
    task.name = label
    ONE.MAX_WALL = box
    t0 = time.time()
    rec = sera.live(task, teaching=bool(task.words))
    ex = task.data[0][0]
    seen = task.perceive(ex)
    log(f"{label}: {rec['verdict'] if rec.get('proven') else 'not proven'} | "
        f"{LG.show(rec['answer'], sera.field.names()) if rec.get('answer') is not None else '-'} | "
        f"{time.time() - t0:.0f} s")
    log(f"   e.g. the question '{words(ex[0])}' brings to mind ({len(seen) - len(ex)} memories; the latest three): "
        f"{' / '.join(words(s) for s in seen[len(ex):][-3:])}")
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--book', default=None)
    ap.add_argument('--box', type=float, default=10.0, help='minutes per world')
    ap.add_argument('--field', default=None, help='the SERA to start from (its saved Field)')
    ap.add_argument('--psych', default='D:/ai/PI&E/private/psychology-sources-20260907')
    ap.add_argument('--phil', default='D:/ai/PI&E/private/sources')
    a = ap.parse_args()
    TK.BOOK = DICT.load(a.book)
    if a.book and TK.BOOK is None:              # a named dictionary that is not there is refused, never run without
        sys.exit(f'--book {a.book}: no WordNet dictionary there (data.noun missing)')    # (ideas-4, 2026-09-29)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    lines = []

    def log(s):
        print(s, flush=True)
        lines.append(s)

    rng = np.random.default_rng([a.seed, 29])
    field = PH.Field.load(a.field) if a.field else PH.Field(a.seed)
    sera = ONE.Sera(a.seed, field)
    box = a.box * 60
    log('## 1. Taught' + (f' (from its Field {a.field})' if a.field else ''))
    known = {n for c in field.concepts for n in [field.names().get(c['id'])] if n}
    teach(sera, out, box, log, skip=known & {'first', 'last', 'who'})

    log('\n## 2. Reading, and what things are to it')
    ideas = sera._ideas()
    newborn = PH.Ideas()
    for s in KITCHEN + OTHERS + ONCE:
        ideas.read(tuple(TS.sym(w) for w in s.split()), 'the teacher')
    for s in ONCE:
        newborn.read(tuple(TS.sym(w) for w in s.split()), 'the teacher')
    for w in ('kitchen', 'pantry', 'mary', 'bread'):
        for ln in describe(ideas, w, rng):
            log(ln)
    log('A newborn that read only the pantry sentence:')
    for w in ('kitchen', 'pantry'):
        for ln in describe(newborn, w, rng):
            log(ln)
    book = TK.BOOK.says('kitchen')[:1] if TK.BOOK is not None else []
    log(f"(the dictionary says of kitchen: {book}; SERA has not read it)")

    log('\n## 3. Closed book: stories')
    first, second = TS.READERS[:24], TS.READERS[24:]
    closed(sera, lambda: TS.closed_where(a.seed, True, first), 'closed where (taught)', box, log)
    closed(sera, lambda: TS.closed_where(a.seed + 7, False, second), 'closed where (alone, new names)', box, log)

    log('\n## 4. Closed book: the books (read whole, then asked with the books gone)')
    import copy
    import sera_language as SL
    phil = SL.gutenberg_sentences(a.phil)
    books = {'psychology (OpenStax)': SL.psych_sentences(a.psych),
             'Plato, The Republic (Gutenberg 1497)': [r for r in phil if r[1] == 'gutenberg-1497.txt'],
             'Locke, An Essay Concerning Humane Understanding, vol. 1 (Gutenberg 10615)':[r for r in phil if r[1] == 'gutenberg-10615.txt']}
    defs_of = {}
    for book, rows in books.items():
        if not rows:
            log(f"{book}: not found - not read, not asked")
            continue
        t0 = time.time()
        for sentence, _ in rows:                   # every sentence as its words: lower case, no punctuation, a leading
            ws = re.findall(r'[a-z]+', sentence.lower())            # the/a/an dropped (the form the questions use)
            if ws and ws[0] in ('the', 'a', 'an'):
                ws = ws[1:]
            if ws:
                ideas.read(tuple(TS.sym(w) for w in ws), book)
        terms = {k: v for s in SL.read_sentences(rows, TK.BOOK)[0].values() for k, v in s.items()}
        defs_of[book] = {t: [s for s in sents if s[0] == t] for t, sents in terms.items()}
        once = sum(1 for d in defs_of[book].values() if len(d) == 1)
        log(f"read {book}: {len(rows)} sentences in {time.time() - t0:.0f} s; {len(terms)} terms it defines "
            f"('<term> is ...'), {once} defined once")
    log(f"its memory now: {ideas.read_n} sentences, {len(ideas.of)} things (each keeps its last {PH.IDEA_MEMORY} "
        f"situations)")

    def once(book):
        return sorted(t for t, d in defs_of.get(book, {}).items() if len(d) == 1)   # one answer (a term defined
    #                                                                                   several times has several)

    def ask(prog, who, terms, defs, mind, seed, show=0):
        """'what is <term>?' for each term, the book gone: its own proven program on what comes to mind (mind None:
        no memory). Right if its answer is the book's definition."""
        test = TS.closed_what_is(seed, False, [defs[t][0] for t in terms])
        test.mind = mind
        right, out = 0, []
        for q, ans in test._pool_q:
            x = (tuple(TS.sym(w) for w in q),)
            got = LG.safe(prog, {'g': test.perceive(x)}, who._concepts()) if prog is not None else None
            ok = got == tuple(TS.sym(w) for w in ans)
            right += ok
            if len(out) < show:
                out.append(f"SERA (closed book): {words(q)}? "
                           f"{words(got) if isinstance(got, tuple) else 'I do not know'}"
                           f"{'' if ok else '   [the book: ' + words(tuple(TS.sym(w) for w in ans)) + ']'}")
        return right, len(test._pool_q), out

    psych = 'psychology (OpenStax)'
    names = once(psych)
    order = list(np.random.default_rng([a.seed, 61]).permutation(len(names)))
    taught_terms = sorted(names[i] for i in order[:len(names) // 2])
    test_terms = sorted(names[i] for i in order[len(names) // 2:])
    before = copy.deepcopy(ideas)                  # the same memory, for a newborn (equal reading)
    lesson = lambda: TS.closed_what_is(a.seed, True, [defs_of[psych][t][0] for t in taught_terms])
    rec = closed(sera, lesson, 'closed what is (taught on half the psychology terms)', box, log)
    prog = rec.get('answer') if rec.get('proven') else None
    r, n, shown = ask(prog, sera, test_terms, defs_of[psych], ideas, a.seed + 1, show=12)
    log(f"psychology, terms it was never asked about: {r} of {n} right (taught SERA, its memory)")
    for ln in shown:
        log(ln)
    r0, n0, _ = ask(prog, sera, test_terms, defs_of[psych], None, a.seed + 1)
    log(f"the same, without its memory (the question alone): {r0} of {n0} (measured)")
    newborn = ONE.Sera(a.seed, PH.Field(a.seed))
    newborn.field.ideas = before
    nrec = closed(newborn, lesson, 'a newborn with the same memory, the same lesson', box, log)
    nprog = nrec.get('answer') if nrec.get('proven') else None
    rn, nn, _ = ask(nprog, newborn, test_terms, defs_of[psych], newborn._ideas(), a.seed + 1)
    log(f"psychology, a newborn with the same memory: {rn} of {nn} (measured)")
    for book in list(books)[1:]:
        ts = once(book)
        if not ts:
            continue
        r, n, shown = ask(prog, sera, ts, defs_of[book], ideas, a.seed + 2, show=6)
        rn, nn, _ = ask(nprog, newborn, ts, defs_of[book], newborn._ideas(), a.seed + 2)
        log(f"{book}, never taught on this book: {r} of {n} right (taught SERA); newborn with the same memory {rn} "
            f"of {nn}")
        for ln in shown:
            log(ln)

    log('\n## 5. After reading the books: what some of their things are to it')
    for w in ('memory', 'language', 'depression', 'justice', 'soul', 'property'):
        for ln in describe(ideas, w, rng):
            log(ln)
    (out / 'REPORT.md').write_text('# SERA: ideas of things and closed-book reading\n\n' + '\n'.join(lines) + '\n',
                                   encoding='utf-8')
    sera.field.save(out / 'field.pkl')
    print('IDEAS DONE', flush=True)


if __name__ == '__main__':
    main()
