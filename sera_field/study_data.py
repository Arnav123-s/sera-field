"""Human teaching views with full input coverage and label-separated targets."""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import ast
import hashlib
import json
from pathlib import Path
import re
import zipfile

from .records import sha256, write_json

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r"\d+(?:[,.]\d+)*|[^\W\d_]+(?:['’][^\W\d_]+)*|[^\w\s]", re.UNICODE)
NUMBER = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?")
VOCAB = 16384
OPS = ('+', '-', '*', '/')


@lru_cache(maxsize=100000)
def word_id(word):
    return 1 + int.from_bytes(hashlib.blake2s(word.casefold().encode(), digest_size=4).digest(), 'little') % (VOCAB - 1)


def tokens(text):
    return [word_id(m.group()) for m in TOKEN.finditer(text)] or [1]


def sentences(text):
    # Every non-whitespace character remains in exactly one source slice.
    ends = [m.end() for m in re.finditer(r'[.!?](?:["”\']?)(?=\s+[A-Z0-9“"\'])|\n\s*\n', text)]
    starts = [0] + ends
    slices = [(s, e) for s, e in zip(starts, ends + [len(text)]) if text[s:e].strip()]
    return slices or [(0, len(text))]


def number_pool(text, previous=()):
    values = []
    for raw in [m.group().replace(',', '') for m in NUMBER.finditer(text)] + list(previous) + ['1', '2', '10', '100', '0.5']:
        value = str(Fraction(raw))
        if value not in values:
            values.append(value)
    return values


def binary_annotation(expression):
    try:
        node = ast.parse(expression.replace(',', ''), mode='eval').body
        if not isinstance(node, ast.BinOp) or type(node.op) not in (ast.Add, ast.Sub, ast.Mult, ast.Div):
            return None
        def constant(n):
            if isinstance(n, ast.Constant) and type(n.value) in (int, float):
                return Fraction(str(n.value))
            if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
                return -constant(n.operand)
            raise ValueError('Not a literal')
        a, b = constant(node.left), constant(node.right)
        return (ast.Add, ast.Sub, ast.Mult, ast.Div).index(type(node.op)), str(a), str(b)
    except (ValueError, SyntaxError, TypeError, ZeroDivisionError):
        return None


def expression_value(op, a, b):
    a, b = Fraction(a), Fraction(b)
    if op == 0:
        return a + b
    if op == 1:
        return a - b
    if op == 2:
        return a * b
    if op == 3:
        return a / b
    raise ValueError('Unknown operation')


def canonical_expression(op, a, b):
    a, b = str(Fraction(a)), str(Fraction(b))
    if op in (0, 2):
        a, b = sorted((a, b))
    return json.dumps([OPS[op], a, b], separators=(',', ':'))


def reading_view(row):
    teacher = row['teacher']
    context = row['prompt'][:teacher['context_length']]
    spans = sentences(context)
    valid = []
    for i, (s, e) in enumerate(spans):
        if any(s <= a['answer_start'] and a['answer_start'] + len(a['text']) <= e for a in teacher['answers']):
            valid.append(i)
    return {'id': row['identity'], 'group': row['group'], 'source': row['source_sha256'],
            'track': 'human_reading', 'question': teacher['question'], 'context': context,
            'options': [context[s:e].strip() for s, e in spans], 'spans': spans,
            'targets': valid, 'answers': teacher['answers']}


def math_views(row):
    annotations = list(re.finditer(r'<<([^<>]+)>>', row['teacher']['worked_solution']))
    previous, trace = [], []
    for step, match in enumerate(annotations):
        left, sep, right = match.group(1).rpartition('=')
        parsed = binary_annotation(left) if sep else None
        pool = number_pool(row['prompt'], previous)
        if parsed and parsed[1] in pool and parsed[2] in pool:
            op, a, b = parsed
            try:
                value = expression_value(op, a, b)
                if value != Fraction(right.replace(',', '')):
                    raise ValueError('Human annotation arithmetic mismatch')
                yield {'id': row['identity'] + ':' + str(step), 'group': row['group'],
                       'source': row['source_sha256'], 'track': 'human_mathematics',
                       'question': row['prompt'] + ('\nVerified earlier work: ' + '; '.join(trace) if trace else ''),
                       'values': pool, 'target': [op, pool.index(a), pool.index(b)], 'answer': str(value),
                       'teacher_forced_steps': step, 'original_one_step': len(annotations) == 1}
            except (ZeroDivisionError, ValueError):
                pass
        if sep:
            try:
                previous.append(str(Fraction(right.replace(',', ''))))
                trace.append(match.group(1))
            except ValueError:
                pass


def _group_split(group):
    n = int(hashlib.sha256(('CONNECTED-003-books-v1\n' + group).encode()).hexdigest()[:8], 16) % 10
    return 'train' if n < 8 else 'development' if n == 8 else 'sealed'


