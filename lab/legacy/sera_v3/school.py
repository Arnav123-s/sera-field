"""SERA's school (B3): learning a new kind of law from a few worlds, with a caretaker at first, then alone.

A life is a sequence of worlds whose law structures were never dreamed (sera.worlds held-out split), plus a few of
dreamed kinds so forgetting would show. After each world the imagination may learn from one labelled example:
  - taught arm:   in the taught phase the caretaker says which law was right (the true law, i.e. which of its
                  imaginations was right, or none of them); afterwards only laws the checker verified;
  - verified arm: only laws the independent checker verified (its own discoveries), from the start;
  - frozen arm:   never learns (the control).
Learning = a few gradient steps on everything learned so far in this life, mixed with rehearsed dreams so old
knowledge is kept. It is cheap (about a second on one CPU thread) and it changes behaviour: the imagination decides
which invented terms enter the judge's ledger and which experiments are made (sera.mind).

Per world the log records: phase, level, split, truth, claim, sure, verified, right, throws, own pushes, the true
law's rank among the imagination's proposals at the start (None if not among them), its probability, seconds.
"""
import glob
import os
import time

import numpy as np
import torch

from ccops5.core import checker, grammar

import core_check
from . import compact as C, dreams as D, imagine as I, mind as SM, worlds as SW

ARMS = {'taught': dict(learn=True, teacher=True), 'verified': dict(learn=True, teacher=False),
        'frozen': dict(learn=False, teacher=False)}


def plan(seed, n_taught=10, n_alone=10):
    """(phase, level, split, index): held-out invented-term laws (L3, L4), with one dreamed-kind world in five."""
    rng = np.random.default_rng([seed, 515])
    out = []
    for n in range(n_taught + n_alone):
        phase = 'taught' if n < n_taught else 'alone'
        if n % 5 == 4:
            out.append((phase, int(rng.choice([1, 2])), 'dream', 20_000 + n))
        else:
            out.append((phase, int(rng.choice([3, 4])), 'held', 20_000 + n))
    return out


RUNS = os.environ.get('SERA_RUNS', 'D:/ai/labs/ccops5-sera-lab/sera-runs')   # SERA_RUNS: another machine (Colab)


class Learner:
    """Few-shot updates of the imagination, with dream rehearsal against forgetting."""

    def __init__(self, model, dreams_set, lr=5e-4, steps=30, rehearse=64, seed=0):
        self.model, self.steps, self.rehearse = model, steps, rehearse
        self.opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
        files = sorted(glob.glob(f'{RUNS}/{dreams_set}/shard-*.npz'))[-5:]
        z = [np.load(f) for f in files]
        self.dF = torch.tensor(np.concatenate([a['features'] for a in z]), dtype=torch.float32)
        self.dW = torch.tensor(np.concatenate([a['world'] for a in z]))
        self.dY = torch.tensor(np.concatenate([a['label'] for a in z]), dtype=torch.long)
        self.F, self.W, self.Y = [], [], []
        self.rng = np.random.default_rng(seed)

    def add(self, feats, world, family):
        self.F.append(torch.tensor(feats, dtype=torch.float32))
        self.W.append(torch.tensor(world))
        self.Y.append(D.FAMILY_INDEX[grammar.canonical(family)])

    def train(self, steps):
        """Gradient steps on everything learned so far in this life, each batch mixed with rehearsed dreams."""
        if not self.Y:
            return
        self.model.train()
        for _ in range(steps):
            idx = torch.tensor(self.rng.choice(len(self.dY), size=self.rehearse, replace=False))
            Fb = torch.cat([torch.stack(self.F), self.dF[idx]])
            Wb = torch.cat([torch.stack(self.W), self.dW[idx]])
            Yb = torch.cat([torch.tensor(self.Y), self.dY[idx]])
            loss = I.loss(self.model, Fb, Wb, Yb)
            self.opt.zero_grad(set_to_none=True)
            loss.backward()
            self.opt.step()
        self.model.eval()

    def learn(self, feats, world, family):
        self.add(feats, world, family)
        self.train(self.steps)


class LadderLearner(Learner):
    """v3.1 (plan revision 2): learns from every graded imagination of a world (sera.grade: the credit ladder), not
    only from the one law a world proved; dream rehearsal against forgetting as before."""

    def __init__(self, model, dreams_set, **kw):
        super().__init__(model, dreams_set, **kw)
        self.grades = []                      # (features, world vector, Grade)

    def learn_graded(self, feats, world, grade):
        from . import grade as G  # noqa: F401  (the Grade type)
        self.grades.append((torch.tensor(feats, dtype=torch.float32), torch.tensor(world), grade))
        self.train(self.steps)

    def train(self, steps):
        from . import grade as G
        if not self.grades:
            return super().train(steps)
        self.model.train()
        Fg = torch.stack([f for f, _, _ in self.grades])
        Wg = torch.stack([w for _, w, _ in self.grades])
        gs = [g for _, _, g in self.grades]
        for _ in range(steps):
            idx = torch.tensor(self.rng.choice(len(self.dY), size=self.rehearse, replace=False))
            loss = I.loss(self.model, self.dF[idx], self.dW[idx], self.dY[idx]) + G.loss(self.model, Fg, Wg, gs)
            self.opt.zero_grad(set_to_none=True)
            loss.backward()
            self.opt.step()
        self.model.eval()


def live_life(seed, arm, model_path, dreams_set='dreams-v1', n_taught=10, n_alone=10, eps=0.2, progress=None):
    torch.set_num_threads(1)
    torch.manual_seed(seed)
    model = I.Imagination()
    model.load_state_dict(torch.load(model_path, map_location='cpu'))
    model.eval()
    cfg = ARMS[arm]
    learner = Learner(model, dreams_set, seed=seed) if cfg['learn'] else None
    log = []
    for n, (phase, level, split, index) in enumerate(plan(seed, n_taught, n_alone)):
        t0 = time.perf_counter()
        w = SW.make(seed, index, level, split)
        truth = grammar.canonical(w.spec.family)
        feats, wv, _ = C.compact(w.throws)
        props = I.propose(model, feats[None].astype(np.float32), wv[None], K=16)[0]
        fams = [f for f, _ in props]
        rank = fams.index(truth) + 1 if truth in fams else None
        r = SM.Mind(model, w.sigma, eps=eps, budget=3 * w.n_situations).live(w)
        verified = bool(r.sure and checker.check(r.certificate, r.ledger.throws, w.sigma)[0])
        claim = grammar.canonical(r.claim)
        label = None
        if cfg['learn']:
            if cfg['teacher'] and phase == 'taught':
                label = truth                                    # the caretaker: "this one was right"
            elif verified:
                label = claim                                    # its own checked discovery
        if label is not None:
            learner.learn(feats, wv, label)
        row = dict(n=n, phase=phase, level=level, split=split, truth=grammar.name(truth), claim=grammar.name(claim),
                   sure=r.sure, verified=verified, right=bool(verified and claim == truth),
                   wrong=bool(r.sure and core_check.wrong(r.certificate, w)),          # the frozen definition
                   sure_unverified=bool(r.sure and not verified),
                   throws=r.throws, own=r.own_pushes, rank=rank, p_true=round(dict(props).get(truth, 0.0), 4),
                   learned=None if label is None else grammar.name(label),
                   learned_true=None if label is None else bool(label == truth), seconds=round(time.perf_counter() - t0, 1))
        log.append(row)
        if progress:
            progress(row)
    return dict(seed=seed, arm=arm, worlds=log)
