"""Verified capture and mass-conserving Flory-Huggins bulk relaxation."""
import copy
import math
import torch
from torch import nn

from .credit_bridge import identity
from .topological_memory import encode_density,decode_density


def laplace(value):
    # Two-dimensional periodic bulk: depth and the boundary-node ring.
    return sum(value.roll(1,d)+value.roll(-1,d)-2*value for d in (-3,-2))


def free_energy(value, target, *, chi=2.2, kappa=.08, pin=8.):
    entropy=value*value.log()+(1-value)*(1-value).log()+chi*value*(1-value)
    gradient=sum((value.roll(-1,d)-value).square() for d in (-3,-2))
    return (entropy+.5*kappa*gradient+.5*pin*(value-target).square()).sum((-3,-2,-1))


@torch.no_grad()
def relax(value,target,*,steps=12):
    value=value.clone()
    start_mass=value.sum((-3,-2,-1)); start_energy=free_energy(value,target)
    accepted=0
    for _ in range(steps):
        mu=value.log()-(1-value).log()+2.2*(1-2*value)-.08*laplace(value)+8*(value-target)
        direction=laplace(mu)
        old=free_energy(value,target);dt=.008
        for _ in range(16):
            candidate=value+dt*direction
            if bool(((candidate<=0)|(candidate>=1)).any()):
                dt*=.5;continue
            energy=free_energy(candidate,target)
            if bool((energy<=old+1e-6).all()):
                value=candidate;accepted+=1;break
            dt*=.5
    return value,{'accepted_steps':accepted,
                  'mass_error':float((value.sum((-3,-2,-1))-start_mass).abs().max()),
                  'energy_before':start_energy.tolist(),
                  'energy_after':free_energy(value,target).tolist()}


class CondensateMemory(nn.Module):
    def __init__(self,nodes=8,slots=16,depth=4):
        super().__init__()
        self.nodes,self.slots,self.depth=nodes,slots,depth
        self.register_buffer('density',torch.full((slots,depth,nodes,3),.5))
        self.register_buffer('masses',torch.ones(slots,nodes,3,8))
        self.register_buffer('keys',torch.zeros(slots,nodes*3))
        self.register_buffer('active',torch.zeros(slots,dtype=torch.bool))
        self.register_buffer('cursor',torch.zeros((),dtype=torch.int64))
        self.evidence=[]

    def get_extra_state(self):
        return {'evidence':copy.deepcopy(self.evidence)}

    def set_extra_state(self,state):
        self.evidence=copy.deepcopy(state['evidence'])

    def recall(self,source,proposal=None):
        # Source-key affinity retrieves only the relaxed density, not a duplicate
        # table of unquantized values. Never mutates factual memory on inference.
        active=self.active.clone();keys=self.keys;density=self.density
        if proposal is not None:
            if proposal.get('status')!='conditional_memory_proposal':
                raise ValueError('Explicit hypothetical memory status required')
            slot=proposal['slot'];active[slot]=True
            keys=keys.clone();density=density.clone()
            keys[slot]=proposal['key'];density[slot]=proposal['density']
        if not bool(active.any()):
            return torch.zeros_like(source)
        query=torch.nn.functional.normalize(source.flatten(1),dim=-1)
        key=torch.nn.functional.normalize(keys[active],dim=-1)
        score=8*query@key.T
        weights=score.softmax(-1)
        values=(density[active].mean(1)-.5)/.35
        return torch.einsum('bs,snc->bnc',weights,values)

    @torch.no_grad()
    def propose(self,source):
        if source.shape!=(self.nodes,3) or not torch.isfinite(source).all():
            raise ValueError('One finite field tag is required')
        target=.5+.35*source.tanh();masses=encode_density(target)
        decoded=decode_density(masses)
        potential=decoded[None].expand(self.depth,-1,-1)
        density,diagnostics=relax(potential.clone(),potential)
        return {'status':'conditional_memory_proposal','slot':int(self.cursor)%self.slots,
                'key':source.flatten().clone(),'masses':masses,'density':density,
                'codec_max_error':float((target-decoded).abs().max()),'relaxation':diagnostics}

    @torch.no_grad()
    def capture(self,source,event,*,predictor,decision_policy):
        outcome=event.get('outcome',{})
        required=('goal','decision','predictor','policy_before','evidence_id','assessment_id',
                  'source_sha256','verifier_sha256','assumptions_id')
        if (not event.get('accepted') or not outcome.get('verified') or
            any(not outcome.get(k) for k in required) or
            outcome.get('evidence_kind') not in {'independent_simulation','measurement','exact_checker','human_assessment'}):
            raise ValueError('Qualified independent credit and its identities are required')
        if outcome['predictor']!=predictor or outcome['policy_before']!=decision_policy:
            raise ValueError('Stale or unrelated capture tag')
        if outcome.get('intended_intervention')!=outcome.get('observed_intervention'):
            raise ValueError('Unperformed intervention cannot qualify capture')
        if not (math.isfinite(outcome.get('before_loss',math.nan)) and
                math.isfinite(outcome.get('after_loss',math.nan)) and
                0<=outcome['after_loss']<outcome['before_loss']):
            raise ValueError('Capture requires positive independently measured progress')
        if any(e['evidence_id']==outcome['evidence_id'] or e['assessment_id']==outcome['assessment_id']
               or e['decision']==outcome['decision'] for e in self.evidence):
            raise ValueError('Capture evidence/assessment/decision already consumed')
        if source.shape!=(self.nodes,3) or not torch.isfinite(source).all():
            raise ValueError('One finite field tag is required')
        proposal=self.propose(source);slot=proposal['slot']
        record={**{k:outcome[k] for k in required},'slot':slot,
                'tag':identity(source.tolist()),'codec_max_error':proposal['codec_max_error'],
                'relaxation':proposal['relaxation'],'overwrites_slot_revision':int(self.cursor)>=self.slots}
        self.masses[slot].copy_(proposal['masses']);self.density[slot].copy_(proposal['density'])
        self.keys[slot].copy_(source.flatten());self.active[slot]=True
        self.cursor+=1;self.evidence.append(record)
        return record

    @torch.no_grad()
    def sleep(self):
        if not bool(self.active.any()):return {'active_slots':0}
        target=decode_density(self.masses[self.active])[:,None].expand(-1,self.depth,-1,-1)
        density,report=relax(self.density[self.active],target)
        self.density[self.active]=density
        return {'active_slots':int(self.active.sum()),**report}
