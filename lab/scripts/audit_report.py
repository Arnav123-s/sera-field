"""Trace report numbers to files cited in the same table row, bullet, or paragraph."""

import argparse
import glob
import json
import re
from pathlib import Path


BACKTICK = re.compile(r'`([^`]+)`')
# a number may end a sentence ("937."): only a word character or a decimal part may not follow it
NUMBER = re.compile(r'(?<![\w.])[-+]?\d+(?:,\d{3})*(?:\.\d+)?%?(?!\w|\.\d)')
PAIR = re.compile(r'(?<![\w.])(\d+(?:,\d{3})*)\s+(?:of)\s+(\d+(?:,\d{3})*)(?!\w|\.\d)|(?<![\w.])(\d+(?:,\d{3})*)/(\d+(?:,\d{3})*)(?!\w|\.\d)', re.I)
EXEMPT = [
    re.compile(r'\b\d{4}-\d{1,2}-\d{1,2}\b'),
    re.compile(r'\b\d{1,2}:\d{2}(?::\d{2})?\b'),
    re.compile(r'\b(?:seed|seeds|batch|batches)\s+\d+(?:\s*[-–]\s*\d+)?\b', re.I),
    re.compile(r'\b(?:B\d+-\d+|[BCLMST]\d+[a-z]?)\b', re.I),
    re.compile(r'(?:§|Â§)\s*\d+(?:\.\d+)*'),
    re.compile(r'\b(?:section|chapter)\s+\d+(?:\.\d+)*\b', re.I),
    re.compile(r'\b(?=[0-9a-f]{7,40}\b)(?=[0-9a-f]*[a-f])[0-9a-f]+\b', re.I),
]
BULLET = re.compile(r'^\s*(?:[-*+] |\d+[.)] )')


def units(report):
    """Yield (first line, combined text) without counting sub-bullets twice."""
    lines = report.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or stripped == '---':
            index += 1
            continue
        start = index + 1
        if stripped.startswith('|'):
            if not re.fullmatch(r'[|:\s-]+', stripped):
                yield start, stripped
            index += 1
            continue
        block = [line]
        index += 1
        if BULLET.match(line):
            indent = len(line) - len(line.lstrip())
            while index < len(lines):
                next_line = lines[index]
                next_stripped = next_line.strip()
                if not next_stripped:
                    if index + 1 < len(lines) and lines[index + 1].strip() and (
                            len(lines[index + 1]) - len(lines[index + 1].lstrip()) > indent):
                        index += 1
                        continue
                    break
                next_indent = len(next_line) - len(next_line.lstrip())
                if next_indent <= indent or next_stripped.startswith('#'):
                    break
                block.append(next_line)
                index += 1
        else:
            while index < len(lines):
                next_line = lines[index]
                if not next_line.strip() or next_line.lstrip().startswith(('#', '|')) or BULLET.match(next_line):
                    break
                block.append(next_line)
                index += 1
        yield start, '\n'.join(block)


def _masked(text):
    """Keep offsets while hiding inline code and exempt expressions."""
    chars = list(text)
    for pattern in [BACKTICK, *EXEMPT]:
        visible = ''.join(chars)
        for match in pattern.finditer(visible):
            chars[match.start():match.end()] = ' ' * (match.end() - match.start())
    # Numbered Markdown list markers are structure, not claims.
    visible = ''.join(chars)
    for match in re.finditer(r'(?m)^\s*\d+[.)](?=\s)', visible):
        chars[match.start():match.end()] = ' ' * (match.end() - match.start())
    return ''.join(chars)


def numbers(text):
    visible = _masked(text)
    pairs = list(PAIR.finditer(visible))
    found = [(match.start(), match.group(), tuple(group for group in match.groups() if group is not None))
             for match in pairs]
    for match in NUMBER.finditer(visible):
        if not any(pair.start() <= match.start() < pair.end() for pair in pairs):
            found.append((match.start(), match.group(), None))
    return [(label, parts) for _, label, parts in sorted(found)]


def cited_files(text, root):
    root = root.resolve()
    found = set()
    for token in BACKTICK.findall(text):
        # A path is a single backtick token; commands and prose are not citations.
        if not token or token.startswith('-'):
            continue
        candidate = Path(token)
        if not candidate.is_absolute():
            candidate = root / candidate
        for name in glob.glob(str(candidate)):
            path = Path(name).resolve()
            if path.is_file() and path.is_relative_to(root):
                found.add(path)
    return sorted(found)


def _json_values(data):
    if isinstance(data, bool):
        return []
    if isinstance(data, (int, float)):
        return [data]
    if isinstance(data, dict):
        values = [len(data)]
        for key in sorted(data):
            values.extend(_json_values(data[key]))
        return values
    if isinstance(data, list):
        values = [len(data), sum(item is True for item in data), sum(item is False for item in data)]
        for item in data:
            values.extend(_json_values(item))
        return values
    return []


def _same_number(label, value):
    label = label.replace(',', '')
    percent = label.endswith('%')
    if percent:
        label = label[:-1]
        value *= 100
    digits = len(label.split('.', 1)[1]) if '.' in label else 0
    if digits == 0 and not percent:
        return value == int(label)
    return f'{value:.{digits}f}' == label.lstrip('+')


def _text_has_number(text, label):
    # Whole tokens prevent a claimed 2 from matching 20 or 2.5.
    return re.search(r'(?<![\w.])' + re.escape(label) + r'(?![\w.])', text) is not None


def _file_matches(path, label, parts, cache):
    if path not in cache:
        source = path.read_text(encoding='utf-8', errors='replace')
        try:
            data = json.loads(source) if path.suffix.lower() == '.json' else None
        except json.JSONDecodeError:
            data = None
        cache[path] = (source, _json_values(data) if data is not None else [])
    source, values = cache[path]
    labels = parts if parts else (label,)
    return all(_text_has_number(source, item) or any(_same_number(item, value) for value in values)
               for item in labels)


def audit(report, root):
    cache = {}
    rows = []
    for line, unit in units(report):
        cited = cited_files(unit, root)
        for label, parts in numbers(unit):
            matched = next((path for path in cited if _file_matches(path, label, parts, cache)), None)
            status = 'traced' if matched else 'untraced' if cited else 'no-source'
            rows.append((line, label, status, matched.relative_to(root.resolve()).as_posix() if matched else ''))
    return rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--warn-only', action='store_true')
    args = parser.parse_args(argv)
    rows = audit(args.report.read_text(encoding='utf-8'), args.root)
    print('| Unit line | Number | Status | File |')
    print('|---:|---:|---|---|')
    for line, label, status, path in rows:
        print(f'| {line} | {label} | {status} | {path} |')
    counts = {name: sum(row[2] == name for row in rows) for name in ('traced', 'untraced', 'no-source')}
    print(f"Totals: {len(rows)} numbers; {counts['traced']} traced; "
          f"{counts['untraced']} untraced; {counts['no-source']} no-source")
    return 0 if args.warn_only or not (counts['untraced'] or counts['no-source']) else 1


if __name__ == '__main__':
    raise SystemExit(main())
