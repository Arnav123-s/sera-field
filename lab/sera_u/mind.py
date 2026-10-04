"""One owner, one optimizer, all symbolic abilities, receipts and random streams."""
from contextlib import contextmanager
import copy
from dataclasses import asdict, replace
import hashlib
import io
import json
import math
import os
from pathlib import Path
import pickle
import random
import sys
import time

import numpy as np
import torch

from sera import crutches as CR, lang as LG, one as ONE, phi as PH, tasks as TS, talk as TK
from .field.native_owner import NativeConfig, detached_state
from .ports import PortBudget, TaskView, digest
from .proposer import FieldOwner, Proposer
from .sleep import Receipt, Sleep, expand, Curiosity, Syndrome, gap_parts, gap_kind, independent
from .memory import Memory, MemoryField, BranchReadGate, memory_records, public_context
from .discovery import CRUTCHES as U9_CRUTCHES, Discovery
from .clock import Clock, activate, operation, work_constructor

U14_CRUTCHES = ('work_doubling', 'observe_to_floor', 'questions_first', 'retire_understood', 'discovery_memory',
    'holes_constant', 'holes_term', 'holes_domain', 'holes_failure', 'holes_join', 'holes_uncovered')

SCHEMA = 'sera-u-2'
U1_CRUTCHES = ('field_proposer', 'program_dreams', 'sleep_library', 'field_input_ports')
U2_CRUTCHES = ('memory_layer_a', 'memory_layer_b', 'field_understanding')
U3_CRUTCHES = ('field_ways', 'field_methods', 'field_roadmap', 'inner_judge')
U6_CRUTCHES = ('gap_syndromes', 'aimed_dreams')
U7_CRUTCHES = ('taught_not_yet', 'abstain_bar')
U8_CRUTCHES = ('memory_choice',)
U_CRUTCHES = U1_CRUTCHES+U2_CRUTCHES+U3_CRUTCHES+U6_CRUTCHES+U7_CRUTCHES+U8_CRUTCHES
ARMS = ('full', 'no-proposer', 'no-dreams', 'no-library')
CURIOSITY_ARMS = ('aimed', 'unaimed')


def arm_settings(arm):
    if arm not in ARMS+CURIOSITY_ARMS:
        raise ValueError('Unknown SERA-U arm')
    settings = dict(field_proposer=arm != 'no-proposer', program_dreams=arm != 'no-dreams',
                    sleep_library=arm != 'no-library', field_input_ports=True,
                    **{k: k not in CR.OFF for k in U2_CRUTCHES})
    added = {k: CR.on(k) for k in U3_CRUTCHES}
    if arm in CURIOSITY_ARMS:
        added.update({k: k not in CR.OFF for k in U3_CRUTCHES+U6_CRUTCHES})
        added.update({k: arm == 'aimed' and k not in CR.OFF for k in U6_CRUTCHES})
    elif any(CR.on(k) for k in U6_CRUTCHES):
        added.update({k: CR.on(k) for k in U6_CRUTCHES})
    if any(CR.on(k) or k in CR.OFF or k in CR.ON for k in U7_CRUTCHES):
        added.update({k: CR.on(k) for k in U7_CRUTCHES})
    if any(added.values()):
        settings.update(added)
    if CR.on('memory_choice') or 'memory_choice' in CR.ON or 'memory_choice' in CR.OFF:
        settings['memory_choice'] = CR.on('memory_choice')
    return settings


def source_identity():
    path = Path(__file__).parent/'field'
    manifest = json.loads((path/'SOURCE.json').read_text(encoding='utf-8-sig'))
    for item in manifest['files']:
        if hashlib.sha256((path/item['path']).read_bytes()).hexdigest() != item['vendored_sha256']:
            raise ValueError('Changed pinned Field file: '+item['path'])
    return digest(manifest)


def code_identity():
    root = Path(__file__).resolve().parents[1]
    paths = sorted([*root.glob('sera/*.py'), *root.glob('ccops5/core/*.py'),
                    *root.glob('sera_u/*.py'), root/'scripts/sera_u_rsi.py', root/'scripts/sera_u_discovery.py',
                    root/'scripts/sera_u_einstein.py', root/'scripts/sera_u_scientists.py', root/'scripts/sera_u_darwin.py', root/'scripts/sera_u_roadmap.py',
                    root/'scripts/sera_u_holes.py'])
    return digest([(str(p.relative_to(root)).replace('\\', '/'), hashlib.sha256(p.read_bytes()).hexdigest())
                   for p in paths if p.is_file()])


def expanded_size(p, concepts):
    """A program's size with its concept calls expanded; None when it calls a concept this mind does not hold (VM C's
    no-library arm, 25d7a29: an unproven answer kept a call from before the arm's library was taken away)."""
    try:
        return LG.size(expand(p, concepts))
    except ValueError:
        return None


def global_rng():
    return dict(python=random.getstate(), numpy=np.random.get_state(), cpu=torch.get_rng_state(),
                cuda=torch.cuda.get_rng_state_all() if torch.cuda.is_available() else [])


def restore_rng(state):
    random.setstate(state['python'])
    np.random.set_state(state['numpy'])
    torch.set_rng_state(state['cpu'].cpu())
    if state['cuda']:
        if not torch.cuda.is_available() or len(state['cuda']) != torch.cuda.device_count():
            raise ValueError('Exact CUDA RNG topology is unavailable')
        torch.cuda.set_rng_state_all([v.cpu() for v in state['cuda']])


