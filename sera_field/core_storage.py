"""Exact byte recovery into the coupled owner's actual retained coordinates.

Each byte is represented by one five-qubit code cell; its eight bits are also
recorded as scalar-mass QWZ phases. Neither representation certifies meaning.
The byte digest, schema and goal/predictor/evidence scope qualify a recovery.
This is finite classical storage, with its actual expansion reported explicitly.
"""
import copy
import hashlib
import math

import torch

from .native_data import identity
from .perfect_tensor_memory import encode_density, decode_density
from .topological_memory import encode_density as chern_encode, decode_density as chern_decode


DTYPES = {str(t): t for t in (torch.float32, torch.float64, torch.int64, torch.bool)}
MAX_BYTES = 65536


@torch.no_grad()
def protect_state(state, scope):
    if not isinstance(scope, dict) or any(not scope.get(k) for k in ('goal', 'source', 'weights', 'events')):
        raise ValueError('Bind retained coordinates to goal, predictor, source and observed history')
    layout, pieces = [], []
    for key, value in sorted(state.items()):
        if not isinstance(value, torch.Tensor) or str(value.dtype) not in DTYPES or not bool(torch.isfinite(value).all()):
            raise ValueError('Finite supported retained tensors required')
        value = value.detach().cpu().contiguous()
        raw = value.reshape(-1).view(torch.uint8)
        layout.append({'name': key, 'shape': list(value.shape), 'dtype': str(value.dtype), 'bytes': raw.numel()})
        pieces.append(raw)
    raw = torch.cat(pieces)
    if not 0 < raw.numel() <= MAX_BYTES:
        raise ValueError('Retained state exceeds the declared finite storage allocation')
    levels = raw.double()/255
    code = encode_density(levels)
    topology = chern_encode(.1+.8*levels)
    metadata = {'schema': 'coupled-state-byte-code-022', 'scope': copy.deepcopy(scope), 'layout': layout,
                'payload_sha256': hashlib.sha256(raw.numpy().tobytes()).hexdigest(),
                'bytes': raw.numel(), 'semantics': 'protected observed coordinates, not certified truth'}
    result = {'metadata': metadata, 'metadata_sha256': identity(metadata), 'code': code, 'topology': topology,
              'storage': {'raw_bytes': raw.numel(), 'code_bytes': code.numel()*code.element_size(),
                          'topology_bytes': topology.numel()*topology.element_size(),
                          'scope': 'stored arrays; excludes serialization, recovery and process memory'}}
    recovered, _ = recover_state(result, scope=scope)
    if any(not torch.equal(recovered[k], v.detach().cpu()) for k, v in state.items()):
        raise ValueError('Protected retained coordinates did not round trip exactly')
    return result


@torch.no_grad()
def recover_state(record, *, scope, erasures=()):
    metadata = record['metadata']
    if identity(metadata) != record['metadata_sha256'] or metadata['scope'] != scope:
        raise ValueError('Changed storage identity or stale goal/predictor/evidence scope')
    count = metadata['bytes']
    if (metadata['schema'] != 'coupled-state-byte-code-022' or type(count) is not int
            or not 0 < count <= MAX_BYTES or record['code'].shape != (count, 32)
            or record['topology'].shape != (count, 8)):
        raise ValueError('Invalid finite protected-state layout')
    decoded, syndrome = decode_density(record['code'], erasures=erasures)
    levels = (255*decoded).round()
    if not bool(((levels >= 0) & (levels <= 255)).all()) or not torch.allclose(255*decoded, levels, atol=1e-5, rtol=0):
        raise ValueError('Recovery does not represent byte levels within the noise contract')
    phase_levels = ((chern_decode(record['topology'])-.1)/.8*255).round()
    if not torch.equal(levels, phase_levels):
        raise ValueError('Protected payload and topological phases disagree')
    raw = levels.to(torch.uint8).cpu().numpy().tobytes()
    if hashlib.sha256(raw).hexdigest() != metadata['payload_sha256']:
        raise ValueError('Recovered payload failed independent byte integrity')
    restored, cursor = {}, 0
    for row in metadata['layout']:
        if row['name'] in restored or row['dtype'] not in DTYPES or any(type(d) is not int or d < 0 for d in row['shape']):
            raise ValueError('Invalid protected coordinate schema')
        dtype = DTYPES[row['dtype']]
        size = math.prod(row['shape'])*torch.empty((), dtype=dtype).element_size()
        if size != row['bytes'] or cursor+size > count:
            raise ValueError('Protected coordinate size mismatch')
        value = (torch.frombuffer(bytearray(raw[cursor:cursor+size]), dtype=dtype).clone()
                 if size else torch.empty(0, dtype=dtype))
        restored[row['name']] = value.reshape(row['shape']); cursor += size
    if cursor != count:
        raise ValueError('Unclaimed protected coordinate bytes')
    return restored, {'exact_bytes_verified': True, 'scope_verified': True,
                      'syndrome_probability': syndrome.sum(0).tolist(), 'decoded_bytes': count}
