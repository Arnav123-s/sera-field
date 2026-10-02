"""The evidence cache changes no number: compare School lives run with the cache off, cold and warm.

    python school_run.py --quick --cache none --results <base>/off
    python school_run.py --quick --cache <base>/cache --results <base>/cold
    python school_run.py --quick --cache <base>/cache --results <base>/warm
    python scripts/cache_equivalence.py <base>
"""
import json, sys
from pathlib import Path

base = Path(sys.argv[1])
DROP = {'seconds', 'minutes', 'evidence', 'commit'}


def clean(x):
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items() if k not in DROP}
    if isinstance(x, list):
        return [clean(v) for v in x]
    return x


ok = True
for life in sorted((base / 'off').glob('life-*.json')):
    ref = clean(json.loads(life.read_text(encoding='utf-8')))
    for other in ('cold', 'warm'):
        p = base / other / life.name
        raw = json.loads(p.read_text(encoding='utf-8'))
        same = clean(raw) == ref
        ok &= same
        print(f'{life.stem:28s} off vs {other:4s}: {"IDENTICAL" if same else "DIFFERENT"}  cache {raw["evidence"]}  '
              f'worlds {len(ref["worlds"])}')
print('ALL IDENTICAL' if ok else 'MISMATCH')
