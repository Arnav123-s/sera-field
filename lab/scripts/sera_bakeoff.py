"""Frozen-input F / Phi / U comparison; every table is rebuilt from saved units.

freeze writes the teacher/observer suite once. run executes ONE independent arm
per VM. report never constructs a learner or regrades a saved answer. ARC is
development-only (the ARC-AGI training directory), with explicit pinned IDs.
"""
import argparse
from contextlib import contextmanager
import copy
from fractions import Fraction
import io
import json
import math
import os
from pathlib import Path
import pickle
import random
import sys
import time
import traceback

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import sera_u_course as UC, sera_course as C, sera_u_rsi as RSI
from scripts import sera_arc as ARC, sera_bench_lists as LISTS
from sera import crutches as CR, lang as LG, one as ONE, phi as PH, tasks as TS
from sera_u.field.core_owner import CoreOwner
from sera_u.field.native_owner import NativeConfig
from sera_u.field import core_proposals as GP, core_programs as PROGRAMS
from sera_u.mind import global_rng, restore_rng
from sera_u.ports import PortBudget, digest

torch = RSI.torch
ARMS = ('F', 'Phi', 'U', 'U-no-proposer', 'U-no-a', 'U-no-b', 'U-no-understanding',
        'U-no-inner', 'U-no-ways', 'U-no-curiosity', 'U-no-not-yet', 'U-scrutiny')
ABLATIONS = {
    'U-no-proposer': ('field_proposer',), 'U-no-a': ('memory_layer_a',),
    'U-no-b': ('memory_layer_b',), 'U-no-understanding': ('field_understanding',),
    'U-no-inner': ('inner_judge',), 'U-no-ways': (),
    'U-no-curiosity': ('gap_syndromes', 'aimed_dreams'), 'U-no-not-yet': ('taught_not_yet',),
}
PORTS = {
    'F': 'Pinned CoreOwner, original GraphProposal/choice/meaning/response heads. Scalar num->num uses '
         'its exact rational graph head (four slots), trained on shown-value agreement, no supplied program. '
         'Language/talk uses native option_logits, options from heard context/outputs only; it can select a heard '
         'word phrase but cannot synthesize arbitrary number lists/grids, a lab certificate, lab concepts, HRR, '
         'lab dreams or worked decomposition. '
         'Rail trajectory text can be heard, but has no certified-law output; these are unsupported misses. '
         'Its physical response and semantic heads are retained without invented labels or physics projections.',
    'Phi': 'S27 curriculum and original Sera engine, library/search/talk/rail judge; no geometric owner. '
           'The common runner reserves RSI time for matched autonomous wake practice; no neural sleep update. '
           'S27 live/feedback, per-task fade and lab lesson_words default are preserved and reported. '
           'Scheduling adds shared phase budgets and practice revisits; historical wall totals are not reproduced.',
    'U': 'S27 value/word/book ports, checked replay, geometric owner, lab abilities; individual port limits '
         'remain explicit. lesson_words off; taught_not_yet on; abstain_bar off; scrutiny off in the main arm.',
}


@contextmanager
def arm_environment(arm):
    on, off = set(CR.ON), set(CR.OFF)
    env_on, env_off = os.environ.get('SERA_CRUTCH_ON'), os.environ.get('SERA_CRUTCH_OFF')
    try:
        CR.ON = set()
        CR.OFF = {'judge_scrutiny'}
        if arm != 'Phi':
            CR.OFF.add('lesson_words')
        if arm == 'U-scrutiny':
            CR.OFF.discard('judge_scrutiny')
            CR.ON.add('judge_scrutiny')
        if arm.startswith('U'):
            CR.OFF.update(ABLATIONS.get(arm, ()))
            CR.OFF.add('abstain_bar' if arm != 'U-no-not-yet' else 'taught_not_yet')
            CR.ON.update(k for k in UC.U_CRUTCHES if k not in CR.OFF)
            if arm == 'U-no-not-yet':
                CR.ON.add('abstain_bar')
        os.environ['SERA_CRUTCH_ON'] = ','.join(sorted(CR.ON))
        os.environ['SERA_CRUTCH_OFF'] = ','.join(sorted(CR.OFF))
        yield
    finally:
        CR.ON, CR.OFF = on, off
        for name, value in (('SERA_CRUTCH_ON', env_on), ('SERA_CRUTCH_OFF', env_off)):
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


