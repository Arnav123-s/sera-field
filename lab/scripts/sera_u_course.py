"""S27 on SERA-U: revisited practice, fading demonstrations, three RSI rounds.

Teacher/book/observer code belongs in this runner. No observer grade is put in
the entity checkpoint. A two-slot checkpoint plus atomic STATE.json commits a
unit, learning and the cursor together; reports only read committed units.
"""
import argparse
from contextlib import contextmanager
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import sera_course as C
from scripts import sera_u_rsi as RSI
from sera import crutches as CR, dictionary as DICT, lang as LG, one as ONE, phi as PH, tasks as TS
from sera_u.mind import SeraU, U_CRUTCHES
from sera_u.ports import PortBudget, TaskView, digest
from sera_u.memory import public_context

PHASES = C.PHASES
ORDER = ('lesson', 'study', 'rsi', 'test1', 'test2', 'test3')
SHARES = (2., 1., 1., 1., 1., 1.)
WEIGHTS = dict(zip(ORDER, (1., .6, .4, .25, .1, 0.)))
STATUSES = ('right', 'wrong', 'not-yet', 'not reached')
NOT_YET_WORDS = ('not', 'yet')  # teacher content, heard only in lesson


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def validate_suite(suite):
    """Keep the pilot's integrity checks; defer bounded-port misses to units.

    Validation constructs every full view. Only PortBudget from its encoder is
    deferred; type/domain/identity/overlap failures still abort. No truncated
    view is supplied to a learner and its actual encoder remains unchanged.
    """
    original = TaskView.records
    def integrity_records(view, *args, **kwargs):
        try:
            return original(view, *args, **kwargs)
        except PortBudget:
            return ()
    TaskView.records = integrity_records
    try:
        return RSI.validate_frozen_suite(suite)
    finally:
        TaskView.records = original


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def runner_identity():
    root = Path(__file__).resolve().parents[1]
    return digest([(p.relative_to(root).as_posix(), sha(p)) for p in
                   (root/'scripts/sera_u_course.py', root/'scripts/sera_bakeoff.py',
                    root/'scripts/sera_course.py', root/'scripts/sera_u_rsi.py',
                   root/'scripts/crutch_ledger.py') if p.exists()])


def book_identity(path):
    if not path:
        return None
    root = Path(path)
    files = sorted([*root.glob('data.*'), *root.glob('index.*'), *root.glob('*.exc')])
    return digest([(p.name, sha(p)) for p in files])


def u_switches(off=()):
    switches = {k: k not in CR.OFF and k not in off for k in U_CRUTCHES}
    switches['memory_choice'] = CR.on('memory_choice') and 'memory_choice' not in off
    switches['abstain_bar'] = False
    if 'taught_not_yet' in off:
        switches['abstain_bar'] = 'abstain_bar' not in CR.OFF
    return switches


def retire_lesson_words():
    names = sorted(set(filter(None, os.environ.get('SERA_CRUTCH_OFF', '').split(','))) | {'lesson_words'})
    os.environ['SERA_CRUTCH_OFF'] = ','.join(names)
    CR.OFF.add('lesson_words')


def public_plan(plan):
    return {p: [{k: r[k] for k in ('id', 'name', 'digest', 'number_seed')} for r in plan[p]] for p in PHASES}


def public_task_digest(task):
    """All initial public channels, including example outputs and query probes."""
    if task.form == 'strengths':
        return TaskView.from_task(task).identity
    return digest(dict(inputs=sorted(task.inputs.items()), out=task.out, data=LG.freeze(task.data),
                       probes=LG.freeze(task.probes()), words=[TS.text(w) for w in task.words],
                       passage=[TS.text(s) for s in task.reading()] if hasattr(task, 'reading') else []))


class CourseWorld:
    """Preserve Story perception, reading and rail ports; suppress private help.

    Exact audit success/failure is available as in S27, but its counterexample
    cannot be copied into practice or an exam. Teacher grading is separate.
    Test3 keeps the independent proof gate, with no teacher/book answer channel.
    """
    def __init__(self, task, phase):
        self.world, self.course_phase = task, phase
        self.course_lesson = False

    def __getattr__(self, name):
        if name in ('_y', '_target', '_worked_values', '_worked', '_worked_of', 'hidden', 'signs'):
            raise AttributeError(name)
        return getattr(object.__getattribute__(self, 'world'), name)

    @property
    def mind(self):
        return getattr(self.world, 'mind', None)

    @mind.setter
    def mind(self, value):
        if hasattr(self.world, 'mind'):
            self.world.mind = value

    def actions(self, *args, **kwargs):
        return []

    def explore(self, *args, **kwargs):
        return None

    def worked(self, x):
        return None

    def teacher_truth(self, word):
        return False

    def grade(self, *args, **kwargs):
        return dict(verdict='not proven')  # an observer grade has no engine path

    def verify(self, *args, **kwargs):
        if self.form == 'exact':
            # Exact.verify appends failures to data; suppressing its RETURN is
            # insufficient. A detached judge also isolates Story._fresh's lambda.
            judge = copy.deepcopy(self.world)
            judge.data = copy.deepcopy(self.world.data)
            if isinstance(judge, TS.Story):
                judge._fresh = lambda rng: judge._make(rng)[0]
            vocab = copy.deepcopy((TS.VOCAB, TS.WORDS, TS._NEXT))
            try:
                ok, n, _ = judge.verify(*args, **kwargs)
            finally:
                TS.VOCAB, TS.WORDS, TS._NEXT = vocab
            return ok, n, None
        return self.world.verify(*args, **kwargs)


