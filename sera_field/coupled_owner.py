"""One continuing owner with coupled geometric processing and verified memory."""
import torch
from torch import nn

from .clifford_sheaf import typed_source,lift_rotation
from .concept_language import LanguageConceptOwner
from .condensate import CondensateMemory
from .gauge import adjoint_rotations,group_from_coordinates
from .reversible_field import EchoSheafField
from .situation_core import loop_feature
from .spd_sheaf import covariance_sequence,covariance_drive
from .temporal_echo import timed_positions


class CoupledField(EchoSheafField):
    def __init__(self,nodes=8,rounds=4,*,backend='echo',steps=32):
        super().__init__(nodes,rounds,backend=backend,steps=steps)
        if steps%4:
            raise ValueError('Four timed frames require a divisible step count')
        self.raw_covariance=nn.Parameter(torch.tensor(-2.))
        self.raw_memory=nn.Parameter(torch.tensor(-2.))
        self.raw_anchor=nn.Parameter(torch.tensor(0.))
        self.memory=CondensateMemory(nodes)
        self.ablation=None
        self.last_source=None
        self.memory_preview=None

    def imagine(self,source,previous=None,*,use_imagination=True):
        self.last_source=source.detach().clone()
        vector_transport=adjoint_rotations(self.links).transpose(-1,-2)
        restrictions=lift_rotation(vector_transport)
        recalled=self.memory.recall(source,self.memory_preview) if self.ablation!='no_memory' else torch.zeros_like(source)
        mixed=source+.15*self.raw_memory.sigmoid()*recalled
        covariance=covariance_sequence(mixed,vector_transport,.1+self.raw_anchor.sigmoid())
        drive,_=covariance_drive(covariance,mixed[None])
        gain=.2*self.raw_covariance.sigmoid() if self.ablation!='no_covariance' else 0.
        frames=mixed[None]+gain*(drive-mixed[None])
        injections=torch.stack([typed_source(frame,restrictions) for frame in frames])
        q=self.prior.expand(source.shape[0],-1,-1) if previous is None else previous
        if use_imagination:
            positions=timed_positions(q,torch.zeros_like(q),injections,restrictions,self.prior,
                        .1+.9*self.raw_stiffness.sigmoid(),.05+.2*self.raw_condensation.sigmoid(),
                        steps=self.steps//4,backend=self.backend)
            state=positions[-1]
        else:
            state=injections[-1]
        loop=loop_feature(group_from_coordinates(self.links),source).to(state.dtype)
        features=torch.cat((state.square().sum(-1).add(1e-8).sqrt(),loop[:,None]),-1)
        return state,features


class CoupledOwner(LanguageConceptOwner):
    def __init__(self,*args,capture_enabled=True,**kwargs):
        super().__init__(*args,**kwargs)
        self.capture_enabled=capture_enabled
        self.field=CoupledField(self.config['nodes'],self.config['rounds'],
                                backend=self.field.backend,steps=self.field.steps)
        # Choosing a capture proposal receives an ordinary score-function trace;
        # this is distinct from temporal state-credit learning inside the field.
        self.capture_policy=nn.Linear(4,2)
        nn.init.zeros_(self.capture_policy.weight);nn.init.zeros_(self.capture_policy.bias)

    def specification(self):
        return {**super().specification(),'type':'coupled-field-012','capture_enabled':self.capture_enabled}


def extend_coupled(parent,*,capture_enabled=True,seed=12112):
    torch.manual_seed(seed)
    spec=dict(parent.specification());spec.pop('type')
    owner=CoupledOwner(**spec,capture_enabled=capture_enabled)
    result=owner.load_state_dict(parent.state_dict(),strict=False)
    allowed=('field.raw_covariance','field.raw_memory','field.raw_anchor','field.memory.','capture_policy.')
    if result.unexpected_keys or any(not k.startswith(allowed) for k in result.missing_keys):
        raise ValueError('Unexpected parent compatibility')
    return owner
