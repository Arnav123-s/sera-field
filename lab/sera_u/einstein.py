"""U10: fallible habits over acquired programs, never supplied world laws.

All transformations are executable acquired concepts with observed inverses.
Principle standing and prediction credit are search evidence, never proof.
The bounded shared-structure revision order is not a guarantee of discovery.
"""
import itertools
import time

import numpy as np

from sera import lang as LG, phi as PH
from .discovery import Certification
from .ports import digest, observed

CRUTCHES = ('thought_experiments', 'symmetry_principles',
            'doubt_assumptions', 'bold_predictions')
# Same teaching schedule as U5. These are evidence weights, not law content.
PHASE_WEIGHTS = dict(lesson=1., study=.6, rsi=.4, test1=.25, test2=.1, test3=0.)


def prediction_record(pid, world, action, law, predicted, principles=()):
    """Prospective record shared by U10 value and U11 member predictions."""
    return dict(id=pid, world=world, action=action, law=law, principles=principles,
                predicted=observed(predicted), result=None, confirmed=None,
                recorded_at=time.time(), performed_at=None)


class EinsteinMethods(PH.FieldMethods):
    """SERA-U-only extension; the lab MOVES and Sera.one are untouched."""
    def __init__(self, switches):
        super().__init__()
        self.switches = dict(switches)

    def candidates(self):
        return [('observe',)] + [(k,) for k in CRUTCHES if self.switches[k]]

    def demonstrate(self, shown, moment, *, phase, origin):
        if origin != 'taught' or phase not in ('lesson', 'study', 'test1'):
            raise ValueError('No demonstrations on rediscovery or assessment worlds')
        if not self.switches.get(shown, False):
            return False
        x = self.features(moment)
        a, b = self.taught.setdefault(('discovery', (shown,)),
            [np.zeros((self.d, self.d)), np.zeros(self.d)])
        weight = PHASE_WEIGHTS[phase]
        a += weight*np.outer(x, x)/self.noise**2
        b += weight*x/self.noise**2
        return True


def nodes(program):
    out = [program]
    for child in program[2:]:
        out.extend(nodes(child))
    return tuple(out)


def replace_part(program, part, replacement):
    if program == part:
        return replacement
    return program[:2] + tuple(replace_part(c, part, replacement) for c in program[2:])


def value(program, x, concepts):
    return LG.safe(program, {'x': x}, concepts)


def imagined_inputs(rows, typ):
    """Limits/extremes are extrapolations of observed material, not symmetries."""
    seen = [x for x, _ in rows]
    out = list(seen)
    if typ == 'num':
        for x in seen:
            if type(x) is int:
                out.extend((0, -x, max(-LG.MAX_INT, min(LG.MAX_INT, 2*x)),
                            max(-LG.MAX_INT, min(LG.MAX_INT, 4*x))))
    else:
        for x in seen:
            if isinstance(x, tuple):
                out.extend(((), x[:1], (x+x)[:LG.MAX_LEN]))
                if x:
                    out.append(tuple(x[0] for _ in range(min(LG.MAX_LEN, 2*len(x)))))
    return tuple(sorted(set(out), key=repr))[:64]