@contextmanager
def answer_seam(mind, channel, phase):
    """Temporary CLASS hooks, never closures in the checkpointed engine dict.

    SeraU.live owns rollback, receipts, ports and RNG isolation. Its existing
    engine delegates to S27's answer_channel before proof credit. Test2 must use
    a bit-only hook even in the no-not-yet arm (the U3 correction hook reads y).
    """
    cls = type(mind.engine)
    had_live, had_verdict = 'live' in cls.__dict__, 'course_verdict' in cls.__dict__
    live, verdict = cls.live, cls.course_verdict

    def hooked(engine, task, *args, **kwargs):
        kwargs['answer_channel'] = channel
        return live(engine, task, *args, **kwargs)

    def bit_only(engine, task, law, right, source, reliability=False):
        memory = getattr(engine, 'memory', None)
        if memory is not None and memory.choosing:
            memory.feedback = bool(right)
        if hasattr(engine, '_u_verdict'):
            engine._u_verdict(task, law, right, 'teacher')
        return ONE.Sera.course_verdict(engine, task, law, right, 'test2',
                                      reliability and not engine._u_on('inner_judge'))

    cls.live = hooked
    if phase == 'test2':
        cls.course_verdict = bit_only
    try:
        yield
    finally:
        if had_live:
            cls.live = live
        else:
            del cls.live
        if phase == 'test2':
            if had_verdict:
                cls.course_verdict = verdict
            else:
                del cls.course_verdict


class UBackend:
    kind = 'U'

    def __init__(self, seed, device='cpu', switches=None):
        retire_lesson_words()
        self.mind = SeraU(seed, device=device, crutches=switches or u_switches())

    @property
    def field(self):
        return self.mind.field

    @property
    def engine(self):
        return self.mind.engine

    def save(self, path):
        self.mind.save(path)

    def load(self, path):
        self.mind = SeraU.load(path)

    def settings(self):
        result = {name: CR.on(name) for name in sorted(CR.REGISTRY)}
        result.update(self.mind.crutches)
        return result

    def live(self, task, phase, wall, channel, teaching=False):
        with answer_seam(self.mind, channel, phase):
            return self.mind.live(task, phase=phase, teaching=teaching,
                                  origin='book' if phase == 'study' else None, task_wall=wall)

    def demonstrate(self, task):
        if self.mind.crutches.get('memory_choice'):
            # Teacher policy only. The learner gets a fading demonstration,
            # never this resemblance test as a decision rule or a target law.
            kind, cue = public_context(TaskView.from_task(task))
            head = self.field.memory_choice
            resembles = any(e['kind'] == kind and len(e['cue']) == len(cue) and
                            math.dist(e['cue'], cue) <= .25 for e in head.eligible)
            available = head.options(self.mind.crutches['memory_layer_a'], self.mind.crutches['memory_layer_b'])
            shown = available[-1] if resembles else 'plain'
            self.mind.teach_memory_choice(task, shown, phase='lesson')
        if not self.mind.crutches['taught_not_yet'] or task.form != 'exact':
            return
        # Values/probabilities, never a teacher program: a public observed
        # candidate is enough to demonstrate sure -> answer / unsure -> work.
        with self.mind.scope():
            features = PH.InnerJudge.features(self.mind.engine._u_reads([TaskView.from_task(task)])[0][0]
                                             .detach().cpu().numpy())
            kind = ONE.kind_of(task)
            for probability, shown in ((1., 'answer'), (0., 'method'), (0., 'step')):
                f = self.field.loop.choice_features(features, probability)
                self.field.loop.demonstrate(kind, f, ('answer', 'method', 'step'), shown)

    def teach_words(self):
        if self.mind.crutches['taught_not_yet']:
            self.mind.teach_not_yet(NOT_YET_WORDS)


