"""Package only the inference tensors under the ordinary numerical lease."""
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import torch
from sera_field.native_training import STUDY, read, load_native
from sera_field.records import sha256, write_json


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'): raise SystemExit('Use the numerical supervisor')
    torch.set_num_threads(1)
    decision = read(ROOT / 'reports/NATIVE-019/QUALIFICATION.json')
    owner, selected, payload = load_native(STUDY / 'native')
    target = ROOT / 'checkpoints/NATIVE-019'; target.mkdir(parents=True, exist_ok=True)
    if not (target / 'SELECTION.json').exists():
        revisions = target / 'revisions'; revisions.mkdir(exist_ok=True)
        temporary = revisions / 'inference.pt'
        if temporary.exists(): raise ValueError('Reconcile the interrupted package before retrying')
        torch.save({'specification': owner.specification(), 'owner': owner.state_dict(),
                    'step': selected['step'], 'sources': payload['sources']}, temporary)
        digest = sha256(temporary); temporary.rename(revisions / (digest + '.pt'))
        packaged = {**selected, 'sha256': digest, 'revision': digest + '.pt'}
        write_json(target / 'SELECTION.json', packaged)
        write_json(target / 'MANIFEST.json', {'inference': packaged, 'source_training': selected,
            'qualified_native_memory': decision['all_gates'],
            'role': 'qualified native-memory research owner' if decision['all_gates'] else 'preserved native-memory research candidate',
            'earlier_default_owner_replaced': False, 'parent_checkpoint': None, 'pretrained_weights': None})
    restored, _, _ = load_native(target)
    checks = {key: torch.equal(value, restored.state_dict()[key]) for key, value in owner.state_dict().items()}
    if not all(checks.values()): raise ValueError('Packaged native tensors differ')
    write_json(ROOT / 'reports/NATIVE-019/PACKAGE.json', {'exact_tensor_identity': all(checks.values()),
        'tensors_checked': len(checks), 'selected_training': selected, 'package': read(target / 'MANIFEST.json')})
    print(json.dumps({'native_package': str(target), 'exact_tensors': len(checks)}))


if __name__ == '__main__': main()
