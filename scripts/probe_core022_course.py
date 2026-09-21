"""Actual full-course derivative workload, zero optimizer or curriculum steps."""
import json
import os
from pathlib import Path
import random
import sys
import time

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import torch
from sera_field.core_course_data import CoreData, pair
from sera_field.core_owner import CoreOwner
from sera_field.native_owner import NativeConfig
from sera_field.native_data import physical_episode
from sera_field.native_training import loss_cases
from sera_field.core_teaching_loss import teaching_loss
from sera_field.joint_training import cycle
from sera_field.model import weight_hash
from sera_field.records import write_json


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'): raise SystemExit('Use the numerical resource supervisor')
    out = ROOT/'runs/CORE-022/course-probe'
    if out.exists(): raise ValueError('Preserve completed workload evidence')
    out.mkdir(parents=True)
    torch.set_num_threads(1); torch.manual_seed(22259); random.seed(22259)
    data = CoreData(); owner = CoreOwner(NativeConfig(nodes=4, rounds=2), program_slots=8)
    initial = weight_hash(owner); records = []
    for kind in ('semantic','pairs','reading','programs','physics','mixed'):
        owner.zero_grad(set_to_none=True); started = time.perf_counter()
        if kind == 'physics': rows = [physical_episode('CORE-022-resource-fixture', i) for i in range(8)]
        elif kind == 'mixed': rows = pair(data.development['semantic'][:4], 'CORE-022-resource-fixture')
        else:
            # Largest available development inputs in this finite allocation;
            # no training update and no reserved final view is opened.
            rows = sorted(data.development[kind], key=lambda r: len(json.dumps(r)), reverse=True)[:4 if kind == 'reading' else 8]
        if kind == 'programs': loss, _ = teaching_loss(owner, rows)
        elif kind == 'mixed': loss, _, _ = cycle(owner, rows, training=True)
        else: loss, _ = loss_cases(owner, data, kind, rows, split='development')
        if not torch.isfinite(loss): raise ValueError('Nonfinite complete-course workload')
        loss.backward()
        grads = {name: float(p.grad.norm()) for name,p in owner.named_parameters() if p.grad is not None}
        if any(not torch.isfinite(p.grad).all() for p in owner.parameters() if p.grad is not None):
            raise ValueError('Nonfinite complete-course derivative')
        records.append({'kind': kind, 'batch': len(rows), 'ids': [r['id'] for r in rows],
            'loss': float(loss.detach()), 'wall_seconds': time.perf_counter()-started, 'gradient_norms': grads})
        del loss
        print(json.dumps({k:v for k,v in records[-1].items() if k != 'gradient_norms'}), flush=True)
    result = {'initial_weights': initial, 'final_weights': weight_hash(owner), 'same_weights': initial == weight_hash(owner),
        'owner_specification': owner.specification(), 'workloads': records, 'optimizer_steps': 0,
        'curriculum_presentations': 0, 'final_views_opened': False}
    if not result['same_weights']: raise ValueError('Resource probe changed weights')
    write_json(out/'RESULT.json', result); write_json(ROOT/'reports/CORE-022/COURSE_WORKLOAD.json', result)


if __name__ == '__main__': main()
