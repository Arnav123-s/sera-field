"""Separate batch-position rounding from a forbidden observed-input bypass."""
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import torch
from sera_field.native_owner import NativeOwner
from sera_field.records import sha256, write_json


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'): raise SystemExit('Use the numerical supervisor')
    torch.set_num_threads(1); torch.manual_seed(19119)
    owner = NativeOwner().eval()
    premises = ['A boy carries flowers.', 'An empty machine sits outside.']
    hypotheses = ['Something is being carried.'] * 2
    result = {}
    for dtype in ('float32', 'float64'):
        owner.to(dtype=getattr(torch, dtype))
        empty = owner.semantic(premises, hypotheses, memory=False)
        permuted = owner.semantic(list(reversed(premises)), hypotheses, memory=False)
        direct = owner.meaning(owner.imagine(owner.empty(2), owner.encode_texts(hypotheses)))
        retained = owner.semantic(premises, hypotheses)
        result[dtype] = {
            'batch_position_max_abs_difference': float((empty[0]-empty[1]).abs().max().detach()),
            'changed_discarded_premises_exact': torch.equal(empty, permuted),
            'explicit_empty_query_exact': torch.equal(empty, direct),
            'retained_premise_effect_max_abs': float((retained[0]-retained[1]).abs().max().detach()),
            'epsilon': torch.finfo(getattr(torch, dtype)).eps,
        }
    result['interpretation'] = 'Exact equality at fixed batch positions tests premise independence; cross-position float equality has arithmetic roundoff.'
    result['script_sha256'] = sha256(__file__)
    result['numerical_attempt'] = os.environ['SERA_FIELD_SUPERVISED']
    result['training_started'] = False
    write_json(ROOT / 'reports/NATIVE-019/ROUNDING_DIAGNOSIS.json', result)
    print(json.dumps(result))
    if not all(r['changed_discarded_premises_exact'] and r['explicit_empty_query_exact']
               for k, r in result.items() if k in ('float32', 'float64')):
        raise ValueError('Observed-input independence needs a model repair before teaching')


if __name__ == '__main__': main()
