"""Post-final diagnosis, explicitly not a new held-out qualification."""
import json
import os
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import torch
from sera_field.concept_language import lexical_features
from sera_field.study_inquiry import load_selected
from sera_field.records import write_json

if not os.environ.get('SERA_FIELD_SUPERVISED'): raise SystemExit('Use supervisor')
torch.set_num_threads(1)
root=ROOT/'runs/CONCEPT-010'
owner,_=load_selected(root)
bank=json.loads((root/'PHRASE_BANKS.json').read_text())['final']
texts=[s for group in bank for s in group]
labels=torch.tensor([r for r,group in enumerate(bank) for _ in group])
with torch.no_grad():
    base=owner.question_route(owner.encode_texts(texts))
    residual=owner.lexical_route(lexical_features(texts))
    logits={'old_head':base,'residual_alone':residual,'combined':base+residual}
metrics={k:float((v.argmax(-1)==labels).float().mean()) for k,v in logits.items()}
rows=[{'question':s,'expected':int(labels[i]),**{k:v[i].tolist() for k,v in logits.items()}} for i,s in enumerate(texts)]
result={'scope':'Post-final diagnostic on already opened questions; not qualification or a new test.',
        'accuracy':metrics,'rows':rows}
write_json(root/'ROUTING_DIAGNOSIS.json',result)
print(json.dumps(metrics))
