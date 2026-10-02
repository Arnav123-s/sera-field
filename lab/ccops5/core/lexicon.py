"""Outcome-conditioned word evidence and checked mass estimates."""

import math
from dataclasses import dataclass, field


@dataclass
class Lexicon:
    vocabulary: object
    alpha: float = 1e-3
    n: dict = field(init=False)
    log_q: dict = field(init=False)
    N0: dict = field(init=False)
    N1: dict = field(init=False)
    mass: dict = field(init=False)
    logw: dict = field(init=False)
    seen: dict = field(init=False)
    unseen_mass: dict = field(init=False)
    log_pooled: dict = field(init=False)
    reference: bool = field(default=False, init=False)
    definitions: dict = field(default_factory=dict, init=False)

    def __post_init__(self):
        self.vocabulary = tuple(sorted(set(self.vocabulary)))
        if not self.vocabulary:
            raise ValueError("vocabulary must not be empty")
        if self.alpha <= 0:
            raise ValueError("alpha must be positive")
        self.n = {w: {} for w in self.vocabulary}
        self.log_q = {w: 0.0 for w in self.vocabulary}
        self.N0 = {w: 0 for w in self.vocabulary}
        self.N1 = {w: 0 for w in self.vocabulary}
        self.mass = {w: {"n": 0, "mean": 0.0, "M2": 0.0} for w in self.vocabulary}
        self.logw = {w: {'kt': math.log(0.5), 'unseen': math.log(0.5)} for w in self.vocabulary}
        self.seen = {w: [] for w in self.vocabulary}
        self.unseen_mass = {w: 0.5 for w in self.vocabulary}
        self.log_pooled = {w: 0.0 for w in self.vocabulary}

    @classmethod
    def with_definitions(cls, vocabulary, table, alpha=1e-3):
        result = cls(vocabulary, alpha)
        result.reference = True
        result.definitions = {w: table[w] for w in result.vocabulary if w in table}
        return result

    # The e-process numerator is a Bayesian mixture of predictors of "was w heard?" given the outcome (development note,
    # 2026-09-24; the first version used only the per-outcome KT predictor, which pays a learning cost on every
    # outcome stream and grounded an informative word in 9 of 100 test lives):
    #   'kt'   per-outcome KT, prior 1/2 (a word may relate to several outcomes);
    #   k      "the word is about outcome k": KT on worlds with outcome k and KT on all others, prior
    #          (1/2) * 6 / (pi^2 r^2), where r is the rank of k's first appearance (fixed in advance, so valid);
    #   unseen the outcomes not seen yet act as one block (they all predict with the pooled KT until they appear).
    # A mixture of predictable predictors is predictable, so log E_w keeps its guarantee.
    @staticmethod
    def _kt(a_h, a_other):
        return math.log((a_h + 0.5) / (a_h + a_other + 1.0))

    @staticmethod
    def _logsumexp(xs):
        top = max(xs)
        return top + math.log(sum(math.exp(x - top) for x in xs))

    def _rank_prior(self, r):
        return 0.5 * 6.0 / (math.pi ** 2 * r * r)

    def _component_logq(self, word, comp, h, outcome):
        """log q_m(h | outcome) for one component, from counts before this update."""
        n0, n1 = self.N0[word], self.N1[word]
        if comp == 'kt':
            a0, a1 = self.n[word].get(outcome, [0, 0])
            return self._kt(a1 if h else a0, a0 if h else a1)
        if comp == 'unseen':
            return self._kt(n1 if h else n0, n0 if h else n1)
        k0, k1 = self.n[word].get(comp, [0, 0])
        if outcome == comp:
            return self._kt(k1 if h else k0, k0 if h else k1)
        o0, o1 = n0 - k0, n1 - k1
        return self._kt(o1 if h else o0, o0 if h else o1)

    def update(self, heard, outcome):
        heard = set(heard)
        for word in self.vocabulary:
            h = int(word in heard)
            lw = self.logw[word]
            if outcome not in self.seen[word]:          # its component splits off the unseen block
                self.seen[word].append(outcome)
                r = len(self.seen[word])
                prior = self._rank_prior(r)
                left = self.unseen_mass[word]
                lw[outcome] = math.log(prior) + self.log_pooled[word]
                self.unseen_mass[word] = max(left - prior, 0.0)
                lw['unseen'] = (math.log(self.unseen_mass[word]) + self.log_pooled[word]
                                if self.unseen_mass[word] > 0 else -math.inf)
            before = self._logsumexp(list(lw.values()))
            for comp in list(lw):
                if lw[comp] > -math.inf:
                    lw[comp] += self._component_logq(word, comp, h, outcome)
            self.log_q[word] += self._logsumexp(list(lw.values())) - before
            n0, n1 = self.N0[word], self.N1[word]
            self.log_pooled[word] += self._kt(n1 if h else n0, n0 if h else n1)
            counts = self.n[word].setdefault(outcome, [0, 0])
            counts[h] += 1
            self.N1[word] += h
            self.N0[word] += 1 - h

    def predictive(self, word, h, outcome):
        """The mixture's current probability that `word` is heard (h=1) or not (h=0) in a world with `outcome`."""
        lw = dict(self.logw[word])
        if outcome not in self.seen[word]:
            r = len(self.seen[word]) + 1
            lw[outcome] = math.log(self._rank_prior(r)) + self.log_pooled[word]
        vals = [(v, self._component_logq(word, c, h, outcome)) for c, v in lw.items() if v > -math.inf]
        return math.exp(self._logsumexp([v + q for v, q in vals]) - self._logsumexp([v for v, _ in vals]))

    @staticmethod
    def _xlogx(k, total):
        return 0.0 if k == 0 else k * math.log(k / total)

    def log_e(self, word):
        total = self.N0[word] + self.N1[word]
        if total == 0:
            return 0.0
        return self.log_q[word] - self._xlogx(self.N1[word], total) - self._xlogx(self.N0[word], total)

    def threshold(self):
        return math.log(len(self.vocabulary) / self.alpha)

    def grounded(self, word):
        return self.log_e(word) >= self.threshold()

    def grounded_words(self):
        return sorted(w for w in self.vocabulary if self.grounded(w))

    def log_prior(self, heard, outcome):
        heard = set(heard)
        if self.reference:
            total = 0.0
            for word in sorted(heard):
                if word in self.definitions:
                    total += math.log(0.99 if self.definitions[word] == outcome else 0.01)
            return total
        total = 0.0
        for word in self.grounded_words():
            total += math.log(self.predictive(word, int(word in heard), outcome))
        return total

    def update_mass(self, word, log_mu):
        if word not in self.mass:
            raise KeyError(word)
        item = self.mass[word]
        item["n"] += 1
        delta = float(log_mu) - item["mean"]
        item["mean"] += delta / item["n"]
        item["M2"] += delta * (float(log_mu) - item["mean"])

    def predict_mass(self, heard):
        for word in sorted(set(heard)):
            if word in self.mass and self.mass[word]["n"] >= 3:
                item = self.mass[word]
                sd = math.sqrt(max(0.0, item["M2"]) / (item["n"] - 1))
                return item["mean"], sd, item["n"]
        return None

    def state(self):
        return {
            "vocabulary": list(self.vocabulary), "alpha": self.alpha,
            "n": {w: {o: list(c) for o, c in sorted(self.n[w].items())} for w in self.vocabulary},
            "log_q": dict(self.log_q), "N0": dict(self.N0), "N1": dict(self.N1),
            "mass": {w: dict(self.mass[w]) for w in self.vocabulary},
            "reference": self.reference, "definitions": dict(self.definitions),
            "logw": {w: dict(self.logw[w]) for w in self.vocabulary},
            "seen": {w: list(self.seen[w]) for w in self.vocabulary},
            "unseen_mass": dict(self.unseen_mass), "log_pooled": dict(self.log_pooled),
        }

    @classmethod
    def from_state(cls, state):
        result = cls(state["vocabulary"], state["alpha"])
        result.n = {w: {o: list(c) for o, c in state["n"][w].items()} for w in result.vocabulary}
        result.log_q = {w: float(state["log_q"][w]) for w in result.vocabulary}
        result.N0 = {w: int(state["N0"][w]) for w in result.vocabulary}
        result.N1 = {w: int(state["N1"][w]) for w in result.vocabulary}
        result.mass = {w: dict(state["mass"][w]) for w in result.vocabulary}
        result.reference = bool(state.get("reference", False))
        result.definitions = dict(state.get("definitions", {}))
        result.logw = {w: {k: float(v) for k, v in state["logw"][w].items()} for w in result.vocabulary}
        result.seen = {w: list(state["seen"][w]) for w in result.vocabulary}
        result.unseen_mass = {w: float(state["unseen_mass"][w]) for w in result.vocabulary}
        result.log_pooled = {w: float(state["log_pooled"][w]) for w in result.vocabulary}
        return result
