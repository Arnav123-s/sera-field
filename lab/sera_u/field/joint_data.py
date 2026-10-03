"""Prospective mixed histories with attributable human text and declared physics."""
from collections import defaultdict
import json
import random

from .native_data import (ROOT, GENRE, NativeData, Bank, fixed, rank, identity,
                          untouched_semantic, physical_episode, independent_outcome)
from .records import sha256


def fresh_human(cohort):
    path = GENRE / ('sealed_' + cohort + '.jsonl')
    previous = fixed(path, 4096, 'GENRE-017-final-' + cohort)
    excluded = {r['source_group'] for r in previous + untouched_semantic(cohort)[0]}
    groups = defaultdict(list)
    with path.open(encoding='utf-8') as handle:
        for line in handle:
            row = json.loads(line)
            if row['source_group'] not in excluded:
                groups[row['source_group']].append(row)
    selected = sorted(groups, key=lambda g: rank('JOINT-020-final|' + cohort, g))[:128]
    if len(selected) != 128:
        raise ValueError('Insufficient untouched complete premise groups')
    return [r for group in selected for r in sorted(groups[group], key=lambda r: r['id'])]


def paired(rows, namespace, start=0, *, shifted=False):
    result = []
    for i, human in enumerate(rows):
        number = start+i
        physical = physical_episode(namespace, number, shifted=shifted)
        result.append({'id': identity([namespace, human['id'], physical['id']]),
                       'human': human, 'physics': physical, 'text_first': bool(number % 2),
                       'supports': 4 if shifted else 2})
    return result


def registered_sources():
    native = json.loads((ROOT / 'runs/NATIVE-019/native/SELECTION.json').read_text())
    manifest = json.loads((GENRE / 'MANIFEST.json').read_text())
    if sha256(GENRE / 'MANIFEST.json') != '40e3b405de1a964045ad9af9c2d36b75dc8924bfb54b097334881d989057e9e3':
        raise ValueError('Human source manifest changed')
    for name, info in manifest['partitions'].items():
        if sha256(GENRE / (name + '.jsonl')) != info['sha256']:
            raise ValueError('Human source bytes changed')
    finals = {}
    for name in ('matched', 'mismatched'):
        rows = fresh_human(name)
        finals[name] = {'ids': [r['id'] for r in rows],
                        'groups': sorted({r['source_group'] for r in rows}),
                        'source_rows_sha256': identity(rows)}
    return {'initial_selection': native, 'protocol_sha256': sha256(ROOT / 'protocols/JOINT-020.md'),
            'human_manifest': sha256(GENRE / 'MANIFEST.json'), 'finals': finals,
            'initial_from_scratch_lineage': True, 'external_pretrained_weights': False}


class JointData:
    def __init__(self):
        self.rehearsal = NativeData()
        self.bank = self.rehearsal.banks['semantic']
        self.order = list(range(len(self.bank.offsets)))
        random.Random(202019).shuffle(self.order)
        human = fixed(GENRE / 'development.jsonl', 128, 'JOINT-020-development')
        self.development = paired(human, 'JOINT-020-development')

    def lesson(self, cycle, batch=16):
        positions = [self.order[(cycle*batch+i) % len(self.order)] for i in range(batch)]
        return paired(self.bank.get(positions), 'JOINT-020-training', cycle*batch)

    def finals(self, cohort):
        return paired(fresh_human(cohort), 'JOINT-020-final-' + cohort)

    def shifted(self):
        human = fresh_human('matched')
        return paired(human[:256], 'JOINT-020-shifted-final', shifted=True)


def action_number(row):
    # Uniform independent behavior, identical for both training arms. Selection
    # at evaluation instead uses the model's retained learned action scores.
    return random.Random(int(rank('JOINT-020-action', row['id']), 16)).randrange(10)
