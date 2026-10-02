"""ccops5 lab | the ball-throw robot: it finds each place's laws by evidence, then earns the idea
that one hidden number per ball (its mass) explains how every place treats it.

What it sees: positions every 0.05 s, a ball's visible size and look, and the speed a known push
gives the ball on a rail. From the rail it gets a "push number" q = push / speed. It never reads a
ball's mass.

1. Laws of a place. Its ideas are sets of terms: a steady pull down, a steady push sideways,
   drag ∝ v, drag ∝ |v|·v, each in still or in moving air (the air's speed is fitted). Each ball
   gets its own numbers. Ideas are weighed by re-trial: each throw is predicted from the ball's
   other throws, and the evidence for A over B is the sum over throws of the difference in leftover
   (in noise units), at most 6 per throw; 9 is decisive. It keeps the simplest idea that is not
   decisively beaten. It is sure only when every other idea is decisively beaten, except bigger
   ideas (its idea plus extra parts, such as moving air) that do not predict new throws better by
   at least 1: a bigger idea that does is a hint, and stays open. While a rival stays open it
   throws a ball itself, where its idea and the rival would part most; a bigger rival is tried at
   the strongest version the data still allow (for moving air, the fastest wind not yet ruled
   out). If even that version could not be seen on any throw, the extra parts add nothing. It
   states the range of wind speeds it cannot rule out, so "still air" is a claim with a bound.
   (Version 2. Version 1 closed a bigger idea unless it was decisively better, and so was sure of
   still air while moving air predicted better by 7 and 8: fresh seeds 14 and 17.)
2. The concept. A ball's number for a term in a place might be:
     R0  anything (no sharing): a ball new to a place gets that place's average;
     Rs  a + C·size^k (size only);
     R1  a + C·size^k / q (the push number: mass), k in 0..3 chosen by fit;
     R2  R1 plus a second hidden number per ball, fitted.
   They are weighed by predicting each (ball, place) from all the others, in units of each
   number's own uncertainty. It keeps the concept only if R1 beats R0 and Rs decisively and R2
   does not beat R1.
3. Galileo. In the vacuum room: one shared pull for every ball, against a pull for each ball,
   weighed by re-trial in the same way.

Built as an isolated experiment. Not part of sera-field.
"""
import itertools
import math

import numpy as np
import torch
from torch import nn

from .ballworld import DT_OBS, DT_SIM, N_BALLS, N_OBS, PLACES, PUSH, SIGMA_POS, TRAINING

SIGMA_A = math.sqrt(6) * SIGMA_POS / DT_OBS ** 2     # noise of an acceleration worked out from positions
SURPRISE = 1.8
DECISIVE = 9.0
ONE_THROW = 6.0
WORTH = 1.0                  # the least evidence that counts: a throw must add this, and so must a hint
OWN_THROWS = 6
TERMS = ('down', 'side', 'drag1', 'drag2')
KS = (0, 1, 2, 3)
WIND_GRID = np.linspace(-6.0, 6.0, 61)
IDEAS = ([(ts, False) for n in range(1, 5) for ts in itertools.combinations(TERMS, n)]
         + [(ts, True) for n in range(1, 5) for ts in itertools.combinations(TERMS, n)
            if 'drag1' in ts or 'drag2' in ts])
TRUTH = {'vacuum': (('down',), False), 'air': (('down', 'drag2'), False),
         'windy': (('down', 'drag2'), True), 'water': (('down', 'drag2'), False),
         'moon': (('down',), False)}


# ---------- seeing a throw ----------

def kinematics(xs, ys):
    """Speeds and accelerations from positions, by central differences."""
    v = np.stack((xs[2:] - xs[:-2], ys[2:] - ys[:-2]), 1) / (2 * DT_OBS)
    a = np.stack((xs[2:] - 2 * xs[1:-1] + xs[:-2], ys[2:] - 2 * ys[1:-1] + ys[:-2]), 1) / DT_OBS ** 2
    return v, a