def attempt(backend, task, phase, wall, seed, corrected=False, reliability=True):
    if hasattr(backend, 'course_attempt'):
        return backend.course_attempt(task, phase, wall, seed, corrected, reliability)
    captured = dict(law=None, concepts={}, proven=None)
    base_task = task

    def channel(world, law, concepts, proven):
        captured.update(law=law, concepts=copy.deepcopy(concepts), proven=proven)
        missing = law is None or (world.form == 'strengths' and proven is None)
        if hasattr(backend, 'mind') and backend.mind.crutches['taught_not_yet'] and proven is None:
            missing = True  # an unsubmitted U7 candidate earns no teacher feedback
        if (phase == 'test2' and hasattr(backend, 'mind') and not backend.mind.crutches['taught_not_yet']
                and CR.on('course_told_wrong') and not backend.engine.course_reliable(world)):
            missing = True  # retain U3's explicit abstain_bar comparison
        captured['missing'] = missing
        if phase == 'test3':
            return None
        if missing:
            return dict(right=None)
        right = C.isolated_grade(base_task, law, concepts, proven, seed)
        captured['right'] = right
        return dict(right=right, source='book' if phase == 'study' else 'test2' if phase == 'test2' else 'teacher',
                    reliability=reliability and (phase != 'test2' or CR.on('course_told_wrong')))

    world = CourseWorld(task, phase) if phase in ('study', 'test2', 'test3') else task
    world.course_phase = phase
    if phase == 'lesson' and hasattr(backend, 'demonstrate'):
        backend.demonstrate(task)
    rec = backend.live(world, phase, wall, channel, teaching=phase == 'lesson' or corrected)
    # U7 can withhold the leading candidate in _finish AFTER S27's channel.
    missing = captured.get('missing', True) or (rec.get('answer') is None and task.form == 'exact')
    if backend.kind != 'U':
        missing = captured.get('missing', True)
    right = (C.isolated_grade(base_task, captured['law'], captured['concepts'], captured['proven'], seed)
             if phase == 'test3' and not missing else captured.get('right', False))
    status = 'not-yet' if missing else 'right' if right else 'wrong'
    unit = C.BASE.unit_of(rec)
    if 'memory_choice' in rec:
        unit['memory_choice'] = rec['memory_choice']
    unit.update(phase=phase, status=status, observer_right=bool(right),
                feedback=None if phase == 'test3' or missing else
                dict(verdict='right' if right else 'wrong', source='book' if phase == 'study' else 'teacher'),
                response=None if missing else rec.get('claim') or LG.show(captured['law']),
                observations=list(task.data) if task.form == 'exact' else None)
    if missing and hasattr(backend.field, 'u7_words') and backend.field.u7_words:
        unit['response'] = TS.text(backend.field.u7_words)
    if unit['feedback'] is not None:
        unit['feedback']['reliability'] = reliability and (phase != 'test2' or CR.on('course_told_wrong')) and not (
            hasattr(backend, 'mind') and backend.mind.crutches['inner_judge'])
    if phase == 'test1' and not corrected and status != 'right':
        unit['correction'] = C.correction(task, captured['law'], captured['concepts'], seed)
        unit['observations'] = list(task.data) if task.form == 'exact' else None
    if unit.get('verdict') == 'SURE AND WRONG':
        raise ValueError('Course tripwire: sure and wrong')
    return unit


def teacher_arrays(field):
    """Only teacher sufficient statistics; learned evidence is untouched."""
    for slot in ('loop', 'methods', 'steps', 'memory_choice'):
        obj = getattr(field, slot, None)
        if obj is None:
            continue
        for name in ('taught', 'choice_taught'):
            def walk(value):
                if isinstance(value, dict):
                    for k in sorted(value, key=repr):
                        yield from walk(value[k])
                elif isinstance(value, (list, tuple)):
                    for v in value:
                        yield from walk(v)
                elif hasattr(value, 'shape'):
                    yield value
            yield from walk(getattr(obj, name, {}))
        for name in ('At', 'bt'):
            if hasattr(obj, name):
                yield getattr(obj, name)


def fade(field, old_weight, weight):
    ratio = weight / old_weight if old_weight else 0.
    for array in teacher_arrays(field):
        array *= ratio
    if weight == 0 and hasattr(field, 'u7_words'):
        field.u7_words = ()  # no supplied teacher phrase at the final exam


@contextmanager
def evidence_weight(weight, taught_ways=True):
    """Scale NEW demonstrations too, including book-induced U7 demonstrations.

    Existing per-task TAUGHT_FADE still runs. Phase weights cap the teacher's
    additive evidence; learned returns and the fixed acceptance bar are unchanged.
    """
    patches = []
    for cls, method in ((PH.LoopField, 'teach'), (PH.MethodField, 'teach'),
                        (PH.StepField, 'teach'), (PH.NotYetWays, 'demonstrate'),
                        (PH.MemoryChoice, 'demonstrate')):
        original = getattr(cls, method)
        scale = weight if taught_ways or method == 'demonstrate' else 0.

        def scaled(obj, *args, _original=original, _scale=scale, **kwargs):
            before = {id(a): a.copy() for a in teacher_arrays_proxy(obj)}
            result = _original(obj, *args, **kwargs)
            for a in teacher_arrays_proxy(obj):
                prior = before.get(id(a))
                if prior is None:
                    a *= _scale
                else:
                    a[...] = prior + _scale * (a - prior)
            return result

        patches.append((cls, method, original))
        setattr(cls, method, scaled)
    try:
        yield
    finally:
        for cls, method, original in reversed(patches):
            setattr(cls, method, original)


def teacher_arrays_proxy(obj):
    holder = type('TeacherHolder', (), {})()
    holder.loop = obj
    return teacher_arrays(holder)