class PhiBackend:
    kind = 'Phi'

    def __init__(self, seed, device='cpu'):
        self.seed = seed
        random.seed(seed)
        RSI.np.random.seed(seed)
        torch.manual_seed(seed)
        self.field = PH.Field(seed)
        self.engine = ONE.Sera(seed, self.field)

    def settings(self):
        return {k: CR.on(k) for k in sorted(CR.REGISTRY)}

    def save(self, path):
        # Unlike field-only saves, preserve stochastic streams and engine state.
        payload = dict(field=self.field, engine={k: v for k, v in self.engine.__dict__.items() if k != 'field'},
                       rng=global_rng(), vocab=copy.deepcopy((TS.VOCAB, TS.WORDS, TS._NEXT)))
        temp = Path(str(path)+'.pending')
        temp.write_bytes(pickle.dumps(payload, protocol=5))
        os.replace(temp, path)

    def load(self, path):
        payload = pickle.loads(Path(path).read_bytes())
        self.field = payload['field']
        self.engine = ONE.Sera(self.seed, self.field)
        self.engine.__dict__.update(payload['engine'])
        TS.VOCAB, TS.WORDS, TS._NEXT = copy.deepcopy(payload['vocab'])
        restore_rng(payload['rng'])

    def live(self, task, phase, wall, channel, teaching=False):
        old = ONE.MAX_WALL
        try:
            ONE.MAX_WALL = wall
            return self.engine.live(task, teaching=teaching, answer_channel=channel)
        finally:
            ONE.MAX_WALL = old

    def course_attempt(self, task, phase, wall, seed, corrected=False, reliability=True):
        # Literal S27 feedback engine: keep the lab arm's original default
        # channels instead of silently installing U7's read-only audit ports.
        unit = C.live(self.engine, task, phase, time.time()+wall, seed, corrected=corrected)
        if unit['status'] == 'abstained':
            unit['status'] = 'not-yet'
        if unit.get('feedback') is not None:
            unit['feedback']['reliability'] = phase == 'test2' and CR.on('course_told_wrong')
        return unit

    def snapshot(self):
        return copy.deepcopy(self)

    def rsi(self, out, state, deadline, task_wall, batches):
        # Same reserved wake examples, independent autonomous history. No U
        # replay or invented analogue of a neural update is attached to Phi.
        return baseline_rsi(self, out, state, deadline, task_wall, batches)


class NativeAccount:
    def __init__(self):
        self.tasks = 0

    def account(self):
        return dict(tasks=self.tasks, concepts=0, note='native owner; no lab concept Field')


def text_context(task):
    passage = [TS.text(s) for s in task.reading()] if hasattr(task, 'reading') else []
    if task.form == 'exact':
        rows = [f'{TS.text(x)} -> {TS.text(y)}' if task.subject == 'language' else repr((x, y)) for x, y in task.data]
    else:
        # The same measured rail trajectories, with no hidden mass/force labels.
        rows = [repr((tuple(t.x), tuple(t.v))) for t in task.throws]
    return ' '.join(passage + rows + [TS.text(task.words)]) or 'observed empty context'


