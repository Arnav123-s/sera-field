"""The one mind (M1b): it lives a world situation by situation, runs its own experiments, and says "sure" only
with an accepted certificate. See M1_DESIGN.md §4 and §4a.

In each situation (one object, of unknown mass):
  1. the teacher's pushes;
  2. while it is not sure and has budget: find what blocks its leading idea's certificate (an unbeaten rival,
     an extra term whose bound excludes 0, or a band wider than eps) and make the push, from its menu of push
     programs, that it expects to tell them apart best (simulated on copies of its ideas);
  3. at the end of the world: its claim, with the certificate or with what is still open, and the
     "something else" alarm.

The teacher's side (answers, the evidence that decides between two ideas, and fading help) is in `teach`.
"""
import dataclasses
import math

import numpy as np

from . import gaps, grammar, likelihood as L, paths, truth
from .worlds import Action, hand

BUDGET = 3                       # own pushes per situation, as the relentless robot had
COMMANDS = (-1.0, -0.5, 0.5, 1.0)
DURATIONS = (0.2, 0.4, 0.8, 1.2)


def menu(model=None, coef=None, mu=None, durations=DURATIONS, commands=COMMANDS):
    """Push programs it can make: single pushes of several lengths and strengths, and pushes that reverse in
    time with the motion (like pushing a swing), timed from where its leading idea says the object turns.
    A world may lend it tools (a longer rail, a stronger hand): more durations and commands."""
    acts = [Action(((0.0, d, u),)) for d in durations for u in commands]
    if model is not None:
        first = Action(((0.0, 0.4, 1.0),))
        xs, vs = paths.simulate_program(*first.arrays(), mu, model.kind, model.a, model.b, model.codes_coef(coef),
                                        model.sx, model.sv, 0.0, 0.0)
        turns = [i * paths.DT_OBS for i in range(1, len(vs)) if vs[i - 1] > 0 >= vs[i] or vs[i - 1] < 0 <= vs[i]]
        if turns:
            t1 = turns[0]
            acts.append(Action(((0.0, 0.4, 1.0), (t1, t1 + 0.4, -1.0))))
            if len(turns) > 1:
                t2 = turns[1]
                acts.append(Action(((0.0, 0.4, 1.0), (t1, t1 + 0.4, -1.0), (t2, t2 + 0.4, 1.0))))
    return acts


def predicted(model, post, situation, action):
    nc = model.n_coef
    coef = post.mean[:nc]
    mu = post.mean[nc + post.order.index(situation)] if situation in post.order else L.MU_PRIOR[0]
    xs, vs = paths.simulate_program(*action.arrays(), mu, model.kind, model.a, model.b, model.codes_coef(coef),
                                    model.sx, model.sv, 0.0, 0.0)
    return np.concatenate([xs, vs])


def separation(ledger, fam_a, fam_b, situation, action):
    """Expected log-evidence one push would add between two families: 0.5 * |(f_A - f_B) / sigma|^2."""
    ma, mb = ledger._models[fam_a], ledger._models[fam_b]
    fa = predicted(ma, ledger.post[fam_a], situation, action)
    fb = predicted(mb, ledger.post[fam_b], situation, action)
    scale = np.concatenate([np.full(paths.N_OBS, 1 / ledger.sigma[0]), np.full(paths.N_OBS, 1 / ledger.sigma[1])])
    d = (fa - fb) * scale
    return 0.5 * float(d @ d) if np.all(np.isfinite(d)) else 0.0


def blocker(ledger, leader, cert):
    """What stands between the leader and a certificate: a family to separate it from, or None (band)."""
    thr = grammar.log_threshold(leader, cert.alpha)      # D9
    weak = [b for b, e in cert.rivals.items() if e < thr and b in ledger.Q]     # truth-v2 T2: a wide rival has no
    if weak:                                                                     # score here; the grower adds it
        return max(weak, key=lambda b: ledger.Q[b])
    wide = [(hi - lo, i) for i, (lo, hi) in cert.nested.items() if not lo <= 0.0 <= hi]
    if wide:
        return grammar.canonical(leader + (max(wide)[1],))
    return None