class Meter:
    """Consultations are not actions: count both and label their coverage.

    Every switch has measured consultation counts. Callable seams count actual
    executions where available; an uninstrumented action/effect is null, never 0.
    Counterfactuals here use pure worked()/numbers() reads, not replayed learning.
    """
    def __init__(self, state):
        self.state = state

    @contextmanager
    def measure(self, backend):
        counts = self.state.setdefault('meter', {})
        switches = backend.settings()
        original = CR.on

        def checked(name):
            value = original(name)
            if self.state.get('counterfactual_active'):
                return value
            row = counts.setdefault(name, dict(consulted=0, enabled=0, calls=0))
            row['consulted'] += 1
            row['enabled'] += int(value)
            # These inline gates have no independently callable mechanism.
            # Count a taken, effective branch at its observed execution site,
            # excluding record/settings queries. No stack values enter Field.
            caller = sys._getframe(1)
            function = caller.f_code.co_name
            inline = {
                'leader_override': ('live',), 'convince_halving': ('live',),
                'rail_cues': ('_cues',), 'nobody_said': ('_correct',),
                'talk_tally': ('_correct',), 'frame_identity': ('_reliable', 'course_reliable', 'course_verdict', 'converse'),
                'way_back': ('_step',), 'teacher_none_fits': ('_none_fit_late',),
                'teach_rechecking': ('_observe_push', '_observe_report'),
                'lesson_words': ('numbers',),
            }
            if name in inline and function in inline[name]:
                self.state['instrumented'] = sorted(set(self.state.get('instrumented', [])) | {name})
                if value and (name != 'convince_halving' or caller.f_locals.get('st', {}).get('shown', 0) > 0):
                    row['calls'] += 1
                self.state.setdefault('action_scopes', {})[name] = 'taken inline gate in '+','.join(inline[name])
            return value

        CR.on = checked
        patches = []
        instrumented = set(self.state.setdefault('instrumented', []))
        # Class patching is important: SeraU serializes/rolls back at entry.
        if hasattr(backend, 'mind'):
            from sera_u.proposer import Proposer, FieldOwner
            from sera_u.memory import Memory
            from sera_u.sleep import Sleep, Curiosity
            from sera_u.field.core_owner import CoreOwner
            seams = [(Proposer, 'beam', 'field_proposer'), (FieldOwner, 'encode_record', 'field_input_ports'),
                     (CoreOwner, 'observe', 'memory_layer_a'), (Memory, 'ring', 'memory_layer_b'),
                     (Memory, 'neural', 'field_understanding'), (Sleep, 'dream', 'program_dreams'),
                     (Sleep, 'abstract', 'sleep_library'), (Curiosity, 'decode', 'gap_syndromes'),
                     (PH.FieldMethods, 'choose', 'field_methods'), (PH.FieldSteps, 'score', 'field_roadmap'),
                     (PH.FieldMethods, 'next_method', 'field_methods'),
                     (PH.FieldWays, 'choose', 'field_ways'), (PH.NotYetWays, 'pick', 'taught_not_yet'),
                     (PH.InnerJudge, 'verdict', 'inner_judge'), (PH.InnerJudge, 'decide', 'abstain_bar'),
                     (Curiosity, 'dream_trial', 'aimed_dreams'),
                     (PH.NotYetWays, 'demonstrate', 'taught_not_yet'),
                     (PH.MemoryChoice, 'pick', 'memory_choice')]
            seams.append((type(backend.engine), 'course_reliable', 'abstain_bar'))
            for cls, method, name in seams:
                if not hasattr(cls, method):
                    continue
                original_method = getattr(cls, method)
                own = method in cls.__dict__
                instrumented.add(name)

                def counted(obj, *args, _original=original_method, _name=name, **kwargs):
                    if self.state.get('counterfactual_active'):
                        return _original(obj, *args, **kwargs)
                    if switches.get(_name):
                        counts.setdefault(_name, dict(consulted=0, enabled=0, calls=0))['calls'] += 1
                    result = _original(obj, *args, **kwargs)
                    if _name == 'memory_choice' and switches.get(_name):
                        decision = args[1] if len(args) > 1 else kwargs['decision']
                        options = self.state.setdefault('memory_choices', {}).setdefault(decision, {})
                        options[result[0]] = options.get(result[0], 0) + 1
                    if _name == 'abstain_bar' and switches.get(_name):
                        cf = self.state.setdefault('counterfactuals', {}).setdefault(_name,
                            dict(n=0, changed=0, scope='submission versus bar off; not correctness causality'))
                        cf['n'] += 1
                        accepted = result[0] if isinstance(result, tuple) else result
                        cf['changed'] += int(not accepted)
                    return result

                patches.append((cls, method, original_method, own))
                setattr(cls, method, counted)
        # Registered taught crutches have callable seams even on the lab arm.
        for cls, method, name in ((TS.Exact, 'worked', 'course_worked_steps'),
                                  (ONE.Sera, '_none_fit_late', 'teacher_none_fits'),
                                  (TS.JudgeScrutiny, 'begin', 'judge_scrutiny')):
            if not hasattr(cls, method) or method == '_none_fit_late':
                continue  # staticmethod: consultations are measured separately
            original_method = getattr(cls, method)
            own = method in cls.__dict__
            instrumented.add(name)
            def counted(obj, *args, _original=original_method, _name=name, **kwargs):
                result = _original(obj, *args, **kwargs)
                if self.state.get('counterfactual_active'):
                    return result
                if switches.get(_name) and result is not None:
                    counts.setdefault(_name, dict(consulted=0, enabled=0, calls=0))['calls'] += 1
                return result
            patches.append((cls, method, original_method, own))
            setattr(cls, method, counted)
        self.state['instrumented'] = sorted(instrumented)
        # These gates are fully watched even if their site never runs in a
        # phase: zero means no observed taken branch, not an uninstalled probe.
        watched_inline = ('leader_override', 'convince_halving', 'rail_cues', 'nobody_said', 'talk_tally',
                          'frame_identity', 'way_back', 'teacher_none_fits', 'teach_rechecking', 'lesson_words')
        self.state['instrumented'] = sorted(set(self.state['instrumented']) | set(watched_inline))
        for name in watched_inline:
            self.state.setdefault('action_scopes', {}).setdefault(name, 'taken inline gate at its registered site')
        try:
            yield
        finally:
            CR.on = original
            for cls, method, method_value, own in reversed(patches):
                if own:
                    setattr(cls, method, method_value)
                else:
                    delattr(cls, method)

    def counterfactual(self, task):
        trials = self.state.setdefault('counterfactuals', {})
        for name, method in (('course_worked_steps', 'worked'), ('lesson_words', 'numbers')):
            if not hasattr(task, method) or task.form != 'exact':
                continue
            on, off = set(CR.ON), set(CR.OFF)
            try:
                self.state['counterfactual_active'] = True
                args = (task.data[0][0],) if method == 'worked' and task.data else ()
                if method == 'worked' and not args:
                    continue
                CR.ON.add(name)
                CR.OFF.discard(name)
                a = getattr(task, method)(*args)
                CR.OFF.add(name)
                b = getattr(task, method)(*args)
                row = trials.setdefault(name, dict(n=0, changed=0, scope='public channel only; not outcome causality'))
                row['n'] += 1
                row['changed'] += int(a != b)
            finally:
                CR.ON, CR.OFF = on, off
                self.state.pop('counterfactual_active', None)

    def observe(self, unit):
        if unit.get('phase') != 'test2':
            return
        name = 'course_told_wrong'
        self.state['instrumented'] = sorted(set(self.state.get('instrumented', [])) | {name})
        row = self.state.setdefault('meter', {}).setdefault(name, dict(consulted=0, enabled=0, calls=0))
        supplied = bool((unit.get('feedback') or {}).get('reliability'))
        row['calls'] += int(supplied)
        self.state.setdefault('action_scopes', {})[name] = 'actual verdict-only reliability contributions'
        if unit.get('feedback'):
            cf = self.state.setdefault('counterfactuals', {}).setdefault(name,
                dict(n=0, changed=0, scope='reliability contribution versus off; not task causality'))
            cf['n'] += 1
            cf['changed'] += int(supplied)

    def boundary(self, backend, phase, edge, weight):
        switches = backend.settings()
        counts = self.state.get('meter', {})
        entries = {}
        for name in sorted(CR.REGISTRY):
            c = CR.REGISTRY[name]
            entries[name] = dict(on=switches[name], status=c['status'],
                                 teacher_weight=weight if c['status'] == 'taught' else None,
                                 use=copy.deepcopy(counts.get(name, dict(consulted=0, enabled=0, calls=0))),
                                 action_scope='instrumented callable executions; consults do not establish action',
                                 outcome_dependence=None,
                                 counterfactual=copy.deepcopy(self.state.get('counterfactuals', {}).get(name)))
            if name not in self.state.get('instrumented', []):
                entries[name]['use']['calls'] = None
            if name in self.state.get('action_scopes', {}):
                entries[name]['action_scope'] = self.state['action_scopes'][name]
            if name == 'memory_choice' and switches[name]:
                entries[name]['choices'] = copy.deepcopy(self.state.get('memory_choices', {}))
        row = dict(phase=phase, boundary=edge, weight=weight, crutches=entries,
                   teacher_evidence=sum(float(abs(a).sum()) for a in teacher_arrays(backend.field)),
                   field=backend.field.account(), peak_mb=ONE._peak_mb())
        self.state.setdefault('ledger', []).append(row)


