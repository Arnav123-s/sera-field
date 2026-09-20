"""Read-only split audit; no model, final scoring or candidate selection."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sera_field.records import sha256, write_json


def normalized(text):
    return ' '.join(re.findall(r'\w+', text.casefold()))


def main():
    data = ROOT / 'local/CONNECTED-003-data-v1'
    manifest = json.loads((data / 'MANIFEST.json').read_text())
    groups, aliases = defaultdict(set), defaultdict(list)
    counts, duplicate_outputs = {}, defaultdict(set)
    for split in ('train', 'development', 'sealed'):
        for kind in ('reading', 'math', 'pairs'):
            path = data / (split + '-' + kind + '.jsonl')
            assert sha256(path) == manifest['files'][path.name]
            count = 0
            with path.open(encoding='utf-8') as source:
                for line in source:
                    row = json.loads(line)
                    groups[row['group']].add(split)
                    content = normalized(row['question'])
                    if kind == 'reading':
                        content += '\n' + normalized(row['context'])
                    elif kind == 'pairs':
                        content += '\n' + normalized(row['answer'])
                        duplicate_outputs[hashlib.sha256(normalized(row['answer']).encode()).hexdigest()].add(split)
                    aliases[hashlib.sha256(content.encode()).hexdigest()].append((row['id'], split))
                    count += 1
            counts[split + '-' + kind] = count
    collisions = [values for values in aliases.values() if len({s for _, s in values}) > 1]
    exclusions = sorted({identity for cluster in collisions for identity, _ in cluster})
    report = {'counts': counts, 'group_conflicts': {k: sorted(v) for k, v in groups.items() if len(v) > 1},
              'cross_partition_exact_input_clusters': len(collisions),
              'excluded_record_ids': exclusions, 'duplicate_output_values_across_partitions': sum(len(x)>1 for x in duplicate_outputs.values()),
              'duplicate_output_scope': 'Common replies/definitions can recur under different inputs; not by itself a duplicated task.',
              'near_duplicate_scope': 'No broad compositional generalization claim; article/dialogue/book-block groups plus exact alias quarantine.',
              'data_manifest_sha256': sha256(data / 'MANIFEST.json'), 'audit_code_sha256': sha256(__file__),
              'model_evaluation_performed': False}
    if report['group_conflicts']:
        raise ValueError('Group overlap must be repaired before teaching')
    target = data / 'SPLIT_AUDIT.json'
    if target.exists():
        raise ValueError('Preserve prior audit; do not silently replace')
    write_json(target, report)
    print(json.dumps({k: v for k, v in report.items() if k != 'excluded_record_ids'}, indent=2))


if __name__ == '__main__':
    main()
