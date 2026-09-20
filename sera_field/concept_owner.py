"""One observed relationship used by prediction, inference, planning and language."""
import copy
import json
from pathlib import Path

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from .credit_bridge import identity
from .reversible_field import EchoOwner
from .records import sha256, write_json

TRAIN_PHRASES = (
    ('What happens when the control input increases?', 'How does more drive change acceleration?',
     'What is the effect of increasing the applied input?', 'Increase the control and describe the response.'),
    ('What happens when speed increases?', 'How does faster motion change acceleration?',
     'What is the effect of increasing velocity?', 'Increase the speed and describe the response.'))
TRANSFER_PHRASES = (
    ('If I raise the input, how will acceleration change?', 'Imagine applying more drive. What happens?'),
    ('If I raise the velocity, how will acceleration change?', 'Imagine moving faster. What happens?'))


def basis(x):
    v, u = x[..., 0], x[..., 1]
    return torch.stack((u, v, v * v.abs(), torch.ones_like(v)), -1)


class ConceptOwner(EchoOwner):
    def __init__(self, width=48, nodes=8, rounds=4, *, backend='echo', steps=32, precision_kind='full'):
        super().__init__(width, nodes, rounds, backend=backend, steps=steps)
        if precision_kind not in ('full', 'diagonal'):
            raise ValueError('Explicit acquisition precision required')
        self.precision_kind = precision_kind
        self.acquisition = nn.Sequential(nn.Linear(2*width+nodes+2, 32), nn.Tanh(), nn.Linear(32, 10))
        with torch.no_grad():
            self.acquisition[-1].weight.zero_()
            self.acquisition[-1].bias.zero_()
            self.acquisition[-1].bias[[0,2,5,9]] = -1.6
        self.question_route = nn.Sequential(nn.Linear(width, 24), nn.Tanh(), nn.Linear(24, 2))
        self.meaning = nn.Sequential(nn.Linear(10, 48), nn.Tanh(), nn.Linear(48, 3))

    def specification(self):
        return {**super().specification(), 'type': 'concept-owner-008', 'precision_kind': self.precision_kind}

    def precision(self, latent):
        raw = self.acquisition(latent)
        lower = torch.zeros(len(raw), 4, 4, dtype=raw.dtype)
        k = 0
        for i in range(4):
            for j in range(i+1):
                lower[:, i, j] = (F.softplus(raw[:, k])+.01 if i == j else
                                  .2*raw[:, k].tanh() if self.precision_kind == 'full' else raw[:, k]*0)
                k += 1
        return lower @ lower.transpose(-1,-2) + torch.eye(4)[None]*1e-4

    def world(self, observations, present):
        if not torch.isfinite(observations).all() or not torch.isfinite(present).all():
            raise ValueError('Finite measured observations required')
        if torch.any((present != 0) & (present != 1)) or torch.any(present.sum(1) < 1):
            raise ValueError('At least one observed row and a binary mask are required')
        prior = super().world(observations, present)
        x = basis(observations) * present[..., None]
        y = observations[..., 2] * present
        precision = self.precision(prior['latent'])
        gram = x.transpose(-1,-2) @ x
        residual = y[:,None] - torch.einsum('bnc,bhc->bhn', x, prior['coefficients'])
        rhs = torch.einsum('bnc,bhn->bch', x, residual)
        correction = torch.linalg.solve(gram+precision, rhs).transpose(-1,-2)
        return {**prior, 'prior_coefficients': prior['coefficients'],
                'coefficients': prior['coefficients']+correction,
                'precision': precision, 'observed_gram': gram}

    def directional_logits(self, coefficients, queries, route):
        c = coefficients.mean(1)
        role = F.one_hot(route, 2).to(c.dtype)
        delta = torch.stack((role[:,1]*.5, role[:,0]*.5), -1)
        descriptor = torch.cat((c, queries/3, delta, role), -1)
        return self.meaning(descriptor)

    def route_logits(self, questions):
        return self.question_route(self.encode_texts(questions))


def continue_owner(parent, kind, seed=8108):
    torch.manual_seed(seed)
    owner = ConceptOwner(**parent.config, backend=parent.field.backend,
                         steps=parent.field.steps, precision_kind=kind)
    result = owner.load_state_dict(parent.state_dict(), strict=False)
    if result.unexpected_keys or any(not k.startswith(('acquisition.','question_route.','meaning.')) for k in result.missing_keys):
        raise ValueError('Unexpected parent compatibility')
    for name, p in owner.named_parameters():
        p.requires_grad_(name.startswith(('acquisition.','question_route.','meaning.')))
    return owner


def numpy_predict(coefficients, queries):
    x = np.asarray(queries, dtype=float)
    v, u = x[...,0], x[...,1]
    return np.asarray(coefficients) @ np.stack((u,v,v*np.abs(v),np.ones_like(v)), -1).T


def inverse_input(coefficients, velocity, acceleration):
    c = np.asarray(coefficients)
    gain = c[:,0]
    valid = np.abs(gain) >= .05
    value = np.full(len(c), np.nan)
    value[valid] = (acceleration-c[valid,1]*velocity-c[valid,2]*velocity*abs(velocity)-c[valid,3])/gain[valid]
    return {'hypotheses': [float(v) if np.isfinite(v) else None for v in value],
            'mean': float(np.mean(value[valid])) if valid.any() else None,
            'assumption': 'locally identifiable input gain and retained response basis'}


