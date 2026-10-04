"""U9: search and retention, not supplied laws or proof of truth by compression.

Only public descriptors, performed experiments, own conjectures and scalar
judge verdicts survive here. A runner-owned pool is a transient argument; no
world, oracle, teacher target, held-out throw or bound method is stored.
"""
import copy
from dataclasses import dataclass
import math
import time
from types import SimpleNamespace

import numpy as np

from sera import compact as C, lang as LG, phi as PH, tasks as TS
from .ports import TaskView, digest, observed
from .sleep import Receipt, expand, family, independent, substitute

CRUTCHES = ('open_worlds', 'own_questions', 'designed_experiments',
            'unification_credit', 'hidden_quantities')
DEFAULT_SHARE = .10
SCHEMA = 'u9-discovery-1'


@dataclass(frozen=True)
class WorldView:
    """Body's public interface, with an opaque identity and no posed problem."""
    id: str
    form: str
    tin: str = 'num'
    tout: str = 'num'
    objects: int = 1
    sigma: tuple = (.001, .001)
    object_ids: tuple = ()       # optional public continuity of the same bodies

    def __post_init__(self):
        if (type(self.id) is not str or type(self.form) is not str or type(self.tin) is not str or
                type(self.tout) is not str or type(self.objects) is not int or
                self.form not in ('exact', 'strengths') or not self.id or self.objects < 1):
            raise ValueError('Invalid open-world interface')
        object.__setattr__(self, 'sigma', observed(self.sigma))
        object.__setattr__(self, 'object_ids', observed(self.object_ids))
        if any(type(k) is not str for k in self.object_ids):
            raise ValueError('Public object identities must be opaque strings')
        if (self.tin not in ('num', 'list') or self.tout not in ('num', 'list') or
                len(self.sigma) != 2 or any(type(s) not in (int, float) or
                    not math.isfinite(s) or s <= 0 for s in self.sigma)):
            raise ValueError('Finite positive sensor uncertainties required')


@dataclass(frozen=True)
class Certification:
    """Allowlisted verdict. No counterexample or hidden input leaves the judge."""
    accepted: bool
    kind: str
    bound: tuple                 # e.g. ('eps', .2), ('delta', 1e-6), ('audit_n', n)
    record: str                  # opaque observer record ID
    refuted: bool = False        # distinguish uncertainty from a witnessed failure

    def __post_init__(self):
        if type(self.accepted) is not bool or type(self.refuted) is not bool:
            raise TypeError('Boolean judge verdict required')
        if self.kind not in ('curve', 'drawing', 'formula'):
            raise ValueError('Honest credit kind required')
        object.__setattr__(self, 'bound', observed(self.bound))
        if type(self.record) is not str or not self.record or not self.bound:
            raise ValueError('A bound judge record is required')


@dataclass(frozen=True)
class OwnQuestion:
    view: TaskView
    world: str
    observations: str
    reason: str
    scope: str = 'own-question'
    origin: str = 'explore'


class Readout:
    """Neutral Gaussian return policy, like U3 ways and U6's Field decoder.

    All arms start at zero with equal uncertainty. The measured return is
    learning progress per charged second. Raw elapsed times belong in reports.
    Teacher sufficient statistics fade by the existing TAUGHT_FADE.
    """
    def __init__(self):
        self.own, self.taught = {}, {}
        self.steps = 0

    def posterior(self, name):
        a, b = self.own.get(name, (np.zeros((65, 65)), np.zeros(65)))
        ta, tb = self.taught.get(name, (np.zeros((65, 65)), np.zeros(65)))
        precision = np.eye(65) + a + ta
        cov = np.linalg.inv(precision)
        return cov @ (b + tb), cov

    def score(self, name, x, rng):
        mean, cov = self.posterior(name)
        return float(rng.multivariate_normal(mean, cov) @ x)

    def pick(self, choices, x, rng):
        return min(sorted(choices), key=lambda n: (-self.score(n, x, rng), n))

    def learn(self, name, x, gain, seconds):
        y = float(np.clip(gain / max(seconds, 1e-6), -20., 20.))
        a, b = self.own.setdefault(name, (np.zeros((65, 65)), np.zeros(65)))
        a += np.outer(x, x)
        b += x*y
        self.steps += 1
        for ta, tb in self.taught.values():
            ta *= PH.TAUGHT_FADE
            tb *= PH.TAUGHT_FADE

    def demonstrate(self, name, x, phase):
        if phase not in ('lesson', 'study', 'test1'):
            raise ValueError('No teacher demonstration outside the U5 teaching phases')
        a, b = self.taught.setdefault(name, (np.zeros((65, 65)), np.zeros(65)))
        a += np.outer(x, x)
        b += x


def add_proof(field, key, support=1):
    """One more proof of `key`, counted as every proof is: in layer B's role counts when the Field understands
    (SERA-U's MemoryField has no standing table), else in the legacy Field's standing table."""
    if getattr(field, 'field_understanding', False):
        from .memory import add_count
        add_count(field.ideas, ('hypothesis', key), support=support)
    else:
        field.standing.setdefault(key, [0, 0])[0] += support


def compression_credit(bits, coverage):
    """Two-part code: sum of baseline minus residual bits, minus one law code.

    Each world has one current observation snapshot, so revisiting does not
    multiply its credit. This is compression credit, not a proof of truth.
    """
    return sum(base-residual for base, residual in coverage.values()) - bits


def hidden_quantity(objects, responses, drives, sigma, *, bits_per_number=32.):
    """Fit an unnamed number per thing against the best shared-number rival.

    The drive already includes the conjectured force. Compare the same
    residual Gaussian code on both sides; charge identifiers AND all scalars.
    Neither caller nor this fitter knows the world's true per-object numbers.
    A tentative fitted quantity is not credited as a certified physical law.
    """
    obj = np.asarray(objects, int)
    y, f = np.asarray(responses, float), np.asarray(drives, float)
    if (not (len(obj) == len(y) == len(f)) or not len(y) or not math.isfinite(sigma) or sigma <= 0 or
            not math.isfinite(bits_per_number) or bits_per_number < 0):
        raise ValueError('Aligned own observations and positive noise required')
    if not np.isfinite(y).all() or not np.isfinite(f).all():
        raise ValueError('Finite own measurements required')
    shared = float(f @ y / max(f @ f, 1e-12))
    values, pred = {}, np.zeros_like(y)
    for k in sorted(set(map(int, obj))):
        mask = obj == k
        fk, yk = f[mask], y[mask]
        if len(fk) < 2 or fk @ fk < 1e-10:
            return None
        value = float(fk @ yk / (fk @ fk))
        values[k], pred[mask] = value, value*fk
    factor = 1. / (2*sigma*sigma*math.log(2))
    without = float(np.sum((y-shared*f)**2))*factor + bits_per_number
    with_it = float(np.sum((y-pred)**2))*factor + len(values)*(
        bits_per_number + math.log2(max(2, len(values))))
    representation = 'per-thing'
    unit, counts = None, ()
    # Search an unnamed shared scale times small integers; never read or name
    # the units world's hidden layer. All candidates come from fitted values.
    if all(v > 0 for v in values.values()):
        masses = {k: 1/v for k, v in values.items()}
        scales = sorted({m/n for m in masses.values() for n in range(1, 7)})
        for scale in scales:
            ns = {k: max(1, min(6, int(round(m/scale)))) for k, m in masses.items()}
            fitted = {k: 1/(scale*ns[k]) for k in ns}
            prediction = np.array([f[i]*fitted[int(k)] for i, k in enumerate(obj)])
            code = (bits_per_number + len(ns)*(math.log2(max(2, len(ns)))+math.log2(6))
                    + float(np.sum((y-prediction)**2))*factor)
            if code < with_it:
                with_it, values = code, fitted
                unit, counts, representation = scale, tuple(sorted(ns.items())), 'shared-scale'
    if with_it >= without:
        return None
    return dict(values=tuple(sorted(values.items())), bits_saved=without-with_it,
                without_bits=without, with_bits=with_it, representation=representation,
                scale=unit, counts=counts)


