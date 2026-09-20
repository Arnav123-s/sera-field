"""Every use executes the same acquired numerical relation and its conditions."""
import numpy as np
import torch

from .credit_bridge import identity
from .model import weight_hash


def serialize_model(owner,model,assessment,*,evidence_ids,original_goal):
    rows=model['observations'][0].detach().tolist()
    if len(evidence_ids)!=len(rows) or len(set(evidence_ids))!=len(rows):
        raise ValueError('Distinct observation identities required')
    rank=model['rank']
    data={'rank':rank,'predictor':weight_hash(owner),'base':model['world']['coefficients'][0].detach().tolist(),
          'observations':rows,'evidence_ids':list(evidence_ids),'original_goal':original_goal,
          'assessment':assessment,'scope':{'input_bounds':[-2.,2.],
          'status':'observation-fitted model qualified on separate calibration; predictions remain conditional'}}
    if rank:
        data.update(directions=owner.residual_directions[:rank].detach().tolist(),
                    offsets=(owner.residual_offsets[:rank]+.5*model['context'][0,:rank]).detach().tolist(),
                    projection=model['projection'][0].detach().tolist(),
                    residual_coefficients=model['residual_coefficients'][0].detach().tolist())
    return {'concept_id':identity(data),**data}


def predict(concept,queries):
    x=np.asarray(queries,dtype=float);v,u=x[...,0],x[...,1]
    basis=np.stack((u,v,v*np.abs(v),np.ones_like(v)),-1)
    y=np.asarray(concept['base'])@basis.T
    if concept['rank']:
        phi=np.tanh(x@np.asarray(concept['directions']).T+np.asarray(concept['offsets']))
        residual=phi-basis@np.asarray(concept['projection'])
        y+=np.asarray(concept['residual_coefficients'])@residual.T
    return y


def inverse(concept,velocity,target):
    controls=np.linspace(-2,2,129)
    values=predict(concept,np.column_stack((np.full_like(controls,velocity),controls))).mean(0)-target
    brackets=[(controls[i],controls[i+1]) for i in range(len(controls)-1) if values[i]*values[i+1]<=0]
    alternatives=[]
    for lo,hi in brackets:
        for _ in range(24):
            mid=(lo+hi)/2
            a,b=predict(concept,[[velocity,lo],[velocity,mid]]).mean(0)-target
            if a*b<=0:hi=mid
            else:lo=mid
        u=(lo+hi)/2
        if not any(abs(u-r['input'])<1e-5 for r in alternatives):
            alternatives.append({'input':u,'method':'bracketed-bisection',
                'conditional_residual':float(predict(concept,[[velocity,u]]).mean()-target)})
    if not alternatives:
        i=int(np.abs(values).argmin());alternatives=[{'input':float(controls[i]),
            'method':'bounded-residual-minimization','conditional_residual':float(values[i])}]
    return {'concept_id':concept['concept_id'],'alternatives':alternatives,
            'input':min(alternatives,key=lambda r:abs(r['conditional_residual']))['input'],
            'status':'conditional numerical solutions; residuals retained'}


def rollout(concept,controls,*,velocity=0.,duration=.4,steps=32):
    controls=np.asarray(controls);state=np.zeros((len(controls),2));state[:,1]=velocity
    dt=duration/steps
    def rhs(s):return np.column_stack((s[:,1],predict(concept,np.column_stack((s[:,1],controls))).mean(0)))
    for _ in range(steps):
        a=rhs(state);b=rhs(state+dt*a/2);c=rhs(state+dt*b/2);d=rhs(state+dt*c)
        state+=dt*(a+2*b+2*c+d)/6
        if not np.isfinite(state).all() or np.abs(state).max()>10000:
            raise ValueError('Trajectory left numerical scope')
    return state


def plan(concept,target,*,velocity=0.,duration=.4):
    controls=np.linspace(-2,2,33);endpoints=rollout(concept,controls,velocity=velocity,duration=duration)
    error=((endpoints-np.asarray(target))**2).mean(-1);order=np.argsort(error,kind='stable')
    return {'concept_id':concept['concept_id'],'input':float(controls[order[0]]),
            'alternatives':[{'input':float(controls[i]),'endpoint':endpoints[i].tolist(),
                             'conditional_loss':float(error[i])} for i in order[:5]],
            'scope':{'constant_control':True,'duration':duration,'velocity':velocity}}


def explain(owner,concept,question,point):
    with torch.no_grad():route=int(owner.route_logits([question]).argmax())
    original=np.asarray(point,dtype=float);changed=original.copy();changed[1 if route==0 else 0]+=.5
    delta=float(np.diff(predict(concept,np.stack((original,changed))).mean(0))[0])
    label=2 if delta>.08 else 0 if delta<-.08 else 1
    words=('decreases','changes by less than the stated tolerance','increases')
    return {'concept_id':concept['concept_id'],'route':route,'direction':label,'delta':delta,
            'answer':f"At this operating point, increasing {('control input','velocity')[route]} by 0.5 {words[label]} the modeled response.",
            'rendering':'retained learned language routing; numerical consequence and supplied sentence renderer'}
