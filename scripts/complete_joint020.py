"""Frozen teaching, then independent final/replay processes for the mixed owner."""
import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import torch
from sera_field.joint_data import JointData, registered_sources
from sera_field.joint_training import STUDY, train, evaluate
from sera_field.native_data import identity, physical_episode
from sera_field.native_training import source_files, load_native, assess, read
from sera_field.records import write_json, sha256

REPORT = ROOT / 'reports/JOINT-020'
ROUTES = ('credited', 'withheld', 'initial', 'uniform', 'disagreement', 'stop',
          'erase_history', 'no_imagination')


def sources():
    extra = ['sera_field/joint_cycle.py', 'sera_field/joint_data.py',
             'sera_field/joint_training.py', 'scripts/complete_joint020.py']
    return {**registered_sources(), 'implementation': {**source_files(),
              **{p: sha256(ROOT / p) for p in extra}}}


def select(route):
    arm = 'withheld' if route == 'withheld' else 'credited'
    return load_native(STUDY / arm, pointer='INITIAL.json' if route == 'initial' else 'SELECTION.json')


def run_final(data, *, replay=False):
    if not all((STUDY / arm / 'COMPLETE.json').exists() for arm in ('credited', 'withheld')):
        raise ValueError('Finish both matched courses before final predictions')
    results = {}; exact = {}; retention = {}
    for route in ('credited',) if replay else ROUTES:
        owner, selected, _ = select(route)
        mode = route if route in ('uniform', 'disagreement', 'stop') else 'learned'
        ablation = route if route in ('erase_history', 'no_imagination') else None
        results[route] = {}
        for cohort in ('matched', 'mismatched', 'shifted'):
            rows = data.shifted() if cohort == 'shifted' else data.finals(cohort)
            metrics, cases = evaluate(owner, rows, route=mode, ablation=ablation)
            result = {'route': route, 'cohort': cohort, 'checkpoint': selected,
                      'metrics': metrics, 'ids_sha256': identity([r['id'] for r in rows]),
                      'cases_sha256': identity(cases), 'registration': sha256(STUDY / 'SOURCES.json')}
            output = STUDY / ('replay' if replay else 'final') / route / cohort
            output.mkdir(parents=True, exist_ok=True)
            path = output / 'RESULTS.json'
            if path.exists() and read(path) != result:
                raise ValueError('Preserve prior final; recomputation differs')
            if not path.exists():
                (output / 'cases.jsonl').write_text(''.join(json.dumps(r, allow_nan=False)+'\n' for r in cases), encoding='utf-8')
                write_json(path, result)
            if replay:
                exact[cohort] = result == read(STUDY / 'final' / route / cohort / 'RESULTS.json')
            results[route][cohort] = result
            print(json.dumps({'joint_final': route, 'cohort': cohort, 'metrics': metrics}), flush=True)
        if route in ('credited', 'withheld', 'initial'):
            retention[route] = {}
            for cohort in ('matched', 'mismatched'):
                human = [r['human'] for r in data.finals(cohort)]
                metrics, _ = assess(owner, data.rehearsal, 'semantic', human)
                retention[route][cohort] = metrics
            physical = [physical_episode('JOINT-020-retention-final', i) for i in range(256)]
            retention[route]['physics'] = assess(owner, data.rehearsal, 'physics', physical)[0]
    if replay:
        exact['retention'] = retention['credited'] == read(REPORT / 'RETENTION.json')['credited']
        write_json(REPORT / 'REPLAY.json', {'fresh_process': True, 'checks': exact, 'exact': all(exact.values())})
        if not all(exact.values()):
            raise ValueError('Independent mixed-owner replay differs')
    else:
        write_json(REPORT / 'RESULTS.json', results)
        write_json(REPORT / 'RETENTION.json', retention)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=('prepare', 'train', 'final', 'replay'))
    args = parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use the numerical supervisor')
    torch.set_num_threads(1)
    registration = sources(); path = STUDY / 'SOURCES.json'
    if path.exists():
        if read(path) != registration:
            raise ValueError('Frozen joint registration changed')
    elif args.phase == 'prepare':
        write_json(path, registration)
    else:
        raise ValueError('Prepare the prospective source/split registration first')
    if args.phase == 'prepare':
        write_json(REPORT / 'REGISTRATION.json', registration)
        print(json.dumps({'registered_final_counts': {k: len(v['ids']) for k, v in registration['finals'].items()},
                          'parent_weights': registration['initial_selection']['weights']}), flush=True)
        return
    data = JointData()
    if args.phase == 'train':
        for arm in ('credited', 'withheld'):
            train(arm, data, registration)
        if read(STUDY / 'credited/INITIAL.json')['weights'] != read(STUDY / 'withheld/INITIAL.json')['weights']:
            raise ValueError('Matched initial tensors differ')
    else:
        run_final(data, replay=args.phase == 'replay')


if __name__ == '__main__':
    main()