def split_score(predictions, bits=()):
    """Entropy of rival program answers, the split question of synth._split.

    Here candidates use SERA's language rather than synth's older grammar.
    No answers from the world are queried to calculate the split.
    """
    counts = {}
    if bits and len(bits) != len(predictions):
        raise ValueError('One description length per rival required')
    offset = min(bits) if bits else 0.
    for j, y in enumerate(predictions):
        weight = 2.**(-(bits[j]-offset)) if bits else 1.
        counts[repr(y)] = counts.get(repr(y), 0)+weight
    n = sum(counts.values())
    return -sum(v/n*math.log2(v/n) for v in counts.values() if v) if n else 0.


def residual_code(values, sigma):
    """A fixed, disclosed two-part signed-integer code at sensor precision.

    Quantize each residual in units of sigma; unary magnitude bit-length plus
    its binary digits and sign is a decodable code. No truth grades enter it.
    It is a search objective, not an alteration of the certificate's bar.
    """
    out = 0.
    for value in np.asarray(values, float).ravel():
        if not math.isfinite(value):
            return math.inf
        n = abs(int(round(float(value)/sigma)))
        out += 1 + 2*max(1, n.bit_length())
    return out


def public_rail(world, observations):
    """Reuse Rail's perception and fitting with an inert body, no world law."""
    from ccops5.core.worlds import Action, Throw
    task = TS.Rail.__new__(TS.Rail)
    task.world = SimpleNamespace(n_situations=world.objects)
    task.name, task.words, task.signs = world.id, [], None
    task.sigma = world.sigma
    task.throws = [Throw(k, j, Action(segments), np.array(xs), np.array(vs), 'own')
                   for j, (k, segments, xs, vs) in enumerate(observations)]
    task._ledger, task._cache, task._knots, task.pushes = None, {}, {}, len(observations)
    return task