def features(idea, v, w):
    """For each sample, the push of each term (x and y) per unit of its number."""
    terms, moving = idea
    r = v - np.array([w if moving else 0.0, 0.0])
    speed = np.hypot(r[:, 0], r[:, 1])[:, None]
    cols = {'down': np.tile([0.0, -1.0], (len(v), 1)), 'side': np.tile([1.0, 0.0], (len(v), 1)),
            'drag1': -r, 'drag2': -speed * r}
    return np.stack([cols[t] for t in terms], -1)


def fit(idea, throws, w):
    """One ball's numbers for an idea: least squares on its throws, with their uncertainty."""
    A = np.vstack([features(idea, v, w).reshape(-1, len(idea[0])) for v, _ in throws])
    b = np.concatenate([a.reshape(-1) for _, a in throws])
    c = np.linalg.lstsq(A, b, rcond=None)[0]
    left = b - A @ c
    se = SIGMA_A * np.sqrt(np.clip(np.diag(np.linalg.pinv(A.T @ A)), 0, None))
    return c, float(left @ left), se


def leftover(idea, c, throw, w):
    v, a = throw
    d = a - features(idea, v, w) @ c
    return float((d * d).sum())


def halves(throw):
    v, a = throw
    n = len(v) // 2
    return [(v[:n], a[:n]), (v[n:], a[n:])]


def units(throws):
    """The pieces used for re-trial: whole throws, or the two halves of a single throw."""
    return throws if len(throws) >= 2 else halves(throws[0])


def best_wind(idea, data):
    if not idea[1]:
        return 0.0
    return float(min(WIND_GRID, key=lambda w: sum(fit(idea, t, w)[1] for t in data.values())))


def retrial(idea, data, w):
    """Each throw predicted from the same ball's other throws: leftover in noise units."""
    out = []
    for ball in sorted(data):
        pieces = units(data[ball])
        for j in range(len(pieces)):
            c = fit(idea, pieces[:j] + pieces[j + 1:], w)[0]
            out.append(leftover(idea, c, pieces[j], w) / SIGMA_A ** 2)
    return np.array(out)


def wind_scan(idea, data):
    """The winds a moving-air version of this idea cannot rule out, by re-trial at each wind on the grid:
    the extreme winds not decisively beaten by the best one, then the first beaten wind beyond each side
    (the range it states, so the true wind lies inside it)."""
    moving = (idea[0], True)
    prof = [retrial(moving, data, w) for w in WIND_GRID]
    best = min(range(len(WIND_GRID)), key=lambda i: prof[i].sum())
    ok = [i for i, p in enumerate(prof) if float(np.clip(p - prof[best], -ONE_THROW, ONE_THROW).sum()) < DECISIVE]
    lo, hi = min(ok), max(ok)
    return (float(WIND_GRID[lo]), float(WIND_GRID[hi]),
            float(WIND_GRID[max(lo - 1, 0)]), float(WIND_GRID[min(hi + 1, len(WIND_GRID) - 1)]))


def complexity(idea):
    return len(idea[0]) + idea[1]


def covers(big, small):
    return set(small[0]) <= set(big[0]) and big[1] >= small[1]


def judge(data):
    """Weigh every idea on this place's throws. Returns the kept idea, the open rivals and the
    evidence function."""
    scores = {}
    for idea in IDEAS:
        w = best_wind(idea, data)
        scores[idea] = (w, retrial(idea, data, w))

    def ev(a, b):
        """Evidence for idea a over idea b."""
        return float(np.clip(scores[b][1] - scores[a][1], -ONE_THROW, ONE_THROW).sum())

    best = min(IDEAS, key=lambda i: scores[i][1].sum())
    fine = [i for i in IDEAS if ev(best, i) < DECISIVE]
    kept = min(fine, key=lambda i: (complexity(i), scores[i][1].sum()))
    # A bigger idea (kept plus extra parts) that predicts new throws better by at least WORTH is a hint
    # of something extra, so it stays open until it is settled.
    open_ = [r for r in IDEAS if r != kept and ev(kept, r) < DECISIVE
             and not (covers(r, kept) and ev(r, kept) < WORTH)]
    return kept, scores, open_, ev


