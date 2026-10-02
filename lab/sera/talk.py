"""SERA's words (plan revision 6; the author, 2026-09-27: "do not give it a predefined set of words, sentences, formulas
- it must learn and be taught, and use them on its own").

SERA is born with no words. What it has is a way to learn them:
- a word is any token it hears (an open vocabulary: nothing is listed in advance);
- what a word can mean is one of the things SERA itself can tell about a law it understands: one of its own concepts
  (a shape it made, a program, a rule), the input it depends on (where, how fast, when - its senses), or which way it
  pushes (back or along). This set grows as SERA invents: a new concept is a new thing a word can mean;
- it learns which word means what across situations (cross-situational learning, the IBM Model 1 alignment of Brown et
  al. 1993 as used for child word learning by Yu and Ballard 2007): each word heard in a situation stands for one of
  the meanings true of what happened there; t(word | meaning) is re-estimated by expectation-maximization over the
  situations it remembers (the last MAX_SITUATIONS). A word always heard with the same meaning, and whose other
  companions are explained by other words, comes to mean it.

It uses them on its own:
- hearing: words heard while it works are evidence about the law (Model 1's likelihood of the sentence under each law's
  meanings); a word whose meaning it has not learned moves nothing;
- speaking: it says a law in its own words - for each meaning of the law, the word it has learned for it, if it holds
  it with at least SPEAK probability; for a concept nobody named, a word it coins itself (made from its own random
  syllables, then kept: its own name for its own idea);
- the observer's checking of what it says uses the teacher's language (which it never reads).

The teacher's language (TEACHER) belongs to the caretaker, not to SERA: it is how we talk when we teach. SERA hears only
the tokens.
"""
import math

import numpy as np

BOOK = None                      # a dictionary it can read (sera.dictionary.Book; the program sets it; 2026-09-28)
MAX_SITUATIONS = 400
EM_ITERS = 8
SPEAK = 0.6                      # it uses a word for a meaning when P(meaning | word) is at least this
FLOOR = 1e-3                     # a word's chance under a meaning it has never been heard with
SLIP = 0.05                      # a sentence's words, each unrelated to the law with this chance
SYLLABLES = ('ka', 'lo', 'mi', 'tu', 're', 'sa', 'no', 'vi', 'pe', 'du', 'fo', 'ri')   # sounds, not words


# --- the teacher's language (the caretaker's; SERA never reads this table) ---
TEACHER = {('position', 'straight'): 'spring', ('position', 'cubic'): 'stiff', ('position', 'growing'): 'bend',
           ('position', 'steps'): 'wall', ('position', 'wave'): 'ripple', ('speed', 'straight'): 'drag',
           ('speed', 'growing'): 'thick', ('speed', 'steps'): 'rub', ('speed', 'cubic'): 'syrup',
           ('speed', 'wave'): 'wobble', ('nothing', 'steady'): 'wind'}
TEACHER_INPUT = {'position': 'far', 'speed': 'fast', 'time': 'while', 'nothing': 'always'}
TEACHER_SIGN = {-1: 'back', 1: 'along'}


def meanings_of(law):
    """What SERA can tell about a law it understands, as meanings: [('concept', id) ...] + [('input', s) ...] +
    [('sign', +-1) ...]. `law` is a list of parts, each a dict(concept=id or None, input=s, sign=+-1)."""
    out = []
    for p in law:
        if p.get('concept') is not None:
            out.append(('concept', p['concept']))
        if p.get('input'):
            out.append(('input', p['input']))
        if p.get('sign'):
            out.append(('sign', int(p['sign'])))
    return list(dict.fromkeys(out))