class Engine(ONE.Sera):
    """No-library control still lives the same loop; no macro can be installed."""
    memory = None

    def _u_on(self, name):
        return bool(getattr(self, 'u_switches', {}).get(name, False))

    def _u_bar_on(self):
        # Old masks carry U3's bar implicitly; explicit U7 masks can ablate it.
        return self._u_on('inner_judge') and self._u_on('abstain_bar') and not self._u_on('taught_not_yet')

    def _u_phase(self, task, teaching=False):
        default = 'lesson' if teaching else 'world'
        if hasattr(task, 'course_lesson'):
            default = 'lesson' if task.course_lesson else 'test3'
        return getattr(self, '_u_phase_name', getattr(task, 'course_phase', default))

    def _u_configuration(self, task, leader, available, moves, moment, trig, st, rng, t0):
        if not self._u_on('taught_not_yet'):
            return None
        if st['proven'] is not None:
            return ['leave'], {'leave': (0., 0.)}
        self._u_choice_started = time.process_time()
        kind = ONE.kind_of(task)
        x = (self._u_candidate_inputs(task, [leader])[0] if leader is not None else
             PH.InnerJudge.features(self._u_reads([TaskView.from_task(task)])[0][0].detach().cpu().numpy()))
        probability = self.field.inner.probability(kind, x) if self._u_on('inner_judge') else .5
        tried = st.setdefault('u_tried_methods', set())
        ranking = self.field.methods.ranking(kind, moves, trig, tried)
        methods = [m for m in ranking if m not in (('step',), ('recall',))]
        options = {}
        if 'prove' in available:
            options['answer'] = ('prove', None)
        if methods:
            options['method'] = ('imagine', methods[0])
        if task.form == 'exact' and len(task.inputs) == 1 and ('step',) not in tried:
            # An unsure but fitting candidate must not suppress a smallest step.
            options['step'] = ('imagine', ('step',))
        if 'recall' in moves and ('recall',) not in tried:
            options['recall'] = ('imagine', ('recall',))
        if 'ask' in available and self._u_phase(task, st['teaching']) in ('lesson', 'test1', 'talk', 'world'):
            options['ask'] = ('ask', None)
        if self._u_on('gap_syndromes') and self.field.curiosity.gap is not None and methods:
            options['dig'] = ('imagine', methods[0])
        if 'grow' in available:
            options['grow'] = ('grow', None)
        spent = 0. if not np.isfinite(ONE.MAX_WALL) else (time.time()-t0)/max(ONE.MAX_WALL, 1e-6)
        action, f, values = self.field.loop.pick(kind, x, probability, options, rng, spent)
        if action is None:
            return [], {}
        continuation = min((a for a in options if a != 'answer'),
                           key=lambda a: (-values[a][1], a), default=None)
        if st.get('u_teacher_advice') and 'imagine' in st['u_teacher_advice'] and continuation is not None:
            self.field.loop.demonstrate(kind, f, options, continuation)
        if leader is not None:
            self.field.loop.remember(kind, leader, action, f, continuation)
        st['u_choice'] = (kind, action, f, self._u_choice_started)
        st.setdefault('u_not_yet', []).append(dict(step=st['steps'], state='not-yet',
                                                   action=action, probability=probability))
        faculty, method = options[action]
        if method is not None:
            st['u_next_method'] = method
            tried.add(method)
            # This learned action is an imagination moment, including a dig
            # whose located part enters only the hypothetical context.
            if action == 'dig':
                gap = self.field.curiosity.gap
                view = TaskView.from_task(task)
                view = replace(view, hypotheses=view.hypotheses +
                               ((('hypothetical-gap', repr(gap)),),))
                read = self._u_reads([view])[0][0].detach().cpu().numpy()
                self.field.methods.bind(read)
        return [faculty], {faculty: values[action]}

    def _u_methods(self, kind, moves, trig, rng, st):
        method = st.pop('u_next_method', None)
        if not self._u_on('taught_not_yet') or method is None:
            return self.field.methods.choose(kind, moves, trig, rng)
        return self.field.methods.next_method(kind, method, trig)

    def _u_moment_return(self, st, gain):
        choice = st.pop('u_choice', None)
        if choice is not None:
            kind, action, f, started = choice
            seconds = max(time.process_time()-started, 1e-6)
            # Time consumes return even when no public progress was made.
            self.field.loop.choice_learn(kind, action, f, float(np.clip(gain/seconds, -20., 20.))-seconds)

    def _ask_us(self, task, leader, doubt, st, speak, cap=False):
        if not self._u_on('taught_not_yet'):
            return super()._ask_us(task, leader, doubt, st, speak, cap)
        # State only. An end-of-budget event cannot ask for test answers.
        speak('not-yet', 'not-yet', cap=bool(cap))

    def _u_reads(self, views, concepts=None):
        concepts = self.proposer.admitted(self._concepts() if concepts is None else concepts)
        previous = self.proposer.memory
        self.proposer.memory = getattr(self, '_u_branch_memory', previous)
        try:
            with torch.no_grad():
                return self.proposer.features_many(views, [concepts]*len(views), memory_read=True)
        finally:
            self.proposer.memory = previous

    def _u_bind(self, task):
        if self.memory is not None and getattr(self.memory, 'choosing', False):
            self.memory.consult(TaskView.from_task(task))
        if not any(self._u_on(k) for k in ('field_ways', 'field_methods', 'field_roadmap', 'taught_not_yet')):
            return
        read = self._u_reads([TaskView.from_task(task)])[0]
        features = read[0].detach().cpu().numpy()
        for switch, slot in (('field_ways', 'loop'), ('field_methods', 'methods'), ('field_roadmap', 'steps')):
            if self._u_on(switch) or self._u_on('taught_not_yet'):
                getattr(self.field, slot).bind(features)

    def _moves_available(self, task, *args, **kwargs):
        self._u_bind(task)
        moves = super()._moves_available(task, *args, **kwargs)
        if self.memory is not None and getattr(self.memory, 'choosing', False) and not self.memory.b:
            moves.discard('recall')
        if self._u_on('field_methods') or self._u_on('taught_not_yet'):
            if task.form == 'exact':
                moves.add('dream')
                if len(task.inputs) == 1 and getattr(task, 'var', None):
                    moves.add('back')
            # Recall through layer B is available on the One Field path too.
            if self.memory is not None and self.memory.b:
                moves.add('recall')
        return moves

    @staticmethod
    def _u_candidate_view(view, candidate, values):
        # Imagined rows on the view's own hypothetical channel, never a memory event/pair
        # or a public query. Public examples and queries remain intact. Candidate identity
        # and predictions are read through the same stable ports as everything else.
        rows = ((('hypothetical-candidate', repr(candidate)),),)
        rows += tuple((('hypothetical-output', value),) for value in values)
        return replace(view, hypotheses=view.hypotheses + rows)

    def _u_candidate_inputs(self, task, candidates):
        view = TaskView.from_task(task)
        concepts = self._concepts()
        views = []
        for p in candidates:
            values = ([LG.safe(p, dict(b), concepts) for b, _ in view.examples]
                      if task.form == 'exact' else ())
            views.append(self._u_candidate_view(view, p, values))
        reads = self._u_reads(views, concepts)
        return [PH.InnerJudge.features(f.detach().cpu().numpy()) for f, _ in reads]

    def _u_syndrome(self, task, order, log_u, log_b, *, accepted=None, final=False):
        if not self._u_on('gap_syndromes') or not hasattr(self, '_u_gap_context'):
            return ()
        context = self._u_gap_context
        view = TaskView.from_task(task)
        candidates = tuple(order[:16]) if view.form == 'exact' else ()
        # One read per changed public moment, not per repeated choice loop.
        fingerprint = (view.identity, candidates, tuple(log_u.get(p) for p in candidates),
                       tuple(log_b.get(p) for p in candidates), accepted)
        if not final and fingerprint == context['fingerprint']:
            return context.get('checks', ())
        context['fingerprint'] = fingerprint
        context['candidates'] = candidates
        context['log_u'], context['log_b'] = dict(log_u), dict(log_b)
        concepts = self._concepts()
        reads = self._u_reads([view], concepts)
        features = reads[0][0].detach().cpu().numpy()
        context['features'] = features
        memories = []
        if candidates and self.memory is not None and self.memory.a and self.memory.b and hasattr(self.field, 'familiarity'):
            tags = [(p, ('concept', p[1]) if p[0] == 'concept' else ('sym', p[1]))
                    for p in gap_parts(candidates, view) if p[0] in ('production', 'concept')
                    and p not in (('production', 'var'), ('production', 'lam'), ('production', 'lit'))]
            if tags:
                memories = self._u_memory_checks(view, tags)
        if not final:
            context['surest'] = getattr(self.proposer, '_gap_surest', None)
        surest = context.get('surest')
        checks = self.field.curiosity.checks(view, candidates, concepts, memories=memories,
                                            roadmap=context['roadmap'], log_u=log_u, log_b=log_b,
                                            surest=surest, accepted=accepted)
        context['checks'] = checks
        if not final:
            gap = self.field.curiosity.decode(context['view'], checks, features)
            # Credit only the first location that initiated this run's digging.
            if context['gap'] is None and gap is not None:
                context['gap'] = copy.deepcopy(gap)
        return checks

    def _u_memory_checks(self, view, tags):
        with torch.no_grad():
            # Same cue, A recall alone against B familiarity ringing alone.
            f, w, _ = self.proposer.owner.read_features_many(
                [view], states=[self.memory.mind.state], rings=[None], memory_read=True,
                context=('syndrome-a', self.memory.a, self.memory.b))[0]
            a = self.proposer.owner.familiarity_readout(f, w, tuple(('part', tag) for _, tag in tags))
            kind, public = public_context(view)
            b, _ = self.field.familiarity(kind, public, tuple(tag for _, tag in tags), (),
                                         version='u2-public-v1' if view.form == 'exact' else 'context-v1')
            return [(part, float(value), b.get(tag, 0.)) for (part, tag), value in zip(tags, a)]


    def _u_actions(self, task, actions):
        if self._u_on('taught_not_yet') and self._u_phase(task) not in ('lesson', 'test1', 'talk', 'world'):
            return []
        if not self._u_on('gap_syndromes') or not hasattr(self, '_u_gap_context'):
            return actions
        context = self._u_gap_context
        if context['phase'] not in ('lesson', 'test1', 'talk', 'world'):
            return []                  # no newly answered questions in study/test2/test3
        gap = self.field.curiosity.gap
        if task.form != 'exact' or gap is None or not gap['inputs']:
            return actions
        wanted = {LG.freeze(dict(b)[task.var]) for b in gap['inputs'] if task.var in dict(b)}
        preferred = [a for a in actions if a['action'][0] == 'ask' and LG.freeze(a['action'][1]) in wanted]
        return preferred or actions

    def _u_order(self, task, order):
        if not self._u_on('inner_judge') or not order:
            return order
        # Bound resident batch size, while reading each candidate just once.
        frontier = order[:ONE.TOP]
        scores = []
        for j in range(0, len(frontier), 8):
            xs = self._u_candidate_inputs(task, frontier[j:j+8])
            scores += [self.field.inner.probability(ONE.kind_of(task), x) for x in xs]
        return [frontier[j] for j in sorted(range(len(frontier)), key=lambda j: (-scores[j], j))] + order[len(frontier):]

    def _u_predict(self, task, candidate):
        if self._u_on('inner_judge'):
            self.__dict__.setdefault('_u_predictions', {})[(ONE.kind_of(task), candidate)] = self._u_candidate_inputs(task, [candidate])[0]

    def _u_verdict(self, task, candidate, right, source):
        if self._u_on('gap_syndromes') and self._u_on('inner_judge'):
            x = getattr(self, '_u_predictions', {}).get((ONE.kind_of(task), candidate))
            if x is not None:
                p = self.field.inner.probability(ONE.kind_of(task), x)
                self.field.curiosity.verdict(gap_kind(TaskView.from_task(task)), p, bool(right), source)
        if not self._u_on('inner_judge'):
            if self._u_on('taught_not_yet'):
                self.field.loop.returned(ONE.kind_of(task), candidate, bool(right), source=source,
                                         elapsed=max(time.process_time()-getattr(self, '_u_choice_started', time.process_time()), 1e-6))
            return
        x = self.__dict__.setdefault('_u_predictions', {}).pop((ONE.kind_of(task), candidate), None)
        if x is None:
            x = self._u_candidate_inputs(task, [candidate])[0]
        self.field.inner.verdict(ONE.kind_of(task), candidate, x, bool(right), source)
        if self._u_on('taught_not_yet'):
            self.field.loop.returned(ONE.kind_of(task), candidate, bool(right), source=source,
                                     elapsed=max(time.process_time()-getattr(self, '_u_choice_started', time.process_time()), 1e-6))

    def course_verdict(self, task, law, right, source, reliability=False):
        if self.memory is not None and getattr(self.memory, 'choosing', False):
            if source not in ('teacher', 'book', 'test1', 'test2') or self._u_phase(task) == 'test3':
                raise ValueError('Only received course verdicts train memory choice')
            self.memory.feedback = bool(right)
        if self._u_on('inner_judge') or self._u_on('taught_not_yet'):
            # The S27 caller alone controls whether verdicts are available. It
            # must use these explicit teaching sources, never an observer grade.
            admitted = 'book' if source == 'book' else 'teacher' if source in ('teacher', 'test1', 'test2') else None
            if admitted is None:
                raise ValueError('Unrecognized course feedback source')
            if (self._u_on('inner_judge') and (source != 'test2' or not self._u_on('taught_not_yet')) and
                    admitted == 'teacher' and not right and task.form == 'exact'):
                self._u_teach_answer(task, law)
            else:
                self._u_verdict(task, law, right, admitted)
        return super().course_verdict(task, law, right, source, reliability and not self._u_on('inner_judge'))

    def course_reliable(self, task):
        if self._u_on('taught_not_yet'):
            x = PH.InnerJudge.features(self._u_reads([TaskView.from_task(task)])[0][0].detach().cpu().numpy())
            p = self.field.inner.probability(ONE.kind_of(task), x) if self._u_on('inner_judge') else .5
            action, _, _ = self.field.loop.pick(ONE.kind_of(task), x, p, {'answer', 'method'}, np.random)
            return action == 'answer'
        if self._u_bar_on():
            return self.field.inner.probability(ONE.kind_of(task), np.r_[1., np.zeros(64)]) >= self.field.inner.bar(ONE.kind_of(task))
        return super().course_reliable(task)

    def _teacher_says_wrong(self, task, law, concepts, st):
        self._u_predict(task, law)
        result = super()._teacher_says_wrong(task, law, concepts, st)
        if self._u_on('inner_judge') or self._u_on('taught_not_yet'):
            if self._u_on('inner_judge') and result is not None and task.form == 'exact':
                self._u_teach_answer(task, law)
            else:
                self._u_verdict(task, law, result is None, 'teacher')
        return result

    def _u_teach_answer(self, task, wrong):
        view = TaskView.from_task(task)
        # The teacher's corrected public outputs are the positive half, without
        # guessing a solution program or importing a private target.
        right = ('shown-answer', tuple(y for _, y in view.examples))
        views = [self._u_candidate_view(view, wrong,
                                       [LG.safe(wrong, dict(b), self._concepts()) for b, _ in view.examples]),
                 self._u_candidate_view(view, right, [y for _, y in view.examples])]
        reads = self._u_reads(views)
        xs = [PH.InnerJudge.features(f.detach().cpu().numpy()) for f, _ in reads]
        before = self.__dict__.setdefault('_u_predictions', {}).pop((ONE.kind_of(task), wrong), xs[0])
        if self._u_on('gap_syndromes'):
            self.field.curiosity.verdict(gap_kind(view), self.field.inner.probability(ONE.kind_of(task), before), False, 'teacher')
        self.field.inner.correct(ONE.kind_of(task), wrong, before, right, xs[1], source='teacher')
        if self._u_on('taught_not_yet'):
            self.field.loop.returned(ONE.kind_of(task), wrong, False, source='teacher',
                                     elapsed=max(time.process_time()-getattr(self, '_u_choice_started', time.process_time()), 1e-6))

    def _u_talk_inputs(self, g, q, candidates):
        # The question and actually heard situation are the only input here.
        view = TaskView((('g', 'list(list)'),), 'list', queries=((('g', LG.freeze(g)),),),
                        words=(TS.text(q),))
        views = [self._u_candidate_view(view, (cid, value), (value,)) for cid, value in candidates]
        return [PH.InnerJudge.features(f.detach().cpu().numpy()) for f, _ in self._u_reads(views)]

    def _u_talk_gap(self, g, q, rang):
        if not self._u_on('gap_syndromes'):
            return
        view = TaskView((('g', 'list(list)'),), 'list', queries=((('g', LG.freeze(g)),),),
                        words=(TS.text(g[0] if q is None else q),))
        concepts = self._concepts()
        candidates = tuple(LG.node('c', LG.node('var', payload='g'), payload=cid) for cid, _ in rang
                           if LG.fits(concepts.get('_sig', {}).get(cid, ('', '')), 'list(list)', 'list'))
        if not candidates:
            return
        features = self._u_reads([view], concepts)[0][0].detach().cpu().numpy()
        checks = self.field.curiosity.checks(view, candidates, concepts)
        gap = self.field.curiosity.decode(view, checks, features)
        if gap is not None and gap['inputs'] and getattr(self, '_u_talk_allowed', False):
            # The heard situation is the disagreeing input. The existing taught
            # conversation supplies its answer later, through _u_talk_correct.
            qid = self.field.ask('talk', 'candidate disagreement',
                                 'My fitting ideas disagree on this heard situation. What is its answer?',
                                 kind=gap_kind(view), inputs=gap['inputs'])
            self._u_talk_gap_request = dict(id=qid, view=view, candidates=candidates, gap=copy.deepcopy(gap))

    def _u_talk_work(self, g, q, got, cid, rang):
        """Recall alternatives and compose one executable step, using heard context."""
        self._u_choice_started = time.process_time()
        concepts = self._concepts()
        candidates = [(cid, got)] if got is not None and cid is not None else []
        for c, _ in rang:
            value = LG.safe(LG.node('c', LG.node('var', payload='g'), payload=c), {'g': g}, concepts)
            if TS.is_words(value) and (c, value) not in candidates:
                candidates.append((c, value))
        # One smallest typed composition, followed by reading the resulting words.
        ids = sorted(c for c in concepts if c != '_sig')
        for first in ids:
            sig = concepts['_sig'].get(first, ())
            if len(sig) != 2 or sig[0] != 'list(list)':
                continue
            for second in ids:
                other = concepts['_sig'].get(second, ())
                if len(other) != 2 or other != (sig[1], 'list'):
                    continue
                p = LG.node('c', LG.node('c', LG.node('var', payload='g'), payload=first), payload=second)
                value = LG.safe(p, {'g': g}, concepts)
                if TS.is_words(value):
                    candidates.append(((first, second), value))
                if len(candidates) >= ONE.TOP:
                    break
            if len(candidates) >= ONE.TOP:
                break
        if not candidates:
            self._u_last_talk = None
            return None, None, rang
        candidates = candidates[:ONE.TOP]
        kind = ('talk', tuple(q[:2]))
        xs = self._u_talk_inputs(g, q, candidates)
        probabilities = [self.field.inner.probability(kind, x) if self._u_on('inner_judge') else .5 for x in xs]
        j = min(range(len(candidates)), key=lambda i: (-probabilities[i], i))
        cid, got = candidates[j]
        x, p = xs[j], probabilities[j]
        action, f, _ = self.field.loop.pick(kind, x, p, {'answer', 'recall'}, np.random)
        token = (cid, LG.freeze(got))
        self.field.loop.remember(kind, token, action, f, 'recall')
        self._u_last_talk = dict(kind=kind, candidate=token, x=x, probability=p, answer=action == 'answer',
                                g=LG.freeze(g), q=LG.freeze(q), cid=cid, got=got)
        return got if action == 'answer' else None, cid, rang

    def _u_talk_tick(self, on_say=None):
        if not self._u_on('taught_not_yet'):
            return
        self.field.u7_turn += 1
        deadline = time.time()+getattr(self, '_u_pending_wall', 10.)
        # At most one charged work moment per pending question per incoming turn.
        # Their original heard situations stay intact; observer targets are absent.
        for item in list(self.field.u7_talk_pending):
            if time.time() >= deadline:
                break
            started = time.process_time()
            got, cid, rang = super().reply(item['g'], item['q'])
            got, cid, rang = self._u_talk_work(item['g'], item['q'], got, cid, rang)
            last = getattr(self, '_u_last_talk', None)
            if last is not None:
                token = last['candidate']
                saved = self.field.loop.withheld.get((last['kind'], token))
                if saved is not None:
                    self.field.loop.choice_learn(last['kind'], 'recall', saved[1],
                                                 -(time.process_time()-started))
            if got is not None:
                event = dict(id=item['id'], question=TS.text(item['q']), said=TS.text(got),
                             status='answered', asked_turn=item['asked_turn'], answered_turn=self.field.u7_turn,
                             delay_turns=self.field.u7_turn-item['asked_turn'])
                self.field.u7_talk_events.append(event)
                self.field.u7_talk_pending.remove(item)
                if on_say is not None:
                    on_say(event)

    def _u_talk_record(self, g, q, got, row):
        if not self._u_on('taught_not_yet'):
            return
        row['turn'] = self.field.u7_turn
        row['status'] = 'answered' if got is not None else 'not-yet'
        words = getattr(self.field, 'u7_words', ())
        row['response'] = TS.text(got) if got is not None else TS.text(words) if words else 'not-yet'
        if got is None:
            qid = 'talk-' + str(self.field.u7_turn)
            self.field.u7_talk_pending.append(dict(id=qid, g=LG.freeze(g), q=LG.freeze(q),
                                                   asked_turn=self.field.u7_turn, status='not-yet'))
            row['pending_id'] = qid
        else:
            row['answered_turn'] = self.field.u7_turn

    def reply(self, g, q=None):
        if not (self._u_on('inner_judge') or self._u_on('taught_not_yet')):
            result = super().reply(g, q)
            self._u_talk_gap(g, q, result[2])
            return result
        q = g[0] if q is None else q
        got, cid, rang = super().reply(g, q)
        self._u_talk_gap(g, q, rang)
        if self._u_on('taught_not_yet'):
            return self._u_talk_work(g, q, got, cid, rang)
        if cid is None:
            self._u_last_talk = None
            return got, cid, rang
        # Kind comes from the question's actually heard first two words; task
        # labels and the observer's per-item kind never enter this decision.
        kind = ('talk', tuple(q[:2]))
        x = self._u_talk_inputs(g, q, [(cid, got)])[0]
        token = (cid, LG.freeze(got))
        if self._u_bar_on():
            answer, p = self.field.inner.decide(kind, token, x)
        else:
            answer, p = True, self.field.inner.probability(kind, x)
        self._u_last_talk = dict(kind=kind, candidate=token, x=x, probability=p, answer=answer,
                                 g=LG.freeze(g), q=LG.freeze(q), cid=cid, got=got)
        return got if answer else None, cid, rang

    def converse(self, *args, **kwargs):
        events0 = len(self.field.u7_talk_events) if self._u_on('taught_not_yet') else 0
        if self._u_on('taught_not_yet'):
            self._u_pending_wall = kwargs.pop('pending_wall', 10.)
        if self._u_on('gap_syndromes'):
            self._u_talk_allowed = bool(kwargs.get('teaching', args[1] if len(args) > 1 else True))
            self.field.curiosity.surprises.clear()
        try:
            result = super().converse(*args, **kwargs)
        finally:
            self.__dict__.pop('_u_talk_allowed', None)
            self.__dict__.pop('_u_talk_gap_request', None)
            self.__dict__.pop('_u_pending_wall', None)
        if self._u_on('gap_syndromes'):
            result['u6'] = self.field.curiosity.report()
        if self._u_on('inner_judge'):
            result['u3'] = dict(inner=self.field.inner.report())
        if self._u_on('taught_not_yet'):
            result['u7'] = dict(delayed=copy.deepcopy(self.field.u7_talk_events[events0:]),
                                pending=copy.deepcopy(self.field.u7_talk_pending))
        return result

    def _u_talk_end_turn(self, q):
        if self._u_on('taught_not_yet'):
            self.field.loop.end_task(('talk', tuple(q[:2])))

    def _u_talk_correct(self, g, q, y, got, cid, said):
        request = self.__dict__.pop('_u_talk_gap_request', None)
        if self._u_on('gap_syndromes') and request is not None:
            view = request['view']
            answered = replace(view, examples=(((('g', LG.freeze(g)),), LG.freeze(y)),))
            checks = self.field.curiosity.checks(answered, request['candidates'], self._concepts())
            self.field.curiosity.finish(view.identity, request['gap'], checks,
                                        solved=bool(y is not None and got == y), search=0.)
            # No candidate/program standing comes from this question's answer.
            self.field.answer(request['id'], 'hint')
        last = getattr(self, '_u_last_talk', None)
        if not (self._u_on('inner_judge') or self._u_on('taught_not_yet')) or last is None:
            return
        inner, kind = self.field.inner, last['kind']
        # Even a withheld candidate gets the later teacher verdict. The grade
        # of an untaught item never calls this seam.
        right = last['got'] == y
        if self._u_on('gap_syndromes'):
            self.field.curiosity.verdict('exact:list(list)->list', last['probability'], bool(right), 'talk')
        if self._u_on('taught_not_yet'):
            self.field.loop.returned(kind, last['candidate'], bool(right), source='talk',
                                     elapsed=max(time.process_time()-getattr(self, '_u_choice_started', time.process_time()), 1e-6))
        if not self._u_on('inner_judge'):
            return
        inner.verdict(kind, last['candidate'], last['x'], bool(right), 'talk')
        if not right:
            good = [c for c in sorted(said) if said[c] == y and y is not None]
            corrected = (good[0] if good else None, y)
            x = self._u_talk_inputs(g, q, [corrected])[0]
            inner.verdict(kind, (corrected[0], LG.freeze(y)), x, True, 'talk', action=False)
            # A pair's logistic difference explicitly learns which is better.
            delta = x-last['x']
            w = inner.weights[kind]
            w += .35*(1.-1./(1.+np.exp(-np.clip(w @ delta, -30., 30.))))*delta
            inner.contrasts += 1

    def _reliable(self, c, frame, tally):
        if self._u_on('inner_judge') or self._u_on('taught_not_yet'):
            last = getattr(self, '_u_last_talk', None)
            if last is None:
                return True
            value = LG.safe(LG.node('c', LG.node('var', payload='g'), payload=c),
                            {'g': last['g']}, self.field.concept_table())
            x = self._u_talk_inputs(last['g'], last['q'], [(c, value)])[0]
            if self._u_on('taught_not_yet'):
                p = self.field.inner.probability(last['kind'], x) if self._u_on('inner_judge') else .5
                action, _, _ = self.field.loop.pick(last['kind'], x, p,
                                                    {'answer', 'recall'}, np.random)
                return action == 'answer'
            if not self._u_bar_on():
                return True
            return self.field.inner.probability(last['kind'], x) >= self.field.inner.bar(last['kind'])
        return super()._reliable(c, frame, tally)

    def _imagine(self, method, task, kind, leader, concepts, library, mu, st, hyps, extra, speak, known=()):
        if not (self._u_on('field_methods') or self._u_on('taught_not_yet')):
            return super()._imagine(method, task, kind, leader, concepts, library, mu, st, hyps, extra, speak, known)
        assignments = self.field.methods.assignments
        branch = assignments.pop(0)[1] if assignments else 0
        # Existing lab methods can build provisional concepts/senses or press
        # Ideas. Run each on a disposable symbolic copy with memory writes
        # detached, then expand the returned programs back to the real library.
        original, memory, pmemory = self.field, self.memory, self.proposer.memory
        original_memory_a = self.proposer.memory_a_enabled
        if pmemory is not None and getattr(pmemory, 'choosing', False):
            self.proposer.memory_a_enabled = pmemory.a
        prior_senses = {row['name'] for row in original.senses}
        if self._u_on('inner_judge'):
            local_switches = dict(self.u_switches)
            self.u_switches['inner_judge'] = False
        else:
            local_switches = None
        pfield = self.proposer.field
        saved = {k: v for k, v in self.__dict__.items() if k.startswith('_') and not k.startswith('_u_')}
        # Isolate mutable engine caches as well as its Field. In particular,
        # _footholds may alias the live st: copying only st would still write it.
        self.__dict__.update({k: copy.deepcopy(v) for k, v in saved.items()})
        saved_fragments = copy.deepcopy(self.proposer.fragments)
        saved_deadline = LG.DEADLINE[0]
        start = time.process_time()
        local = copy.deepcopy(st)
        self.field = copy.deepcopy(original)
        if pmemory is not None and getattr(pmemory, 'choosing', False):
            gate = BranchReadGate(pmemory)
            self.field._bridge = self.field.ideas._bridge = gate
        self.memory = self.proposer.memory = None
        self.proposer.field = self.field
        self._u_branch = branch
        self._u_branch_memory = pmemory
        try:
            out = super()._imagine(method, task, kind, leader, copy.deepcopy(concepts), library, mu,
                                   local, hyps, dict(extra), speak, known)
            proposed_senses = [copy.deepcopy(row) for row in self.field.senses if row['name'] not in prior_senses]
            if task.form == 'exact':
                temporary = self._concepts()
                temporary.update(concepts)
                expanded = {}
                for p, (origin, m) in out.items():
                    try:
                        expanded[expand(p, temporary)] = (origin, m)
                    except ValueError:      # it calls a concept this arm does not hold: it cannot run, so it is dropped
                        continue
                out = expanded
        finally:
            self.field, self.memory, self.proposer.memory = original, memory, pmemory
            self.proposer.memory_a_enabled = original_memory_a
            if local_switches is not None:
                self.u_switches = local_switches
            self.proposer.field = pfield
            self.proposer.fragments = saved_fragments
            for k in sorted(set(self.__dict__)-set(saved)):
                if k.startswith('_') and not k.startswith('_u_'):
                    self.__dict__.pop(k, None)
            self.__dict__.update(saved)
            self.__dict__.pop('_u_branch', None)
            self.__dict__.pop('_u_branch_memory', None)
            LG.DEADLINE[0] = saved_deadline
        # Actual public-example improvement per CPU second for this method,
        # not an identical global return credited to all three branches.
        evidence = (task.evidence(list(out), concepts, library, mu) if task.form == 'strengths'
                    else task.evidence(list(out), concepts))
        base = (task.evidence([leader], concepts, library, mu) if task.form == 'strengths'
                else task.evidence([leader], concepts)) if leader is not None else {}
        gain = max(evidence.values(), default=-TS.MISS_NATS)-max(base.values(), default=-TS.MISS_NATS)
        st.setdefault('u_method_returns', {}).setdefault(method, []).append(
            float(np.clip(gain/max(time.process_time()-start, 1e-6), -20., 40.)))
        if local.get('u_steps'):
            for p in out:
                st.setdefault('u_step_proposals', {})[p] = local['u_steps']
        candidates = list(out)
        if proposed_senses:
            for p in candidates:
                st.setdefault('u_sense_proposals', {})[p] = proposed_senses
        predictions = ([tuple(LG.safe(p, dict(b), concepts) for b, _ in TaskView.from_task(task).examples)
                        for p in candidates[:ONE.TOP]] if task.form == 'exact' else [])
        st.setdefault('u_branches', []).append(dict(branch=branch, method=method, hypothetical=True,
                                                   candidates=candidates, values=predictions))
        if task.form == 'exact':
            self.proposer.imagined = list(dict.fromkeys(self.proposer.imagined+candidates))
            for p in candidates:
                sig = LG.infer(p, concepts, arg=task.var)
                if sig is not None:
                    self.proposer.fragments.append(dict(ast=p, free=tuple(sorted(task.inputs.items())),
                                                        out=task.out, partial=False, hypothetical=True))
        if not original.methods.assignments:
            # Re-encode the method-driven outcomes together once all branches
            # have run; branch values stay conditional, with no event write.
            rows = st['u_branches'][-3:]
            base_view = TaskView.from_task(task)
            views = [self._u_candidate_view(base_view, row['candidates'][0],
                                            row['values'][0] if row['values'] else ())
                     if row['candidates'] else base_view for row in rows]
            reads = self._u_reads(views, concepts)
            for row, (f, _) in zip(rows, reads):
                row['field'] = f[row['branch']].detach().cpu().tolist()
        return out

    def _move(self, move, task, *args, **kwargs):
        if (self._u_on('field_methods') or self._u_on('taught_not_yet')) and move in ('dream', 'back', 'recall'):
            kind, focus, concepts, library, mu, st, hyps, extra, speak = args
            if move == 'dream':
                if not self.proposer.enabled:
                    return []
                view = TaskView.from_task(task)
                read = self._u_reads([view], concepts)[0]
                sketches = self.proposer.beam(view, concepts, tuple(task.numbers()),
                                             deadline=LG.DEADLINE[0], read=read,
                                             branch=getattr(self, '_u_branch', 0))
                return [(p, ('dreamed',)) for p in sketches]
            if move == 'back':
                return self._u_backward(task, concepts)
            branch_memory = getattr(self, '_u_branch_memory', self.memory)
            if move == 'recall' and branch_memory is not None and branch_memory.b:
                keys = [('concept', c) for c in sorted(self.field.proven_ideas())]
                view = TaskView.from_task(task)
                tokens = tuple(token for row in view.records(max_examples=max(4, len(view.examples)),
                                                             max_records=None)
                               for token, _, _, _ in row)
                rang = self.field.ideas.evoked(tuple(task.words)+tokens, keys)
                if task.form == 'exact':
                    return [(LG.node('c', LG.node('var', payload=task.var), payload=k[1]), ('ring', k[1]))
                            for k, _ in rang
                            if LG.fits(concepts['_sig'][k[1]], task.inputs[task.var], task.out)]
                return [(((ch, 'concept', k[1]),), ('ring', k[1])) for k, _ in rang
                        if tuple(concepts['_sig'][k[1]]) == ('num', 'num') for ch in self._channels()]
        return self._observed_move(move, task, *args, **kwargs)

    def _u_backward(self, task, concepts):
        var = task.var
        xs = [LG.freeze(x) for x, _ in task.data]
        ctx = dict(task=task, concepts=concepts, pairs=list(task.data), where=list(range(len(xs))),
                   xs=xs, constants=tuple(task.numbers()), tout=task.out,
                   names=self.field.names(), teaching=False)
        got = self._backward(ctx, var, task.inputs[var], xs, LG.DEADLINE[0])
        return [] if got is None else [(got[0], ('imagined back',))]

    def _step(self, task, concepts, speak, have, st):
        if not (self._u_on('field_roadmap') or self._u_on('taught_not_yet')):
            return super()._step(task, concepts, speak, have, st)
        saved = LG.DEADLINE[0]
        self._step_cut = False
        try:
            return self._roadmap(task, concepts, speak, st)
        finally:
            LG.DEADLINE[0] = saved

    def _dream_roadmap(self, view, concepts, read, until):
        if not self.proposer.enabled:
            return []
        sketches = []
        for branch in range(3):
            sketches += self.proposer.beam(view, concepts, deadline=until, read=read, branch=branch)[:1]
        return list(dict.fromkeys(sketches))

    def _roadmap(self, task, concepts, speak, st):
        view = TaskView.from_task(task)
        # A time/work bound prevents an infinite hypothetical loop. It imposes
        # no decomposition order and does not enumerate a future step plan.
        until = min(LG.DEADLINE[0], time.time()+ONE.STEP_MAX)
        definitions, selected, seen = {}, [], set()
        root_probes = [dict(p) for p in task.probes()]
        original_xs = [p[task.var] for p in root_probes]
        for x, _ in task.data:
            if x not in original_xs:
                original_xs.append(x)
                root_probes.append({task.var: x})
        probes = copy.deepcopy(root_probes)
        where = [original_xs.index(x) for x, _ in task.data]
        inputs = dict(task.inputs)
        while time.time() < until:
            read = self._u_reads([view], concepts)[0]
            self.field.steps.bind(read[0].detach().cpu().numpy())
            sketches = self._dream_roadmap(view, concepts, read, until)
            expected = [tuple(LG.safe(p, dict(b), concepts) for b, _ in view.examples) for p in sketches]
            if self._u_on('gap_syndromes') and hasattr(self, '_u_gap_context'):
                for p, predictions in zip(sketches, expected):
                    for (bindings, _), prediction in zip(view.examples, predictions):
                        try:
                            computed = independent(p, dict(bindings), concepts)
                        except (ValueError, KeyError, *LG.BAD):
                            computed = None
                        self._u_gap_context['roadmap'].append((p, bindings, prediction, computed))
            st.setdefault('u_roadmap', []).append(dict(what='dream', hypothetical=True,
                                                     sketches=sketches, values=expected, inputs=tuple(sorted(inputs))))
            for sketch in sketches:
                program = sketch
                for name, body in reversed(list(definitions.items())):
                    program = ONE._put(program, name, body)
                if task.consistent(program, concepts):
                    # Only this call can accept. No intermediate gets standing.
                    st['u_steps'] = selected
                    if hasattr(self, '_u_branch') or self._u_on('taught_not_yet'):
                        return [(program, ('roadmap', len(selected)))]
                    accepted = self._prove(task, program, concepts, self.field.concept_table(), st, speak)
                    if accepted:
                        return [(program, ('roadmap', len(selected)))]
                    return []  # outer counterexample is handled by the live loop
            # Every full sketch failed publicly. Select exactly one next step.
            ctx = dict(task=task, concepts=concepts, pairs=list(task.data), where=where,
                       xs=original_xs, constants=tuple(task.numbers()), tout=task.out,
                       sf=self.field.steps, rng=np.random.default_rng([self.seed, st['steps'], 29]),
                       names=self.field.names(), teaching=st.get('teaching'), speak=speak)
            if not sketches:
                return []
            # The settled readout now sees EACH sketch's predicted values
            # beside the public outputs it failed to match. The existing five
            # StepField coordinates stay unchanged; the Field learns where
            # the gap is and which one fragment helped to close it.
            gaps = [self._u_candidate_view(view, p, vals) for p, vals in zip(sketches, expected)]
            gap_reads = self._u_reads(gaps, concepts)
            self.field.steps.bind(np.stack([gap_reads[j % len(gap_reads)][0][j].detach().cpu().numpy()
                                            for j in range(3)]))
            candidates = self._step_candidates(ctx, inputs, probes, until)
            candidates = [c for c in candidates if repr(c[0]) not in seen
                          and not any(c[2] == [p[name] for p in probes] for name in sorted(inputs))]
            if not candidates:
                return []
            worked = getattr(task, 'worked', None)
            if st.get('teaching') and worked is not None:
                taught = [worked(x) for x, _ in task.data]
                for c in candidates:
                    if all(w is not None and any(c[3][j] == value for value in w)
                           for j, w in enumerate(taught)):
                        self.field.steps.teach(c[4], 1.)
            rng = np.random.default_rng([self.seed, st['steps'], len(selected), 31])
            scores = [self.field.steps.score(c[4], rng) for c in candidates]
            j = sorted(range(len(candidates)), key=lambda k: (-scores[k], repr(candidates[k][0])))[0]
            e, typ, vals, made, f = candidates[j]
            selected.append(self.field.steps.features(f).copy())
            seen.add(repr(e))
            name = 'u_next'
            while name in inputs:
                name += "'"
            definitions[name] = e
            inputs[name] = typ
            probes = [dict(p, **{name: v}) for p, v in zip(probes, vals)]
            examples = tuple((tuple(sorted(probes[j].items())), y) for j, (_, y) in zip(where, task.data))
            view = replace(view, inputs=tuple(sorted(inputs.items())), examples=examples,
                           queries=tuple(tuple(sorted(p.items())) for p in probes))
            st['u_roadmap'].append(dict(what='next', step=e, values=made, hypothetical=True))
            # Re-enter at the WHOLE dream; never choose a second step first.
        return []

    def _things(self, task, ctx):
        if self.memory is not None and self.memory.context is not None:
            ctx = self.memory.context[1]
        return super()._things(task, ctx)

    def _lay_in_world(self, task, ctx, *args, **kwargs):
        if self.memory is not None and self.memory.context is not None:
            ctx = self.memory.context[1]
        return super()._lay_in_world(task, ctx, *args, **kwargs)

    def _doubt_after(self, task, *args, **kwargs):
        if self.memory is not None:
            self.memory.refresh(TaskView.from_task(task))
        return super()._doubt_after(task, *args, **kwargs)

    def _finish(self, task, *args, **kwargs):
        if self.memory is not None:
            self.memory.refresh(TaskView.from_task(task))
        result = super()._finish(task, *args, **kwargs)
        st = args[4]
        if self._u_on('gap_syndromes') and hasattr(self, '_u_gap_context'):
            context = self._u_gap_context
            accepted = None if st.get('proven') is None else st['proven']['law']
            checks = self._u_syndrome(task, context['candidates'], context.get('log_u', {}),
                                      context.get('log_b', {}), accepted=accepted, final=True)
            self.field.curiosity.finish(context['view'].identity, context['gap'], checks,
                                        solved=bool(st.get('proven')),
                                        search=max(0., self.proposer.stats['search']-context['search']))
            self.field.curiosity.decode(context['view'], checks, context['features'])
            result['u6'] = self.field.curiosity.report()
        if any(self._u_on(k) for k in U3_CRUTCHES):
            result['u3'] = dict(branches=st.get('u_branches', []), roadmap=st.get('u_roadmap', []),
                                inner=self.field.inner.report() if self._u_on('inner_judge') else None)
        if self._u_on('taught_not_yet'):
            result['u7'] = dict(state='right' if result['proven'] else 'not-yet',
                                time_to_right=st.get('u_time_to_right') if result['proven'] else None,
                                moments=st.get('u_not_yet', []),
                                wrong_attempts=max(0, sum(m['action'] == 'answer' for m in st.get('u_not_yet', []))
                                                  - int(result['proven'])))
            if not result['proven']:
                result['candidate'] = result['answer']
                result['answer'] = None
                result['verdict'] = 'not-yet'
            self.field.log[-1].update(verdict=result['verdict'], status=result['u7']['state'])
        return result

    def _observed_move(self, move, task, *args, **kwargs):
        result = super()._move(move, task, *args, **kwargs)
        if self.memory is not None:
            self.memory.refresh(TaskView.from_task(task))
        return result

    def _prove(self, task, leader, *args, **kwargs):
        result = super()._prove(task, leader, *args, **kwargs)
        st = args[2]
        choice_active = self.memory is not None and getattr(self.memory, 'choosing', False)
        if result and (self._u_on('taught_not_yet') or choice_active) and time.time() > LG.DEADLINE[0]:
            st['proven'], result = None, False
        if result and choice_active and self.memory.time_to_right is None:
            self.memory.time_to_right = time.perf_counter()-self.memory.item_started
        if result and self._u_on('taught_not_yet'):
            st['u_time_to_right'] = time.perf_counter()-getattr(self, '_u_item_started', time.perf_counter())
        if result and task.form == 'strengths':
            for row in st.get('u_sense_proposals', {}).get(leader, []):
                if any(part[0] == row['name'] for part in leader):
                    if not any(old['name'] == row['name'] for old in self.field.senses):
                        self.field.senses.append(copy.deepcopy(row))
                    if row['name'] not in self._task_senses:
                        self._task_senses.append(row['name'])
        if self._u_on('field_roadmap') or self._u_on('taught_not_yet'):
            used = st.pop('u_steps', []) or st.get('u_step_proposals', {}).pop(leader, [])
            for f in used:
                self.field.steps.learn(f, 1. if result else -1.)
        if self.memory is not None:
            # Outer acceptance is observed evidence. Observer grades are not read.
            self.memory.event('audit-result', (leader, bool(result)), progress=1. if result else None)
            self.memory.refresh(TaskView.from_task(task))
        return result

    def _refute(self, task, key, st, *args, **kwargs):
        already = key in st.get('refuters', set())
        result = super()._refute(task, key, st, *args, **kwargs)
        if not already:
            self._u_verdict(task, key[1], False, 'refutation')
        if self.memory is not None and not already:
            # A live counterexample remains an association, not an extra standing vote.
            self.memory.event('counterexample', key, progress=-1.)
            self.memory.refresh(TaskView.from_task(task))
        return result

    def _correct(self, words, frame, y, got, cid, *args, **kwargs):
        if self.memory is not None:
            # Only converse(teaching=True) calls this teacher-feedback seam.
            self.memory.event('teacher-verdict', (tuple(sorted(words, key=repr)), y, got, cid),
                              progress=1. if y == got else -1.)
        return super()._correct(words, frame, y, got, cid if type(cid) is int else None, *args, **kwargs)

    def _wish(self, *args, **kwargs):
        roadmap = getattr(self.field, 'roadmap_readout', None)
        if roadmap is not None and args and args[0].form == 'exact' and len(args[0].inputs) == 1:
            task = args[0]
            roadmap.wish((next(iter(task.inputs.values())), task.out),
                         digest((tuple(sorted(task.inputs.items())), task.out, task.data)))
        return super()._wish(*args, **kwargs) if self.library_enabled else []

    def _build(self, *args, **kwargs):
        return super()._build(*args, **kwargs) if self.library_enabled else None

    def _invent_part(self, *args, **kwargs):
        return super()._invent_part(*args, **kwargs) if self.library_enabled else None


