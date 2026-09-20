"""The continuing owner with a finite neural-field action in its boundary path."""
import torch

from .finite_neural_action import FiniteNeuralAction
from .gauge import adjoint_rotations
from .history_owner import HistoryField, HistoryOwner


class EnsembleField(HistoryField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ensemble_action = FiniteNeuralAction(self.nodes)
        self.action_mode = 'exact'; self.teaching_noise = 0.
        self.last_action_source = None

    def imagine(self, source, previous=None, *, use_imagination=True):
        self.last_action_source = source.detach().clone()
        transport = adjoint_rotations(self.links).transpose(-1, -2)
        updated = self.ensemble_action(source, transport, mode=self.action_mode,
            noise=self.teaching_noise if self.training else 0.)
        return super().imagine(updated, previous, use_imagination=use_imagination)


class GenreOwner(HistoryOwner):
    def __init__(self, *args, action_kind='exact', teaching_noise=0.03, **kwargs):
        if action_kind not in {'exact', 'gaussian'} or teaching_noise not in {0., .03}:
            raise ValueError('Use a prospectively specified action/noise arm')
        super().__init__(*args, **kwargs)
        self.action_kind = action_kind; self.teaching_noise = teaching_noise
        self.field = EnsembleField(self.config['nodes'], self.config['rounds'],
                                  backend=self.field.backend, steps=self.field.steps)
        self.field.action_mode = action_kind; self.field.teaching_noise = teaching_noise

    def specification(self):
        return {**super().specification(), 'type': 'finite-neural-action-017',
                'action_kind': self.action_kind, 'teaching_noise': self.teaching_noise}


def extend_genre(parent, *, action_kind='exact', teaching_noise=.03, seed=17117):
    torch.manual_seed(seed)
    spec = dict(parent.specification()); spec.pop('type')
    owner = GenreOwner(**spec, action_kind=action_kind, teaching_noise=teaching_noise)
    result = owner.load_state_dict(parent.state_dict(), strict=False)
    allowed = ('field.ensemble_action.',)
    if parent.specification()['type'] == 'curvature-semantic-015':
        allowed += ('field.continuum.', 'field.raw_history_gain', 'field.history_', 'field._extra_state')
    if result.unexpected_keys or any(not key.startswith(allowed) for key in result.missing_keys):
        raise ValueError('Unexpected finite-field parent incompatibility')
    return owner
