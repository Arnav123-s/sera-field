"""Compare re-run result files with saved ones, value by value.

Used to check that the lab reproduces its committed results after a change of
environment (for example the move to the lab's own .venv). Only the wall-clock
field `seconds` is ignored.

    python scripts/compare_results.py legacy\ball\ball-results scratch/repro/ball-seed1
"""
import json
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
IGNORED = {'seconds'}


def diffs(a, b, path='', out=None):
    out = [] if out is None else out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k in IGNORED:
                continue
            if k not in a or k not in b:
                out.append(f'{path}/{k}: only in {"new" if k in b else "saved"}')
            else:
                diffs(a[k], b[k], f'{path}/{k}', out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f'{path}: length {len(a)} vs {len(b)}')
        for i, (x, y) in enumerate(zip(a, b)):
            diffs(x, y, f'{path}[{i}]', out)
    elif isinstance(a, float) or isinstance(b, float):
        if not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
            out.append(f'{path}: {a!r} vs {b!r}')
        elif not (a == b or (math.isnan(a) and math.isnan(b)) or abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))):
            out.append(f'{path}: {a!r} vs {b!r}')
    elif a != b:
        out.append(f'{path}: {a!r} vs {b!r}')
    return out


def main():
    saved, new = Path(sys.argv[1]), Path(sys.argv[2])
    files = sorted(new.glob('*.json'))
    if not files:
        print(f'no result files in {new}')
        sys.exit(1)
    bad = 0
    for f in files:
        ref = saved / f.name
        if not ref.exists():
            print(f'MISSING saved file for {f.name}')
            bad += 1
            continue
        d = diffs(json.loads(ref.read_text(encoding='utf-8')), json.loads(f.read_text(encoding='utf-8')))
        if d:
            bad += 1
            print(f'DIFF {f.name}: {len(d)} differences, first ones:')
            for line in d[:5]:
                print(f'    {line}')
        else:
            print(f'SAME {f.name}')
    print('ALL SAME' if not bad else f'{bad} of {len(files)} files differ')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
