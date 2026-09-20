"""The same actual task owner with a typed Clifford graph-sheaf field."""
from .grounded_owner import GroundedOwner
from .clifford_sheaf import CliffordSheafField


class ScfeOwner(GroundedOwner):
    def __init__(self, width=48, nodes=8, rounds=4):
        super().__init__(width=width, nodes=nodes, rounds=rounds)
        self.field = CliffordSheafField(nodes, rounds, source_field=self.field)

    def specification(self):
        return {'type': 'clifford-sheaf-field-004', **self.config}
