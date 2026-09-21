"""Chronology-only repair with preserved teaching inputs and unopened groups."""
from collections import defaultdict
import json

from .joint_data import JointData, paired, registered_sources as original_sources
from .native_data import ROOT, GENRE, rank, identity, fixed, untouched_semantic
from .records import sha256


def counterbalance(rows):
    # World number and its family remain unchanged. The ordering bit now cycles
    # independently, so every four consecutive worlds contain the full product.
    return [{**row, 'text_first': bool((row['physics']['number']//2) % 2)} for row in rows]


def untouched_human(cohort):
    prior = json.loads((ROOT / 'reports/JOINT-020/REGISTRATION.json').read_text())
    path = GENRE / ('sealed_'+cohort+'.jsonl')
    excluded = set(prior['finals'][cohort]['groups'])
    excluded.update(r['source_group'] for r in fixed(path, 4096, 'GENRE-017-final-'+cohort))
    excluded.update(r['source_group'] for r in untouched_semantic(cohort)[0])
    groups = defaultdict(list)
    with path.open(encoding='utf-8') as handle:
        for line in handle:
            row = json.loads(line)
            if row['source_group'] not in excluded:
                groups[row['source_group']].append(row)
    selected = sorted(groups, key=lambda g: rank('JOINT-021-final|'+cohort, g))[:128]
    if len(selected) != 128:
        raise ValueError('Fewer than 128 untouched groups; preserve all prior finals')
    return [r for group in selected for r in sorted(groups[group], key=lambda r: r['id'])]


class BalancedJointData(JointData):
    def __init__(self):
        super().__init__()
        self.development = counterbalance(self.development)

    def lesson(self, cycle, batch=16):
        return counterbalance(super().lesson(cycle, batch=batch))

    def finals(self, cohort):
        return counterbalance(paired(untouched_human(cohort), 'JOINT-021-final-'+cohort))

    def shifted(self):
        return counterbalance(paired(untouched_human('matched')[:256], 'JOINT-021-shifted-final', shifted=True))


def registered_sources():
    previous = original_sources()
    previous['protocol_sha256'] = sha256(ROOT / 'protocols/JOINT-021.md')
    previous['finals'] = {}
    for cohort in ('matched', 'mismatched'):
        rows = untouched_human(cohort)
        previous['finals'][cohort] = {'ids': [r['id'] for r in rows],
            'groups': sorted({r['source_group'] for r in rows}), 'source_rows_sha256': identity(rows)}
    previous['repair'] = {'previous_registration': sha256(ROOT / 'reports/JOINT-020/REGISTRATION.json'),
                         'changed': 'chronology only in teaching/development; final worlds and premise groups are fresh',
                         'training_family_order_counts_per_arm': 4096}
    return previous