def worst_band_cells(ledger, leader, share=0.1):
    """Where the "something else" band is widest (search only; the certificate recomputes the band itself):
    the flexible fit of the leader plus the smooth basis, evaluated on the visited cells (D10). Returns the scope
    and the worst cells (at least 3)."""
    scope = truth.scope_of(ledger.throws)
    model = truth.model_of(leader, extra_basis=True, scope=scope)
    q_f, post_f = truth.prequential(model, ledger.throws, ledger.sigma)
    fit_f = L.fit(model, ledger.throws, ledger.sigma, start=post_f, iters=40)
    basis = truth.basis_for(leader, scope)
    na, nb = grammar.n_coef(leader), len(basis)
    if not fit_f.ok:
        return scope, []
    cb, cov = fit_f.coef[na:na + nb], fit_f.cov[na:na + nb, na:na + nb]
    radius2 = max(2.0 * (fit_f.loglik - q_f + math.log(len(ledger.families) / 1e-3)), 0.0)
    xs = np.linspace(scope['x'][0], scope['x'][1], truth.GRID)
    vs = np.linspace(scope['v'][0], scope['v'][1], truth.GRID)
    vals = []
    for (i, j) in scope['cells']:
        b = np.array([paths.term(1, d[0], d[1], xs[i], vs[j], model.sx, model.sv) for d in basis])
        vals.append((abs(float(b @ cb)) + math.sqrt(radius2 * max(float(b @ cov @ b), 0.0)), (i, j)))
    vals.sort(reverse=True)
    return scope, [c for _, c in vals[:max(3, int(round(share * len(vals))))]]


def band_push(ledger, leader, k, options):
    """The push whose predicted path spends the most readings in the cells where the band is widest (D10: more
    readings there shrink the band; a push into unvisited places would add new cells instead)."""
    model, post = ledger._models[leader], ledger.post[leader]
    scope, worst = worst_band_cells(ledger, leader)
    targets = set(worst)

    def hits(a):
        p = predicted(model, post, k, a)
        return sum(truth.cell_of(scope, float(x), float(v)) in targets
                   for x, v in zip(p[:paths.N_OBS], p[paths.N_OBS:]))

    scored = [(hits(a), -float(np.max(np.abs(predicted(model, post, k, a)))), n) for n, a in enumerate(options)]
    return options[max(scored)[2]]


def merge_proposals(from_leader, from_hand, top):
    """Up to `top` distinct proposals, taken alternately from the leader's leftover and the hand-only leftover."""
    out, seen = [], set()
    for pair in zip(from_leader + [None] * len(from_hand), from_hand + [None] * len(from_leader)):
        for p in pair:
            if p is not None and p['term'] not in seen and len(out) < top:
                seen.add(p['term'])
                out.append(p)
    return out


def bracket_exponents(proposals, span=0.3):
    """Add the grid neighbours (within `span`) of each input's leading power term, so the exact evidence, not the
    fast tier, chooses the exponent. The fast tier fits central-difference accelerations, which smear the kink of
    |v|^p at v = 0: for p = 0.2-0.4 it prefers 0.5 (measured 2026-09-24)."""
    out, seen, done = list(proposals), {p['term'] for p in proposals}, set()
    grid = [q for q in gaps.P_GRID if q not in (1.0, 2.0, 3.0)]
    for p in proposals:
        term = p['term']
        if term[0] != 'power' or term[1] in done:
            continue
        done.add(term[1])
        for q in grid:
            if 0 < abs(q - term[2]) <= span + 1e-9 and ('power', term[1], q) not in seen:
                seen.add(('power', term[1], q))
                out.append({'term': ('power', term[1], q), 'gain': 0.0, 'name': grammar.term_name(('power', term[1], q))})
    return out


@dataclasses.dataclass
class Report:
    claim: tuple
    sure: bool
    certificate: object
    alarm: bool
    open: tuple
    throws: int
    own_pushes: int
    events: tuple = ()                # (situation, event): 'surprise', 'blocked', 'end', 'alarm'
    ledger: object = dataclasses.field(default=None, repr=False)
    invention: object = dataclasses.field(default=None, repr=False)   # see Mind._invent


SURPRISE_RMS = 5.0               # a push that lands this many sigmas (RMS) from what its leading idea predicts


