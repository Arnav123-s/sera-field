"""A taught course, independent practice, and three increasingly unaided tests.

All curriculum content lives here, on the teacher/book side. SERA receives examples and intermediate values,
never the Python functions that make them. Checkpoints commit immutable attempt units through field.pkl;
COURSE.json can always be rebuilt from those units. Observer grades never live in the Field.
"""
import argparse
import copy
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

os.environ.setdefault('CCOPS5_SHAPES', 'library')
os.environ.setdefault('CCOPS5_CLAIM', 'functional')
os.environ.setdefault('CCOPS5_BAND', 'claim')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402
from sera import crutches as CR, dictionary as DICT, lang as LG, one as ONE, phi as PH, tasks as TS, talk as TK
try:
    from scripts import sera_one as BASE
except ImportError:  # direct execution from scripts/
    import sera_one as BASE

PHASES = ('lesson', 'study', 'test1', 'test2', 'test3')
SHARES = (2, 1, 1, 1, 1)
STATUSES = ('right', 'wrong', 'abstained', 'not reached')
# These are deliberately different from ALL of sera_one.alone's compositions.
COMPOSED_LISTS = {
    'reverse of one more': (lambda xs: [x + 1 for x in xs], lambda xs: xs[::-1], 'list'),
    'last of the doubled': (lambda xs: [2 * x for x in xs], lambda xs: xs[-1] if xs else 0, 'num'),
}
COMPOSED_NUMBERS = {
    'odd of twice': (lambda n: 2 * n, lambda n: 2 * n + 1),
    'twice the triangle': (lambda n: n * (n + 1) // 2, lambda n: 2 * n),
}
STORIES = (TS.lesson_first, TS.lesson_last, TS.lesson_who, TS.lesson_where, TS.lesson_where_now,
           TS.lesson_who_in, TS.lesson_is_in, TS.closed_where, TS.closed_what_is)


def composed(seed):
    out = []
    for i, (name, (inner, outer, typ)) in enumerate(COMPOSED_LISTS.items()):
        def build(name=name, inner=inner, outer=outer, typ=typ, i=i):
            task = TS.list_task('list: ' + name, lambda x: outer(inner(x)), typ, seed, 500 + i,
                                words=name.split())
            task._worked_values = lambda x: (inner(x), outer(inner(x)))
            task.course_composed = True
            return task
        out.append(('list: ' + name, build))
    for i, (name, (inner, outer)) in enumerate(COMPOSED_NUMBERS.items()):
        def build(name=name, inner=inner, outer=outer, i=i):
            task = TS.number_task('number: ' + name, lambda x: outer(inner(x)), seed, 500 + i,
                                  words=name.split())
            task._worked_values = lambda x: (inner(x), outer(inner(x)))
            task.course_composed = True
            return task
        out.append(('number: ' + name, build))
    return out


def lesson_builders(seed, simple=False):
    base = BASE.teaching(seed)
    if simple:
        base = [(n, b) for n, b in base if 'spring and drag' not in n]
        stories = STORIES[:2]  # positional questions are the single-step language items
    else:
        stories = STORIES
    out = base + [('story: ' + fn.__name__, lambda fn=fn, i=i: fn(seed + 100 * i))
                  for i, fn in enumerate(stories)]
    if not simple:
        out += composed(seed)
    return out


def story_before_last(seed):
    """Untaught transfer: find that person's penultimate movement, rather than their latest location."""
    def make(r):
        sentences, who = TS._where_story(r, n_min=5, n_max=10)
        theirs = [s for s in sentences if s[0] == who]
        return sentences, ['where', 'was', who, 'before', 'the', 'last', 'move'], theirs[-2][-1]
    return TS.Story('where before last', make, seed, words=())


def phase_builders(seed, phase):
    fresh_seed = seed + PHASES.index(phase) * 100_000
    if phase == 'test3':
        return BASE.alone(fresh_seed) + [
            ('story: ' + fn.__name__, lambda fn=fn, i=i: fn(fresh_seed + 100 * i))
            for i, fn in enumerate((TS.lesson_where_first, story_before_last, TS.lesson_what_is_alone))]
    return lesson_builders(fresh_seed, simple=phase == 'test1')


def strip_teacher(task):
    """Remove channels, including the story tasks' precomputed demonstrations, before independent work."""
    task.words = []
    if hasattr(task, '_worked_values'):
        task._worked_values = None
    for name in ('_worked', '_worked_of'):
        if hasattr(task, name):
            setattr(task, name, {})
    return task


def refresh_numbers(task, seed):
    # The old number builder ignores seed and always shows 1,2,3,4. Fresh seeds alone are NOT fresh instances.
    if type(task) is TS.Exact and task.inputs == {'n': 'num'}:
        rng = np.random.default_rng([seed, 271])
        xs = [int(x) for x in rng.permutation(16)]
        task.data = [(x, task._y(x)) for x in xs[:4]]
        task.pool = xs[4:]
        task._probe_inputs = xs


def input_digest(task):
    """Only the actual inputs, including a rail's readings and a book's passage; no name, seed or target."""
    if task.form == 'strengths':
        return ONE.truth.digest(task.throws)
    def readable(x):
        if task.subject == 'language':
            return [TS.text(s) for s in x]
        return LG.freeze(x)
    examples = sorted((readable(x) for x, _ in task.data), key=repr)
    pool = sorted((readable(x) for x in task.pool), key=repr)
    passage = [TS.text(s) for s in task.reading()] if hasattr(task, 'reading') else []
    data = (task.form, sorted(task.inputs.items()), examples, pool, passage)
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()


def make_plan(seed):
    """Keep only names/builders/digests, rather than retaining all rail worlds in RAM. Refuse input reuse."""
    plan, seen = {}, {}
    for phase in PHASES:
        rows = []
        for i, (name, builder) in enumerate(phase_builders(seed, phase)):
            task = builder()
            number_seed = seed + PHASES.index(phase) * 100_000 + i
            refresh_numbers(task, number_seed)
            digest = input_digest(task)
            while digest in seen and type(task) is TS.Exact and task.inputs == {'n': 'num'}:
                number_seed += 1_000_000
                refresh_numbers(task, number_seed)
                digest = input_digest(task)
            assert digest not in seen, f'course instance reused: {phase}/{name} and {seen.get(digest)}'
            seen[digest] = (phase, name)
            rows.append(dict(id=f'{phase}-{i:03d}', name=name, digest=digest, builder=builder,
                             number_seed=number_seed))
        plan[phase] = rows
    return plan


def materialize(row, phase):
    task = row['builder']()
    refresh_numbers(task, row['number_seed'])
    assert input_digest(task) == row['digest'], 'non-deterministic course instance'
    task.course_lesson = phase == 'lesson'
    if phase != 'lesson':
        strip_teacher(task)
    elif getattr(task, 'course_composed', False):
        if not CR.on('course_worked_steps'):
            task._worked_values = None
    elif type(task) is TS.Exact:
        task._worked_values = lambda x: (task._y(x),)
    return task


def isolated_grade(task, law, concepts, proven, seed):
    """The observer/book's calculation, detached from the mind, traces, task caches, and symbol vocabulary."""
    if law is None:
        return False
    vocab, words, next_word = dict(TS.VOCAB), dict(TS.WORDS), TS._NEXT[0]
    try:
        observer = copy.deepcopy(task)
        if isinstance(observer, TS.Story):
            # deepcopy does not rebind the Story constructor's lambda (it closes over the ORIGINAL self).
            observer._fresh = lambda rng: observer._make(rng)[0]
        if task.form == 'strengths':
            if proven is None:
                return False  # no certified physical answer to grade
            g = observer.grade(proven['cert'], True, n_throws=proven.get('n'))
        else:
            g = observer.grade(law, copy.deepcopy(concepts), proven is not None, seed=seed)
        return g['verdict'] in ('proven right', 'right, unsure')
    finally:
        TS.VOCAB.clear()
        TS.VOCAB.update(vocab)
        TS.WORDS.clear()
        TS.WORDS.update(words)
        TS._NEXT[0] = next_word


def correction(task, law, concepts, seed):
    """A teacher's answer and its worked values, shown ONLY after test1's first reply."""
    if task.form == 'strengths':
        # Rail proofs are curves/functions, not Exact inputs; there is no compatible worked-value seam.
        task.words = list(TK.teacher_tokens(task.hidden, task.signs, np.random.default_rng([seed, 927])))
        return dict(answer=ONE.grammar.name(task.hidden), words=list(task.words), steps=None)
    x = task.data[0][0]
    if law is not None:
        rng = np.random.default_rng([seed, 929])
        for _ in range(100):
            candidate = task._fresh(rng)
            if task._value(law, candidate, concepts) != task._y(candidate):
                x = candidate
                break
    y = task._y(x)
    task.data.append((x, y))
    if isinstance(task, TS.Story):
        # Test1's positional stories are single-step: only values, including the shown correct answer.
        task._worked = {LG.freeze(value): (task._y(value),) for value in task._probe_inputs}
        task._worked[LG.freeze(x)] = (y,)
        steps = (y,)
    else:
        steps = (y,)  # single-step items: the step's value is the answer
        task._worked_values = lambda value: (task._y(value),)
    return dict(input=x, answer=y, steps=steps)


def restore_observations(task, unit):
    if task.form == 'exact':
        task.data = [(LG.freeze(x), LG.freeze(y)) for x, y in unit['observations']]
    c = unit.get('correction')
    if c and task.form == 'strengths':
        task.words = list(c['words'])
    elif c and not isinstance(task, TS.Story):
        task._worked_values = lambda x: (task._y(x),)
    elif c:
        task._worked = {LG.freeze(x): (task._y(x),) for x in task._probe_inputs}
        task._worked[LG.freeze(c['input'])] = (LG.freeze(c['answer']),)


def live(sera, task, phase, deadline, seed, corrected=False):
    """Call the same Sera.live engine. The optional answer channel precedes proof credit.

    test3's channel always returns None; the hidden grade is computed only AFTER live returns.
    Study returns only its own book success/fail. Test2 returns only a teacher success/fail, never a correction.
    """
    captured = {}
    def channel(t, law, concepts, proven):
        captured.update(law=law, concepts=concepts, proven=proven)
        abstained = law is None or (t.form == 'strengths' and proven is None) or (
                                    phase == 'test2' and CR.on('course_told_wrong')
                                    and not sera.course_reliable(t))
        captured['abstained'] = abstained
        if phase == 'test3':
            return None
        if abstained:
            return dict(right=None)
        right = isolated_grade(t, law, concepts, proven, seed)
        captured['right'] = right
        return dict(right=right, source='book' if phase == 'study' else 'teacher',
                    reliability=(phase in ('lesson', 'test1') or
                                 (phase == 'test2' and CR.on('course_told_wrong'))))
    old_wall = ONE.MAX_WALL
    try:
        ONE.MAX_WALL = max(0.001, deadline - time.time())
        rec = sera.live(task, teaching=phase == 'lesson' or corrected, answer_channel=channel)
    finally:
        ONE.MAX_WALL = old_wall
    abstained = captured['abstained']
    right = (isolated_grade(task, captured['law'], captured['concepts'], captured['proven'], seed)
             if phase == 'test3' and not abstained else captured.get('right', False))
    status = 'abstained' if abstained else ('right' if right else 'wrong')
    u = BASE.unit_of(rec)
    u['settings'] = dict(CR.settings(include_course=True), one_field=ONE.ONE_FIELD)
    u.update(phase=phase, status=status, observer_right=bool(right),
             feedback=None if phase == 'test3' or abstained else
             dict(verdict='right' if right else 'wrong', source='book' if phase == 'study' else 'teacher'),
             response="I don't know" if abstained else (rec.get('claim') or LG.show(captured['law'])),
             observations=list(task.data) if task.form == 'exact' else None)
    if phase == 'test1' and not corrected and status != 'right':
        u['correction'] = correction(task, captured['law'], captured['concepts'], seed)
        # The correction is one of the observations needed on a resumed retry.
        u['observations'] = list(task.data) if task.form == 'exact' else None
    return u


def json_safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, dict):
        return {k: json_safe(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_safe(v) for v in value]
    return value


def write_json(path, value):
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(json_safe(value), indent=1, default=str, allow_nan=False), encoding='utf-8')
    os.replace(tmp, path)


