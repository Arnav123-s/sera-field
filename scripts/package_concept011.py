"""Export qualified inference weights, retaining complete training state locally."""
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
    root=ROOT/'runs/CONCEPT-011';dest=ROOT/'checkpoints/CONCEPT-011'
    decision=json.loads((root/'DECISION.json').read_text())
    if not decision['qualified'] or not decision['all_five_replays_exact']:
        raise ValueError('Qualification and independent replays required')
    owner,selected=load_selected(root)
    registry=json.loads((root/'FINAL_REGISTRATION.json').read_text())
    if registry['selections']['repair']!=selected:raise ValueError('Assessed checkpoint changed')
    if (dest/'SELECTION.json').exists():
        old,_=load_selected(dest)
        if weight_hash(old)!=weight_hash(owner) or old.specification()!=owner.specification():
            raise ValueError('Existing package differs')
        return
    revisions=dest/'revisions';revisions.mkdir(parents=True,exist_ok=True)
    temp=revisions/'inference.tmp'
    with temp.open('xb') as handle:
        torch.save({'bridge':{'owner':owner.state_dict(),'specification':owner.specification()},
                    'lineage':{'source_selection':selected,'decision_sha256':sha256(root/'DECISION.json'),
                               'role':'qualified_five_use_owner'}},handle)
    digest=sha256(temp);path=revisions/(digest+'.pt');temp.rename(path)
    package={**selected,'source_checkpoint_sha256':selected['sha256'],'sha256':digest,'revision':path.name,
             'role':'qualified_five_use_owner','retained_concept_reward_updates':754}
    write_json(dest/'SELECTION.json',package)
    loaded,_=load_selected(dest)
    if weight_hash(loaded)!=selected['weights']:raise ValueError('Export changed weights')
    write_json(dest/'MANIFEST.json',{'inference_checkpoint':package,'decision':decision,
        'parameter_count':sum(p.numel() for p in owner.parameters()),
        'parameter_bytes':sum(p.numel()*p.element_size() for p in owner.parameters()),
        'file_bytes':path.stat().st_size,'no_raw_corpus_text':True,'no_optimizer_or_training_buffer':True,
        'complete_resume_state':'runs/CONCEPT-011/revisions','older_packages':'preserved unchanged',
        'source_parent':'runs/CONCEPT-009','inherited_new_concept_training':'runs/CONCEPT-008/full',
        'inherited_qualified_policy':'runs/CONCEPT-008/reward',
        'retained_human_record_union':78746})
    print(json.dumps(package,indent=2))


if __name__=='__main__':main()