class Discovery:
    def __init__(self, switches, einstein=None, scientists=None, darwin=None, roadmap=None):
        if set(switches) != set(CRUTCHES) or any(type(v) is not bool for v in switches.values()):
            raise ValueError('Declare all registered discovery switches')
        self.switches = dict(switches)
        self.policy = Readout()
        self.worlds, self.observations, self.rivals, self.levels = {}, {}, {}, {}
        self.surprises, self.tried, self.laws, self.quantities = {}, {}, {}, {}
        self.questions, self.pending, self.events = [], [], []
        self.active = None
        self.experiments = self.checks = 0
        self.teacher_shown = False
        from sera import crutches as CR
        from .einstein import CRUTCHES as U10, Einstein
        ways = {k: CR.on(k) for k in U10} if einstein is None else dict(einstein)
        if set(ways) != set(U10) or any(type(v) is not bool for v in ways.values()):
            raise ValueError('Declare all four boolean U10 switches')
        if any(ways.values()):
            self.einstein = Einstein(ways)
        from .scientists import CRUTCHES as U11, Scientists
        habits = {k: CR.on(k) for k in U11} if scientists is None else dict(scientists)
        if set(habits) != set(U11) or any(type(v) is not bool for v in habits.values()):
            raise ValueError('Declare all five boolean U11 switches')
        if any(habits.values()):
            self.scientists = Scientists(habits)
        from .darwin import CRUTCHES as U12, Darwin
        habits = {key: CR.on(key) for key in U12} if darwin is None else dict(darwin)
        if set(habits) != set(U12) or any(type(value) is not bool for value in habits.values()):
            raise ValueError('Declare all five boolean U12 switches')
        if any(habits.values()):
            self.darwin = Darwin(habits)
        from .roadmap import CRUTCHES as U13, Roadmap
        habits = {key: CR.on(key) for key in U13} if roadmap is None else dict(roadmap)
        if set(habits) != set(U13) or any(type(value) is not bool for value in habits.values()):
            raise ValueError('Declare all three boolean U13 switches')
        if any(habits.values()):
            self.roadmap = Roadmap(habits)

    def quantity_values(self, wid):
        rows = [v for k, v in self.quantities.items() if k[1] == wid]
        return dict(rows[-1]['values']) if rows else None

    def reuse_credit(self, hypothesis, form):
        if not self.switches['unification_credit']:
            return 0.
        # Compression is a learned search prior, never a shortcut past an audit.
        return max((self.standing(k) for k, e in self.laws.items()
                    if e['hypothesis'] == hypothesis and e['form'] == form), default=0.)

    def learning_state(self):
        # Events contain raw elapsed costs and are observer reporting only.
        state = {k: v for k, v in self.__dict__.items() if k not in ('events', 'einstein', 'scientists', 'darwin', 'roadmap', '_wiring_hops', '_wiring_enabled')}
        if hasattr(self, 'einstein'):
            state['einstein'] = self.einstein.learning_state()
        if hasattr(self, 'scientists'):
            state['scientists'] = self.scientists.learning_state()
        if hasattr(self, 'darwin'):
            state['darwin'] = self.darwin.learning_state()
        if hasattr(self, 'roadmap'):
            state['roadmap'] = self.roadmap.learning_state()
        return state

    def trace(self, name, laws, outputs=()):
        """Observer-only receipts at consumer entry/output, no inferred credit."""
        if not getattr(self, '_wiring_enabled', False):
            return
        entry = self.__dict__.setdefault('_wiring_hops', {}).setdefault(name, dict(received=set(), outputs=set()))
        entry['received'].update(laws)
        entry['outputs'].update(outputs)
        self.events.append(dict(seconds=0., wiring_hop=dict(habit=name,
            received=sorted(laws, key=repr), outputs=sorted(outputs, key=repr))))

    def syndromes(self, mind, view, rivals):
        checks = mind.field.curiosity.checks(view, rivals, mind.field.concept_table())
        if checks:
            read = mind.engine._u_reads([view])[0][0].detach().cpu().numpy()
            mind.field.curiosity.decode(view, checks, read)
            self.trace('gap_syndromes', [k for k, e in self.laws.items() if e['hypothesis'] in rivals],
                       ['checks:'+digest(tuple(s.check for s in checks))])
        return checks

    def view(self, wid, query=()):
        w, rows = self.worlds[wid], self.observations[wid]
        if w.form == 'exact':
            return TaskView((('x', w.tin),), w.tout,
                tuple(((('x', x),), y) for x, y in rows[-4:]),
                tuple((('x', observed(x)),) for x in query),
                measurements=tuple(('object-identity', k) for k in w.object_ids))
        # Raw observations, deterministic bounded sampling for the neural port.
        # The symbolic fitter still uses every own observed reading.
        measurements = []
        for j, (k, segs, xs, vs) in enumerate(rows[-4:]):
            measurements.extend(('push', j, a, b, f) for a, b, f in segs)
            step = max(1, math.ceil(len(xs)/20))
            from ccops5.core import paths
            measurements.extend(('motion', k, j, i*paths.DT_OBS, xs[i], vs[i])
                                for i in range(0, len(xs), step))
        return TaskView((('s', 'num'),), 'num', measurements=tuple(measurements), form='strengths')

    def own_question(self, wid, reason, query=()):
        if reason not in ('surprise', 'committee', 'anomaly', 'paradox', 'principle'):
            raise ValueError('Own public reason required')
        q = OwnQuestion(self.view(wid, query), wid, digest(self.observations[wid]), reason)
        self.questions.append(q)
        del self.questions[:-64]
        return q

    def features(self, mind, view):
        read = mind.engine._u_reads([view])[0][0].detach().cpu().numpy()
        return PH.InnerJudge.features(read)

    def standing(self, law):
        entry = self.laws[law]
        if not self.switches['unification_credit']:
            return float(len(entry['coverage']))
        mean, _ = self.policy.posterior('unify')
        # Neutral weight starts at one; it learns only from later reuse verdicts.
        weight = math.exp(float(np.clip(mean @ entry['features'], -4., 4.)))
        credit = compression_credit(entry['bits'], entry['coverage'])
        return weight*credit if math.isfinite(credit) else 0.

    def search_view(self, wid):
        snapshot = digest(self.observations[wid])
        return next((q.view for q in reversed(self.questions)
                     if q.world == wid and q.observations == snapshot), self.view(wid))

    def candidate_features(self, mind, wid, hyp):
        # Bounded imagined identity; a long fitted table's repr would overflow
        # the neural byte port. Public observations are left intact.
        from dataclasses import replace
        view = self.search_view(wid)
        row = ((('hypothetical-candidate', digest(hyp)),),)
        return self.features(mind, replace(view, hypotheses=view.hypotheses+row))

    def anomaly(self, mind, wid, law, verdict):
        if not verdict.refuted:
            return None
        entry = dict(world=wid, law=law, status='not-yet', scope='own-question', origin='explore')
        if entry not in self.pending:
            self.pending.append(entry)
        if hasattr(mind, 'holes'):
            mind.holes.anomaly(mind, wid, law=law)
        q = self.own_question(wid, 'anomaly') if self.switches['own_questions'] else None
        if mind.crutches.get('taught_not_yet'):
            view = self.view(wid)
            if not any(r['identity'] == view.identity for r in mind.field.revisit_queue):
                mind.field.revisit_queue.append(dict(identity=view.identity, view=view, phase='world',
                    attempts=1, first_at=mind.field.tasks, last_at=mind.field.tasks,
                    current_identity=view.identity, current_view=view, status='not-yet',
                    origin='explore', discovery_world=wid))
        if hasattr(self, 'einstein'):
            self.einstein.doubt(self, wid, (law,), source=verdict.record)
        if hasattr(self, 'scientists'):
            self.scientists.anomaly(self, wid, law, verdict)
        # In particular, do not refute this law's certificates in other worlds.
        return q

    def demonstrate_quantity(self, objects, y, f, sigma, *, phase='lesson'):
        if self.teacher_shown or not self.switches['hidden_quantities']:
            return False
        result = hidden_quantity(objects, y, f, sigma)
        if result is None:
            return False
        self.policy.demonstrate('quantity', np.r_[1., np.zeros(64)], phase)
        self.teacher_shown = True
        return True

    def register_worlds(self, public):
        for w in public:
            if type(w) is not WorldView:
                raise TypeError('Open world descriptors only')
            if w.id in self.worlds and self.worlds[w.id] != w:
                raise ValueError('Open-world body changed during resume')
            self.worlds[w.id] = w
            self.observations.setdefault(w.id, [])
            self.rivals.setdefault(w.id, ())
            self.levels.setdefault(w.id, 0)
            self.surprises.setdefault(w.id, 0.)

    def propose(self, mind, wid, deadline):
        """Field proposals plus bounded language search; never a law dictionary."""
        if getattr(self, '_wiring_enabled', False):
            self.events.append(dict(seconds=0., wiring_proposal=wid))
        w, view = self.worlds[wid], self.search_view(wid)
        concepts = mind.proposer.admitted(mind.field.concept_table())
        level = self.levels[wid]
        saved = LG.DEADLINE[0]
        LG.DEADLINE[0] = deadline
        try:
            if w.form == 'exact':
                nums = TS.numbers_of([(dict(b)['x'], y) for b, y in view.examples])
                found = (mind.proposer.beam(view, concepts, constants=nums, nodes=9+level, deadline=deadline)
                         if mind.proposer.enabled else [])
                if time.time() < deadline:
                    probes = [dict(b) for b, _ in view.examples]
                    probes += [dict(b) for b in view.queries]
                    # Observational equivalence must also include imagined inputs:
                    # deduping only on answered inputs destroys the rival committee.
                    from .sleep import sample_input
                    probes += [{'x': sample_input(w.tin, mind.random)} for _ in range(8)]
                    found += [p for p, _ in LG.search(dict(view.inputs), w.tout, probes,
                        3+2*level, concepts, constants=nums,
                        work=max(1, int(deadline-mind.clock.count)) if getattr(mind, 'clock_mode', 'wall') == 'work' else 256*(level+1),
                        lambda_size=3+level)]
                # Prefer previously discovered laws; they are conjectures here.
                found += [e['hypothesis'] for e in self.laws.values() if e['form'] == 'exact'
                          and e['signature'] == (w.tin, w.tout)]
                if hasattr(self, 'scientists'):
                    found += list(self.scientists.predicted_laws(self, wid))
                found = sorted(set(found), key=lambda p: (
                    sum(LG.safe(p, dict(b), concepts) != y for b, y in view.examples),
                    LG.bits(p, concepts)-self.reuse_credit(p, w.form), repr(p)))
                if hasattr(self, 'einstein'):
                    found = self.einstein.order(mind, self, wid, found)
                return tuple(found[:16])
            task = public_rail(w, self.observations[wid])
            mu = self.quantity_values(wid) or task.first_masses()
            if self.quantities and self.switches['hidden_quantities']:
                # A partial fitted table augments the body's initial sensing,
                # without removing unvisited objects from the fitter.
                mu = {**task.first_masses(), **mu}
            parts = mind.engine._parts_physics(task, level, concepts)
            single = task.evidence([(p,) for p in parts], concepts, mind.field.shapes(), mu)
            laws = mind.engine._laws(task, parts, single, level)
            laws += [e['hypothesis'] for e in self.laws.values() if e['form'] == 'strengths']
            evidence = task.evidence(laws, concepts, mind.field.shapes(), mu)
            return tuple(sorted(set(laws), key=lambda p: (
                -evidence.get(p, -math.inf)-math.log(2)*self.reuse_credit(p, w.form),
                mind.engine._bits(p, w.form, concepts), repr(p)))[:8])
        finally:
            LG.DEADLINE[0] = saved

    def experiment_menu(self, mind, wid):
        w, rows, rivals = self.worlds[wid], self.observations[wid], self.rivals[wid]
        concepts = mind.field.concept_table()
        if w.form == 'exact':
            from .sleep import sample_input
            # The body bounds the hand, not the observer's audit distribution.
            inputs = [sample_input(w.tin, mind.random) for _ in range(24)]
            inputs += [dict(b)['x'] for b in self.search_view(wid).queries]
            menu, seen = [], {x for x, _ in rows}
            for x in sorted(set(inputs), key=repr):
                if x in seen:
                    continue
                ys = [LG.safe(p, {'x': x}, concepts) for p in rivals]
                location = TS.JudgeScrutiny.region(x)
                last = TS.JudgeScrutiny.region(rows[-1][0]) if rows else location
                surprise = self.surprises[wid]/(1+sum((a-b)**2 for a, b in zip(location, last)))
                menu.append(dict(action=('ask', x), info=split_score(ys, tuple(LG.bits(p, concepts) for p in rivals)),
                                 surprise=surprise,
                                 predicted=ys[0] if ys else None))
            return menu
        from ccops5.core.worlds import Action
        if len(rows) < 2 or not rivals:
            return [dict(action=('push', k, Action(((0., d, u),)).segments), info=0., surprise=0., predicted=None)
                    for k in range(w.objects) for d in (.5, 1.2, 2.) for u in (-1., 1.)]
        task = public_rail(w, rows)
        claims = [task.claim_terms(p, concepts, mind.field.shapes(), ramp=True) for p in rivals]
        families = list(dict.fromkeys(f for claim in claims if claim for f in [claim[0]]))
        if not families:
            return [dict(action=('push', k, Action(((0., .5, u),)).segments),
                         info=0., surprise=self.surprises[wid], predicted=None)
                    for k in range(w.objects) for u in (-1., 1.)]
        try:
            led = task.ledger(families)
            # Reuses design.programs' hand-limited pumping/switching programs
            # and Rail's Box-Hill rival separation. Nothing is pushed here.
            menu = task.actions(mind.numpy, led, families, np.full(len(families), 1/len(families)))
        except (ValueError, np.linalg.LinAlgError):
            return []
        return [dict(action=('push', int(r['action'][1]), r['action'][2].segments),
                     info=r['info'], surprise=self.surprises[wid],
                     predicted=None if r['predicted'] is None else tuple(map(float, r['predicted']))) for r in menu]

    def choose_experiment(self, menu, x, rng):
        if not menu:
            return None, None
        if not self.switches['designed_experiments']:
            return menu[int(rng.integers(len(menu)))], 'random'
        route = self.policy.pick(('split', 'surprise', 'random'), x, rng)
        if route == 'random':
            return menu[int(rng.integers(len(menu)))], route
        key = 'info' if route == 'split' else 'surprise'
        return min(menu, key=lambda r: (-r[key], repr(r['action']))), route

    def fit_quantity(self, mind, wid, x):
        started = time.perf_counter()
        if not self.switches['hidden_quantities'] or self.worlds[wid].form != 'strengths':
            return None
        # Its use is a learned choice, whereas the bits gate is compulsory.
        if self.policy.pick(('quantity', 'no-quantity'), x, mind.numpy) != 'quantity':
            self.policy.learn('no-quantity', x, 0., time.perf_counter()-started)
            return None
        task = public_rail(self.worlds[wid], self.observations[wid])
        obj, y, hand, xb, vb, tb = C.intervals(task.throws)
        # Local drift is nuisance, fitted only to its own measurements; no
        # dictionary of domain laws or true object numbers is supplied.
        drift = np.column_stack((np.ones(len(y)), xb, vb, tb))
        residual, drives = y.copy(), hand.copy()
        for k in sorted(set(map(int, obj))):
            mask = obj == k
            d = drift[mask]
            residual[mask] -= d @ np.linalg.lstsq(d, y[mask], rcond=None)[0]
            drives[mask] -= d @ np.linalg.lstsq(d, hand[mask], rcond=None)[0]
        result = hidden_quantity(obj, residual, drives,
            math.sqrt(2)*task.sigma[1]/C.DT)
        if result is None:
            self.policy.learn('quantity', x, 0., time.perf_counter()-started)
            return None
        key = ('quantity', wid, digest(result['values']))
        if key not in self.quantities:
            self.quantities[key] = result
            # An unnamed concept with its own key, tentative until the whole
            # conjecture is certified. This table is of FITTED observations.
            mind.field.ideas.bind(('observed-world', wid), key, 1.)
            if mind.crutches['sleep_library'] and len(result['values']) >= 2:
                grid, values = zip(*result['values'])
                body = LG.node('tab', payload=(tuple(map(float, grid)), tuple(values)))
                concept = mind.field.invent(body, ('num', 'num'), 'physics', wid+' (wished)',
                    (key,), extra=dict(origin='explore', quantity_key=key, quantity_hypothesis=True,
                                      bits_saved=result['bits_saved']))
                result['concept_id'] = concept['id']
                mind.proposer.changed()
        self.policy.learn('quantity', x, min(1., result['bits_saved']/max(result['without_bits'], 1.)),
                          time.perf_counter()-started)
        return key

    def observation_code(self, mind, wid, hyp):
        w = self.worlds[wid]
        if w.form == 'exact':
            base = sum(8*len(repr(y).encode()) for _, y in self.observations[wid])
            # The audit bounds errors under D; it does not override any observed
            # counterexample. Encode all own misses rather than claiming zero.
            concepts = mind.field.concept_table()
            missed = sum(8*len(repr(y).encode())+16 for v, y in self.observations[wid]
                         if LG.safe(hyp, {'x': v}, concepts) != y)
            return float(base), 16.+missed
        from ccops5.core import likelihood as L
        task = public_rail(w, self.observations[wid])
        concepts = mind.field.concept_table()
        fam = task.family(hyp, concepts, mind.field.shapes())
        if fam is None:
            return 0., math.inf
        led = task.ledger([fam])
        fit = led.mle(fam)
        if not fit.ok:
            return 0., math.inf
        model = led._models[fam]
        base, residual = 0., 16. + 32*(len(fit.coef)+len(fit.mu))
        for t in task.throws:
            kt = L.knocked(t, (fit.knocks or {}).get(t.situation, 0))
            actual = np.concatenate((t.x, t.v))
            predicted = L._sim(model, fit.coef, fit.mu[t.situation], kt)
            n = len(t.x)
            base += residual_code(actual[:n], w.sigma[0])+residual_code(actual[n:], w.sigma[1])
            residual += residual_code((actual-predicted)[:n], w.sigma[0])
            residual += residual_code((actual-predicted)[n:], w.sigma[1])
        return base, residual

    def admit(self, mind, wid, hyp, verdict, x, seconds, *, law_key=None):
        if type(verdict) is not Certification or not verdict.accepted:
            raise ValueError('Only outer acceptance discovers a law')
        w, concepts = self.worlds[wid], copy.deepcopy(mind.field.concept_table())
        surface_hyp = hyp
        hyp = expand(hyp, concepts) if w.form == 'exact' else hyp
        # A free curve is a hypothesis class, not one reusable function. Its
        # independently fitted coefficients must never unify by syntax alone.
        flexible = w.form == 'strengths' and verdict.kind == 'curve'
        kept_key = next((k for k, e in sorted(self.laws.items()) if w.form == 'strengths' and
                         e['form'] == w.form and e.get('transfer_hypothesis') == hyp), None)
        key = law_key or kept_key or digest((w.form, (w.tin, w.tout), hyp, verdict.kind,
                                (wid,) if flexible else ()))
        bits = (LG.bits(hyp, concepts) if w.form == 'exact' else mind.engine._bits(hyp, w.form, concepts))
        entry = self.laws.setdefault(key, dict(hypothesis=hyp, form=w.form,
            signature=(w.tin, w.tout), bits=bits, kind=verdict.kind, coverage={},
            certificates={}, features=x.copy(), concept_ids=[]))
        fresh = wid not in entry['coverage']
        if fresh:
            if w.form == 'exact' and hasattr(self, 'roadmap'):
                self.roadmap.reused(surface_hyp, wid)
            entry['certificates'][wid] = verdict
            # Measured outputs' literal code versus one law code plus a world
            # reference and residual, using only its own observations.
            base, residual = self.observation_code(mind, wid, hyp)
            entry['coverage'][wid] = (float(base), float(residual))
            mind.field.ideas.bind(('observed-world', wid), ('discovered-law', key), 1.)
            if w.form == 'exact':
                if any(LG.safe(hyp, {'x': v}, concepts) != y for v, y in self.observations[wid]):
                    raise ValueError('Outer exact acceptance contradicts own observation')
                view = self.view(wid)
                if len(view.examples) == 4:
                    receipt = Receipt.make(view, (hyp,), concepts, scope='exact-audit', origin='explore',
                        source='explore:'+wid, acceptance=(verdict.record, verdict.kind, verdict.bound))
                    receipt.check(concepts, reserved=mind.sleep.reserved, sources=mind.sleep.reserved_sources)
                    if receipt.id not in mind.sleep.consumed:
                        mind.checked_wake.add(receipt.id)
                        mind.sleep.admit(receipt, concepts)
                if mind.crutches['sleep_library'] and not entry['concept_ids']:
                    body = substitute(hyp, 'x', LG.node('var', payload='_'))
                    concept = mind.field.invent(body, (w.tin, w.tout),
                        'code' if LG.is_list(w.tin) else 'math', wid, LG.parts(body),
                        extra=dict(origin='explore', proof=dict(kind=verdict.kind, bound=verdict.bound,
                                                               record=verdict.record)))
                    entry['concept_ids'].append(concept['id'])
                    mind.engine._register(concept)
                    mind.proposer.changed()
            elif mind.crutches['sleep_library']:
                self._keep_physics(mind, wid, hyp, verdict, entry)
            self.pending = [r for r in self.pending if r['world'] != wid]
            if mind.crutches.get('taught_not_yet'):
                mind.field.revisit_queue = [r for r in mind.field.revisit_queue if r.get('discovery_world') != wid]
        if self.switches['unification_credit'] and fresh:
            self.policy.learn('unify', x, float(len(entry['coverage']) > 1), seconds)
        if not fresh:
            entry['certificates'][wid] = verdict
            entry['coverage'][wid] = self.observation_code(mind, wid, hyp)
        if fresh:
            # One outer certificate in one more world is one proof of the law, counted as every proof is (SERA-U keeps
            # standing in layer B's role counts; the legacy Field in its table). The compression credit stays this
            # module's search prior (reuse_credit), never a proof count.
            add_proof(mind.field, ('discovered-law', key))
            if getattr(mind, 'u14', {}).get('discovery_memory') and mind.proposer.memory is not None:
                # Open-world proof previously reached layer B/library replay,
                # but omitted the native audit-result experience used by live.
                mind.memory.event('audit-result', (hyp, True), progress=1.)
                mind.memory.refresh(self.view(wid))
        if hasattr(self, 'scientists'):
            self.scientists.admitted(mind, self, wid, key, fresh, seconds)
        if hasattr(mind, 'holes'):
            mind.holes.settle(mind, wid, key)
            mind.holes.raise_questions(mind, wid, key, surface_hyp)
        if getattr(mind, 'wiring', False):
            self.events.append(dict(seconds=0., admission_record=dict(law=key, world=wid,
                record=verdict.record, fresh=fresh, kind=verdict.kind)))
        return key, fresh

    def transfer(self, mind, pool, key, deadline):
        """Try one retained law on every compatible world it has already seen.

        No proof transfers by fiat: each world supplies its own outer check.
        A failed world opens an anomaly without erasing any other certificate.
        """
        entry, rows = self.laws[key], []
        for wid in sorted(self.worlds):
            if time.time() >= deadline:
                break
            w = self.worlds[wid]
            if (wid in entry['coverage'] or not self.observations[wid] or w.form != entry['form'] or
                    (w.tin, w.tout) != entry['signature']):
                continue
            # Transfer only a fixed drawing/formula, never refit a free curve
            # in another world and call it the same discovered law.
            hyp = entry.get('transfer_hypothesis', entry['hypothesis'])
            if w.form == 'strengths' and (any(p[1] == 'curve' for p in hyp) or
                    entry['kind'] == 'curve' and 'transfer_hypothesis' not in entry):
                continue
            x = self.candidate_features(mind, wid, hyp)
            inner = getattr(mind.field, 'inner', None) if mind.crutches.get('inner_judge') else None
            kind = 'discovery:'+w.form
            if inner is not None and not inner.decide(kind, hyp, x)[0]:
                continue
            started = time.perf_counter()
            verdict = pool.certify(wid, hyp, mind.field.concept_table(), tuple(self.observations[wid]),
                                   library=mind.field.shapes())
            if type(verdict) is not Certification:
                raise TypeError('Unsafe transfer judge result')
            self.checks += 1
            if inner is not None:
                inner.verdict(kind, hyp, x, verdict.accepted, source='proof')
            if verdict.accepted:
                self.admit(mind, wid, hyp, verdict, x, time.perf_counter()-started, law_key=key)
            else:
                self.anomaly(mind, wid, key, verdict)
                if self.switches['unification_credit']:
                    self.policy.learn('unify', x, -1., time.perf_counter()-started)
            rows.append(dict(world=wid, accepted=verdict.accepted, kind=verdict.kind,
                             record=verdict.record, bound=verdict.bound))
        return rows

    def _keep_physics(self, mind, wid, hyp, verdict, entry):
        """Keep certified shapes, and checked self-executions of those shapes.

        These receipts never assert that fitted force values were measured:
        their scope explicitly says accepted shape self-execution.
        """
        if 'transfer_hypothesis' in entry:
            return
        task = public_rail(self.worlds[wid], self.observations[wid])
        concepts = mind.field.concept_table()
        claim = task.claim_terms(hyp, concepts, mind.field.shapes(),
                                ramp=dict(verdict.bound).get('ramp', verdict.kind == 'formula'))
        if claim is None:
            return
        fam = claim[0]
        fit = task.ledger([fam]).mle(fam)
        if not fit.ok:
            return
        retained = []
        for part, (term, credit) in zip(hyp, claim[1]):
            if part[1] == 'concept':
                retained.append(part)
                continue
            # A curve certificate proves the fitted cell, not the expression
            # used to choose its coordinate (e.g. 1+x^3 must stay a curve).
            kept_part = (term[1], 'curve', term[2]) if credit == 'curve' else part
            c = mind.engine._invent_part(task, kept_part, fam, fit, concepts, task.context(),
                proof=dict(origin='explore', kind=credit, bound=verdict.bound, record=verdict.record))
            if c is None:
                continue
            entry['concept_ids'].append(c['id'])
            retained.append((c.get('argument_input', part[0]), 'concept', c['id']))
            concepts = mind.field.concept_table()
            p = LG.node('c', LG.node('var', payload='x'), payload=c['id'])
            xs = (-2., -.5, .5, 2.)
            try:
                ys = tuple(independent(p, {'x': v}, concepts) for v in xs)
                view = TaskView((('x', 'num'),), 'num', tuple(((('x', v),), y) for v, y in zip(xs, ys)))
                receipt = Receipt.make(view, (p,), concepts, scope='explore-shape', origin='explore',
                    source='explore-shape:'+wid+':'+str(c['id']),
                    acceptance=(verdict.record, credit, verdict.bound))
                mind.checked_wake.add(receipt.id)
                mind.sleep.admit(receipt, concepts)
            except ValueError:
                # A library shape can stand even if outside the replay port.
                continue
        if len(retained) == len(hyp):
            entry['transfer_hypothesis'] = tuple(retained)
            # A learned table costs its actual scalar payload once. Short
            # concept keys cannot make a large drawing free to transmit.
            if any(credit == 'curve' for _, credit in claim[1]):
                entry['bits'] += sum(32.*len(c['body'][1][1]) for c in mind.field.concepts
                                    if c['id'] in entry['concept_ids'] and c['body'][0] == 'tab')
        mind.proposer.changed()

    def rival_entropy(self, mind, wid):
        """Own-observation uncertainty; no held-out verdict or truth grade."""
        rivals = self.rivals[wid]
        if len(rivals) < 2:
            return 0.
        w, concepts = self.worlds[wid], mind.field.concept_table()
        if w.form == 'exact':
            scores = [-TS.MISS_NATS*sum(LG.safe(p, {'x': v}, concepts) != y
                       for v, y in self.observations[wid]) for p in rivals]
        else:
            task = public_rail(w, self.observations[wid])
            scores_by_law = task.evidence(rivals, concepts, mind.field.shapes(),
                                        self.quantity_values(wid) or task.first_masses())
            scores = [scores_by_law.get(p, -math.inf) for p in rivals]
        a = np.asarray(scores, float)
        if not np.isfinite(a).any():
            return math.log2(len(rivals))
        a = np.where(np.isfinite(a), a, -math.inf)
        weights = np.exp(a-np.max(a))
        weights /= weights.sum()
        return -sum(float(v)*math.log2(float(v)) for v in weights if v > 0)

    def tick(self, mind, pool, *, deadline=math.inf):
        """One checkpointable unit. Pool methods are never saved in the entity."""
        if not self.switches['open_worlds'] or time.time() >= deadline:
            return None
        started = time.perf_counter()
        work = getattr(mind, 'clock_mode', 'wall') == 'work'
        if work:
            mind.clock.charge('tick')
        from ccops5.core import grammar
        grammar.use_library(mind.field.shapes())
        self.register_worlds(pool.public())
        if not self.worlds:
            return None
        wid = self.active or sorted(self.worlds)[0]
        x = self.features(mind, self.view(wid))
        retired = getattr(getattr(mind, 'holes', None), 'retired', {}) if getattr(mind, 'u14', {}).get('retire_understood') else {}
        choices = ['visit:'+k for k in sorted(self.worlds) if k not in retired]
        if not choices:
            return None
        if self.active is not None and self.active not in retired:
            choices.append('stay')
        choice = self.policy.pick(choices, x, mind.numpy)
        if choice != 'stay':
            wid = choice[6:]
        self.active = wid
        w = self.worlds[wid]
        if mind.proposer.memory is not None:
            if getattr(mind, 'u14', {}).get('discovery_memory') and mind.crutches.get('memory_choice'):
                mind.memory.start_choice(self.view(wid), wall=math.inf if work else max(0., deadline-time.time()),
                                         phase='world', started=started)
            else:
                mind.memory.begin(self.view(wid))
        x = self.features(mind, self.view(wid))
        covered_before = sum(len(e['coverage']) for e in self.laws.values())
        row = dict(world=wid, origin='explore', search_and_retention=True,
                   experiment=None, certified=None, discovered=False, progress=0.)
        wiring = getattr(mind, 'wiring', False)
        if wiring:
            row['wiring'] = dict(observations=sum(map(len, self.observations.values())),
                floor_worlds=[k for k in sorted(self.worlds) if len(self.observations[k]) >=
                              (4 if self.worlds[k].form == 'exact' else 2)],
                proposals=0, candidates_audited=0, certified=0, admitted=0, habits={})
            before_habits = wiring_snapshot(mind)
        darwin = getattr(self, 'darwin', None)
        darwin_context, darwin_gain, watching = None, 0., False
        if darwin is not None:
            darwin_context = darwin.run(mind, self, wid, deadline=min(deadline,
                mind.clock.bound('darwin', mind) if work else time.time()+.1))
            watching = darwin_context[2]
            row['darwin_methods'] = darwin_context[0]
        if hasattr(pool, 'next_specimen'):
            incoming = pool.next_specimen(self)
            if incoming is not None:
                specimen_world, samples = incoming
                if specimen_world not in self.worlds:
                    raise ValueError('Specimen without a public body')
                for observation in samples:
                    observation = observed(observation)
                    body = self.worlds[specimen_world]
                    action = (('ask', observation[0]) if body.form == 'exact'
                              else ('push', observation[0], observation[1]))
                    forecast = darwin.forecast(mind, self, specimen_world, action) if darwin is not None else None
                    self.observations[specimen_world].append(observation)
                    if darwin is not None:
                        darwin_gain += darwin.receive(mind, self, specimen_world, action, observation, forecast)
                row['received_specimen'] = specimen_world
        scientists = getattr(self, 'scientists', None)
        if scientists is not None:
            science_record_start = scientists.records()
            science_chosen, science_moment, science_results, science_chase = scientists.run(
                mind, self, pool, wid, deadline=deadline)
            # Persistence is allowed to move focus before this item's search.
            wid = self.active
            w = self.worlds[wid]
            x = self.features(mind, self.view(wid))
            row['world'] = wid
            row['scientist_methods'] = science_results
        einstein = getattr(self, 'einstein', None)
        if einstein is not None:
            previous_laws = set(self.laws)
            record_start = dict(predictions=len(einstein.predictions), revisions=len(einstein.revisions),
                paradoxes={k: len(p['experiments']) for k, p in einstein.paradoxes.items()},
                principles={k: digest((p['laws'], p['standing'], p['credit'])) for k, p in einstein.principles.items()})
            chosen, moment, outcomes = einstein.run(mind, self, pool, wid, deadline=deadline)
            row['einstein_methods'] = outcomes
        roadmap = getattr(self, 'roadmap', None)
        roadmap_context, rough_plan, estimate_id, estimate_gain = None, None, None, 0.
        if roadmap is not None:
            roadmap_context = roadmap.run(mind, self, pool, wid, deadline=min(deadline,
                mind.clock.bound('roadmap', mind) if work else time.time()+.35))
            row['roadmap_methods'] = roadmap_context[0]
            if ('rough_estimates',) in roadmap_context[0] and roadmap.switches['rough_estimates']:
                rough_plan, _ = self.choose_experiment(self.experiment_menu(mind, wid), x, mind.numpy)
                if rough_plan is not None:
                    estimate_id = roadmap.predict(mind, self, wid, rough_plan['action'])
                    row['rough_estimate'] = estimate_id
        count = len(self.observations[wid])
        if getattr(mind, 'u14', {}).get('observe_to_floor') and count < (4 if w.form == 'exact' else 2):
            floor_choice = self.policy.pick(('observe-to-floor', 'continue'), x, mind.numpy)
            if floor_choice == 'observe-to-floor':
                while count < (4 if w.form == 'exact' else 2) and time.time() < deadline:
                    menu = self.experiment_menu(mind, wid)
                    experiment, _ = self.choose_experiment(menu, x, mind.numpy)
                    if experiment is None:
                        break
                    action = experiment['action']
                    self.observations[wid].append(observed(pool.act(wid, action)))
                    if work:
                        mind.clock.charge('act')
                    self.experiments += 1
                    count += 1
                self.policy.learn(floor_choice, x, float(count >= (4 if w.form == 'exact' else 2)),
                                  max(1, count) if work else time.perf_counter()-started)
        question_choice = None
        if self.switches['own_questions'] and (self.rivals[wid] or self.surprises[wid] or
                                               any(r['world'] == wid for r in self.pending)):
            question_choice = self.policy.pick(('question', 'observe'), x, mind.numpy)
        if question_choice == 'question':
            from .sleep import sample_input
            reason = ('anomaly' if any(r['world'] == wid for r in self.pending) else
                      'surprise' if self.surprises[wid] else 'committee')
            queries = tuple(sample_input(w.tin, mind.random) for _ in range(4)) if w.form == 'exact' else ()
            q = self.own_question(wid, reason, queries)
            # This self-made view conditions both the Field and language search.
            x = self.features(mind, q.view)
            row['question'] = q.view.identity
        if not watching and count >= (4 if w.form == 'exact' else 2) and time.time() < deadline:
            if wiring:
                row['wiring']['proposals'] += 1
            proposal_start = time.perf_counter()
            proposal_bound = min(deadline, mind.clock.bound('proposal:'+wid, mind) if work else time.time()+.5)
            self.rivals[wid] = self.propose(mind, wid, proposal_bound)
            if work:
                fit = any(all(LG.safe(p, {'x': v}, mind.field.concept_table()) == y
                    for v, y in self.observations[wid]) for p in self.rivals[wid]) if w.form == 'exact' else bool(self.rivals[wid])
                mind.clock.finish('proposal:'+wid, mind, time.perf_counter()-proposal_start, float(fit))
            self.levels[wid] = (self.levels[wid]+1 if work else min(3, self.levels[wid]+1))
            if roadmap is not None and w.form == 'exact' and not any(all(
                    LG.safe(p, {'x': value}, mind.field.concept_table()) == y
                    for value, y in self.observations[wid]) for p in self.rivals[wid]):
                roadmap.wish((w.tin, w.tout), wid)
        rivals = self.rivals[wid]
        if question_choice == 'question':
            checks = ()
            if mind.crutches.get('gap_syndromes') and w.form == 'exact':
                checks = self.syndromes(mind, q.view, rivals)
            row['question'] = q.view.identity
        estimate_trial = None
        audit_candidates = rivals if work else rivals[:2]
        if roadmap is not None and not watching and estimate_id is not None:
            ordered, estimate_trial = roadmap.order(mind, self, wid, audit_candidates)
            # Original first two remain the unchanged, unpruned fallback.
            audit_candidates = tuple(dict.fromkeys(ordered[:2]+rivals[:2]))
        for hyp in (() if watching else audit_candidates):
            if time.time() >= deadline:
                break
            concepts = mind.field.concept_table()
            if w.form == 'exact' and any(LG.safe(hyp, {'x': v}, concepts) != y for v, y in self.observations[wid]):
                continue
            trial = (wid, digest(hyp), digest(self.observations[wid]))
            if trial in self.tried:
                continue
            features = self.candidate_features(mind, wid, hyp)
            # Calibrated inner veto; absence of U3 is a neutral try, never credit.
            kind = 'discovery:'+w.form
            inner = getattr(mind.field, 'inner', None) if mind.crutches.get('inner_judge') else None
            if inner is not None and not inner.decide(kind, hyp, features)[0]:
                continue
            self.tried[trial] = True
            self.checks += 1
            verdict = pool.certify(wid, hyp, concepts, tuple(self.observations[wid]), library=mind.field.shapes())
            if wiring:
                row['wiring']['candidates_audited'] += 1
                row['wiring']['certified'] += int(verdict.accepted)
            if type(verdict) is not Certification:
                raise TypeError('Unsafe judge result')
            if roadmap is not None:
                roadmap.checked(estimate_trial, hyp, verdict)
            if inner is not None:
                inner.verdict(kind, hyp, features, verdict.accepted, source='proof')
            if einstein is not None:
                einstein.checked(wid, hyp, verdict.accepted)
            row['certified'] = dict(accepted=verdict.accepted, kind=verdict.kind,
                                    bound=verdict.bound, record=verdict.record)
            if verdict.accepted:
                old_laws = len(self.laws)
                key, fresh = self.admit(mind, wid, hyp, verdict, x, time.perf_counter()-started)
                if wiring:
                    row['wiring']['admitted'] += int(fresh)
                row.update(law=key, discovered=len(self.laws) > old_laws,
                           reused=fresh and len(self.laws[key]['coverage']) > 1)
                if len(self.laws) > old_laws:
                    row['transfer'] = self.transfer(mind, pool, key, deadline)
                break
            for key in sorted(self.laws):
                if self.laws[key]['hypothesis'] == hyp:
                    self.anomaly(mind, wid, key, verdict)
        if time.time() < deadline:
            menu = self.experiment_menu(mind, wid)
            target = einstein.target(self, wid) if einstein is not None else None
            if rough_plan is not None and estimate_id is not None:
                experiment, route = rough_plan, 'random'
            elif target is not None:
                experiment, route = target, 'split'
            elif (scientists is not None and scientists.switches['one_change_experiments']
                    and ('one_change_experiments',) in science_chosen):
                experiment, route = scientists.choose_experiment(self, menu, wid, x, mind.numpy, mind.field.concept_table())
            else:
                experiment, route = self.choose_experiment(menu, x, mind.numpy)
            if experiment is not None:
                previous_rivals = len(rivals)
                entropy = self.rival_entropy(mind, wid) if w.form == 'strengths' else 0.
                action = experiment['action']
                prediction_id = (einstein.predict(mind, self, wid, action)
                    if einstein is not None and ('bold_predictions',) in chosen else None)
                forecast = darwin.forecast(mind, self, wid, action) if darwin is not None else None
                observation = observed(pool.act(wid, action))
                if work:
                    mind.clock.charge('act')
                if roadmap is not None and estimate_id is not None:
                    estimate_gain = roadmap.settle(estimate_id, observation)
                if w.form == 'exact':
                    if observation[0] != action[1]:
                        raise ValueError('World answered an input SERA did not choose')
                    surprise = float(experiment['predicted'] is not None and experiment['predicted'] != observation[1])
                    concepts = mind.field.concept_table()
                    self.rivals[wid] = tuple(p for p in rivals if LG.safe(p, {'x': observation[0]}, concepts) == observation[1])
                else:
                    if observation[:2] != action[1:]:
                        raise ValueError('World observed a push SERA did not choose')
                    y = np.array(observation[2]+observation[3])
                    prediction = experiment['predicted']
                    scales = np.r_[np.full(len(observation[2]), w.sigma[0]),
                                   np.full(len(observation[3]), w.sigma[1])]
                    surprise = (float(np.sqrt(np.mean(((y-np.array(prediction))/scales)**2)))
                                if prediction is not None else 0.)
                if einstein is not None:
                    einstein.confirm(mind, self, wid, action, observation)
                    prediction_gain = einstein.settle(mind, self, prediction_id, observation)
                    row['bold_prediction'] = prediction_id
                    row['prediction_gain'] = prediction_gain
                if scientists is not None:
                    scientists.meet(self, wid, action, observation)
                    row['experiment_option'] = route
                    if 'anchor' in experiment:
                        row['one_change_anchor'] = experiment['anchor']
                self.observations[wid].append(observation)
                if darwin is not None:
                    darwin_gain += darwin.receive(mind, self, wid, action, observation, forecast)
                if mind.proposer.memory is not None:
                    mind.memory.refresh(self.view(wid))
                self.surprises[wid] = surprise
                if surprise and hasattr(mind, 'holes'):
                    mind.holes.anomaly(mind, wid)
                self.experiments += 1
                row['experiment'] = action
                gain = ((previous_rivals-len(self.rivals[wid]))/max(1, previous_rivals)
                        if w.form == 'exact' else
                        max(0., entropy-self.rival_entropy(mind, wid))/max(1., entropy))
                row['progress'] = gain
                if self.switches['designed_experiments'] or route == 'one-change':
                    self.policy.learn(route, x, gain, time.perf_counter()-started)
                if surprise and self.switches['own_questions'] and question_choice == 'question':
                    self.own_question(wid, 'surprise')
                if w.form == 'strengths' and len(self.observations[wid]) >= 2:
                    row['quantity'] = self.fit_quantity(mind, wid, x)
        row['seconds'] = time.perf_counter()-started
        if hasattr(mind, 'holes'):
            row['learning_progress'] = mind.holes.visit(mind, wid)
            row['progress'] += row['learning_progress']
            row['holes'] = mind.holes.report(mind)
        if work:
            row.update(work=row['seconds'], cost_unit='work')
        gain = float(sum(len(e['coverage']) for e in self.laws.values())-covered_before)+row['progress']
        self.policy.learn(choice, x, gain, row['seconds'])
        if question_choice is not None:
            self.policy.learn(question_choice, x, gain, row['seconds'])
        if einstein is not None:
            doubt_removed = max(0., moment['doubt']-self.rival_entropy(mind, wid))
            certification_gain = float(sum(len(e['coverage']) for e in self.laws.values())-covered_before)
            einstein.feedback(chosen, moment, doubt_removed+certification_gain+row.get('prediction_gain', 0.), row['seconds'])
            row['einstein_doubt_removed'] = doubt_removed
            row['einstein_law_kinds'] = [self.laws[k]['kind'] for k in sorted(set(self.laws)-previous_laws)]
            row['einstein'] = einstein.report()
            # Store deltas, not a growing full history at every tick.
            row['einstein_records'] = copy.deepcopy(dict(
                paradoxes={k: p for k, p in einstein.paradoxes.items()
                           if record_start['paradoxes'].get(k) != len(p['experiments'])},
                principles={k: p for k, p in einstein.principles.items()
                            if record_start['principles'].get(k) != digest((p['laws'], p['standing'], p['credit']))},
                revisions=einstein.revisions[record_start['revisions']:],
                predictions=einstein.predictions[record_start['predictions']:]))
        if scientists is not None:
            scientists.feedback(self, science_chosen, science_moment, science_results, row, science_chase)

            row['scientists'] = scientists.report()
            row['scientist_records'] = scientists.records_delta(science_record_start)
        if darwin is not None:
            darwin.feedback(mind, self, darwin_context, row, darwin_gain)
            row['darwin'] = darwin.report(mind.field)
            charged = time.perf_counter()-started
            darwin.costs['real'] += max(0., charged-row['seconds'])
            row['seconds'] = charged
            row['darwin']['seconds'] = dict(darwin.costs)
        if roadmap is not None:
            roadmap.feedback(roadmap_context, row, estimate_gain)
            if estimate_trial is not None and not estimate_trial['solved']:
                if time.time() >= deadline:
                    roadmap.pruning_counts['censored_fallbacks'] += 1
                roadmap.estimate_choice.learn(estimate_trial['method'], estimate_trial['feature'], -.05, 1.)
            row['roadmap'] = roadmap.report()
        row['experiments_total'] = self.experiments
        if getattr(mind, 'u14', {}).get('discovery_memory') and mind.proposer.memory is not None and mind.memory.choice_on:
            row['discovery_memory'] = mind.memory.finish_choice(self.view(wid), right=bool(
                row.get('certified') and row['certified']['accepted']))
        if wiring:
            after_habits = wiring_snapshot(mind)
            row['wiring']['observations'] = sum(map(len, self.observations.values()))
            row['wiring']['floor_worlds'] = [k for k in sorted(self.worlds) if len(self.observations[k]) >=
                                            (4 if self.worlds[k].form == 'exact' else 2)]
            for name in sorted(after_habits):
                received, outputs = after_habits[name]
                old = before_habits.get(name, ([], []))[1]
                row['wiring']['habits'][name] = dict(received=received,
                    outputs=[k for k in outputs if k not in old])
        self.events.append(row)
        return row


