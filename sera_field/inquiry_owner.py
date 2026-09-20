"""Learned investigation remains part of the same acquired-model owner."""
import torch
from .learned_extension import ExtensionOwner
from .fusion_inquiry import LocalInvestigationPolicy


class InquiryOwner(ExtensionOwner):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.imagination_policy=LocalInvestigationPolicy()

    def specification(self):
        return {**super().specification(),'type':'local-inquiry-014'}

    @torch.no_grad()
    def investigation_inputs(self,model,observations):
        prediction=self.predict_model(model,observations[...,:2]).mean(1)[0]
        rows=observations[0]
        return torch.stack((rows[:,0]/2,rows[:,1]/2,prediction/4,(rows[:,2]-prediction)/2),-1)


def extend_inquiry(parent,seed=14114):
    torch.manual_seed(seed);spec=dict(parent.specification());spec.pop('type')
    owner=InquiryOwner(**spec)
    result=owner.load_state_dict(parent.state_dict(),strict=False)
    if result.unexpected_keys or any(not k.startswith('imagination_policy.') for k in result.missing_keys):
        raise ValueError('Unexpected investigation parent')
    for name,p in owner.named_parameters():p.requires_grad_(name.startswith('imagination_policy.'))
    return owner