def validate_carry_shapes(payload):
    """Reject unknown object slots using the new body's declared vocabulary.

    Dynamic dictionary entries (laws, words, policies) are learned data, but an
    unknown owner/Field/engine member is a code migration requiring a new rule.
    """
    import ast
    root = Path(__file__).resolve().parents[1]
    known = set()
    # Every module whose objects a life can retain (a talk Lexicon lives in the Field): the body's whole vocabulary.
    for relative in sorted(str(p.relative_to(root)) for folder in ('sera', 'sera_u') for p in (root/folder).glob('*.py')):
        tree = ast.parse((root/relative).read_text(encoding='utf-8-sig'))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                known.update(child.target.id for child in node.body if isinstance(child, ast.AnnAssign)
                             and isinstance(child.target, ast.Name))
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == 'self':
                known.add(node.attr)
            # Members a body sets on another object (`self.field.rates = []`, `F.off_choice_rates`) are code too.
            if isinstance(node, ast.Attribute) and isinstance(node.ctx, ast.Store):
                known.add(node.attr)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ('setattr', 'getattr', 'hasattr'):
                if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant) and isinstance(node.args[1].value, str):
                    known.add(node.args[1].value)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'setdefault':
                if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                    known.add(node.args[0].value)
    # Field attachments made by the body rather than Field's own methods.
    known.update(('einstein_methods', 'scientist_methods', 'darwin_methods', 'roadmap_readout',
                  'hologram', 'inner', 'curiosity', 'memory_choice', 'revisit_queue',
                  'u7_revisits_solved', 'u7_talk_pending', 'u7_talk_events', 'u7_turn',
                  'field_understanding', 'u_schema', '_task_senses'))
    groups = {'field': payload['field'].__dict__, 'engine': payload['engine'],
              'proposer': payload['proposer']}
    if 'discovery' in payload:
        groups['discovery'] = payload['discovery'].__dict__
        for name in ('einstein', 'scientists', 'darwin', 'roadmap'):
            if hasattr(payload['discovery'], name):
                groups[name] = getattr(payload['discovery'], name).__dict__
    for name, state in groups.items():
        unknown = set(state)-known
        if unknown:
            raise ValueError('Unknown '+name+' carry shape: '+repr(sorted(unknown)))
    seen = set()
    def inspect_nested(value):
        if id(value) in seen:
            return
        seen.add(id(value))
        if isinstance(value, (torch.Tensor, np.ndarray)):
            return
        if isinstance(value, dict):
            for item in value.values():
                inspect_nested(item)
        elif isinstance(value, (list, tuple, set)):
            for item in sorted(value, key=repr) if isinstance(value, set) else value:
                inspect_nested(item)
        elif hasattr(value, '__dict__') and type(value).__module__.startswith(('sera.', 'sera_u.')):
            if type(value).__module__.startswith('sera_u.field.'):
                raise ValueError('Unknown retained native object shape')
            if type(value) is TaskView:
                if set(value.__dict__) != set(TaskView.__dataclass_fields__):
                    raise ValueError('Unknown public-view carry shape')
            else:
                unknown = set(value.__dict__)-known
                if unknown:
                    raise ValueError('Unknown nested carry shape: '+repr(sorted(unknown)))
            from .discovery import Readout
            if isinstance(value, Readout):
                for table in (value.own, value.taught):
                    for pair in table.values():
                        if not isinstance(pair, (tuple, list)) or len(pair) != 2 or \
                                not all(isinstance(a, np.ndarray) for a in pair) or \
                                pair[0].shape != (65, 65) or pair[1].shape != (65,) or \
                                not all(np.isfinite(a).all() for a in pair):
                            raise ValueError('Unknown learned policy shape')
            inspect_nested(value.__dict__)
    for name in ('field', 'discovery', 'agenda', 'holes', 'work_policy'):
        if name in payload:
            inspect_nested(payload[name])


