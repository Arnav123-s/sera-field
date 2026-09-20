"""Export assessed inference state, with actual retained bulk and source identities."""
import json
import os
from pathlib import Path
import sys

import torch

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from sera_field.model import weight_hash,parameters
from sera_field.records import sha256,write_json
from sera_field.study_inquiry import load_selected


if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use scripts/supervise.py')
torch.set_num_threads(1)
qualification=json.loads((ROOT/'reports/UNIFIED-012/QUALIFICATION.json').read_text())
if not qualification['all_gates']:raise SystemExit('Candidate qualification has not passed')
source=ROOT/'runs/UNIFIED-012/coupled';owner,selected=load_selected(source)
target=ROOT/'checkpoints/UNIFIED-012';(target/'revisions').mkdir(parents=True,exist_ok=True)
if (target/'MANIFEST.json').exists():
    exported,_=load_selected(target)
    if weight_hash(exported)!=selected['weights']:raise ValueError('Preserve conflicting export')
else:
    payload={'bridge':{'owner':owner.state_dict(),'specification':owner.specification()},
             'source_checkpoint_sha256':selected['sha256'],'source_selection':selected,
             'kind':'assessed inference package; full optimizer/RNG history retained in local runs'}
    temporary=target/'revisions/export.tmp';torch.save(payload,temporary)
    digest=sha256(temporary);temporary.rename(target/'revisions'/(digest+'.pt'))
    selection={**selected,'sha256':digest,'revision':digest+'.pt','source_checkpoint_sha256':selected['sha256'],
               'role':'qualified_coupled_owner'}
    write_json(target/'SELECTION.json',selection)
    write_json(target/'MANIFEST.json',{'selection':selection,'specification':owner.specification(),
        'parameters':parameters(owner),'retained_captures':int(owner.field.memory.cursor),
        'qualification':'reports/UNIFIED-012/QUALIFICATION.json','source':'runs/UNIFIED-012/coupled',
        'report':'reports/UNIFIED-012/REPORT.md','full_resumable_training_state_retained':True})
print(json.dumps({'weights':weight_hash(owner),'package':str(target)}))
