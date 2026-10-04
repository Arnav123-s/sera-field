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
from sera import crutches as CR
from sera_u.discovery import CRUTCHES as U9_CRUTCHES, DEFAULT_SHARE, generation_report


def finite(value, where, found):
    """A copy with each non-finite float as its repr ('inf', '-inf', 'nan'): strict JSON keeps it, said plainly.

    VM A's U10 control (25d7a29) stopped writing state.json on an inf from a discovery commit; `found` names where."""
    if isinstance(value, float) and not math.isfinite(value):
        found.append(where)
        return repr(value)
    if isinstance(value, dict):
        return {k: finite(v, f'{where}/{k}', found) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [finite(v, f'{where}/{i}', found) for i, v in enumerate(value)]
    return value


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    pending = path.with_name(path.name+'.pending')
    found = []
    value = finite(value, '', found)
    if found:
        print(f'{path.name}: non-finite values written as strings at', found[:8], file=sys.stderr, flush=True)
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
    # Named generation samples survive; every other unit replaces one rolling
    # file. Bootstrap's rolling file remains the immutable shared arm parent.
    named = (checkpoint == f'{mind.arm}-g{state.get("generation", 0)}.pt' or
             any(r['file'] == checkpoint for r in state.get('checkpoints', {}).values()))
    checkpoint = checkpoint if named else ('bootstrap-rolling.pt' if state.get('stage') != 'arms'
                                           else mind.arm+'-rolling.pt')
    state['checkpoint'] = checkpoint
    data = mind.dumps()
    state['checkpoint_sha256'] = hashlib.sha256(data).hexdigest()
    temporary = (out/checkpoint).with_name(checkpoint+'.pending')
    with temporary.open('wb') as fh:
        fh.write(data)
        fh.flush()
        os.fsync(fh.fileno())
    # A journal is observer metadata only. Either old state+checkpoint, or this
    # journal+new checkpoint, is valid after a crash between the two replaces.
    write(out/'state.pending', state)
    os.replace(temporary, out/checkpoint)
    write(out/'state.json', state)


def recover(out, state):
    path = out/state['checkpoint']
    if hashlib.sha256(path.read_bytes()).hexdigest() != state['checkpoint_sha256']:
        journal = read(out/'state.pending') if (out/'state.pending').exists() else {}
        if journal.get('checkpoint') != state['checkpoint'] or hashlib.sha256(path.read_bytes()).hexdigest() != journal.get('checkpoint_sha256'):
            raise ValueError('Stale/corrupt runner checkpoint')
        state.update(journal)
        write(out/'state.json', state)
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
    if state['protocol'].get('clock') == 'work' or state.get('life_session'):
        return work_report(out, state)
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
    if 'discovery' in state['protocol']:
        from scripts.sera_u_discovery import report as discovery_report
        result['discovery'] = discovery_report(state.get('discovery_generations', []),
                                               state.get('discovery_judges', []))
        if any('einstein' in r for r in state.get('discovery_generations', [])):
            from scripts.sera_u_einstein import report_einstein
            result['einstein'] = report_einstein(state['discovery_generations'], state.get('discovery_judges', []))
        if any('scientists' in r for r in state.get('discovery_generations', [])):
            from scripts.sera_u_scientists import report_scientists
            result['scientists'] = report_scientists(state['discovery_generations'], state.get('discovery_judges', []))
    write(out/'g_curve.json', result)
    return result


def run(args):
    if getattr(args, 'clock', 'wall') == 'work' or getattr(args, 'life', None):
        return run_work(args)
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
    discovery_on = CR.on('open_worlds')
    if discovery_on:
        share = getattr(args, 'discovery_share', DEFAULT_SHARE)
        if not math.isfinite(share) or not 0 < share <= .5:
            raise ValueError('Discovery share must be finite, positive and at most one half')
        if args.hours*3600*share > 5400:
            raise ValueError('Discovery must fit the existing training allowance (share <= .25 at six hours)')
        protocol['discovery'] = dict(share=share, switches={k: CR.on(k) for k in U9_CRUTCHES},
            generation_wall=args.hours*3600/(len(arms)*(args.generations+1)),
            suite='frozen observer-owned rediscovery, never supplied questions or laws')
        from sera_u.einstein import CRUTCHES as U10_CRUTCHES
        if any(CR.on(k) for k in U10_CRUTCHES):
            protocol['discovery']['einstein'] = {k: CR.on(k) for k in U10_CRUTCHES}
            if not getattr(args, 'rediscovery_suite', None):
                raise ValueError('U10 A/B requires one frozen observer Einstein suite')
        from sera_u.scientists import CRUTCHES as U11_CRUTCHES
        if any(CR.on(k) for k in U11_CRUTCHES):
            protocol['discovery']['scientists'] = {k: CR.on(k) for k in U11_CRUTCHES}
            if not getattr(args, 'rediscovery_suite', None):
                raise ValueError('U11 A/B requires one frozen scientists suite')
        from sera_u.roadmap import CRUTCHES as U13_CRUTCHES
        if any(CR.on(key) for key in U13_CRUTCHES):
            protocol['discovery']['roadmap'] = {key: CR.on(key) for key in U13_CRUTCHES}
            if not args.rediscovery_suite:
                raise ValueError('U13 A/B requires one frozen roadmap suite')
        from sera_u.darwin import CRUTCHES as U12_CRUTCHES
        if any(CR.on(key) for key in U12_CRUTCHES):
            protocol['discovery']['darwin'] = {key: CR.on(key) for key in U12_CRUTCHES}
            if not getattr(args, 'rediscovery_suite', None):
                raise ValueError('U12 requires one frozen lineage suite')
        protocol['budgets']['discovery'] = args.hours*3600*share
        protocol['budgets']['train'] = max(0., 5400-protocol['budgets']['discovery'])
        external_discovery = getattr(args, 'rediscovery_suite', None)
        if external_discovery:
            protocol['discovery']['suite_sha256'] = hashlib.sha256(Path(external_discovery).read_bytes()).hexdigest()
    frozen_path = getattr(args, 'frozen_suite', None)
    if arms == CURIOSITY_ARMS and frozen_path is None:
        raise ValueError('Paired U6 A/B requires --frozen-suite pointing to the saved U1 observer.json')
    frozen_bytes = Path(frozen_path).read_bytes() if frozen_path else None
    if frozen_bytes is not None:
        # Any paired A/B may share one saved observer suite: each case's own suite is built from its own bootstrap's
        # proofs, so cases that bootstrap differently would otherwise be assessed on different items.
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
                    raise ValueError('Paired bootstrap failed the same eight-program/four-source gate')
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
            if discovery_on:
                from scripts.sera_u_discovery import freeze as freeze_discovery, validate as validate_discovery
                external = getattr(args, 'rediscovery_suite', None)
                manifest = (validate_discovery(read(external), suite, base) if external else
                            validate_discovery(freeze_discovery(base, suite, args.seed), suite, base))
                if 'einstein' in protocol['discovery'] and manifest.get('einstein_suite') != 'u10-einstein-1':
                    raise ValueError('U10 requires an observer Einstein suite, frozen once and never taught')
                if 'scientists' in protocol['discovery'] and manifest.get('scientists_suite') != 'u11-scientists-1':
                    raise ValueError('U11 requires a scientists suite, frozen once and never taught')
                if 'darwin' in protocol['discovery'] and manifest.get('lineage_suite') != 'u12-lineage-1':
                    raise ValueError('U12 requires a lineage suite, frozen once and never taught')
                if 'roadmap' in protocol['discovery'] and manifest.get('roadmap_suite') != 'u13-roadmap-1':
                    raise ValueError('U13 requires a roadmap suite, frozen once and never taught')
                write(out/'observer-discovery.json', manifest)
                state['discovery_suite_sha256'] = hashlib.sha256((out/'observer-discovery.json').read_bytes()).hexdigest()
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
            if discovery_on:
                cap = max(0, int(cap*protocol['budgets']['train']/5400))
                if hashlib.sha256((out/'observer-discovery.json').read_bytes()).hexdigest() != state['discovery_suite_sha256']:
                    raise ValueError('Frozen rediscovery suite changed')
                from scripts.sera_u_discovery import WorldPool, teach_quantity_once
                discovery_manifest = read(out/'observer-discovery.json')
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
                    if discovery_on:
                        state.update(phase='discovery', discovery_deadline=None)
                        demo_start = len(mind.discovery.events)
                        with mind.scope():
                            teach_quantity_once(mind)
                            if hasattr(mind.discovery, 'einstein'):
                                from scripts.sera_u_einstein import teach_einstein_once
                                teach_einstein_once(mind)
                            if hasattr(mind.discovery, 'scientists'):
                                from scripts.sera_u_scientists import teach_scientists_once
                                teach_scientists_once(mind)
                            if hasattr(mind.discovery, 'darwin'):
                                from scripts.sera_u_darwin import teach_darwin_once
                                teach_darwin_once(mind)
                            if hasattr(mind.discovery, 'roadmap'):
                                from scripts.sera_u_roadmap import teach_roadmap_once
                                teach_roadmap_once(mind)
                        for demo in mind.discovery.events[demo_start:]:
                            state['costs'].append(dict(phase='roadmap-method-demonstration' if demo.get('roadmap_demo') else 'darwin-method-demonstration' if demo.get('darwin_demo') else 'scientists-method-demonstration' if demo.get('scientist_demo') else 'einstein-method-demonstration' if demo.get('einstein_demo')
                                else 'quantity-demonstration', arm=arm, wall=demo['seconds']))
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
                        state.update(phase='discovery' if discovery_on else 'sleep', unit_index=0)
                        if discovery_on:
                            state['discovery_deadline'] = None
                        commit(out, state, mind, f'{arm}-g{generation}-wake-done.pt')
                    if state['phase'] == 'discovery':
                        if any(r['false_credit'] for r in state.get('discovery_judges', [])):
                            raise ValueError('Discovery tripwire persists: false credit must be zero')
                        if discovery_manifest.get('roadmap_suite'):
                            from scripts.sera_u_roadmap import RoadmapPool
                            pool = RoadmapPool(discovery_manifest, generation=generation)
                        elif discovery_manifest.get('lineage_suite'):
                            from scripts.sera_u_darwin import LineagePool
                            pool = LineagePool(discovery_manifest, generation=generation)
                        elif discovery_manifest.get('scientists_suite'):
                            from scripts.sera_u_scientists import ScientistsPool
                            pool = ScientistsPool(discovery_manifest)
                        else:
                            pool = WorldPool(discovery_manifest)
                        if state.get('discovery_deadline') is None:
                            allowance = protocol['discovery']['generation_wall']*protocol['discovery']['share']
                            state['discovery_deadline'] = min(state['deadline'], time.time()+allowance)
                            state['discovery_started'] = time.time()
                            state['discovery_event_start'] = len(mind.discovery.events)
                            commit(out, state, mind, f'{arm}-g{generation}-discovery-start.pt')
                        # The absolute phase deadline and last completed tick are
                        # committed together; resume never resets the allowance.
                        while time.time() < state['discovery_deadline']:
                            if hasattr(mind.discovery, 'darwin'):
                                mind.field.hologram['generation'] = generation
                            unit_started = time.perf_counter()
                            row = mind.discover(pool, deadline=state['discovery_deadline'])
                            if row is None:
                                break
                            row['seconds'] = time.perf_counter()-unit_started
                            state['costs'].append(dict(phase='discovery', arm=arm, generation=generation,
                                                       wall=row['seconds']))
                            state.setdefault('discovery_judges', []).extend(
                                dict(r, arm=arm, generation=generation) for r in pool.audit_records)
                            pool.audit_records.clear()
                            state['unit_index'] += 1
                            # Persist even a tripwire before stopping, so a
                            # false certification is never hidden by rollback.
                            # A crash between checkpoint save and state.json
                            # replacement must leave the previous file intact.
                            commit(out, state, mind, f'{arm}-g{generation}-discovery{state["unit_index"]}.pt')
                            if any(r['false_credit'] for r in state['discovery_judges']):
                                raise ValueError('Discovery tripwire: false credit must be zero')
                        rows = mind.discovery.events[state['discovery_event_start']:]
                        summary = generation_report(rows)
                        summary['seconds'] = time.time()-state['discovery_started']
                        summary['seconds_per_law'] = summary['seconds']/summary['laws'] if summary['laws'] else None
                        state.setdefault('discovery_generations', []).append(dict(arm=arm, generation=generation, **summary))
                        state.update(phase='sleep', unit_index=0)
                        commit(out, state, mind, f'{arm}-g{generation}-discovery-done.pt')
                    if state['phase'] == 'sleep':
                        start = time.perf_counter()
                        with mind.scope():
                            mind.sleep.abstract()
                            if discovery_on:
                                if discovery_manifest.get('roadmap_suite'):
                                    from scripts.sera_u_roadmap import RoadmapPool
                                    dream_pool = RoadmapPool(discovery_manifest, generation=generation)
                                elif discovery_manifest.get('lineage_suite'):
                                    from scripts.sera_u_darwin import LineagePool
                                    dream_pool = LineagePool(discovery_manifest, generation=generation)
                                elif discovery_manifest.get('scientists_suite'):
                                    from scripts.sera_u_scientists import ScientistsPool
                                    dream_pool = ScientistsPool(discovery_manifest)
                                else:
                                    dream_pool = WorldPool(discovery_manifest)
                                dream_pool.sync(mind.discovery)
                                mind.sleep.dream(32, deadline=min(state['deadline'], time.time()+120),
                                                 filter_program=dream_pool.dream_allowed)
                            else:
                                mind.sleep.dream(32, deadline=min(state['deadline'], time.time()+120))
                        state['costs'].append(dict(phase='dream', arm=arm, generation=generation, wall=time.perf_counter()-start))
                        state.update(phase='train', unit_index=0)
                        commit(out, state, mind, f'{arm}-g{generation}-dream.pt')
                    if state['phase'] == 'train':
                        for j in range(state['unit_index'], cap):
                            if sum(c['wall'] for c in state['costs'] if c['phase'] == 'train') >= protocol['budgets']['train']:
                                raise TimeoutError('Declared training allowance exhausted' if discovery_on else
                                                   'Declared 1.5-hour training allowance exhausted')
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


def work_report(out, state):
    """Everything here is computed from persisted observer records."""
    from scripts.sera_u_discovery import report as discovery_report
    result = dict(schema='u14-work-1', protocol=state['protocol'],
        complete=state['stage'] == 'complete', observer_stop=state.get('observer_stop'),
        failure=state.get('failure'), checkpoints=state['checkpoints'],
        costs=state['costs'], questions=state.get('rows', []),
        digests=state.get('digests', {}), holes=state.get('holes', {}),
        discovery=discovery_report(state.get('discovery_generations', []), state.get('discovery_judges', [])))
    result['exam'] = dict(asked=len(state.get('exam_items', {})),
        right_at_first_answer=sum(r.get('right_at_first_answer') is True for r in state.get('exam_items', {}).values()),
        answered_eventually=sum(r.get('answered_eventually') is True for r in state.get('exam_items', {}).values()),
        still_open=sum(r.get('status') == 'not-yet' for r in state.get('exam_items', {}).values()),
        items=state.get('exam_items', {}))
    result['exam']['generations'] = []
    for arm in state['protocol']['arms']:
        for generation in sorted({r['generation'] for r in state.get('exam_items', {}).values() if r['arm'] == arm}):
            items = [r for r in state['exam_items'].values() if r['arm'] == arm and r['generation'] == generation]
            result['exam']['generations'].append(dict(arm=arm, generation=generation, asked=len(items),
                right_at_first_answer=sum(r['right_at_first_answer'] is True for r in items),
                answered_eventually=sum(r['answered_eventually'] is True for r in items),
                still_open=sum(r['status'] == 'not-yet' for r in items),
                work_to_answer=[r['work_to_answer'] for r in items if r['work_to_answer'] is not None]))
    result['exam']['false_credit'] = sum(r.get('grade', {}).get('verdict') == 'SURE AND WRONG'
                                      for r in state.get('exam_items', {}).values())
    result['false_credit'] = result['exam']['false_credit'] + result['discovery']['false_credit']
    if (Path(out)/'observer-discovery.json').exists():
        manifest = read(Path(out)/'observer-discovery.json')
        if manifest.get('holes_suite'):
            from scripts.sera_u_holes import report_holes
            result['holes_suite'] = report_holes(state.get('discovery_generations', []), manifest)
    write(Path(out)/'g_curve.json', result)
    return result


def run_work(args):
    """One observer work allowance; SERA allocates it through learned methods.

    Generation boundaries are observer sampling points, never inner method
    quotas. Absolute work limits are saved with the cursor and survive pauses.
    """
    from sera_u.mind import U14_CRUTCHES
    from sera_u.discovery import Readout
    from scripts.sera_u_discovery import WorldPool, validate, freeze
    from scripts.sera_one import teaching
    from sera_u.life import Life
    life = Life(args.life) if getattr(args, 'life', None) else None
    if args.work <= 0 or args.observer_wall <= 0:
        raise ValueError('Positive session work and observer wall required')
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    arms = tuple(args.arms.split(','))
    if any(a not in ARMS+CURIOSITY_ARMS+('no-holes', 'no-questions-first') for a in arms) or len(set(arms)) != len(arms):
        raise ValueError('Unknown or repeated work arm')
    protocol = dict(seed=args.seed, device=args.device, clock=args.clock, work=args.work,
        generations=args.generations, eval_tasks=args.eval_tasks, wake_tasks=args.wake_tasks,
        arms=list(arms), code=code_identity(), source=source_identity(),
        batched_reads=not args.no_batched_reads,
        u14={k: CR.on(k) for k in U14_CRUTCHES},
        # U14's two arms are the full arm with some U14 switches off (configure_fork); they had no settings of their
        # own here and stopped every work run at its start (Colab, 2026-10-03 21:17).
        crutches={a: arm_settings('full' if a in ('no-holes', 'no-questions-first') else a) for a in arms},
        u14_arms={a: sorted(k for k in U14_CRUTCHES if (a == 'no-holes' and k.startswith('holes_')) or
                            (a == 'no-questions-first' and k == 'questions_first'))
                  for a in arms if a in ('no-holes', 'no-questions-first')},
        discovery=dict(switches={k: CR.on(k) for k in U9_CRUTCHES}),
        frozen_suite_sha256=hashlib.sha256(Path(args.frozen_suite).read_bytes()).hexdigest() if args.frozen_suite else None,
        rediscovery_sha256=hashlib.sha256(Path(args.rediscovery_suite).read_bytes()).hexdigest() if args.rediscovery_suite else None)
    for module, group in (('einstein', 'einstein'), ('scientists', 'scientists'),
                          ('darwin', 'darwin'), ('roadmap', 'roadmap')):
        import importlib
        switches = importlib.import_module('sera_u.'+module).CRUTCHES
        protocol['discovery'][group] = {k: CR.on(k) for k in switches}
    if (out/'state.json').exists():
        state = read(out/'state.json')
        if state['protocol'] != protocol:
            raise ValueError('Exact work resume requires the same frozen protocol')
        if bool(life) != bool(state.get('life_session')) or (args.session is not None and
                args.session != state.get('life_session')):
            raise ValueError('Changed life/session on exact work resume')
        mind = recover(out, state)
    else:
        factory = lambda: SeraU(args.seed, device=args.device, clock=args.clock, wiring=True,
                                batched_reads=not args.no_batched_reads)
        mind, parent = life.open(factory, carry=args.carry) if life else (factory(), None)
        if mind.clock_mode != args.clock:
            # Work/wall is an observer protocol choice; retaining its learned
            # policies and Field does not create a new mind.
            from sera_u.clock import Clock
            mind.clock_mode = args.clock
            if args.clock == 'work' and not hasattr(mind, 'clock'):
                mind.clock, mind.work_policy = Clock(), Readout()
        if args.clock == 'work':
            mind.clock.start(args.work)
        state = dict(protocol=protocol, stage='bootstrap', started=time.time(), rows=[], costs=[],
            checkpoints={}, bootstrap_index=0, arm_index=0, active_arm=None, generation=0,
            phase='growth', unit_index=0, parent_count=mind.clock.count if args.clock == 'work' else 0)
        if life:
            row = life.begin(mind, args.work, parent, session=getattr(args, 'session', None))
            state.update(life_session=row['id'], life_parent=parent)
            if life.ledger['born']:
                state['stage'] = 'prepare'
            else:
                state['bootstrap_index'] = life.ledger.get('birth_index', 0)
        commit(out, state, mind, 'bootstrap.pt')
        write(out/'protocol.json', protocol)
    stop = threading.Event()
    timer = threading.Timer(args.observer_wall, stop.set)
    timer.daemon = True
    timer.start()
    state.pop('observer_stop', None)
    life_row = next((r for r in life.ledger['sessions'] if r['id'] == state['life_session']), None) if life else None
    if life and life_row is None:
        timer.cancel()
        raise ValueError('Runner session is absent from this life ledger')
    working = args.clock == 'work'
    if not working and not hasattr(mind, 'work_policy'):
        mind.work_policy = Readout()
    used = lambda: mind.clock.count if working else sum(c['wall'] for c in state['costs']
        if c.get('arm', state.get('active_arm')) == state.get('active_arm'))
    spent_out = lambda: mind.clock.expired() if working else used() >= args.hours*3600
    try:
        if state['stage'] == 'bootstrap':
            lessons = [(n, b) for n, b in teaching(args.seed) if n.startswith(('number:', 'list:'))]
            for index in range(state['bootstrap_index'], len(lessons)):
                if stop.is_set() or spent_out():
                    state['observer_stop'] = 'safety_wall' if stop.is_set() else 'session_work'
                    break
                name, builder = lessons[index]
                task = builder()
                if len(task.data) < 4:
                    x = task.pool[0]
                    task.data.append((x, task._y(x)))
                started, count = time.perf_counter(), used()
                mind.live(task, teaching=True, task_wall=math.inf if working else args.task_wall)
                state['bootstrap_index'] = index+1
                state['costs'].append(dict(phase='bootstrap', task=name, work=used()-count if working else 0,
                                           wall=time.perf_counter()-started))
                commit(out, state, mind, 'bootstrap.pt')
                if life:
                    life.save_birth(mind, index+1)
            if state['bootstrap_index'] == len(lessons):
                if not state.get('methods_taught'):
                    started, count = time.perf_counter(), used()
                    with mind.scope():
                        from scripts.sera_u_discovery import teach_quantity_once
                        from scripts.sera_u_einstein import teach_einstein_once
                        from scripts.sera_u_scientists import teach_scientists_once
                        from scripts.sera_u_darwin import teach_darwin_once
                        from scripts.sera_u_roadmap import teach_roadmap_once
                        if mind.discovery:
                            teach_quantity_once(mind)
                            if hasattr(mind.discovery, 'einstein'):
                                teach_einstein_once(mind)
                            if hasattr(mind.discovery, 'scientists'):
                                teach_scientists_once(mind)
                            if hasattr(mind.discovery, 'darwin'):
                                teach_darwin_once(mind)
                            if hasattr(mind.discovery, 'roadmap'):
                                teach_roadmap_once(mind)
                        if hasattr(mind, 'agenda') and mind.u14['questions_first']:
                            mind.agenda.demonstrate(phase='lesson', origin='taught')
                        if hasattr(mind, 'holes'):
                            mind.holes.demonstrate(phase='lesson', origin='taught')
                    state['methods_taught'] = True
                    state['costs'].append(dict(phase='birth-method-demonstrations',
                        work=used()-count if working else 0, wall=time.perf_counter()-started))
                    commit(out, state, mind, 'bootstrap.pt')
                if life and not life.ledger['born']:
                    life.born(mind)
                state['stage'] = 'prepare'
        if state['stage'] == 'prepare':
            suite = validate_frozen_suite(read(args.frozen_suite)) if args.frozen_suite else freeze_suite(mind, args.seed)
            manifest = validate(read(args.rediscovery_suite), suite, mind) if args.rediscovery_suite else freeze(mind, suite, args.seed)
            write(out/'observer.json', suite)
            write(out/'observer-discovery.json', manifest)
            state.update(stage='arms', suite_sha256=hashlib.sha256((out/'observer.json').read_bytes()).hexdigest(),
                discovery_suite_sha256=hashlib.sha256((out/'observer-discovery.json').read_bytes()).hexdigest(),
                base='base.pt', base_sha256=mind.save(out/'base.pt'))
            if life:
                life_row['fork_parent_digest'] = state['base_sha256']
                from sera_u.life import atomic_json
                atomic_json(life.ledger_path, life.ledger)
            write(out/'state.json', state)
        if state['stage'] == 'arms':
            suite, manifest = read(out/'observer.json'), read(out/'observer-discovery.json')
            if hashlib.sha256((out/'observer.json').read_bytes()).hexdigest() != state['suite_sha256'] or \
                    hashlib.sha256((out/'observer-discovery.json').read_bytes()).hexdigest() != state['discovery_suite_sha256']:
                raise ValueError('Frozen observer suite changed')
            for arm_index in range(state['arm_index'], len(arms)):
                arm = arms[arm_index]
                if state['active_arm'] != arm:
                    mind = SeraU.load(out/'base.pt')
                    # A fork carries all learned state; only the requested
                    # removable method switches differ. No fresh owner or RNG.
                    configure_fork(mind, arm)
                    if not working and not hasattr(mind, 'work_policy'):
                        mind.work_policy = Readout()
                    mind.sleep.reserved = set(suite['reserved'])
                    mind.sleep.reserved_sources = {r['source'] for r in suite['assessment']}
                    state.update(active_arm=arm, generation=0, unit_index=0)
                    queue_exam(mind, suite, state, life, life_row, 0)
                    commit(out, state, mind, arm+'-rolling.pt')
                    if life:
                        life.checkpoint(life_row, mind)
                pool = work_pool(manifest, state['generation'])
                if mind.discovery:
                    pool.sync(mind.discovery)
                while not spent_out() and not stop.is_set():
                    start, count = time.perf_counter(), used()
                    event_start = len(mind.discovery.events) if mind.discovery else 0
                    x = mind.choice_features()
                    choices = ['wake']
                    if mind.discovery is not None:
                        choices.append('discover')
                    if mind.sleep.replay:
                        choices.extend(('dream', 'train'))
                    allowed_questions = {q['id'] for q in getattr(getattr(mind, 'agenda', None), 'items', {}).values()
                        if q['status'] == 'open' and (q['outside'] or any(h['agenda'] == q['id'] and
                            mind.holes.switches[h['reason']] for h in getattr(getattr(mind, 'holes', None), 'questions', {}).values()))}
                    if allowed_questions:
                        choices.append('question')
                    first = [q for q in getattr(getattr(mind, 'agenda', None), 'items', {}).values()
                             if q['outside'] and q['status'] == 'open' and not q['not_yet']]
                    choice = ('question' if first and mind.u14['questions_first'] else
                                mind.work_policy.pick(choices, x, mind.numpy))
                    bound = mind.clock.bound(choice, mind) if working else time.time()+args.task_wall
                    gain = 0.
                    if choice == 'question':
                        key = mind.agenda.next(mind, priority=mind.u14['questions_first'], allowed=allowed_questions)
                        if not mind.agenda.items[key]['outside'] and hasattr(mind, 'holes'):
                            row = mind.work_hole(key, pool, deadline=bound)
                            gain = float(mind.agenda.items[key]['status'] == 'answered')
                            response = None
                        else:
                            response = 'outside'
                        item = state['exam_items'].get(arm+':'+key)
                        # Previous sessions' public questions also remain open;
                        # their observer bodies are loaded from the life ledger.
                        if item is None and life:
                            item = next((q for q in life.ledger.get('exam_records', {}).values()
                                         if q['id'] == key), None)
                        body = build_task(item['spec']) if item else None
                        if response is not None:
                            response = mind.work_question(key, body=body, task_wall=args.task_wall)
                            gain = float(response['answer'] is not None)
                        if item and response is not None:
                            grade_question(item, response, body, args.seed)
                            state['exam_items'][arm+':'+key] = item
                            if life and arm == 'full':
                                life.ledger.setdefault('exam_records', {})[key] = copy.deepcopy(item)
                                from sera_u.life import atomic_json
                                atomic_json(life.ledger_path, life.ledger)
                    elif choice == 'discover':
                        row = mind.discover(pool, deadline=bound)
                        if row is not None:
                            row['seconds'] = time.perf_counter()-start
                            gain = row['progress']+float(row['discovered'])
                    elif choice == 'dream':
                        with mind.scope():
                            allowance = max(1, int(bound-mind.clock.count)) if working else 32
                            gain = len(mind.sleep.dream(count=allowance,
                                attempts=allowance if working else 512, deadline=bound, filter_program=pool.dream_allowed))
                    elif choice == 'train':
                        batches = max(1, int(bound-mind.clock.count)) if working else 1
                        previous = next((r['objective'] for r in reversed(mind.sleep.logs) if r['kind'] == 'train'), None)
                        trained = mind.train(batches, 8, deadline=bound)
                        if trained and previous is not None:
                            gain = max(0., previous-trained[-1]['objective'])
                    else:
                        spec = suite['wake'][state['unit_index'] % len(suite['wake'])]
                        from sera_u.mind import AssessmentTask
                        record = mind.live(AssessmentTask(build_task(spec)), task_wall=math.inf if working else args.task_wall)
                        gain = float(record['proven'])
                    # Every route can ask the judge, including a hole chase.
                    state.setdefault('discovery_judges', []).extend(dict(r, arm=arm,
                        generation=state['generation']) for r in pool.audit_records)
                    pool.audit_records.clear()
                    if mind.discovery:
                        state.setdefault('discovery_records', []).extend(dict(copy.deepcopy(r),
                            arm=arm, generation=state['generation']) for r in mind.discovery.events[event_start:])
                    if hasattr(mind, 'holes'):
                        state.setdefault('holes', {})[arm] = copy.deepcopy(mind.holes.report(mind))
                    if any(r['false_credit'] for r in state['discovery_judges']):
                        commit(out, state, mind, arm+'-rolling.pt')
                        raise ValueError('Discovery tripwire: false credit must be zero')
                    spent = mind.clock.count-count if working else time.perf_counter()-start
                    if not spent:
                        if working:
                            mind.clock.charge('method')
                        spent = 1
                    mind.work_policy.learn(choice, x, gain, spent)
                    if working:
                        mind.clock.finish(choice, mind, spent, gain)
                        spent = mind.clock.count-count
                    state['costs'].append(dict(phase=choice, arm=arm, generation=state['generation'],
                        work=spent if working else 0, wall=time.perf_counter()-start))
                    state['unit_index'] += 1
                    milestone = state['parent_count'] + (args.work if working else args.hours*3600)*(state['generation']+1)/(args.generations+1)
                    while state['generation'] <= args.generations and used() >= milestone:
                        if mind.discovery:
                            records = [r for r in state.get('discovery_records', []) if
                                       r['arm'] == arm and r['generation'] == state['generation']]
                            summary = generation_report(records)
                            if 'wiring' not in summary:
                                # An empty interval still displays the last
                                # recorded public snapshot, with zero new work.
                                prior = next((r for r in reversed(state.get('discovery_records', []))
                                              if r['arm'] == arm and 'wiring' in r), None)
                                if prior is not None:
                                    summary['wiring'] = copy.deepcopy(prior['wiring'])
                                    summary['wiring'].update(proposals=0, candidates_audited=0, certified=0, admitted=0)
                                    for hop in summary['wiring']['habits'].values():
                                        hop['outputs'] = []
                            if 'wiring' in summary:
                                audits = [r for r in state.get('discovery_judges', []) if
                                          r['arm'] == arm and r['generation'] == state['generation']]
                                summary['wiring'].update(candidates_audited=len(audits),
                                    certified=sum(r['accepted'] for r in audits),
                                    admitted=sum(bool(r.get('fresh')) for r in summary.get('admission_records', [])))
                            if arm in state.get('holes', {}):
                                summary['holes'] = copy.deepcopy(state['holes'][arm])
                            state.setdefault('discovery_generations', []).append(dict(arm=arm,
                                generation=state['generation'], **summary))
                        name = f'{arm}-g{state["generation"]}.pt'
                        sha = mind.save(out/name)
                        state['checkpoints'][arm+':'+str(state['generation'])] = dict(file=name, sha256=sha)
                        state['generation'] += 1
                        if hasattr(pool, 'generation'):
                            pool.generation = state['generation']
                        if state['generation'] <= args.generations:
                            queue_exam(mind, suite, state, life, life_row, state['generation'])
                        milestone = state['parent_count'] + (args.work if working else args.hours*3600)*(state['generation']+1)/(args.generations+1)
                    commit(out, state, mind, arm+'-rolling.pt')
                    if life:
                        life.checkpoint(life_row, mind)
                if stop.is_set():
                    state['observer_stop'] = 'safety_wall'
                    if life:
                        life.finish_arm(life_row, mind, dict(costs=state['costs'], questions=state.get('exam_items', {}),
                            discovery_judges=state.get('discovery_judges', [])), complete=False)
                    break
                state.setdefault('digests', {})[arm] = mind.learning_hash()
                if hasattr(mind, 'holes'):
                    state.setdefault('holes', {})[arm] = mind.holes.report(mind)
                if life:
                    life.finish_arm(life_row, mind, dict(costs=state['costs'], questions=state.get('exam_items', {}),
                        discovery_generations=state.get('discovery_generations', []),
                        discovery_judges=state.get('discovery_judges', [])), complete=True)
                state.update(arm_index=arm_index+1, active_arm=None)
                write(out/'state.json', state)
            if state['arm_index'] == len(arms):
                state['stage'] = 'complete'
        state['finished'] = time.time()
        write(out/'state.json', state)
        if life:
            if state['stage'] == 'bootstrap':
                life.save_birth(mind, state['bootstrap_index'])
                life_row['work_done'] = max(0, mind.clock.count-life_row['start_work']) if working else 0
            life.finish(life_row, 'complete' if state['stage'] == 'complete' else 'observer_stop')
    except (ValueError, TimeoutError) as exc:
        state.update(failure=str(exc), failure_trace=traceback.format_exc()[-6000:], finished=time.time())
        commit(out, state, mind, mind.arm+'-rolling.pt')
        if life:
            life.finish_arm(life_row, mind, dict(costs=state['costs'], questions=state.get('exam_items', {}),
                discovery_judges=state.get('discovery_judges', []), failure=str(exc)), complete=False)
            life.finish(life_row, 'failure')
    finally:
        timer.cancel()
    return work_report(out, state)


def fresh_exam(spec, seed, serial):
    """Fresh inputs from a frozen generator. All outputs stay observer-side
    until they are the four public examples of the once-asked question."""
    rng = np.random.default_rng([seed, 1403, serial])
    distribution = Distribution(spec['tin'])
    xs = tuple(distribution(rng) for _ in range(20))
    public = copy.deepcopy(spec)
    public.update(examples=xs[:4], pool=xs[4:], name='exam-'+str(serial))
    return public


def queue_exam(mind, suite, state, life, life_row, generation):
    state.setdefault('exam_items', {})
    history = set(life.ledger['exam_asked']) if life else set()
    history.update(r['public_digest'] for r in state['exam_items'].values() if r['arm'] == mind.arm)
    serial = (len(life.ledger['exam_asked']) if life else 0) + generation*len(suite['assessment'])
    # Every paired arm uses the same parent's draw sequence, even after full
    # has advanced the ledger. Its initial history/count are saved once.
    state.setdefault('exam_parent_count', len(life.ledger['exam_asked']) if life else 0)
    state.setdefault('exam_parent_history', sorted(history))
    serial = state['exam_parent_count'] + generation*len(suite['assessment'])
    history = set(state['exam_parent_history']) | {r['public_digest'] for r in
        state['exam_items'].values() if r['arm'] == mind.arm}
    for j, original in enumerate(suite['assessment']):
        attempt = 0
        while True:
            spec = fresh_exam(original, state['protocol']['seed'], serial+j+attempt*1000000)
            body = build_task(spec)
            view = TaskView.from_task(body)
            if view.identity not in history:
                break
            attempt += 1
        key = mind.ask(view, 'exam:'+view.identity)
        history.add(view.identity)
        item = dict(id=key, arm=mind.arm, generation=generation, spec=spec,
            public_digest=view.identity, status='not-yet', right_at_first_answer=None,
            answered_eventually=False, work_to_answer=None, responses=0)
        state['exam_items'][mind.arm+':'+key] = item
        # After the single ask it is experience. Teaching demonstrations still
        # cannot run here; only an unchanged proof can create a replay receipt.
        mind.sleep.reserved.discard(original['family'])
        mind.sleep.reserved_sources.discard(original['source'])
        if life and mind.arm == 'full':
            life.ledger['exam_asked'].append(view.identity)
            life.ledger.setdefault('exam_records', {})[key] = copy.deepcopy(item)
            life_row['questions_asked'].append(key)
    if life:
        from sera_u.life import atomic_json
        atomic_json(life.ledger_path, life.ledger)


def grade_question(item, response, body, seed):
    """Observer-only. Nothing returned to SERA from this function."""
    item['responses'] += 1
    item['work'] = response['work']
    if response['answer'] is None:
        item['status'] = 'not-yet'
        return
    grade = body.grade(LG.freeze(response['answer']), {}, True, seed=seed)
    right = grade['verdict'] == 'proven right'
    first_answer = item['right_at_first_answer']
    if first_answer is None:
        first_answer = right
    item.update(status='answered', answered_eventually=right, work_to_answer=response['work'],
                right_at_first_answer=first_answer, grade=grade, late=response['late'])
    if grade['verdict'] == 'SURE AND WRONG':
        raise ValueError('Exam tripwire: sure and wrong')


def work_pool(manifest, generation):
    from scripts.sera_u_discovery import WorldPool
    if manifest.get('roadmap_suite'):
        from scripts.sera_u_roadmap import RoadmapPool as Pool
    elif manifest.get('lineage_suite'):
        from scripts.sera_u_darwin import LineagePool as Pool
    elif manifest.get('scientists_suite'):
        from scripts.sera_u_scientists import ScientistsPool as Pool
    else:
        Pool = WorldPool
    if manifest.get('holes_suite'):
        from scripts.sera_u_holes import HolesPool
        if Pool is WorldPool:
            Pool = HolesPool
        else:
            class LinkedPool(HolesPool, Pool):
                pass
            Pool = LinkedPool
    return Pool(manifest, generation=generation) if manifest.get('lineage_suite') else Pool(manifest)


def configure_fork(mind, arm):
    mind.arm = arm
    from sera_u.mind import U14_CRUTCHES
    settings = arm_settings('full' if arm in ('no-holes', 'no-questions-first') else arm)
    mind.u14 = {k: CR.on(k) for k in U14_CRUTCHES}
    if arm == 'no-holes':
        for key in sorted(mind.u14):
            if key.startswith('holes_'):
                mind.u14[key] = False
    if arm == 'no-questions-first':
        mind.u14['questions_first'] = False
    if any(mind.u14.values()) and not hasattr(mind, 'agenda'):
        from sera_u.agenda import Agenda
        mind.agenda = Agenda()
    if any(mind.u14.values()) and not hasattr(mind, 'holes'):
        from sera_u.holes import Holes
        mind.holes = Holes(mind.u14)
    if hasattr(mind, 'holes'):
        mind.holes.switches = {k: mind.u14['holes_'+k] for k in mind.holes.switches}
    for key in ('field_proposer', 'program_dreams', 'sleep_library'):
        mind.crutches[key] = settings[key]
    mind.proposer.enabled = mind.crutches['field_proposer']
    mind.engine.library_enabled = mind.crutches['sleep_library']


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='command', required=True)
    for command in ('preflight', 'run', 'report'):
        parser = sub.add_parser(command)
        parser.add_argument('--out', required=True)
        if command != 'report':
            parser.add_argument('--device', choices=('cpu', 'cuda'), default='cpu')
            parser.add_argument('--seed', type=int, default=3)
            parser.add_argument('--threads', type=int, default=1,
                                help='Work-mode observer thread count; learner reductions always use one thread')
            parser.add_argument('--no-batched-reads', action='store_true',
                                help='Use the complete pre-US single-read execution path')
        if command == 'run':
            parser.add_argument('--clock', choices=('work', 'wall'), default='wall')
            parser.add_argument('--life', default=None, help='Continue one rolling SERA; full advances it, ablations fork')
            parser.add_argument('--session', default=None, help='Stable optional life session identity')
            parser.add_argument('--carry', action='store_true', help='Explicit new-code carry; exact load still refuses changed code')
            parser.add_argument('--work', type=int, default=100000,
                                help='Observer total session work per paired arm, including shared birth')
            parser.add_argument('--observer-wall', type=float, default=21600.,
                                help='Work mode: outer observer stop, never a learner deadline')
            parser.add_argument('--laptop-preflight', default=None)
            parser.add_argument('--frozen-suite', default=None, help='Paired A/Bs: one saved observer.json shared by every case; observer side only')
            parser.add_argument('--arms', default=','.join(ARMS))
            parser.add_argument('--generations', type=int, default=3)
            parser.add_argument('--task-wall', type=float, default=10.)
            parser.add_argument('--eval-tasks', type=int, default=48)
            parser.add_argument('--wake-tasks', type=int, default=16)
            parser.add_argument('--hours', type=float, default=6.)
            parser.add_argument('--discovery-share', type=float, default=DEFAULT_SHARE,
                                help='Open worlds only: fixed fraction of each nominal generation wall (default .10)')
            parser.add_argument('--rediscovery-suite', default=None,
                                help='Open worlds only: frozen observer-discovery.json shared by same-VM cases')
        if command == 'preflight':
            parser.add_argument('--laptop', action='store_true', help='This CPU machine is the actual target laptop')
    args = ap.parse_args()
    if getattr(args, 'threads', 1) <= 0:
        ap.error('--threads must be positive')
    torch.set_num_threads(args.threads if getattr(args, 'clock', 'wall') == 'work' else 1)
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
