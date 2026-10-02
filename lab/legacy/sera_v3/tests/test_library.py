"""The library: append-only hash chain, e-LOND admission, empty-slot predictions from its own pattern."""
import math
import types

from ccops5.core import grammar
from legacy.sera_v3 import lawspace as LS, library as LB


def _cert(log_e, fam):
    return types.SimpleNamespace(rivals={('x',): log_e}, log_prior=grammar.log_prior(fam), digest='d' * 8)


def test_chain_and_admission():
    lib = LB.Library()
    strong = (('product', 'cubic', 'straight'),)
    lib.new_world()
    assert lib.offer(strong, _cert(60.0, strong), 1)
    weak = (('product', 'straight', 'steps'),)
    lib.new_world()
    assert not lib.offer(weak, _cert(1.0, weak), 2)                 # too little evidence for the library
    lib.new_world()
    assert lib.offer(weak, _cert(60.0, weak), 3)
    before = lib.alpha_now()
    for _ in range(10):                                             # unsure worlds still count as tests
        lib.new_world()
    assert lib.alpha_now() < before
    assert lib.verify_chain()
    lib.entries[0]['world'] = 99                                    # tampering breaks the chain
    assert not lib.verify_chain()


def test_empty_slots_come_from_the_pattern():
    lib = LB.Library()
    for fam in [(('product', 'cubic', 'straight'),), (('product', 'straight', 'steps'),), (('power', 'speed', 0.4),)]:
        lib.new_world()
        assert lib.offer(fam, _cert(80.0, fam), 0)
    slots = lib.empty_slots()
    assert (('product', 'cubic', 'steps'),) in slots                 # row of one, column of the other
    assert (('power', 'speed', 0.3),) in slots and (('power', 'position', 0.4),) in slots
    assert all(LS.claimable(s) and s not in lib.met for s in slots)