class Mind:
    def __init__(self, sigma, eps=0.1, budget=BUDGET, experiments=True, on_event=None, board=None, invent=False,
                 invent_top=8, invent_budget=6):
        """on_event(situation, event) is called at public moments (the caretaker listens; it cannot change the
        evidence). `board` is accepted for the School's bookkeeping and never read here: in M1 the board only
        orders the gut's ideas and chooses worlds, so the mind's pushes and evidence are the same with or
        without it (check C13a)."""
        self.sigma = sigma
        self.eps = eps
        self.budget = budget
        self.experiments = experiments
        self.on_event = on_event
        self.board = board
        self.invent = invent
        self.invent_top = invent_top
        self.invent_budget = invent_budget

    def live(self, world):
        """Live one world: returns a Report. `world` gives situations and makes pushes (world.push)."""
        ledger = truth.Ledger(grammar.space(), self.sigma)
        own = 0
        events = []

        def emit(k, event):
            events.append((k, event))
            if self.on_event is not None:
                self.on_event(k, event)

        tools = getattr(world, 'tools', None) or {}
        durations, commands = tools.get('durations', DURATIONS), tools.get('commands', COMMANDS)
        teacher = world.situations()
        for k in range(world.n_situations):
            for i, throw in enumerate(teacher[k]):      # the teacher's pushes (made in advance, same for all minds)
                if i == 0:                              # resistance: the push lands far from what it expected
                    lead = ledger.best_family()
                    pred = predicted(ledger._models[lead], ledger.post[lead], k, throw.action)
                    z = np.concatenate([(throw.x - pred[:paths.N_OBS]) / self.sigma[0],
                                        (throw.v - pred[paths.N_OBS:]) / self.sigma[1]])
                    if np.all(np.isfinite(z)) and math.sqrt(float(np.mean(z * z))) > SURPRISE_RMS:
                        emit(k, 'surprise')
                ledger.add(throw)
            blocked = False
            for _ in range(self.budget if self.experiments else 0):
                leader = ledger.best_family()
                cert = truth.certify(ledger, leader, self.eps)
                if cert.accepted:
                    break
                rival = blocker(ledger, leader, cert)
                if rival is not None and not blocked:
                    emit(k, 'blocked')
                    blocked = True
                model = ledger._models[leader]
                post = ledger.post[leader]
                nc = model.n_coef
                mu = post.mean[nc + post.order.index(k)] if k in post.order else L.MU_PRIOR[0]
                options = menu(model, post.mean[:nc], mu, durations, commands)
                if rival is not None:
                    best = max(options, key=lambda a: separation(ledger, leader, rival, k, a))
                else:                                   # the band blocks: revisit where it is widest (D10)
                    best = band_push(ledger, leader, k, options)
                ledger.add(world.push(k, best, 'own'))
                own += 1
            emit(k, 'end')
        leader = ledger.best_family()
        cert = truth.certify(ledger, leader, self.eps)
        alarm = truth.something_else(ledger, leader)[0]
        if alarm:
            emit(world.n_situations - 1, 'alarm')
        invention = self._invent(world, ledger, leader, durations, commands) if (alarm and self.invent) else None
        return Report(leader, bool(cert.accepted), cert, bool(alarm), cert.reasons, len(ledger.throws), own,
                      tuple(events), ledger, invention)

    def _invent(self, world, ledger, leader, durations, commands):
        """When the alarm fires: imagine terms that fill the gap (gaps.propose, from the leftover's shape), replay
        every stored throw through a ledger over the base ideas plus those terms (prequentially, in order), and
        run its own experiments on the last object against whatever blocks the best family's certificate. The
        claim needs log(1/(alpha pi)) against every rival (D9), so growing on noise stays below alpha."""
        # Proposals from the leader's leftover and from the hand-only leftover (development note, 2026-09-24: in an x*v world the
        # leading base family had absorbed part of the effect and x*v was not among its leftover's proposals).
        # Session 2 (dev seed 1, T5): both lists must contribute (the cap used to be filled from the first list), and
        # the exact tier gets each leading exponent's neighbours, because the fast tier's exponent is biased.
        proposals = merge_proposals(gaps.propose(ledger.throws, leader, top=self.invent_top),
                                    gaps.propose(ledger.throws, (), top=self.invent_top), self.invent_top)
        proposals = sorted(bracket_exponents(proposals), key=lambda p: -p['gain'])
        terms = tuple(p['term'] for p in proposals)
        inv = truth.Ledger(grammar.space(inventions=terms), self.sigma)
        for t in ledger.throws:
            inv.add(t)
        k, own = world.n_situations - 1, 0
        for _ in range(self.invent_budget):
            lead = inv.best_family()
            cert = truth.certify(inv, lead, self.eps)
            if cert.accepted:
                break
            rival = blocker(inv, lead, cert)
            model, post = inv._models[lead], inv.post[lead]
            nc = model.n_coef
            mu = post.mean[nc + post.order.index(k)] if k in post.order else L.MU_PRIOR[0]
            options = menu(model, post.mean[:nc], mu, durations, commands)
            if rival is not None:
                best = max(options, key=lambda a: separation(inv, lead, rival, k, a))
            else:
                best = band_push(inv, lead, k, options)
            inv.add(world.push(k, best, 'own'))
            own += 1
        lead = inv.best_family()
        return {'proposals': proposals, 'family': lead, 'certificate': truth.certify(inv, lead, self.eps),
                'ledger': inv, 'own': own}
