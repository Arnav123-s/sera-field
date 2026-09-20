"""Complete finite Ising measurement branches and local recurrent policy credit.

Projective outcomes generate candidate interventions; an acquired model supplies
their physical predictions. Neither amplitudes nor branch counts certify truth.
"""
import itertools
import hashlib
import torch
from torch import nn

from .credit_bridge import CreditBridge
from .model import weight_hash


def majoranas():
    identity=torch.eye(2,dtype=torch.complex128)
    x=torch.tensor([[0,1],[1,0]],dtype=torch.complex128)
    y=torch.tensor([[0,-1j],[1j,0]],dtype=torch.complex128)
    z=torch.diag(torch.tensor([1,-1],dtype=torch.complex128))
    result=[]
    for site in range(3):
        for axis in (x,y):
            factors=[z if j<site else axis if j==site else identity for j in range(3)]
            result.append(torch.kron(torch.kron(factors[0],factors[1]),factors[2]))
    return result


def projectors():
    gamma=majoranas();eye=torch.eye(8,dtype=torch.complex128)
    def charge(i,j,sign):return .5*(eye+sign*1j*gamma[i]@gamma[j])
    return gamma,charge


def measurement_candidates(coordinates):
    """All 24 outcomes of three three-measurement circuits, no postselection."""
    z=coordinates.detach().double()
    theta=torch.pi*z[0].sigmoid();phase=torch.pi*z[1].tanh()
    logical=torch.stack((torch.cos(theta/2).to(torch.complex128),
                          torch.exp(1j*phase)*torch.sin(theta/2)))
    embedding=torch.eye(8,dtype=torch.complex128)[:,[3,6]]
    initial=embedding@logical
    gamma,charge=projectors()
    logical_z=-1j*gamma[0]@gamma[1]
    logical_x=1j*gamma[1]@gamma[4]
    records=[]
    for circuit,(i,j) in enumerate(((0,1),(1,4),(4,0))):
        for a,b,c in itertools.product((-1,1),repeat=3):
            operation=charge(2,3,c)@charge(j,2,b)@charge(i,2,a)@embedding
            ket=operation@logical
            probability=float(torch.vdot(ket,ket).real)
            if probability<=1e-14:
                records.append({'circuit':circuit,'outcomes':[a,b,c],'probability':0.,'probe':None});continue
            ket=ket/probability**.5
            bx=float(torch.vdot(ket,logical_x@ket).real);bz=float(torch.vdot(ket,logical_z@ket).real)
            # Canonical operational identity, independent of wording, current
            # numeric coordinates or the recorded measurement-outcome aliases.
            norm=(operation.conj().T@operation).trace().real/2
            observables=torch.stack((operation.conj().T@logical_x@operation,
                                      operation.conj().T@logical_z@operation))/norm
            encoded=torch.view_as_real(observables).round(decimals=10).numpy()
            encoded[abs(encoded)<1e-10]=0
            method=hashlib.sha256(encoded.tobytes()).hexdigest()
            records.append({'circuit':circuit,'outcomes':[a,b,c],'probability':probability/3,
                            'method':method,'probe':[max(-2.,min(2.,2*bx)),max(-2.,min(2.,2*bz))]})
    if abs(sum(r['probability'] for r in records)-1)>1e-10:
        raise ValueError('Incomplete measurement outcomes')
    return records


class LocalInvestigationPolicy(nn.Module):
    """Diagonal recurrent units with exact forward local eligibility traces.

    This limited recurrent topology makes the forward eligibility recurrence
    exact. It is not an exact replacement for arbitrary densely recurrent BPTT.
    """
    def __init__(self,width=16,inputs=4):
        super().__init__()
        self.input_weights=nn.Parameter(torch.randn(width,inputs)*.15)
        self.input_bias=nn.Parameter(torch.zeros(width))
        self.raw_recurrence=nn.Parameter(torch.full((width,),.3))
        self.output_weights=nn.Parameter(torch.randn(2,width)*.03)
        self.output_bias=nn.Parameter(torch.zeros(2))

    def reference(self,inputs):
        h=torch.zeros_like(self.raw_recurrence)
        for x in inputs:h=torch.tanh(self.raw_recurrence.tanh()*h+self.input_weights@x+self.input_bias)
        return self.output_weights@h+self.output_bias

    @torch.no_grad()
    def eligibility(self,inputs,sample,*,sigma=.7):
        h=torch.zeros_like(self.raw_recurrence)
        ew=torch.zeros_like(self.input_weights);eb=torch.zeros_like(h);ea=torch.zeros_like(h)
        alpha=self.raw_recurrence.tanh()
        for x in inputs:
            previous=h;h=torch.tanh(alpha*h+self.input_weights@x+self.input_bias)
            derivative=1-h.square()
            ew=derivative[:,None]*(alpha[:,None]*ew+x[None])
            eb=derivative*(alpha*eb+1)
            ea=derivative*(alpha*ea+(1-alpha.square())*previous)
        mean=self.output_weights@h+self.output_bias
        error=(sample-mean)/(sigma*sigma)
        learning_signal=self.output_weights.T@error
        trace={'input_weights':learning_signal[:,None]*ew,'input_bias':learning_signal*eb,
               'raw_recurrence':learning_signal*ea,'output_weights':error[:,None]*h[None],
               'output_bias':error}
        return mean,trace


class LocalCreditBridge(CreditBridge):
    def record_local_score(self,*,decision,goal,predictor,assumptions_id,trace,sample):
        if not all((decision,goal,predictor,assumptions_id)):
            raise ValueError('Decision, original goal, predictor and scope required')
        if decision in self.pending or decision in self.used_decisions or len(self.pending)>=32:
            raise ValueError('Duplicate decision or unresolved capacity')
        parameters={n:p for n,p in self.owner.named_parameters() if p.requires_grad}
        if set(trace)!=set(parameters):raise ValueError('Every trainable coordinate needs explicit eligibility')
        for name,p in parameters.items():
            if trace[name].shape!=p.shape or not torch.isfinite(trace[name]).all():
                raise ValueError('Invalid local derivative trace')
        self.pending[decision]={'goal':goal,'predictor':predictor,'assumptions':assumptions_id,
            'policy':weight_hash(self.owner),'choice':sample.detach().tolist(),
            'eligibility':{k:v.detach().clone() for k,v in trace.items()},
            'logits':torch.zeros(2),'trace_kind':'local recurrent Gaussian score derivative'}