class Lexicon:
    """What SERA's words mean to it, learned from the situations it remembers."""

    def __init__(self, seed=0):
        self.situations = []              # [(tokens, meanings)]
        self.t = {}                       # meaning -> {word: t(word | meaning)}
        self.coined = {}                  # meaning -> its own word
        self.heard = {}                   # word -> times heard
        self._rng = np.random.default_rng([seed, 4242])

    # --- learning ---
    def hear(self, tokens, meanings):
        """A situation: words heard where these meanings were true (known after SERA understood the law there)."""
        tokens, meanings = [str(w) for w in tokens], list(meanings)
        if not tokens or not meanings:
            return
        for w in tokens:
            self.heard[w] = self.heard.get(w, 0) + 1
        self.situations.append((tokens, meanings))
        del self.situations[:-MAX_SITUATIONS]
        self._em()

    def _em(self):
        words = sorted({w for ws, _ in self.situations for w in ws})
        means = sorted({m for _, ms in self.situations for m in ms}, key=repr)
        t = {m: {w: 1.0 / len(words) for w in words} for m in means}
        for _ in range(EM_ITERS):
            count = {m: {} for m in means}
            for ws, ms in self.situations:
                for w in ws:
                    z = sum(t[m].get(w, 0.0) for m in ms)
                    if z <= 0:
                        continue
                    for m in ms:
                        c = t[m].get(w, 0.0) / z
                        count[m][w] = count[m].get(w, 0.0) + c
            t = {}
            for m in means:
                tot = sum(count[m].values())
                t[m] = {w: c / tot for w, c in count[m].items()} if tot > 0 else {}
        self.t = t

    # --- what a word means to it ---
    def meaning(self, word):
        """{meaning: P(meaning | word)} (flat over meanings when the word is unknown)."""
        scores = {m: tw.get(word, 0.0) for m, tw in self.t.items()}
        tot = sum(scores.values())
        if tot <= 0:
            return {}
        return {m: s / tot for m, s in scores.items() if s > 0}

    def grounded(self, level=0.9, min_heard=2):
        """[(word, meaning, probability)] it holds with at least `level`, heard at least `min_heard` times."""
        out = []
        for w, n in sorted(self.heard.items()):
            if n < min_heard:
                continue
            p = self.meaning(w)
            if p:
                m = max(p, key=p.get)
                if p[m] >= level:
                    out.append((w, m, p[m]))
        return out

    # --- using them ---
    def log_likelihood(self, tokens, meanings):
        """log P(tokens | a law with these meanings): each word stands for one of them (or slips)."""
        if not tokens:
            return 0.0
        vocab = max(len({w for ws, _ in self.situations for w in ws}), 1)
        ms = list(meanings) or [None]
        out = 0.0
        for w in tokens:
            if w not in self.heard or not any(w in tw for tw in self.t.values()):
                close, sure = self._near(w)               # a word it never heard: what the book says, if it has one
                if not close:
                    continue                              # otherwise it tells it nothing
                tot = sum(c for c, _ in close)
                p = sum(max(sum(c * self.t.get(m, {}).get(v, 0.0) for c, v in close) / tot, FLOOR)
                        for m in ms if m is not None) / len(ms)
                out += sure * math.log((1 - SLIP) * p + SLIP / vocab)     # as its closest known words would, as
                continue                                                  # sure as they are close
            p = sum(max(self.t.get(m, {}).get(w, 0.0), FLOOR) for m in ms if m is not None) / len(ms)
            out += math.log((1 - SLIP) * p + SLIP / vocab)
        return out

    def _near(self, word, near=3):
        """The known words closest to a word it never heard, in the book: ([(closeness, word)], how sure)."""
        if BOOK is None or not BOOK.knows(word):
            return [], 0.0
        close = sorted(((BOOK.closeness(word, v), v) for v in self.heard if v != word and self.meaning(v)),
                       reverse=True)[:near]
        close = [(c, v) for c, v in close if c > 0]
        return close, (close[0][0] if close else 0.0)

    def understand(self, word):
        """What a word means to it, as it would tell us: dict(meaning {meaning: p}, how (heard / the book / not
        known), sure, through (the known words it went through), book (what the book says))."""
        book = BOOK.says(word) if BOOK is not None else []
        if word in self.heard and self.meaning(word):
            p = self.meaning(word)
            return dict(meaning=p, how='heard', sure=max(p.values()), through=[], book=book)
        close, sure = self._near(word)
        if not close:
            return dict(meaning={}, how='not known', sure=0.0, through=[], book=book)
        scores = {}
        for c, v in close:
            for m, q in self.meaning(v).items():
                scores[m] = scores.get(m, 0.0) + c * q
        tot = sum(scores.values())
        return dict(meaning={m: s / tot for m, s in scores.items()}, how='the book', sure=sure,
                    through=[v for _, v in close], book=book)

    def word_for(self, meaning, coin=False):
        """Its word for a meaning: the one it has learned (P(meaning | word) >= SPEAK), else its own coined one; with
        `coin`, it makes one up for a concept nobody named."""
        best, bp = None, 0.0
        for w in self.heard:
            p = self.meaning(w).get(meaning, 0.0)
            if p > bp:
                best, bp = w, p
        if best is not None and bp >= SPEAK:
            return best
        if meaning in self.coined:
            return self.coined[meaning]
        if coin and meaning[0] == 'concept':
            used = set(self.heard) | set(self.coined.values())
            while True:
                w = ''.join(self._rng.choice(SYLLABLES, size=2))
                if w not in used:
                    break
            self.coined[meaning] = w
            return w
        return None

    def say(self, meanings, coin=True):
        """A law in its own words: one word per meaning it has a word for (in the order of the meanings)."""
        words = []
        for m in meanings:
            w = self.word_for(m, coin=coin)
            if w is not None and w not in words:
                words.append(w)
        return words


# --- the teacher speaks (the caretaker's side; uses the hidden law) ---
def teacher_tokens(family, signs, rng):
    """The caretaker's sentence about a hidden law (a family of the judge's grammar) and the sign of each part: a name
    for each part, the input it depends on and which way it pushes, in a shuffled order (SERA must not rely on word
    order). Words the teacher has no name for are left out (it names only what it was taught to name)."""
    toks = []
    for term, sign in zip(family, signs):
        name = TEACHER.get(term)
        if name is None and term[0] == 'drive':
            name = 'motor'
        if name:
            toks.append(name)
        inp = term[0] if term[0] in ('position', 'speed', 'nothing') else 'time' if term[0] == 'drive' else None
        if inp:
            toks.append(TEACHER_INPUT[inp])
        if sign and inp not in ('time', 'nothing'):
            toks.append(TEACHER_SIGN[int(sign)])
    toks = list(dict.fromkeys(toks))
    rng.shuffle(toks)
    return toks


def teacher_truth(word, family, signs):
    """Is `word` (in the teacher's language) true of the hidden law? For the observer's check of what SERA says."""
    for term, sign in zip(family, signs):
        if TEACHER.get(term) == word or (term[0] == 'drive' and word == 'motor'):
            return True
        inp = term[0] if term[0] in ('position', 'speed', 'nothing') else 'time' if term[0] == 'drive' else \
            term[1] if term[0] in ('cell', 'shape') else None          # a law in no list still has its input
        if inp and TEACHER_INPUT[inp] == word:
            return True
        if sign and TEACHER_SIGN.get(int(sign)) == word and inp not in ('time', 'nothing'):
            return True
    return False
