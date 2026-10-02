"""B5 lives survive crashes (the laptop crashed twice on 2026-09-24): a life resumed from its checkpoint equals an
uninterrupted one - the same wake and evaluation records, the same imagination weights afterwards. The worlds and the
mind are replaced by fast stand-ins whose results depend on the imagination's weights, so any state the checkpoint
failed to carry (weights, optimizer, learner memory or sampler, random streams) changes the records."""
import os
import types

import numpy as np
import pytest
import torch

from ccops5.core import grammar
from legacy.sera_v3 import compact as C, generations as GN, school as SC, worlds as SW

MODEL = os.path.join(os.environ.get('SERA_RUNS', 'D:/ai/labs/ccops5-sera-lab/sera-runs'), 'imagine-v1', 'model.pt')


class _Crash(Exception):
    pass


class _SmallLearner(SC.Learner):
    def __init__(self, model, dreams_set, lr=5e-4, steps=30, rehearse=64, seed=0):
        self.model, self.steps, self.rehearse = model, 3, 8
        self.opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
        g = torch.Generator().manual_seed(0)
        self.dF = torch.randn(64, len(C.TERMS), 8, generator=g)
        self.dW = torch.randn(64, 7, generator=g)
        self.dY = torch.randint(0, 50, (64,), generator=g)
        self.F, self.W, self.Y = [], [], []
        self.rng = np.random.default_rng(seed)


class _SmallLadder(SC.LadderLearner):
    def __init__(self, model, dreams_set, **kw):
        _SmallLearner.__init__(self, model, dreams_set, **kw)
        self.grades = []


def _stand_ins(monkeypatch, crash_at=None):
    calls = {'n': 0}
    fams = [grammar.canonical((i,)) for i in grammar.IDEAS]

    def make(seed, idx, lv, sp):
        fam = fams[(idx * 7 + lv) % len(fams)]
        return types.SimpleNamespace(spec=types.SimpleNamespace(family=fam, level=lv), throws=idx, sigma=(1e-3, 1e-3))

    def compact(throws):
        r = np.random.default_rng(throws)
        return r.normal(size=(len(C.TERMS), 8)).astype(np.float32), r.normal(size=7).astype(np.float32), None

    def run_world(model, w, eps=0.2, design=False):
        calls['n'] += 1
        if calls['n'] == crash_at:
            raise _Crash
        s = float(sum(p.detach().double().sum() for p in model.parameters()))
        right = bool(int(abs(s) * 1e4) % 3 == 0)
        other = fams[(fams.index(w.spec.family) + 1) % len(fams)]
        led = types.SimpleNamespace(families=[w.spec.family, other], Q={w.spec.family: 0.0, other: -3.0 - s % 1})
        cert = types.SimpleNamespace(family=w.spec.family, accepted=False, alpha=1e-3)
        return (types.SimpleNamespace(claim=w.spec.family, certificate=cert, ledger=led, alarm=False, q_start=None),
                dict(level=w.spec.level, truth=grammar.name(w.spec.family), claim=grammar.name(w.spec.family),
                     sure=False, verified=False, right=right, wrong=False, sure_unverified=False, throws=round(s, 9),
                     own=0, cpu=0.0))

    monkeypatch.setattr(GN, 'suite', lambda seed, per=4: [('L1', 1, 'dream', 30_000 + i) for i in range(4)])
    monkeypatch.setattr(SW, 'make', make)
    monkeypatch.setattr(C, 'compact', compact)
    monkeypatch.setattr(GN, 'run_world', run_world)
    monkeypatch.setattr(GN, 'imagination_metrics', lambda model, worlds: dict(
        top1=0.0, top16=0.0, p_true=float(sum(p.detach().double().sum() for p in model.parameters()))))
    monkeypatch.setattr(SC, 'Learner', _SmallLearner)
    monkeypatch.setattr(SC, 'LadderLearner', _SmallLadder)


def _strip(life):
    for g in life['generations']:
        g.pop('wake_cpu', None)
        g.pop('sleep_cpu', None)
    return life


@pytest.mark.parametrize('crash_at', [5, 7, 12])        # in a wake, in an evaluation, in the last evaluation
def test_a_resumed_life_equals_an_uninterrupted_one(monkeypatch, tmp_path, crash_at):
    kw = dict(generations=2, wake=3, progress=lambda row: None)
    _stand_ins(monkeypatch)
    whole = _strip(GN.live(1, 'full', MODEL, **kw))
    ckpt = tmp_path / 'life.ckpt'
    _stand_ins(monkeypatch, crash_at=crash_at)
    with pytest.raises(_Crash):
        GN.live(1, 'full', MODEL, checkpoint=ckpt, **kw)
    assert ckpt.exists()
    _stand_ins(monkeypatch)
    resumed = _strip(GN.live(1, 'full', MODEL, checkpoint=ckpt, **kw))
    assert resumed == whole


def test_a_resumed_ladder_life_equals_an_uninterrupted_one(monkeypatch, tmp_path):
    """The ladder arm (plan revision 2, P4) carries its graded memory through a crash too."""
    kw = dict(generations=2, wake=3, progress=lambda row: None)
    _stand_ins(monkeypatch)
    whole = _strip(GN.live(1, 'ladder', MODEL, **kw))
    ckpt = tmp_path / 'life.ckpt'
    _stand_ins(monkeypatch, crash_at=9)
    with pytest.raises(_Crash):
        GN.live(1, 'ladder', MODEL, checkpoint=ckpt, **kw)
    _stand_ins(monkeypatch)
    assert _strip(GN.live(1, 'ladder', MODEL, checkpoint=ckpt, **kw)) == whole