class NativeBackend:
    kind = 'F'

    def __init__(self, seed, device='cpu'):
        self.seed, self.device = seed, device
        torch.use_deterministic_algorithms(True)
        random.seed(seed)
        RSI.np.random.seed(seed)
        torch.manual_seed(seed)
        # Same explicitly reduced engineering geometry as U, pinned equations,
        # its OWN heads. No FieldOwner / lab production alphabet / new readout.
        self.owner = CoreOwner(NativeConfig(nodes=4, rounds=1)).to(device)
        self.optimizer = torch.optim.AdamW(self.owner.parameters(), lr=.001, weight_decay=.0001)
        self.field = NativeAccount()

    def settings(self):
        return {k: False for k in sorted(CR.REGISTRY)}

    def save(self, path):
        payload = dict(owner=self.owner.state_dict(), optimizer=self.optimizer.state_dict(),
                       field=self.field, rng=global_rng())
        temp = Path(str(path)+'.pending')
        torch.save(payload, temp)
        os.replace(temp, path)

    def load(self, path):
        payload = torch.load(path, map_location=self.device, weights_only=False)
        self.owner.load_state_dict(payload['owner'])
        self.optimizer.load_state_dict(payload['optimizer'])
        self.field = payload['field']
        restore_rng(payload['rng'])

    def snapshot(self):
        stream = io.BytesIO()
        torch.save(dict(owner=self.owner.state_dict(), optimizer=self.optimizer.state_dict(),
                        field=self.field, rng=global_rng()), stream)
        result = NativeBackend(self.seed, self.device)
        payload = torch.load(io.BytesIO(stream.getvalue()), map_location=self.device, weights_only=False)
        result.owner.load_state_dict(payload['owner'])
        result.optimizer.load_state_dict(payload['optimizer'])
        result.field = payload['field']
        restore_rng(payload['rng'])
        return result

    def scalar(self, task, wall, training):
        start = time.time()
        context = text_context(task)
        question = 'infer scalar output from the observed input output pairs'
        state, _ = self.owner.remember_texts([context])
        distribution = self.owner.program_distribution(state, [question], [1])
        proposals = GP.sample(distribution, 32)
        scored = []
        for row in proposals:
            if time.time()-start >= wall:
                break
            try:
                correct = sum(Fraction(PROGRAMS.execute(row['program'], [int(x)])['value']) == y for x, y in task.data)
            except (ValueError, ZeroDivisionError, OverflowError):
                correct = 0
            scored.append((correct, row))
        if training and scored:
            # Checked values provide reward, not a teacher's graph. Centered
            # policy gradient updates the original graph head and owner together.
            rewards = [n/max(1, len(task.data)) for n, _ in scored]
            center = sum(rewards)/len(rewards)
            loss = sum(-(r-center)*GP.log_probability(distribution, row['program'], row['branch'])
                       for r, (_, row) in zip(rewards, scored))/len(scored)
            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.owner.parameters(), 1.)
            self.optimizer.step()
        best = max(enumerate(scored), key=lambda v: (v[1][0], -v[0]))[1][1]['program'] if scored else None
        return best

    def language(self, task, training, deadline=math.inf):
        context = text_context(task)
        options = sorted({TS.text(y) for _, y in task.data})
        if not options:
            return []
        if training:
            for x, y in task.data:
                if time.time() >= deadline:
                    break
                row = self.owner.option_logits([context+' query '+TS.text(x)], [options])
                loss = -row.log_softmax(-1)[0, options.index(TS.text(y))]
                self.optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.owner.parameters(), 1.)
                self.optimizer.step()
        return options

    def course_attempt(self, task, phase, wall, seed, corrected=False, reliability=True):
        deadline = time.time()+wall
        training = phase == 'lesson' or corrected
        self.field.tasks += 1
        scalar = task.form == 'exact' and list(task.inputs.values()) == ['num'] and task.out == 'num'
        language = task.form == 'exact' and task.subject == 'language' and task.out in ('num', 'list')
        # Native scalar symbols are not silently treated as an arbitrary numeric
        # regression target. Only native options are used for word-valued outputs.
        if not scalar and not language:
            return dict(phase=phase, status='not-yet', unsupported=True, response=None, feedback=None,
                        reason='native heads cannot emit this output/claim schema', observations=None)
        program = self.scalar(task, wall, training) if scalar else None
        options = self.language(task, training, deadline) if language else []
        def value(x):
            if language:
                if not options:
                    return None
                with torch.no_grad():
                    logits = self.owner.option_logits([text_context(task)+' query '+TS.text(x)], [options])
                word = options[int(logits[0].argmax())]
                return tuple(TS.sym(w) for w in word.split()) if task.out == 'list' else TS.sym(word)
            if program is None:
                return None
            try:
                return Fraction(PROGRAMS.execute(program, [int(x)])['value'])
            except (ValueError, ZeroDivisionError, OverflowError):
                return None
        predictions = [value(x) for x in task._probe_inputs] if scalar else []
        supplied = program is not None or bool(options)
        # Same detached fresh observer distribution as S27 (including its
        # Story lambda fix), never only a handful of convenient public probes.
        observer = copy.deepcopy(task)
        if isinstance(observer, TS.Story):
            observer._fresh = lambda rng: observer._make(rng)[0]
        grading_rng = RSI.np.random.default_rng([seed, 991, len(task.name)])
        old_vocab = copy.deepcopy((TS.VOCAB, TS.WORDS, TS._NEXT))
        try:
            right = bool(supplied)
            for _ in range(200):
                if not right:
                    break
                if time.time() >= deadline:
                    right = None
                    break
                x = observer._fresh(grading_rng)
                if value(x) != observer._y(x):
                    right = False
        finally:
            TS.VOCAB, TS.WORDS, TS._NEXT = old_vocab
        # A study/test2 learner receives ONE bit about its proposed graph. No
        # private values or positive target graphs are used to update its heads.
        if supplied and right is not None and phase in ('study', 'test2') and scalar:
            state, _ = self.owner.remember_texts([text_context(task)])
            distribution = self.owner.program_distribution(state, ['infer scalar output from the observed input output pairs'], [1])
            logp = torch.logsumexp(torch.stack([GP.log_probability(distribution, program, b) for b in range(3)]), 0)
            loss = -(1. if right else -1.)*logp
            self.optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.owner.parameters(), 1.)
            self.optimizer.step()
        unit = dict(phase=phase, status='not-yet' if right is None else 'right' if right else 'wrong' if supplied else 'not-yet',
                    observer_right=bool(right), response=program or (options if language else None), native_predictions=[str(p) for p in predictions],
                    feedback=None if phase == 'test3' or not supplied or right is None else
                    dict(verdict='right' if right else 'wrong', source='book' if phase == 'study' else 'teacher'),
                    observations=list(task.data), proven=False, native_graph=program,
                    note='native response; no lab proof certificate')
        if phase == 'test1' and not corrected and not right:
            unit['correction'] = C.correction(task, None, {}, seed)
            unit['observations'] = list(task.data)
        return unit

    def rsi(self, out, state, deadline, task_wall, batches):
        return baseline_rsi(self, out, state, deadline, task_wall, batches)


def backend_for(arm, seed, device):
    if arm == 'F':
        return NativeBackend(seed, device)
    if arm == 'Phi':
        return PhiBackend(seed, device)
    return UC.UBackend(seed, device, UC.u_switches(ABLATIONS.get(arm, ())))