def attempt_units(out, progress):
    units = {}
    for uid in progress['committed']:
        path = out / 'units' / (uid + '.json')
        if not path.exists():
            raise ValueError(f'checkpoint is missing its committed unit: {path}')
        u = json.loads(path.read_text(encoding='utf-8'))
        units.setdefault(u['item_id'], []).append(u)
    return units


def report(out, plan, progress, settings):
    units = attempt_units(out, progress)
    phases = {}
    for phase in PHASES:
        items = []
        for row in plan[phase]:
            attempts = units.get(row['id'], [])
            items.append(dict(id=row['id'], name=row['name'], input_digest=row['digest'],
                              status=attempts[-1]['status'] if attempts else 'not reached',
                              attempts=len(attempts), wall=sum(u['attempt_wall'] for u in attempts),
                              results=[dict(status=u['status'], unit=f"units/{u['unit_id']}.json")
                                       for u in attempts]))
        counts = {s: sum(r['status'] == s for r in items) for s in STATUSES}
        phases[phase] = dict(items=items, counts=counts, attempts=sum(r['attempts'] for r in items),
                             wall=progress['spent'][phase], budget=progress['budgets'][phase],
                             field_size=progress['phase_fields'].get(phase),
                             finished=phase in progress['finished'])
    result = json_safe(dict(schema_version=1, seed=progress['seed'], settings=settings, phases=phases,
                            dictionary=dict(path=progress['identity']['book'], loaded=TK.BOOK is not None)))
    write_json(out / 'COURSE.json', result)
    return result


