"""Environmental search hints accumulated from checked outcomes."""

import json
import math

import numpy as np

from . import grammar


class Board:
    """Trails, misfit hotspots, and pairs that need a better experiment."""

    def __init__(self, rho=0.1, tau_min=0.05, grid=8, corrections_registry=None):
        self.rho = rho
        self.tau_min = tau_min
        self.grid = grid
        self.corrections_registry = corrections_registry if corrections_registry is not None else set()
        self.trails = {idea: 1.0 for idea in grammar.IDEAS}
        self.hotspots = np.zeros((grid, grid))
        self.lookalikes = {}
        self.audit = []

    def deposit_certificate(self, library, claim):
        if not any(c is claim for c in library.claims) or not claim.sure:
            raise ValueError('unchecked deposit')
        amounts = []
        for idea in claim.family:
            self.trails[idea] += 1.0
            amounts.append([list(idea), 1.0])
        self.audit.append({'kind': 'certificate', 'source_id': claim.certificate.digest,
                           'amounts': amounts})

    def deposit_correction(self, correction):
        if (not all(key in correction for key in ('id', 'family', 'issued_by'))
                or correction.get('issued_by') != 'teacher'
                or correction.get('id') not in self.corrections_registry):
            raise ValueError('unchecked deposit')
        amounts = []
        for idea in correction['family']:
            self.trails[idea] += 0.5
            amounts.append([list(idea), 0.5])
        self.audit.append({'kind': 'correction', 'source_id': correction['id'],
                           'amounts': amounts})

    def deposit_alarm(self, log_e, threshold, cells):
        if log_e < threshold or not cells:
            raise ValueError('unchecked deposit')
        amount = log_e / len(cells)
        for row, col in cells:
            self.hotspots[row, col] += amount
        self.audit.append({'kind': 'alarm', 'source_id': None,
                           'amounts': [[row, col, amount] for row, col in cells]})

    def mark_lookalike(self, family_a, family_b):
        pair = tuple(sorted((grammar.name(family_a), grammar.name(family_b))))
        self.lookalikes[pair] = self.lookalikes.get(pair, 0.0) + 1.0
        self.audit.append({'kind': 'lookalike', 'source_id': list(pair), 'amounts': 1.0})

    def evaporate(self):
        factor = 1 - self.rho
        for idea in self.trails:
            self.trails[idea] = max(self.tau_min, factor * self.trails[idea])
        self.hotspots *= factor
        self.lookalikes = {pair: amount * factor for pair, amount in sorted(self.lookalikes.items())
                           if amount * factor >= 0.01}

    def trail_score(self, family):
        return sum(math.log(self.trails[idea]) for idea in family)

    def placement_hint(self):
        if self.lookalikes:
            pair = max(sorted(self.lookalikes), key=lambda p: self.lookalikes[p])
            if self.lookalikes[pair] >= 2.0:
                return 'large', None
        row, col = np.unravel_index(int(np.argmax(self.hotspots)), self.hotspots.shape)
        if (self.hotspots[row, col] >= 1.0
                and (col < self.grid / 4 or col >= 3 * self.grid / 4)):
            return 'fast', None
        return None

    def cell_of(self, x_norm, v_norm):
        def index(value):
            return min(self.grid - 1, max(0, int((float(value) + 1) * self.grid / 2)))

        return index(x_norm), index(v_norm)

    def to_json(self):
        return json.dumps({
            'rho': self.rho,
            'tau_min': self.tau_min,
            'grid': self.grid,
            'trails': [[list(idea), amount] for idea, amount in self.trails.items()],
            'hotspots': self.hotspots.tolist(),
            'lookalikes': [[list(pair), amount] for pair, amount in sorted(self.lookalikes.items())],
            'audit': self.audit,
        }, sort_keys=True)

    @classmethod
    def from_json(cls, text):
        data = json.loads(text)
        board = cls(data['rho'], data['tau_min'], data['grid'])
        board.trails = {tuple(idea): amount for idea, amount in data['trails']}
        board.hotspots = np.array(data['hotspots'], dtype=float)
        board.lookalikes = {tuple(pair): amount for pair, amount in data['lookalikes']}
        board.audit = data['audit']
        return board
