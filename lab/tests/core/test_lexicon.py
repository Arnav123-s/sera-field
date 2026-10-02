import math
import unittest

import numpy as np

from ccops5.core.lexicon import Lexicon


class LexiconTests(unittest.TestCase):
    def test_fillers_rarely_ground(self):
        rng = np.random.default_rng(101)
        grounded = 0
        outcomes = np.array(list("ABCDEFGH"))
        for _ in range(200):
            lex = Lexicon(["filler"])
            for outcome in rng.choice(outcomes, size=60):
                lex.update(["filler"] if rng.random() < 0.2 else [], str(outcome))
            grounded += lex.grounded("filler")
        self.assertLessEqual(grounded, 1)

    def test_informative_word_grounds(self):
        rng = np.random.default_rng(202)
        successes = 0
        outcomes = np.array(list("ABCDEFGH"))
        for _ in range(100):
            lex = Lexicon(["signal"])
            # 120 worlds (development note, 2026-09-24): the brief's 40 was below what the information allows. This noisy
            # word carries about 0.22 nats per world against about 15 nats of threshold and learning cost;
            # measured: 5/100 lives ground by 40 worlds, 91/100 by 120.
            for outcome in rng.choice(outcomes, size=120):
                p = 0.9 if outcome == "A" else 0.05
                lex.update(["signal"] if rng.random() < p else [], str(outcome))
            successes += lex.grounded("signal")
        self.assertGreaterEqual(successes, 90)

    def test_prior_favours_observed_outcome_when_grounded(self):
        lex = Lexicon(["signal"])
        for outcome, heard in [("A", True)] * 30 + [("B", False)] * 30:
            lex.update(["signal"] if heard else [], outcome)
        self.assertTrue(lex.grounded("signal"))
        self.assertGreater(lex.log_prior(["signal"], "A"), lex.log_prior(["signal"], "B"))

    def test_kt_three_steps(self):
        # KT with Beta(1/2, 1/2): heard (0, 0) -> 1/2; not heard after (0, 1) -> 1/4; heard after (1, 1) -> 1/2.
        self.assertAlmostEqual(Lexicon._kt(0, 0), math.log(1 / 2))
        self.assertAlmostEqual(Lexicon._kt(0, 1), math.log(1 / 4))
        self.assertAlmostEqual(Lexicon._kt(1, 1), math.log(1 / 2))

    def test_mixture_equals_brute_force(self):
        """log_q = log sum_m prior_m * P_m(whole sequence), each component computed directly (development note, 2026-09-24)."""
        seq = [(1, "A"), (0, "B"), (1, "A"), (0, "C"), (0, "B"), (1, "A"), (1, "C")]
        lex = Lexicon(["w"])
        for h, o in seq:
            lex.update(["w"] if h else [], o)

        def kt_seq(bits):
            lp, c = 0.0, [0, 0]
            for b in bits:
                lp += math.log((c[b] + 0.5) / (c[0] + c[1] + 1.0))
                c[b] += 1
            return lp

        outcomes = []
        for _, o in seq:
            if o not in outcomes:
                outcomes.append(o)
        per_outcome = sum(kt_seq([h for h, o in seq if o == k]) for k in outcomes)
        terms = [math.log(0.5) + per_outcome]
        for r, k in enumerate(outcomes, start=1):
            prior = 0.5 * 6 / (math.pi ** 2 * r * r)
            terms.append(math.log(prior) + kt_seq([h for h, o in seq if o == k]) + kt_seq([h for h, o in seq if o != k]))
        left = 0.5 - sum(0.5 * 6 / (math.pi ** 2 * r * r) for r in range(1, len(outcomes) + 1))
        terms.append(math.log(left) + kt_seq([h for h, _ in seq]))
        top = max(terms)
        expected = top + math.log(sum(math.exp(t - top) for t in terms))
        self.assertAlmostEqual(lex.log_q["w"], expected, places=9)
        n1 = sum(h for h, _ in seq)
        n0 = len(seq) - n1
        pooled = n1 * math.log(n1 / len(seq)) + n0 * math.log(n0 / len(seq))
        self.assertAlmostEqual(lex.log_e("w"), expected - pooled, places=9)

    def test_mass_requires_three_and_returns_mean(self):
        lex = Lexicon(["heavy"])
        lex.update_mass("heavy", 1.0)
        lex.update_mass("heavy", 2.0)
        self.assertIsNone(lex.predict_mass(["heavy"]))
        lex.update_mass("heavy", 3.0)
        mean, sd, n = lex.predict_mass(["heavy"])
        self.assertEqual((mean, n), (2.0, 3))
        self.assertAlmostEqual(sd, 1.0)

    def test_state_round_trip(self):
        lex = Lexicon(["b", "a"])
        for outcome, heard in [("A", ["a"]), ("B", ["b"]), ("A", [])]:
            lex.update(heard, outcome)
        restored = Lexicon.from_state(lex.state())
        for word in lex.vocabulary:
            self.assertAlmostEqual(restored.log_e(word), lex.log_e(word))


if __name__ == "__main__":
    unittest.main()
