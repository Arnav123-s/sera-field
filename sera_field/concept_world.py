"""Independent, labeled simulation teacher/checker. No learner imports."""
from dataclasses import dataclass
import numpy as np
from scipy.integrate import solve_ivp
from .study_world import stable_seed


@dataclass(frozen=True)
class World:
    gain: float
    linear: float
    quadratic: float
    offset: float
    omitted: float=0.

    def observe(self,v,u):
        return self.gain*np.asarray(u)+self.linear*np.asarray(v)+self.quadratic*np.asarray(v)*abs(np.asarray(v))+self.offset+self.omitted*np.sin(2*np.asarray(v))

    def intervene(self,requested,scale=1.):
        v,u=map(float,requested);performed=[v,u*scale]
        return {'requested':[v,u],'performed':performed,'observation':[*performed,float(self.observe(*performed))],
                'actuation_matched':scale==1.,'origin':'independent_simulation'}

    def endpoint(self,u,velocity=0.,duration=.8):
        sol=solve_ivp(lambda t,y:[y[1],float(self.observe(y[1],u))],(0,duration),[0.,velocity],
                      method='DOP853',rtol=1e-10,atol=1e-12)
        if not sol.success:raise ValueError('Independent integration failed')
        return sol.y[:,-1]


def case(seed,index,split,*,omitted=False,inquiry=False):
    rng=np.random.default_rng(stable_seed('CONCEPT-008',seed,index,split))
    # Signed drive gain is actuator orientation, not a negative inertial mass.
    w=World(float(rng.uniform(.7,1.3)*rng.choice([-1,1])),
            float(rng.uniform(-.7,.7)) if index%4 else 0.,
            float(rng.uniform(-.2,.2)) if index%3 else 0.,
            float(rng.uniform(-.5,.5)),float(rng.uniform(.4,.8)) if omitted else 0.)
    n=2 if inquiry else int(rng.integers(2,13))
    x=rng.uniform(-2,2,(n,2))
    if inquiry:x*=.12
    y=w.observe(x[:,0],x[:,1])+rng.normal(0,.03,n)
    support=np.column_stack((x,y)).astype('float32')
    queries=rng.uniform(-2,2,(12,2)).astype('float32')
    return w,support,queries


def direction(w,query,route):
    changed=np.array(query,dtype=float);changed[1 if route==0 else 0]+=.5
    difference=float(w.observe(*changed)-w.observe(*query))
    return 2 if difference>.08 else 0 if difference<-.08 else 1