# ---------- imagining a throw ----------

def accel_fn(idea, c, w):
    terms, moving = idea
    k = dict(zip(terms, (float(x) for x in c)))
    wx = w if moving else 0.0
    down, side, d1, d2 = k.get('down', 0.0), k.get('side', 0.0), k.get('drag1', 0.0), k.get('drag2', 0.0)

    def acc(vx, vy):
        rx = vx - wx
        s = math.hypot(rx, vy)
        return side - d1 * rx - d2 * s * rx, -down - d1 * vy - d2 * s * vy
    return acc


def rollout(acc, speed, angle):
    """Where a throw goes if acc is the law: positions every DT_OBS (RK4 at DT_SIM)."""
    x = y = 0.0
    vx, vy = speed * math.cos(angle), speed * math.sin(angle)
    xs, ys = [x], [y]
    h, per = DT_SIM, int(round(DT_OBS / DT_SIM))
    for _ in range(N_OBS - 1):
        for _ in range(per):
            k1vx, k1vy = acc(vx, vy)
            k2x, k2y = vx + .5 * h * k1vx, vy + .5 * h * k1vy
            k2vx, k2vy = acc(k2x, k2y)
            k3x, k3y = vx + .5 * h * k2vx, vy + .5 * h * k2vy
            k3vx, k3vy = acc(k3x, k3y)
            k4x, k4y = vx + h * k3vx, vy + h * k3vy
            k4vx, k4vy = acc(k4x, k4y)
            x += h / 6 * (vx + 2 * k2x + 2 * k3x + k4x)
            y += h / 6 * (vy + 2 * k2y + 2 * k3y + k4y)
            vx += h / 6 * (k1vx + 2 * k2vx + 2 * k3vx + k4vx)
            vy += h / 6 * (k1vy + 2 * k2vy + 2 * k3vy + k4vy)
        xs.append(x)
        ys.append(y)
    return np.array(xs), np.array(ys)


def landing(xs, ys):
    """Where a throw comes back down to its starting height (None if it does not)."""
    for i in range(2, len(ys)):
        if ys[i] < 0 <= ys[i - 1]:
            return float(xs[i - 1] + (xs[i] - xs[i - 1]) * ys[i - 1] / (ys[i - 1] - ys[i]))
    return None


def speed_for(predict, target, angle):
    """The speed at this angle that it expects to land on the target (bisection)."""
    lo, hi = 0.5, 15.0
    for _ in range(25):
        mid = (lo + hi) / 2
        land = landing(*predict(mid, angle))
        if land is None or land > target:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def miss(xs, ys, true_xs, true_ys):
    """Typical distance between where it guessed the ball would be and where it was (metres)."""
    return float(np.sqrt(np.mean((xs - true_xs) ** 2 + (ys - true_ys) ** 2)))


# ---------- weighted fits for the concept ----------

def wls(X, y, wt):
    sw = np.sqrt(wt)
    beta = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)[0]
    return beta


def power(s, k):
    return s ** k


