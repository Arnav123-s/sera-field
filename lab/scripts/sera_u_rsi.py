"""S28's bounded, frozen four-arm pilot. All verdicts come from saved records."""
import argparse
import copy
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import threading
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('CCOPS5_SHAPES', 'library')
os.environ.setdefault('CCOPS5_CLAIM', 'functional')
os.environ.setdefault('CCOPS5_BAND', 'claim')

import numpy as np
import torch

from sera import lang as LG, tasks as TS, one as ONE
from sera_u import SeraU
from sera_u.mind import ARMS, CURIOSITY_ARMS, U_CRUTCHES, U3_CRUTCHES, U6_CRUTCHES, arm_settings, code_identity, source_identity
from sera_u.ports import TaskView, PortBudget, digest
from sera_u.sleep import Receipt, expand, family, independent, sample_input, substitute


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(path.name+'.pending')
    with pending.open('w', encoding='utf-8') as fh:
        json.dump(value, fh, sort_keys=True, indent=2, default=str, allow_nan=False)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(pending, path)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def commit(out, state, mind, checkpoint):
    # Observer grades/timings stay in state.json, never in an entity checkpoint.
    mind.progress['runner'] = {k: state[k] for k in ('stage', 'bootstrap_index', 'arm_index', 'active_arm',
                              'generation', 'phase', 'unit_index', 'deadline') if k in state}
    mind.progress['protocol_digest'] = digest(state['protocol'])
    if hasattr(mind.field, 'curiosity'):
        state.setdefault('curiosity', {})[mind.arm] = mind.field.curiosity.report()
    state['checkpoint'] = checkpoint
    state['checkpoint_sha256'] = mind.save(out/checkpoint)
    write(out/'state.json', state)


def recover(out, state):
    path = out/state['checkpoint']
    if hashlib.sha256(path.read_bytes()).hexdigest() != state['checkpoint_sha256']:
        raise ValueError('Stale/corrupt runner checkpoint')
    return SeraU.load(path)


def timed_preflight(device, seed, out, *, deadline=math.inf, engineering=True, laptop=False, batched_reads=True):
    start = time.perf_counter()
    if device == 'cuda' and not torch.cuda.is_available():
        raise ValueError('Requested GPU is unavailable')
    engineering_result = None
    if engineering:
        proc = subprocess.run([sys.executable, '-m', 'pytest', 'tests/sera_u', '-q'], cwd=ROOT,
                              # The gate tests the code under its standard settings: a pilot case's ablation
                              # switches (memory off, U3/U6 on/off, ...) must not change the tests' default
                              # schemas; U3's and U6's own contracts enable their explicit entity masks.
                              env={**os.environ, 'PYTHONHASHSEED': '0', 'SERA_CRUTCH_ON': '',
                                   'SERA_CRUTCH_OFF': 'lesson_words' if 'lesson_words' in
                                   os.environ.get('SERA_CRUTCH_OFF', '').split(',') else ''},
                              capture_output=True, text=True,
                              timeout=max(1., min(1440., deadline-time.time())))
        engineering_result = dict(returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)
        write(out/'engineering.json', engineering_result)
        if proc.returncode:
            raise ValueError('Engineering tests failed; see engineering.json')
    mind = SeraU(seed, device=device, batched_reads=batched_reads)
    view = TaskView((('x', 'num'),), 'num', tuple((((('x', x),)), x+1) for x in (-2, 0, 1, 4)),
                    queries=tuple((('x', x),) for x in range(-8, 12)))
    list_inputs = ((), tuple(range(8)), tuple(range(-8, 0)), (2, -2, 0, 3))
    list_view = TaskView((('x', 'list'),), 'list',
                         tuple((((('x', x),)), tuple(reversed(x))) for x in list_inputs),
                         queries=tuple((('x', list_inputs[j % 4]),) for j in range(20)))
    # Targets here are explicit derivative/latency fixtures, never RSI teaching evidence.
    target = LG.node('add', LG.node('var', payload='x'), LG.node('one'))
    from sera_u.sleep import program_log_probability
    with mind.scope():
        loss = -program_log_probability(mind.proposer, view, (target,), {})
        mind.optimizer.zero_grad(set_to_none=True)
        loss.backward()
    groups = {}
    for name in ('words.weight', 'core.links', 'production_query.weight'):
        parameter = dict(mind.owner.named_parameters())[name]
        groups[name] = None if parameter.grad is None else float(parameter.grad.norm())
    if any(v is None or not math.isfinite(v) or v <= 0 for v in groups.values()):
        raise ValueError('Input/core/readout derivative preflight failed')
    times = []
    with torch.no_grad():
        for j in range(12):
            if time.time() >= deadline:
                raise TimeoutError('Preflight exceeded budget')
            if device == 'cuda':
                torch.cuda.synchronize()
            t = time.perf_counter()
            mind.owner.task_features(view if j % 2 == 0 else list_view)
            if device == 'cuda':
                torch.cuda.synchronize()
            times.append(time.perf_counter()-t)
    # Measure one real checked batch and exact next-update resume on the declared device.
    fixture = Receipt.make(view, (target,), {}, scope='exact-audit', origin='taught', source='preflight-fixture')
    mind.checked_wake.add(fixture.id)
    mind.sleep.admit(fixture, {})
    t = time.perf_counter()
    mind.train(1, 8)
    if device == 'cuda':
        torch.cuda.synchronize()
    batch_seconds = time.perf_counter()-t
    snapshot = mind.dumps()
    mind.train(1, 8)
    reference = mind.learning_hash()
    restarted = SeraU.loads(snapshot)
    restarted.train(1, 8)
    exact = all(torch.equal(p, dict(restarted.owner.named_parameters())[name])
                for name, p in mind.owner.named_parameters())
    # Training wall logs differ; compare actual weights/optimizer/RNGs in tests,
    # and record the fixture's owner restart result here.
    if not exact:
        raise ValueError('Device exact next-update restart failed')
    count = sum(p.numel() for p in mind.owner.parameters())
    result = dict(device=device, batched_reads=batched_reads, parameters=count, median=statistics.median(times),
                  p95=float(np.quantile(times, .95)), peak_process_mb=ONE._peak_mb(),
                  gpu_peak_bytes=torch.cuda.max_memory_allocated() if device == 'cuda' else 0,
                  gradient=groups, batch_seconds=batch_seconds, exact_resume=exact,
                  owner_reference_hash=reference, source=mind.source, code=mind.code,
                  runtime=dict(machine=platform.platform(), processor=platform.processor(),
                               threads=torch.get_num_threads(), torch=torch.__version__, numpy=np.__version__),
                  engineering=bool(engineering_result and engineering_result['returncode'] == 0),
                  common_batches=max(1, min(120, int(5400/max(batch_seconds, .001)/16))),
                  wall=time.perf_counter()-start,
                  laptop_latency_certified=bool(laptop and device == 'cpu' and statistics.median(times) <= .5
                                                and float(np.quantile(times, .95)) <= 1.
                                                and ONE._peak_mb() is not None and ONE._peak_mb() <= 2048.),
                  latency_inputs='balanced number/list, four examples, twenty query/probe records, lists through length eight')
    write(out/'preflight.json', result)
    return result


