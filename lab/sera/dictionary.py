"""A dictionary SERA reads (2026-09-28, the author: "give it a dictionary and ask it to understand it, learn it, so it can
understand English better and communicate better with us").

The dictionary (Princeton WordNet 3.0: each sense of a word with its definition, its examples, the other words for it
and what it is a kind of) is a book outside SERA, like a world. It gives words about words; only SERA's experience ties
a word to anything. A word SERA knows is one it grounded itself: heard where one of its own meanings was true (one of
its concepts, an input, a direction; sera.talk). Reading, it learns:
- how close two words are: their definitions (with the other words for them, and what they are a kind of) share words,
  each weighted by how much it tells - the log of how rare it is in the whole book, so "the" and "of" tell nothing and
  no list of little words is needed; words that begin alike are one word to it (turn, turned, turning);
- what a word it never heard means to it: the meanings of the known words closest to it, by closeness - a guess, said
  as a guess, weighed by how close, that its own experience then confirms or corrects (sera.talk.Lexicon.understand);
- what the book says a word means, to tell us.
"""
import math
import os
import re
from pathlib import Path

POS = {'n': 'noun', 'v': 'verb', 'a': 'adj', 's': 'adj', 'r': 'adv'}
_TOKEN = re.compile(r"[a-z]+")


class Book:
    """WordNet read from its data files (data.noun, data.verb, data.adj, data.adv, index.*)."""

    def __init__(self, path):
        path = Path(path)
        self.synsets = {}              # (pos, offset) -> dict(words, text, tokens, kinds)
        self.senses = {}               # lemma -> [(pos, offset)], most common sense first
        for pos in ('noun', 'verb', 'adj', 'adv'):
            for line in open(path / f'data.{pos}', encoding='utf-8', errors='replace'):
                if line.startswith('  '):
                    continue
                head, _, gloss = line.partition(' | ')
                f = head.split()
                off, p = f[0], f[2]
                n = int(f[3], 16)
                words = [re.sub(r'\(.*\)$', '', f[4 + 2 * i]).lower() for i in range(n)]
                k = 4 + 2 * n
                ptrs = int(f[k])
                kinds = []
                for j in range(ptrs):
                    sym, o, q = f[k + 1 + 4 * j], f[k + 2 + 4 * j], f[k + 3 + 4 * j]
                    if sym in ('@', '@i'):
                        kinds.append(('a' if q == 's' else q, o))
                text = gloss.strip().split('; "')[0].strip()
                self.synsets[('a' if p == 's' else p, off)] = dict(words=words, text=text, kinds=kinds,
                                                                     tokens=_TOKEN.findall(text.lower()))
        for pos, p in (('noun', 'n'), ('verb', 'v'), ('adj', 'a'), ('adv', 'r')):
            for line in open(path / f'index.{pos}', encoding='utf-8', errors='replace'):
                if line.startswith('  '):
                    continue
                f = line.split()
                lemma, n = f[0].lower(), int(f[2])
                offs = f[-n:]
                self.senses.setdefault(lemma, []).extend((p, o) for o in offs)
        self.exc = {}                  # a form the book lists as another word's (has -> have, mice -> mouse)
        for pos in ('noun', 'verb', 'adj', 'adv'):
            p = path / f'{pos}.exc'
            if p.exists():
                for line in open(p, encoding='utf-8', errors='replace'):
                    f = line.split()
                    if len(f) >= 2:
                        self.exc.setdefault(f[0].lower(), f[1].lower())
        self.df = {}
        for s in self.synsets.values():
            for t in set(s['tokens']):
                self.df[t] = self.df.get(t, 0) + 1
        self.n = len(self.synsets)
        self._bags = {}

    # --- reading ---
    def root(self, token):
        """The book's word a token is (its own spelling, a form the book lists as another word's: 'has' -> 'have', or
        the longest word of the book it begins with, nearly all of it: 'turned' -> 'turn')."""
        if token in self.senses:
            return token
        if token in self.exc:
            return self.exc[token]
        for k in range(len(token) - 1, max(3, len(token) - 4), -1):
            if token[:k] in self.senses:
                return token[:k]
        return token

    def weight(self, token):
        """How much a word in a definition tells: the log of how rare it is in the book."""
        return math.log((self.n + 1) / (self.df.get(token, 0) + 1))

    def bag(self, word):
        """What the book says about a word, as words: its definitions (the common senses first), the other words for
        it, and what it is a kind of - each word weighted by how much it tells."""
        word = word.lower().replace(' ', '_')
        hit = self._bags.get(word)
        if hit is not None:
            return hit
        out = {}
        for rank, key in enumerate(self.senses.get(self.root(word), [])[:8]):
            s = self.synsets.get(key)
            if s is None:
                continue
            w = 1.0 / (rank + 1)
            toks = s['tokens'] + [t for x in s['words'] for t in x.split('_')]
            for k2 in s['kinds']:
                toks += [t for x in self.synsets.get(k2, {}).get('words', []) for t in x.split('_')]
            for t in toks:
                t = self.root(t)
                out[t] = out.get(t, 0.0) + w * self.weight(t)
        norm = math.sqrt(sum(v * v for v in out.values())) or 1.0
        out = {t: v / norm for t, v in out.items()}
        self._bags[word] = out
        return out

    def closeness(self, a, b):
        """How close two words are in the book (0 to 1): what the book says about each, compared."""
        if self.root(a.lower()) == self.root(b.lower()):
            return 1.0
        x, y = self.bag(a), self.bag(b)
        if len(x) > len(y):
            x, y = y, x
        return float(sum(v * y.get(t, 0.0) for t, v in x.items()))

    def says(self, word, most=2):
        """What the book says a word means: its first definitions."""
        out = []
        for key in self.senses.get(self.root(word.lower()), [])[:most]:
            s = self.synsets.get(key)
            if s is not None:
                out.append(f"({POS[key[0]]}) {s['text']}")
        return out

    def knows(self, word):
        return self.root(word.lower()) in self.senses


def load(path=None):
    """The book at `path` (or $SERA_BOOK), or None when there is none."""
    path = path or os.environ.get('SERA_BOOK')
    if not path or not (Path(path) / 'data.noun').exists():
        return None
    return Book(path)
