"""Attributable human source views and a separately declared simulation teacher."""
from array import array
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random

from .records import sha256

ROOT = Path(__file__).resolve().parents[1]
GENRE = ROOT / 'local/HUMAN-GENRE-data-v1'
LEGACY = ROOT / 'local/CONNECTED-003-data-v1'
SCHEDULE = ('semantic', 'physics', 'semantic', 'pairs', 'semantic', 'reading', 'semantic', 'math')
TRACKS = ('calculus', 'dailydialog', 'descartes', 'grammar', 'plato', 'programming', 'webster')


def identity(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def rank(prefix, value):
    return hashlib.sha256((prefix + value).encode()).hexdigest()


class Bank:
    def __init__(self, path, *, tracks=False):
        self.path = Path(path); self.offsets = array('Q'); self.tracks = defaultdict(list)
        with self.path.open('rb') as handle:
            while True:
                offset = handle.tell(); line = handle.readline()
                if not line: break
                index = len(self.offsets); self.offsets.append(offset)
                if tracks: self.tracks[json.loads(line)['track']].append(index)

    def get(self, indices):
        result = []
        with self.path.open('rb') as handle:
            for index in indices:
                handle.seek(self.offsets[index]); result.append(json.loads(handle.readline()))
        return result


def fixed(path, n, prefix, *, track=None):
    import heapq
    heap = []
    with Path(path).open(encoding='utf-8') as handle:
        for ordinal, line in enumerate(handle):
            row = json.loads(line)
            if track is not None and row['track'] != track: continue
            key = int(rank(prefix, row['id']), 16)
            heapq.heappush(heap, (-key, ordinal, row))
            if len(heap) > n: heapq.heappop(heap)
    return [row for _, _, row in sorted(heap, reverse=True)]


def untouched_semantic(cohort):
    path = GENRE / ('sealed_' + cohort + '.jsonl')
    # Replicate only the frozen prior ID selection, not predictions or selection
    # from outcomes. Exclude the complete premise groups, including unchosen rows.
    previous = fixed(path, 4096, 'GENRE-017-final-' + cohort)
    excluded = {row['source_group'] for row in previous}
    groups = defaultdict(list)
    with path.open(encoding='utf-8') as handle:
        for line in handle:
            row = json.loads(line)
            if row['source_group'] not in excluded: groups[row['source_group']].append(row)
    selected = sorted(groups, key=lambda x: rank('NATIVE-019-final|' + cohort + '|', x))[:256]
    rows = [r for g in selected for r in sorted(groups[g], key=lambda r: r['id'])]
    return rows, {'excluded_prior_groups': len(excluded), 'eligible_groups': len(groups),
                  'groups': selected, 'rows': len(rows), 'ids_sha256': identity([r['id'] for r in rows])}


def source_contract():
    expected = '40e3b405de1a964045ad9af9c2d36b75dc8924bfb54b097334881d989057e9e3'
    if sha256(GENRE / 'MANIFEST.json') != expected: raise ValueError('Human genre manifest changed')
    gm = json.loads((GENRE / 'MANIFEST.json').read_text())
    lm = json.loads((LEGACY / 'MANIFEST.json').read_text())
    for name, info in gm['partitions'].items():
        if sha256(GENRE / (name + '.jsonl')) != info['sha256']: raise ValueError('Genre view changed')
    for name, digest in lm['files'].items():
        if sha256(LEGACY / name) != digest: raise ValueError('Earlier human view changed')
    finals = {name: untouched_semantic(name)[1] for name in ('matched', 'mismatched')}
    return {'genre_manifest': expected, 'earlier_human_manifest': sha256(LEGACY / 'MANIFEST.json'),
            'prospective_protocol': sha256(ROOT / 'protocols/NATIVE-019.md'),
            'prospective_amendment': sha256(ROOT / 'protocols/NATIVE-019-AMENDMENT.md'),
            'source_group_selection': finals, 'native_final_predictions_opened': False}


class NativeData:
    def __init__(self):
        self.banks = {'semantic': Bank(GENRE / 'train.jsonl'),
            'pairs': Bank(LEGACY / 'train-pairs.jsonl', tracks=True),
            'reading': Bank(LEGACY / 'train-reading.jsonl'), 'math': Bank(LEGACY / 'train-math.jsonl')}
        self.orders = {}
        for name, bank in self.banks.items():
            parts = bank.tracks.items() if name == 'pairs' else [(name, range(len(bank.offsets)))]
            for key, indices in parts:
                order = list(indices); random.Random(int(rank('NATIVE-019-order', key), 16)).shuffle(order)
                self.orders[key] = order
        self.development = {'semantic': fixed(GENRE / 'development.jsonl', 256, 'NATIVE-019-development'),
            'reading': fixed(LEGACY / 'development-reading.jsonl', 128, 'NATIVE-019-reading'),
            'math': fixed(LEGACY / 'development-math.jsonl', 128, 'NATIVE-019-math')}
        self.development['pairs'] = [row for track in TRACKS for row in
            fixed(LEGACY / 'development-pairs.jsonl', 128, 'NATIVE-019-pairs', track=track)]

    def lesson(self, step, batch=32):
        kind = SCHEDULE[step % len(SCHEDULE)]
        occurrence = sum(1 for t in SCHEDULE[:step % len(SCHEDULE)] if t == kind)
        occurrence += (step // len(SCHEDULE)) * SCHEDULE.count(kind)
        if kind == 'physics':
            return kind, [physical_episode('NATIVE-019-training', occurrence * batch + i) for i in range(batch)]
        key = kind
        if kind == 'pairs':
            key = TRACKS[occurrence % len(TRACKS)]; occurrence //= len(TRACKS)
        order = self.orders[key]
        indices = [order[(occurrence * batch+i) % len(order)] for i in range(batch)]
        return kind, self.banks[kind].get(indices)

    def distractors(self, row, split):
        if split == 'train':
            bank = self.banks['pairs']; available = bank.tracks[row['track']]
            rng = random.Random(int(rank('NATIVE-019-options', row['id']), 16))
            result = []; seen = {row['answer']}; attempts = 0
            while len(result) < 3 and attempts < 100:
                candidate = bank.get([available[rng.randrange(len(available))]])[0]; attempts += 1
                if candidate['answer'] not in seen and candidate['group'] != row['group']:
                    result.append(candidate['answer']); seen.add(candidate['answer'])
            return result
        # Development distractors remain development-only. Some tiny source
        # tracks have no development rows; actual counts are always reported.
        choices = [r for r in self.development['pairs'] if r['track'] == row['track']
                   and r['group'] != row['group'] and r['answer'] != row['answer']]
        choices.sort(key=lambda r: rank(row['id'], r['id']))
        result = []; seen = {row['answer']}
        for candidate in choices:
            if candidate['answer'] not in seen:
                result.append(candidate['answer']); seen.add(candidate['answer'])
            if len(result) == 3: break
        return result

    def choices(self, kind, rows, split):
        contexts, alternatives, targets = [], [], []
        for row in rows:
            if kind == 'reading':
                contexts.append(row['context'] + '\nQuestion: ' + row['question'])
                alternatives.append(row['options']); targets.append(row['targets'])
            elif kind == 'pairs':
                options = [row['answer'], *self.distractors(row, split)]
                order = list(range(len(options)))
                random.Random(int(rank('NATIVE-019-choice', row['id']), 16)).shuffle(order)
                contexts.append(row['question']); alternatives.append([options[i] for i in order])
                targets.append([order.index(0)])
            elif kind == 'math':
                # Human worked steps provide the two operands. The learned task
                # selects an operation/equivalent exact result, not both operands.
                _, left, right = row['target']; a, b = map(Fraction, (row['values'][left], row['values'][right]))
                options, valid = [], []
                for op in ('+', '-', '*', '/'):
                    if op == '/' and not b: continue
                    value = {'+': lambda: a+b, '-': lambda: a-b, '*': lambda: a*b, '/': lambda: a/b}[op]()
                    if value == Fraction(row['answer']): valid.append(len(options))
                    options.append('(' + str(a) + ') ' + op + ' (' + str(b) + ')')
                if not valid: raise ValueError('Human worked step failed independent exact arithmetic')
                contexts.append(row['question']); alternatives.append(options); targets.append(valid)
            else: raise ValueError('Unknown human choice track')
        return contexts, alternatives, targets


def physical_episode(namespace, number, *, shifted=False):
    rng = random.Random(int(rank(namespace + '|', str(number)), 16))
    mass = rng.uniform(.5, 2.); drag = rng.uniform(0., .8); offset = rng.uniform(-.4, .4)
    quadratic = bool(number % 2)
    def outcome(force, velocity):
        return force / mass - drag * (velocity * abs(velocity) if quadratic else velocity) + offset
    support = [[rng.uniform(-1, 1), rng.uniform(-1, 1)] for _ in range(4)]
    support = [[force, v, outcome(force, v)] for force, v in support]
    limit = 1.5 if shifted else 1.
    queries = [[rng.uniform(-limit, limit), rng.uniform(-limit, limit)] for _ in range(3)]
    return {'id': identity([namespace, number]), 'namespace': namespace, 'number': number,
        'support': support, 'queries': queries, 'targets': [outcome(*q) for q in queries],
        'teacher_only': {'mass': mass, 'drag': drag, 'offset': offset, 'quadratic': quadratic}}


def independent_outcome(teacher, force, velocity):
    # Separately written scalar assessor. The owner does not import this module.
    drag_force = teacher['drag'] * velocity
    if teacher['quadratic']: drag_force *= abs(velocity)
    return (force - teacher['mass'] * drag_force) / teacher['mass'] + teacher['offset']