class Mind:
    """The loop robot. kind 'concept' forms the concept; kind 'per_place' never shares numbers
    between places (R0 only)."""

    def __init__(self, kind, balls, seed):
        self.kind, self.seed = kind, seed
        self.balls = {b['id']: {'seen_size': b['seen_size'], 'q': PUSH / b['rail_speed']} for b in balls}
        self.data = {p: {} for p in PLACES}
        self.laws = {}
        self.concept = None
        self.galileo = None

    def see(self, place, ball, xs, ys):
        self.data[place].setdefault(ball, []).append(kinematics(xs, ys))

    # ----- laws of a place -----

    def learn_place(self, place, throw=None, allowed=(), budget=OWN_THROWS):
        own, stuck, closed = 0, False, set()
        kept, scores, open_, ev = judge(self.data[place])
        while throw is not None and own < budget:
            live = [r for r in open_ if r not in closed]
            if not live:
                break
            rival = min(live, key=lambda r: ev(kept, r))
            bigger = covers(rival, kept)
            choice = (self.edge_throw(place, kept, scores, rival, allowed) if bigger else
                      self.best_throw(place, kept, scores[kept][0], rival, scores[rival][0], allowed)[0])
            if choice is None:
                if bigger:          # even its strongest version could not be seen on any throw: it adds nothing
                    closed.add(rival)
                    continue
                stuck = True
                break
            ball, speed, angle = choice
            self.see(place, ball, *throw(ball, speed, angle, own))
            own += 1
            kept, scores, open_, ev = judge(self.data[place])
            closed = set()
        if throw is not None:       # the same test when its throws are used up: invisible even at its strongest
            closed |= {r for r in open_ if r not in closed and covers(r, kept)
                       and self.edge_throw(place, kept, scores, r, allowed) is None}
        open_ = [r for r in open_ if r not in closed]
        w = scores[kept][0]
        bigger = [r for r in IDEAS if r != kept and covers(r, kept)]
        lean = max(bigger, key=lambda r: ev(r, kept)) if bigger else None
        self.laws[place] = {
            'idea': kept, 'w': w, 'sure': not open_, 'own_throws': own, 'stuck': stuck,
            'wind_range': (wind_scan(kept, self.data[place])[2:]
                           if any(t in ('drag1', 'drag2') for t in kept[0]) else None),
            'lean': (describe(lean), ev(lean, kept)) if lean else None,
            'open': [describe(r) for r in sorted(open_, key=lambda r: ev(kept, r))[:3]],
            'beaten': [describe(r) for r in IDEAS if r != kept and ev(kept, r) >= DECISIVE],
            'numbers': {b: fit(kept, t, w) for b, t in self.data[place].items()}}
        if place == 'vacuum':
            self.galileo = self.weigh_galileo()

    def edge_throw(self, place, kept, scores, rival, allowed):
        """For a bigger rival: the throw where its strongest version the data still allow would part most
        from its idea, or None if no throw would add WORTH. When the rival adds moving air to still air,
        both ends of the winds not yet ruled out are tried, since a throw may show a head wind more than a
        tail wind."""
        winds = [scores[rival][0]]
        if rival[1] and not kept[1]:
            lo, hi, _, _ = wind_scan(rival, self.data[place])
            winds = [w for w in (lo, hi) if w != 0.0] or winds
        tries = [self.best_throw(place, kept, scores[kept][0], rival, w, allowed, edge=True) for w in winds]
        return max(tries, key=lambda t: t[1])[0]

    def best_throw(self, place, kept, w_k, rival, w_r, allowed, edge=False):
        """The throw where its idea and the rival would part most, imagined with its idea, and what it is
        expected to add (None if no throw would add WORTH). With edge, the rival is a bigger idea taken
        at its strongest version the data still allow: each extra number moved 3 standard errors further
        from zero than its best fit (its wind is chosen by the caller)."""
        speeds = (1.0, 2.0, 3.0, 4.0) if place == 'water' else (2.0, 4.0, 6.0, 8.0)
        best, gain_best = None, WORTH          # a throw must be expected to add at least WORTH
        for ball in allowed:
            if ball not in self.data[place]:
                continue
            c_k = fit(kept, self.data[place][ball], w_k)[0]
            c_r, _, se_r = fit(rival, self.data[place][ball], w_r)
            if edge:
                c_r = np.array([c + math.sqrt(DECISIVE) * s * (1.0 if c >= 0 else -1.0) if t not in kept[0] else c
                                for t, c, s in zip(rival[0], c_r, se_r)])
            for speed in speeds:
                for angle in (0.3, 0.8, 1.3):
                    xs, ys = rollout(accel_fn(kept, c_k, w_k), speed, angle)
                    v, _ = kinematics(xs, ys)
                    d = features(kept, v, w_k) @ c_k - features(rival, v, w_r) @ c_r
                    gain = float((d * d).sum()) / SIGMA_A ** 2
                    if gain > gain_best:
                        best, gain_best = (ball, speed, angle), gain
        return best, gain_best

    def weigh_galileo(self):
        """One shared pull for every ball, against a pull for each ball, by re-trial."""
        idea, w = self.laws['vacuum']['idea'], self.laws['vacuum']['w']
        data = self.data['vacuum']
        per_ball, shared, differ = [], [], 0.0
        for ball in sorted(data):
            pieces = units(data[ball])
            for j in range(len(pieces)):
                own = fit(idea, pieces[:j] + pieces[j + 1:], w)[0]
                others = pieces[:j] + pieces[j + 1:] + [t for b, ts in data.items() if b != ball for t in ts]
                common = fit(idea, others, w)[0]
                per_ball.append(leftover(idea, own, pieces[j], w) / SIGMA_A ** 2)
                shared.append(leftover(idea, common, pieces[j], w) / SIGMA_A ** 2)
                differ = max(differ, float(np.abs(own - common).max()))
        per_ball, shared = np.array(per_ball), np.array(shared)
        for_shared = float(np.clip(per_ball - shared, -ONE_THROW, ONE_THROW).sum())
        pulls = {b: float(fit(idea, t, w)[0][idea[0].index('down')]) for b, t in data.items()} \
            if 'down' in idea[0] else {}
        qs = [self.balls[b]['q'] for b in pulls]
        corr = float(np.corrcoef(list(pulls.values()), qs)[0, 1]) if len(pulls) > 2 else None
        return {'for_shared': for_shared, 'same': for_shared > -DECISIVE, 'pulls': pulls,
                'spread': float(np.std(list(pulls.values()))) if pulls else None, 'corr_with_q': corr,
                'models_differ_by': differ, 'throws_per_ball': min(len(t) for t in data.values())}

    # ----- the concept -----

    def entries(self, skip=None):
        """Every (place, term, ball, number, uncertainty) it has, except one (ball, place)."""
        out = []
        for place in TRAINING:
            law = self.laws[place]
            for ball, (c, _, se) in law['numbers'].items():
                if (ball, place) == skip:
                    continue
                for t, ci, si in zip(law['idea'][0], c, se):
                    out.append(((place, t), ball, float(ci), max(float(si), 1e-6)))
        return out

    def x_of(self, model, ball, k):
        s, q = self.balls[ball]['seen_size'], self.balls[ball]['q']
        return power(s, k) if model == 'Rs' else power(s, k) / q

    def fit_groups(self, entries, model):
        """For each (place, term): the fitted rule and, for R1/Rs, the chosen k."""
        groups = {}
        for g, b, c, se in entries:
            groups.setdefault(g, []).append((b, c, se))
        rules = {}
        for g, rows in groups.items():
            y = np.array([c for _, c, _ in rows])
            wt = np.array([1 / se ** 2 for _, _, se in rows])
            if model == 'R0' or len(rows) < 3:
                rules[g] = ('R0', float(np.sum(wt * y) / np.sum(wt)))
                continue
            best = None
            for k in (KS if model == 'R1' else KS[1:]):
                X = np.column_stack([np.ones(len(rows)), [self.x_of(model, b, k) for b, _, _ in rows]])
                # k is chosen by re-trial too: each ball predicted from the others.
                held = 0.0
                for i in range(len(rows)):
                    keep = np.arange(len(rows)) != i
                    held += float(wt[i] * (y[i] - X[i] @ wls(X[keep], y[keep], wt[keep])) ** 2)
                if best is None or held < best[0]:
                    beta = wls(X, y, wt)
                    cov = np.linalg.pinv((X * wt[:, None]).T @ X)
                    best = (held, k, beta, float(np.sqrt(max(cov[1, 1], 0))))
            rules[g] = (model, best[1], best[2], best[3])
        return rules

    def predict_rule(self, rule, ball):
        if rule[0] == 'R0':
            return rule[1]
        _, k, beta, _ = rule
        return float(beta[0] + beta[1] * self.x_of(rule[0], ball, k))

    def fit_r2(self, entries, r1, fold):
        """R1 plus a second hidden number per ball, by alternating least squares (5 restarts)."""
        rng = np.random.default_rng([self.seed, 77, fold])
        balls = sorted({b for _, b, _, _ in entries})
        groups = sorted({g for g, _, _, _ in entries})
        rows = {g: [(b, c, se) for gg, b, c, se in entries if gg == g] for g in groups}
        xk = {g: (lambda b, g=g: self.x_of('R1', b, r1[g][1]) if r1[g][0] == 'R1' else 0.0) for g in groups}
        best = None
        for _ in range(5):
            h = {b: float(rng.normal()) for b in balls}
            for _ in range(40):
                beta = {}
                for g in groups:
                    X = np.array([[1.0, xk[g](b), h[b]] for b, _, _ in rows[g]])
                    y = np.array([c for _, c, _ in rows[g]])
                    wt = np.array([1 / se ** 2 for _, _, se in rows[g]])
                    beta[g] = wls(X if len(y) >= 4 else X[:, :2], y, wt)
                    if len(beta[g]) == 2:
                        beta[g] = np.append(beta[g], 0.0)
                for b in balls:
                    num = den = 0.0
                    for g in groups:
                        for bb, c, se in rows[g]:
                            if bb == b:
                                wt = 1 / se ** 2
                                num += wt * beta[g][2] * (c - beta[g][0] - beta[g][1] * xk[g](b))
                                den += wt * beta[g][2] ** 2
                    if den > 1e-12:
                        h[b] = num / den
                vals = np.array(list(h.values()))
                sd = float(vals.std()) or 1.0
                h = {b: (v - vals.mean()) / sd for b, v in h.items()}
            loss = sum((c - beta[g][0] - beta[g][1] * xk[g](b) - beta[g][2] * h[b]) ** 2 / se ** 2
                       for g in groups for b, c, se in rows[g])
            if best is None or loss < best[0]:
                best = (loss, beta, dict(h), xk)
        return best

    def form_concept(self):
        """Weigh R0, Rs, R1 and R2 by predicting each (ball, place) from all the others."""
        pairs = sorted({(b, p) for p in TRAINING for b in self.laws[p]['numbers']})
        err = {m: [] for m in ('R0', 'Rs', 'R1', 'R2')}
        for fold, (ball, place) in enumerate(pairs):
            train = self.entries(skip=(ball, place))
            test = [e for e in self.entries() if e[1] == ball and e[0][0] == place]
            rules = {m: self.fit_groups(train, m) for m in ('R0', 'Rs', 'R1')}
            _, beta, h, xk = self.fit_r2(train, rules['R1'], fold)
            for m in err:
                total = 0.0
                for g, b, c, se in test:
                    if m == 'R2':
                        pred = beta[g][0] + beta[g][1] * xk[g](b) + beta[g][2] * h.get(b, 0.0) if g in beta else c
                    else:
                        pred = self.predict_rule(rules[m][g], b) if g in rules[m] else c
                    total += ((c - pred) / se) ** 2
                err[m].append(total)
        err = {m: np.array(v) for m, v in err.items()}

        def ev(a, b):
            return float(np.clip(err[b] - err[a], -ONE_THROW, ONE_THROW).sum())
        final = self.fit_groups(self.entries(), 'R1')
        kept = ev('R1', 'R0') >= DECISIVE and ev('R1', 'Rs') >= DECISIVE and ev('R2', 'R1') < DECISIVE
        # It predicts with the simplest way of sharing that is not decisively beaten by the best.
        order = ('R0', 'Rs', 'R1', 'R2')
        best = min(order, key=lambda m: err[m].sum())
        winner = next(m for m in order if ev(best, m) < DECISIVE)
        self.concept = {'kept': kept, 'winner': winner, 'R1_over_R0': ev('R1', 'R0'), 'R1_over_Rs': ev('R1', 'Rs'),
                        'R2_over_R1': ev('R2', 'R1'), 'pairs': len(pairs), 'rules': final,
                        'model': (final if winner == 'R1' else
                                  self.fit_r2(self.entries(), final, len(pairs)) if winner == 'R2' else
                                  self.fit_groups(self.entries(), winner))}

    # ----- predicting -----

    def numbers(self, place, ball):
        law = self.laws[place]
        idea = law['idea']
        if ball in self.data[place]:
            return fit(idea, self.data[place][ball], law['w'])[0]
        if self.kind == 'concept' and self.concept and place in TRAINING:
            model, winner = self.concept['model'], self.concept['winner']
            if winner == 'R2':
                _, beta, h, xk = model
                return np.array([beta[(place, t)][0] + beta[(place, t)][1] * xk[(place, t)](ball)
                                 + beta[(place, t)][2] * h.get(ball, 0.0) for t in idea[0]])
            return np.array([self.predict_rule(model[(place, t)], ball) for t in idea[0]])
        cs = [c for c, _, _ in law['numbers'].values()]
        return np.mean(cs, 0)

    def predict(self, place, ball, speed, angle):
        law = self.laws[place]
        return rollout(accel_fn(law['idea'], self.numbers(place, ball), law['w']), speed, angle)

    def surprise_on(self, place_like, throw):
        """How surprising a throw is if the place obeys the law of place_like (noise units)."""
        law = self.laws[place_like]
        v, a = throw
        c = np.mean([c for c, _, _ in law['numbers'].values()], 0)
        d = a - features(law['idea'], v, law['w']) @ c
        return float(np.sqrt(np.mean(d * d)) / SIGMA_A)

    def name(self, words):
        """Learn where 'heavy' starts on the push number from the balls it was told about.
        A ball between the heaviest 'light' ball and the lightest 'heavy' ball gets 'not sure'."""
        qs = {b: self.balls[b]['q'] for b in self.balls}
        heavy = [qs[b] for b, w in words.items() if w == 'heavy']
        light = [qs[b] for b, w in words.items() if w == 'light']
        lo = max(light) if light else -np.inf
        hi = min(heavy) if heavy else np.inf
        if lo >= hi:                                    # the words overlap: no clean cut, so no sure names
            lo, hi = min(lo, hi), max(lo, hi)
        return {b: 'heavy' if qs[b] > hi else 'light' if qs[b] < lo else 'not sure'
                for b in self.balls if b not in words}, (lo, hi)

    # ----- saying it -----

    def sayings(self):
        out = []
        for place in PLACES:
            if place not in self.laws:
                continue
            law = self.laws[place]
            idea, w = law['idea'], law['w']
            parts = []
            for t in idea[0]:
                rule = self.concept['rules'].get((place, t)) if self.concept and self.concept['kept'] else None
                cs = [c[idea[0].index(t)] for c, _, _ in law['numbers'].values()]
                parts.append(term_words(t, rule, float(np.mean(cs))))
            text = f"In the {place}: " + '; '.join(parts)
            wr, medium = law['wind_range'], 'water' if place == 'water' else 'air'
            if idea[1]:
                text += f"; the air moves sideways at {w:+.1f} m/s (somewhere from {wr[0]:+.1f} to {wr[1]:+.1f})"
            elif wr is not None:
                text += f"; the {medium} seems still (any flow lies between {wr[0]:+.1f} and {wr[1]:+.1f} m/s)"
            if place == 'vacuum' and self.galileo and self.galileo['same']:
                text += '. Every ball falls the same, heavy or light'
            if law['sure']:
                text += '. I am sure: every other idea I tried fits worse, and no bigger idea predicts new throws better.'
            elif law['lean'] and law['lean'][1] >= WORTH and law['lean'][0] in law['open']:
                text += (f". I am not sure: {law['lean'][0]} predicts new throws better by {law['lean'][1]:.1f}, "
                         f"and 9 would settle it.")
            else:
                text += f". I am not sure: {', '.join(law['open'])} fits as well."
            out.append(text)
        if self.concept:
            c = self.concept
            if c['kept']:
                out.append('One hidden number per ball, how hard it is to push (its mass), explains how every '
                           f"place treats it. I am sure: it predicted each ball in each place from the others "
                           f"better than 'no sharing' (evidence {c['R1_over_R0']:.0f}) and 'size only' "
                           f"({c['R1_over_Rs']:.0f}), and a second hidden number did not help "
                           f"({c['R2_over_R1']:.0f}; 9 is decisive).")
            elif c['winner'] == 'R2':
                out.append("One hidden number per ball is not enough here: a second hidden number predicted balls in "
                           f"new places better (evidence {c['R2_over_R1']:.0f}; 9 is decisive), so I use two.")
            else:
                out.append("I do not yet think one hidden number per ball explains every place "
                           f"(evidence over no sharing {c['R1_over_R0']:.0f}, over size only {c['R1_over_Rs']:.0f}, "
                           f"second number {c['R2_over_R1']:.0f}; 9 is decisive).")
        return out