def baseline_rsi(backend, out, state, deadline, task_wall, batches):
    suite = state['rsi_suite']
    done = {u['id'] for u in state['committed']}
    start_phase, prior_spent = time.time(), state['spent']['rsi']
    def save(unit):
        state['spent']['rsi'] = prior_spent+time.time()-start_phase
        UC.commit(out, backend, state, unit)
    if not suite:
        raise ValueError('Bake-off requires the shared frozen RSI observer suite')
    for g in range(4):
        if g:
            for i, spec in enumerate(suite['wake']):
                uid = f'rsi-g{g}-wake-{i:03d}'
                if uid in done or time.time() >= deadline:
                    continue
                start = time.time()
                try:
                    task = RSI.build_task(spec)
                    if backend.kind == 'F':
                        # Same wake example values; F can train its own graph head.
                        rec = backend.course_attempt(task, 'lesson', min(task_wall, deadline-time.time()), backend.seed)
                    else:
                        rec = UC.attempt(backend, task, 'study', min(task_wall, deadline-time.time()), backend.seed)
                except PortBudget as exc:
                    rec = dict(status='not-yet', failure=dict(kind='port-budget', reason=str(exc)))
                save(dict(unit_id=uid, measure='rsi-work', generation=g,
                                                    work='wake', record=rec, wall=time.time()-start))
            uid = f'rsi-g{g}-sleep'
            if uid not in done and time.time() < deadline:
                save(dict(unit_id=uid, measure='rsi-work', generation=g,
                                                    work='abstract-dream-train', unsupported=True,
                                                    reason='native/lab baseline has no SERA-U sleep objective'))
        for i, spec in enumerate(suite['assessment']):
            uid = f'rsi-g{g}-exam-{i:03d}'
            if uid in done or time.time() >= deadline:
                continue
            clone = backend.snapshot()
            start = time.time()
            box = max(.001, min(task_wall, deadline-start))
            before_rng = global_rng()
            try:
                rec = UC.attempt(clone, RSI.build_task(spec), 'test3', box, backend.seed)
            except PortBudget as exc:
                rec = dict(status='not-yet', failure=str(exc))
            finally:
                restore_rng(before_rng)
            elapsed = time.time()-start
            if elapsed > box and rec['status'] == 'right':
                rec.update(status='not-yet', time_box_miss=True)
            save(dict(unit_id=uid, measure='rsi', generation=g,
                                                input_digest=digest(spec), status=rec['status'], record=rec,
                                                wall=elapsed, box=box))


def freeze(out, *, seed, rsi_suite, list_data, arc_data, arc_ids, list_ids, task_wall=30., hours=5.75, book=None):
    out = Path(out)
    if out.exists():
        raise ValueError('Frozen suite destination already exists')
    if not math.isfinite(hours) or not 0 < hours <= 6 or not math.isfinite(task_wall) or task_wall <= 0:
        raise ValueError('Finite positive time box required, at most six hours per arm')
    suite = UC.validate_suite(UC.read(rsi_suite))
    plan = C.make_plan(seed)
    trials = LISTS.load(list_data)
    list_ids = list_ids or sorted(trials)[:3]
    development = ARC.load(arc_data, 'training')
    arc_ids = arc_ids or sorted(development)[:3]
    if not arc_ids or not list_ids or any(i not in development for i in arc_ids) or any(i not in trials for i in list_ids):
        raise ValueError('Missing list functions or ARC development IDs (training directory only)')
    if any(len(trials[i]) != 11 for i in list_ids):
        raise ValueError('The list benchmark requires all eleven ordered trials per function')
    talk = TS.talk_world(seed+900_000, n=24)
    frozen = dict(schema='u5-bakeoff-suite-1', seed=seed, task_wall=task_wall, hours=hours,
                  course=UC.public_plan(plan), rsi=suite, lists={i: trials[i] for i in list_ids},
                  arc={i: development[i] for i in arc_ids}, arc_split='training/development',
                  talk=[dict(input=x, answer=y, kind=k) for x, y, k in talk.items],
                  book=str(book) if book else None, source=RSI.source_identity(), learner=RSI.code_identity(),
                  book_sha256=UC.book_identity(book),
                  runner=UC.runner_identity(), vocab=dict(vocab=TS.VOCAB, words=TS.WORDS, next=TS._NEXT))
    # Full content digests include labels on the observer side; public input
    # digests are separately recorded in every attempt. No digest substitutes
    # for actually passing the same example/query data to each arm.
    frozen['inputs_digest'] = digest({k: frozen[k] for k in ('course', 'rsi', 'lists', 'arc', 'talk')})
    C.write_json(out, frozen)
    return frozen


def restore_vocab(frozen):
    TS.VOCAB = {str(k): int(v) for k, v in frozen['vocab']['vocab'].items()}
    TS.WORDS = {int(k): str(v) for k, v in frozen['vocab']['words'].items()}
    TS._NEXT = list(frozen['vocab']['next'])


def match_plan(frozen):
    plan = C.make_plan(frozen['seed'])
    if UC.public_plan(plan) != frozen['course']:
        # JSON number/list container normalization is intentional.
        if digest(UC.public_plan(plan)) != digest(frozen['course']):
            raise ValueError('Course instances differ from the frozen suite')
    return plan


def clone_backend(backend):
    if hasattr(backend, 'mind'):
        result = object.__new__(UC.UBackend)
        result.mind = SeraU_clone(backend.mind)
        result.mind.progress['assessment'] = True
        return result
    return backend.snapshot()


def SeraU_clone(mind):
    return UC.SeraU.loads(mind.dumps(), exact=True)


def evaluate_task(backend, task, wall, seed):
    clone = clone_backend(backend)
    try:
        return UC.attempt(clone, task, 'test3', wall, seed)
    except PortBudget as exc:
        return dict(status='not-yet', failure=dict(kind='port-budget', reason=str(exc)))


def evaluation_plan(frozen):
    rows = []
    for i, row in enumerate(frozen['course']['test3']):
        rows.append(dict(id='world-'+row['id'], measure='physics' if row['name'].startswith('rail:') else
                         'unseen-list' if row['name'].startswith('list:') else
                         'unseen-number' if row['name'].startswith('number:') else 'language', row=row))
    for fid in sorted(frozen['lists']):
        for j in range(len(frozen['lists'][fid])):
            rows.append(dict(id=f'list-{fid}-{j+1:02d}', measure='list-benchmark', fid=fid, trial=j))
    rows += [dict(id='arc-'+pid, measure='arc-development', pid=pid) for pid in sorted(frozen['arc'])]
    rows += [dict(id=f'talk-{j:03d}', measure='talk', turn=j) for j in range(len(frozen['talk']))]
    return rows


