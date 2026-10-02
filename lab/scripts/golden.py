"""Record and compare deterministic truth-layer results across code changes."""

import argparse
import json
import math
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from ccops5.core import grammar, truth, checker, worlds


FORCES = ('rubbing', 'spring', 'water drag', 'swing', 'x*v force', 'motor', 'none')
SECTIONS = ('Q', 'mle', 'certificates', 'alarm', 'checker')


def plain(value):
    """Convert result values to strict JSON, including nonfinite floats."""
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [plain(v) for v in value]
    if isinstance(value, float):
        if math.isnan(value):
            return 'nan'
        if math.isinf(value):
            return 'inf' if value > 0 else '-inf'
    return value


def certificate_data(cert):
    return {
        'rivals': {grammar.name(f): v for f, v in cert.rivals.items()},
        'nested': {grammar.name((idea,)): bounds for idea, bounds in cert.nested.items()},
        'band': cert.band,
        'adequacy': cert.adequacy,
        'scope': cert.scope,
        'accepted': cert.accepted,
        'reasons': cert.reasons,
    }


def world_record(item):
    index, force = item
    w = worlds.make(1, force, index=950 + index, situations=5, tricks=0.05)
    ledger = truth.Ledger(grammar.space(), w.sigma)
    scores = []
    for throw in w.throws:
        ledger.add(throw)
        scores.append({grammar.name(f): ledger.Q[f] for f in ledger.families})
    mle = {grammar.name(f): ledger.mle(f).loglik for f in ledger.families}
    best = ledger.best_family()
    certificates = {}
    targets = [('best', best)]
    if w.truth is not None:
        targets.append(('truth', w.truth))
    best_half = None
    for label, family in targets:
        certificates[label] = {'family': grammar.name(family)}
        for eps in (0.1, 0.5):
            cert = truth.certify(ledger, family, eps)
            certificates[label][str(eps)] = certificate_data(cert)
            if label == 'best' and eps == 0.5:
                best_half = cert
    accepted, reasons = checker.check(best_half, ledger.throws, w.sigma)
    return plain({
        'force': force,
        'Q': scores,
        'mle': mle,
        'certificates': certificates,
        'alarm': truth.something_else(ledger, best),
        'checker': {'accepted': accepted, 'reasons': reasons},
    })


def record(path):
    started = time.perf_counter()
    with Pool(7) as pool:
        rows = pool.map(world_record, enumerate(FORCES))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({'worlds': rows}, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(f'Recorded {path} in {time.perf_counter() - started:.2f}s')


def compare(a_path, b_path, tol):
    a = json.loads(a_path.read_text(encoding='utf-8'))
    b = json.loads(b_path.read_text(encoding='utf-8'))
    structural = []
    stats = {section: {'abs': (0.0, ''), 'rel': (0.0, '')} for section in SECTIONS}

    def walk(left, right, path, section=None):
        if isinstance(left, dict) and isinstance(right, dict):
            left_keys, right_keys = set(left), set(right)
            for key in sorted(left_keys - right_keys):
                structural.append(f'{path}.{key}: missing from B')
            for key in sorted(right_keys - left_keys):
                structural.append(f'{path}.{key}: missing from A')
            for key in sorted(left_keys & right_keys):
                walk(left[key], right[key], f'{path}.{key}', key if key in SECTIONS else section)
        elif isinstance(left, list) and isinstance(right, list):
            if len(left) != len(right):
                structural.append(f'{path}: length {len(left)} != {len(right)}')
            for i, (x, y) in enumerate(zip(left, right)):
                walk(x, y, f'{path}[{i}]', section)
        elif type(left) is bool or type(right) is bool:
            if type(left) is not type(right) or left != right:
                structural.append(f'{path}: {left!r} != {right!r}')
        elif isinstance(left, (int, float)) and isinstance(right, (int, float)):
            absolute = abs(left - right)
            relative = absolute / max(1, abs(left), abs(right))
            if section in stats:
                for kind, value in (('abs', absolute), ('rel', relative)):
                    if value > stats[section][kind][0]:
                        stats[section][kind] = (value, path)
        elif type(left) is not type(right) or left != right:
            structural.append(f'{path}: {left!r} != {right!r}')

    walk(a, b, '$')
    for difference in structural:
        print(f'STRUCTURAL {difference}')
    for section in SECTIONS:
        absolute, abs_path = stats[section]['abs']
        relative, rel_path = stats[section]['rel']
        print(f'{section}: max abs {absolute:.12g} at {abs_path or "(none)"}; '
              f'max rel {relative:.12g} at {rel_path or "(none)"}')
    largest = max(stats[section]['rel'][0] for section in SECTIONS)
    passed = not structural and largest <= tol
    print(f'{"No difference" if passed and largest == 0 else "Differences found" if not passed else "Within tolerance"}: '
          f'{len(structural)} structural, max relative {largest:.12g}, tolerance {tol:.12g}')
    return 0 if passed else 1


def main():
    if os.environ.get('PYTHONHASHSEED') != '0':
        raise SystemExit('PYTHONHASHSEED=0 is required')
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    rec = commands.add_parser('record')
    rec.add_argument('out', type=Path)
    comp = commands.add_parser('compare')
    comp.add_argument('a', type=Path)
    comp.add_argument('b', type=Path)
    comp.add_argument('--tol', type=float, default=1e-9)
    args = parser.parse_args()
    if args.command == 'record':
        record(args.out)
        return 0
    if not math.isfinite(args.tol) or args.tol < 0:
        parser.error('--tol must be finite and nonnegative')
    return compare(args.a, args.b, args.tol)


if __name__ == '__main__':
    raise SystemExit(main())
