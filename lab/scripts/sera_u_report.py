"""Generate a living SERA-U report from saved JSON only (stdlib, no learner imports).

Usage: python scripts/sera_u_report.py --runs BATCH [BATCH ...] --write SERA_U_REPORT.md
       --detail SERA_U_REPORT_TABLES.md
The main report has outcome, habit and noise summaries. All arm/generation tables
and provenance go to --detail (default: beside --write). Existing detail markers
in the main report are emptied; text outside markers remains byte-for-byte intact.
Markers: outcome, batches, assessment, full-curve, retention, habits, noise,
differences, sources, or tables (all sections). Unknown/duplicate/broken markers
are errors. An absent report receives an outcome/technical/plain-words template.
The default index is this checkout's sera-runs/report-index.json; --index overrides it.
Different frozen suites within a batch are refused. Across batches, tables are
partitioned by BOTH suite hashes. Comparisons also require equal saved allowances,
seed, device and evaluation sizes. Noise is the largest absolute replicate gap
for the same arm, generation and metric, not a confidence interval.
"""
import argparse
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
from itertools import combinations
import json
from pathlib import Path
import re
import statistics


REPO = Path(__file__).resolve().parents[1]
MISSING = 'MISSING'
MARKER = re.compile(r'<!-- generated:(begin|end) ([A-Za-z0-9_-]+) -->')
SECTIONS = ('outcome', 'batches', 'assessment', 'full-curve', 'retention',
            'habits', 'noise', 'differences', 'sources')


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False)


def cell(value, precision=2):
    if value is None:
        return MISSING
    if isinstance(value, float) or (numeric(value) and precision == 1):
        text = f'{value:.{precision}f}'
    elif isinstance(value, bool):
        text = 'true' if value else 'false'
    elif isinstance(value, (dict, list)):
        text = '; '.join(f'{path}={cell(item, 1 if seconds_metric(path) else precision)}'
                         for path, item in leaves(value))
    else:
        text = str(value)
    return text.replace('&', '&amp;').replace('|', '&#124;').replace('<', '&lt;').replace('>', '&gt;').replace('\r', '').replace('\n', '<br>')


