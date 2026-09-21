"""Fresh immutable training/development views; keep previous and sealed work."""
from collections import Counter
import json
import os
from pathlib import Path
import sys
import warnings

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.core_teaching import SourceRejection, mathematics_view, programming_view, public_input
from sera_field.records import sha256, write_json

SOURCE = ROOT/'local/CONNECTED-002-human-views-v1'
OUTPUT = ROOT/'local/CORE-022-executable-human-v2'
EXPECTED = {'train': 'b4f1901a7399aa3a51ea2907ee98308892e4a22d7a3aa09a811da1eb107001ed',
    'development': 'db9f86b4165d9adddc24e2878e04c1455983891c8aaae8b7a230764a8b4530a4',
    'sealed': 'bc2d3190295e6c2dc04e0308fdf56d5647d2858728e51d04aaee2e853dd385d2'}


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'): raise SystemExit('Use the local resource supervisor')
    for split, digest in EXPECTED.items():
        if sha256(SOURCE/(split+'.jsonl')) != digest: raise ValueError('Original qualified human bytes changed')
    if OUTPUT.exists(): raise ValueError('Preserve existing preparation; use its manifest or a new reviewed version')
    OUTPUT.mkdir()
    counts = {}; files = {}; group_sets = {}; source_ids = set()
    for split in ('train', 'development'):
        stats = Counter(); group_sets[split] = set()
        with (SOURCE/(split+'.jsonl')).open(encoding='utf-8') as source, \
                (OUTPUT/(split+'.jsonl')).open('x', encoding='utf-8') as output, \
                (OUTPUT/(split+'-outcomes.jsonl')).open('x', encoding='utf-8') as outcomes, \
                (OUTPUT/(split+'-rejected.jsonl')).open('x', encoding='utf-8') as rejected:
            for line in source:
                row = json.loads(line)
                if row['subject'] not in ('mathematics', 'programming'): continue
                stats['inspected:'+row['subject']] += 1
                source_ids.add(row['source_sha256']); group_sets[split].add(row['group'])
                try:
                    with warnings.catch_warnings(record=True) as warning_records:
                        warnings.simplefilter('always')
                        view = mathematics_view(row) if row['subject'] == 'mathematics' else programming_view(row)
                    stats['source_parse_warnings'] += len(warning_records)
                    if warning_records:
                        view['source_parse_warnings'] = [str(w.message) for w in warning_records]
                except (ValueError, ZeroDivisionError, OverflowError, RecursionError) as error:
                    reason = str(error) if isinstance(error, SourceRejection) else type(error).__name__+': '+str(error)
                    stats['rejected:'+row['subject']+':'+reason] += 1
                    rejected.write(json.dumps({'id': row['identity'], 'group': row['group'],
                        'source_sha256': row['source_sha256'], 'reason': reason}, ensure_ascii=False)+'\n')
                    continue
                stats['checked:'+view['track']] += 1
                if not view['programs']:
                    stats['outcome_only:'+view['graph_status']] += 1
                    outcomes.write(json.dumps(view, ensure_ascii=False)+'\n'); continue
                stats['executable:'+view['track']] += 1
                stats['graph_targets'] += len(view['programs'])
                stats['ambiguous_numeric_bindings'] += bool(view.get('binding_ambiguities'))
                stats['checked_calculations'] += len(view.get('checked_calculations', []))
                stats['human_code_assertions'] += len(view.get('cases', []))
                view['learner_input'] = public_input(view)
                output.write(json.dumps(view, ensure_ascii=False)+'\n')
        counts[split] = dict(stats)
        for suffix in ('', '-outcomes', '-rejected'):
            path = OUTPUT/(split+suffix+'.jsonl'); files[path.name] = {'sha256': sha256(path), 'bytes': path.stat().st_size}
    if group_sets['train'] & group_sets['development']: raise ValueError('Original source groups overlap')
    record = {'schema': 'sera-field.core022.executable-human-views.2', 'source_files': EXPECTED,
        'view_directory': OUTPUT.name,
        'preserved_previous': 'CORE-022-executable-human-v1; preserves earlier compiler and view bytes',
        'source_identities': sorted(source_ids), 'files': files, 'counts': counts,
        'group_counts': {k: len(v) for k,v in group_sets.items()}, 'train_development_group_overlap': 0,
        'source_code': {p: sha256(ROOT/p) for p in ('sera_field/core_teaching.py',
            'sera_field/core_programs.py', 'sera_field/core_program_verifier.py', 'scripts/prepare_core022_teaching.py')},
        'sealed_contents_opened': False, 'raw_downloaded_code_executed': False,
        'curriculum_started': False, 'existing_source_views_modified': False,
        'scope': 'Whole numeric instances and scalar human assertions; checked teacher targets are not semantic law proofs.'}
    write_json(OUTPUT/'MANIFEST.json', record)
    write_json(ROOT/'reports/CORE-022/TEACHING_VIEWS.json', record)
    print(json.dumps(record, indent=2))


if __name__ == '__main__': main()
