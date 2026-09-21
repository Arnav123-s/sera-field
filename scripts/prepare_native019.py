"""Read-only source reconciliation; no model import or numerical learner work."""
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.native_data import source_contract, GENRE
from sera_field.records import write_json, sha256


def main():
    path = ROOT / 'reports/NATIVE-019/SOURCE_PREPARATION.json'
    if path.exists(): raise ValueError('Preserve the already prepared native source record')
    wall, cpu = time.perf_counter(), time.process_time()
    contract = source_contract()
    train = set(json.loads((GENRE / 'train-groups.json').read_text()))
    development = set(json.loads((GENRE / 'development-groups.json').read_text()))
    final = {key: set(value['groups']) for key, value in contract['source_group_selection'].items()}
    groups = {'train': train, 'development': development, **final}
    overlap = {a + ':' + b: len(groups[a] & groups[b]) for i, a in enumerate(groups) for b in list(groups)[i+1:]}
    if any(overlap.values()): raise ValueError('Native source groups cross partitions')
    result = {'contract': contract, 'group_overlaps': overlap, 'producer_sha256': sha256(__file__),
        'model_imports': False, 'predictions_computed': 0,
        'wall_seconds': time.perf_counter()-wall, 'cpu_seconds': time.process_time()-cpu}
    write_json(path, result)
    print(json.dumps({'source_prepared': True, 'counts': {k: {'groups': len(v['groups']), 'rows': v['rows'],
        'eligible_groups': v['eligible_groups']} for k, v in contract['source_group_selection'].items()},
        'group_overlaps': overlap, 'wall_seconds': result['wall_seconds']}))


if __name__ == '__main__': main()
