"""Read-only source-view reconciliation before the complete-core curriculum."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.records import write_json


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024*1024), b''): result.update(chunk)
    return result.hexdigest()


def source_rows(path):
    with path.open(encoding='utf-8') as handle:
        for line in handle:
            yield json.loads(line)


def main():
    legacy = ROOT/'local/CONNECTED-003-data-v1'
    genre = ROOT/'local/HUMAN-GENRE-data-v1'
    lm = json.loads((legacy/'MANIFEST.json').read_text())
    gm = json.loads((genre/'MANIFEST.json').read_text())
    if digest(genre/'MANIFEST.json') != '40e3b405de1a964045ad9af9c2d36b75dc8924bfb54b097334881d989057e9e3':
        raise ValueError('Qualified genre manifest changed')
    checked = []
    # Hashing a sealed file verifies bytes only. No final record or prediction
    # is loaded for curriculum design or model selection.
    for root, entries in ((legacy, lm['files']),
            (genre, {name+'.jsonl': info['sha256'] for name, info in gm['partitions'].items()})):
        for name, expected in entries.items():
            actual = digest(root/name)
            if actual != expected: raise ValueError('Qualified human view changed: '+name)
            checked.append({'view': root.name+'/'+name, 'sha256': actual, 'bytes': (root/name).stat().st_size})
    math = Counter(); source_ids = set(); groups = set()
    for row in source_rows(legacy/'train-math.jsonl'):
        math['rows'] += 1; source_ids.add(row['source']); groups.add(row['group'])
        math['with_supplied_earlier_work'] += int(row['teacher_forced_steps'] > 0)
        math['original_single_step_problem'] += int(row['original_one_step'])
        op, left, right = row['target']
        math['target_uses_first_four_inventory_entries'] += int(left < 4 and right < 4)
        math['maximum_supplied_values'] = max(math['maximum_supplied_values'], len(row['values']))
    math['source_groups'] = len(groups)
    tracks = Counter(); code = Counter(); functions = Counter()
    for row in source_rows(legacy/'train-pairs.jsonl'):
        tracks[row['track']] += 1; source_ids.add(row['source'])
        if row['track'] != 'programming': continue
        code['human_source_records'] += 1
        try: tree = ast.parse(row['answer'])
        except SyntaxError:
            code['not_parseable_as_current_python'] += 1; continue
        found = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        code['parseable_records'] += 1
        for fn in found:
            functions['total_functions'] += 1
            body = [n for n in fn.body if not isinstance(n, ast.Expr) or not isinstance(n.value, ast.Constant)]
            if len(fn.args.args) <= 4 and len(body) == 1 and isinstance(body[0], ast.Return):
                functions['at_most_four_arguments_single_return'] += 1
    summary = {'schema': 'sera-field.core022.intake-audit.1',
        'legacy_manifest': digest(legacy/'MANIFEST.json'), 'genre_manifest': digest(genre/'MANIFEST.json'),
        'source_files_verified': checked, 'human_math': dict(math), 'human_pair_tracks': dict(tracks),
        'human_code': dict(code), 'human_code_functions': dict(functions),
        'source_id_count_in_inspected_training_views': len(source_ids),
        'final_contents_or_predictions_opened': False, 'curriculum_training_started': False,
        'input_scope': 'training-view inventory only; complete final allocation remains prospective',
        'required_curriculum_distinctions': [
            'A mathematics row can be one teacher-forced step rather than an original whole question.',
            'The numeric inventory may include supplied constants and earlier verified results.',
            'Raw human Python is inspected as syntax only; no downloaded code is executed.',
            'Single-return counts do not establish compilability into the finite scalar grammar.',
            'Human language source-pair selection is separate from newly generated explanation.',
            'Earlier opened final cohorts stay preserved; freeze new group-disjoint assessment IDs.']}
    output = ROOT/'reports/CORE-022/INTAKE.json'
    if output.exists() and json.loads(output.read_text()) != summary:
        raise ValueError('Preserve the earlier intake audit before creating a changed record')
    write_json(output, summary)
    print(json.dumps({k:v for k,v in summary.items() if k != 'source_files_verified'}))


if __name__ == '__main__': main()