def endpoints(coefficients, controls, velocity=0., duration=.8, steps=64):
    c=np.asarray(coefficients,dtype=float)[:,None,:]
    u=np.asarray(controls,dtype=float)[None,:]
    z=np.zeros((len(c),u.shape[1],2)); z[:,:,1]=velocity
    dt=duration/steps
    def f(s):
        v=s[:,:,1]
        return np.stack((v,c[:,:,0]*u+c[:,:,1]*v+c[:,:,2]*v*np.abs(v)+c[:,:,3]),-1)
    for _ in range(steps):
        a=f(z);b=f(z+dt*a/2);d=f(z+dt*b/2);e=f(z+dt*d)
        z+=dt*(a+2*b+2*d+e)/6
        if not np.isfinite(z).all() or abs(z).max()>10000:
            raise ValueError('Imagined trajectory exceeded its numerical scope')
    return z


def plan(coefficients, target, velocity=0., duration=.8):
    controls=np.linspace(-2,2,41)
    imagined=endpoints(coefficients,controls,velocity,duration)
    losses=((imagined-np.asarray(target)[None,None])**2).mean((0,2))
    ranked=np.argsort(losses,kind='stable')
    return {'input':float(controls[ranked[0]]),'predicted_endpoint':imagined[:,ranked[0]].mean(0).tolist(),
            'alternatives':[{'input':float(controls[i]),'conditional_loss':float(losses[i]),
                             'endpoints':imagined[:,i].tolist()} for i in ranked[:5]],
            'assumptions':{'constant_input':True,'duration':duration,'initial_velocity':velocity,'bounds':[-2,2]}}


def acquire(owner, observations, predictor, evidence_ids):
    rows=np.asarray(observations,dtype='float32')
    if rows.ndim!=2 or rows.shape[1]!=3 or not len(rows) or not np.isfinite(rows).all():
        raise ValueError('Measured [velocity, control input, acceleration] rows required')
    if len(evidence_ids)!=len(rows) or len(set(evidence_ids))!=len(rows):
        raise ValueError('Every observation requires distinct evidence')
    with torch.no_grad():
        world=owner.world(torch.from_numpy(rows)[None],torch.ones(1,len(rows)))
    c=world['coefficients'][0].tolist()
    state={'predictor':predictor,'observations':rows.tolist(),'evidence_ids':list(evidence_ids),
           'coefficients':c,'scope':'observed control/velocity response; supplied four-term basis',
           'epistemic_status':'observation-conditioned hypotheses'}
    return {'concept_id':identity(state),**state}


def explain(owner, concept, question, query=(0.,0.)):
    with torch.no_grad():
        logits=owner.route_logits([question]); route=int(logits.argmax())
        c=torch.tensor(concept['coefficients'])[None]
        labels=owner.directional_logits(c,torch.as_tensor(np.asarray(query),dtype=torch.float32)[None],torch.tensor([route]))
        direction=int(labels.argmax())
    changes=('decreases','changes by less than the taught tolerance','increases')
    variable=('control input','velocity')[route]
    return {'concept_id':concept['concept_id'],'question':question,'learned_route':route,
            'direction':direction,'explanation':f'At the stated operating point, increasing {variable} by 0.5 {changes[direction]} the predicted acceleration.',
            'operating_point':[float(x) for x in query],'status':'conditional learned classification',
            'rendering':'supplied sentence form; route and direction selected by trained weights'}


def append_session(root, owner, predictor, goal, observations, evidence_ids, expected_parent=None):
    """Content-addressed, optimistic single-writer persistence; no guessed facts."""
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    pointer=root/'CURRENT.json'
    current=json.loads(pointer.read_text()) if pointer.exists() else None
    if (current['sha256'] if current else None)!=expected_parent:
        raise ValueError('Session advanced: reload before appending')
    old=None
    if current:
        path=root/(current['sha256']+'.json')
        if sha256(path)!=current['sha256']:raise ValueError('Corrupt session revision')
        old=json.loads(path.read_text())
        if old['predictor']!=predictor or old['original_goal']!=goal:
            raise ValueError('Predictor and original goal are immutable within this session')
        observations=old['concept']['observations']+observations
        evidence_ids=old['concept']['evidence_ids']+evidence_ids
    concept=acquire(owner,observations,predictor,evidence_ids)
    value={'parent':expected_parent,'predictor':predictor,'original_goal':goal,'concept':concept}
    with (root/'WRITE.lock').open('x') as lock:
        try:
            again=json.loads(pointer.read_text())['sha256'] if pointer.exists() else None
            if again!=expected_parent:raise ValueError('Concurrent session update')
            raw=(json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
            import hashlib
            digest=hashlib.sha256(raw).hexdigest()
            path=root/(digest+'.json')
            if not path.exists():
                with path.open('xb') as handle:handle.write(raw)
            write_json(pointer,{'sha256':digest,'concept_id':concept['concept_id']})
        finally:
            # The lock file is this call's own file, after exclusive creation.
            lock.close()
            (root/'WRITE.lock').unlink()
    return value