def evaluation_digest(spec, frozen, plan):
    kind = spec['measure']
    if kind in ('physics', 'unseen-list', 'unseen-number', 'language'):
        row = next(r for r in plan['test3'] if r['id'] == spec['row']['id'])
        return UC.public_task_digest(C.materialize(row, 'test3'))
    if kind == 'list-benchmark':
        trials, j = frozen['lists'][spec['fid']], spec['trial']
        return UC.public_task_digest(LISTS.ListBench(spec['fid'], trials[:j], trials[j][0], seed=frozen['seed']))
    if kind == 'arc-development':
        return UC.public_task_digest(ARC.Puzzle(spec['pid'], frozen['arc'][spec['pid']]))
    return digest([r['input'] for r in frozen['talk'][:spec['turn']+1]])


def measure(backend, spec, frozen, plan, wall):
    kind, seed = spec['measure'], frozen['seed']
    if kind in ('physics', 'unseen-list', 'unseen-number', 'language'):
        row = next(r for r in plan['test3'] if r['id'] == spec['row']['id'])
        task = C.materialize(row, 'test3')
        return dict(evaluate_task(backend, task, wall, seed), input_digest=row['digest'])
    if kind == 'list-benchmark':
        fid, j = spec['fid'], spec['trial']
        trials = frozen['lists'][fid]
        task = LISTS.ListBench(fid, trials[:j], trials[j][0], seed=seed)
        clone = clone_backend(backend)
        if clone.kind == 'F':
            return dict(status='not-yet', unsupported=True, input_digest=digest((trials[:j], trials[j][0])))
        captures = {}
        def channel(t, law, concepts, proven):
            captures.update(law=law, concepts=copy.deepcopy(concepts), proven=proven)
            return None
        try:
            rec = clone.live(UC.CourseWorld(task, 'test3'), 'test3', wall, channel)
            law = rec.get('answer')
            prediction = LG.safe(law, {'l': tuple(trials[j][0])}, captures.get('concepts', {})) if law else None
            right = prediction == tuple(trials[j][1])
            status = 'right' if right else 'wrong' if prediction is not None else 'not-yet'
            return dict(status=status, prediction=prediction, target=trials[j][1], trial=j+1,
                        input_digest=digest((trials[:j], trials[j][0])), record=C.BASE.unit_of(rec))
        except PortBudget as exc:
            return dict(status='not-yet', failure=dict(kind='port-budget', reason=str(exc)),
                        input_digest=digest((trials[:j], trials[j][0])))
    if kind == 'arc-development':
        task = ARC.Puzzle(spec['pid'], frozen['arc'][spec['pid']])
        # Public-only world: the test labels are kept in observer_task. ARC's
        # verifier can use given examples and grid form, never the test outputs.
        public = copy.deepcopy(task)
        public._answers = []
        clone = clone_backend(backend)
        if clone.kind == 'F':
            return dict(status='not-yet', unsupported=True, score=0., input_digest=C.input_digest(task))
        captures = {}
        def channel(t, law, concepts, proven):
            captures['concepts'] = copy.deepcopy(concepts)
            return None
        try:
            rec = clone.live(public, 'test3', wall, channel)
            a1, a2 = ARC.attempts(task, rec, captures.get('concepts', {}))
            score = ARC.score(task, a1, a2)
            return dict(status='right' if score == 1 else 'wrong' if a1 is not None else 'not-yet',
                        score=score, answers=[a1, a2], input_digest=C.input_digest(task), record=C.BASE.unit_of(rec))
        except PortBudget as exc:
            return dict(status='not-yet', score=0., failure=dict(kind='port-budget', reason=str(exc)),
                        input_digest=C.input_digest(task))
    # Every talk prefix is replayed on a disposable copy so delayed U7 answers
    # can mature across turns, without leaking y/kind or retaining exam learning.
    j = spec['turn']
    clone = clone_backend(backend)
    prefix = frozen['talk'][:j+1]
    emitted = []
    if clone.kind == 'F':
        for row in prefix:
            x = LG.freeze(row['input'])
            context = ' '.join(TS.text(s) for s in x[1:]) or 'empty heard situation'
            options = sorted({TS.text(w) for s in x[1:] for w in s})
            said = options[int(clone.owner.option_logits([context+' question '+TS.text(x[0])], [options])[0].argmax())] if options else None
            emitted.append(TS.sym(said) if said else None)
        got = emitted[-1]
    else:
        for row in prefix:
            x = LG.freeze(row['input'])
            if hasattr(clone, 'mind'):
                # Recreate converse's public-only turn seams so pending replies
                # mature. No y, observer kind or correction enters the engine.
                with clone.mind.scope():
                    engine = clone.engine
                    for sentence in x[1:]:
                        engine._ideas().read(sentence, 'talk')
                    if clone.mind.crutches['taught_not_yet']:
                        engine._u_pending_wall = wall/max(1, len(prefix))
                        engine._u_talk_tick()
                    reply = engine.reply(x, x[0])
                    if clone.mind.crutches['taught_not_yet']:
                        engine._u_talk_record(x, x[0], reply[0], {})
                        engine._u_talk_end_turn(x[0])
                        engine.__dict__.pop('_u_pending_wall', None)
            else:
                for sentence in x[1:]:
                    clone.field.ideas.read(sentence, 'talk')
                reply = clone.engine.reply(x, x[0])
            emitted.append(reply)
        final = emitted[-1]
        got = final.get('value') if isinstance(final, dict) else final[0] if isinstance(final, tuple) else final
    target = LG.freeze(prefix[-1]['answer'])
    # Native word choice and lab word-list replies use the same heard text.
    right = got is not None and target is not None and TS.text(got) == TS.text(target)
    delayed = copy.deepcopy(getattr(clone.field, 'u7_talk_events', []))
    for event in delayed:
        original = frozen['talk'][event['asked_turn']-1]
        event['observer_right'] = original['answer'] is not None and event['said'] == TS.text(original['answer'])
    return dict(status='right' if right else 'wrong' if got is not None else 'not-yet',
                response=got, target=target, emissions=emitted,
                delayed=delayed,
                input_digest=digest([row['input'] for row in prefix]))


