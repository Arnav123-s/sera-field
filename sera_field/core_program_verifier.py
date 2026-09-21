"""Independent coefficient and finite-input contracts for proposed scalar graphs.

This checker shares the declared syntax, but neither the proposal executor nor
its computed answers. Targets stay outside the owner until independent review.
"""
from copy import deepcopy
from fractions import Fraction
from pathlib import Path

from .core_programs import BASE, CONSTANTS, UNARY, rational, validate
from .native_data import identity
from .records import sha256


def clean(poly):
    result = {p: rational(c) for p, c in poly.items() if c}
    if len(result) > 256 or any(sum(p) > 16 for p in result):
        raise ValueError('Declared polynomial degree or coefficient count exceeded')
    return result


def terms(poly):
    return [[list(p), str(c)] for p, c in sorted(clean(poly).items())]


def polynomial(program):
    """Recursive exact coefficient expansion, independently of execution."""
    validate(program); arity = program['arity']; zero = (0,)*arity
    cache = {}
    def add(a, b):
        result = dict(a)
        for p, c in b.items(): result[p] = result.get(p, Fraction(0))+c
        return clean(result)
    def multiply(a, b):
        result = {}
        for p, c in a.items():
            for q, d in b.items():
                key = tuple(x+y for x, y in zip(p, q))
                if sum(key) > 16: raise ValueError('Declared polynomial degree exceeded')
                result[key] = result.get(key, Fraction(0))+c*d
        return clean(result)
    def visit(ref):
        if ref < 4:
            powers = [0]*arity; powers[ref] = 1
            return {tuple(powers): Fraction(1)}
        if ref < BASE: return clean({zero: Fraction(CONSTANTS[ref-4])})
        if ref in cache: return cache[ref]
        op, left, right = program['nodes'][ref-BASE]; a = visit(left)
        b = a if op in UNARY else visit(right)
        if op == 'add': result = add(a, b)
        elif op == 'sub': result = add(a, {p: -c for p, c in b.items()})
        elif op in ('mul', 'square'): result = multiply(a, b)
        elif op == 'neg': result = {p: -c for p, c in a.items()}
        elif op == 'div':
            if set(b) != {zero} or b[zero] == 0:
                raise ValueError('Polynomial proof requires a nonzero constant denominator')
            result = clean({p: c/b[zero] for p, c in a.items()})
        else:
            raise ValueError('Piecewise operation requires finite execution or a different proof contract')
        cache[ref] = result; return result
    return visit(program['output'])


def independently_execute(program, inputs):
    """Recursive exact evaluator; deliberately separate from iterative executor."""
    validate(program)
    if len(inputs) != program['arity']: raise ValueError('Independent input arity mismatch')
    values = list(map(rational, inputs)); cache = {}
    def visit(ref):
        if ref < 4: return values[ref]
        if ref < BASE: return Fraction(CONSTANTS[ref-4])
        if ref in cache: return cache[ref]
        op, left, right = program['nodes'][ref-BASE]; a = visit(left)
        b = a if op in UNARY else visit(right)
        operations = {'add': lambda: a+b, 'sub': lambda: a-b, 'mul': lambda: a*b,
            'div': lambda: a/b, 'neg': lambda: -a, 'square': lambda: a**2,
            'abs': lambda: abs(a), 'min': lambda: a if a < b else b,
            'max': lambda: a if a > b else b}
        cache[ref] = rational(operations[op]()); return cache[ref]
    return visit(program['output'])