class _CanonicalSet(set):
    def __reduce__(self):
        return set, (sorted(self, key=repr),)


def canonical_payload(value, visited=None):
    """Stable pickle ordering on a detached checkpoint copy, including sets."""
    visited = {} if visited is None else visited
    if id(value) in visited:
        return visited[id(value)]
    if type(value) is str:
        # Pickle shares a string by object identity: a reloaded key 'cpu' is a fresh object where the running one is
        # the interned 'cpu' torch also names a storage location with, so the same state saved 8 bytes apart (development review).
        return sys.intern(value)
    if (isinstance(value, np.ndarray) and value.dtype.kind in 'biufc' and value.dtype.fields is None
            and value.dtype == np.dtype(value.dtype.type)):
        # The same holds for a reloaded array's dtype, an equal copy of numpy's shared one (numpy no longer calls it
        # builtin): rebuild plain numeric arrays on the shared dtype.
        result = value.astype(value.dtype.type)
        visited[id(value)] = result
        return result
    if isinstance(value, np.random.Generator) and isinstance(value.bit_generator.seed_seq, np.random.SeedSequence):
        # A reloaded generator's seed pool is such an array too: rebuild it from its seed, then its exact state.
        bits, seq = value.bit_generator, value.bit_generator.seed_seq
        result = np.random.Generator(type(bits)(np.random.SeedSequence(
            entropy=seq.entropy, spawn_key=seq.spawn_key, pool_size=seq.pool_size,
            n_children_spawned=seq.n_children_spawned)))
        result.bit_generator.state = bits.state
        visited[id(value)] = result
        return result
    if isinstance(value, (torch.Tensor, np.ndarray)) or type(value) in (bytes, int, float, bool, type(None)):
        return value
    if isinstance(value, set):
        result = _CanonicalSet(canonical_payload(v, visited) for v in sorted(value, key=repr))
        visited[id(value)] = result
        return result
    if isinstance(value, dict):
        visited[id(value)] = value
        # Dictionary insertion order can be learned chronology (for example,
        # the latest fitted quantity). Preserve it across a save/reload.
        items = [(canonical_payload(k, visited), canonical_payload(v, visited)) for k, v in value.items()]
        value.clear()
        value.update(items)
        return value
    if isinstance(value, list):
        visited[id(value)] = value
        value[:] = [canonical_payload(v, visited) for v in value]
    elif isinstance(value, tuple):
        value = tuple(canonical_payload(v, visited) for v in value)
    elif hasattr(value, '__dict__') and type(value).__module__.startswith(('sera.', 'sera_u.')):
        visited[id(value)] = value
        canonical_payload(value.__dict__, visited)
    return value


