"""Freeze a retention manifest for scripts/sera_ring_diagnostic.py from a saved Field.

Every lesson the Field's log records as proven right, which is also one of `scripts/sera_one.py`'s teaching
builders for the given development seed, is listed with its input digest. The digest is computed by rebuilding the
original task before any live work. The manifest is bound to the Field file's sha256.

    python scripts/ring_retention_manifest.py --field FIELD.pkl --seed 3 --out retention.json
"""
import argparse
import json
import pickle
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.sera_one import teaching                      # noqa: E402
from scripts.sera_ring_diagnostic import input_digest, sha256, write_json   # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--field', required=True)
    ap.add_argument('--seed', type=int, choices=(1, 2, 3), required=True)
    ap.add_argument('--out', required=True)
    a = ap.parse_args()
    with open(a.field, 'rb') as f:
        field = pickle.load(f)
    proven = [r['task'] for r in getattr(field, 'log', []) if r.get('verdict') == 'proven right']
    builders = dict(teaching(a.seed))
    lessons, skipped = [], []
    for name in dict.fromkeys(proven):                        # each lesson once, in the order it was proven
        if name not in builders:
            skipped.append(name)
            continue
        lessons.append(dict(seed=a.seed, source='teaching', name=name, input_sha256=input_digest(builders[name]())))
    write_json(a.out, dict(pre_field_sha256=sha256(a.field), lessons=lessons))
    print(f'{len(lessons)} lessons frozen; not teaching builders of seed {a.seed}: {skipped}')


if __name__ == '__main__':
    main()