def human_pairs():
    records = json.loads((ROOT / 'local/CURRICULUM_SOURCE_CHECK.json').read_text())
    for record in records:
        name = record['source']
        if name not in {'grammar', 'plato', 'descartes', 'calculus', 'webster', 'dailydialog'}:
            continue
        path = Path(record['path'])
        if sha256(path) != record['sha256']:
            raise ValueError('Human source changed: ' + name)
        base = {'source': record['sha256'], 'origin': 'human', 'track': name}
        if name == 'dailydialog':
            with zipfile.ZipFile(path) as archive:
                # Keep original train/development/test boundaries, one dialogue per group.
                for info in archive.infolist():
                    if info.filename.endswith('.zip'):
                        import io
                        with zipfile.ZipFile(io.BytesIO(archive.read(info))) as inner:
                            for item in inner.infolist():
                                if item.filename.endswith('.txt') and Path(item.filename).name.startswith('dialogues_') and not any(x in item.filename for x in ('act', 'emotion')):
                                    split = 'development' if 'validation' in item.filename else 'sealed' if 'test' in item.filename else 'train'
                                    for i, line in enumerate(inner.read(item).decode('utf-8').splitlines()):
                                        turns = [t.strip() for t in line.split('__eou__') if t.strip()]
                                        group = name + ':' + item.filename + ':' + str(i)
                                        for j in range(len(turns) - 1):
                                            yield {**base, 'id': group + ':' + str(j), 'group': group, 'split': split,
                                                   'question': turns[j], 'answer': turns[j + 1]}
            continue
        text = path.read_text(encoding='utf-8-sig')
        start = re.search(r'\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK[^\n]*\n', text)
        end = re.search(r'\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK', text)
        offset = start.end() if start else 0
        text = text[offset:end.start() if end else len(text)]
        if name == 'webster':
            entries = list(re.finditer(r'(?m)^([A-Z][A-Z ;,\-\'()]{1,70})\r?$', text))
            for i, entry in enumerate(entries):
                body = text[entry.end():entries[i+1].start() if i+1 < len(entries) else len(text)].strip()
                if len(body) < 30:
                    continue
                question = entry.group(1).strip().casefold()
                group = name + ':' + question
                # Entire entry is the target; long entries are not prefix-clipped.
                yield {**base, 'id': group, 'group': group, 'split': _group_split(group),
                       'question': question, 'answer': body, 'offset': offset + entry.start()}
        else:
            for i, match in enumerate(re.finditer(r'\S[^\n]*(?:\n(?!\s*\n)[^\n]+)*', text)):
                paragraph = match.group()
                slices = sentences(paragraph)
                if len(slices) < 2 or len(paragraph) < 90:
                    continue
                cut = slices[0][1]
                group = name + ':block:' + str(i // 32)
                yield {**base, 'id': name + ':' + str(i), 'group': group, 'split': _group_split(group),
                       'question': paragraph[:cut].strip(), 'answer': paragraph[cut:].strip(),
                       'offset': offset + match.start()}


def prepare(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    root = ROOT / 'local/CONNECTED-002-human-views-v1'
    source_manifest = json.loads((root / 'MANIFEST.json').read_text())
    counts, rejected = Counter(), Counter()
    handles = {(s, kind): (output / (s + '-' + kind + '.jsonl')).open('x', encoding='utf-8')
               for s in ('train', 'development', 'sealed') for kind in ('reading', 'math', 'pairs')}
    def emit(split, kind, row):
        row['split'] = split
        handles[split, kind].write(json.dumps(row, ensure_ascii=False) + '\n')
        counts[split + ':' + row['track']] += 1
    try:
        for split in ('train', 'development', 'sealed'):
            path = root / (split + '.jsonl')
            if sha256(path) != source_manifest['files'][split]['sha256']:
                raise ValueError('Frozen partition changed')
            with path.open(encoding='utf-8') as source:
                for line in source:
                    row = json.loads(line)
                    if row['subject'] == 'language_reading':
                        view = reading_view(row)
                        if view['targets']:
                            emit(split, 'reading', view)
                        else:
                            rejected[split + ':answer_crosses_sentence_boundary'] += 1
                    elif row['subject'] == 'mathematics':
                        views = list(math_views(row))
                        for view in views:
                            emit(split, 'math', view)
                        if not views:
                            rejected[split + ':no_binary_teaching_step'] += 1
                    elif row['subject'] == 'programming':
                        emit(split, 'pairs', {'id': row['identity'], 'group': row['group'],
                                             'source': row['source_sha256'], 'origin': 'human',
                                             'track': 'programming', 'question': row['prompt'],
                                             'answer': row['teacher']['reference_program']})
        for row in human_pairs():
            emit(row['split'], 'pairs', row)
    finally:
        for handle in handles.values():
            handle.close()
    manifest = {'schema': 'sera-field.connected-003.data.1', 'counts': dict(counts),
                'excluded_transformations': dict(rejected), 'original_partition_manifest': sha256(root / 'MANIFEST.json'),
                'files': {p.name: sha256(p) for p in sorted(output.glob('*.jsonl'))},
                'transform_sha256': sha256(__file__), 'finals_inspected_for_selection': False,
                'human_targets_are_separate_from_inputs': True}
    write_json(output / 'MANIFEST.json', manifest)
    return manifest


def load_records(root, split, kind):
    root = Path(root)
    manifest = json.loads((root / 'MANIFEST.json').read_text())
    path = root / (split + '-' + kind + '.jsonl')
    if sha256(path) != manifest['files'][path.name]:
        raise ValueError('Teaching/evaluation view changed')
    audit_path = root / 'SPLIT_AUDIT.json'
    excluded = set(json.loads(audit_path.read_text())['excluded_record_ids']) if audit_path.exists() else set()
    with path.open(encoding='utf-8') as source:
        return [row for line in source if (row := json.loads(line))['id'] not in excluded]


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = prepare(args.output)
    print(json.dumps({k: v for k, v in result.items() if k != 'files'}, indent=2))