def einstein_records(rows):
    result = dict(paradoxes={}, principles={}, revisions=[], predictions=[])
    for row in rows:
        record = row.get('einstein_records', {})
        result['paradoxes'].update(record.get('paradoxes', {}))
        result['principles'].update(record.get('principles', {}))
        result['revisions'].extend(record.get('revisions', ()))
        result['predictions'].extend(record.get('predictions', ()))
    return result


def generation_report(rows):
    discoveries = [r for r in rows if r.get('discovered')]
    seconds = sum(r['seconds'] for r in rows)
    experiments = sum(r.get('experiment') is not None for r in rows)
    kinds = {k: sum(r['certified']['kind'] == k for r in discoveries) for k in ('curve', 'drawing', 'formula')}
    n = len(discoveries)
    if any('einstein_law_kinds' in r for r in rows):
        accepted = [kind for r in rows for kind in r.get('einstein_law_kinds', ())]
        kinds = {kind: accepted.count(kind) for kind in ('curve', 'drawing', 'formula')}
        n = len(accepted)
    result = dict(laws=n, by_kind=kinds, seconds=seconds, experiments=experiments,
                seconds_per_law=seconds/n if n else None, experiments_per_law=experiments/n if n else None,
                reuse=sum(bool(r.get('reused'))+sum(t['accepted'] for t in r.get('transfer', ())) for r in rows),
                credit='compression credit, not proof of truth; rediscovery of laws we hid')
    if any('admission_record' in row for row in rows):
        result['admission_records'] = [row['admission_record'] for row in rows if 'admission_record' in row]
    if any('wiring' in row for row in rows):
        result['wiring'] = wiring_report(rows)
    latest = next((r for r in reversed(rows) if 'einstein' in r), None)
    if latest is not None:
        result['einstein'] = copy.deepcopy(latest['einstein'])
        result['einstein_records'] = copy.deepcopy(einstein_records(rows))
    latest_science = next((r for r in reversed(rows) if 'scientists' in r), None)
    if latest_science is not None:
        result['scientists'] = copy.deepcopy(latest_science['scientists'])
        result['scientist_records'] = scientist_records(rows)
    latest_darwin = next((row for row in reversed(rows) if 'darwin' in row), None)
    if latest_darwin is not None:
        result['darwin'] = copy.deepcopy(latest_darwin['darwin'])
    latest_roadmap = next((row for row in reversed(rows) if 'roadmap' in row), None)
    if latest_roadmap is not None:
        result['roadmap'] = copy.deepcopy(latest_roadmap['roadmap'])
    latest_holes = next((row for row in reversed(rows) if 'holes' in row), None)
    if latest_holes is not None:
        result['holes'] = copy.deepcopy(latest_holes['holes'])
    return result


