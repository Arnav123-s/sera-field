"""Package the assessed echo owner without changing the protected default."""
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import torch
from sera_field.records import sha256,write_json
from sera_field.study_inquiry import load_selected
from sera_field.model import weight_hash


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use supervisor')
    torch.set_num_threads(1)
    study=ROOT/'runs/ECHO-007'
    decision=json.loads((study/'DECISION.json').read_text())
    registry=json.loads((study/'FINAL_REGISTRATION.json').read_text())
    for arm in ('echo','autograd','no_core_credit','parent'):
        replay=json.loads((study/'replay'/arm/'REPLAY.json').read_text())
        if not replay['all_metrics_and_raw_records_exact']:raise ValueError('Missing independent replay')
    owner,selected=load_selected(study/'echo')
    if selected!= {k:v for k,v in registry['selections']['echo'].items() if k!='selection_sha256'}:
        raise ValueError('Selection differs from independent assessment')
    destination=ROOT/'checkpoints/ECHO-007'
    if (destination/'SELECTION.json').exists():
        old,_=load_selected(destination)
        if weight_hash(old)!=weight_hash(owner):raise ValueError('Preserve the different existing package')
        return
    revisions=destination/'revisions';revisions.mkdir(parents=True,exist_ok=True)
    temporary=revisions/'inference.tmp'
    with temporary.open('xb') as handle:
        torch.save({'bridge':{'owner':owner.state_dict(),'specification':owner.specification()},
                    'lineage':{'source_selection':selected,'parent_selection_sha256':registry['selections']['parent']['selection_sha256'],
                               'decision_sha256':sha256(study/'DECISION.json'),
                               'role':'qualified_optional_successor' if decision['promote'] else 'experimental_candidate'}},handle)
    digest=sha256(temporary);path=revisions/(digest+'.pt');temporary.rename(path)
    manifest={**selected,'source_checkpoint_sha256':selected['sha256'],'sha256':digest,'revision':path.name,
              'role':'qualified_optional_successor' if decision['promote'] else 'experimental_candidate'}
    write_json(destination/'SELECTION.json',manifest)
    restored,_=load_selected(destination)
    if weight_hash(restored)!=selected['weights']:raise ValueError('Export changed learned weights')
    write_json(destination/'MANIFEST.json',{'inference_checkpoint':manifest,'decision':decision,
        'parameter_count':sum(p.numel() for p in owner.parameters()),
        'parameter_bytes':sum(p.numel()*p.element_size() for p in owner.parameters()),
        'file_bytes':path.stat().st_size,'no_raw_corpus_text':True,
        'complete_resume_state':'runs/ECHO-007/echo/revisions',
        'default_owner':'checkpoints/SCFE-004 remains preserved'})
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':main()
