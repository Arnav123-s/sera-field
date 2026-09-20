"""Finite gapped-band codec for numerical density values.

The code stores quantized values, not truth. Semantic scope and evidence remain
external to the invariant. General perturbations use the lattice charge audit;
the fast decoder is exact only for the stated scalar-mass Hamiltonian family.
"""
import numpy as np
import torch


def qwz_chern(mass, *, grid=12, perturbation=None):
    if grid < 6:
        raise ValueError('Momentum grid too small for this audit')
    k = np.arange(grid)*2*np.pi/grid
    x,y = np.meshgrid(k,k,indexing='ij')
    d = np.stack((np.sin(x),np.sin(y),mass+np.cos(x)+np.cos(y)),-1)
    if perturbation is not None:
        d = d+np.asarray(perturbation)
    h = np.empty((grid,grid,2,2),dtype=complex)
    h[...,0,0]=d[...,2];h[...,1,1]=-d[...,2]
    h[...,0,1]=d[...,0]-1j*d[...,1];h[...,1,0]=d[...,0]+1j*d[...,1]
    values,vectors=np.linalg.eigh(h)
    gap=float(np.min(values[...,1]-values[...,0]))
    if gap < 1e-7:
        raise ValueError('Spectral gap closed; charge does not qualify this code')
    occupied=vectors[...,0]
    links=[]
    for axis in (0,1):
        link=np.sum(occupied.conj()*np.roll(occupied,-1,axis=axis),axis=-1)
        if np.min(np.abs(link)) < 1e-8:
            raise ValueError('Singular lattice overlap; refine the momentum audit')
        links.append(link/np.abs(link))
    u,v=links
    curvature=np.angle(u*np.roll(v,-1,axis=0)*np.conj(np.roll(u,-1,axis=1))*np.conj(v))
    charge=float(curvature.sum()/(2*np.pi))
    return {'charge':charge,'integer':int(round(charge)),'gap':gap,'grid':grid}


def encode_density(values):
    if not torch.isfinite(values).all() or bool(((values<.1)|(values>.9)).any()):
        raise ValueError('Density codec range is [0.1,0.9]')
    integers=torch.round((values-.1)/.8*255).to(torch.int64)
    bits=(integers[...,None] >> torch.arange(8)) & 1
    return torch.where(bits.bool(),-torch.ones_like(bits,dtype=values.dtype),
                       torch.ones_like(bits,dtype=values.dtype))


def decode_density(masses):
    # Exact phase boundaries for d=(sin kx,sin ky,m+cos kx+cos ky).
    if not torch.isfinite(masses).all() or bool(((masses.abs()<=.05)|(masses.abs()>=1.95)).any()):
        raise ValueError('Outside the certified nonzero QWZ phase intervals')
    bits=(masses<0).to(masses.dtype)
    integers=(bits*(2**torch.arange(8))).sum(-1)
    return .1+.8*integers/255
