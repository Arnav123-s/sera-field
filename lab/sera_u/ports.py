"""Explicit public senses. No task object survives this boundary."""
from dataclasses import dataclass
import hashlib
import json
import math

from sera import lang as LG, tasks as TS


class PortBudget(ValueError):
    """The complete public input exceeds this declared pilot budget."""


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def observed(value):
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError('A nonfinite measurement needs an explicit missing value')
        return value
    if isinstance(value, (list, tuple)):
        return tuple(observed(x) for x in value)
    raise TypeError(f'Not an allowed observed value: {type(value).__name__}')


@dataclass(frozen=True)
class TaskView:
    inputs: tuple
    out: str
    examples: tuple = ()                 # (sorted ((input name, value), ...), public output)
    queries: tuple = ()                  # sorted input bindings, never query answers
    words: tuple = ()
    measurements: tuple = ()             # raw action/object/time/x/v/uncertainty, with missing masks
    form: str = 'exact'
    hypotheses: tuple = ()               # imagined rows ('hypothetical-*' names): never facts; their own role port

    def __post_init__(self):
        object.__setattr__(self, 'inputs', tuple(tuple(x) for x in self.inputs))
        object.__setattr__(self, 'examples', tuple((tuple((k, observed(v)) for k, v in bindings), observed(y))
                                                 for bindings, y in self.examples))
        object.__setattr__(self, 'queries', tuple(tuple((k, observed(v)) for k, v in bindings) for bindings in self.queries))
        object.__setattr__(self, 'measurements', tuple(observed(row) for row in self.measurements))
        object.__setattr__(self, 'words', tuple(self.words))
        object.__setattr__(self, 'hypotheses', tuple(tuple((k, observed(v)) for k, v in row) for row in self.hypotheses))
        if any(not str(k).startswith('hypothetical-') for row in self.hypotheses for k, _ in row):
            raise ValueError('An imagined row needs hypothetical-* names')
        if self.form not in ('exact', 'strengths'):
            raise ValueError('Unknown public task form')
        if tuple(sorted(self.inputs)) != self.inputs or len(dict(self.inputs)) != len(self.inputs):
            raise ValueError('Input names must be unique and sorted')
        for bindings, answer in self.examples:
            if tuple(k for k, _ in bindings) != tuple(k for k, _ in self.inputs):
                raise ValueError('Examples need exactly the public input bindings')
            observed(answer)
            for _, v in bindings:
                observed(v)
        for bindings in self.queries:
            if tuple(k for k, _ in bindings) != tuple(k for k, _ in self.inputs):
                raise ValueError('Queries need exactly the public input bindings')
        if any(type(w) is not str for w in self.words):
            raise TypeError('Only actually heard text is a text sense')

    @classmethod
    def from_task(cls, task):
        # Deliberate allowlist: never copy __dict__, context(), subject, name, grade,
        # _target, _fresh, _truth_words, certificates, or a teacher's solution.
        inputs = tuple(sorted(task.inputs.items()))
        if task.form == 'strengths':
            rows = []
            from ccops5.core import paths
            for throw_index, throw in enumerate(task.throws):
                for j, (x, v) in enumerate(zip(throw.x, throw.v)):
                    rows.append(('motion', int(throw.situation), throw_index, j*paths.DT_OBS, float(x), float(v)))
                starts, ends, forces = throw.action.arrays()
                rows.extend(('push', throw_index, float(a), float(b), float(f))
                            for a, b, f in zip(starts, ends, forces))
            return cls(inputs, task.out, words=tuple(TS.text(w) for w in task.words),
                       measurements=tuple(rows), form='strengths')
        if len(inputs) != 1:
            raise PortBudget('The task adapter requires explicit bindings for multiple inputs')
        var = inputs[0][0]
        examples = tuple((((var, observed(x)),), observed(y)) for x, y in task.data)
        queries = tuple(tuple((k, observed(p[k])) for k, _ in inputs) for p in task.probes())
        return cls(inputs, task.out, examples, queries, tuple(TS.text(w) for w in task.words))

    @property
    def identity(self):
        # A view with no imagined rows keeps the identity it had before the hypothetical channel (U3).
        return digest({k: v for k, v in self.__dict__.items() if k != 'hypotheses' or v})

    def records(self, max_examples=4, max_list=8, max_tokens=256, max_records=128):
        """Pair order is irrelevant; sequence order within each value is retained.

        Every record has its own role/position/missing ports. Oversized values
        fail, never get silently truncated. Repeated examples remain repeated.
        """
        if len(self.examples) > max_examples:
            raise PortBudget('More than four public examples; declare a larger port budget')
        records = []

        def encode(value, out, depth=0):
            if depth > 8:
                raise PortBudget('Nested value exceeds depth eight')
            if value is None:
                out.append(('missing', 0., 0., 0.))
            elif type(value) is bool:
                out.append(('bool:1' if value else 'bool:0', 0., 0., 1.))
            elif type(value) in (int, float):
                token = ('int:' + str(value)) if type(value) is int else ('real:' + value.hex())
                scale = math.log1p(abs(value))
                out.append((token, math.copysign(1., value) if value else 0.,
                            scale / (1. + scale), 1.))
            elif type(value) is str:
                out.extend((word, 0., 0., 1.) for word in value.split())
            else:
                if len(value) > max_list:
                    raise PortBudget('A list exceeds length eight')
                out.append(('open:' + str(depth), 0., len(value)/max_list, 1.))
                for item in value:
                    encode(item, out, depth+1)
                out.append(('close:' + str(depth), 0., 0., 1.))

        def add(kind, values):
            row = [('role:' + kind, 0., 0., 1.)]
            for key, value in values:
                row.append(('binding:' + key, 0., 0., 1.))
                encode(value, row)
            if len(row) > max_tokens:
                raise PortBudget('A complete record exceeds 256 tokens')
            records.append(tuple(row))

        add('schema', [('in:' + name, typ) for name, typ in self.inputs] + [('out', self.out)])
        for bindings, y in sorted(self.examples, key=repr):
            add('pair', list(bindings) + [('public-output', y)])
        for bindings in sorted(self.queries, key=repr):
            add('query', bindings)
        if self.words:
            add('heard', [('text', ' '.join(self.words))])
        for row in self.measurements:
            add('measurement', [('raw', row)])
        for row in self.hypotheses:                  # in the order imagined: a candidate, then its predictions
            add('hypothetical', row)
        if max_records is not None and len(records) > max_records:
            raise PortBudget('More than 128 complete observed records')
        return tuple(records)