def committed_units(out, state):
    units = []
    for row in state['committed']:
        path = Path(out)/'units'/(row['id']+'.json')
        if sha(path) != row['sha256']:
            raise ValueError('Changed or missing committed unit: '+str(path))
        unit = read(path)
        if unit['unit_id'] != row['id']:
            raise ValueError('Committed unit identity differs: '+str(path))
        units.append(unit)
    return units


def report(out):
    out = Path(out)
    state = read(out/'STATE.json')
    units = committed_units(out, state)
    planned = {r['id']: r for p in PHASES for r in state['plan'][p]}
    if len({r['id'] for r in state['committed']}) != len(state['committed']):
        raise ValueError('Repeated committed unit')
    for u in units:
        if 'item_id' in u and (u['item_id'] not in planned or u['input_digest'] != planned[u['item_id']]['digest']):
            raise ValueError('Course unit input digest differs from its frozen item')
    phases = {}
    for phase in PHASES:
        items = []
        for row in state['plan'][phase]:
            trials = [u for u in units if u.get('item_id') == row['id']]
            right = next((i for i, u in enumerate(trials) if u['status'] == 'right'), None)
            items.append(dict(id=row['id'], name=row['name'], input_digest=row['digest'],
                              status=trials[-1]['status'] if trials else 'not reached', attempts=len(trials),
                              wall=sum(u['attempt_wall'] for u in trials),
                              attempts_to_right=None if right is None else right+1,
                              time_to_right=None if right is None else sum(u['attempt_wall'] for u in trials[:right+1]),
                              phase_time_to_right=None if right is None else trials[right]['phase_elapsed'],
                              results=[u['unit_id'] for u in trials]))
        phases[phase] = dict(items=items, counts={s: sum(r['status'] == s for r in items) for s in STATUSES},
                             attempts=sum(r['attempts'] for r in items), spent=state['spent'][phase],
                             budget=state['budgets'][phase], finished=phase in state['finished'])
    curves = []
    for g in range(4):
        expected = len((state.get('rsi_suite') or {}).get('assessment', []))
        rows = [u for u in units if u.get('measure') == 'rsi' and u.get('generation') == g]
        curves.append(dict(generation=g, right=sum(u['status'] == 'right' for u in rows), N=expected,
                           observed=len(rows), missing=expected-len(rows),
                           g=sum(u['status'] == 'right' for u in rows)/expected if expected else None))
    result = dict(schema='u5-course-1', protocol=state['protocol'], phases=phases, rsi=curves,
                  rsi_work=[u for u in units if u.get('measure') == 'rsi-work'],
                  complete=all(p in state['finished'] for p in ORDER), stop=state.get('stop'),
                  dictionary=state['dictionary'], settings=state['settings'], ledger_boundaries=len(state.get('ledger', [])),
                  time=dict(spent=state['spent'], peak_mb=max((u.get('peak_mb') or 0 for u in units), default=0)))
    result['coverage_complete'] = all(r['counts']['not reached'] == 0 for r in phases.values()) and all(
        g['N'] > 0 and g['missing'] == 0 for g in curves)
    C.write_json(out/'COURSE.json', result)
    lines = '\n'.join(json.dumps(C.json_safe(r), sort_keys=True, default=str, allow_nan=False)
                      for r in state.get('ledger', []))
    tmp = out/'LEDGER.jsonl.tmp'
    tmp.write_text(lines + ('\n' if lines else ''), encoding='utf-8')
    os.replace(tmp, out/'LEDGER.jsonl')
    return result


