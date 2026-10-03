"""Fresh complete-core candidate, under construction before curriculum launch.

Reuses input/readout engineering from NativeOwner, never its learned tensors.
Observed and conditional histories evolve through the same coupled energy.
The complete-core acceptance ledger records the further connections required
before this candidate may start its curriculum.
"""
import torch
from torch import nn

from .clifford_sheaf import lift_rotation, typed_source
from .continuum_core import ConditionalGaugeFlow
from .fibonacci_space import FibonacciSpace
from .gauge import group_from_coordinates
from .native_owner import NativeOwner, NativeConfig, select_state
from .situation_core import loop_feature
from .stationary_field import stationary
from .unified_energy import UnifiedEnergy
from .core_proposals import GraphProposal


class ConditionalFusion(nn.Module):
    """A learned mixture of stated braid words, with all path outcomes retained.

    Encoding produces a normalized pure state; a convex mixture of unitary braid
    channels gives a positive trace-one density. This is a finite classical
    simulation. Its labels are latent paths, not independently verified facts.
    """
    def __init__(self, nodes):
        super().__init__()
        self.encoding = nn.Linear(6*nodes, 18)
        space = FibonacciSpace(4, 1)
        a, b, c = (space.braid(i) for i in (1, 2, 3))
        operators = torch.stack((torch.eye(3, dtype=torch.complex128), a, b, c, a @ b, b @ a))
        self.register_buffer('braid_operators', operators)

    def forward(self, retained, query, *, measurement='none', outcome=None):
        if measurement not in ('none', 'unread', 'read') or (measurement == 'read') != (outcome is not None):
            raise ValueError('Declare absent, unread or one explicit read outcome')
        if outcome is not None and (type(outcome) is not int or not 0 <= outcome < 3):
            raise ValueError('A valid fusion-path outcome is required')
        encoded = self.encoding(torch.cat((retained.flatten(1), query.flatten(1)), -1))
        magnitude, phase, mixture, continuation = encoded[:, :3], encoded[:, 3:6], encoded[:, 6:12], encoded[:, 12:]
        amplitude = torch.polar(magnitude.softmax(-1).sqrt(), torch.pi*phase.tanh())
        operators = self.braid_operators.to(amplitude)
        outcomes = torch.einsum('kij,bj->bki', operators, amplitude)
        density = torch.einsum('bk,bki,bkj->bij', mixture.softmax(-1).to(outcomes), outcomes, outcomes.conj())
        measured_probabilities = density.diagonal(dim1=-2, dim2=-1).real
        unread = torch.diag_embed(measured_probabilities).to(density)
        # The measurement is followed by a channel that need not commute with
        # it. Thus absent and unread measurements have distinct consequences,
        # not merely distinct metadata with an identical downstream calculation.
        projectors = torch.diag_embed(torch.eye(3, device=density.device, dtype=measured_probabilities.dtype)).to(density)
        subnormalized = measured_probabilities[:, :, None, None]*projectors[None]
        current = density if measurement == 'none' else unread
        if measurement == 'read':
            if bool((measured_probabilities[:, outcome] <= 0).any()):
                raise ValueError('An impossible path has no conditional continuation')
            current = projectors[outcome].expand_as(density)
        transformed = operators[None] @ current[:, None] @ operators.mH[None]
        continued = (continuation.softmax(-1)[:, :, None, None]*transformed).sum(1)
        probabilities = continued.diagonal(dim1=-2, dim2=-1).real
        # Reading the complete left-associated path basis yields three rank-one
        # outcomes. The unread channel keeps only that basis diagonal. Neither
        # is silently assigned to the factual state.
        return {'density': density, 'path_probabilities': probabilities,
                'measurement_probabilities': measured_probabilities, 'subnormalized_outcomes': subnormalized,
                'unread_density': unread, 'continued_density': continued,
                'measurement': measurement, 'outcome': outcome,
                'word_probabilities': mixture.softmax(-1), 'continuation_probabilities': continuation.softmax(-1)}