def run_arm(out, suite_path, arm, *, device='cpu', batches=16):
    started = time.time()
    out = Path(out)
    frozen = UC.read(suite_path)
    if arm not in ARMS:
        raise ValueError('Unknown bake-off arm')
    if frozen['schema'] != 'u5-bakeoff-suite-1' or frozen['arc_split'] != 'training/development':
        raise ValueError('Not a development-only frozen suite')
    if frozen['inputs_digest'] != digest({k: frozen[k] for k in ('course', 'rsi', 'lists', 'arc', 'talk')}):
        raise ValueError('Frozen input content digest changed')
    if frozen['source'] != RSI.source_identity() or frozen['learner'] != RSI.code_identity() or frozen['runner'] != UC.runner_identity():
        raise ValueError('Frozen source/learner/runner changed')
    if frozen['book_sha256'] != UC.book_identity(frozen['book']):
        raise ValueError('Dictionary differs from frozen inputs')
    restore_vocab(frozen)
    with arm_environment(arm):
        plan = match_plan(frozen)
        backend = backend_for(arm, frozen['seed'], device)
        signature = dict(arm=arm, suite_sha256=UC.sha(suite_path), inputs_digest=frozen['inputs_digest'],
                         hours=frozen['hours'], task_wall=frozen['task_wall'], device=device, batches=batches,
                         ports=PORTS['U' if arm.startswith('U') else arm])
        signature['taught_ways'] = arm != 'U-no-ways'
        path = out/'ARM.json'
        out.mkdir(parents=True, exist_ok=True)
        if path.exists():
            if UC.read(path)['protocol'] != signature:
                raise ValueError('Arm resume protocol differs')
        else:
            C.write_json(path, dict(protocol=signature, evaluations=[], finished=False,
                                   started=started, deadline=started+3600*frozen['hours'],
                                   runtime=dict(machine=RSI.platform.platform(), processor=RSI.platform.processor(),
                                                torch=torch.__version__, numpy=RSI.np.__version__,
                                                threads=torch.get_num_threads(), device=device)))
        arm_state = UC.read(path)
        arm_state.pop('stop', None)
        try:
            # 80% teaching including RSI; 20% frozen additional measures.
            # The same phase shares, course inputs and per-item cap apply to all.
            result = UC.run(out/'course', seed=frozen['seed'], hours=frozen['hours']*.8,
                            device=device, task_wall=frozen['task_wall'], batches=batches,
                            book=frozen['book'], rsi_suite=frozen['rsi'], plan=plan,
                            shares=(2., 1., 2., 1., 1., 1.), backend_factory=lambda: backend,
                            absolute_deadline=arm_state['deadline'], taught_ways=arm != 'U-no-ways')
            course_state = UC.read(out/'course'/'STATE.json')
            backend.load(out/'course'/course_state['checkpoint'])
            done = {r['id'] for r in arm_state['evaluations']}
            specs = evaluation_plan(frozen)
            (out/'units').mkdir(exist_ok=True)
            for i, spec in enumerate(specs):
                if spec['id'] in done or time.time() >= arm_state['deadline']:
                    continue
                t0 = time.time()
                remaining = sum(r['id'] not in done for r in specs[i:])
                wall = min(frozen['task_wall'], max(.001, (arm_state['deadline']-t0)/max(1, remaining)))
                before_rng = global_rng()
                before_hash = backend.mind.learning_hash() if hasattr(backend, 'mind') else None
                try:
                    try:
                        unit = measure(backend, spec, frozen, plan, wall)
                    except PortBudget as exc:
                        unit = dict(status='not-yet', failure=dict(kind='port-budget', reason=str(exc)))
                    unit['public_digest'] = evaluation_digest(spec, frozen, plan)
                finally:
                    restore_rng(before_rng)
                if before_hash is not None and before_hash != backend.mind.learning_hash():
                    raise ValueError('Frozen evaluation mutated U learning state')
                elapsed = time.time()-t0
                if elapsed > wall and unit['status'] == 'right':
                    unit.update(status='not-yet', time_box_miss=True)
                    if 'score' in unit:
                        unit['unboxed_score'], unit['score'] = unit['score'], 0.
                unit.update(unit_id=spec['id'], measure=spec['measure'], arm=arm, wall=elapsed,
                            peak_mb=ONE._peak_mb(), box=wall,
                            gpu_peak_bytes=torch.cuda.max_memory_allocated() if device == 'cuda' else 0)
                upath = out/'units'/(spec['id']+'.json')
                C.write_json(upath, unit)
                arm_state['evaluations'].append(dict(id=spec['id'], sha256=UC.sha(upath)))
                C.write_json(path, arm_state)
            arm_state['finished'] = result['complete'] and result['coverage_complete'] and len(arm_state['evaluations']) == len(specs)
            arm_state['finished_at'] = time.time()
        except (Exception, KeyboardInterrupt) as exc:
            arm_state['stop'] = dict(reason=str(exc), traceback=traceback.format_exc()[-8000:])
            arm_state['stopped_at'] = time.time()
            C.write_json(path, arm_state)
            raise
        C.write_json(path, arm_state)
    return arm_state