class AssessmentTask:
    """Read-only observer adapter: judge verdicts, no audit counterexample feedback.

    This object is passed to the lab engine, never to the Field. Hidden scoring
    is done separately by the observer after the trial. Allowed queries are
    disabled for this reserved, fixed-public-example protocol.
    """
    def __init__(self, task):
        self._judge = copy.deepcopy(task)
        for name in ('inputs', 'out', 'var', 'data', 'words', 'subject', 'name', 'form', '_probe_inputs'):
            setattr(self, name, copy.deepcopy(getattr(task, name)))

    def probes(self):
        return [{self.var: x} for x in self._probe_inputs]

    def context(self):
        from sera.tasks import Exact
        return Exact.context(self)

    def numbers(self):
        from sera.tasks import numbers_of
        return numbers_of(self.data)

    def consistent(self, p, concepts):
        return all(LG.safe(p, {self.var: x}, concepts) == y for x, y in self.data)

    def evidence(self, exprs, concepts):
        from sera.tasks import MISS_NATS
        return {p: -MISS_NATS*sum(LG.safe(p, {self.var: x}, concepts) != y for x, y in self.data) for p in exprs}

    def actions(self, *args, **kwargs):
        return []

    def explore(self, *args, **kwargs):
        return None

    def verify(self, p, concepts, bits, rng):
        ok, n, _ = self._judge.verify(p, concepts, bits, rng)
        return ok, n, None                 # failing input and its hidden answer never leave the judge

    def grade(self, p, concepts, accepted, **kwargs):
        return dict(verdict='proven right' if accepted else 'not proven')

    def teacher_truth(self, word):
        return False                       # no teacher in an assessment: as an exact task, only its own words