class Distribution:
    def __init__(self, typ):
        self.typ = typ

    def __call__(self, rng):
        def value(typ):
            if LG.is_list(typ):
                return tuple(value(LG.elem(typ)) for _ in range(int(rng.integers(0, 9))))
            if typ == 'num':
                return int(rng.integers(-8, 9))
            if typ == 'bool':
                return bool(rng.integers(0, 2))
            if typ == 'real':
                return float(rng.uniform(-4, 4))
            raise ValueError('Outside pilot input grammar')
        return value(self.typ)


UNDEFINED = ('Bounded non-boolean number required', 'Bounded list required', 'Finite real required',
             'Independent executor step budget', 'Range bound')


class Target:
    """Observer/world-owned program. Never passed to the Field or replay."""
    def __init__(self, ast):
        self.ast = LG.freeze(ast)

    def __call__(self, x):
        try:
            return independent(self.ast, {'x': x}, {})
        except ValueError as exc:
            # Outside the interpreter's bounds the world's value is undefined, as LG.safe's None is for the lab's own
            # executor; any other interpreter error is a real fault and still raises.
            if str(exc) not in UNDEFINED:
                raise
            return None


def build_task(spec):
    return TS.Exact('code' if LG.is_list(spec['tin']) else 'math', spec['name'], Target(spec['program']),
                    {'x': spec['tin']}, spec['tout'], LG.freeze(spec['examples']), LG.freeze(spec['pool']),
                    Distribution(spec['tin']))


def seed_programs(mind):
    programs = {}
    for receipt, concepts in mind.sleep.replay:
        var, tin = receipt.view.inputs[0]
        for p in receipt.targets:
            p = substitute(expand(p, concepts), var, LG.node('var', payload='x'))
            key = family(p, {})
            programs.setdefault(key, (p, tin, receipt.view.out, receipt.source))
    return [programs[k] for k in sorted(programs)]


BOOT_WALL, REVISIT_WALL = 1440, 1440    # seconds: the lessons in course order; revisits of lessons not yet proven