def report(out, suite_path, runs):
    """All numerators, denominators, digests and timing read from saved units."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    frozen = UC.read(suite_path)
    expected_specs = evaluation_plan(frozen)
    arms = {}
    common_controls = None
    for run_path in runs:
        run_path = Path(run_path)
        state = UC.read(run_path/'ARM.json')
        protocol = state['protocol']
        if protocol['suite_sha256'] != UC.sha(suite_path) or protocol['inputs_digest'] != frozen['inputs_digest']:
            raise ValueError('Bake-off arms have different frozen inputs')
        controls = {k: protocol[k] for k in ('hours', 'task_wall', 'device', 'batches') if k in protocol}
        if any(k in frozen and controls.get(k) != frozen[k] for k in ('hours', 'task_wall')):
            raise ValueError('Saved arm differs from frozen time box')
        if common_controls is not None and common_controls != controls:
            raise ValueError('Bake-off arm time/device/update controls differ')
        common_controls = controls
        arm = protocol['arm']
        if arm in arms:
            raise ValueError('Duplicate arm')
        units = []
        expected = {r['id']: r['measure'] for r in expected_specs}
        if len({e['id'] for e in state['evaluations']}) != len(state['evaluations']):
            raise ValueError('Repeated saved evaluation unit')
        for entry in state['evaluations']:
            upath = run_path/'units'/(entry['id']+'.json')
            if UC.sha(upath) != entry['sha256']:
                raise ValueError('Changed saved evaluation unit')
            unit = UC.read(upath)
            if entry['id'] not in expected or unit['unit_id'] != entry['id'] or unit['measure'] != expected[entry['id']]:
                raise ValueError('Unplanned or renamed saved evaluation unit')
            units.append(unit)
        course = UC.report(run_path/'course')  # reconstruction, never re-execution
        if digest(UC.read(run_path/'course'/'STATE.json')['plan']) != digest(frozen['course']):
            raise ValueError('Course input digests differ')
        measures = {}
        for name in sorted({r['measure'] for r in expected_specs}):
            selected = [u for u in units if u['measure'] == name]
            n = sum(r['measure'] == name for r in expected_specs)
            measures[name] = dict(N=n, observed=len(selected), missing=n-len(selected),
                                  counts={s: sum(u['status'] == s for u in selected) for s in UC.STATUSES[:-1]},
                                  unsupported=sum(bool(u.get('unsupported')) for u in selected),
                                  port_misses=sum((u.get('failure') or {}).get('kind') == 'port-budget'
                                                  for u in selected if isinstance(u.get('failure'), dict)),
                                  wall=sum(u['wall'] for u in selected),
                                  peak_mb=max((u.get('peak_mb') or 0 for u in selected), default=0))
            if name == 'arc-development':
                measures[name]['mean_score'] = sum(u.get('score', 0.) for u in selected)/n if n else None
            if name == 'list-benchmark':
                later = [u for u in selected if u.get('trial', 1) >= 2]
                later_n = sum(max(0, len(v)-1) for v in frozen['lists'].values())
                measures[name]['accuracy_trials_2_plus'] = sum(u['status'] == 'right' for u in later)/later_n if later_n else None
            if name == 'talk':
                last = next((u for u in reversed(selected) if u.get('delayed')), {})
                delayed = last.get('delayed', [])
                measures[name]['delayed_answered'] = len(delayed)
                measures[name]['delayed_right'] = sum(e['observer_right'] for e in delayed)
        course_units = UC.committed_units(run_path/'course', UC.read(run_path/'course'/'STATE.json'))
        course_inputs = [(u['item_id'], u.get('public_digest', u['input_digest'])) for u in course_units if 'item_id' in u]
        arms[arm] = dict(protocol=protocol, complete=state['finished'], course=course, measures=measures,
                         stop=state.get('stop'), course_inputs=course_inputs,
                         runtime=state.get('runtime'),
                         total_wall=(max(state.get('finished_at', 0), state.get('stopped_at', 0), state.get('started', 0))
                                     -state.get('started', 0)),
                         inputs=[(u['unit_id'], u.get('public_digest', u.get('input_digest'))) for u in units])
    # Compare actual observed digests, including partial arms' intersections.
    by_id = {}
    for arm, row in sorted(arms.items()):
        for uid, value in row['inputs']+row['course_inputs']:
            if uid in by_id and by_id[uid] != value:
                raise ValueError('Different actual inputs at '+uid)
            by_id[uid] = value
    result = dict(schema='u5-bakeoff-1', suite_sha256=UC.sha(suite_path), inputs_digest=frozen['inputs_digest'],
                  arms=arms, missing_arms=[a for a in ARMS if a not in arms],
                  complete=len(arms) == len(ARMS) and all(r['complete'] for r in arms.values()),
                  note='Saved runs only. Unsupported, missing and port-budget rows are never right. '
                       'One-seed development pilot; no ranking is asserted before complete measurements.')
    C.write_json(out/'BAKEOFF.json', result)
    lines = ['| arm | lesson_words | scrutiny | test1 right/N | test2 right/N | test3 right/N | g0..g3 | complete |',
             '|---|---|---|---|---|---|---|---|']
    for arm, row in sorted(arms.items()):
        course = row['course']
        cells = [f"{course['phases'][p]['counts']['right']}/{len(course['phases'][p]['items'])}" for p in ('test1', 'test2', 'test3')]
        curve = ', '.join(f"{g['right']}/{g['N']}" for g in course['rsi'])
        settings = course['settings']
        lines.append(f"| {arm} | {settings['lesson_words']} | {settings['judge_scrutiny']} | " +
                     ' | '.join(cells) + f" | {curve} | {row['complete']} |")
    lines += ['', '| arm | course phase | right | wrong | not yet | not reached | attempts | seconds |',
              '|---|---|---|---|---|---|---|---|']
    for arm, row in sorted(arms.items()):
        for phase in ('test1', 'test2', 'test3'):
            p = row['course']['phases'][phase]
            c = p['counts']
            lines.append(f"| {arm} | {phase} | {c['right']} | {c['wrong']} | {c['not-yet']} | "
                         f"{c['not reached']} | {p['attempts']} | {p['spent']:.2f} |")
    lines += ['', '| arm | measure | right/N | wrong | not yet | missing | unsupported | seconds | peak MB |',
              '|---|---|---|---|---|---|---|---|---|']
    for arm, row in sorted(arms.items()):
        for name, m in sorted(row['measures'].items()):
            lines.append(f"| {arm} | {name} | {m['counts']['right']}/{m['N']} | {m['counts']['wrong']} | "
                         f"{m['counts']['not-yet']} | {m['missing']} | {m['unsupported']} | {m['wall']:.2f} | {m['peak_mb']:.1f} |")
    lines += ['', '| arm | total seconds | course peak MB | evaluation peak MB |', '|---|---|---|---|']
    for arm, row in sorted(arms.items()):
        peak = max((m['peak_mb'] for m in row['measures'].values()), default=0)
        lines.append(f"| {arm} | {row['total_wall']:.2f} | {row['course']['time']['peak_mb']:.1f} | {peak:.1f} |")
    lines += ['', 'R/N uses the frozen denominator, including missing and unsupported items. '
              'The JSON also retains ARC mean score, list trials 2+ accuracy, delayed talk answers, '
              'port misses, runtime, per-item time to right and the exact arm port descriptions.',
              'U-no-ways masks new faculty/method/step demonstrations while keeping learned returns '
              'and the separate U7 answer/continue demonstration. Phi retains its S27 feedback default.']
    (out/'BAKEOFF.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    subs = ap.add_subparsers(dest='command', required=True)
    f = subs.add_parser('freeze')
    f.add_argument('--out', required=True)
    f.add_argument('--seed', type=int, default=3)
    f.add_argument('--rsi-suite', required=True)
    f.add_argument('--list-data', required=True)
    f.add_argument('--arc-data', required=True)
    f.add_argument('--arc-ids')
    f.add_argument('--list-ids')
    f.add_argument('--hours', type=float, default=5.75)
    f.add_argument('--task-wall', type=float, default=30.)
    f.add_argument('--book')
    r = subs.add_parser('run')
    r.add_argument('--out', required=True)
    r.add_argument('--suite', required=True)
    r.add_argument('--arm', choices=ARMS, required=True)
    r.add_argument('--device', choices=('cpu', 'cuda'), default='cpu')
    r.add_argument('--batches', type=int, default=16)
    p = subs.add_parser('report')
    p.add_argument('--out', required=True)
    p.add_argument('--suite', required=True)
    p.add_argument('--runs', required=True, help='comma-separated saved arm folders')
    args = ap.parse_args()
    torch.set_num_threads(1)
    if args.command == 'freeze':
        result = freeze(args.out, seed=args.seed, rsi_suite=args.rsi_suite, list_data=args.list_data,
                        arc_data=args.arc_data, arc_ids=args.arc_ids.split(',') if args.arc_ids else None,
                        list_ids=args.list_ids.split(',') if args.list_ids else None, hours=args.hours,
                        task_wall=args.task_wall, book=args.book)
    elif args.command == 'run':
        result = run_arm(args.out, args.suite, args.arm, device=args.device, batches=args.batches)
    else:
        result = report(args.out, args.suite, args.runs.split(','))
    print(json.dumps(dict(command=args.command, out=args.out, complete=result.get('finished', result.get('complete')),
                          inputs_digest=result.get('inputs_digest'), stop=result.get('stop')), default=str), flush=True)
    if args.command == 'run' and not result['finished']:
        raise SystemExit(2)


if __name__ == '__main__':
    main()
