"""Complete the frozen fresh-owner course; never load a predecessor's weights."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import torch
from sera_field.native_data import NativeData, source_contract, untouched_semantic, physical_episode, identity
from sera_field.native_training import (STUDY, ARMS, TOTAL, train, assess, source_files,
    read, load_native, selected_ablation)
from sera_field.records import sha256, write_json

REPORT = ROOT / 'reports/NATIVE-019'
ROUTES = ('native', 'delayed', 'trace', 'initial', 'erase_history', 'no_bulk', 'equal_rates', 'no_imagination')


def cohorts():
    return {**{name: ('semantic', untouched_semantic(name)[0]) for name in ('matched', 'mismatched')},
        'physics': ('physics', [physical_episode('NATIVE-019-final', i) for i in range(512)]),
        'physics_shifted': ('physics', [physical_episode('NATIVE-019-shifted-final', i, shifted=True) for i in range(512)])}


def registration():
    if not all((STUDY / arm / 'COMPLETE.json').exists() for arm in ARMS):
        raise ValueError('Finish every matched arm before any native final prediction')
    selected = {arm: read(STUDY / arm / 'SELECTION.json') for arm in ARMS}
    return {'selected': selected, 'initial': read(STUDY / 'native/INITIAL.json'),
        'sources': read(STUDY / 'SOURCES.json'),
        'cohorts': {name: {'kind': kind, 'ids': [r['id'] for r in rows],
                          'n': len(rows), 'source_rows_sha256': identity(rows)}
                    for name, (kind, rows) in cohorts().items()},
        'all_training_finished_before_finals': True}


def route_owner(route):
    base = route if route in ARMS else 'native'
    pointer = 'INITIAL.json' if route == 'initial' else 'SELECTION.json'
    owner, selected, _ = load_native(STUDY / base, pointer=pointer)
    ablation = selected_ablation(base, selected['step']) if route in ARMS else (None if route == 'initial' else route)
    return owner, selected, True, ablation


def final(data, *, replay=False):
    reg = registration(); path = REPORT / 'FINAL_REGISTRATION.json'
    if path.exists():
        if read(path) != reg: raise ValueError('Frozen native final registration changed')
    elif replay: raise ValueError('Register original finals before replay')
    else: write_json(path, reg)
    equality = {}
    for route in ('native',) if replay else ROUTES:
        owner, selected, memory, ablation = route_owner(route)
        for name, (kind, rows) in cohorts().items():
            root = STUDY / ('replay' if replay else 'final') / route / name
            root.mkdir(parents=True, exist_ok=True)
            summary_path = root / 'RESULTS.json'; cases_path = root / 'cases.jsonl'
            if summary_path.exists():
                result = read(summary_path)
                if (result['cases_sha256'] != sha256(cases_path) or result['checkpoint'] != selected
                        or result['registration_sha256'] != sha256(path)):
                    raise ValueError('Completed native result identity changed')
            else:
                metrics, cases = assess(owner, data, kind, rows, memory=memory, ablation=ablation)
                encoded = ''.join(json.dumps(case, allow_nan=False) + '\n' for case in cases)
                if cases_path.exists() and cases_path.read_text(encoding='utf-8') != encoded:
                    raise ValueError('Preserve the interrupted final predictions; fresh execution differed')
                if not cases_path.exists(): cases_path.write_text(encoded, encoding='utf-8')
                result = {'route': route, 'cohort': name, 'metrics': metrics, 'checkpoint': selected,
                    'memory': memory, 'ablation': ablation, 'cases_sha256': sha256(cases_path),
                    'registration_sha256': sha256(path)}
                write_json(summary_path, result)
            if replay:
                original = read(STUDY / 'final' / route / name / 'RESULTS.json')
                equality[name] = result == original
            print(json.dumps({'native_final': route, 'cohort': name, 'replay': replay, 'metrics': result['metrics']}), flush=True)
    if replay:
        write_json(REPORT / 'REPLAY.json', {'fresh_process': True, 'checks': equality, 'exact': all(equality.values())})
        if not all(equality.values()): raise ValueError('Native final replay differs')


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'): raise SystemExit('Use the numerical supervisor')
    parser = argparse.ArgumentParser(); parser.add_argument('--replay', action='store_true'); args = parser.parse_args()
    torch.set_num_threads(1)
    data = NativeData()
    if args.replay:
        final(data, replay=True); return
    if not (ROOT / 'reports/GENRE-017/REPORT.md').exists():
        raise ValueError('Preserve the earlier director; finish its owned sequence first')
    sources = {**source_contract(), 'implementation': source_files(),
               'runner_sha256': sha256(__file__)}
    if (STUDY / 'SOURCES.json').exists():
        if read(STUDY / 'SOURCES.json') != sources: raise ValueError('Existing native sources changed')
    else: write_json(STUDY / 'SOURCES.json', sources)
    for arm in ARMS: train(arm, data, sources)
    initial = [read(STUDY / arm / 'INITIAL.json')['weights'] for arm in ARMS]
    if len(set(initial)) != 1: raise ValueError('Matched fresh initialization differs')
    final(data)
    subprocess.run([sys.executable, '-X', 'utf8', '-u', __file__, '--replay'], check=True, cwd=ROOT)


if __name__ == '__main__': main()
