"""Preserved-course audit: cross history order independently of physical family."""
from collections import Counter
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import torch
from sera_field.joint_data import JointData
from sera_field.joint_training import STUDY, evaluate
from sera_field.native_training import load_native
from sera_field.native_data import physical_episode, identity
from sera_field.records import write_json


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use the numerical supervisor')
    torch.set_num_threads(1)
    counts = Counter(); number = 0
    with (STUDY / 'credited/training.jsonl').open() as handle:
        for line in handle:
            for case in json.loads(line)['cases']:
                physical = physical_episode('JOINT-020-training', number)
                if physical['id'] != case['physical_id']:
                    raise ValueError('Training physical identity differs')
                family = 'quadratic' if physical['teacher_only']['quadratic'] else 'linear'
                counts[family+'|'+case['chronology']] += 1
                number += 1
    data = JointData(); results = {}
    for arm, pointer in (('credited', 'SELECTION.json'), ('withheld', 'SELECTION.json'), ('initial', 'INITIAL.json')):
        owner, selected, _ = load_native(STUDY / ('withheld' if arm == 'withheld' else 'credited'), pointer=pointer)
        results[arm] = {'checkpoint': selected, 'orders': {}}
        for first in (False, True):
            rows = [{**r, 'text_first': first, 'id': identity(['JOINT-020-order-diagnosis', r['id'], first])}
                    for r in data.development]
            metrics, _ = evaluate(owner, rows)
            results[arm]['orders']['text_first' if first else 'measurements_first'] = metrics
    expected = {family+'|'+order for family in ('linear', 'quadratic')
                for order in ('text_first', 'measurements_first')}
    independent = expected == set(counts)
    record = {'training_contingency': dict(counts), 'all_family_order_cells_taught': independent,
              'development_crossed_orders': results,
              'finding': 'The original deterministic schedule confounded order with the two physical families.',
              'scope': 'Post-training design diagnosis on development worlds; no weights, selection or final results changed.',
              'next_required_repair': 'Counterbalance physical family and chronology before a fresh matched teaching/evaluation protocol.'}
    write_json(ROOT / 'reports/JOINT-020/ORDER_DIAGNOSIS.json', record)
    print(json.dumps({'family_order_training_cells': dict(counts), 'all_cells_taught': independent}), flush=True)


if __name__ == '__main__':
    main()
