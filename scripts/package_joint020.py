"""Preserve an explicitly assessed research owner and its exact inference tensors."""
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import torch
from sera_field.joint_training import STUDY
from sera_field.native_training import load_native, read
from sera_field.records import sha256, write_json


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use the numerical supervisor')
    torch.set_num_threads(1)
    decision = read(ROOT / 'reports/JOINT-020/QUALIFICATION.json')
    owner, selected, payload = load_native(STUDY / 'credited')
    target = ROOT / 'checkpoints/JOINT-020'; revisions = target / 'revisions'; revisions.mkdir(parents=True, exist_ok=True)
    if not (target / 'SELECTION.json').exists():
        temp = revisions / 'inference.pt'
        if temp.exists():
            raise ValueError('Preserve interrupted package for inspection')
        torch.save({'specification': owner.specification(), 'owner': owner.state_dict(), 'step': selected['step'],
                    'sources': payload['sources']}, temp)
        digest = sha256(temp); temp.rename(revisions / (digest+'.pt'))
        packaged = {**selected, 'sha256': digest, 'revision': digest+'.pt'}
        write_json(target / 'SELECTION.json', packaged)
        write_json(target / 'MANIFEST.json', {'inference': packaged, 'source_training': selected,
            'all_frozen_gates': decision['all_frozen_gates'], 'all_qualification_checks': decision['all_gates'],
            'qualification': 'reports/JOINT-020/QUALIFICATION.json',
            'role': 'qualified mixed investigation owner' if decision['all_gates'] else 'preserved mixed investigation research candidate',
            'earlier_defaults_replaced': False, 'parent_owner': 'NATIVE-019', 'external_pretrained_weights': False})
    restored, _, _ = load_native(target)
    checks = {k: torch.equal(v, restored.state_dict()[k]) for k, v in owner.state_dict().items()}
    if not all(checks.values()):
        raise ValueError('Packaged joint tensors differ')
    write_json(ROOT / 'reports/JOINT-020/PACKAGE.json', {'exact_tensors': all(checks.values()),
                'tensors_checked': len(checks), 'manifest': read(target / 'MANIFEST.json')})
    print(json.dumps({'joint_package': str(target), 'exact_tensors': all(checks.values())}), flush=True)


if __name__ == '__main__':
    main()
