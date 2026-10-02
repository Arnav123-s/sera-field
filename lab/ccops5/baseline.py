"""ccops5 lab | the ordinary way, for comparison.

One neural network. All knowledge lives in its weights, trained online with
backpropagation on the same childhood. It sees the same appearances, places
and words, and gets the same number of pushes, chosen at random. It has no
library, no checking and no growing.

'baseline_parts' is the same network, also shown the parts a thing is made of
(the sum of the parts' looks and how many parts there are), as the connected
learner is. Without it, the glued-toy comparison was unfair.

'baseline_sets' is the fairer version of that: a small network reads each
part's look on its own, the results are added up (a "deep sets" network), and
the sum goes in with everything else. It can learn a hidden number for each
part and add them, which is what the glued-toy rules need. Both parts are
trained together by backpropagation.

'baseline_words' is the plain network, but for the brand-new toys of the
words-only stage it is not shown their look (all zeros, the average look), so
it can lean on the words alone, as the connected learner does when a look is
unfamiliar.

Built as an isolated experiment. Not part of sera-field.
"""
import numpy as np
import torch
from torch import nn

from . import world as W
from .mind import MAX_TRIALS, DT_MODEL, miss, samples_from


class WeightsOnly:
    SET_WIDTH = 8

    def __init__(self, seed, parts=False, blind_new=False):
        torch.manual_seed(seed)
        self.parts = parts
        self.blind_new = blind_new
        extra = {False: 0, 'sum': W.APP_DIM + 1, 'sets': self.SET_WIDTH}[parts]
        width = 3 + W.APP_DIM + len(W.SCENES) + len(W.WORDS) + extra
        self.net = nn.Sequential(nn.Linear(width, 64), nn.Tanh(), nn.Linear(64, 64), nn.Tanh(),
                                 nn.Linear(64, 1))
        weights = list(self.net.parameters())
        if parts == 'sets':
            self.each = nn.Sequential(nn.Linear(W.APP_DIM, 32), nn.Tanh(), nn.Linear(32, self.SET_WIDTH))
            weights += list(self.each.parameters())
        self.optimizer = torch.optim.Adam(weights, lr=1e-3)
        self.rng = np.random.default_rng([seed, 77])
        self.events = []
        self.laws = []

    def context(self, ep):
        scene = np.zeros(len(W.SCENES))
        scene[W.SCENES.index(ep['scene'])] = 1.0
        words = np.array([1.0 if w in ep['words'] else 0.0 for w in W.WORDS])
        look = np.zeros_like(ep['app']) if self.blind_new and ep['stage'] == W.STAGES[6] else ep['app']
        base = np.concatenate((look, scene, words))
        if not self.parts:
            return torch.from_numpy(base)
        # A single thing is one part: itself.
        parts = ep.get('parts') or [ep['app']]
        if self.parts == 'sets':
            return torch.from_numpy(base), torch.from_numpy(np.array(parts, dtype=base.dtype))
        return torch.from_numpy(np.concatenate((base, np.sum(parts, 0), [len(parts)])))

    def accel(self, z, ctx):
        if self.parts == 'sets':
            base, parts = ctx
            ctx = torch.cat((base, self.each(parts).sum(0)))
        return self.net(torch.cat((z, ctx.expand(z.shape[0], -1)), -1)).squeeze(-1)

    def imagine(self, ctx, u):
        x, v = torch.zeros(1), torch.zeros(1)
        push, rest = torch.tensor([u]), torch.zeros(1)

        def acc(x, v, c):
            return self.accel(torch.stack((x, v, c), -1), ctx).clamp(-50, 50)

        out, h, step = [x], DT_MODEL, 0
        per = int(round(W.DT_OBS / DT_MODEL))
        with torch.no_grad():
            for _ in range(W.N_OBS - 1):
                for _ in range(per):
                    c = push if step * h < W.T_PUSH - 1e-9 else rest
                    k1x, k1v = v, acc(x, v, c)
                    k2x, k2v = v + .5 * h * k1v, acc(x + .5 * h * k1x, v + .5 * h * k1v, c)
                    k3x, k3v = v + .5 * h * k2v, acc(x + .5 * h * k2x, v + .5 * h * k2v, c)
                    k4x, k4v = v + h * k3v, acc(x + h * k3x, v + h * k3v, c)
                    x = x + h / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
                    v = v + h / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
                    step += 1
                out.append(x)
        return torch.cat(out).numpy()

    def learn(self, samples, ctx, steps=60):
        z = torch.cat([s[0] for s in samples])
        a = torch.cat([s[1] for s in samples])
        for _ in range(steps):
            loss = (self.accel(z, ctx) - a).square().mean()
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

    def live(self, ep, rng_world, index):
        ctx, u_check = self.context(ep), ep['check_u']
        guess = self.imagine(ctx, u_check)
        samples, pushes = [], []
        for _ in range(MAX_TRIALS):
            u = float(self.rng.choice(W.COMMANDS))
            xs, vs = W.simulate(ep['params'], u, rng_world)
            samples.append(samples_from(xs, vs, u))
            pushes.append(u)
            self.learn(samples, ctx)
        answer = self.imagine(ctx, u_check)
        xs, vs = W.simulate(ep['params'], u_check, rng_world)
        record = {'episode': index, 'stage': ep['stage'], 'scene': ep['scene'], 'kind': ep['kind'],
                  'trick': ep['trick'], 'words': list(ep['words']), 'source': 'weights', 'pushes': pushes,
                  'miss_before': miss(guess, xs), 'miss_after': miss(answer, xs), 'laws': 0}
        if ep['stage'] == W.STAGES[6]:
            record['miss_word_guess'] = record['miss_before']
        if ep.get('parts'):
            record['parts'] = len(ep['parts'])
        self.learn(samples + [samples_from(xs, vs, u_check)], ctx)
        return record