def commit(out, backend, state, unit=None):
    if unit is not None:
        path = out/'units'/(unit['unit_id']+'.json')
        C.write_json(path, unit)
        state['committed'].append(dict(id=unit['unit_id'], sha256=sha(path)))
    slot = 1 - state.get('slot', 1)
    path = out/f'checkpoint-{slot}.pt'
    backend.save(path)
    state.update(slot=slot, checkpoint=path.name, checkpoint_sha256=sha(path))
    C.write_json(out/'STATE.json', state)


def rsi_phase(out, backend, state, deadline, task_wall, batches, clock=time.time):
    """Use the hardened pilot's tasks, independent observer and sleep methods.

    Reserve before teaching when a suite is supplied. Course-derived suites are
    frozen once after study; they are development runs, not bake-off comparisons.
    """
    if not isinstance(backend, UBackend):
        if hasattr(backend, 'rsi'):
            return backend.rsi(out, state, deadline, task_wall, batches)
        return
    mind = backend.mind
    start, spent = clock(), state['spent']['rsi']
    def save(unit=None):
        state['spent']['rsi'] = spent+max(0., clock()-start)
        commit(out, backend, state, unit)
    if not state.get('rsi_suite'):
        state['rsi_suite'] = RSI.freeze_suite(mind, state['protocol']['seed'])
        save()
    suite = state['rsi_suite']
    mind.sleep.reserved = set(suite['reserved'])
    mind.sleep.reserved_sources = {r['source'] for r in suite['assessment']}
    done = {r['id'] for r in state['committed']}
    for generation in range(4):
        if generation:
            for j, spec in enumerate(suite['wake']):
                uid = f'rsi-g{generation}-wake-{j:03d}'
                if uid in done or clock() >= deadline:
                    continue
                t0 = clock()
                try:
                    rec = mind.live(RSI.build_task(spec), task_wall=min(task_wall, deadline-clock()))
                    if rec.get('verdict') == 'SURE AND WRONG':
                        raise ValueError('Wake tripwire: sure and wrong')
                    status, failure = ('right' if rec['proven'] else 'not-yet'), None
                except PortBudget as exc:
                    rec, status, failure = {}, 'not-yet', str(exc)
                unit = dict(unit_id=uid, measure='rsi-work', generation=generation, work='wake',
                            status=status, failure=failure, record=C.BASE.unit_of(rec), wall=clock()-t0)
                save(unit)
            uid = f'rsi-g{generation}-sleep'
            if uid not in done and clock() < deadline:
                t0 = clock()
                with mind.scope():
                    try:
                        abstractions = mind.sleep.abstract()
                        abstract_failure = None
                    except PortBudget as exc:
                        abstractions, abstract_failure = [], str(exc)
                    try:
                        dreams = mind.sleep.dream(32, deadline=min(deadline, clock()+120)) if clock() < deadline else []
                        dream_failure = None
                    except PortBudget as exc:
                        dreams, dream_failure = [], str(exc)
                save(dict(unit_id=uid, measure='rsi-work', generation=generation,
                          work='abstract-dream', abstracts=len(abstractions), dreams=len(dreams),
                          port_misses=dict(abstract=abstract_failure, dream=dream_failure), wall=clock()-t0))
            for j in range(batches):
                uid = f'rsi-g{generation}-train-{j:03d}'
                if uid in done or clock() >= deadline:
                    continue
                t0 = clock()
                if mind.sleep.replay:
                    try:
                        trained = mind.train(1, 8, deadline=deadline)
                        failure = None
                    except PortBudget as exc:
                        trained, failure = [], str(exc)
                else:
                    trained, failure = [], 'no checked wake replay; no teacher program is substituted'
                save(dict(unit_id=uid, measure='rsi-work', generation=generation,
                          work='train', records=trained, failure=failure, wall=clock()-t0))
        for j, spec in enumerate(suite['assessment']):
            uid = f'rsi-g{generation}-exam-{j:03d}'
            if uid in done or clock() >= deadline:
                continue
            try:
                row = mind.assess(RSI.build_task(spec), task_wall=min(task_wall, deadline-clock()))
            except PortBudget as exc:
                row = dict(solved=False, status='not-yet', failure=str(exc), wall=0.)
            unit = dict(row, unit_id=uid, measure='rsi', generation=generation,
                        status='right' if row['solved'] else row.get('status', 'not-yet'),
                        input_digest=digest(spec), peak_mb=row.get('memory_mb'))
            save(unit)