def describe(idea):
    names = {'down': 'a steady pull down', 'side': 'a steady push sideways', 'drag1': 'drag in step with speed',
             'drag2': 'drag with speed squared'}
    return ' + '.join(names[t] for t in idea[0]) + (' in moving air' if idea[1] else '')


def size_power(k):
    return {0: '', 1: '·size', 2: '·size²', 3: '·size³'}[k]


def term_words(t, rule, mean):
    what = {'down': 'pulled down by', 'side': 'pushed sideways by', 'drag1': 'slowed by v times',
            'drag2': 'slowed by |v|·v times'}[t]
    if rule is None or rule[0] == 'R0':
        return f'{what} {mean:.3f}'
    _, k, beta, se_c = rule
    if abs(beta[1]) < 3 * se_c:
        return f'{what} {beta[0]:.3f}, the same for every ball'
    a = f'{beta[0]:.3f} ' if abs(beta[0]) > 0.05 else ''
    sign = ('− ' if beta[1] < 0 else '+ ') if a else ('−' if beta[1] < 0 else '')
    return f'{what} {a}{sign}{abs(beta[1]):.3f}{size_power(k)}/mass'


class Net:
    """The ordinary way: one neural network that maps speed, place, which ball, visible size, push
    number and look to acceleration, trained online on every throw it sees."""

    def __init__(self, seed, balls):
        torch.manual_seed(seed)
        self.balls = {b['id']: b for b in balls}
        width = 2 + len(PLACES) + N_BALLS + 2 + 4
        self.net = nn.Sequential(nn.Linear(width, 64), nn.Tanh(), nn.Linear(64, 64), nn.Tanh(), nn.Linear(64, 2))
        self.opt = torch.optim.Adam(self.net.parameters(), lr=3e-3)
        self.x, self.y = [], []

    def context(self, place, ball):
        c = np.zeros(len(PLACES) + N_BALLS + 6)
        c[PLACES.index(place)] = 1.0
        c[len(PLACES) + ball] = 1.0
        b = self.balls[ball]
        c[len(PLACES) + N_BALLS] = b['seen_size']
        c[len(PLACES) + N_BALLS + 1] = PUSH / b['rail_speed']      # the same push number the loop robot gets
        c[len(PLACES) + N_BALLS + 2:] = b['look']
        return c

    def see(self, place, ball, xs, ys):
        v, a = kinematics(xs, ys)
        self.x.append(np.hstack([v, np.tile(self.context(place, ball), (len(v), 1))]))
        self.y.append(a)
        X = torch.tensor(np.vstack(self.x), dtype=torch.float32)
        Y = torch.tensor(np.vstack(self.y), dtype=torch.float32)
        for _ in range(40):
            loss = (self.net(X) - Y).square().mean()
            self.opt.zero_grad()
            loss.backward()
            self.opt.step()

    def predict(self, place, ball, speed, angle):
        W = [p.detach().numpy().astype(float) for p in self.net.parameters()]
        ctx = self.context(place, ball)

        def acc(vx, vy):
            h = np.tanh(W[0] @ np.concatenate(([vx, vy], ctx)) + W[1])
            h = np.tanh(W[2] @ h + W[3])
            out = W[4] @ h + W[5]
            return float(out[0]), float(out[1])
        return rollout(acc, speed, angle)