class CoreOwner(NativeOwner):
    def __init__(self, config=None, *, program_slots=4):
        super().__init__(config or NativeConfig())
        if self.config.branches != 3:
            raise ValueError('The pinned four-tau, total-tau construction has three path branches')
        # Remove the previous equation, rather than silently registering two
        # independent memories or unused inherited field parameters.
        del self.field, self.memory, self.observation_write, self.raw_memory_gain
        self.core = UnifiedEnergy(self.config.nodes)
        self.flow = ConditionalGaugeFlow(self.config.nodes)
        self.fusion = ConditionalFusion(self.config.nodes)
        self.raw_observation_port = nn.Parameter(torch.tensor(0.))
        self.raw_stationary = nn.Parameter(torch.tensor(0.))
        self.raw_curvature_tag = nn.Parameter(torch.tensor(0.))
        self.adequacy_policy = nn.Sequential(nn.Linear(72, 24), nn.Tanh(), nn.Linear(24, 3))
        # Zero slots is only for exact reconstruction of the preserved earlier
        # engineering specification. New candidates own fresh proposal weights.
        self.program_slots = program_slots
        if program_slots:
            self.program_map = GraphProposal(program_slots)

    def specification(self):
        return {'type': 'complete-core-candidate-022', **vars(self.config),
                **({'program_slots': self.program_slots} if self.program_slots else {}),
                'extension_size': self.core.extension_size,
                'status': 'engineering; complete acceptance precedes curriculum'}

    def install_extension(self, size):
        self.core.install_extension(size)
        self.extension_port = nn.Linear(self.config.nodes*3, size).to(self.core.prior)
        self.extension_readout = nn.Linear(size+1, 64, bias=False).to(self.core.prior)
        nn.init.zeros_(self.extension_readout.weight)

    def empty(self, batch):
        state = self.core.empty(batch)
        ref = state['q']
        return {**state, 'marks': ref.new_zeros(batch, 2),
                'flow_context': ref.new_zeros(batch, 4),
                'events': torch.zeros(batch, dtype=torch.int64, device=ref.device)}

    def transport(self):
        return self.core.geometry()[0]

    def remembered(self, state):
        _, anchors = self.core.geometry()
        bulk = (anchors[None] @ state['bulk'].mean((1, 2))[..., None]).squeeze(-1)
        # Boundary history and the slower variables are coordinates of one
        # situation, all active from the first input. No raw premise is bypassed
        # into the answer map at query time.
        return (state['q'][..., [1, 2, 4]]+state['fast']+state['slow']+bulk)/4

    def transition(self, state, source, *, observed):
        if source.shape != state['fast'].shape or not bool(torch.isfinite(source).all()):
            raise ValueError('Finite source coordinates in this situation are required')
        transport, _ = self.core.geometry()
        current = torch.stack((source.square().mean((-1, -2)),
            state['fast'].square().mean((-1, -2)), state['marks'][:, 0], state['marks'][:, 1]), -1)
        context = .5*state['flow_context']+.5*current
        flowed, logdet = self.flow(source, context, transport)
        coefficient = .25+self.raw_stationary.sigmoid()
        settled = stationary(flowed, transport, coefficient)
        # A measured port and a hypothetical goal port share the numerical map.
        # Only the former returns an observed event; their states never alias.
        restrictions = lift_rotation(transport)
        injection = typed_source(settled, restrictions)
        before, _ = self.core.energy(state, settled)
        port = .1+.4*self.raw_observation_port.sigmoid()
        actual = {k: state[k] for k in (*self.core.coordinates, 'reservoir')}
        # Curvature changes the input coupling rather than becoming a substitute
        # for temporal derivative eligibility or independent correctness.
        tag = loop_feature(group_from_coordinates(self.core.links), settled).to(source)
        gain = port*(1+.1*self.raw_curvature_tag.sigmoid()*tag.tanh())
        actual['q'] = (1-gain[:, None, None])*actual['q']+gain[:, None, None]*injection
        if self.core.extension_size:
            actual['extension'] = .8*actual['extension']+.2*self.extension_port(source.flatten(1)).tanh()
        after_port, _ = self.core.energy(actual, settled)
        port_work = after_port-before
        defects = source.new_zeros(len(source)); active_work = source.new_zeros(len(source))
        for _ in range(self.config.rounds):
            actual, evidence = self.core.coupled_step(actual, settled, dt=.02)
            defects = defects+evidence['discrete_balance_defect']
            active_work = active_work+evidence['active_work_integral']
        result = {**state, **actual, 'flow_context': context,
                  'events': state['events']+int(observed)}
        return result, {'conditional_logdet': logdet, 'port_work': port_work,
                        'energy_defect': defects, 'active_work_integral': active_work,
                        'curvature_tag': tag, 'source': settled}

    def observe(self, state, source, *, equal_rates=False, checked_progress=None, simple_trace=False):
        if equal_rates or simple_trace:
            raise ValueError('Register controls for the coupled equation; do not reuse a different memory ablation')
        result, diagnostics = self.transition(state, source, observed=True)
        if checked_progress is not None:
            if checked_progress.shape != state['marks'].shape[:1] or not bool(torch.isfinite(checked_progress).all()):
                raise ValueError('Finite independently checked progress is required')
            progress = checked_progress.detach()
            result['marks'] = .95*state['marks']+.05*torch.stack((progress.clamp_min(0), (-progress).clamp_min(0)), -1)
        return result, diagnostics

    def conditional(self, state, source, *, propagate=True, measurement='none', outcome=None):
        remembered = self.remembered(state)
        branches = self.fusion(remembered, source, measurement=measurement, outcome=outcome)
        weights = branches['path_probabilities']
        batch, nodes = source.shape[:2]
        proposal = (source[:, None] + (.1+.2*weights[:, :, None, None])
                    * self.branches.tanh()[None])
        indices = torch.arange(batch, device=source.device).repeat_interleave(3)
        copies = select_state(state, indices)
        proposed = proposal.reshape(batch*3, nodes, 3)
        if propagate:
            imagined, diagnostics = self.transition(copies, proposed, observed=False)
            field = imagined['q']
        else:
            imagined = copies
            field = typed_source(proposed, lift_rotation(self.transport()))
            diagnostics = {'control': 'bypass hypothetical propagation; preserve acquired state'}
        geometry = torch.cat((field.square().sum(-1).add(1e-8).sqrt(),
            loop_feature(group_from_coordinates(self.core.links), proposed).to(field)[:, None]), -1)
        relation = torch.cat((remembered, source, remembered*source, (remembered-source).abs()), -1)
        relation = relation.flatten(1)[:, None].expand(-1, 3, -1).reshape(batch*3, -1)
        output = self.joint_readout(torch.cat((relation, field.flatten(1), geometry), -1))
        if self.core.extension_size:
            output = output+self.extension_readout(torch.cat((imagined['extension'], imagined['disagreement']), -1))
        return output.reshape(batch, 3, -1), {**branches, 'hypothetical_state': imagined,
                                             'dynamics': diagnostics}

    def assess_adequacy(self, state, source, diagnostics):
        if diagnostics.shape != (len(source), 8) or not bool(torch.isfinite(diagnostics).all()):
            raise ValueError('Eight explicit scale and independently measured error features required')
        features = self.imagine(state, source).mean(1)
        return self.adequacy_policy(torch.cat((features, diagnostics), -1))

    def imagine(self, state, source, *, ablation=None):
        if ablation == 'erase_history':
            state = self.empty(len(source))
        elif ablation not in (None, 'no_imagination'):
            raise ValueError('Declare a coupled-core inference intervention explicitly')
        return self.conditional(state, source, propagate=ablation != 'no_imagination')[0]

    def program_distribution(self, state, questions, arities):
        if not self.program_slots:
            raise ValueError('This preserved owner predates executable graph proposals')
        features, branches = self.conditional(state, self.encode_texts(questions))
        return self.program_map(features, branches['path_probabilities'], arities)