class SeraU:
    @work_constructor
    def __init__(self, seed=3, *, device='cpu', config=None, arm='full', field=None, crutches=None,
                 batched_reads=True, discovery=None, einstein=None, scientists=None, darwin=None, roadmap=None,
                 wiring=False, clock='wall', u14=None):
        if clock not in ('work', 'wall'):
            raise ValueError('Unknown learner clock')
        self.clock_mode = clock
        self.u14 = {k: CR.on(k) for k in U14_CRUTCHES} if u14 is None else dict(u14)
        if set(self.u14) != set(U14_CRUTCHES) or any(type(v) is not bool for v in self.u14.values()):
            raise ValueError('Declare all boolean U14 switches')
        if clock == 'work':
            from .discovery import Readout
            self.clock, self.work_policy = Clock(), Readout()
        if any(self.u14.values()):
            from .agenda import Agenda
            self.agenda = Agenda()
            from .holes import Holes
            self.holes = Holes(self.u14)
        self.wiring = bool(wiring)
        if type(batched_reads) is not bool:
            raise ValueError('batched_reads must be boolean')
        self.batched_reads = batched_reads
        self.seed, self.arm, self.device = seed, arm, torch.device(device)
        self.crutches = arm_settings(arm) if crutches is None else dict(crutches)
        discovery_switches = ({k: CR.on(k) for k in U9_CRUTCHES} if discovery is None else dict(discovery))
        if set(discovery_switches) != set(U9_CRUTCHES) or any(type(v) is not bool for v in discovery_switches.values()):
            raise ValueError('Declare the registered boolean discovery crutches')
        # No entity, RNG draw, port, extra record or payload slot on the old path.
        self.discovery = Discovery(discovery_switches, einstein=einstein, scientists=scientists, darwin=darwin, roadmap=roadmap) if discovery_switches['open_worlds'] else None
        if self.discovery is not None and self.wiring:
            self.discovery._wiring_enabled = True
        self.u8_declared = 'memory_choice' in self.crutches
        memory_choice = self.crutches.pop('memory_choice', False)
        self.u7_declared = any(k in self.crutches for k in U7_CRUTCHES)
        if set(self.crutches) == set(U1_CRUTCHES):
            self.crutches.update({k: False for k in U2_CRUTCHES})
        if set(self.crutches) == set(U1_CRUTCHES+U2_CRUTCHES):
            self.crutches.update({k: False for k in U3_CRUTCHES+U6_CRUTCHES+U7_CRUTCHES})
        if set(self.crutches) == set(U1_CRUTCHES+U2_CRUTCHES+U3_CRUTCHES):
            self.crutches.update({k: False for k in U6_CRUTCHES})
        if set(self.crutches) == set(U1_CRUTCHES+U2_CRUTCHES+U3_CRUTCHES+U6_CRUTCHES):
            self.crutches.update(taught_not_yet=False, abstain_bar=self.crutches['inner_judge'])
        if self.u8_declared:
            self.crutches.update(memory_choice=memory_choice)
        expected = U_CRUTCHES if self.u8_declared else U_CRUTCHES[:-1]
        if set(self.crutches) != set(expected) or any(type(v) is not bool for v in self.crutches.values()):
            raise ValueError('Declare the registered boolean U crutches')
        self.source = source_identity()
        self.code = code_identity()
        self.config = config or NativeConfig(nodes=4, rounds=1)
        outside = global_rng()
        try:
            os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
            torch.use_deterministic_algorithms(True)
            torch.backends.cudnn.benchmark = False
            torch.backends.cudnn.deterministic = True
            random.seed(seed)
            np.random.seed(seed)
            torch.manual_seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(seed)
            self.owner = FieldOwner(self.config).to(self.device)
            self.owner.port_enabled = self.crutches['field_input_ports']
            self.optimizer = torch.optim.AdamW(self.owner.parameters(), lr=.001, weight_decay=.0001)
            self.field = copy.deepcopy(field) if field is not None else PH.Field(seed)
            if hasattr(self.field, 'einstein_methods') and not (self.discovery is not None
                                                                and hasattr(self.discovery, 'einstein')):
                raise ValueError('U10-off requires its own U9 history')
            if getattr(self.field, 'field_understanding', False) and not self.crutches['field_understanding']:
                raise ValueError('Understanding-off requires its own fresh legacy history')
            if not self.crutches['sleep_library']:
                self.field.concepts = []
            if any(self.crutches[k] for k in U2_CRUTCHES) or self.crutches.get('memory_choice', False):
                self.field = MemoryField.adopt(self.field, self.crutches['field_understanding'])
            if self.crutches.get('memory_choice', False):
                if not hasattr(self.field, 'memory_choice'):
                    self.field.memory_choice = PH.MemoryChoice()
            elif hasattr(self.field, 'memory_choice'):
                raise ValueError('Memory-choice-off requires its own fixed memory history')
            if self.discovery is not None and hasattr(self.discovery, 'einstein'):
                # After MemoryField.adopt (it rebuilds the Field): the Field holds the very head discovery trains.
                self.field.einstein_methods = self.discovery.einstein.methods
            if self.discovery is not None and hasattr(self.discovery, 'scientists'):
                self.field.scientist_methods = self.discovery.scientists.methods
            elif hasattr(self.field, 'scientist_methods'):
                raise ValueError('U11-off requires its own U10 history')
            if self.discovery is not None and hasattr(self.discovery, 'darwin'):
                self.discovery.darwin.attach(self.field)
            elif hasattr(self.field, 'hologram'):
                raise ValueError('U12-off requires its own fresh history')
            if self.discovery is not None and hasattr(self.discovery, 'roadmap'):
                previous = getattr(self.field, 'roadmap_readout', None)
                if previous is not None and previous.switches != self.discovery.roadmap.switches:
                    raise ValueError('U13 ablation requires its own fresh history')
                self.discovery.roadmap.attach(self.field)
            elif hasattr(self.field, 'roadmap_readout'):
                raise ValueError('U13-off requires its own fresh history')
            if hasattr(self.field, 'curiosity') and not self.crutches['gap_syndromes']:
                raise ValueError('Curiosity-off requires its own U3 history')
            self.proposer = Proposer(self.owner, self.field, enabled=self.crutches['field_proposer'])
            self.proposer.memory_a_enabled = self.crutches['memory_layer_a']
            for switch, slot, cls in (('field_ways', 'loop', PH.FieldWays),
                                      ('field_methods', 'methods', PH.FieldMethods),
                                      ('field_roadmap', 'steps', PH.FieldSteps)):
                if self.crutches[switch] and not isinstance(getattr(self.field, slot), cls):
                    setattr(self.field, slot, cls())
                if not self.crutches[switch] and not self.crutches['taught_not_yet'] and isinstance(getattr(self.field, slot), cls):
                    raise ValueError('Readout-off requires its own legacy history')
            if self.crutches['taught_not_yet']:
                if not isinstance(self.field.loop, PH.NotYetWays):
                    ways = PH.NotYetWays()
                    if isinstance(self.field.loop, PH.FieldWays):
                        ways.__dict__.update(copy.deepcopy(self.field.loop.__dict__))
                    self.field.loop = ways
                if not isinstance(self.field.methods, PH.FieldMethods):
                    self.field.methods = PH.FieldMethods()
                if not isinstance(self.field.steps, PH.FieldSteps):
                    self.field.steps = PH.FieldSteps()
                self.field.__dict__.setdefault('revisit_queue', [])
                self.field.__dict__.setdefault('u7_revisits_solved', 0)
                self.field.__dict__.setdefault('u7_talk_pending', [])
                self.field.__dict__.setdefault('u7_talk_events', [])
                self.field.__dict__.setdefault('u7_turn', 0)
            elif isinstance(self.field.loop, PH.NotYetWays):
                raise ValueError('Not-yet-off requires its own history')
            if (self.crutches['inner_judge'] or self.crutches['taught_not_yet']) and not hasattr(self.field, 'inner'):
                self.field.inner = PH.InnerJudge()
            if self.crutches['gap_syndromes'] and not hasattr(self.field, 'curiosity'):
                self.field.curiosity = Curiosity()
            self.engine = Engine(seed, self.field, self.proposer, self.crutches['sleep_library'])
            self.engine.u_switches = {k: self.crutches[k] for k in U3_CRUTCHES+U6_CRUTCHES+U7_CRUTCHES}
            self.state = detached_state(self.owner.empty(1))
            self.proposer.retained = self.state
            self.rngs = global_rng()
        finally:
            restore_rng(outside)
        self.random = random.Random(seed)
        self.numpy = np.random.default_rng(seed)
        self.torch_generator = torch.Generator(device=self.device).manual_seed(seed)
        self.updates = 0
        self.checked_wake = set()
        self.sleep = Sleep(self)
        self.progress = {}                  # runner cursor, hashed frozen protocol, cost accounting
        self.word_symbols = dict(vocab=copy.deepcopy(TS.VOCAB), words=copy.deepcopy(TS.WORDS), next=list(TS._NEXT))
        self.book = copy.deepcopy(TK.BOOK)
        self._active = False
        self.memory = Memory(self)
        if sum(p.numel() for p in self.owner.parameters()) > 1_200_000:
            raise ValueError('S28 pilot owner exceeds 1.2 million parameters')

    @contextmanager
    def scope(self):
        outside = global_rng()
        on, off = set(CR.ON), set(CR.OFF)
        symbolic = (TS.VOCAB, TS.WORDS, TS._NEXT)
        book = TK.BOOK
        memory_limit = LG._MEMORY.get('limit')
        had_memory_limit = 'limit' in LG._MEMORY
        counts = LG.EXECUTION_COUNTS
        work_scope = activate(self)
        work_scope.__enter__()
        try:
            if bool(getattr(self.field, 'field_understanding', False)) != self.crutches['field_understanding']:
                raise ValueError('Understanding switch changed; start a fresh history')
            if hasattr(self.field, 'memory_choice') != self.crutches.get('memory_choice', False):
                raise ValueError('Memory-choice switch changed; start a fresh history')
            restore_rng(self.rngs)
            scoped = ((U1_CRUTCHES+U2_CRUTCHES) if any(self.crutches[k] for k in U2_CRUTCHES)
                      else U1_CRUTCHES) + (U3_CRUTCHES if any(self.crutches[k] for k in U3_CRUTCHES) else ()) + (U6_CRUTCHES if any(self.crutches[k] for k in U6_CRUTCHES) else ()) + (U7_CRUTCHES if self.u7_declared else ())
            if self.u8_declared:
                scoped += U8_CRUTCHES
            CR.ON = (on-set(U_CRUTCHES)) | {k for k in scoped if self.crutches[k]}
            CR.OFF = (off-set(U_CRUTCHES)) | {k for k in scoped if not self.crutches[k]}
            if any(self.u14.values()):
                CR.ON = (CR.ON-set(U14_CRUTCHES)) | {k for k, v in self.u14.items() if v}
                CR.OFF = (CR.OFF-set(U14_CRUTCHES)) | {k for k, v in self.u14.items() if not v}
            if self.discovery is not None:
                CR.ON = (CR.ON-set(U9_CRUTCHES)) | {k for k, v in self.discovery.switches.items() if v}
                CR.OFF = (CR.OFF-set(U9_CRUTCHES)) | {k for k, v in self.discovery.switches.items() if not v}
                if hasattr(self.discovery, 'einstein'):
                    from .einstein import CRUTCHES as U10_CRUTCHES
                    ways = self.discovery.einstein.switches
                    CR.ON = (CR.ON-set(U10_CRUTCHES)) | {k for k, v in ways.items() if v}
                    CR.OFF = (CR.OFF-set(U10_CRUTCHES)) | {k for k, v in ways.items() if not v}
                if hasattr(self.discovery, 'scientists'):
                    from .scientists import CRUTCHES as U11_CRUTCHES
                    habits = self.discovery.scientists.switches
                    CR.ON = (CR.ON-set(U11_CRUTCHES)) | {k for k, v in habits.items() if v}
                    CR.OFF = (CR.OFF-set(U11_CRUTCHES)) | {k for k, v in habits.items() if not v}
                if hasattr(self.discovery, 'darwin'):
                    from .darwin import CRUTCHES as U12_CRUTCHES
                    habits = self.discovery.darwin.switches
                    CR.ON = (CR.ON-set(U12_CRUTCHES)) | {key for key, value in habits.items() if value}
                    CR.OFF = (CR.OFF-set(U12_CRUTCHES)) | {key for key, value in habits.items() if not value}
                if hasattr(self.discovery, 'roadmap'):
                    from .roadmap import CRUTCHES as U13_CRUTCHES
                    habits = self.discovery.roadmap.switches
                    CR.ON = (CR.ON-set(U13_CRUTCHES)) | {key for key, value in habits.items() if value}
                    CR.OFF = (CR.OFF-set(U13_CRUTCHES)) | {key for key, value in habits.items() if not value}
            TS.VOCAB, TS.WORDS, TS._NEXT = (copy.deepcopy(self.word_symbols['vocab']),
                                          copy.deepcopy(self.word_symbols['words']), list(self.word_symbols['next']))
            TK.BOOK = self.book
            self.owner.port_enabled = self.crutches['field_input_ports']
            self.proposer.enabled = self.crutches['field_proposer']
            self.proposer.memory_a_enabled = self.crutches['memory_layer_a']
            self.engine.library_enabled = self.crutches['sleep_library']
            if self.engine.u_switches != {k: self.crutches[k] for k in U3_CRUTCHES+U6_CRUTCHES+U7_CRUTCHES}:
                raise ValueError('Readout switches changed; start a fresh history')
            LG._MEMORY['limit'] = 2048.
            LG.EXECUTION_COUNTS = dict(interpreter_calls=0, interpreter_steps=0, primitive_calls=0)
            if any(self.crutches[k] for k in U2_CRUTCHES) or self.crutches.get('memory_choice', False):
                switches = self.field.ideas.u_memory_switches()
                if switches != {k: self.crutches[k] for k in U1_CRUTCHES+U2_CRUTCHES}:
                    raise ValueError('Memory ledger and entity switches disagree')
                self.proposer.memory = self.engine.memory = self.memory
                self.field._bridge = self.field.ideas._bridge = self.memory
            yield
        finally:
            self.proposer.memory = self.engine.memory = None
            self.engine.__dict__.pop('_u_last_talk', None)
            self.engine.__dict__.pop('_u_predictions', None)
            self.engine.__dict__.pop('_u_gap_context', None)
            self.engine.__dict__.pop('_u_talk_gap_request', None)
            self.engine.__dict__.pop('_u_talk_allowed', None)
            self.engine.__dict__.pop('_u_phase_name', None)
            self.engine.__dict__.pop('_u_item_started', None)
            self.engine.__dict__.pop('_u_choice_started', None)
            self.field.__dict__.pop('_bridge', None)
            self.field.ideas.__dict__.pop('_bridge', None)
            self.memory.current = None
            self.memory.context = None
            self.memory.seen_records.clear()
            self.memory.checked_parts.clear()
            self.memory.clear_reads()
            self.memory._prepared = None
            self.memory.reset_choice()
            self.proposer._feature_cache.clear()
            self.owner.clear_readouts()
            self.rngs = global_rng()
            restore_rng(outside)
            CR.ON, CR.OFF = on, off
            self.word_symbols = dict(vocab=TS.VOCAB, words=TS.WORDS, next=TS._NEXT)
            TS.VOCAB, TS.WORDS, TS._NEXT = symbolic
            self.book, TK.BOOK = TK.BOOK, book
            if had_memory_limit:
                LG._MEMORY['limit'] = memory_limit
            else:
                LG._MEMORY.pop('limit', None)
            LG.EXECUTION_COUNTS = counts
            work_scope.__exit__(None, None, None)

    @operation
    def live(self, task, *, teaching=False, task_wall=10., max_steps=None, origin=None, phase=None):
        if self.clock_mode == 'work':
            # Inherited ONE's loop uses MAX_WALL as well as LG.DEADLINE.
            # Here its numeric unit is work, bounded by the learned call.
            task_wall = max(0., self.clock.ceiling-self.clock.count)
            max_steps = math.inf
        if self._active:
            raise ValueError('Nested task living is unsupported')
        start = time.perf_counter()
        rollback = self.dumps()
        saved_wall = ONE.MAX_WALL
        initial = (TaskView.from_task(task) if task.form == 'exact' or
                   any(self.crutches.get(k, False) for k in U2_CRUTCHES+U6_CRUTCHES+U7_CRUTCHES+U8_CRUTCHES) else None)
        receipt_initial = initial
        if self.crutches['taught_not_yet'] and initial is not None:
            queued = next((item for item in self.field.revisit_queue if initial.identity in
                           (item['identity'], item.get('current_identity'))), None)
            if queued is not None:
                receipt_initial = queued['view']
        self._active = True
        try:
            ONE.MAX_WALL = task_wall
            with self.scope():
                self.proposer._beamed.clear()
                self.proposer.cursors.clear()
                self.proposer._scores.clear()
                if self.crutches['gap_syndromes']:
                    self.proposer._gap_surest = None
                self.proposer.fragments.clear()
                self.proposer.imagined.clear()
                if self.crutches['gap_syndromes']:
                    self.field.curiosity.surprises.clear()
                if self.crutches.get('memory_choice', False):
                    choice_phase = phase or self.engine._u_phase(task, teaching)
                    self.memory.start_choice(initial, wall=task_wall, phase=choice_phase, started=start)
                    ONE.MAX_WALL = max(0., task_wall-(time.perf_counter()-start))
                elif self.proposer.memory is not None:
                    self.memory.begin(initial)
                if self.crutches['gap_syndromes']:
                    default_phase = 'lesson' if teaching else 'world'
                    if hasattr(task, 'course_lesson'):
                        default_phase = 'lesson' if task.course_lesson else 'test3'
                    allowed_phase = phase or getattr(task, 'course_phase', default_phase)
                    if allowed_phase not in ('lesson', 'study', 'test1', 'test2', 'test3', 'talk', 'world'):
                        raise ValueError('Unknown curiosity/course phase')
                    self.engine._u_gap_context = dict(view=initial, phase=allowed_phase,
                                                     search=self.proposer.stats['search'], candidates=(),
                                                     roadmap=[], gap=None, fingerprint=None)
                self.engine._u_phase_name = phase or self.engine._u_phase(task, teaching)
                if self.engine._u_phase_name not in ('lesson', 'study', 'test1', 'test2', 'test3', 'talk', 'world'):
                    raise ValueError('Unknown not-yet/course phase')
                self.engine._u_item_started = time.perf_counter()
                active_task = (AssessmentTask(task) if (self.crutches['taught_not_yet'] or self.crutches.get('memory_choice', False)) and
                               self.engine._u_phase_name in ('test2', 'test3') and task.form == 'exact' and
                               not isinstance(task, AssessmentTask) else task)
                rec = self.engine.live(active_task, teaching=teaching and self.engine._u_phase_name not in
                                       ('test2', 'test3') if (self.crutches['taught_not_yet'] or self.crutches.get('memory_choice', False)) else teaching,
                                       max_steps=max_steps)
                if self.crutches.get('memory_choice', False):
                    time_to_right = ((self.memory.time_to_right if self.memory.time_to_right is not None
                                      else time.perf_counter()-start) if rec['proven'] else None)
                    rec['memory_choice'] = self.memory.finish_choice(TaskView.from_task(active_task),
                                                                  right=bool(rec['proven']))
                    rec['memory_choice']['time_to_right'] = time_to_right
                if self.crutches['taught_not_yet']:
                    self._record_not_yet(initial, rec, self.engine._u_phase_name, TaskView.from_task(active_task))
                # Only the independent audit grants program targets. Observer
                # grades are not consulted for untaught wake credit.
                if (not self.progress.get('assessment') and task.form == 'exact' and rec['proven']
                        and rec.get('answer') is not None):
                    if not teaching or rec.get('teacher_says') != 'wrong':
                        view = TaskView.from_task(task)
                        try:
                            view.records()
                        except PortBudget:
                            # Examples added while living exceed the pilot port; the proven program fits the
                            # first queued/original public view, which stays within the budget.
                            view = receipt_initial
                        concepts = self.engine._concepts()
                        try:
                            receipt = Receipt.make(view, (rec['answer'],), concepts, scope='exact-audit',
                                                   origin=origin or ('taught' if teaching else 'alone'),
                                                   source='public:'+receipt_initial.identity)
                        except ValueError as exc:
                            # Replay labels need exactly four public examples (the pilot's port); a proof on another
                            # view stands, it just gives no replay label (course items, 2026-10-03).
                            if not str(exc).startswith('Pilot program receipts require four'):
                                raise
                            rec['receipt_skipped'] = str(exc)
                            receipt = None
                        try:
                            if receipt is not None:
                                receipt.check(concepts, reserved=self.sleep.reserved,
                                              sources=self.sleep.reserved_sources)
                        except ValueError as exc:
                            if str(exc) != 'Reserved family/source in training target':
                                raise
                            # Its own proof landed on a family the observer reserved for assessment: never replayed,
                            # and the overlap is in the record for the observer; the run goes on.
                            rec['reserved_overlap'] = list(receipt.families)
                        else:
                            if receipt is not None and receipt.id not in self.sleep.consumed:
                                self.checked_wake.add(receipt.id)
                                self.sleep.admit(receipt, concepts)

                recorded_crutches = {k: self.crutches[k] for k in (
                    ((U1_CRUTCHES+U2_CRUTCHES) if any(self.crutches[k] for k in U2_CRUTCHES)
                     else U1_CRUTCHES) + (U3_CRUTCHES if any(self.crutches[k] for k in U3_CRUTCHES) else ()) + (U6_CRUTCHES if any(self.crutches[k] for k in U6_CRUTCHES) else ()) + (U7_CRUTCHES if self.u7_declared else ()))}
                if self.crutches.get('memory_choice', False):
                    recorded_crutches.update(memory_choice=True)
                rec['sera_u'] = dict(arm=self.arm, crutches=recorded_crutches,
                                     public_digest=None if initial is None else initial.identity,
                                     wall=time.perf_counter()-start, updates=self.updates,
                                     execution=dict(LG.EXECUTION_COUNTS))
                return rec
        except Exception:
            # The rollback's exact-resume check compares the lab knobs; restore the task's wall first.
            ONE.MAX_WALL = saved_wall
            restored = SeraU.loads(rollback)
            self.__dict__.update(restored.__dict__)
            self.sleep.mind = self
            self.memory.mind = self
            raise
        finally:
            self._active = False
            ONE.MAX_WALL = saved_wall

    def _record_not_yet(self, view, rec, phase, current=None):
        queue = self.field.revisit_queue
        current = view if current is None else current
        previous = next((item for item in queue if view.identity in
                         (item['identity'], item.get('current_identity'))), None)
        if rec['proven']:
            if previous is not None:
                queue.remove(previous)
                self.field.u7_revisits_solved += 1
                rec['u7']['solved_on_revisit'] = True
        elif phase != 'test3' and not self.progress.get('assessment'):
            if previous is None:
                queue.append(dict(identity=view.identity, view=view, phase=phase, attempts=1,
                                  first_at=self.field.tasks, last_at=self.field.tasks, status='not-yet',
                                  current_identity=current.identity, current_view=current))
            else:
                previous['attempts'] += 1
                previous['last_at'] = self.field.tasks
                previous['current_identity'], previous['current_view'] = current.identity, current
        rec['u7']['revisit_pending'] = len(queue)
        rec['u7']['revisits_solved'] = self.field.u7_revisits_solved

    def revisit(self, items, *, task_wall=10., max_steps=None, deadline=float('inf')):
        """U5 scheduling seam: retry public queued items after intervening teaching.
        Worlds/judges stay with the caller; only public TaskViews enter the Field.
        Exams never gain an extra attempt through this queue.
        """
        if not self.crutches.get('taught_not_yet'):
            return []
        records = []
        queued = {}
        for item in self.field.revisit_queue:
            queued[item['identity']] = item
            queued[item.get('current_identity', item['identity'])] = item
        for task in items:
            if time.time() >= deadline:
                break
            item = queued.get(TaskView.from_task(task).identity)
            if item is None or item['phase'] in ('test2', 'test3') or self.field.tasks <= item['last_at']:
                continue
            records.append(self.live(task, phase=item['phase'], teaching=item['phase'] == 'lesson',
                                     task_wall=min(task_wall, deadline-time.time()), max_steps=max_steps))
        return records

    def teach_answer_choice(self, task, candidate, right, *, continuation='method', phase='lesson'):
        """Teacher demonstration, with no supplied program or invented answer words."""
        if not self.crutches['taught_not_yet'] or phase not in ('lesson', 'study', 'test1'):
            raise ValueError('Answer-choice demonstrations belong to allowed teaching phases')
        if type(right) is not bool or continuation not in ('method', 'step', 'recall'):
            raise ValueError('A teacher verdict and an executable continuation are required')
        with self.scope():
            x = self.engine._u_candidate_inputs(task, [candidate])[0]
            p = self.field.inner.probability(ONE.kind_of(task), x) if self.crutches['inner_judge'] else .5
            f = self.field.loop.choice_features(x, p)
            self.field.loop.demonstrate(ONE.kind_of(task), f, {'answer', continuation},
                                        'answer' if right else continuation)

    def teach_not_yet(self, words):
        """Course phrase demonstration; no words are supplied by the implementation."""
        if not self.crutches['taught_not_yet']:
            raise ValueError('Enable taught_not_yet for its course words')
        words = words.split() if isinstance(words, str) else list(words)
        if not words or any(type(word) is not str or not word for word in words):
            raise ValueError('Teach a nonempty heard phrase')
        with self.scope():
            self.field.lexicon.hear(words, [('state', 'not-yet')])
            self.field.u7_words = tuple(TS.sym(word) for word in words)
            self.field.ideas.read(self.field.u7_words, 'course')

    def teach_memory_choice(self, task, shown, *, decision='consult', phase='lesson'):
        """Public demonstration only; test2/test3 cannot add teacher evidence."""
        if phase not in ('lesson', 'study', 'test1', 'world'):
            raise ValueError('Memory demonstrations are forbidden in test2/test3')
        if not self.crutches.get('memory_choice', False):
            return False
        view = TaskView.from_task(task)
        with self.scope(), torch.no_grad():
            self.memory.choosing, self.memory.selected = True, (False, False)
            try:
                f, _, _ = self.memory.features(view)
                feature = PH.MemoryChoice.features(f.detach().cpu().numpy())
            finally:
                self.memory.choosing = False
            head = self.field.memory_choice
            head.demonstrate(public_context(view)[0], decision, feature,
                             head.options(self.crutches['memory_layer_a'], self.crutches['memory_layer_b']), shown)
        return True

    @operation
    def train(self, *args, **kwargs):
        with self.scope():
            return self.sleep.train(*args, **kwargs)

    def converse(self, *args, **kwargs):
        with self.scope():
            return self.engine.converse(*args, **kwargs)

    def reply(self, *args, **kwargs):
        with self.scope():
            return self.engine.reply(*args, **kwargs)

    def study_order(self, items, *, phase='study'):
        """U5 seam: prioritize supplied public book tasks; no private metadata."""
        items = list(items)
        if phase != 'study' or not self.crutches['gap_syndromes']:
            return items
        views = [item if type(item) is TaskView else TaskView.from_task(item) for item in items]
        return [items[j] for j in self.field.curiosity.study_order(views)]

    def choice_features(self):
        """The actual retained Field read, using only its current public view."""
        if self.discovery is not None and self.discovery.active in self.discovery.worlds:
            view = self.discovery.view(self.discovery.active)
        else:
            view = next((q['question'] for q in getattr(getattr(self, 'agenda', None), 'items', {}).values()
                         if q['status'] == 'open' and type(q['question']) is TaskView),
                        TaskView((('x', 'num'),), 'num'))
        def read():
            return PH.InnerJudge.features(self.engine._u_reads([view])[0][0].detach().cpu().numpy())
        if getattr(self, '_clock_active', False):
            return read()
        with self.scope():
            return read()

    def ask(self, question, source):
        """Put actually received words or public task data first, retaining it."""
        from .agenda import Agenda
        if not hasattr(self, 'agenda'):
            self.agenda = Agenda()
        return self.agenda.ask(question, source, self.clock.count if self.clock_mode == 'work' else 0)

    def work_question(self, key=None, *, body=None, task_wall=10.):
        """Body/judge is ephemeral. A late revisit never calls ask again."""
        if not hasattr(self, 'agenda'):
            return None
        key = key or self.agenda.next(self, priority=self.u14['questions_first'])
        if key is None:
            return None
        item = self.agenda.items[key]
        question = item['question']
        count = self.clock.count if self.clock_mode == 'work' else 0
        features = self.choice_features()
        if type(question) is str:
            with self.scope():
                words = tuple(TS.sym(w) for w in question.split())
                answer, _, _ = self.engine.reply((words,), words)
        elif body is not None:
            if TaskView.from_task(body).identity != question.identity:
                raise ValueError('Question body does not match its saved public view')
            result = self.live(AssessmentTask(body), task_wall=task_wall, phase='world',
                               origin='interaction', max_steps=math.inf if self.clock_mode == 'work' else None)
            answer = expand(result['answer'], self.field.concept_table()) if result['proven'] else None
        else:
            answer = None
        spent = self.clock.count-count if self.clock_mode == 'work' else 0
        return self.agenda.settle(key, answer, spent, self.clock.count if self.clock_mode == 'work' else 0,
                                  features=features)

    def study(self, items, *, task_wall=10., max_steps=None, deadline=float('inf')):
        """Read supplied book tasks in gap order, within the study answer boundary."""
        records = []
        items = tuple(items)
        for item in self.study_order(items):
            if time.time() >= deadline:
                break
            records.append(self.live(item, origin='book', phase='study', max_steps=max_steps,
                                     task_wall=min(task_wall, deadline-time.time())))
        records.extend(self.revisit(items, task_wall=task_wall, max_steps=max_steps, deadline=deadline))
        return records

    @operation
    def discover(self, pool, *, deadline=float('inf')):
        """One completed discovery unit; the observer's pool is never retained."""
        if self.discovery is None:
            return None
        if self._active:
            raise ValueError('Nested discovery is unsupported')
        rollback = self.dumps()
        self._active = True
        try:
            with self.scope():
                if hasattr(pool, 'sync'):
                    pool.sync(self.discovery)
                if self.wiring:
                    pool.wiring = True
                return self.discovery.tick(self, pool, deadline=deadline)
        except Exception:
            self._active = False
            restored = SeraU.loads(rollback)
            self.__dict__.update(restored.__dict__)
            self.sleep.mind = self.memory.mind = self
            raise
        finally:
            self._active = False

    @operation
    def work_hole(self, key, pool, *, deadline=float('inf')):
        if not hasattr(self, 'holes') or self.discovery is None:
            return None
        q = next(q for q in self.holes.questions.values() if q['agenda'] == key)
        if not self.holes.switches[q['reason']]:
            return None
        rollback = self.dumps()
        self._active = True
        try:
            with self.scope():
                if hasattr(pool, 'sync'):
                    pool.sync(self.discovery)
                if self.wiring:
                    pool.wiring = True
                return self.holes.work(self, key, pool, deadline)
        except Exception:
            self._active = False
            restored = SeraU.loads(rollback)
            self.__dict__.update(restored.__dict__)
            self.sleep.mind = self.memory.mind = self
            raise
        finally:
            self._active = False

    def _payload(self):
        if self._active:
            raise ValueError('Checkpoint only at a completed task or training-batch boundary')
        engine = {k: v for k, v in self.engine.__dict__.items() if k not in ('field', 'proposer', 'memory', '_u_last_talk', '_u_predictions')}
        proposer = {k: v for k, v in self.proposer.__dict__.items() if k not in ('owner', 'field', '_scores', 'memory', '_feature_cache')}
        # Searches are restartable declarative cursors, not serialized Python generators.
        payload = dict(schema=SCHEMA, seed=self.seed, arm=self.arm, device=str(self.device), config=asdict(self.config),
                    source=self.source, code=self.code, crutches=self.crutches, u7_declared=self.u7_declared,
                    u8_declared=self.u8_declared,
                    batched_reads=self.batched_reads,
                    owner=self.owner.state_dict(),
                    owner_training=self.owner.training, optimizer=self.optimizer.state_dict(), field=self.field,
                    state=self.state, token_ids=self.owner.token_ids, production_ids=self.owner.production_ids,
                    understanding_ids=self.owner.understanding_ids,
                    engine=engine, proposer=proposer, sleep={k: v for k, v in self.sleep.__dict__.items() if k != 'mind'},
                    rngs=self.rngs, random=self.random.getstate(), numpy=self.numpy.bit_generator.state,
                    torch_generator=self.torch_generator.get_state(), checked_wake=self.checked_wake,
                    updates=self.updates, progress=self.progress, word_symbols=self.word_symbols,
                    book=self.book, runtime=dict(torch=torch.__version__,
                    numpy=np.__version__, threads=1 if self.clock_mode == 'work' else torch.get_num_threads(), deterministic=torch.are_deterministic_algorithms_enabled(),
                    knobs=CR.settings()),
                    **({'clock': self.clock.state(), 'work_policy': self.work_policy,
                        'clock_mode': self.clock_mode} if hasattr(self, 'clock') else {}),
                    **({'allocation_policy': self.work_policy} if self.clock_mode == 'wall' and
                        hasattr(self, 'work_policy') and not hasattr(self, 'clock') else {}),
                    **({'u14': self.u14} if any(self.u14.values()) else {}),
                    **({'agenda': self.agenda} if hasattr(self, 'agenda') else {}),
                    **({'holes': self.holes} if hasattr(self, 'holes') else {}),
                    **({'wiring': True} if self.wiring else {}),
                    **({'discovery': self.discovery} if self.discovery is not None else {}))
        if self.clock_mode == 'work':
            # Cache UUIDs and measured observer seconds cannot distinguish two
            # identical learned checkpoints. The original reporting events
            # remain in the observer's journal; work costs remain in learning.
            payload = copy.deepcopy(payload)
            if self.device.type == 'cpu':
                payload['rngs']['cuda'] = []  # CPU life is independent of unrelated GPUs
            payload['field'].ideas.gen = 'work-cache'
            if 'discovery' in payload:
                payload['discovery'] = copy.deepcopy(payload['discovery'])
                for event in payload['discovery'].events:
                    if event.get('cost_unit') == 'work':
                        event['seconds'] = event.get('work', 0)
            payload = canonical_payload(payload)
        return payload

    def dumps(self):
        stream = io.BytesIO()
        torch.save(self._payload(), stream)
        payload = stream.getvalue()
        outer = io.BytesIO()
        torch.save(dict(schema=SCHEMA, sha256=hashlib.sha256(payload).hexdigest(), payload=payload), outer)
        return outer.getvalue()

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(path.name+'.pending')
        with temporary.open('wb') as fh:
            fh.write(self.dumps())
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(temporary, path)
        return hashlib.sha256(path.read_bytes()).hexdigest()

    @classmethod
    def loads(cls, data, *, device=None, exact=True, _carry=False):
        outer = torch.load(io.BytesIO(data), map_location='cpu', weights_only=False)
        if outer['schema'] != SCHEMA or hashlib.sha256(outer['payload']).hexdigest() != outer['sha256']:
            raise ValueError('Corrupt or incompatible checkpoint envelope')
        p = torch.load(io.BytesIO(outer['payload']), map_location='cpu', weights_only=False)
        selected_device = str(device) if device is not None else p['device']
        if p['schema'] != SCHEMA or p['source'] != source_identity() or (not _carry and p['code'] != code_identity()):
            raise ValueError('Checkpoint schema/source/learner changed')
        if exact and (selected_device != p['device'] or p['runtime']['torch'] != torch.__version__ or
                      p['runtime']['numpy'] != np.__version__ or (p.get('clock_mode', 'wall') == 'wall' and
                      p['runtime']['threads'] != torch.get_num_threads()) or
                      p['runtime']['knobs'] != CR.settings()):
            raise ValueError('Exact resume requires the same device, runtime, threads and lab crutches')
        result = cls(p['seed'], device=selected_device, config=NativeConfig(**p['config']), arm=p['arm'],
                     field=p['field'], crutches=p['crutches'], batched_reads=p.get('batched_reads', True),
                     clock=p.get('clock_mode', 'wall'), u14=p.get('u14', dict.fromkeys(U14_CRUTCHES, False)),
                     discovery=p['discovery'].switches if 'discovery' in p else {k: False for k in U9_CRUTCHES},
                     einstein=(p['discovery'].einstein.switches if 'discovery' in p and hasattr(p['discovery'], 'einstein')
                               else dict.fromkeys(('thought_experiments', 'symmetry_principles',
                                                   'doubt_assumptions', 'bold_predictions'), False)),
                     scientists=(p['discovery'].scientists.switches if 'discovery' in p and hasattr(p['discovery'], 'scientists')
                                 else dict.fromkeys(('one_change_experiments', 'gap_predictions', 'number_conjectures',
                                                     'conserved_quantities', 'anomaly_pursuit'), False)),
                     darwin=(p['discovery'].darwin.switches if 'discovery' in p and hasattr(p['discovery'], 'darwin')
                             else dict.fromkeys(('world_hologram', 'patient_observation', 'lineage_trees',
                                                 'change_mechanisms', 'deep_time'), False)),
                     roadmap=(p['discovery'].roadmap.switches if 'discovery' in p and hasattr(p['discovery'], 'roadmap')
                              else dict.fromkeys(('own_operations', 'rederive_concepts', 'rough_estimates'), False)))
        if result.crutches != p['crutches']:
            raise ValueError('Changed arm crutch settings')
        result.u7_declared = p.get('u7_declared', False)
        result.u8_declared = p.get('u8_declared', False)
        result.owner.load_state_dict(p['owner'])
        result.owner.train(p['owner_training'])
        result.owner.token_ids, result.owner.production_ids = p['token_ids'], p['production_ids']
        result.owner.understanding_ids = p['understanding_ids']
        result.optimizer.load_state_dict(p['optimizer'])
        result.state = {k: v.to(result.device) for k, v in p['state'].items()}
        result.engine.__dict__.update(p['engine'])
        result.proposer.__dict__.update(p['proposer'])
        result.proposer.retained = result.state
        result.proposer._restore_pending = bool(result.proposer.cursors)
        result.sleep.__dict__.update(p['sleep'])
        result.rngs = p['rngs']
        result.random.setstate(p['random'])
        result.numpy.bit_generator.state = p['numpy']
        if exact:
            result.torch_generator.set_state(p['torch_generator'].cpu())
        elif result.device.type == 'cpu':
            result.rngs['cuda'] = []          # assessment migration is not claimed as an exact GPU resume
        result.updates, result.checked_wake, result.progress = p['updates'], p['checked_wake'], p['progress']
        result.word_symbols = p['word_symbols']
        result.book = p['book']
        result.discovery = p.get('discovery')
        result.wiring = p.get('wiring', False)
        if 'agenda' in p:
            p['agenda'].validate()
            result.agenda = p['agenda']
        if 'holes' in p:
            p['holes'].validate()
            result.holes = p['holes']
        if 'clock' in p:
            result.clock = Clock(p['clock'])
            result.work_policy = p['work_policy']
        elif 'allocation_policy' in p:
            result.work_policy = p['allocation_policy']
        if result.discovery is not None and hasattr(result.discovery, 'einstein'):
            result.field.einstein_methods = result.discovery.einstein.methods
        if result.discovery is not None and hasattr(result.discovery, 'scientists'):
            result.field.scientist_methods = result.discovery.scientists.methods
        if result.discovery is not None and hasattr(result.discovery, 'darwin'):
            result.discovery.darwin.attach(result.field)
        if result.discovery is not None and hasattr(result.discovery, 'roadmap'):
            result.discovery.roadmap.attach(result.field)
        # Runtime LG tables are deliberately rebuilt; no cross-task global cache is learning state.
        LG.forget_searches()
        return result

    @classmethod
    def load(cls, path, **kwargs):
        return cls.loads(Path(path).read_bytes(), **kwargs)

    @classmethod
    def carry(cls, path, *, device=None):
        """Explicit new body, same learned life; exact load still rejects code.

        Only the documented sera-u-2 shapes are accepted. No tensor is resized,
        no policy head is silently discarded, and pinned Field code must match.
        """
        data = Path(path).read_bytes()
        outer = torch.load(io.BytesIO(data), map_location='cpu', weights_only=False)
        if set(outer) != {'schema', 'sha256', 'payload'} or outer['schema'] != SCHEMA or \
                hashlib.sha256(outer['payload']).hexdigest() != outer['sha256']:
            raise ValueError('Unknown/corrupt carry envelope')
        p = torch.load(io.BytesIO(outer['payload']), map_location='cpu', weights_only=False)
        required = {'schema', 'seed', 'arm', 'device', 'config', 'source', 'code', 'crutches',
            'u7_declared', 'u8_declared', 'batched_reads', 'owner', 'owner_training', 'optimizer',
            'field', 'state', 'token_ids', 'production_ids', 'understanding_ids', 'engine', 'proposer',
            'sleep', 'rngs', 'random', 'numpy', 'torch_generator', 'checked_wake', 'updates',
            'progress', 'word_symbols', 'book', 'runtime'}
        optional = {'discovery', 'wiring', 'clock', 'clock_mode', 'work_policy', 'allocation_policy', 'u14', 'agenda', 'holes'}
        if not required <= set(p) or set(p)-required-optional:
            raise ValueError('Unknown carry payload shape: '+repr(sorted(set(p)-required-optional)))
        if set(p['sleep']) != {'replay', 'dreams', 'consumed', 'reserved', 'reserved_sources', 'logs'}:
            raise ValueError('Unknown sleep shape')
        if not isinstance(p['field'], PH.Field) or set(p['state']) != set(
                FieldOwner(NativeConfig(**p['config'])).empty(1)):
            raise ValueError('Unknown learned Field/state shape')
        validate_carry_shapes(p)
        result = cls.loads(data, device=device, exact=False, _carry=True)
        # state_dict loading checks every owner/optimizer tensor shape. Verify
        # retained state too: it is not an nn.Module's state_dict.
        expected = result.owner.empty(1)
        for key, value in result.state.items():
            if not isinstance(value, torch.Tensor) or value.shape != expected[key].shape:
                raise ValueError('Unknown retained tensor shape: '+key)
        for parameter, state in result.optimizer.state.items():
            if set(state)-{'step', 'exp_avg', 'exp_avg_sq', 'max_exp_avg_sq'}:
                raise ValueError('Unknown optimizer state shape')
            for name, value in state.items():
                if isinstance(value, torch.Tensor) and name != 'step' and value.shape != parameter.shape:
                    raise ValueError('Unknown optimizer tensor shape')
        result.carry_manifest = dict(from_code=p['code'], to_code=result.code,
            parent_digest=hashlib.sha256(data).hexdigest(),
            carried=sorted(set(p)-{'schema', 'code', 'source', 'runtime', 'progress'}),
            renamed=[], dropped=['progress (observer runner cursor)'],
            rebound=['code', 'source', 'runtime'], schema=SCHEMA)
        result.progress = {}
        return result

    def learning_hash(self):
        """Stable learning-state hash, excluding allocator IDs and elapsed-time counters."""
        sha = hashlib.sha256()
        def add(value):
            if isinstance(value, torch.Tensor):
                t = value.detach().cpu().contiguous()
                sha.update(str((str(t.dtype), tuple(t.shape))).encode())
                sha.update(t.numpy().tobytes())
            elif isinstance(value, np.ndarray):
                sha.update(str((str(value.dtype), value.shape)).encode())
                sha.update(value.tobytes())
            elif isinstance(value, dict):
                for k in sorted(value, key=repr):
                    add(k); add(value[k])
            elif isinstance(value, (list, tuple, set)):
                sha.update(type(value).__name__.encode())
                for v in sorted(value, key=repr) if isinstance(value, set) else value:
                    add(v)
            elif isinstance(value, (PH.Field, PH.Ideas)):
                # Hash retained state, not spare HRR capacity or perception caches
                # that the checkpoint intentionally trims/drops. Ideas.gen is a random
                # perception-cache key (uuid4), different for every new Ideas.
                state = value.__getstate__()
                if isinstance(value, PH.Field) and 'log' in state:
                    # The log's per-task wall seconds are an elapsed-time counter (0.5 vs 0.6 s flipped the hash).
                    state = {**state, 'log': [{k: v for k, v in e.items() if k != 'wall'} if isinstance(e, dict)
                                              else e for e in state['log']]}
                if isinstance(value, PH.Field) and 'hologram' in state:
                    from .darwin import clean
                    state = {**state, 'hologram': clean(state['hologram'])}
                if isinstance(value, PH.Field) and 'roadmap_readout' in state:
                    state = {**state, 'roadmap_readout': state['roadmap_readout'].learning_state()}
                add({k: v for k, v in state.items() if k != 'gen'} if isinstance(value, PH.Ideas) else state)
            elif isinstance(value, Syndrome):
                # A self-check's cost is its measured seconds (a record, never learned from): an elapsed-time counter.
                add({k: v for k, v in value.__dict__.items() if k != 'cost'})
            elif hasattr(value, '__dict__'):
                add(value.__dict__)
            else:
                sha.update(pickle.dumps(value, protocol=5))
        p = self._payload()
        p['sleep'] = {k: v for k, v in p['sleep'].items() if k != 'logs'}
        for key in ('owner', 'optimizer', 'field', 'state', 'token_ids', 'production_ids', 'understanding_ids', 'sleep', 'rngs',
                    'random', 'numpy', 'torch_generator', 'checked_wake', 'updates', 'crutches', 'word_symbols', 'book'):
            add(p[key])
        if self.discovery is not None:
            add(self.discovery.learning_state())
        if hasattr(self, 'clock'):
            add(self.clock.state()); add(self.work_policy)
        elif hasattr(self, 'work_policy'):
            add(self.work_policy)
        if any(self.u14.values()):
            add(self.u14)
        if hasattr(self, 'agenda'):
            add(self.agenda.learning_state())
        if hasattr(self, 'holes'):
            add(self.holes.learning_state())
        return sha.hexdigest()

    def assess(self, task, *, task_wall=10., max_steps=None):
        before = self.learning_hash()
        start_load = time.perf_counter()
        clone = SeraU.loads(self.dumps(), device='cpu', exact=False)
        clone.progress['assessment'] = True
        load_wall = time.perf_counter()-start_load
        return self._assess_clone(task, clone, before, load_wall, task_wall=task_wall, max_steps=max_steps)

    def _assess_clone(self, task, clone, before, load_wall, *, task_wall, max_steps, preparation_wall=0.):
        # Assessment trial mutations are isolated and discarded, including token
        # growth, RNGs, lexicon, controllers, wishes, and temporary proof credit.
        start = time.perf_counter()
        error, rec = None, None
        try:
            rec = clone.live(AssessmentTask(task), task_wall=task_wall, max_steps=max_steps)
        except PortBudget as exc:
            error = str(exc)
        judge_start = time.perf_counter()
        grade = task.grade(rec['answer'], clone.engine._concepts(), bool(rec['proven']), seed=self.seed) if rec else {}
        judge_wall = time.perf_counter()-judge_start
        elapsed = time.perf_counter()-start+preparation_wall
        if rec is not None:
            rec['sera_u']['wall'] += preparation_wall
        solved = bool(rec and rec.get('proven') and elapsed <= task_wall)
        solved = solved and grade.get('verdict') == 'proven right'
        after = self.learning_hash()
        if before != after:
            raise ValueError('Held-out assessment mutated the checkpoint learning state')
        result = dict(task=task.name, solved=bool(solved), wall=elapsed, load_wall=load_wall,
                    search=clone.proposer.stats['search']-self.proposer.stats['search'],
                    inference=clone.proposer.stats['inference']-self.proposer.stats['inference'],
                    proposal=clone.proposer.stats['proposal']-self.proposer.stats['proposal'],
                    judge=(rec or {}).get('timing', {}).get('prove', 0.)+judge_wall,
                    expanded_size=None if not rec or rec.get('answer') is None else
                        expanded_size(rec['answer'], clone.engine._concepts()),
                    surface_size=None if not rec or rec.get('answer') is None else LG.size(rec['answer']),
                    execution=(rec or {}).get('sera_u', {}).get('execution', {}),
                    candidates=clone.proposer.stats['candidates']-self.proposer.stats['candidates'],
                    record=rec, grade=grade, failure=error, before=before, after=after,
                    memory_mb=LG._rss_mb(), scope='fixed independent audit; no observer feedback')
        if self.u7_declared:
            result['status'] = ('right' if solved else 'wrong' if rec and rec['proven'] and
                                grade.get('verdict') != 'proven right' else 'not-yet')
            result['time_to_right'] = (rec.get('u7', {}).get('time_to_right', elapsed) if solved else None)
        if self.crutches.get('memory_choice', False):
            result['time_to_right'] = ((rec or {}).get('memory_choice', {}).get('time_to_right')
                                       if solved else None)
        return result

    @staticmethod
    def _prepare_assessments(clones, views):
        """Batch only independent initial public observations and their first read.

        Each clone allocates its OWN token IDs and writes its OWN symbolic memory.
        The shared numerical owner has identical weights. Later live events clear
        the prepared read, and each trial continues with its isolated history.
        """
        from collections import Counter
        # Choosing trials must first draw from their own plain read, and may
        # not write the current item before deciding to remember it. US's fixed
        # path below remains untouched; memory.features_many still batches reads.
        if any(clone.crutches.get('memory_choice') for clone in clones):
            return 0.
        started = time.perf_counter()
        observed_sources, observed_states, active = [], [], []
        for clone, view in zip(clones, views):
            if not any(clone.crutches[k] for k in U2_CRUTCHES):
                continue
            memory, sources = clone.memory, []
            records = memory_records(view)
            # refresh writes all copies at their first occurrence, including
            # nonadjacent duplicate measurements. Preserve that event order.
            schedule = [row for row, count in Counter(records).items() for _ in range(count)]
            with clone.scope(), torch.no_grad():
                if memory.a:
                    sources = memory.encode_rows(schedule)
                for row in schedule:
                    if memory.b:
                        tokens = tuple(t[0] for t in row)
                        for j in range(0, len(tokens), 60):
                            PH.Ideas.read(clone.field.ideas, tokens[j:j+60])
                    clone.proposer.changed()
            # scope() intentionally clears transient task state on exit.
            memory.current = view
            memory.context = public_context(view)
            memory.seen_records = Counter(records)
            memory.checked_parts = []
            memory._prepared = view
            if memory.a:
                active.append(clone)
                observed_sources.append(sources)
                observed_states.append(clone.state)
        with torch.no_grad():
            if active:
                state = active[0].owner.observe_sources_many(observed_sources, states=observed_states)
                for j, clone in enumerate(active):
                    clone.state = detached_state({k: v[j:j+1] for k, v in state.items()})
                    clone.proposer.retained = clone.state
            sources, states, readers, rings = [], [], [], []
            for clone, view in zip(clones, views):
                if not (clone.crutches['field_proposer'] or
                        (clone.crutches['memory_layer_a'] and clone.crutches['field_understanding'])):
                    continue
                readers.append((clone, view))
                memory_on = any(clone.crutches[k] for k in U2_CRUTCHES)
                retained = clone.state if clone.crutches['memory_layer_a'] else clone.owner.empty(1)
                states.append(retained)
                ring = clone.memory.ring(view) if memory_on else None
                rings.append(ring)
                sources.append(clone.owner.task_sources(view, ring=ring, memory_read=memory_on))
            reads = clones[0].owner.features_from_sources_many(sources, states=states) if readers else []
            for (clone, view), read, ring in zip(readers, reads, rings):
                clone.proposer._feature_cache[(view, True)] = read
                clone.memory.cache_read(view, True, read, ring)
        # Share actual preparation cost across trials; it remains part of assessment wall.
        return (time.perf_counter()-started)/len(clones)

    def assess_many(self, tasks, *, task_wall=10., max_steps=None, batch_size=8):
        """Yield isolated trials in order, batching their independent Field reads."""
        tasks = tuple(tasks)
        if batch_size < 1:
            raise ValueError('Positive assessment batch size required')
        if not self.batched_reads:
            for task in tasks:
                yield self.assess(task, task_wall=task_wall, max_steps=max_steps)
            return
        before, snapshot = self.learning_hash(), self.dumps()
        for offset in range(0, len(tasks), batch_size):
            group = tasks[offset:offset+batch_size]
            views = [TaskView.from_task(task) for task in group]
            # Preserve the original recorded PortBudget failure path.
            try:
                for view in views:
                    view.records()
            except PortBudget:
                for task in group:
                    yield self.assess(task, task_wall=task_wall, max_steps=max_steps)
                continue
            clones, load_walls = [], []
            for _ in group:
                start_load = time.perf_counter()
                clone = SeraU.loads(snapshot, device='cpu', exact=False)
                clone.progress['assessment'] = True
                clones.append(clone)
                load_walls.append(time.perf_counter()-start_load)
            preparation = self._prepare_assessments(clones, views)
            for task, clone, load_wall in zip(group, clones, load_walls):
                # Prepared read time is included in the inference accounting.
                clone.proposer.stats['inference'] += preparation
                yield self._assess_clone(task, clone, before, load_wall, task_wall=task_wall,
                                         max_steps=max_steps, preparation_wall=preparation)
