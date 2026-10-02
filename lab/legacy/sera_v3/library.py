"""SERA's library (B5): what it has proven, kept forever, and what that knowledge predicts it has not yet met.

- Append-only, hash-chained entries: each is a law the independent checker verified, with its world, its certificate
  digest and its prior-weighted evidence. Nothing is ever edited or removed (canalization).
- Admission (D13, lifelong false-discovery control): every world lived is one e-LOND test j (`new_world`, called for
  every world whether or not the mind was sure: e_j = 0 when not sure; independent review review L1: an index advanced only by
  verified claims is data-dependent). A verified claim enters only if its prior-weighted e-value passes
  alpha_j = ALPHA_FDR * gamma_j * (entries so far + 1), gamma_j = 6 / (pi^2 j^2).
  SCOPE (independent review review L2): pi(F) * min_b E(F:b) is an e-value against "F is wrong" only when the truth is among the
  certificate's rivals, i.e. in the ledger's space and not containing F. Two error kinds lie outside this guarantee: a
  missing term (the truth contains F) and an invented truth the imagination never put in the ledger. For those, the
  frozen-wrong rate of admitted entries is reported directly (generations.py), not claimed from e-LOND.
- Empty slots (Gell-Mann): certified laws laid out in the grammar's structure table. A slot is predicted when its row
  and its column both hold certified laws but the slot itself has not been met. SERA dreams its predictions in sleep.
"""
import hashlib
import json
import math
from collections import Counter

from ccops5.core import grammar
from . import lawspace as LS

ALPHA_FDR = 0.05


class Library:
    def __init__(self):
        self.entries = []
        self.candidates = 0
        self.met = set()                      # every law it has been sure of or been told of (not only admitted)

    @property
    def head(self):
        return self.entries[-1]['hash'] if self.entries else '0' * 16

    def new_world(self):
        """Every world lived is one test (e = 0 when the mind was not sure)."""
        self.candidates += 1

    def alpha_now(self):
        j = max(self.candidates, 1)
        return ALPHA_FDR * 6 / (math.pi ** 2 * j * j) * (len(self.entries) + 1)

    def offer(self, family, cert, world_id, level=None):
        """A checker-verified claim asks to enter. Returns True if admitted (e-LOND). `level` (rev 5.1): the level of
        the world's own test, taken when it was lived (a verdict from the judge's office comes worlds later; admissions
        still pending then were not counted, so the level is never larger than LOND's)."""
        family = grammar.canonical(family)
        self.met.add(family)
        level = self.alpha_now() if level is None else level   # e-LOND level of the world's test
        log_e = min(cert.rivals.values()) + cert.log_prior if cert.rivals else math.inf   # prior-weighted evidence
        if log_e < math.log(1 / level):
            return False
        body = dict(family=[list(t) for t in family], world=world_id, digest=cert.digest, log_e=round(log_e, 4),
                    prev=self.head)
        h = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()[:16]
        self.entries.append(dict(body, hash=h, family_t=family))
        return True

    def verify_chain(self):
        prev = '0' * 16
        for e in self.entries:
            body = {k: e[k] for k in ('family', 'world', 'digest', 'log_e', 'prev')}
            if e['prev'] != prev or hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()[:16] != e['hash']:
                return False
            prev = e['hash']
        return True

    def counts(self):
        return Counter(e['family_t'] for e in self.entries)

    def terms(self):
        return sorted({t for e in self.entries for t in e['family_t']}, key=grammar._key)

    def empty_slots(self, limit=64):
        """Laws the library's pattern predicts but it has not met (row and column both certified)."""
        known = self.terms()
        prods = {(t[1], t[2]) for t in known if t[0] == 'product'}
        pows = {(t[1], t[2]) for t in known if t[0] == 'power'}
        drives = {(t[1], t[2]) for t in known if t[0] == 'drive'}
        ideas = [t for t in known if t in grammar.IDEAS]
        pairs = [e['family_t'] for e in self.entries if len(e['family_t']) == 2]
        out = []
        for a, b in prods:                                    # products: swap one factor with another certified one
            for c, d in prods:
                for s in (('product', a, d), ('product', c, b)):
                    out.append((s,))
        for inp, p in pows:                                   # powers: the other input; neighbouring exponents
            other = 'speed' if inp == 'position' else 'position'
            out.append((('power', other, p),))
            for q in (round(p - 0.1, 1), round(p + 0.1, 1), round(p - 0.2, 1), round(p + 0.2, 1)):
                if q in LS.P_VALUES:
                    out.append((('power', inp, q),))
        for fn, w in drives:                                  # drives: the other function; neighbouring frequencies
            out.append((('drive', 'cos' if fn == 'sin' else 'sin', w),))
            for q in (round(w - 0.1, 1), round(w + 0.1, 1)):
                if q in LS.W_VALUES:
                    out.append((('drive', fn, q),))
        for f1 in pairs:                                      # pairs: swap one member with a member of another pair
            for f2 in pairs:
                for x in f1:
                    for y in f2:
                        rest = tuple(t for t in f1 if t != x)
                        out.append(rest + (y,))
        for t in known:                                       # an invented term met alone, with a known idea
            if LS.is_open(t):
                for i in ideas:
                    out.append((t, i))
        seen, slots = set(), []
        for f in out:
            f = grammar.canonical(f)
            if len(f) != len(set(f)) or f in seen or f in self.met or not LS.claimable(f):
                continue
            seen.add(f)
            slots.append(f)
        return slots[:limit]
