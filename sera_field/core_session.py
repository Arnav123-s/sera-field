"""Persistent questions and independently credited updates of the CORE-022 owner.

The inherited event/receipt protocol is unchanged. Only construction and owner
precision are specialized; a second answer model is never introduced.
"""
import os
import copy
from pathlib import Path
import uuid

import torch

from .core_owner import CoreOwner
from .core_adequacy import action_scale_diagnostic, adequacy_features
from .core_storage import protect_state, recover_state
from .joint_session import JointSession
from .native_data import identity
from .native_owner import NativeConfig, detached_state
from .model import weight_hash
from .records import sha256


class CoreSession(JointSession):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.refinements = []

    def propose_refinement(self):
        self.checked_owner()
        if self.pending is not None:
            raise ValueError('Resolve the existing investigation before proposing structural work')
        residuals, variances, receipts = [], [], []
        # Re-evaluate a finite prefix under this predictor. No hidden teacher
        # family or final target is accessed. Confidence and adequacy are kept
        # in separate fields and both reach the learned decision.
        for i, event in enumerate(self.events):
            if event['kind'] != 'measurement': continue
            with torch.no_grad():
                before = self.rebuild(self.events[:i])
                query = next(self.owner.parameters()).new_tensor([[[event['force'], event['velocity']]]])
                prediction = self.owner.physical_query(before, query)[0, 0]
            residuals.append(float(prediction.mean())-event['response'])
            variances.append(float(prediction.var(unbiased=False)))
            receipts.append(event['id'])
            if len(residuals) == 8: break
        with torch.no_grad():
            source = self.owner.encode_texts([self.goal['hypothesis']])
        diagnostic = action_scale_diagnostic(self.owner, self.state, source)
        inputs = adequacy_features(residuals, variances, diagnostic, source)
        with torch.no_grad():
            logits = self.owner.assess_adequacy(self.state, source, inputs)
            if self.owner.core.extension_size: logits[0, 2] = -torch.inf
            # No independent error evidence permits only continued observation.
            # This permission/qualification gate is separate from learned scores.
            if not receipts: logits[0, [0, 2]] = -torch.inf
        content = {'goal': copy.deepcopy(self.goal), 'source': self.source, 'weights': self.weights,
            'state': self.state_id(), 'events': identity(self.events), 'receipt_ids': receipts,
            'pre_observation_residuals': residuals, 'model_variances': variances,
            'scale_diagnostic': diagnostic, 'features': inputs[0].tolist(),
            'probabilities': logits.softmax(-1)[0].tolist(),
            'action': ('retain', 'investigate', 'attach')[int(logits.argmax(-1))],
            'status': 'candidate decision; structural change earns no correctness credit'}
        return {'id': identity(content), **content}

    def attach_for_retry(self, proposal, directory, *, size=4):
        self.checked_owner()
        content = {k: v for k, v in proposal.items() if k != 'id'}
        if (proposal.get('id') != identity(content) or proposal.get('weights') != self.weights
                or proposal.get('state') != self.state_id() or proposal.get('events') != identity(self.events)
                or proposal.get('goal') != self.goal or proposal.get('source') != self.source
                or proposal.get('action') != 'attach' or not proposal.get('receipt_ids') or self.pending is not None):
            raise ValueError('Current evidence-bound attachment decision required')
        if proposal != self.propose_refinement():
            raise ValueError('Changed refinement decision')
        directory = Path(directory)
        parent = directory/('parent-'+proposal['id'])
        parent_id = self.save(parent)
        old_optimizer = self.optimizer
        before_answer = self.answer()
        try:
            self.owner.install_extension(size)
            group = {k: v for k, v in old_optimizer.param_groups[0].items() if k != 'params'}
            if len(old_optimizer.param_groups) != 1:
                raise ValueError('This migration qualifies one AdamW parameter group')
            # Rebuild parameter order exactly as a fresh expanded constructor;
            # preserve every existing parameter object and optimizer moment.
            self.optimizer = torch.optim.AdamW([{'params': list(self.owner.parameters()), **group}])
            self.optimizer.state.update(old_optimizer.state)
            with torch.no_grad(): self.state = detached_state(self.rebuild())
            if not all(bool(torch.isfinite(v).all()) for v in self.state.values()):
                raise ValueError('Nonfinite attached situation')
            self.weights = weight_hash(self.owner)
            self.transition = None
            record = {'proposal': proposal, 'parent_session': parent_id,
                'parent_path': str(parent), 'old_weights': before_answer['weights'],
                'new_weights': self.weights, 'old_stalks': [8]*self.owner.config.nodes,
                'new_stalks': list(self.owner.core.attachment().enlarged.dimensions),
                'optimizer_existing_moments_preserved': True, 'history_reencoded': True,
                'original_goal': copy.deepcopy(self.goal), 'before_answer': before_answer,
                'returned_answer': self.answer(), 'qualification': 'constructed; independent useful-progress assessment pending'}
            record['id'] = identity(record); self.refinements.append(record)
            self.save(directory/('candidate-'+record['id']))
            return copy.deepcopy(record)
        except Exception:
            # Preserve failed candidate files and restore the exact earlier
            # usable owner/optimizer through their independent saved revision.
            restored = type(self).load(parent)
            self.__dict__.update(restored.__dict__)
            raise

    def storage_scope(self):
        return {'goal': identity(self.goal), 'source': self.source,
                'weights': self.weights, 'events': identity(self.events)}

    def checkpoint_extra(self, path):
        record = protect_state(self.state, self.storage_scope())
        directory = Path(path)/'protected'; directory.mkdir(parents=True, exist_ok=True)
        temporary = directory/(uuid.uuid4().hex+'.tmp')
        torch.save(record, temporary)
        digest = sha256(temporary); destination = directory/(digest+'.pt')
        if destination.exists():
            if sha256(destination) != digest:
                raise ValueError('Existing protected state changed')
            temporary.unlink()
        else:
            os.replace(temporary, destination)
        return {'refinements': copy.deepcopy(self.refinements), 'protected_state': {'file': destination.name, 'sha256': digest,
                'metadata_sha256': record['metadata_sha256'], 'storage': record['storage']}}

    def restore_extra(self, path, extra):
        entry = extra.get('protected_state')
        if not entry:
            raise ValueError('Coupled session needs its protected retained state')
        directory = Path(path)/'protected'; location = directory/entry['file']
        if location.resolve().parent != directory.resolve() or sha256(location) != entry['sha256']:
            raise ValueError('Changed protected-state file')
        record = torch.load(location, map_location='cpu', weights_only=False)
        if record['metadata_sha256'] != entry['metadata_sha256']:
            raise ValueError('Changed protected-state metadata')
        decoded, audit = recover_state(record, scope=self.storage_scope())
        if decoded.keys() != self.state.keys() or any(not torch.equal(decoded[k], self.state[k]) for k in decoded):
            raise ValueError('Protected retained state disagrees with independent event replay')
        self.state = decoded
        self.storage_recovery = audit
        self.refinements = copy.deepcopy(extra.get('refinements', []))

    @classmethod
    def owner_from_specification(cls, specification):
        configuration = dict(specification)
        if configuration.pop('type') != 'complete-core-candidate-022':
            raise ValueError('Unexpected coupled owner type')
        configuration.pop('status')
        size = configuration.pop('extension_size')
        owner = CoreOwner(NativeConfig(**configuration))
        if size: owner.install_extension(size)
        return owner
