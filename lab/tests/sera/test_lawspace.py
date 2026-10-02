"""The law language spells exactly the families the frozen judge can certify."""
import math

import pytest

from ccops5.core import grammar
from sera import lawspace as LS


def test_every_certifiable_family_roundtrips_and_is_spellable():
    fams = LS.all_families()
    assert len(fams) == len(set(fams)) == 67 + len(grammar.OPEN_TERMS) * (1 + len(grammar.IDEAS))
    for fam in fams:
        ids = LS.encode(fam)
        assert LS.decode(ids) == fam
        assert len(ids) <= LS.MAX_LEN
        for pos, mask in enumerate(LS.allowed_masks(ids)):        # the speller allows the true spelling
            assert mask[ids[pos + 1]], (fam, pos)
        assert LS.claimable(fam) and math.isfinite(LS.description_length(fam))


def test_speller_refuses_what_the_judge_cannot_certify():
    sp = LS.Speller()
    for tok in ['PROD', 'straight', 'straight']:
        sp.push(tok)
    assert 'PROD' not in sp.allowed() and 'POW' not in sp.allowed() and 'IDEA' in sp.allowed()   # one open term
    for tok in ['IDEA', 'speed', 'straight']:
        sp.push(tok)
    assert sp.allowed() == ['<eos>']                                                              # two terms max
    sp2 = LS.Speller()
    for tok in ['IDEA', 'speed', 'straight', 'IDEA', 'speed']:
        sp2.push(tok)
    assert 'straight' not in sp2.allowed()                                                         # no term twice
    with pytest.raises(ValueError):
        LS.encode((('product', 'straight', 'straight'), ('power', 'speed', 0.5)))


def test_levels():
    assert LS.level(()) == 0
    assert LS.level((('speed', 'straight'),)) == 1
    assert LS.level((('speed', 'straight'), ('position', 'straight'))) == 2
    assert LS.level((('power', 'speed', 0.3),)) == 3
    assert LS.level((('drive', 'sin', 2.5), ('position', 'straight'))) == 4