def run(out, seed=1, hours=6, phase='all', retries=2, shares=SHARES, book=None, plan=None, clock=time.time):
    """Checkpoint after every attempt. A unit written before a failed checkpoint is ignored on resume."""
    out = Path(out)
    (out / 'units').mkdir(parents=True, exist_ok=True)
    ck = out / 'field.pkl'
    field = PH.Field.load(ck) if ck.exists() else PH.Field(seed)
    sera = ONE.Sera(seed, field)
    book = book or os.environ.get('SERA_BOOK')
    TK.BOOK = DICT.load(book)
    if book and TK.BOOK is None:
        raise ValueError(f'dictionary is not readable: {book}')
    settings = dict(CR.settings(include_course=True), one_field=ONE.ONE_FIELD)
    identity = dict(seed=seed, hours=hours, retries=retries, shares=list(shares), book=str(book) if book else None,
                    crutches=settings['crutches_effective'], one_field=ONE.ONE_FIELD,
                    knobs=settings['knobs'], effective=settings['effective'])
    progress = getattr(field, 'course_progress', None)
    if progress is None:
        if ck.exists():
            raise ValueError('field.pkl is not a course checkpoint; use a new output directory')
        progress = dict(seed=seed, identity=identity, committed=[], spent={p: 0.0 for p in PHASES},
                        budgets={p: hours * 3600 * s / sum(shares) for p, s in zip(PHASES, shares)},
                        phase_fields={}, finished=[])
        field.course_progress = progress  # input/cursor/time metadata ONLY; no observer grades
    elif progress['identity'] != identity:
        raise ValueError('resume configuration differs; use the same seed, hours, retries, shares, book and switches')
    plan = make_plan(seed) if plan is None else plan  # load vocabulary before building ANY story worlds
    signature = {p: [(r['id'], r['digest']) for r in plan[p]] for p in PHASES}
    if progress.get('inputs', signature) != signature:
        raise ValueError('resume input digests differ')
    progress['inputs'] = signature
    field.save(ck)
    selected = PHASES if phase == 'all' else (phase,)
    with open(out / 'events.jsonl', 'a', encoding='utf-8') as events:
        def event(**e):
            events.write(json.dumps(dict(e, t=clock())) + '\n')
            events.flush()
        for p in selected:
            if p in progress['finished']:
                continue
            deadline = clock() + max(0.0, progress['budgets'][p] - progress['spent'][p])
            phase_start, phase_spent = clock(), progress['spent'][p]
            prior = attempt_units(out, progress)
            event(kind='phase', phase=p)
            for row in plan[p]:
                attempts = prior.get(row['id'], [])
                limit = 2 if p == 'test1' else (1 + retries if p == 'test2' else 1)
                if len(attempts) >= limit or (attempts and attempts[-1]['status'] != 'wrong'
                                            and not (p == 'test1' and attempts[-1]['status'] == 'abstained')):
                    continue
                if clock() >= deadline:
                    break
                t0 = clock()
                task = materialize(row, p)
                if attempts:
                    restore_observations(task, attempts[-1])
                remaining_items = sum(not prior.get(r['id']) for r in plan[p]) + int(bool(attempts))
                item_end = min(deadline, clock() + (deadline - clock()) / max(1, remaining_items))
                for a in range(len(attempts), limit):
                    if clock() >= item_end:
                        break
                    end = min(item_end, clock() + (item_end - clock()) / (limit - a))
                    u = live(sera, task, p, end, seed, corrected=p == 'test1' and a > 0)
                    uid = f"{row['id']}-a{a + 1}"
                    elapsed = max(0.0, clock() - t0)
                    u.update(item_id=row['id'], unit_id=uid, input_digest=row['digest'], attempt=a + 1,
                             attempt_wall=elapsed, field_size=field.account())
                    write_json(out / 'units' / (uid + '.json'), u)
                    progress['committed'].append(uid)
                    progress['spent'][p] = phase_spent + max(0.0, clock() - phase_start)
                    field.save(ck)  # the commit point: all learning and the attempt cursor move together
                    event(kind='attempt', phase=p, item=row['id'], attempt=a + 1, status=u['status'], wall=elapsed)
                    attempts.append(u)
                    prior[row['id']] = attempts
                    report(out, plan, progress, settings)
                    t0 = clock()
                    if u['status'] == 'right' or (u['status'] == 'abstained' and p != 'test1'):
                        break
            progress['spent'][p] = phase_spent + max(0.0, clock() - phase_start)
            progress['phase_fields'][p] = field.account()
            progress['finished'].append(p)
            field.save(ck)
            event(kind='phase_done', phase=p, wall=progress['spent'][p])
        result = report(out, plan, progress, settings)
    print('COURSE DONE', json.dumps({p: result['phases'][p]['counts'] for p in PHASES}), flush=True)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seed', type=int, default=1)
    ap.add_argument('--hours', type=float, default=6)
    ap.add_argument('--out', required=True)
    ap.add_argument('--book', default=None)
    ap.add_argument('--phase', choices=PHASES + ('all',), default='all')
    ap.add_argument('--retries', type=int, default=2)
    ap.add_argument('--shares', default=','.join(map(str, SHARES)), help='lesson,study,test1,test2,test3 time weights')
    a = ap.parse_args()
    shares = tuple(float(s) for s in a.shares.split(','))
    if len(shares) != 5 or any(not math.isfinite(s) or s <= 0 for s in shares):
        ap.error('--shares needs five finite positive weights')
    if not math.isfinite(a.hours) or a.hours <= 0 or a.retries < 0 or a.seed < 0:
        ap.error('--hours must be finite and positive; --seed and --retries must be nonnegative')
    run(a.out, a.seed, a.hours, a.phase, a.retries, shares, a.book)


if __name__ == '__main__':
    main()