def wiring_snapshot(mind):
    """Observer diagnostics of actual retained references, never policy inputs.

    Merely enabling a habit is not evidence that it consumed a law. Empty
    references and outputs remain empty, including unmet method prerequisites.
    """
    d, result = mind.discovery, {}
    if hasattr(d, 'einstein'):
        e = d.einstein
        result['einstein'] = (sorted({k for p in e.predictions for k in (p['law'],)} |
            {k for p in e.principles.values() for k in p['laws']} |
            {k for p in e.paradoxes.values() for k in p['laws']} |
            {k for p in e.doubts.values() for k in p['laws']}),
            sorted(['prediction:'+p['id'] for p in e.predictions] +
                   ['principle:'+k for k in e.principles] + ['paradox:'+k for k in e.paradoxes]))
    if hasattr(d, 'scientists'):
        s = d.scientists
        result['scientists'] = (sorted({c['anomaly'] for c in s.chases.values()
            if isinstance(c['anomaly'], str)} | {c['explained_by'] for c in s.chases.values()
            if c['explained_by'] is not None}),
            sorted(['chase:'+k for k in s.chases] + ['relation:'+k for k in s.relations] +
                   ['conserved:'+k for k in s.conserved] + ['gap:'+p['id'] for p in s.predictions]))
    if hasattr(d, 'darwin'):
        atlas = mind.field.hologram
        hops = getattr(d, '_wiring_hops', {})
        result['darwin'] = (sorted({k for name in ('world_hologram', 'lineage_trees')
                                   for k in hops.get(name, {}).get('received', ())}),
                            sorted(['tree:'+k for k in atlas['trees']]))
    if hasattr(d, 'roadmap'):
        r = d.roadmap
        received = sorted(k for k, law in d.laws.items() if any(cid in
            {p[1] for p in LG.parts(law['hypothesis']) if p[0] == 'concept'} or
            cid in law['concept_ids'] for cid in (v['original'] for v in r.rebuilds.values())))
        result['roadmap'] = (received, sorted(['rebuild:'+k for k in r.rebuilds] +
                                              ['operation:'+k for k in r.operations]))
    if hasattr(mind.field, 'curiosity'):
        result['curiosity'] = ([], sorted(mind.field.curiosity.found))
    result['memory'] = (sorted(k for k, law in d.laws.items() if any(
        receipt.acceptance and receipt.acceptance[0] in
        {v.record for v in law['certificates'].values()} for receipt, _ in mind.sleep.replay)),
        sorted(receipt.id for receipt, _ in mind.sleep.replay))
    if hasattr(mind, 'holes'):
        result['holes'] = (sorted({q['law'] for q in mind.holes.questions.values()}),
                           sorted(mind.holes.questions))
    for name, hop in sorted(getattr(d, '_wiring_hops', {}).items()):
        result[name] = (sorted(hop['received']), sorted(hop['outputs']))
    for owner, names in (('einstein', ('thought_experiments', 'symmetry_principles', 'doubt_assumptions', 'bold_predictions')),
                         ('scientists', ('one_change_experiments', 'gap_predictions', 'number_conjectures', 'conserved_quantities', 'anomaly_pursuit')),
                         ('darwin', ('lineage_trees',)), ('roadmap', ('rederive_concepts',))):
        if hasattr(d, owner):
            for name in names:
                if getattr(d, owner).switches.get(name):
                    result.setdefault(name, ([], []))
    if hasattr(mind, 'holes'):
        for reason, enabled in mind.holes.switches.items():
            if enabled:
                result.setdefault('holes_'+reason, ([], []))
    return result