class ProgramContract:
    """Local frozen assessor, never supplied to proposal feature construction."""
    def __init__(self, *, goal_id, source_sha256, assessment_id, arity,
                 assumptions, polynomial_terms=None, cases=None):
        if not all(isinstance(s, str) and len(s) == 64 and all(c in '0123456789abcdef' for c in s)
                   for s in (goal_id, source_sha256)) or not assessment_id:
            raise ValueError('Goal, independent source hash and assessment identity required')
        if type(arity) is not int or not 1 <= arity <= 4:
            raise ValueError('A valid assessment arity is required')
        if (polynomial_terms is None) == (cases is None):
            raise ValueError('Choose exactly one independent proof or finite-test contract')
        if not isinstance(assumptions, list) or any(not isinstance(s, str) or not s for s in assumptions):
            raise ValueError('Declare the assumption scope explicitly')
        normalized = {'goal_id': goal_id, 'source_sha256': source_sha256, 'assessment_id': assessment_id,
                      'arity': arity, 'assumptions': sorted(set(assumptions))}
        if polynomial_terms is not None:
            target = {}
            for powers, coefficient in polynomial_terms:
                if (len(powers) != arity or any(type(n) is not int or n < 0 for n in powers)
                        or tuple(powers) in target):
                    raise ValueError('Unique valid monomials required')
                target[tuple(powers)] = rational(coefficient)
            normalized.update(kind='polynomial_identity', terms=terms(target))
        else:
            if not cases or len(cases) > 256: raise ValueError('One to 256 finite checks required')
            rows, seen = [], set()
            for row in cases:
                if set(row) != {'inputs', 'output'} or len(row['inputs']) != arity:
                    raise ValueError('Independent input/output record required')
                values = list(map(lambda x: str(rational(x)), row['inputs']))
                key = identity(values)
                if key in seen: raise ValueError('Duplicate independent test input')
                seen.add(key); rows.append({'inputs': values, 'output': str(rational(row['output']))})
            normalized.update(kind='finite_inputs', cases=rows)
        self._record = normalized
        self._identity = identity(normalized)
        self.verifier_sha256 = sha256(Path(__file__))

    @property
    def record(self): return deepcopy(self._record)

    @property
    def id(self):
        if identity(self._record) != self._identity:
            raise ValueError('Frozen assessment contract changed')
        return self._identity

    def review(self, program):
        record = self.record; contract_id = self.id
        if program.get('arity') != record['arity']: raise ValueError('Assessed arity changed')
        result = {'contract': contract_id, 'source_sha256': record['source_sha256'],
                  'verifier_sha256': self.verifier_sha256, 'kind': record['kind'],
                  'program': identity(program), 'assumptions': record['assumptions']}
        if record['kind'] == 'polynomial_identity':
            try:
                coefficients = terms(polynomial(program))
                passed = coefficients == record['terms']
                result.update(qualified=passed, quality=float(passed), coefficients=coefficients,
                    target_identity=identity(record['terms']),
                    scope='algebraic identity over rational inputs; executable arithmetic has a separate 256-bit bound',
                    failure=None if passed else 'different exact coefficients',
                    coverage=[identity(['polynomial', record['arity'], record['terms']])] if passed else [])
            except (ValueError, ZeroDivisionError, OverflowError) as error:
                result.update(qualified=False, quality=0., coverage=[], failure=str(error),
                              scope='polynomial obligation not established')
        else:
            tests = []
            for row in record['cases']:
                try:
                    prediction = independently_execute(program, row['inputs'])
                    passed = prediction == Fraction(row['output']); error = None
                except (ValueError, ZeroDivisionError, OverflowError) as problem:
                    prediction, passed, error = None, False, str(problem)
                tests.append({'evidence': identity([record['arity'], row]),
                    'inputs': row['inputs'], 'expected': row['output'],
                    'actual': None if prediction is None else str(prediction), 'passed': passed, 'error': error})
            passed_count = sum(t['passed'] for t in tests)
            result.update(qualified=passed_count == len(tests), quality=passed_count/len(tests),
                tests=tests, coverage=[t['evidence'] for t in tests if t['passed']],
                failure=None if passed_count == len(tests) else 'one or more independent checks failed',
                scope='only the listed independently checked inputs; no universal identity inferred')
        result['id'] = identity(result)
        return result
