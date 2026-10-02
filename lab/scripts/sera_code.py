"""SERA's proven ideas as Python (2026-09-30; the author: "I want it to be able to code"; plan 7.11 step 5, its first
half): the observer's printer (sera.pyprint) writes each idea SERA proved - its own programs, in its own language -
as a Python function named by SERA's word for it. The printing is ours; the programs are SERA's.

  python scripts/sera_code.py --field F [--out ideas.py]
"""
import argparse
import os
import sys
from pathlib import Path

os.environ.setdefault('CCOPS5_SHAPES', 'library')
os.environ.setdefault('CCOPS5_CLAIM', 'functional')
os.environ.setdefault('CCOPS5_BAND', 'claim')
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sera import pyprint as PP  # noqa: E402
import sera_converse as SC  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--field', required=True)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    src = PP.module(SC.load(a.field))
    compile(src, '<sera>', 'exec')                      # it is Python
    if a.out:
        Path(a.out).write_text(src, encoding='utf-8')
    print(src)


if __name__ == '__main__':
    main()
