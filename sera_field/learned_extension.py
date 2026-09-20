"""Observation-fitted learned basis extension with explicit adequacy evidence."""
import torch
from torch import nn
from torch.nn import functional as F

from .concept_owner import basis
from .coupled_owner import CoupledOwner,CoupledField
from .gauge import adjoint_rotations
from .stationary_field import stationary


class StationaryCoupledField(CoupledField):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.raw_stationary=nn.Parameter(torch.tensor(-2.))
        self.raw_fhn_a=nn.Parameter(torch.tensor(0.))
        self.raw_fhn_b=nn.Parameter(torch.tensor(0.))

    def imagine(self,source,previous=None,*,use_imagination=True):
        r=adjoint_rotations(self.links).transpose(-1,-2)
        a=.5+F.softplus(self.raw_fhn_a);b=.5+F.softplus(self.raw_fhn_b)
        settled=stationary(source,r,a+1/b)
        mixed=source+.1*self.raw_stationary.sigmoid()*(settled-source)
        return super().imagine(mixed,previous,use_imagination=use_imagination)


def gaussian_scale_flow(hessian):
    eigen=torch.linalg.eigvalsh(hessian.double())
    if bool((eigen<=0).any()):raise ValueError('Positive coefficient action Hessian required')
    scales=eigen.new_tensor([2.,1.,.5])
    flow=(scales[:,None]/(eigen[...,None,:]+scales[:,None].square())).sum(-1)
    integral=.5*torch.log((eigen+4)/(eigen+.25)).sum(-1)
    return {'scales':scales.tolist(),'d_gamma_d_scale':flow.detach().tolist(),
            'integrated_gaussian_flow':integral.detach().tolist(),
            'minimum_eigenvalue':eigen.min(-1).values.detach().tolist(),
            'scope':'finite Gaussian coefficient action; scalar k^2 regulator'}


class ExtensionOwner(CoupledOwner):
    def __init__(self,*args,extension_width=16,**kwargs):
        super().__init__(*args,**kwargs)
        self.extension_width=extension_width
        self.field=StationaryCoupledField(self.config['nodes'],self.config['rounds'],
                                          backend=self.field.backend,steps=self.field.steps)
        self.residual_directions=nn.Parameter(torch.randn(extension_width,2)*1.2)
        self.residual_offsets=nn.Parameter(torch.linspace(-1.5,1.5,extension_width))
        self.residual_context=nn.Sequential(nn.Linear(2*self.config['width']+self.config['nodes']+2,32),
                                            nn.Tanh(),nn.Linear(32,extension_width))
        nn.init.zeros_(self.residual_context[-1].weight);nn.init.zeros_(self.residual_context[-1].bias)
        self.raw_residual_precision=nn.Parameter(torch.full((extension_width,),-4.))

    def specification(self):
        return {**super().specification(),'type':'learned-extension-013','extension_width':self.extension_width}

    def feature(self,inputs,context,rank):
        return torch.tanh(inputs@self.residual_directions[:rank].T+
                          self.residual_offsets[:rank]+.5*context[:,:rank,None].transpose(1,2))

    def extend_model(self,observations,present,rank):
        if rank not in (0,4,8,16) or rank>self.extension_width:
            raise ValueError('Use a prospectively defined bounded extension rank')
        world=self.world(observations,present)
        model={'world':world,'rank':rank,'observations':observations,'present':present}
        if not rank:return model
        x=basis(observations)*present[...,None]
        context=self.residual_context(world['latent'])
        phi=self.feature(observations[...,:2],context,rank)*present[...,None]
        gram=x.transpose(-1,-2)@x
        projection=torch.linalg.solve(gram+1e-4*torch.eye(4),x.transpose(-1,-2)@phi)
        residual_feature=phi-x@projection
        targets=observations[...,2]*present
        errors=targets[:,None]-torch.einsum('bnc,bhc->bhn',x,world['coefficients'])
        precision=torch.diag(F.softplus(self.raw_residual_precision[:rank])+.0001)
        hessian=residual_feature.transpose(-1,-2)@residual_feature+precision
        coefficients=torch.linalg.solve(hessian,torch.einsum('bnr,bhn->brh',residual_feature,errors)).transpose(-1,-2)
        return {**model,'context':context,'projection':projection,'residual_coefficients':coefficients,
                'hessian':hessian,'feature_gram':residual_feature.transpose(-1,-2)@residual_feature}

    def predict_model(self,model,queries):
        base=self.consequences(model['world']['coefficients'],queries)
        if not model['rank']:return base
        features=self.feature(queries,model['context'],model['rank'])-basis(queries)@model['projection']
        return base+torch.einsum('bqr,bhr->bhq',features,model['residual_coefficients'])

    @torch.no_grad()
    def acquire_extension(self,adaptation,calibration):
        if adaptation.ndim!=3 or calibration.ndim!=3 or adaptation.shape[0]!=1 or calibration.shape[0]!=1:
            raise ValueError('One scoped acquisition with separate calibration rows is required')
        if adaptation.shape[1]<8 or calibration.shape[1]<4:
            raise ValueError('Independent calibration and sufficient adaptation evidence required')
        models=[];losses=[];diagnostics=[]
        present=torch.ones(adaptation.shape[:2])
        for rank in (0,4,8,16):
            model=self.extend_model(adaptation,present,rank)
            pred=self.predict_model(model,calibration[...,:2]).mean(1)
            losses.append(float((pred-calibration[...,2]).square().mean()))
            models.append(model)
            if rank:
                d=gaussian_scale_flow(model['hessian'])
                d['observed_feature_rank']=int(torch.linalg.matrix_rank(model['feature_gram'],tol=1e-6)[0])
                diagnostics.append({'rank':rank,**d})
        eligible=[i for i in range(1,4) if losses[0]>.015 and losses[i]<=.75*losses[0]]
        chosen=eligible[0] if eligible else 0
        return models[chosen],{'selected_rank':models[chosen]['rank'],'calibration_mse':losses,
                               'scale_diagnostics':diagnostics,'gap_detected':losses[0]>.015,
                               'qualification':'separate calibration observations; final outcomes withheld'}


def extend_representation(parent,seed=13113):
    torch.manual_seed(seed)
    spec=dict(parent.specification());spec.pop('type')
    owner=ExtensionOwner(**spec)
    result=owner.load_state_dict(parent.state_dict(),strict=False)
    allowed=('field.raw_stationary','field.raw_fhn_a','field.raw_fhn_b','residual_directions',
             'residual_offsets','residual_context.','raw_residual_precision')
    if result.unexpected_keys or any(not k.startswith(allowed) for k in result.missing_keys):
        raise ValueError('Unexpected extension parent')
    for name,p in owner.named_parameters():p.requires_grad_(name.startswith(allowed))
    return owner
