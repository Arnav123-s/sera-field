"""Own gaps from acquired laws and observations; no observer links or names."""
import math

from sera import lang as LG
from .discovery import Readout
from .ports import digest
from .sleep import expand, sample_input, walk

REASONS = ('constant', 'term', 'domain', 'failure', 'join', 'uncovered')


def literals(program):
    return tuple(sorted({p[1] for p in walk(program) if p[0] == 'lit'}, key=repr))


class Holes:
    def __init__(self, switches):
        self.switches = {k: switches['holes_'+k] for k in REASONS}
        self.policy = Readout()
        self.questions, self.events, self.progress, self.retired = {}, [], {}, {}
        self.zero_progress_repeats = 0
        self.teacher_shown = False

    def demonstrate(self, *, phase, origin):
        if phase not in ('lesson', 'study', 'test1') or origin != 'taught':
            raise ValueError('No hole demonstration on discovery/assessment worlds')
        if self.teacher_shown:
            return False
        x = self.feature()
        for name in REASONS:
            if self.switches[name]:
                self.policy.demonstrate('holes_'+name, x, phase)
        self.teacher_shown = True
        return True

    @staticmethod
    def feature():
        import numpy as np
        return np.r_[1., np.zeros(64)]

    def offered(self, mind, wid, key, surface):
        d, law = mind.discovery, mind.discovery.laws[key]
        p = law['hypothesis']
        choices = []
        if law['form'] == 'exact':
            choices.extend(('constant', ('literal', n), wid) for n in literals(p))
            choices.extend(('term', ('expression', q), wid) for q in walk(p)
                           if q != p and q[0] not in ('lit', 'var', 'zero', 'one', 'nil', 'lam') and
                           not any(l['form'] == 'exact' and l['hypothesis'] == q for l in d.laws.values()))
            for cid in sorted({q[1] for q in walk(surface) if q[0] == 'c'}):
                term = expand(LG.node('c', LG.node('var', payload='x'), payload=cid), mind.field.concept_table())
                if not any(l['form'] == 'exact' and l['hypothesis'] == term for l in d.laws.values()):
                    choices.append(('term', ('expression', term), wid))
        values = d.quantity_values(wid)
        if values:
            choices.extend(('constant', ('object', obj, value), wid) for obj, value in sorted(values.items()))
        # A domain question uses a genuinely unperformed public input, not an
        # observer's withheld region or a supplied expansion of a law.
        if law['form'] == 'exact' and not any(q['law'] == key and q['source_world'] == wid and
                q['reason'] == 'domain' for q in self.questions.values()):
            seen = {repr(x) for x, _ in d.observations[wid]}
            x = sample_input(d.worlds[wid].tin, mind.random)
            if repr(x) not in seen:
                choices.append(('domain', ('input', x), wid))
        failures = sorted({r['world'] for r in d.pending if r['law'] == key})
        if d.surprises[wid]:
            failures = sorted(set(failures) | {wid})
        choices.extend(('failure', ('anomaly', digest(d.observations[target])), target)
                       for target in failures)
        for other, entry in sorted(d.laws.items()):
            if other == key or law['form'] != 'exact' or entry['form'] != 'exact':
                continue
            shared = sorted(set(walk(p)) & set(walk(entry['hypothesis'])), key=repr)
            shared = [q for q in shared if q[0] not in ('var', 'zero', 'one', 'nil')]
            for q in shared:
                choices.append(('join', ('laws', other, q), wid))
        covered = {world for entry in d.laws.values() for world in entry['coverage']}
        choices.extend(('uncovered', ('world', other), other) for other in sorted(d.worlds)
                       if d.observations[other] and other not in covered)
        return choices

    def raise_questions(self, mind, wid, key, surface):
        d = mind.discovery
        parent = next((q['id'] for _, q in sorted(self.questions.items()) if q.get('answered_by') == key), None)
        made = []
        for reason, detail, target in self.offered(mind, wid, key, surface):
            if not self.switches[reason]:
                continue
            token = digest((key, reason, detail, target))
            if token in self.questions:
                continue
            method = 'holes_'+reason
            if self.policy.pick((method, 'continue'), mind.choice_features(), mind.numpy) != method:
                continue
            query = (detail[1],) if reason == 'domain' else ()
            view = d.view(target, query)
            agenda_key = mind.agenda.ask(view, 'hole:'+token,
                mind.clock.count if mind.clock_mode == 'work' else 0, outside=False, parent=parent)
            depth = 1+self.questions[parent]['depth'] if parent else 1
            self.questions[token] = dict(id=token, agenda=agenda_key, law=key, source_world=wid,
                world=target, reason=reason, detail=detail, parent=parent, depth=depth, status='open',
                snapshot=digest(d.observations[target]), raised_work=mind.clock.count if mind.clock_mode == 'work' else 0)
            self.events.append(dict(kind='hole', **self.questions[token]))
            d.trace('holes_'+reason, [key], ['hole:'+token])
            mind.field.ideas.bind(('discovered-law', key), ('own-hole', token), 1.)
            made.append(token)
        return made

    def settle(self, mind, wid, key):
        d, law = mind.discovery, mind.discovery.laws[key]
        for token, q in sorted(self.questions.items()):
            if q['status'] != 'open':
                continue
            old, reason, detail = d.laws[q['law']], q['reason'], q['detail']
            answered = False
            if reason == 'constant' and key != q['law'] and wid != q['source_world']:
                source_ids = d.worlds[q['source_world']].object_ids
                target_ids = d.worlds[wid].object_ids
                if source_ids and not set(source_ids) & set(target_ids):
                    continue
                if detail[0] == 'literal' and law['form'] == 'exact':
                    answered = detail[1] in literals(law['hypothesis'])
                elif detail[0] == 'object':
                    values = d.quantity_values(wid) or {}
                    answered = values.get(detail[1]) == detail[2]
            elif reason == 'term' and law['form'] == 'exact':
                answered = detail[1] == law['hypothesis']
            elif reason == 'domain' and wid == q['world'] and law['form'] == 'exact':
                answered = any(x == detail[1] and LG.safe(old['hypothesis'], {'x': x},
                    mind.field.concept_table()) == y for x, y in d.observations[wid])
            elif reason == 'failure':
                answered = wid == q['world'] and key != q['law'] and wid in law['coverage']
            elif reason == 'join' and key not in (q['law'], detail[1]):
                other = d.laws[detail[1]]
                answered = set(old['coverage']) | set(other['coverage']) <= set(law['coverage'])
            elif reason == 'uncovered':
                answered = q['world'] in law['coverage']
            if answered:
                q.update(status='answered', answered_by=key,
                         answered_work=mind.clock.count if mind.clock_mode == 'work' else 0)
                mind.agenda.settle(q['agenda'], ('law', key), 0,
                    mind.clock.count if mind.clock_mode == 'work' else 0, features=mind.choice_features())
                self.events.append(dict(kind='hole-answer', id=token, reason=reason, law=key, depth=q['depth']))
                self.policy.learn('holes_'+reason, mind.choice_features(), 1., max(1,
                    q['answered_work']-q['raised_work']))

    def anomaly(self, mind, wid, law=None):
        if wid in self.retired:
            self.retired.pop(wid)
            self.events.append(dict(kind='reopened', world=wid))
        for key, entry in sorted(mind.discovery.laws.items()):
            if wid in entry['coverage']:
                self.raise_questions(mind, wid, key, entry['hypothesis'])
            elif key == law:
                # A failed transfer is a hole in the source law's scope. Its
                # question targets the failed body but keeps the source reason.
                for source in sorted(entry['coverage']):
                    self.raise_questions(mind, source, key, entry['hypothesis'])

    def work(self, mind, agenda_key, pool, deadline):
        """Direct an own experiment, then use ordinary proposal/audit.

        Target choice uses public compatibility only; planted links never
        enter this code. A new domain question may reopen an understood world.
        """
        q = next(q for q in self.questions.values() if q['agenda'] == agenda_key)
        d = mind.discovery
        compatible = [wid for wid in sorted(d.worlds) if d.worlds[wid].form ==
            d.worlds[q['world']].form and (d.worlds[wid].tin, d.worlds[wid].tout) ==
            (d.worlds[q['world']].tin, d.worlds[q['world']].tout)]
        if q['reason'] in ('constant', 'term', 'join'):
            compatible = [wid for wid in compatible if wid != q['source_world']] or compatible
            wid = self.policy.pick(compatible, mind.choice_features(), mind.numpy)
        else:
            wid = q['world']
        self.retired.pop(wid, None)
        d.active = wid
        if q['reason'] == 'domain':
            action = ('ask', q['detail'][1])
        else:
            menu = d.experiment_menu(mind, wid)
            chosen, _ = d.choose_experiment(menu, mind.choice_features(), mind.numpy)
            if chosen is None:
                return None
            action = chosen['action']
        from .ports import observed
        observation = observed(pool.act(wid, action))
        if mind.clock_mode == 'work':
            mind.clock.charge('act')
        d.observations[wid].append(observation)
        d.experiments += 1
        self.events.append(dict(kind='hole-work', id=q['id'], world=wid, action=action))
        from .discovery import Certification
        for key, law in sorted(d.laws.items()):
            if d.worlds[wid].form != 'exact' or law['form'] != 'exact' or \
                    law['signature'] != (d.worlds[wid].tin, d.worlds[wid].tout):
                continue
            matches = all(LG.safe(law['hypothesis'], {'x': x}, mind.field.concept_table()) == y
                          for x, y in d.observations[wid])
            if not matches:
                if wid in law['coverage']:
                    d.anomaly(mind, wid, key, Certification(False, law['kind'],
                        (('own_hole_experiment', True),), digest(observation), True))
                continue
            verdict = pool.certify(wid, law['hypothesis'], mind.field.concept_table(),
                                   tuple(d.observations[wid]), library=mind.field.shapes())
            d.checks += 1
            if verdict.accepted:
                d.admit(mind, wid, law['hypothesis'], verdict, mind.choice_features(), 1., law_key=key)
                self.settle(mind, wid, key)
            if mind.clock_mode == 'work' and mind.clock.expired(deadline):
                break
        return d.tick(mind, pool, deadline=deadline) if mind.clock_mode != 'work' or not mind.clock.expired(deadline) else None

    def visit(self, mind, wid):
        d, w = mind.discovery, mind.discovery.worlds[wid]
        candidates = [e['hypothesis'] for e in d.laws.values() if wid in e['coverage']]
        candidates.extend(d.rivals[wid])
        if w.form == 'exact' and d.observations[wid]:
            rows = d.observations[wid]
            scores = [(sum(LG.safe(p, {'x': x}, mind.field.concept_table()) != y for x, y in rows)/len(rows),
                       LG.bits(p, mind.field.concept_table())) for p in candidates]
            metric = min(scores, default=(1., math.inf))
        else:
            metric = min((e['coverage'][wid][1], e['bits']) for e in d.laws.values()
                         if wid in e['coverage']) if any(wid in e['coverage'] for e in d.laws.values()) else (math.inf, math.inf)
        previous = self.progress.get(wid)
        gain = 0. if previous is None else float(metric < previous['metric'])
        repeated = previous is not None and gain == 0
        self.zero_progress_repeats += int(repeated)
        self.progress[wid] = dict(metric=metric, visits=1+(previous['visits'] if previous else 0), gain=gain)
        solved = any(wid in e['coverage'] for e in d.laws.values()) and (
            metric[0] == 0 if w.form == 'exact' else repeated and not d.surprises[wid])
        if mind.u14['retire_understood'] and solved and repeated and self.policy.pick(
                ('retire', 'continue'), mind.choice_features(), mind.numpy) == 'retire':
            self.retired[wid] = dict(metric=metric, observations=digest(d.observations[wid]))
            self.events.append(dict(kind='retired', world=wid, zero_progress=True))
        return gain

    def learning_state(self):
        return {k: v for k, v in self.__dict__.items() if k != 'events'}

    def report(self, mind):
        return dict(found=len(self.questions), answered=sum(q['status'] == 'answered' for q in self.questions.values()),
            chain_depth=max((q['depth'] for q in self.questions.values()), default=0),
            distinct_laws=len(mind.discovery.laws) if mind.discovery else 0,
            zero_progress_repeat_visits=self.zero_progress_repeats, retired_worlds=sorted(self.retired),
            records=self.events)

    def validate(self):
        if set(self.__dict__) != {'switches', 'policy', 'questions', 'events', 'progress', 'retired',
                                 'zero_progress_repeats', 'teacher_shown'} or set(self.switches) != set(REASONS):
            raise ValueError('Unknown holes shape')
        for q in self.questions.values():
            if q['reason'] not in REASONS or q['status'] not in ('open', 'answered'):
                raise ValueError('Unknown hole question shape')