def run(out, *, seed=3, hours=5.75, device='cpu', shares=SHARES, task_wall=30., batches=16,
        book=None, rsi_suite=None, switches=None, plan=None, backend_factory=None, clock=time.time,
        absolute_deadline=None, taught_ways=True):
    out = Path(out)
    (out/'units').mkdir(parents=True, exist_ok=True)
    if not math.isfinite(hours) or not 0 < hours <= 6 or not math.isfinite(task_wall) or task_wall <= 0:
        raise ValueError('Finite positive wall and at most six hours required')
    if len(shares) != 6 or any(not math.isfinite(s) or s <= 0 for s in shares) or batches < 0:
        raise ValueError('Six finite positive shares and nonnegative batch count required')
    plan = C.make_plan(seed) if plan is None else plan
    frozen_plan = public_plan(plan)
    suite = read(rsi_suite) if isinstance(rsi_suite, (str, Path)) else rsi_suite
    if suite:
        validate_suite(suite)
    backend = backend_factory() if backend_factory else UBackend(seed, device, switches)
    if backend.kind == 'U':
        retire_lesson_words()
    book_path = book or os.environ.get('SERA_BOOK')
    dictionary = DICT.load(book_path)
    if book_path and dictionary is None:
        raise ValueError('Explicit dictionary is not readable')
    if hasattr(backend, 'mind'):
        backend.mind.book = dictionary
    else:
        C.TK.BOOK = dictionary
    protocol = dict(seed=seed, hours=hours, shares=list(shares), task_wall=task_wall, batches=batches,
                    device=device, backend=backend.kind, switches=backend.settings(), runner=runner_identity(),
                    learner=RSI.code_identity(), source=RSI.source_identity(), plan=digest(frozen_plan),
                    suite=digest(suite), book=str(book_path) if book_path else None,
                    book_sha256=book_identity(book_path),
                    knobs=CR.settings(include_course=True), rsi_placement='after study, before all tests')
    protocol['taught_ways'] = bool(taught_ways)
    protocol['phase_fade'] = WEIGHTS if backend.kind == 'U' else 'legacy per-task fade / native learned weights'
    protocol = C.json_safe(protocol)
    if (out/'STATE.json').exists():
        state = read(out/'STATE.json')
        if state['protocol'] != protocol:
            raise ValueError('Resume protocol changed; use a fresh output directory')
        if sha(out/state['checkpoint']) != state['checkpoint_sha256']:
            raise ValueError('Course checkpoint changed')
        backend.load(out/state['checkpoint'])
        committed_units(out, state)
        state.pop('stop', None)
    else:
        state = dict(protocol=protocol, plan=frozen_plan, committed=[], finished=[], ledger=[],
                     budgets={p: hours*3600*s/sum(shares) for p, s in zip(ORDER, shares)},
                     spent={p: 0. for p in ORDER}, settings=backend.settings(),
                     dictionary=dict(loaded=dictionary is not None, path=protocol['book']),
                     weight=1., rsi_suite=suite, active=None, phase_deadlines={},
                     total_deadline=min(clock()+hours*3600, absolute_deadline if absolute_deadline is not None else math.inf))
        if suite and hasattr(backend, 'mind'):
            backend.mind.sleep.reserved = set(suite['reserved'])
            backend.mind.sleep.reserved_sources = {r['source'] for r in suite['assessment']}
        commit(out, backend, state)
    meter = Meter(state)
    try:
        for phase in ORDER:
            if phase in state['finished']:
                continue
            if state['active'] != phase:
                weight = WEIGHTS[phase] if backend.kind == 'U' else 1.
                fade(backend.field, state['weight'], weight)
                state['weight'], state['active'] = weight, phase
                state['phase_deadlines'][phase] = min(state['total_deadline'], clock()+state['budgets'][phase])
                if phase == 'lesson' and hasattr(backend, 'teach_words'):
                    backend.teach_words()
                meter.boundary(backend, phase, 'enter', state['weight'])
                commit(out, backend, state)
            start, spent = clock(), state['spent'][phase]
            deadline = state['phase_deadlines'][phase]
            with meter.measure(backend), evidence_weight(state['weight'], taught_ways=taught_ways):
                if phase == 'rsi':
                    rsi_phase(out, backend, state, deadline, min(task_wall, 10.), batches, clock)
                else:
                    prior = {}
                    for u in committed_units(out, state):
                        if 'item_id' in u:
                            prior.setdefault(u['item_id'], []).append(u)
                    queue = [r for r in plan[phase] if not prior.get(r['id']) or
                             (prior[r['id']][-1]['status'] != 'right' and phase != 'test3' and
                              (phase != 'test1' or len(prior[r['id']]) < 2))]
                    if phase == 'study' and hasattr(backend, 'mind') and backend.mind.crutches['gap_syndromes']:
                        views, by_view, misses = [], {}, []
                        for row in queue:
                            try:
                                view = TaskView.from_task(C.materialize(row, phase))
                            except PortBudget:
                                misses.append(row)  # still attempted and recorded below
                                continue
                            views.append(view)
                            by_view[id(view)] = row
                        queue = [by_view[id(v)] for v in backend.mind.study_order(views)]+misses
                        state.setdefault('study_orders', []).append([r['id'] for r in queue])
                    while queue and clock() < deadline:
                        row = queue.pop(0)
                        trials = prior.get(row['id'], [])
                        t0 = clock()
                        task = C.materialize(row, phase)
                        initial_public_digest = public_task_digest(task)
                        if trials:
                            C.restore_observations(task, trials[-1])
                        meter.counterfactual(task)
                        # Fair first pass; unused time remains for later revisits.
                        wall = min(task_wall, max(.001, (deadline-clock())/max(1, len(queue)+1)))
                        duty = state.setdefault('reliability_duty', {}).get(phase, 0.)
                        weight = state['weight']
                        reliability = math.floor(duty+weight) > math.floor(duty)
                        state['reliability_duty'][phase] = duty+weight
                        try:
                            unit = attempt(backend, task, phase, wall, seed, corrected=bool(trials) and phase == 'test1',
                                           reliability=reliability)
                        except PortBudget as exc:
                            unit = dict(phase=phase, status='not-yet', observer_right=False, feedback=None,
                                        failure=dict(kind='port-budget', reason=str(exc)), response=None,
                                        observations=list(task.data) if task.form == 'exact' else None)
                            if phase == 'test1' and not trials:
                                unit['correction'] = C.correction(task, None, {}, seed)
                                unit['observations'] = list(task.data) if task.form == 'exact' else None
                        elapsed = max(0., clock()-t0)
                        state['spent'][phase] = spent+max(0., clock()-start)
                        uid = f"{row['id']}-a{len(trials)+1:04d}"
                        unit.update(item_id=row['id'], unit_id=uid, input_digest=row['digest'],
                                    public_digest=initial_public_digest,
                                    attempt=len(trials)+1, attempt_wall=elapsed, phase_elapsed=state['spent'][phase],
                                    peak_mb=ONE._peak_mb())
                        meter.observe(unit)
                        # No guessed certainty for an answer that overruns its box.
                        if elapsed > wall and unit['status'] == 'right':
                            unit['status'], unit['time_box_miss'] = 'not-yet', True
                        commit(out, backend, state, unit)
                        trials.append(unit)
                        prior[row['id']] = trials
                        if unit['status'] != 'right' and phase != 'test3' and (phase != 'test1' or len(trials) < 2):
                            queue.append(row)
                        # Native F has no list/grid port: retain the miss without
                        # an unbounded zero-cost retry loop over unsupported input.
                        if unit.get('unsupported') and backend.kind == 'F':
                            queue = [r for r in queue if r['id'] != row['id']]
            state['spent'][phase] = spent+max(0., clock()-start)
            meter.boundary(backend, phase, 'leave', state['weight'])
            state['finished'].append(phase)
            state['active'] = None
            commit(out, backend, state)
            report(out)
    except (Exception, KeyboardInterrupt) as exc:
        # The last checkpoint and units remain authoritative, including when
        # the learner has rolled back. Failure text stays on the runner side.
        saved = read(out/'STATE.json')
        saved['stop'] = dict(reason=str(exc), traceback=traceback.format_exc()[-8000:])
        C.write_json(out/'STATE.json', saved)
        report(out)
        raise
    return report(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command', choices=('run', 'report'))
    ap.add_argument('--out', required=True)
    ap.add_argument('--seed', type=int, default=3)
    ap.add_argument('--hours', type=float, default=5.75)
    ap.add_argument('--task-wall', type=float, default=30.)
    ap.add_argument('--batches', type=int, default=16)
    ap.add_argument('--device', choices=('cpu', 'cuda'), default='cpu')
    ap.add_argument('--book')
    ap.add_argument('--rsi-suite')
    ap.add_argument('--shares', default=','.join(map(str, SHARES)), help='lesson,study,rsi,test1,test2,test3')
    ap.add_argument('--smoke', action='store_true', help='two number items per phase; RSI still requires a suite')
    args = ap.parse_args()
    RSI.torch.set_num_threads(1)
    if args.command == 'report':
        result = report(args.out)
    else:
        retire_lesson_words()
        plan = C.make_plan(args.seed)
        if args.smoke:
            plan = {p: [r for r in rows if r['name'].startswith('number:')][:2] for p, rows in plan.items()}
        result = run(args.out, seed=args.seed, hours=args.hours, task_wall=args.task_wall, batches=args.batches,
                     device=args.device, book=args.book, rsi_suite=args.rsi_suite, plan=plan,
                     shares=tuple(float(s) for s in args.shares.split(',')))
    print('COURSE DONE', json.dumps(dict(complete=result['complete'], coverage_complete=result['coverage_complete'],
                      phases={p: r['counts'] for p, r in result['phases'].items()}, rsi=result['rsi'], stop=result['stop']),
                      default=str), flush=True)
    if not result['complete']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