def seed_gate(seeds):
    return len(seeds) >= 8 and len({s[3] for s in seeds}) >= 4


def teach_bootstrap(base, lessons, state, save):
    """Teach the bootstrap lessons; `save(n)` commits the n-th unit. The caller checks the seed gate."""
    # Lessons in course order, then "not yet": a lesson it has not yet proven comes back after the others
    # have taught more, while the seed gate is unmet and the revisit allocation (from the reserve) lasts.
    schedule = state.setdefault('bootstrap_schedule', list(range(len(lessons))))
    proven = state.setdefault('bootstrap_proven', {})
    while True:
        spent = sum(c['wall'] for c in state['costs'] if c['phase'] == 'bootstrap')
        if state['bootstrap_index'] >= len(schedule):
            later = [i for i in range(len(lessons)) if not proven.get(lessons[i][0])]
            if seed_gate(seed_programs(base)) or not later or spent >= BOOT_WALL+REVISIT_WALL:
                break
            schedule += later
            state['bootstrap_revisits'] = state.get('bootstrap_revisits', 0)+1
            continue
        position = state['bootstrap_index']
        index = schedule[position]
        if position < len(lessons) and spent >= BOOT_WALL:       # the course order has its own allocation
            raise ValueError('Bootstrap time allocation exhausted')
        if position >= len(lessons) and spent >= BOOT_WALL+REVISIT_WALL:
            state['bootstrap_index'] = len(schedule)
            continue
        name, builder = lessons[index]
        task = builder()
        # Exactly four public examples. The additional observed value is
        # supplied by the authorized teaching world, never a solution AST.
        if len(task.data) < 4:
            x = task.pool[0]
            task.data.append((x, task._y(x)))
        start = time.perf_counter()
        proven[name] = False
        try:
            record = base.live(task, teaching=True, task_wall=min(120., max(.01, state['deadline']-time.time())))
            if record.get('verdict') == 'SURE AND WRONG':
                raise ValueError('Bootstrap tripwire: sure and wrong')
            proven[name] = bool(record.get('proven'))
        except PortBudget as exc:
            state.setdefault('bootstrap_failures', []).append(dict(task=name, reason=str(exc)))
        state['bootstrap_index'] = position+1
        state['costs'].append(dict(phase='bootstrap', task=name, wall=time.perf_counter()-start,
                                   **({'revisit': True} if position >= len(lessons) else {})))
        save(position+1)


