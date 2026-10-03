"""Finite scalar graphs: explicit execution, no Python evaluation or effects."""
from fractions import Fraction
import json

from .native_data import identity

OPERATIONS = ('add', 'sub', 'mul', 'div', 'neg', 'square', 'abs', 'min', 'max')
UNARY = frozenset(('neg', 'square', 'abs'))
CONSTANTS = (-2, -1, 0, 1, 2)
BASE = 4 + len(CONSTANTS)


def rational(value):
    if type(value) not in (int, str, Fraction):
        raise ValueError('Exact rational input requires an integer or fraction string')
    result = Fraction(value)
    if max(result.numerator.bit_length(), result.denominator.bit_length()) > 256:
        raise ValueError('Declared exact arithmetic bound exceeded')
    return result


def validate(program):
    if set(program) != {'arity', 'nodes', 'output'}:
        raise ValueError('An explicit graph, arity and output are required')
    arity, nodes, output = program['arity'], program['nodes'], program['output']
    if type(arity) is not int or not 1 <= arity <= 4 or not isinstance(nodes, list) or not 1 <= len(nodes) <= 8:
        raise ValueError('The finite graph supports one to four inputs and one to eight slots')
    for i, node in enumerate(nodes):
        if not isinstance(node, (tuple, list)) or len(node) != 3 or node[0] not in OPERATIONS:
            raise ValueError('Unknown scalar instruction')
        for ref in node[1:]:
            if type(ref) is not int or not 0 <= ref < BASE+i or arity <= ref < 4:
                raise ValueError('Operands must refer to available inputs, constants or earlier instructions')
        if node[0] in UNARY and node[2] != node[1]:
            raise ValueError('Unary operands have one canonical stored reference')
    if type(output) is not int or not 0 <= output < BASE+len(nodes) or arity <= output < 4:
        raise ValueError('Invalid graph output')
    return program


def reachable(program):
    validate(program)
    active = set()
    def visit(ref):
        if ref < BASE or ref-BASE in active: return
        index = ref-BASE; active.add(index)
        op, a, b = program['nodes'][index]
        visit(a)
        if op not in UNARY: visit(b)
    visit(program['output'])
    return sorted(active)


def execute(program, inputs):
    """Iterative exact execution of reachable instructions only."""
    active = reachable(program)
    if len(inputs) != program['arity']:
        raise ValueError('Input arity differs from the proposed program')
    values = [rational(x) for x in inputs] + [None]*(4-len(inputs)) + list(map(Fraction, CONSTANTS))
    values += [None]*len(program['nodes'])
    trace = []
    for i in active:
        op, a, b = program['nodes'][i]; x, y = values[a], values[b]
        if op == 'add': result = x+y
        elif op == 'sub': result = x-y
        elif op == 'mul': result = x*y
        elif op == 'div': result = x/y
        elif op == 'neg': result = -x
        elif op == 'square': result = x*x
        elif op == 'abs': result = abs(x)
        elif op == 'min': result = min(x, y)
        else: result = max(x, y)
        values[BASE+i] = rational(result)
        trace.append({'slot': i, 'operation': op, 'value': str(result)})
    return {'value': str(values[program['output']]), 'trace': trace, 'cost': len(active)}


def method(program):
    """Normalize declared aliases, without expanding distributive methods.

    Partial divisions retain their domain: x/x is not silently replaced by one.
    Algebraic normalization is an identity for methods, never a correctness test.
    """
    validate(program)
    const = lambda x: ('constant', str(x))
    zero, one = const(Fraction(0)), const(Fraction(1))
    def isconst(x): return x[0] == 'constant'
    def constant_value(x): return Fraction(x[1])
    def negate(x):
        if isconst(x): return const(-constant_value(x))
        if x[0] == 'neg': return x[1]
        return ('neg', x)
    def combine(op, args):
        flattened = []
        for arg in args:
            flattened.extend(arg[1:] if arg[0] == op else [arg])
        constants = [constant_value(x) for x in flattened if isconst(x)]
        other = [x for x in flattened if not isconst(x)]
        c = Fraction(0 if op == 'add' else 1)
        for x in constants: c = c+x if op == 'add' else c*x
        # Do not discard a partial subexpression when multiplication by zero
        # would still evaluate it in the actual graph.
        if c != (0 if op == 'add' else 1) or not other: other.append(const(c))
        other.sort(key=lambda x: json.dumps(x, separators=(',', ':')))
        return other[0] if len(other) == 1 else (op, *other)
    cache = {}
    def tree(ref):
        if ref < 4: return ('input', ref)
        if ref < BASE: return const(Fraction(CONSTANTS[ref-4]))
        if ref in cache: return cache[ref]
        op, a, b = program['nodes'][ref-BASE]; x = tree(a)
        y = tree(b) if op not in UNARY else x
        if op == 'sub': result = combine('add', [x, negate(y)])
        elif op in ('add', 'mul'): result = combine(op, [x, y])
        elif op == 'square': result = combine('mul', [x, x])
        elif op == 'neg': result = negate(x)
        elif op == 'abs':
            result = const(abs(constant_value(x))) if isconst(x) else (x if x[0] == 'abs' else ('abs', x))
        elif op == 'div' and y == one: result = x
        elif op in ('min', 'max'):
            result = x if x == y else (op, *sorted((x, y), key=lambda v: json.dumps(v)))
        else: result = (op, x, y)
        cache[ref] = result; return result
    normalized = tree(program['output'])
    return {'id': identity([program['arity'], normalized]), 'tree': json.loads(json.dumps(normalized)),
            'cost': len(reachable(program))}


def render(program):
    """Engineering rendering of a proposed computation; not generated prose."""
    validate(program)
    values = [f'x{i}' for i in range(4)]+list(map(str, CONSTANTS))
    for op, a, b in program['nodes']:
        x, y = values[a], values[b]
        if op in ('add', 'sub', 'mul', 'div'):
            symbol = {'add': '+', 'sub': '-', 'mul': '*', 'div': '/'}[op]
            values.append(f'({x} {symbol} {y})')
        elif op == 'neg': values.append(f'(-{x})')
        elif op == 'square': values.append(f'({x} * {x})')
        elif op == 'abs': values.append(f'abs({x})')
        else: values.append(f'{op}({x}, {y})')
    return values[program['output']]