class Einstein:
    def __init__(self, switches):
        if set(switches) != set(CRUTCHES) or any(type(v) is not bool for v in switches.values()):
            raise ValueError('Declare all four boolean U10 switches')
        self.switches = dict(switches)
        self.methods = EinsteinMethods(switches)
        self.paradoxes, self.principles, self.doubts = {}, {}, {}
        self.predictions, self.revisions, self.events = [], [], []
        self.law_credit, self.principle_credit = {}, {}
        self.targets, self.attempted, self.questioned = {}, set(), set()
        self.teacher_shown = False
        self.search = dict(principled=0, reordered=0, ordered_search_audits=0, accepted_baseline_ranks=0)
        self.ranks = {}
        self.phase_weight = 1.

    def demonstrate(self, mind, view, *, phase, origin):
        if origin != 'taught' or phase not in ('lesson', 'study', 'test1'):
            raise ValueError('No demonstrations on rediscovery or assessment worlds')
        reads = mind.engine._u_reads([view])[0][0].detach().cpu().numpy()
        self.methods.bind(reads)
        moment = dict(doubt=1., misfit=0., proven=len(mind.field.concepts))
        shown = []
        for name in CRUTCHES:
            if self.methods.demonstrate(name, moment, phase=phase, origin=origin):
                shown.append(name)
        self.teacher_shown = True
        return tuple(shown)

    def phase(self, name):
        weight = PHASE_WEIGHTS[name]
        ratio = weight/self.phase_weight if self.phase_weight else 0.
        for a, b in self.methods.taught.values():
            a *= ratio
            b *= ratio
        self.phase_weight = weight

    def learning_state(self):
        # Raw timestamps/costs are audit annotations only, including nested ones.
        methods = {k: v for k, v in self.methods.__dict__.items()}
        return dict(**({'conservation_principles': self.conservation_principles}
                       if hasattr(self, 'conservation_principles') else {}),
            switches=self.switches, methods=methods, paradoxes=self.paradoxes,
            principles=self.principles, doubts=self.doubts, revisions=self.revisions,
            predictions=[{k: v for k, v in p.items() if k not in ('recorded_at', 'performed_at')}
                         for p in self.predictions], law_credit=self.law_credit,
            principle_credit=self.principle_credit, targets=self.targets,
            attempted=sorted(self.attempted, key=repr), questioned=sorted(self.questioned),
            teacher_shown=self.teacher_shown, search=self.search,
            ranks=self.ranks, phase_weight=self.phase_weight)

    def compatible(self, discovery, wid):
        w = discovery.worlds[wid]
        return [(k, e) for k, e in sorted(discovery.laws.items())
                if e['form'] == w.form and e['signature'] == (w.tin, w.tout)][:16]

    def transforms(self, discovery, wid, concepts):
        """No sign/scale/reverse menu: acquired programs must undo one another.

        An acquired reverse or sign flip can qualify as its own inverse. The
        same test admits any other acquired bijection on these observations.
        This is finite empirical evidence, not a theorem of invertibility.
        """
        w = discovery.worlds[wid]
        if w.form != 'exact':
            return ()
        xs = tuple(sorted({x for x, _ in discovery.observations[wid]}, key=repr))
        if len(xs) < 2:
            return ()
        ids = sorted(k for k, sig in concepts.get('_sig', {}).items()
                     if k in concepts and LG.fits(tuple(sig), w.tin, w.tin))
        transforms = []
        arg = LG.node('var', payload='x')
        for a in ids[:32]:
            p = LG.node('c', arg, payload=a)
            ys = [value(p, x, concepts) for x in xs]
            if any(y is None for y in ys) or all(x == y for x, y in zip(xs, ys)):
                continue
            for b in ids[:32]:
                inverse = LG.node('c', arg, payload=b)
                if all(value(inverse, y, concepts) == x and
                       value(p, value(inverse, x, concepts), concepts) == x
                       for x, y in zip(xs, ys)):
                    transforms.append(dict(key=digest((p, inverse)), program=p,
                                           inverse=inverse, signature=w.tin, evidence=xs))
        return tuple(transforms)

    @staticmethod
    def keeps(program, transform, xs, concepts):
        tested = 0
        for x in xs:
            tx = value(transform['program'], x, concepts)
            y, ty = value(program, x, concepts), value(program, tx, concepts)
            if tx is None or y is None or ty is None or y != ty:
                return False
            tested += 1
        return tested >= 2

    def invariance(self, mind, discovery, wid):
        if not self.switches['symmetry_principles'] or discovery.worlds[wid].form != 'exact':
            return 0
        concepts = mind.field.concept_table()
        laws = self.compatible(discovery, wid)
        xs = imagined_inputs(discovery.observations[wid], discovery.worlds[wid].tin)
        discovery.trace('symmetry_principles', [k for k, _ in laws])
        fresh = 0
        for transform in self.transforms(discovery, wid, concepts):
            supporters = sorted(k for k, e in laws if self.keeps(e['hypothesis'], transform, xs, concepts))
            key = transform['key']
            entry = self.principles.get(key)
            if entry is not None:
                entry['laws'] = supporters
                entry['standing'] = len(supporters)
            if len(supporters) < 2:
                continue
            if entry is None:
                # A learned concept/key in the Field, separate from executable
                # library proofs: empirical principle support never certifies it.
                entry = dict(key=('principle', key), transform=transform,
                             laws=[], standing=0, credit=0., status='fallible')
                self.principles[key] = entry
                fresh += 1
            entry['laws'] = supporters
            entry['standing'] = len(entry['laws'])
            discovery.trace('symmetry_principles', supporters, ['principle:'+key])
            for law in supporters:
                mind.field.ideas.bind(('discovered-law', law), entry['key'], 1.)
        return fresh

    def priority(self, mind, discovery, wid, program):
        if not self.switches['symmetry_principles'] or discovery.worlds[wid].form != 'exact':
            return 0.
        xs = imagined_inputs(discovery.observations[wid], discovery.worlds[wid].tin)
        concepts = mind.field.concept_table()
        score = 0.
        for key, principle in sorted(self.principles.items()):
            if principle['transform']['signature'] != discovery.worlds[wid].tin:
                continue
            if self.keeps(program, principle['transform'], xs, concepts):
                score += principle['standing'] + principle['credit']
            else:
                token = digest((wid, key, program))
                if token not in self.questioned:
                    self.questioned.add(token)
                    if discovery.switches['own_questions']:
                        discovery.own_question(wid, 'principle', xs[:4])
        return score

    def order(self, mind, discovery, wid, programs):
        if not self.switches['symmetry_principles'] and not self.switches['bold_predictions']:
            return programs
        before = tuple(programs)
        def bonus(p):
            prediction = sum(self.law_credit.get(k, 0.) for k, e in self.compatible(discovery, wid)
                             if e['hypothesis'] == p) if self.switches['bold_predictions'] else 0.
            return self.priority(mind, discovery, wid, p) + prediction
        result = tuple(sorted(before, key=lambda p: -bonus(p)))
        if self.principles and discovery.worlds[wid].form == 'exact':
            self.search['principled'] += 1
            self.search['reordered'] += int(result != before)
            self.ranks[wid] = {digest(p): (before.index(p)+1, j+1) for j, p in enumerate(result)}
        return result

    def checked(self, wid, hyp, accepted):
        if self.switches['symmetry_principles'] and wid in self.ranks:
            self.search['ordered_search_audits'] += 1
            if accepted:
                baseline, ordered = self.ranks[wid].get(digest(hyp), (0, 0))
                self.search['accepted_baseline_ranks'] += baseline
                self.search.setdefault('accepted_ordered_ranks', 0)
                self.search['accepted_ordered_ranks'] += ordered

    def thought(self, mind, discovery, wid):
        """Pure imagination: no pool argument, act, certify or judge call."""
        if not self.switches['thought_experiments'] or discovery.worlds[wid].form != 'exact':
            return ()
        concepts = mind.field.concept_table()
        laws = self.compatible(discovery, wid)
        xs = imagined_inputs(discovery.observations[wid], discovery.worlds[wid].tin)
        found = []
        for (ka, a), (kb, b) in itertools.combinations(laws, 2):
            for x in xs:
                ya, yb = value(a['hypothesis'], x, concepts), value(b['hypothesis'], x, concepts)
                if ya is not None and yb is not None and ya != yb:
                    found.append(self.paradox(discovery, wid, (ka, kb), x, (ya, yb)))
                    break
        if self.switches['symmetry_principles']:
            for ka, a in laws:
                for pk, principle in sorted(self.principles.items()):
                    t = principle['transform']
                    if t['signature'] != discovery.worlds[wid].tin:
                        continue
                    for x in xs:
                        tx = value(t['program'], x, concepts)
                        ya, yb = value(a['hypothesis'], x, concepts), value(a['hypothesis'], tx, concepts)
                        if tx is not None and ya is not None and yb is not None and ya != yb:
                            found.append(self.paradox(discovery, wid, (ka,), x, (ya, yb), principle=pk, other=tx))
                            break
        return tuple(found)

    def paradox(self, discovery, wid, laws, x, predictions, *, principle=None, other=None):
        key = digest((wid, laws, x, principle, other))
        if key not in self.paradoxes:
            self.paradoxes[key] = dict(id=key, world=wid, laws=tuple(laws), input=x,
                predictions=tuple(predictions), principle=principle, other=other,
                confirmed=None, experiments=[], results={})
            if discovery.switches['own_questions']:
                discovery.own_question(wid, 'paradox', (x,) if other is None else (x, other))
            self.targets.setdefault(wid, []).append(key)
        return key

    def target(self, discovery, wid):
        if not self.switches['thought_experiments'] or not discovery.switches['designed_experiments']:
            return None
        for key in self.targets.get(wid, ()):
            p = self.paradoxes[key]
            for x in ((p['input'],) if p['other'] is None else (p['input'], p['other'])):
                if repr(x) not in p['results']:
                    return dict(action=('ask', x), predicted=p['predictions'][0],
                                info=1., surprise=0., paradox=key)
        return None

    def confirm(self, mind, discovery, wid, action, observation):
        if not self.switches['thought_experiments']:
            return
        for key in self.targets.get(wid, ()):
            p = self.paradoxes[key]
            if action[1] not in (p['input'], p['other']):
                continue
            p['experiments'].append((discovery.experiments+1, action, observation))
            p['results'][repr(action[1])] = observation[1]
            if p['other'] is None:
                # Real data establish a local failure of at least one law.
                # They cannot prove two true laws in one body simultaneously.
                p['confirmed'] = any(observation[1] != y for y in p['predictions'])
            elif all(repr(x) in p['results'] for x in (p['input'], p['other'])):
                p['confirmed'] = p['results'][repr(p['input'])] != p['results'][repr(p['other'])]
            if p['confirmed'] and self.switches['doubt_assumptions']:
                self.doubt(discovery, wid, p['laws'], source=key)

    def doubt(self, discovery, wid, laws, *, source):
        if not self.switches['doubt_assumptions']:
            return None
        compatible = dict(self.compatible(discovery, wid))
        laws = tuple(sorted(k for k in laws if k in compatible))
        discovery.trace('doubt_assumptions', laws)
        if len(laws) < 2:
            others = [k for k in sorted(compatible) if k not in laws]
            laws = tuple(sorted(set(laws) | set(others[:2-len(laws)])))
        if len(laws) < 2:
            key = digest((wid, laws, source))
            self.doubts.setdefault(key, dict(world=wid, laws=laws, source=source,
                shared=(), status='not-yet', waiting_pair=True))
            discovery.trace('doubt_assumptions', laws, ['doubt:'+key])
            return key
        exact = discovery.worlds[wid].form == 'exact'
        shared = set(nodes(compatible[laws[0]]['hypothesis']) if exact else compatible[laws[0]]['hypothesis'])
        for k in laws[1:]:
            shared.intersection_update(nodes(compatible[k]['hypothesis']) if exact else compatible[k]['hypothesis'])
        # Variables alone are bindings, not a revisable assumption. Concepts,
        # fitted literals and compound subprograms are eligible shared parts.
        shared = (sorted((p for p in shared if p[0] not in ('var', 'zero', 'one', 'nil')),
                         key=lambda p: (-LG.size(p), repr(p))) if exact else sorted(shared, key=repr))
        key = digest((wid, laws, source))
        self.doubts.setdefault(key, dict(world=wid, laws=laws, source=source,
                                        shared=tuple(shared), status='not-yet'))
        discovery.trace('doubt_assumptions', laws, ['doubt:'+key])
        return key

    def revise(self, mind, discovery, pool, wid, *, deadline):
        """Replace a shared part in EACH law, preserving EACH certified scope.

        All outer verdicts are obtained before admitting any revision. A failed
        scope gives no new standing anywhere. This is a search order, not a
        guarantee; bounded acquired alternatives can miss the needed concept.
        """
        if not self.switches['doubt_assumptions']:
            return 0
        concepts = mind.field.concept_table()
        for dk, doubt in sorted(self.doubts.items()):
            if doubt['world'] != wid or doubt['status'] != 'not-yet':
                continue
            if len(doubt['laws']) < 2:
                if len(self.compatible(discovery, wid)) >= 2:
                    successor = self.doubt(discovery, wid, doubt['laws'], source=doubt['source'])
                    doubt.update(status='paired', successor=successor)
                continue
            entries = [discovery.laws[k] for k in doubt['laws']]
            exact = discovery.worlds[wid].form == 'exact'
            alternatives = set()
            for e in entries:
                alternatives.update(nodes(e['hypothesis']) if exact else e['hypothesis'])
            if exact:
                alternatives.update(discovery.rivals[wid])
                arg = LG.node('var', payload='x')
                alternatives.update(LG.node('c', arg, payload=k) for k in sorted(concepts.get('_sig', {})))
                alternatives = sorted((p for p in alternatives if p[0] != 'var'), key=lambda p: (LG.size(p), repr(p)))[:32]
                predicates = [p for p in alternatives if (LG.infer(p, concepts, arg='x') or (None, None))[1] == 'bool']
            else:
                from .discovery import public_rail
                if discovery.switches['hidden_quantities'] and len(discovery.observations[wid]) >= 2:
                    discovery.fit_quantity(mind, wid, discovery.features(mind, discovery.view(wid)))
                    concepts = mind.field.concept_table()
                task = public_rail(discovery.worlds[wid], discovery.observations[wid])
                alternatives.update(mind.engine._parts_physics(task, discovery.levels[wid], concepts))
                for hyp in discovery.rivals[wid]:
                    alternatives.update(hyp)
                alternatives = sorted(alternatives, key=repr)[:32]
                predicates = []
            for part in doubt['shared']:
                # Context dependence is built only from acquired predicates
                # and parts. No observer threshold or formula enters here.
                local = alternatives + [LG.node('if', predicate, part, alt)
                    for predicate in predicates[:4] for alt in alternatives[:8] if alt != part]
                for alternative in local:
                    if time.time() >= deadline:
                        return 0
                    if part == alternative:
                        continue
                    bundle = tuple(replace_part(e['hypothesis'], part, alternative) if exact else
                                   tuple(alternative if p == part else p for p in e['hypothesis']) for e in entries)
                    token = digest((dk, part, bundle))
                    if token in self.attempted:
                        continue
                    self.attempted.add(token)
                    scopes = [(k, world, hyp) for k, e, hyp in zip(doubt['laws'], entries, bundle)
                              for world in sorted(e['coverage'])]
                    if wid not in {world for _, world, _ in scopes}:
                        fits = [(k, wid, hyp) for k, hyp in zip(doubt['laws'], bundle)
                                if not exact or all(value(hyp, x, concepts) == y
                                                    for x, y in discovery.observations[wid])]
                        if not fits:
                            continue
                        scopes.append(fits[0])
                    if exact and any(LG.infer(hyp, concepts, arg='x') is None or
                           not LG.fits(LG.infer(hyp, concepts, arg='x'),
                                       discovery.worlds[world].tin, discovery.worlds[world].tout) or
                           any(value(hyp, x, concepts) != y for x, y in discovery.observations[world])
                           for _, world, hyp in scopes):
                        continue
                    verdicts = []
                    for k, world, hyp in scopes:
                        if time.time() >= deadline:
                            return 0
                        v = pool.certify(world, hyp, concepts, tuple(discovery.observations[world]),
                                         library=mind.field.shapes())
                        if type(v) is not Certification:
                            raise TypeError('Unsafe revision verdict')
                        discovery.checks += 1
                        verdicts.append((k, world, hyp, v))
                    accepted = bool(verdicts) and all(v.accepted for _, _, _, v in verdicts)
                    self.revisions.append(dict(doubt=dk, part=part, replacement=alternative,
                        bundle=bundle, certified=accepted,
                        records=tuple((k, world, v.record, v.accepted) for k, world, _, v in verdicts)))
                    if accepted:
                        for _, world, hyp, v in verdicts:
                            discovery.admit(mind, world, hyp, v, discovery.features(mind, discovery.view(world)), 1.)
                        doubt['status'] = 'revised'
                        return 1
                    return 0  # one costly bundle per unit; next unit tries the next
        return 0

    def predict(self, mind, discovery, wid, action):
        if not self.switches['bold_predictions'] or discovery.worlds[wid].form != 'exact' or action[0] != 'ask':
            return None
        x = action[1]
        # Unseen across ALL visited bodies, not merely the currently selected one.
        if any(x == a for rows in discovery.observations.values() for row in rows
               if len(row) == 2 for a in (row[0],)):
            return None
        concepts = mind.field.concept_table()
        laws = self.compatible(discovery, wid)
        if not laws:
            return None
        discovery.trace('bold_predictions', [k for k, _ in laws])
        key, law = max(laws, key=lambda pair: (self.law_credit.get(pair[0], 0.), pair[0]))
        y = value(law['hypothesis'], x, concepts)
        if y is None:
            return None
        principles = tuple(pk for pk, p in sorted(self.principles.items()) if
            self.switches['symmetry_principles'] and key in p['laws'] and
            self.keeps(law['hypothesis'], p['transform'], (x, value(p['transform']['program'], x, concepts)), concepts))
        p = prediction_record(digest((wid, action, key, len(self.predictions))),
                              wid, action, key, y, principles)
        self.predictions.append(p)  # before the only world call in Discovery.tick
        discovery.trace('bold_predictions', [key], ['prediction:'+p['id']])
        return p['id']

    def settle(self, mind, discovery, pid, observation):
        if pid is None or not self.switches['bold_predictions']:
            return 0.
        p = next(r for r in self.predictions if r['id'] == pid)
        if p['result'] is not None:
            raise ValueError('Prediction already settled')
        p['performed_at'] = time.time()
        p['result'] = observed(observation[1])
        p['confirmed'] = p['result'] == p['predicted']
        gain = 1. if p['confirmed'] else -1.
        self.law_credit[p['law']] = self.law_credit.get(p['law'], 0.) + gain
        for pk in p['principles']:
            self.principle_credit[pk] = self.principle_credit.get(pk, 0.) + gain
            self.principles[pk]['credit'] += gain
        if not p['confirmed']:
            v = Certification(False, 'formula', (('own_prediction', True),), p['id'], True)
            discovery.anomaly(mind, p['world'], p['law'], v)
            self.doubt(discovery, p['world'], (p['law'],), source=p['id'])
        return gain

    def run(self, mind, discovery, pool, wid, *, deadline):
        reads = mind.engine._u_reads([discovery.search_view(wid)])[0][0].detach().cpu().numpy()
        self.methods.bind(reads)
        moment = dict(doubt=discovery.rival_entropy(mind, wid),
                      misfit=discovery.surprises[wid], proven=len(discovery.laws))
        chosen = self.methods.choose('discovery', {'observe'} | {k for k in CRUTCHES if self.switches[k]},
                                     moment, mind.numpy)
        outcomes = []
        for method in chosen:
            if time.time() >= deadline:
                break
            name = method[0]
            started = time.perf_counter()
            gain = 0.
            if name == 'thought_experiments':
                before = len(self.paradoxes)
                self.thought(mind, discovery, wid)
                gain = len(self.paradoxes)-before
            elif name == 'symmetry_principles':
                gain = self.invariance(mind, discovery, wid)
            elif name == 'doubt_assumptions':
                gain = self.revise(mind, discovery, pool, wid, deadline=deadline)
            seconds = time.perf_counter()-started
            # Novel questions/support are not removed doubt. Retain the
            # branch's pending feature until real tick outcomes supply return.
            outcomes.append(dict(method=name, gain=gain, seconds=seconds))
        return chosen, moment, outcomes

    def feedback(self, chosen, moment, gain, seconds):
        for method in chosen:
            self.methods.learn('discovery', method, moment,
                               float(np.clip(gain/max(seconds, 1e-6), -20., 20.)))
        self.methods.end_task()

    def report(self):
        return dict(paradoxes=len(self.paradoxes),
            paradoxes_confirmed=sum(p['confirmed'] is True for p in self.paradoxes.values()),
            paradoxes_tested=sum(bool(p['experiments']) for p in self.paradoxes.values()),
            principles=len(self.principles), principle_search=dict(self.search),
            principle_search_scope='actual audit attempts; accepted frontier ranks are a proxy, paired A/B measures speed',
            dual_world_revisions=sum(r['certified'] for r in self.revisions),
            predictions=len(self.predictions),
            predictions_confirmed=sum(p['confirmed'] is True for p in self.predictions),
            predictions_failed=sum(p['confirmed'] is False for p in self.predictions))
