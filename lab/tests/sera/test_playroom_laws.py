"""T4b world validation (docs/SERA_PLAYROOM.md v0.1 §1, independent review L1): every room law lies in the Field's law set."""
import numpy as np

from ccops5.core import grammar, playroom as R
from sera import field as F


def test_every_room_law_is_a_field_law():
    laws = set(F.LAWS)
    for regime in R.REGIMES:
        terms, _ = R.regime_law(regime, np.random.default_rng(0))
        assert grammar.canonical(terms) in laws, regime