def wiring_report(rows):
    records = [r['wiring'] for r in rows if 'wiring' in r]
    result = {k: sum(r.get(k, 0) for r in records) for k in
              ('proposals', 'candidates_audited', 'certified', 'admitted')}
    result.update(observations=records[-1]['observations'] if records else 0,
                  floor_worlds=records[-1]['floor_worlds'] if records else [], habits={})
    if any('wiring_proposal' in r for r in rows):
        result['proposals'] = sum('wiring_proposal' in r for r in rows)
    hops = [r['wiring_hop'] for r in rows if 'wiring_hop' in r]
    for name in sorted({name for r in records for name in r['habits']} | {r['habit'] for r in hops}):
        result['habits'][name] = {key: sorted({v for r in records
            for v in r['habits'].get(name, {}).get(key, [])} |
            {v for r in hops if r['habit'] == name for v in r[key]}, key=repr)
            for key in ('received', 'outputs')}
    return result


def scientist_records(rows):
    """Combine changed records; append chase attempts and experiment histories."""
    result = dict(families={}, predictions={}, relations={}, conserved={}, chases={}, experiment_origins={})
    for row in rows:
        record = row.get('scientist_records', {})
        for group in ('families', 'relations', 'conserved'):
            result[group].update(copy.deepcopy(record.get(group, {})))
        predictions = record.get('predictions', {})
        if isinstance(predictions, list):
            predictions = {p['id']: p for p in predictions}
        result['predictions'].update(copy.deepcopy(predictions))
        for key, value in record.get('chases', {}).items():
            old = result['chases'].get(key, {})
            result['chases'][key] = {**copy.deepcopy(value),
                'attempts': old.get('attempts', [])+copy.deepcopy(value.get('attempts', [])),
                'gains': old.get('gains', [])+copy.deepcopy(value.get('gains', []))}
        for key, values in record.get('experiment_origins', {}).items():
            result['experiment_origins'].setdefault(key, []).extend(copy.deepcopy(values))
    return result