def freeze_suite(mind, seed, *, eval_tasks=48, wake_tasks=16):
    seeds = seed_programs(mind)
    if not seed_gate(seeds):
        raise ValueError('Bootstrap failed: need eight distinct accepted programs from four source families')
    rng = np.random.default_rng([seed, 610])
    private, seen = {'num': [], 'list': []}, {family(p, {}) for p, _, _, _ in seeds}
    # Templates are selected mechanically from checked acquired vocabulary.
    # No domain AST/program is installed in SERA; these remain world generators.
    for length in (2, 3, 4):
        for indices in itertools.product(range(len(seeds)), repeat=length):
            chain = [seeds[j] for j in indices]
            if any(a[2] != b[1] for a, b in zip(chain, chain[1:])):
                continue
            tin, tout = chain[0][1], chain[-1][2]
            domain = 'list' if LG.is_list(tin) else 'num'
            if tin not in ('num', 'list') or tout not in ('num', 'list'):
                continue
            p = chain[0][0]
            for q, _, _, _ in chain[1:]:
                p = substitute(q, 'x', p)
            fam = family(p, {})
            if fam in seen or LG.size(p) > 40:
                continue
            distribution = Distribution(tin)
            xs = tuple(distribution(rng) for _ in range(20))
            try:
                ys = tuple(independent(p, {'x': x}, {}) for x in xs)
                if any(LG.safe(p, {'x': x}, {}) != y for x, y in zip(xs, ys)):
                    continue
            except (ValueError, KeyError, *LG.BAD):
                continue
            if len(set(map(repr, ys))) < 2 or ys == xs or any(isinstance(y, tuple) and len(y) > 8 for y in ys):
                continue
            seen.add(fam)
            private[domain].append(dict(program=p, tin=tin, tout=tout, family=fam, source=digest(indices),
                                        examples=xs[:4], pool=xs[4:], length=length))
            if all(len(private[d]) >= eval_tasks//2+wake_tasks//2 for d in private):
                break
        if all(len(private[d]) >= eval_tasks//2+wake_tasks//2 for d in private):
            break
    required = eval_tasks//2+wake_tasks//2
    if any(len(private[d]) < required for d in private):
        raise ValueError('Insufficient diverse number/list composition families after reservation')
    assessment, wake = [], []
    for domain in ('num', 'list'):
        order = rng.permutation(len(private[domain]))
        rows = [private[domain][int(j)] for j in order]
        assessment += rows[:eval_tasks//2]
        wake += rows[eval_tasks//2:required]
    for prefix, rows in (('h', assessment), ('w', wake)):
        for j, row in enumerate(rows):
            row['name'] = prefix+str(j)          # opaque observer IDs, never target-derived names
    retention = []
    for j, (p, tin, tout, source) in enumerate(seeds):
        xs = tuple(Distribution(tin)(rng) for _ in range(20))
        retention.append(dict(name='r'+str(j), program=p, tin=tin, tout=tout, family=family(p, {}),
                              source=source, examples=xs[:4], pool=xs[4:], length=1))
    return dict(assessment=assessment, wake=wake, retention=retention,
                reserved=sorted(r['family'] for r in assessment), seed_count=len(seeds),
                split='expanded structural template and acquired source group; overlap may remain behavioral')


def validate_frozen_suite(suite):
    """Observer-side integrity check; no private generator is sent to a learner."""
    if (len(suite['assessment']) != 48 or len(suite['wake']) != 16 or not suite['retention']
            or suite['seed_count'] < 8):
        raise ValueError('Frozen U1 suite requires 48/16 tasks, retention and eight seeds')
    for label, expected in (('assessment', 24), ('wake', 8)):
        rows = suite[label]
        if any(sum(row['tin'] == typ for row in rows) != expected for typ in ('num', 'list')):
            raise ValueError('Frozen suite domain balance changed')
        if len({r['name'] for r in rows}) != len(rows) or len({r['family'] for r in rows}) != len(rows):
            raise ValueError('Frozen suite repeats names or expanded templates')
    if {r['family'] for r in suite['assessment']} & {r['family'] for r in suite['wake']+suite['retention']}:
        raise ValueError('Frozen assessment overlaps wake/retention families')
    if set(suite['reserved']) != {r['family'] for r in suite['assessment']}:
        raise ValueError('Frozen suite reservation changed')
    for row in suite['assessment']+suite['wake']+suite['retention']:
        p = LG.freeze(row['program'])
        if family(p, {}) != row['family'] or len(row['examples']) != 4:
            raise ValueError('Frozen suite program identity/examples changed')
        sig = LG.infer(p, {}, arg='x')
        if LG.size(p) > 40 or sig is None or not LG.fits(sig, row['tin'], row['tout']):
            raise ValueError('Frozen suite program is outside the pilot grammar')
        TaskView.from_task(build_task(row)).records()
    return suite

def report(out):
    out = Path(out)
    state = read(out/'state.json')
    rows = state.get('rows', [])
    arms = tuple(state['protocol'].get('arms', ARMS))
    curves, retention, groups = {}, {}, {}
    n = state['protocol']['eval_tasks']
    generations = state['protocol']['generations']
    complete = state.get('stage') == 'complete'
    for arm in arms:
        curves[arm], retention[arm] = [], []
        for generation in range(generations+1):
            selected = [r for r in rows if r['arm'] == arm and r['generation'] == generation and r['suite'] == 'assessment']
            kept = [r for r in rows if r['arm'] == arm and r['generation'] == generation and r['suite'] == 'retention']
            ok = len(selected) == n and len({r['task'] for r in selected}) == n
            complete = complete and ok and len(kept) == state.get('retention_count', 0)
            curves[arm].append(dict(generation=generation, solved=sum(r['solved'] for r in selected),
                                    N=n, g=sum(r['solved'] for r in selected)/n, rows=len(selected), complete=ok))
            retention[arm].append(sum(r['solved'] for r in kept)/len(kept) if kept else None)
            for domain in ('num', 'list'):
                domain_rows = [r for r in selected if r['domain'] == domain]
                groups[arm+':'+str(generation)+':'+domain] = sum(r['solved'] for r in domain_rows)/(n//2)
    full = [r['solved'] for r in curves[arms[0]]]
    behavioral = bool(complete and generations == 3 and all(a < b for a, b in zip(full, full[1:])) and full[3]-full[0] >= 5)
    for arm in arms[1:]:
        values = [r['solved'] for r in curves[arm]]
        behavioral = behavioral and full[-1]-values[-1] >= 3 and full[-1]-full[0] > values[-1]-values[0]
    common = None
    for arm in arms:
        solved = {r['task'] for r in rows if r['arm'] == arm and r['generation'] == 0
                  and r['suite'] == 'assessment' and r['solved']}
        common = solved if common is None else common & solved
    speed_ratios = {}
    for arm in arms:
        baseline = [r['search'] for r in rows if r['arm'] == arm and r['generation'] == 0 and r['task'] in common]
        final = [r['search'] for r in rows if r['arm'] == arm and r['generation'] == 3 and r['task'] in common and r['solved']]
        speed_ratios[arm] = (statistics.median(final)/statistics.median(baseline)
                             if baseline and len(final) == len(common) and statistics.median(baseline) > 0 else None)
    speed = speed_ratios.get(arms[0]) is not None and speed_ratios[arms[0]] <= .8
    retain = all(values[0] is not None and values[-1] is not None and values[0]-values[-1] <= .05
                 for values in retention.values())
    wrong = any(r.get('grade', {}).get('verdict') == 'SURE AND WRONG' for r in rows)
    laptop = state.get('laptop_preflight', {})
    hardware_ok = bool(laptop.get('laptop_latency_certified') and laptop.get('parameters', 1_200_001) <= 1_200_000
                       and laptop.get('source') == state['protocol'].get('source'))
    engineering_ok = bool(state.get('preflight', {}).get('engineering') and state.get('preflight', {}).get('exact_resume'))
    bootstrap_ok = bool(state.get('bootstrap', {}).get('success'))
    result = dict(schema='s28-pilot-1', curves=curves, domain_g=groups, retention=retention,
                  complete=bool(complete), missing_rows=len(arms)*(generations+1)*n-sum(r['suite'] == 'assessment' for r in rows),
                  common_g0=sorted(common or ()), search_ratios=speed_ratios,
                  behavioral_signal=bool(behavioral and speed and retain and not wrong),
                  engineering=state.get('preflight', {}), bootstrap=state.get('bootstrap'),
                  hardware_gate='passed supplied laptop measurement' if hardware_ok else 'pending actual laptop measurement',
                  pilot_pass=bool(complete and behavioral and speed and retain and not wrong and hardware_ok
                                  and engineering_ok and bootstrap_ok),
                  costs=state.get('costs', []), failure=state.get('failure'),
                  checkpoints=state.get('checkpoints', {}),
                  assessment_wall=sum(r['wall'] for r in rows if 'wall' in r),
                  assessment_load_wall=sum(r.get('load_wall', 0.) for r in rows),
                  search_seconds_per_solved={arm: (sum(r['search'] for r in rows if r['arm'] == arm and
                        r['suite'] == 'assessment')/sum(r['solved'] for r in rows if r['arm'] == arm and
                        r['suite'] == 'assessment')) if any(r['solved'] for r in rows if r['arm'] == arm and
                        r['suite'] == 'assessment') else None for arm in arms},
                  failure_charged_mean={arm: (sum(r.get('wall', 0.) if r['solved'] else
                        state['protocol'].get('task_wall', 10.) for r in rows if r['arm'] == arm and
                        r['suite'] == 'assessment')+((generations+1)*n-sum(r['arm'] == arm and r['suite'] == 'assessment'
                        for r in rows))*state['protocol'].get('task_wall', 10.))/((generations+1)*n) for arm in arms},
                  total_wall=state.get('finished', state['deadline'] if 'deadline' in state else 0)-state.get('started', 0),
                  disclaimer='One-seed pilot only; no confirmatory RSI claim. Missing/timeout/abstention scores zero.')
    if arms == CURIOSITY_ARMS:
        result['schema'] = 'u6-pilot-1'
        result['curiosity'] = state.get('curiosity', {})
        result['time_to_learn'] = {}
        for arm in arms:
            seen = {}
            for row in rows:
                if row['arm'] == arm and row['suite'] == 'assessment' and row['solved']:
                    seen.setdefault(row['task'], dict(generation=row['generation'],
                                                     seconds=row.get('learning_seconds')))
            result['time_to_learn'][arm] = dict(first_solutions=seen, acquired=len(seen),
                                               censored=n-len(seen), N=n)
        result['gaps_found_later_solved'] = {
            arm: state.get('curiosity', {}).get(arm, {}).get('gaps_later_solved', 0) for arm in arms}
        result['previously_unsolved_later_solved'] = {}
        for arm in arms:
            failed = {r['task'] for r in rows if r['arm'] == arm and r['suite'] == 'assessment'
                      and r['generation'] == 0 and not r['solved']}
            later = {r['task'] for r in rows if r['arm'] == arm and r['suite'] == 'assessment'
                     and r['generation'] > 0 and r['solved']}
            result['previously_unsolved_later_solved'][arm] = len(failed & later)
        result['gap_metric_scope'] = 'own public cues with a located gap before acceptance, later outer acceptance; no held-out feedback'
    write(out/'g_curve.json', result)
    return result


def run(args):
    protocol_start = time.time()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    arms = tuple(args.arms.split(','))
    if arms not in (ARMS, CURIOSITY_ARMS):
        raise ValueError('Use the frozen four-arm pilot or the paired aimed,unaimed pilot')
    if arms == CURIOSITY_ARMS and any(not arm_settings('aimed')[k] or arm_settings('unaimed')[k] for k in U6_CRUTCHES):
        raise ValueError('Named aimed/unaimed A/B requires both U6 switches on/off; remove their environment overrides')
    protocol = dict(seed=args.seed, arms=list(arms), generations=args.generations, task_wall=args.task_wall,
                    eval_tasks=args.eval_tasks, wake_tasks=args.wake_tasks, hours=args.hours, device=args.device,
                    source=source_identity(), code=code_identity(), threads=1, batched_reads=not args.no_batched_reads,
                    reading_digest=digest([]), teaching='existing sera_one list/number value-only lessons',
                    crutches={arm: arm_settings(arm) for arm in arms}, judge='unchanged Exact audit; observer-only wrapper',
                    budgets=dict(preflight=1440, bootstrap=BOOT_WALL, bootstrap_revisits=REVISIT_WALL, dreams=1440,
                                 wakes=2160, train=5400, assessments=7920, reserve=1800-REVISIT_WALL))
    frozen_path = getattr(args, 'frozen_suite', None)
    if arms == CURIOSITY_ARMS and frozen_path is None:
        raise ValueError('Paired U6 A/B requires --frozen-suite pointing to the saved U1 observer.json')
    frozen_bytes = Path(frozen_path).read_bytes() if frozen_path else None
    if frozen_bytes is not None:
        if arms != CURIOSITY_ARMS:
            raise ValueError('--frozen-suite is for the paired U6 A/B')
        validate_frozen_suite(json.loads(frozen_bytes))
        protocol['frozen_suite_sha256'] = hashlib.sha256(frozen_bytes).hexdigest()
    laptop_record = read(args.laptop_preflight) if args.laptop_preflight else None
    protocol['laptop_preflight_digest'] = digest(laptop_record)
    if args.generations != 3 or args.eval_tasks != 48 or args.wake_tasks != 16:
        raise ValueError('The frozen pilot requires three generations and 48/16 tasks')
    if args.hours > 6 or args.hours <= 0:
        raise ValueError('Total pilot budget must be positive and at most six hours')
    if (out/'state.json').exists():
        state = read(out/'state.json')
        if state['protocol'] != protocol:
            raise ValueError('Frozen protocol changed; start a fresh experiment')
    else:
        state = dict(protocol=protocol, stage='preflight', deadline=(protocol_start if frozen_bytes is not None else time.time())+3600*args.hours,
                     rows=[], costs=[], checkpoints={}, bootstrap_index=0)
        state['started'] = protocol_start if frozen_bytes is not None else time.time()
        if frozen_bytes is not None:
            state['costs'].append(dict(phase='frozen-suite-validation', wall=time.time()-protocol_start))
        if laptop_record:
            state['laptop_preflight'] = laptop_record
        write(out/'protocol.json', protocol)
        write(out/'state.json', state)
    remaining = state['deadline']-time.time()
    if remaining <= 0:
        state['failure'] = 'Total deadline exhausted; continuation does not reset teaching or wall budget'
        write(out/'state.json', state)
        return report(out)
    def exhausted():
        write(out/'timeout.json', dict(deadline=state['deadline'], code=124,
                                      reason='hard six-hour process budget; last committed unit is resumable'))
        os._exit(124)
    watchdog = threading.Timer(remaining, exhausted)
    watchdog.daemon = True
    watchdog.start()
    try:
        if state['stage'] == 'preflight':
            state['preflight'] = timed_preflight(args.device, args.seed, out,
                                               deadline=min(state['deadline'], time.time()+1440), batched_reads=not args.no_batched_reads)
            state['costs'].append(dict(phase='preflight', wall=state['preflight']['wall']))
            state['stage'] = 'bootstrap'
            base = SeraU(args.seed, device=args.device, arm='unaimed' if arms == CURIOSITY_ARMS else 'full', batched_reads=not args.no_batched_reads)
            commit(out, state, base, 'bootstrap-0.pt')
        if state['stage'] == 'bootstrap':
            from scripts.sera_one import teaching
            lessons = [(name, builder) for name, builder in teaching(args.seed)
                       if name.startswith(('number:', 'list:'))]
            base = recover(out, state)
            teach_bootstrap(base, lessons, state, lambda n: commit(out, state, base, 'bootstrap-'+str(n)+'.pt'))
            if frozen_bytes is None:
                suite = freeze_suite(base, args.seed)
            else:
                suite = validate_frozen_suite(json.loads(frozen_bytes))
                seeds = seed_programs(base)
                if not seed_gate(seeds):
                    raise ValueError('U6 bootstrap failed the same eight-program/four-source gate')
                trained = {family(p, {}) for p, _, _, _ in seeds}
                if trained & set(suite['reserved']):
                    raise ValueError('Saved U1 assessment family overlaps current bootstrap; refusing contaminated A/B')
            state['bootstrap'] = dict(accepted_programs=suite['seed_count'], success=True)
            state['retention_count'] = len(suite['retention'])
            if frozen_bytes is None:
                write(out/'observer.json', suite)  # private generators, never loaded by the proposer
            else:
                (out/'observer.json').write_bytes(frozen_bytes)  # preserve exact U1 artifact bytes
            state['suite_sha256'] = hashlib.sha256((out/'observer.json').read_bytes()).hexdigest()
            state['base'] = state['checkpoint']
            state['base_sha256'] = state['checkpoint_sha256']
            state['stage'], state['arm_index'] = 'arms', 0
            write(out/'state.json', state)
        if state['stage'] == 'arms':
            if hashlib.sha256((out/'observer.json').read_bytes()).hexdigest() != state['suite_sha256']:
                raise ValueError('Frozen observer suite changed')
            suite = read(out/'observer.json')
            if hashlib.sha256((out/state['base']).read_bytes()).hexdigest() != state['base_sha256']:
                raise ValueError('Shared bootstrap checkpoint changed')
            cap = state['preflight']['common_batches']
            for arm_index in range(state['arm_index'], len(arms)):
                arm = arms[arm_index]
                if state.get('active_arm') != arm:
                    seed_mind = SeraU.load(out/state['base'])
                    mind = SeraU(args.seed, device=args.device, arm=arm, field=seed_mind.field, batched_reads=not args.no_batched_reads)
                    mind.owner.load_state_dict(seed_mind.owner.state_dict())
                    mind.optimizer.load_state_dict(seed_mind.optimizer.state_dict())
                    mind.owner.token_ids = copy.deepcopy(seed_mind.owner.token_ids)
                    mind.owner.production_ids = copy.deepcopy(seed_mind.owner.production_ids)
                    if arms == CURIOSITY_ARMS:
                        mind.owner.understanding_ids = copy.deepcopy(seed_mind.owner.understanding_ids)
                    mind.state = copy.deepcopy(seed_mind.state)
                    mind.proposer.retained = mind.state
                    mind.rngs = copy.deepcopy(seed_mind.rngs)
                    for receipt, concepts in seed_mind.sleep.replay:
                        targets = tuple(expand(p, concepts) for p in receipt.targets)
                        copied = Receipt.make(receipt.view, targets, {}, scope=receipt.scope,
                                              origin=receipt.origin, source=receipt.source)
                        mind.checked_wake.add(copied.id)
                        mind.sleep.admit(copied, {})
                    mind.sleep.reserved = set(suite['reserved'])
                    mind.sleep.reserved_sources = {r['source'] for r in suite['assessment']}
                    state.update(active_arm=arm, generation=0, phase='train', unit_index=0, dream_generation=-1)
                    commit(out, state, mind, arm+'-start.pt')
                else:
                    mind = recover(out, state)
                for generation in range(state['generation'], 4):
                    state['generation'] = generation
                    if state['phase'] == 'wake':
                        for j in range(state['unit_index'], 16):
                            start = time.perf_counter()
                            try:
                                record = mind.live(build_task(suite['wake'][j]), task_wall=args.task_wall)
                                if record.get('verdict') == 'SURE AND WRONG':
                                    raise ValueError('Wake tripwire: sure and wrong')
                            except PortBudget as exc:
                                state.setdefault('wake_failures', []).append(dict(arm=arm, generation=generation, task=j, reason=str(exc)))
                            state['costs'].append(dict(phase='wake', arm=arm, generation=generation, wall=time.perf_counter()-start))
                            state['unit_index'] = j+1
                            commit(out, state, mind, f'{arm}-g{generation}-wake{j}.pt')
                        state.update(phase='sleep', unit_index=0)
                        commit(out, state, mind, f'{arm}-g{generation}-wake-done.pt')
                    if state['phase'] == 'sleep':
                        start = time.perf_counter()
                        with mind.scope():
                            mind.sleep.abstract()
                            mind.sleep.dream(32, deadline=min(state['deadline'], time.time()+120))
                        state['costs'].append(dict(phase='dream', arm=arm, generation=generation, wall=time.perf_counter()-start))
                        state.update(phase='train', unit_index=0)
                        commit(out, state, mind, f'{arm}-g{generation}-dream.pt')
                    if state['phase'] == 'train':
                        for j in range(state['unit_index'], cap):
                            if sum(c['wall'] for c in state['costs'] if c['phase'] == 'train') >= 5400:
                                raise TimeoutError('Declared 1.5-hour training allowance exhausted')
                            trained = mind.train(1, 8, deadline=state['deadline'])
                            if not trained:
                                raise TimeoutError('Sleep training incomplete')
                            state['costs'].append(dict(phase='train', arm=arm, generation=generation, **trained[0]))
                            state['unit_index'] = j+1
                            commit(out, state, mind, f'{arm}-g{generation}-train{j}.pt')
                        state.update(phase='assessment', unit_index=0)
                        ck = f'{arm}-g{generation}.pt'
                        commit(out, state, mind, ck)
                        state['checkpoints'][arm+':'+str(generation)] = dict(file=ck, sha256=state['checkpoint_sha256'])
                        write(out/'state.json', state)
                    if state['phase'] == 'assessment':
                        trials = [('assessment', r) for r in suite['assessment']]+[('retention', r) for r in suite['retention']]
                        first = state['unit_index']
                        tasks = [build_task(spec) for _, spec in trials[first:]]
                        for j, row in enumerate(mind.assess_many(tasks, task_wall=args.task_wall), first):
                            label, spec = trials[j]
                            row.update(arm=arm, generation=generation, suite=label,
                                       domain='list' if LG.is_list(spec['tin']) else 'num')
                            if arms == CURIOSITY_ARMS:
                                row['learning_seconds'] = sum(c['wall'] for c in state['costs']
                                                              if c.get('arm', arm) == arm)
                                row['learning_seconds'] += sum(r['wall']+r.get('load_wall', 0.)
                                                               for r in state['rows'] if r['arm'] == arm)
                                row['learning_seconds'] += row['wall']+row.get('load_wall', 0.)
                            state['rows'].append(row)
                            state['unit_index'] = j+1
                            # Evaluation cursor belongs to runner metadata, not learning state.
                            write(out/'state.json', state)
                            if row.get('grade', {}).get('verdict') == 'SURE AND WRONG':
                                raise ValueError('Tripwire: sure and wrong in observer-only assessment')
                        state.update(generation=generation+1, phase='wake', unit_index=0)
                        commit(out, state, mind, f'{arm}-g{generation}-assessed.pt')
                state.update(arm_index=arm_index+1, active_arm=None)
                write(out/'state.json', state)
            state['stage'] = 'complete'
            state['finished'] = time.time()
            write(out/'state.json', state)
    except (ValueError, TimeoutError, subprocess.TimeoutExpired) as exc:
        state['failure'] = str(exc)
        state['failure_trace'] = traceback.format_exc()[-6000:]   # where it stopped, for the record
        state['finished'] = time.time()
        write(out/'state.json', state)
    finally:
        watchdog.cancel()
    return report(out)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='command', required=True)
    for command in ('preflight', 'run', 'report'):
        parser = sub.add_parser(command)
        parser.add_argument('--out', required=True)
        if command != 'report':
            parser.add_argument('--device', choices=('cpu', 'cuda'), default='cpu')
            parser.add_argument('--seed', type=int, default=3)
            parser.add_argument('--no-batched-reads', action='store_true',
                                help='Use the complete pre-US single-read execution path')
        if command == 'run':
            parser.add_argument('--laptop-preflight', default=None)
            parser.add_argument('--frozen-suite', default=None, help='Paired U6: saved U1 observer.json; observer side only')
            parser.add_argument('--arms', default=','.join(ARMS))
            parser.add_argument('--generations', type=int, default=3)
            parser.add_argument('--task-wall', type=float, default=10.)
            parser.add_argument('--eval-tasks', type=int, default=48)
            parser.add_argument('--wake-tasks', type=int, default=16)
            parser.add_argument('--hours', type=float, default=6.)
        if command == 'preflight':
            parser.add_argument('--laptop', action='store_true', help='This CPU machine is the actual target laptop')
    args = ap.parse_args()
    torch.set_num_threads(1)
    if args.command == 'preflight':
        result = timed_preflight(args.device, args.seed, Path(args.out), laptop=args.laptop, batched_reads=not args.no_batched_reads)
    elif args.command == 'report':
        result = report(args.out)
    else:
        result = run(args)
    print(json.dumps(result, sort_keys=True, default=str), flush=True)
    if result.get('failure') or ('complete' in result and not result['complete']):
        raise SystemExit(2)


if __name__ == '__main__':
    main()
