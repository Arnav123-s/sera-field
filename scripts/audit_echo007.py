"""Audit exact learned exposure, parameter retention and field storage after finals."""
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import torch
from sera_field.records import sha256,write_json
from sera_field.reversible_field import position


def payload(root,selected):
    path=root/'revisions'/selected['revision']
    if sha256(path)!=selected['sha256']:raise ValueError('Source checkpoint changed')
    return torch.load(path,map_location='cpu',weights_only=False)


def footprint(backend,steps):
    q=torch.zeros(1,8,8,requires_grad=True);p=torch.zeros_like(q,requires_grad=True)
    source=torch.full_like(q,.1,requires_grad=True)
    restrictions=torch.eye(8).repeat(8,1,1).requires_grad_()
    prior=torch.zeros(8,8,requires_grad=True)
    k=torch.tensor(.5,requires_grad=True);s=torch.tensor(.15,requires_grad=True)
    saved=[]
    def pack(t):saved.append(t);return t
    with torch.autograd.graph.saved_tensors_hooks(pack,lambda t:t):
        output=position(q,p,source,restrictions,prior,k,s,steps=steps,backend=backend)
    unique={t.untyped_storage().data_ptr():t.untyped_storage().nbytes() for t in saved}
    result={'saved_tensor_occurrences':len(saved),'logical_saved_bytes':sum(t.numel()*t.element_size() for t in saved),
            'unique_saved_storage_bytes':sum(unique.values()),'finite_output':bool(torch.isfinite(output).all())}
    return result


def main():
    if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use supervisor')
    torch.set_num_threads(1)
    study=ROOT/'runs/ECHO-007';report=ROOT/'reports/ECHO-007'
    decision=json.loads((study/'DECISION.json').read_text())
    parent=json.loads((ROOT/'checkpoints/SCFE-004/SELECTION.json').read_text())
    basefile=ROOT/'runs/SCFE-004-teaching-1103/revisions'/(parent['teacher_checkpoint_sha256']+'.pt')
    if sha256(basefile)!=parent['teacher_checkpoint_sha256']:raise ValueError('Parent teaching state changed')
    parent_progress=torch.load(basefile,map_location='cpu',weights_only=False)['progress']
    parent_seen=set(parent_progress['seen'])
    arms={}
    for arm in ('echo','autograd','no_core_credit'):
        complete=json.loads((study/arm/'COMPLETE.json').read_text())
        selected=complete['selected'];state=payload(study/arm,selected);progress=state['progress']
        seen=set(progress['seen'])
        arms[arm]={'entire_run':complete,'selected_checkpoint':selected,
                   'selected_exposures':progress['exposures'],'selected_unique_human_records':len(seen),
                   'selected_previously_unseen_human_records':len(seen-parent_seen),
                   'retained_plus_continuation_unique_human_records':len(parent_seen|seen),
                   'selected_physical_systems':progress['physics_cursor'],
                   'human_source_manifest_sha256':progress['data_manifest_sha256']}
    storage={b:{str(n):footprint(b,n) for n in (4,16,32,64)} for b in ('echo','autograd')}
    if len({v['unique_saved_storage_bytes'] for v in storage['echo'].values()})!=1:
        raise ValueError('Echo storage unexpectedly grows with integration depth')
    write_json(report/'LEARNED_STATE.json',{'parent_unique_human_records':len(parent_seen),'arms':arms,'decision':decision})
    write_json(report/'FIELD_STORAGE.json',{'scope':'Saved differentiation tensors for one 8-node, 8-grade field call; excludes encoder/readout tapes, optimizer, branch workspace and process memory.',
        'input_dtype':'float32','internal_dtype':'float64','batch':1,'measurements':storage})
    print(json.dumps({'selected_echo_step':arms['echo']['selected_checkpoint']['step'],
        'echo_additional_distinct_human_records':arms['echo']['selected_unique_human_records'],
        'echo_new_to_parent_human_records':arms['echo']['selected_previously_unseen_human_records'],
        'storage':storage},indent=2))


if __name__=='__main__':main()