def numeric(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def seconds_metric(name):
    return any(word in name.lower() for word in ('seconds', 'wall', 'duration'))


def utc_minute(value):
    if value is None:
        return None
    if numeric(value):
        stamp = datetime.fromtimestamp(value, timezone.utc)
    else:
        stamp = datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
    return stamp.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M')


def short_code(case):
    for source in (case.protocol, case.state):
        code = source.get('code') or source.get('code_sha256')
        if code:
            return str(code)[:12]
        for name in ('package', 'provenance'):
            package = source.get(name)
            if isinstance(package, dict):
                code = package.get('code') or package.get('code_sha256')
                if code:
                    return str(code)[:12]
    return None


def switch_delta(case, baseline):
    current = json.loads(case.switches)
    first = json.loads(baseline.switches)
    paths = sorted(set(current) | set(first))
    changed = [f'{path}={str(current.get(path, False)).lower()}'
               for path in paths if current.get(path, False) != first.get(path, False)]
    return '; '.join(changed) or 'same as first case'


def table(headers, rows, empty_credit=None):
    # All table types, including metadata and empty tables, show the tripwire.
    assert 'false credit' in headers
    out = ['| ' + ' | '.join(headers) + ' |', '|' + '|'.join('---' for _ in headers) + '|']
    metric_columns = [index for index, name in enumerate(headers)
                      if name in ('metric', 'saved curve metric', 'metric / JSON path')]
    for row in rows:
        metric = str(row[metric_columns[0]]) if metric_columns else ''
        out.append('| ' + ' | '.join(cell(value, 1 if seconds_metric(name) or
                   (name in ('value', 'left value', 'right value', 'right - left',
                             'measured absolute spread', 'maximum replicate spread')
                    and seconds_metric(metric)) else 2)
                   for name, value in zip(headers, row)) + ' |')
    if not rows:
        out.append('| ' + ' | '.join(cell(empty_credit) if name == 'false credit' else MISSING for name in headers) + ' |')
    return '\n'.join(out)


def leaves(value, prefix=''):
    """Keep every saved metric, including nulls and record detail, at its JSON path.

    Collections get derived .count rows as well as their original entries. Thus
    fidelity/calibration, chase endings and future habit fields need no invented
    defaults or task-specific reruns. Counts of records are labelled as such.
    """
    if isinstance(value, dict):
        if not value:
            yield prefix + '.count', len(value)
        for key in sorted(value):
            path = prefix + '.' + key if prefix else key
            if key in ('trees', 'mechanisms', 'operations', 'rebuilds', 'paradoxes', 'principles') and isinstance(value[key], dict):
                yield path + '.count', len(value[key])
            yield from leaves(value[key], path)
    elif isinstance(value, list):
        yield prefix + '.count', len(value)
        for index, item in enumerate(value):
            yield from leaves(item, f'{prefix}[{index}]')
    else:
        yield prefix, value


@dataclass
class Case:
    batch: Path
    root: Path
    state: dict
    protocol: dict
    curve: dict
    suite: tuple
    comparisons: list = field(default_factory=list)
    files: list = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    false_values: list = field(default_factory=list)
    comparison_false_values: list = field(default_factory=list)
    discovery_credit_known: bool = False
    notices: list = field(default_factory=list)

    @property
    def label(self):
        return self.batch.name + '/' + self.root.name.removeprefix('u-')

    @property
    def false_credit(self):
        # A zero assessment count cannot fill a missing discovery tripwire.
        value = max(self.false_values, key=abs) if self.false_values else None
        if value == 0 and 'discovery' in self.protocol and not self.discovery_credit_known:
            value = None
        result = MISSING if value is None else (f'{value} FLAG: must be zero' if value else value)
        if any(self.comparison_false_values):
            return f'{result}; batch comparison {max(self.comparison_false_values, key=abs)} FLAG: must be zero'
        return result

    @property
    def scope(self):
        p = self.protocol
        discovery = p.get('discovery', {})
        # The assessment suite and protocol: a discovery case and its discovery-off control are compared on the same
        # assessment suite (development review, 2026-10-03); discovery's own suite and share belong to the case's switches.
        return canonical([self.suite[0], {key: p.get(key) for key in
            ('seed', 'device', 'task_wall', 'eval_tasks', 'generations', 'wake_tasks',
             'hours', 'budgets', 'batched_reads', 'threads', 'reading_digest', 'teaching', 'clock', 'work')},
            self.state.get('retention_count')])

    @property
    def switches(self):
        p = self.protocol
        d = p.get('discovery', {})
        # Missing optional switches and explicitly false switches are equivalent.
        # Code/package digests are deliberately NOT switches: the motivating
        # no-memory/discovery-off replicate has different code digests.
        groups = {'crutches': p.get('crutches', {}), 'u14': p.get('u14', {}),
                  'discovery': {key: d.get(key, {}) for key in
                                ('switches', 'einstein', 'scientists', 'darwin', 'roadmap')}}
        on = {path: value for path, value in leaves(groups) if value is True}
        if any(value for path, value in on.items() if path.startswith('discovery.')):
            on['discovery suite'] = self.suite[1]
            on['discovery share'] = d.get('share')
            on['discovery generation wall'] = d.get('generation_wall')
        return canonical(on)

    @property
    def ending(self):
        if self.state.get('observer_stop') and not self.state.get('failure'):
            return 'observer_stop: '+str(self.state['observer_stop'])
        failure = self.state.get('failure') or self.curve.get('failure')
        if failure:
            kind = 'declared allowance' if 'allowance' in failure.lower() and 'exhaust' in failure.lower() else 'stop'
            return kind + ': ' + failure
        if self.state.get('stage') == 'complete':
            return 'finished' if self.curve.get('complete') is True else 'finished; saved curve incomplete or missing'
        return 'unfinished saved snapshot; stage=' + str(self.state.get('stage', MISSING))


def read_json(path, files, required=False):
    path = path.resolve()
    if not path.is_file():
        files.append({'path': path.as_posix(), 'status': 'missing'})
        if required:
            raise ValueError(f'Missing required saved file: {path}')
        return {}
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError(f'Expected JSON object: {path}')
    files.append({'path': path.as_posix(), 'sha256': hashlib.sha256(raw).hexdigest(), 'status': 'read'})
    return value


def false_evidence(case, value):
    for path, item in leaves(value):
        if path.split('.')[-1] == 'false_credit' and (numeric(item) or isinstance(item, bool)):
            case.false_values.append(int(item) if isinstance(item, bool) else item)


def extract(case):
    state, curve, p = case.state, case.curve, case.protocol
    rows = state.get('rows', [])
    false_evidence(case, state)
    false_evidence(case, curve)
    discovery_counts = []
    for source in (curve.get('discovery', {}),):
        if numeric(source.get('false_credit')) or isinstance(source.get('false_credit'), bool):
            discovery_counts.append(source['false_credit'])
    if 'discovery_judges' in state:
        judges = state['discovery_judges']
        if all('false_credit' in row for row in judges):
            discovery_counts.append(sum(bool(row['false_credit']) for row in judges))
    case.false_values.extend(discovery_counts)
    case.discovery_credit_known = bool(discovery_counts)
    for row in curve.get('exam', {}).get('generations', []):
        for name, value in leaves({k: v for k, v in row.items() if k not in ('arm', 'generation')}):
            case.metrics[('exam', row['arm'], row['generation'], name)] = value
    for arm, value in curve.get('holes', {}).items():
        for name, item in leaves(value):
            case.metrics[('holes', arm, 'latest', name)] = item
    # U8 has no explicit false_credit count. Its observer grades are evidence;
    # do not infer an all-clear if the grades are absent or partial.
    grades = [row.get('grade', {}).get('verdict') for row in rows]
    if grades and all(grade is not None for grade in grades):
        case.false_values.append(sum(grade == 'SURE AND WRONG' for grade in grades))
    groups = defaultdict(list)
    for row in rows:
        if row.get('suite') in ('assessment', 'retention'):
            groups[(row['suite'], row['arm'], row['generation'])].append(row)
    arms = sorted(set(p.get('arms', [])) | {key[1] for key in groups} | set(curve.get('curves', {})))
    for arm in arms:
        saved = {row['generation']: row for row in curve.get('curves', {}).get(arm, [])}
        generations = {key[2] for key in groups if key[1] == arm} | set(saved)
        if numeric(p.get('generations')):
            generations.update(range(p['generations'] + 1))
        for generation in sorted(generations):
            for suite in ('assessment', 'retention'):
                selected = groups.get((suite, arm, generation), [])
                expected = p.get('eval_tasks') if suite == 'assessment' else state.get('retention_count')
                solved = sum(bool(row['solved']) for row in selected) if selected and all('solved' in row for row in selected) else None
                walls = [row['wall'] for row in selected if numeric(row.get('wall'))]
                median = statistics.median(walls) if walls and len(walls) == len(selected) else None
                values = {'solved': solved, 'N': expected, 'rows': len(selected), 'median item wall seconds': median,
                          'fraction': solved / expected if solved is not None and numeric(expected) and expected > 0 else None}
                if suite == 'retention' and values['fraction'] is None:
                    kept = curve.get('retention', {}).get(arm, [])
                    if isinstance(kept, list) and generation < len(kept):
                        values['fraction'] = kept[generation]
                for name, value in values.items():
                    case.metrics[(suite, arm, generation, name)] = value
            for name, value in saved.get(generation, {}).items():
                if name != 'generation':
                    case.metrics[('curve', arm, generation, name)] = value
    discovery = curve.get('discovery')
    if discovery is None and 'discovery' in p:
        case.notices.append('g_curve.json discovery MISSING')
    for row in (discovery or {}).get('generations', []):
        arm, generation = row['arm'], row['generation']
        for name, value in leaves({key: value for key, value in row.items() if key not in ('arm', 'generation')}):
            case.metrics[('discovery', arm, generation, name)] = value
    for name in ('einstein', 'scientists'):
        for arm, row in curve.get(name, {}).get('arms', {}).items():
            for metric, value in leaves(row):
                case.metrics[(name, arm, row.get('generation', 'latest'), metric)] = value
    for path, comparison in case.comparisons:
        if numeric(comparison.get('false_credit')) or isinstance(comparison.get('false_credit'), bool):
            case.comparison_false_values.append(comparison['false_credit'])
        entries = comparison.get('cases', {})
        names = (case.root.name, case.root.name.removeprefix('u-'))
        matches = [entries[name] for name in names if name in entries]
        if len(matches) != 1:
            case.notices.append(path.name + ': case entry MISSING or ambiguous')
            continue
        entry = matches[0]
        false_evidence(case, entry)
        if numeric(entry.get('false_credit')) or isinstance(entry.get('false_credit'), bool):
            case.discovery_credit_known = True
        # A top-level comparison count is a batch tripwire, not a per-case count.
        for arm, row in entry.get('arms', {}).items():
            generation = row.get('generation', 'latest')
            for metric, value in leaves(row):
                case.metrics[(path.name, arm, generation, metric)] = value
        for arm, row in entry.get('roadmap', {}).items():
            for metric, value in leaves(row):
                case.metrics[(path.name, arm, 'latest', 'roadmap.' + metric)] = value
        for metric, value in leaves({key: value for key, value in entry.items() if key not in ('arms', 'roadmap')}):
            case.metrics[(path.name, 'case', 'saved', metric)] = value
    # Clarify important collection counts: attempted operations aren't all built.
    additions = {}
    for key, value in case.metrics.items():
        section, arm, generation, name = key
        if name.endswith('.admitted') or name.endswith('.kept'):
            parent = name.rsplit('.', 2)[0]
            label = 'built' if name.endswith('.admitted') else 'kept'
            target = (section, arm, generation, parent + '.' + label)
            additions[target] = additions.get(target, 0) + (value is True)
    case.metrics.update(additions)
    if 'discovery' in p and not case.discovery_credit_known:
        case.notices.append('Discovery false credit evidence MISSING')


def load_batches(paths):
    cases, all_files = [], []
    batches = sorted({Path(path).resolve() for path in paths}, key=lambda path: path.as_posix())
    if len({path.name for path in batches}) != len(batches):
        raise ValueError('Batch names must be unique for unambiguous report labels')
    for batch in batches:
        roots = sorted((path for path in batch.glob('u-*') if path.is_dir()), key=lambda path: path.name)
        if not roots:
            raise ValueError(f'No u-<case> folders in {batch}')
        comparisons = [(path, read_json(path, all_files)) for path in sorted(batch.glob('u1*-comparison.json'))]
        batch_cases = []
        for root in roots:
            files = []
            state = read_json(root / 'state.json', files, required=True)
            protocol = read_json(root / 'protocol.json', files) or state.get('protocol', {})
            if not protocol:
                raise ValueError(f'Protocol provenance MISSING: {root}')
            if state.get('protocol') and state['protocol'] != protocol:
                raise ValueError(f'State/protocol provenance disagrees: {root}')
            curve = read_json(root / 'g_curve.json', files)
            assessment = state.get('suite_sha256') or protocol.get('frozen_suite_sha256')
            if not assessment or (protocol.get('frozen_suite_sha256') and protocol['frozen_suite_sha256'] != assessment):
                raise ValueError(f'Frozen assessment suite hash MISSING or inconsistent: {root}')
            discovery = state.get('discovery_suite_sha256')
            if 'discovery' in protocol and not discovery:
                raise ValueError(f'Frozen discovery suite hash MISSING: {root}')
            case = Case(batch, root, state, protocol, curve, (assessment, discovery), files=files)
            local = [(path, read_json(path, files)) for path in sorted(root.glob('u1*-comparison.json'))]
            case.comparisons = comparisons + local
            if not case.comparisons:
                case.notices.append('comparison JSON MISSING (not zero; optional for memory-only cases)')
            else:
                declared = protocol.get('discovery', {})
                expected = next((filename for habit, filename in
                    (('roadmap', 'u13-comparison.json'), ('darwin', 'u12-comparison.json'),
                     ('scientists', 'u11-comparison.json'), ('einstein', 'u10-comparison.json'))
                    if habit in declared), None)
                if expected and not any(path.name == expected for path, _ in case.comparisons):
                    case.notices.append(expected + ' MISSING (not zero)')
            for path, comparison in case.comparisons:
                scope = comparison.get('matched_scope')
                if scope and tuple(scope[:2]) != case.suite:
                    raise ValueError(f'Comparison frozen suites disagree with saved state: {path}')
                expected_scope = (*case.suite, protocol.get('device'), protocol.get('seed'),
                                  protocol.get('discovery', {}).get('share'))
                if scope and tuple(scope) != expected_scope[:len(scope)]:
                    raise ValueError(f'Comparison seed/device/allowance disagrees with saved state: {path}')
            extract(case)
            all_files.extend(files)
            batch_cases.append(case)
        if (len({case.suite[0] for case in batch_cases}) != 1 or
                len({case.suite[1] for case in batch_cases if case.suite[1]}) > 1):
            raise ValueError(f'Different frozen suites in {batch}; refusing one comparison table. Supply separate homogeneous batch directories.')
        cases.extend(batch_cases)
    return cases, sorted({record['path']: record for record in all_files}.values(), key=lambda record: record['path'])


def paired_credit(left, right):
    return f'{left.label}: {left.false_credit}; {right.label}: {right.false_credit}'


def pooled(key):
    """A metric key without its generation: (source, arm, generation, metric) -> (source, arm, metric)."""
    return (key[0], key[1], key[3]) if len(key) == 4 else key


def record_detail(metric):
    # One saved record's own fields (a list entry such as `records[12].seconds`) stay in the saved JSON; the tables
    # keep every metric above them and each list's `.count` (U11's records made a 184,000-line detail file, 2026-10-03).
    return '[' in metric


def compared(key):
    # Differences and spreads are kept for what the outcome is read from: assessment and retention per arm and
    # generation, and each discovery snapshot's certified laws, experiments and seconds (development review, 2026-10-03).
    return key[0] in ('assessment', 'retention') or key[3] in ('laws', 'experiments', 'seconds')


def differences(cases):
    noise, spread_rows, diff_rows = {}, [], []
    for left, right in combinations(cases, 2):
        if left.scope != right.scope or left.switches != right.switches:
            continue
        for key in sorted((key for key in set(left.metrics) & set(right.metrics) if compared(key)), key=canonical):
            a, b = left.metrics[key], right.metrics[key]
            if not numeric(a) or not numeric(b):
                continue
            delta = b - a
            # One replicate pair gives one difference per generation (a 0 there is luck, not a bound): the spread of a
            # metric is the largest replicate difference over its generations (development review, 2026-10-03).
            noise[(left.scope, pooled(key))] = max(noise.get((left.scope, pooled(key)), 0), abs(delta))
            spread_rows.append((left.label, right.label, *key, a, b, delta, abs(delta), paired_credit(left, right)))
    for left, right in combinations(cases, 2):
        if left.scope != right.scope:
            continue
        for key in sorted((key for key in set(left.metrics) & set(right.metrics) if compared(key)), key=canonical):
            a, b = left.metrics[key], right.metrics[key]
            if not numeric(a) or not numeric(b):
                continue
            bound = noise.get((left.scope, pooled(key)))
            delta = b - a
            verdict = 'noise MISSING' if bound is None else ('within noise' if abs(delta) < bound else 'at or above measured spread')
            diff_rows.append((left.label, right.label, *key, a, b, delta, bound, verdict, paired_credit(left, right)))
    return spread_rows, diff_rows


def render_sections(cases, files):
    sections = {}
    sections['outcome'] = table(('case', 'outcome', 'saved evidence', 'false credit'),
        [(case.label, case.ending, '; '.join(case.notices) or 'saved JSON read', case.false_credit) for case in cases])
    first = {batch: next(case for case in cases if case.batch == batch)
             for batch in sorted({case.batch for case in cases})}
    sections['batches'] = table(('batch / case', 'package code', 'assessment suite sha256',
        'discovery suite sha256', 'machine', 'start UTC', 'end UTC', 'declared allowance',
        'ending', 'switch changes from first case', 'false credit'),
        [(case.label, short_code(case), case.suite[0],
          case.suite[1] if case.suite[1] else 'no discovery suite declared',
          case.state.get('preflight', {}).get('runtime') or case.curve.get('engineering', {}).get('runtime') or case.protocol.get('machine'),
          utc_minute(case.state.get('started')), utc_minute(case.state.get('finished')),
          {'hours': case.protocol.get('hours'), 'budgets': case.protocol.get('budgets'),
           'deadline UTC': utc_minute(case.state.get('deadline')),
           'clock': case.protocol.get('clock', 'wall'), 'work': case.protocol.get('work')},
          case.ending, switch_delta(case, first[case.batch]), case.false_credit) for case in cases])
    provenance = [(case.label, where, path,
                   str(value)[:12] if path.split('.')[-1] in ('code', 'code_sha256') and value else value,
                   case.false_credit)
                  for case in cases for where, source in (('protocol', case.protocol), ('state', case.state))
                  for path, value in leaves({key: value for key, value in source.items()
                                            if key in ('source', 'provenance') or key.startswith('package')})]
    sections['batches'] += '\n\n' + table(('case', 'saved source', 'provenance path', 'value', 'false credit'),
                                         provenance, '; '.join(f'{c.label}: {c.false_credit}' for c in cases))
    # Keep each suite scope in its own table, including metadata/habit tables.
    # Outcome and batches contain provenance only, never numerical A/B results.
    for section in SECTIONS[2:-1]:
        blocks = []
        for suite in sorted({case.suite for case in cases}, key=canonical):
            group = [case for case in cases if case.suite == suite]
            credits = '; '.join(f'{case.label}: {case.false_credit}' for case in group)
            title = 'Frozen suites: ' + canonical(suite) + '. Cases are comparable only on equal frozen suites.'
            if section in ('assessment', 'retention'):
                rows = []
                for case in group:
                    keys = sorted({(arm, generation) for kind, arm, generation, _ in case.metrics if kind == section})
                    for arm, generation in keys:
                        get = lambda metric: case.metrics.get((section, arm, generation, metric))
                        rows.append((case.label, arm, generation, get('solved'), get('N'), get('rows'),
                                     get('median item wall seconds'), get('fraction'), case.false_credit))
                body = table(('case', 'arm', 'generation', 'solved', 'N (declared)', 'rows saved',
                              'median item wall seconds', 'fraction of declared N', 'false credit'), rows)
            elif section == 'full-curve':
                rows = [(case.label, arm, generation, metric, value, case.false_credit)
                        for case in group for (kind, arm, generation, metric), value in sorted(case.metrics.items(), key=lambda item: canonical(item[0]))
                        if kind == 'curve' and arm == 'full']
                body = table(('case', 'arm', 'generation', 'saved curve metric', 'value', 'false credit'), rows, credits)
            elif section == 'habits':
                rows = [(case.label, kind, arm, generation, metric, value, case.false_credit)
                        for case in group for (kind, arm, generation, metric), value in sorted(case.metrics.items(), key=lambda item: canonical(item[0]))
                        if kind not in ('assessment', 'retention', 'curve') and arm in ('full', 'case') and not record_detail(metric)]
                rows.extend((case.label, 'availability', 'case', 'saved', 'evidence', notice, case.false_credit)
                            for case in group for notice in case.notices)
                body = table(('case', 'saved source / section', 'arm', 'generation', 'metric / JSON path', 'value', 'false credit'), rows)
                wiring_rows = [(case.label, r['arm'], r['generation'], r['observations'],
                    len(r['floor_worlds']), r['proposals'], r['candidates_audited'],
                    r['certified'], r['admitted'], name, len(h['received']), len(h['outputs']), case.false_credit)
                    for case in group for r in case.curve.get('discovery', {}).get('wiring', [])
                    for name, h in sorted(r['habits'].items())]
                if wiring_rows:
                    body += '\n\nWiring (saved records only; zero is a stopped hop).\n\n' + table(
                        ('case', 'arm', 'generation', 'observations', 'worlds at floor',
                         'proposals', 'audited', 'certified', 'admitted', 'habit', 'laws received', 'outputs', 'false credit'), wiring_rows)
            else:
                spreads, diffs = differences(group)
                base = ('left', 'right', 'section', 'arm', 'generation', 'metric', 'left value', 'right value', 'right - left')
                if section == 'noise':
                    body = table(base + ('measured absolute spread', 'false credit'), spreads, credits)
                    title += ' Matching saved switches; code digests may differ (see provenance). Largest replicate gap is used per metric/generation.'
                else:
                    body = table(base + ('maximum replicate spread', 'interpretation', 'false credit'), diffs, credits)
                    title += ' Smaller absolute differences are within noise; no replicate evidence means noise MISSING.'
                title += ' Comparisons additionally match saved seed, device, allowances and evaluation sizes.'
            blocks.append(title + '\n\n' + body)
        sections[section] = '\n\n'.join(blocks)
    credits = '; '.join(f'{case.label}: {case.false_credit}' for case in cases)
    sections['sources'] = table(('saved path', 'status', 'sha256 of bytes read', 'false credit'),
                                [(record['path'], record['status'], record.get('sha256'), credits) for record in files])
    sections['tables'] = '\n\n'.join('### ' + name + '\n\n' + sections[name] for name in SECTIONS)
    return sections


def full_outcome(case):
    generations = sorted({generation for kind, arm, generation, _ in case.metrics
                          if kind == 'assessment' and arm == 'full'})
    if not generations:
        return MISSING, MISSING, MISSING
    counts, walls, denominators = [], [], []
    for generation in generations:
        get = lambda metric: case.metrics.get(('assessment', 'full', generation, metric))
        count = cell(get('solved'))
        if get('solved') is not None and get('rows') != get('N'):
            count += ' (partial)'
        counts.append(count)
        denominators.append(get('N'))
        walls.append(cell(get('median item wall seconds'), 1))
    if len(set(denominators)) == 1:
        solved = ' '.join(counts) + ' /' + cell(denominators[0])
    else:
        solved = ' '.join(count + '/' + cell(n) for count, n in zip(counts, denominators))
    return ' '.join(map(str, generations)), solved, ' '.join(walls)


def habit_snapshots(case):
    """Comparison totals/latest snapshots take priority over the latest full curve."""
    groups = defaultdict(dict)
    for (kind, arm, generation, name), value in case.metrics.items():
        if arm == 'full' and kind not in ('assessment', 'retention', 'curve'):
            groups[(kind, generation)][name] = value
    def priority(key):
        kind, generation = key
        source = int(kind[1:3]) if kind.startswith('u1') and kind.endswith('-comparison.json') else 0
        return (source, generation if numeric(generation) else float('inf'), kind)
    snapshots, seen = [], set()
    for kind, generation in sorted(groups, key=priority, reverse=True):
        if kind not in seen:
            snapshots.append((kind + ':g' + str(generation), groups[(kind, generation)]))
            seen.add(kind)
    return snapshots


def habit_metric(snapshots, *paths):
    for source, values in snapshots:
        for path in paths:
            if path in values:
                return values[path], source
    return None, MISSING


def region_ratio(snapshots, numerator):
    # Saved regional Brier values are cumulative sums; divide by saved trials.
    for source, values in snapshots:
        for prefix in ('darwin.regions', 'regions'):
            count = values.get(prefix + '.count')
            if not isinstance(count, int) or count <= 0:
                continue
            totals, trials = [], []
            for index in range(count):
                totals.append(values.get(f'{prefix}[{index}].{numerator}'))
                trials.append(values.get(f'{prefix}[{index}].trials'))
            if not all(numeric(value) for value in totals + trials) or sum(trials) <= 0:
                return None, source
            return sum(totals) / sum(trials), source
    return None, MISSING


def habit_row(case, profile):
    snapshots, sources = habit_snapshots(case), set()
    def get(*paths):
        value, source = habit_metric(snapshots, *paths)
        if source != MISSING:
            sources.add(source)
        return cell(value, 1 if seconds_metric(paths[0]) else 2)
    def pair(label, first, second):
        return f'{label}={get(*first)}/{get(*second)}'
    values = [pair('laws/experiments', ('laws',), ('experiments',)) +
              '; seconds=' + get('seconds')]
    if profile == 'einstein':
        values += [pair('found/confirmed', ('einstein.paradoxes',), ('einstein.paradoxes_confirmed',)),
                   'principles=' + get('einstein.principles') + '; revisions=' + get('einstein.dual_world_revisions'),
                   'made=' + get('einstein.predictions') + '; confirmed=' + get('einstein.predictions_confirmed') +
                   '; failed=' + get('einstein.predictions_failed')]
    elif profile == 'scientists':
        values += [pair('audited/refuted', ('scientists.conjectures_audited',), ('scientists.conjectures_refuted',)),
                   get('scientists.conserved_quantities'),
                   'started=' + get('scientists.chases_started') + '; ' +
                   '; '.join(status + '=' + get('scientists.chase_endings.' + status)
                             for status in ('pending', 'active', 'released', 'explained'))]
    elif profile == 'darwin':
        fidelity, fidelity_source = region_ratio(snapshots, 'correct')
        calibration, calibration_source = region_ratio(snapshots, 'brier')
        sources.update(source for source in (fidelity_source, calibration_source) if source != MISSING)
        values += ['correct/trials=' + cell(fidelity) + '; Brier/trial=' + cell(calibration),
                   pair('trees/mechanisms', ('darwin.trees.count', 'trees.count'),
                        ('darwin.mechanisms.count', 'mechanisms.count')),
                   'made=' + get('prediction_counts.made', 'darwin.predictions.count') +
                   '; confirmed=' + get('prediction_counts.confirmed') + '; failed=' + get('prediction_counts.failed')]
    elif profile == 'roadmap':
        values += [get('roadmap.operations.built'), get('roadmap.rebuilds.kept'),
                   'coverage=' + get('roadmap.calibration.coverage') +
                   '; order MSE=' + get('roadmap.calibration.mean_squared_order_error'),
                   'mistakes=' + get('roadmap.pruning.mistakes.count') +
                   '; recovered=' + get('roadmap.pruning.recovered')]
    evidence = '; '.join(sorted(sources)) or 'habit metrics MISSING'
    if case.notices:
        evidence += '; ' + '; '.join(case.notices)
    return (case.label, *values, evidence, case.false_credit)


def render_summary_sections(cases):
    # Old detail markers are emptied in place, preserving all surrounding prose.
    sections = {name: '' for name in SECTIONS}
    outcome, habits, noise = [], [], []
    profiles = {
        'discovery': (),
        'einstein': ('paradoxes', 'principles / revisions', 'predictions'),
        'scientists': ('conjectures', 'conserved quantities', 'chases / endings'),
        'darwin': ('hologram fidelity / calibration', 'trees / mechanisms', 'predictions'),
        'roadmap': ('operations built', 'concepts rebuilt', 'estimate calibration', 'pruning'),
    }
    for suite in sorted({case.suite for case in cases}, key=canonical):
        group = [case for case in cases if case.suite == suite]
        title = ('Frozen suites: ' + str(suite[0]) + ' / ' +
                 (str(suite[1]) if suite[1] else 'no discovery suite declared') +
                 '. Cases are comparable only on equal frozen suites.')
        outcome.append(title + '\n\n' + table(
            ('case', 'outcome', 'full generations', 'full solved /N', 'median item seconds', 'false credit'),
            [(case.label, case.ending, *full_outcome(case), case.false_credit) for case in group]))
        _, diffs = differences(group)
        pairs = defaultdict(lambda: {'solved': [], 'median item wall seconds': []})
        for row in diffs:
            left, right, kind, arm, generation, metric, a, b, delta, bound, verdict, credit = row
            if kind != 'assessment' or arm != 'full' or metric not in ('solved', 'median item wall seconds'):
                continue
            precision = 1 if seconds_metric(metric) else 2
            pairs[(left, right)][metric].append(
                f'g{generation}: {cell(delta, precision)} / {cell(bound, precision)} {verdict}')
        indexed = {case.label: case for case in group}
        rows = []
        for (left, right), metrics in sorted(pairs.items()):
            a, b = indexed[left], indexed[right]
            rows.append((left, right, 'replicate' if a.switches == b.switches else 'A/B',
                         '; '.join(metrics['solved']) or MISSING,
                         '; '.join(metrics['median item wall seconds']) or MISSING, paired_credit(a, b)))
        credit = '; '.join(f'{case.label}: {case.false_credit}' for case in group)
        noise.append(title + '\nFull arm: right - left / maximum replicate spread over all generations, shown per generation. '
                     'Smaller absolute gaps are within noise; verdicts use unrounded values. '
                     'Pairs match saved seed, device, allowances and evaluation sizes. Every arm and generation is in the detail file.\n\n' +
                     table(('left', 'right', 'pair', 'solved: delta / spread', 'item seconds: delta / spread', 'false credit'),
                           rows, credit))
        for batch in sorted({case.batch for case in group}):
            batch_cases = [case for case in group if case.batch == batch]
            declared = {habit for case in batch_cases for habit in case.protocol.get('discovery', {})}
            profile = next((name for name in ('roadmap', 'darwin', 'scientists', 'einstein')
                            if name in declared), 'discovery')
            habit_title = ('### ' + batch.name + ' (' + profile + ')\n\n' + title +
                           '\nFull arm: comparison totals when saved; otherwise latest saved habit snapshot. '
                           'Sources identify each snapshot; other habits and arms are in the detail file.\n\n')
            habits.append(habit_title + table(
                ('case', 'certified laws / experiments / seconds', *profiles[profile], 'saved evidence', 'false credit'),
                [habit_row(case, profile) for case in batch_cases]))
    sections['outcome'] = '\n\n'.join(outcome)
    sections['habits'] = '\n\n'.join(habits)
    sections['noise'] = '\n\n'.join(noise)
    sections['tables'] = '\n\n'.join(sections[name] for name in ('outcome', 'habits', 'noise'))
    return sections


def update_markers(raw, sections):
    """Only replace marker interiors; preserve BOM, CRLF and arbitrary outside bytes."""
    text = raw.decode('utf-8')
    matches = list(MARKER.finditer(text))
    if not matches or len(matches) % 2:
        raise ValueError('Missing or unpaired generated markers')
    pieces, cursor, seen = [], 0, set()
    for index in range(0, len(matches), 2):
        begin, end = matches[index:index + 2]
        name = begin.group(2)
        if begin.group(1) != 'begin' or end.group(1) != 'end' or name != end.group(2):
            raise ValueError('Nested, mismatched or unpaired generated markers')
        if name in seen or name not in sections:
            raise ValueError(f'Duplicate or unknown generated section: {name}')
        seen.add(name)
        newline = '\r\n' if '\r\n' in text else '\n'
        pieces.extend((text[cursor:begin.end()], newline,
                       sections[name].replace('\n', newline), newline))
        cursor = end.start()
    pieces.append(text[cursor:])
    return ''.join(pieces).encode('utf-8')


def template(detail=False):
    if detail:
        return ('# SERA-U report tables\n\n' + '\n\n'.join(
            f'<!-- generated:begin {name} -->\n<!-- generated:end {name} -->'
            for name in SECTIONS) + '\n').encode('utf-8')
    return ('# SERA-U report\n\n<!-- generated:begin outcome -->\n<!-- generated:end outcome -->\n\n'
            '## Technical\n\n' + '\n\n'.join(f'<!-- generated:begin {name} -->\n<!-- generated:end {name} -->'
                for name in ('habits', 'noise')) + '\n\n## Plain words\n\n'
            'The tables read saved runs. Missing evidence stays marked as missing. '
            'Small differences are judged against repeated runs with the same switches.\n').encode('utf-8')


def generate(runs, report_path, index_path=None, detail_path=None):
    cases, files = load_batches(runs)
    report_path = Path(report_path)
    detail_path = Path(detail_path) if detail_path is not None else report_path.with_name('SERA_U_REPORT_TABLES.md')
    index_path = Path(index_path) if index_path is not None else REPO / 'sera-runs' / 'report-index.json'
    outputs = (report_path, detail_path, index_path)
    resolved = [path.resolve() for path in outputs]
    inputs = {Path(record['path']) for record in files}
    # Include comparison paths and reject aliases before reading output templates.
    if len(set(resolved)) != len(outputs) or any(path in inputs for path in resolved):
        raise ValueError('Outputs must not overwrite each other or saved inputs')
    sections = render_sections(cases, files)
    summary = render_summary_sections(cases)
    raw = report_path.read_bytes() if report_path.exists() else template()
    detail_raw = detail_path.read_bytes() if detail_path.exists() else template(detail=True)
    output = update_markers(raw, summary)
    detail_output = update_markers(detail_raw, sections)
    index = {'report': report_path.resolve().as_posix(), 'detail': detail_path.resolve().as_posix(), 'files': files,
             'states': [record for record in files if Path(record['path']).name == 'state.json']}
    index_output = (json.dumps(index, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode('utf-8')
    # All saved evidence, suites, paths and both marker sets are validated first.
    report_path.write_bytes(output)
    detail_path.write_bytes(detail_output)
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_bytes(index_output)
    return cases


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', nargs='+', required=True, type=Path)
    parser.add_argument('--write', required=True, type=Path)
    parser.add_argument('--detail', type=Path, help='Detail report (default: SERA_U_REPORT_TABLES.md beside --write)')
    parser.add_argument('--index', type=Path, default=REPO / 'sera-runs' / 'report-index.json')
    args = parser.parse_args(argv)
    try:
        cases = generate(args.runs, args.write, args.index, args.detail)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, str(exc) + '\n')
    if any(any(value != 0 for value in case.false_values + case.comparison_false_values) for case in cases):
        parser.exit(2, 'Report written with FLAG: false credit must be zero\n')
    detail = args.detail or args.write.with_name('SERA_U_REPORT_TABLES.md')
    print(f'Updated {args.write}; detail {detail}; index {args.index}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
