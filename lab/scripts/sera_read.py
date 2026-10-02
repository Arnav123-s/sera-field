"""SERA reads a dictionary (2026-09-28, the author: "give it a dictionary and ask it to understand it, learn it, so it can
understand English better and communicate better with us").

  python scripts/sera_read.py --field RUN/field.pkl --book /content/wordnet

1. Its glossary: every word it has heard, what the word means to it (one of its own ideas, shown in its own language,
   or an input or a direction), how sure it is, and what the book says.
2. The observer's quiz (never shown to SERA): everyday words it has never heard, each put by us beside a word it knows
   that a speaker would mean by it ('flip' for 'reverse'). SERA understands a quiz word right when the meaning it takes
   from the book is the meaning its own known word has for it. Without the book it takes nothing from an unheard word.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sera import dictionary as DICT, lang as LG, phi as PH, talk as TK  # noqa: E402

QUIZ = {'reverse': ('flip', 'invert', 'backward', 'mirror'), 'sum': ('total', 'add', 'altogether'),
        'count': ('number', 'tally', 'how many'), 'double': ('twofold', 'duplicate'), 'twice': ('two times',),
        'square': ('squared',), 'spring': ('elastic', 'coil', 'bounce'), 'drag': ('resistance', 'friction'),
        'wind': ('breeze', 'gust'), 'ripple': ('wave', 'undulation'), 'stiff': ('rigid', 'firm'),
        'rub': ('friction', 'scrape'), 'fast': ('quick', 'speed'), 'far': ('distant', 'position'),
        'last': ('final', 'end'), 'odd': ('uneven',), 'always': ('constantly', 'forever'), 'back': ('backward', 'return')}


def meaning_words(m, field):
    names = field.names()
    kind, ref = m
    if kind == 'concept':
        c = next((c for c in field.concepts if c['id'] == ref), None)
        return f"my idea {names.get(ref, ref)} = {LG.show(c['body'], names)[:60]}" if c else f'my idea {ref}'
    return f'{kind} {ref}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--field', required=True)
    ap.add_argument('--book', default=None)
    a = ap.parse_args()
    field = PH.Field.load(a.field)
    lex = field.lexicon
    TK.BOOK = DICT.load(a.book)
    book = TK.BOOK
    print(f'The book: {len(book.senses)} words, {book.n} senses. SERA knows {len(lex.heard)} words from its own '
          f'experience.\n', flush=True)
    print('### Its glossary: each word it heard, what it means to it, and what the book says\n')
    for w in sorted(lex.heard):
        u = lex.understand(w)
        top = sorted(u['meaning'].items(), key=lambda kv: -kv[1])[:1]
        mine = f"{meaning_words(top[0][0], field)} (sure {top[0][1]:.2f})" if top else 'nothing yet'
        print(f"- **{w}** (heard {lex.heard[w]} times): {mine}. The book: {'; '.join(u['book'][:1]) or '-'}")
    print('\n### The quiz: words it never heard\n')
    print('| Our word | What we mean (a word it knows) | It takes it as | Through | Sure | Right |')
    print('|---|---|---|---|---|---|')
    right = n = 0
    TK_BOOK = TK.BOOK
    for known, news in QUIZ.items():
        if known not in lex.heard or not lex.meaning(known):
            continue
        want = max(lex.meaning(known).items(), key=lambda kv: kv[1])[0]
        for new in news:
            if new in lex.heard:
                continue
            u = lex.understand(new.replace(' ', '_'))
            got = max(u['meaning'].items(), key=lambda kv: kv[1])[0] if u['meaning'] else None
            ok = got == want
            right += ok
            n += 1
            print(f"| {new} | {known} ({meaning_words(want, field)[:50]}) | "
                  f"{meaning_words(got, field)[:50] if got else 'nothing'} | {', '.join(u['through']) or '-'} | "
                  f"{u['sure']:.2f} | {'yes' if ok else 'no'} |")
    TK.BOOK = None
    blind = sum(1 for known, news in QUIZ.items() if known in lex.heard and lex.meaning(known)
                for new in news if new not in lex.heard and lex.understand(new.replace(' ', '_'))['meaning'])
    TK.BOOK = TK_BOOK
    print(f'\nWith the book it understood {right} of {n} words it never heard; without it, {blind} of {n}.')
    print('READ DONE', flush=True)


if __name__ == '__main__':
    main()
