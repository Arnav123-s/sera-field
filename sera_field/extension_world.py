"""Independent teaching worlds; no family identity enters the learner."""
from dataclasses import dataclass
import numpy as np
from .study_world import stable_seed


@dataclass
class HiddenResponse:
    gain:float
    drag:float
    offset:float
    nonlinear:float
    family:int
    frequency:float

    def observe(self,v,u):
        v,u=np.asarray(v),np.asarray(u)
        base=self.gain*u-self.drag*v+self.offset
        if self.family==0:extra=-self.nonlinear*v*np.abs(v)
        elif self.family==1:extra=-self.nonlinear*np.sin(self.frequency*v)
        elif self.family==2:extra=self.nonlinear*(np.tanh(self.frequency*u)-u)
        elif self.family==3:extra=self.nonlinear*np.tanh(v*u)
        else:extra=self.nonlinear*np.tanh(self.frequency*(v+.3*u))
        return base+extra

    def intervene(self,requested,*,scale=1.):
        v,u=map(float,requested);performed=[v,u*scale]
        return {'requested':[v,u],'performed':performed,
                'observation':[*performed,float(self.observe(*performed))],
                'actuation_matched':scale==1.,'origin':'independent_simulation'}


def episode(index,split,*,omitted=False):
    rng=np.random.default_rng(stable_seed('GROW-013',13113,index,split))
    world=HiddenResponse(float(rng.uniform(.7,1.3)),float(rng.uniform(.1,.8)),
        float(rng.uniform(-.4,.4)),float(rng.uniform(.25,.9)),int(rng.integers(5)),
        float(rng.uniform(3.5,5) if omitted else rng.uniform(.7,1.8)))
    adapt=rng.uniform(-2,2,(24,2));calib=rng.uniform(-2,2,(8,2));queries=rng.uniform(-2,2,(16,2))
    rows=lambda x:np.column_stack((x,world.observe(x[:,0],x[:,1]))).astype('float32')
    return world,rows(adapt),rows(calib),queries.astype('float32')
