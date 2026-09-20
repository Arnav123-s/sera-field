"""Acquire a scoped response from measurements and reuse its learned extension."""
import argparse
import json
import os
from pathlib import Path

import numpy as np
import torch

from .credit_bridge import identity
from .extension_study import load_extension
from .extension_tasks import serialize_model,predict,inverse,plan,explain
from .model import weight_hash
from .records import sha256,write_json


def learn(owner,request):
    for key in ('original_goal','adaptation','calibration','source','assumptions'):
        if not request.get(key):raise ValueError('Missing acquisition field: '+key)
    if request['source'].get('kind') not in ('measurement','independent_simulation','human_assessment'):
        raise ValueError('An actual measurement source is required')
    a=np.asarray(request['adaptation'],dtype='float32');c=np.asarray(request['calibration'],dtype='float32')
    if a.ndim!=2 or c.ndim!=2 or a.shape[1]!=3 or c.shape[1]!=3:
        raise ValueError('Observation rows are [velocity,control,response]')
    if not np.isfinite(a).all() or not np.isfinite(c).all():raise ValueError('Finite observations required')
    if set(map(tuple,a[:,:2]))&set(map(tuple,c[:,:2])):
        raise ValueError('Calibration inputs must be separate from adaptation inputs')
    with torch.no_grad():model,assessment=owner.acquire_extension(torch.from_numpy(a)[None],torch.from_numpy(c)[None])
    source_id=identity(request['source'])
    assessment={**assessment,'calibration_observations':c.tolist(),
                'calibration_evidence_id':identity([source_id,'calibration',c.tolist()]),
                'source':request['source'],'assumptions':request['assumptions']}
    return serialize_model(owner,model,assessment,
        evidence_ids=[identity([source_id,'observation',i,row.tolist()]) for i,row in enumerate(a)],
        original_goal=request['original_goal'])


def persist(root,concept,*,expected_parent=None):
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    pointer=root/'CURRENT.json'
    current=json.loads(pointer.read_text()) if pointer.exists() else None
    if (current['sha256'] if current else None)!=expected_parent:
        raise ValueError('Session already exists or advanced; preserve it and use its exact revision')
    if current:
        old=json.loads((root/current['file']).read_text())
        if old['concept']['original_goal']!=concept['original_goal']:
            raise ValueError('Original goal must be preserved')
    record={'parent':expected_parent,'concept':concept}
    digest=identity(record);path=root/(digest+'.json')
    # Own exclusive lock prevents competing revision writers.
    lock=root/'WRITE.lock'
    with lock.open('x') as handle:
        try:
            actual=json.loads(pointer.read_text())['sha256'] if pointer.exists() else None
            if actual!=expected_parent:raise ValueError('Concurrent session advance')
            if not path.exists():
                with path.open('x',encoding='utf-8') as saved:json.dump(record,saved,indent=2,allow_nan=False)
            write_json(pointer,{'sha256':digest,'file':path.name,'file_sha256':sha256(path)})
        finally:
            handle.close();lock.unlink()
    return record


def restore(root):
    root=Path(root);current=json.loads((root/'CURRENT.json').read_text())
    path=root/current['file']
    if path.resolve().parent!=root.resolve() or sha256(path)!=current['file_sha256']:
        raise ValueError('Changed or invalid session file')
    record=json.loads(path.read_text())
    if identity(record)!=current['sha256']:raise ValueError('Changed session content')
    concept=record['concept'];body={k:v for k,v in concept.items() if k!='concept_id'}
    if identity(body)!=concept['concept_id']:raise ValueError('Changed acquired relation')
    return concept


def answer(owner,concept,request):
    if weight_hash(owner)!=concept['predictor']:raise ValueError('Use the same qualified predictor')
    result={'concept_id':concept['concept_id'],'original_goal':concept['original_goal'],
            'assumptions':concept['assessment'].get('assumptions',concept['scope'])}
    if 'queries' in request:result['predictions']=predict(concept,request['queries']).tolist()
    if 'inverse' in request:
        q=request['inverse'];result['inverse']=inverse(concept,q['velocity'],q['response'])
    if 'plan' in request:
        q=request['plan'];result['plan']=plan(concept,q['target'],velocity=q.get('velocity',0.),duration=q.get('duration',.4))
    if 'question' in request:
        result['explanation']=explain(owner,concept,request['question'],request.get('point',[0.,0.]))
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=('learn','answer'))
    parser.add_argument('--owner',type=Path,default=Path('checkpoints/GROW-013'))
    parser.add_argument('--session',type=Path,required=True);parser.add_argument('--input',type=Path,required=True)
    args=parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'):raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1);owner,_=load_extension(args.owner)
    request=json.loads(args.input.read_text(encoding='utf-8'))
    if args.action=='learn':
        concept=learn(owner,request);persist(args.session,concept)
        result=answer(owner,concept,request['original_goal'])
        result['acquisition']=concept['assessment']
    else:result=answer(owner,restore(args.session),request)
    print(json.dumps(result,indent=2,allow_nan=False))


if __name__=='__main__':main()
