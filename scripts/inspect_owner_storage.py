"""Separate actual owner storage, training state and one semantic-call tape.

This is resource instrumentation, not a scientific accuracy assessment. It does
not train, qualify a successor, or open an evaluation cohort.
"""
import argparse
import json
import os
from pathlib import Path
import sys

import torch

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.model import weight_hash
from sera_field.records import sha256, write_json


def tensors(value, prefix=''):
    if isinstance(value, torch.Tensor):
        yield prefix, value
    elif isinstance(value, dict):
        for key, child in value.items():
            yield from tensors(child, prefix + '/' + str(key))
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            yield from tensors(child, prefix + '/' + str(index))


def tensor_storage(named):
    named = list(named); storage = {}
    for _, value in named:
        backing = value.untyped_storage()
        key = (str(value.device), backing.data_ptr(), backing.nbytes())
        storage[key] = backing.nbytes()
    return {'logical_bytes': sum(value.numel() * value.element_size() for _, value in named),
            'unique_backing_bytes': sum(storage.values()), 'tensor_count': len(named),
            'elements': sum(value.numel() for _, value in named)}


def revision(root, pointer):
    record = json.loads((root / pointer).read_text())
    path = root / 'revisions' / record['revision']
    if path.resolve().parent != (root / 'revisions').resolve() or sha256(path) != record['sha256']:
        raise ValueError('Storage inspection requires the exact registered revision')
    return path, record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--kind', choices=('semantic', 'history', 'genre'), required=True)
    parser.add_argument('--owner', required=True); parser.add_argument('--training')
    parser.add_argument('--output', required=True); args = parser.parse_args()
    if not os.environ.get('SERA_FIELD_SUPERVISED'):
        raise SystemExit('Use scripts/supervise.py')
    torch.set_num_threads(1)
    output = (ROOT / args.output).resolve()
    if not output.is_relative_to(ROOT / 'reports') or output.exists():
        raise ValueError('Use a fresh report filename inside this laboratory')
    if args.kind == 'semantic':
        from sera_field.semantic_training import load_semantic as load_owner
    elif args.kind == 'history':
        from sera_field.history_training import load_history as load_owner
    else:
        from sera_field.genre_training import load_genre as load_owner
    root = (ROOT / args.owner).resolve(); checkpoint, selection = revision(root, 'SELECTION.json')
    owner, loaded = load_owner(root); owner.eval()
    if loaded != selection: raise ValueError('Owner identity changed during inspection')
    before = weight_hash(owner)
    parameters = dict(owner.named_parameters()); buffers = dict(owner.named_buffers())
    result = {'owner': str(root.relative_to(ROOT)), 'selection': selection,
        'selected_revision_file_bytes': checkpoint.stat().st_size,
        'revision_role': 'packaged inference' if root.is_relative_to(ROOT / 'checkpoints') else 'local study revision; may contain training state',
        'parameters': tensor_storage(parameters.items()), 'buffers': tensor_storage(buffers.items()),
        'persistent_tensors': tensor_storage([*parameters.items(), *buffers.items()]),
        'buffer_categories': {prefix: tensor_storage((k, v) for k, v in buffers.items() if k.startswith(prefix))
                              for prefix in ('field.history_', 'field.curvature_memory.', 'field.memory.')},
        'specification': owner.specification(),
        'scope': 'Logical tensor bytes and unique backing allocations; not peak process memory or an asymptotic complexity claim.'}
    if args.training:
        training = (ROOT / args.training).resolve()
        path, saved = revision(training, 'revisions/CURRENT.json')
        payload = torch.load(path, map_location='cpu', weights_only=False)
        progress = payload['progress']
        result['resumable_training'] = {'revision': saved, 'file_bytes': path.stat().st_size,
            'all_saved_tensors': tensor_storage(tensors(payload)),
            'optimizer_tensors': tensor_storage(tensors(progress.get('optimizer', {}))),
            'scope': 'Latest committed training state, separately loaded; not summed into inference storage.'}
        del payload
    # All probes use explicit engineering inputs, without source/final labels.
    source = torch.zeros(1, owner.config['nodes'], 3)
    with torch.no_grad():
        state, features = owner.field.imagine(source)
    result['single_field_boundary'] = {'batch': 1, 'input': tensor_storage([('source', source)]),
        'returned_state': tensor_storage([('state', state)]),
        'returned_features': tensor_storage([('features', features)]),
        'scope': 'Returned state only; excludes internal workspaces, parameters and caller storage.'}
    # Count the actual saved tensors for the complete human semantic route, with
    # each current parameter trainable. Keep references so allocations cannot be
    # recycled and counted as a different tensor with the same data address.
    for parameter in owner.parameters(): parameter.requires_grad_(True)
    saved_tensors = []
    def pack(value):
        saved_tensors.append(value); return value
    request = {'premise': 'A person is holding a flower.', 'hypothesis': 'Someone is holding a flower.'}
    with torch.autograd.graph.saved_tensors_hooks(pack, lambda value: value):
        logits = owner.semantic([request['premise']], [request['hypothesis']])
    result['semantic_differentiation_tape'] = {
        **tensor_storage([(str(i), value) for i, value in enumerate(saved_tensors)]),
        'batch': 1, 'request': request, 'finite_output': bool(torch.isfinite(logits).all()),
        'scope': 'Saved tensors for one complete semantic forward, including encoder, three branches and readout; all parameters require gradients, no backward/update performed.'}
    result['weights_after'] = weight_hash(owner)
    if result['weights_after'] != before or not result['semantic_differentiation_tape']['finite_output']:
        raise ValueError('Storage inspection changed retained tensors or yielded nonfinite output')
    result['attempt'] = Path(os.environ['SERA_FIELD_ATTEMPT']).name
    result['script_sha256'] = sha256(__file__)
    write_json(output, result)
    print(json.dumps({key: result[key] for key in ('owner', 'parameters', 'buffers', 'persistent_tensors')}))


if __name__ == '__main__': main()
