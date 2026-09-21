"""Source-group-disjoint streaming course views for the complete fresh owner."""
from array import array
from collections import Counter, defaultdict
import json
from pathlib import Path
import random

from .native_data import ROOT, GENRE, LEGACY, Bank, NativeData, TRACKS, rank, identity, physical_episode
from .records import sha256, write_json

DATA = ROOT/'local/CORE-022-course-v1'
PROGRAMS = ROOT/'local/CORE-022-executable-human-v2'
FILES = {'semantic': GENRE/'train.jsonl', 'pairs': LEGACY/'train-pairs.jsonl',
         'reading': LEGACY/'train-reading.jsonl', 'programs': PROGRAMS/'train.jsonl'}
SCHEDULE = ('semantic', 'physics', 'programs', 'pairs', 'reading', 'semantic',
            'physics', 'programs', 'pairs', 'mixed', 'semantic', 'pairs')
SPLIT_KEY = 'CORE-022-fresh-course-groups-20260921-v1|'


def partition(group):
    bucket = int(rank(SPLIT_KEY, group)[:8], 16) % 20
    return 'final' if bucket == 0 else 'development' if bucket == 1 else 'train'


def prepare():
    if DATA.exists(): raise ValueError('Do not overwrite or reallocate a frozen course')
    DATA.mkdir()
    pools = {}; counts = {}; files = {}; groups = defaultdict(set)
    for kind, path in FILES.items():
        pools[kind] = {role: defaultdict(list) for role in ('train', 'development', 'final')}
        stats = Counter()
        with path.open(encoding='utf-8') as handle:
            for index, line in enumerate(handle):
                row = json.loads(line); group = row.get('group', row.get('source_group'))
                if not group: raise ValueError('Missing original source group')
                role = partition(group); track = row['track'] if kind == 'pairs' else kind
                pools[kind][role][track].append(index); stats[role+':'+track] += 1
                groups[role].add(group)
        counts[kind] = dict(stats); files[kind] = {'path': path.relative_to(ROOT).as_posix(), 'sha256': sha256(path)}
    if any(groups[a] & groups[b] for a,b in (('train','development'), ('train','final'), ('development','final'))):
        raise ValueError('Source groups cross course partitions')
    # Names and hash bucket determine allocation. No prediction, loss or
    # assessment result is computed during allocation.
    write_json(DATA/'INDICES.json', pools)
    record = {'schema': 'sera-field.core022.course-allocation.1', 'split_key': SPLIT_KEY,
        'files': files, 'counts': counts, 'indices_sha256': sha256(DATA/'INDICES.json'),
        'groups': {role: {'count': len(items), 'sha256': identity(sorted(items))} for role,items in groups.items()},
        'prior_sealed_partitions_opened': False, 'model_predictions_computed': False,
        'source_transform_precedes_this_allocation': True, 'all_weights_will_start_fresh': True,
        'allocation_rule': 'Original training groups hashed: bucket 0 final, 1 development, 2..19 teaching; one rule across views.',
        'source_manifests': {str(p.relative_to(ROOT)): sha256(p) for p in (
            GENRE/'MANIFEST.json', LEGACY/'MANIFEST.json', PROGRAMS/'MANIFEST.json')},
        'code': {p: sha256(ROOT/p) for p in ('sera_field/core_course_data.py', 'sera_field/core_teaching.py')}}
    write_json(DATA/'MANIFEST.json', record)
    write_json(ROOT/'reports/CORE-022/COURSE_ALLOCATION.json', record)
    return record


class CoreData(NativeData):
    """Native human choices retain their exact task labels; graphs add a new use."""
    def __init__(self, *, open_final=False):
        manifest = json.loads((DATA/'MANIFEST.json').read_text())
        if sha256(DATA/'INDICES.json') != manifest['indices_sha256']: raise ValueError('Course allocation changed')
        self.pools = json.loads((DATA/'INDICES.json').read_text())
        self.banks = {}
        for kind, entry in manifest['files'].items():
            path = ROOT/entry['path']
            if sha256(path) != entry['sha256']: raise ValueError('Frozen source view changed')
            self.banks[kind] = Bank(path)
        for track, indices in self.pools['pairs']['train'].items():
            self.banks['pairs'].tracks[track] = indices
        self.orders = {}
        for kind in self.banks:
            for track, indices in self.pools[kind]['train'].items():
                order = list(indices); random.Random(int(rank('CORE-022-order|', kind+'|'+track), 16)).shuffle(order)
                self.orders[kind+':'+track] = order
        self.development = self.cohort('development', 64)
        self.allow_final = open_final

    def cohort(self, role, maximum):
        if role == 'final' and not getattr(self, 'allow_final', False):
            raise ValueError('Explicit assessment invocation required to open the reserved cohort')
        if role not in ('development','final'): raise ValueError('Only independent assessment roles')
        result = {}
        for kind, bank in self.banks.items():
            result[kind] = []
            for track, indices in self.pools[kind][role].items():
                chosen = sorted(indices, key=lambda i: rank('CORE-022-'+role+'|'+kind+'|'+track+'|', str(i)))[:maximum]
                result[kind].extend(bank.get(chosen))
        return result

    def rows(self, kind, occurrence, batch):
        track = kind
        if kind == 'pairs':
            tracks = [t for t in TRACKS if self.pools[kind]['train'].get(t)]
            track = tracks[occurrence % len(tracks)]; occurrence //= len(tracks)
        order = self.orders[kind+':'+track]
        return self.banks[kind].get([order[(occurrence*batch+i) % len(order)] for i in range(batch)])

    def lesson(self, step, batch=8):
        kind = SCHEDULE[step % len(SCHEDULE)]
        occurrence = SCHEDULE[:step % len(SCHEDULE)].count(kind)+(step//len(SCHEDULE))*SCHEDULE.count(kind)
        if kind == 'physics': return kind, [physical_episode('CORE-022-physical-teaching', occurrence*batch+i) for i in range(batch)]
        if kind == 'mixed':
            return kind, pair(self.rows('semantic', occurrence, batch), 'CORE-022-mixed-teaching', occurrence*batch)
        return kind, self.rows(kind, occurrence, batch)


def pair(human_rows, namespace, start=0, *, shifted=False):
    rows = []
    for i, human in enumerate(human_rows):
        number = start+i
        physical = physical_episode(namespace, number, shifted=shifted)
        # Quadratic/linear family alternates on the low bit. Chronology changes
        # on the next bit, avoiding the earlier family's parity confound.
        rows.append({'id': identity([namespace, human['id'], number]), 'human': human,
            'physics': physical, 'text_first': bool((number//2)%2), 'supports': 4 if shifted else 2})
    return rows
