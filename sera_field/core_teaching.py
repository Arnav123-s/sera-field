"""Checked human solutions -> label-separated finite graph teaching views.

No downloaded code is executed. Numeric binding alternatives are instance-level
teacher interpretations, not independent proofs of English semantics.
"""
import ast
from fractions import Fraction
from itertools import product
import re

from .core_programs import BASE, CONSTANTS, execute, rational, validate
from .core_program_verifier import independently_execute
from .native_data import identity

NUMBER = re.compile(r'(?<![\w.])\d[\d,]*(?:\.\d+)?')
ANNOTATION = re.compile(r'<<([^<>]+)>>')
MAX_ALTERNATIVES = 16
MAX_TREE_NODES = 128
OPS = {ast.Add: 'add', ast.Sub: 'sub', ast.Mult: 'mul', ast.Div: 'div'}


class SourceRejection(ValueError):
    pass


def expression(text):
    """Parse a bounded exact arithmetic expression, never Python execution."""
    if not isinstance(text, str) or len(text) > 4096:
        raise SourceRejection('expression_size')
    try:
        text = text.strip().replace(',', '')
        tree = ast.parse(text, mode='eval').body
    except (SyntaxError, ValueError) as error:
        raise SourceRejection('expression_syntax') from error
    if sum(1 for _ in ast.walk(tree)) > MAX_TREE_NODES:
        raise SourceRejection('expression_size')
    mark_literals(tree, text)
    return tree


def mark_literals(tree, text):
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            node._sera_literal = ast.get_source_segment(text, node)


def literal(node):
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return rational(getattr(node, '_sera_literal', None) or str(node.value))
    if isinstance(node, ast.UnaryOp) and type(node.op) in (ast.USub, ast.UAdd):
        value = literal(node.operand)
        return -value if isinstance(node.op, ast.USub) else value
    raise SourceRejection('nonliteral')


def check_arithmetic(node):
    """Source-side recursive arithmetic; independent from both graph executors."""
    if isinstance(node, ast.Constant): return literal(node)
    if isinstance(node, ast.UnaryOp) and type(node.op) in (ast.USub, ast.UAdd):
        value = check_arithmetic(node.operand)
        return -value if isinstance(node.op, ast.USub) else value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        a, b = check_arithmetic(node.left), check_arithmetic(node.right)
        if isinstance(node.op, ast.Add): value = a+b
        elif isinstance(node.op, ast.Sub): value = a-b
        elif isinstance(node.op, ast.Mult): value = a*b
        else: value = a/b
        return rational(value)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
        exponent = literal(node.right)
        if exponent.denominator != 1 or not 0 <= exponent <= 4:
            raise SourceRejection('power_scope')
        return rational(check_arithmetic(node.left)**int(exponent))
    raise SourceRejection('arithmetic_syntax')


def constant_tree(value):
    """An explicit arithmetic construction; never append an answer as an input."""
    value = rational(value)
    if value in CONSTANTS: return ('constant', str(value))
    if value < 0: return ('neg', constant_tree(-value))
    if value.denominator != 1:
        return ('div', constant_tree(Fraction(value.numerator)), constant_tree(Fraction(value.denominator)))
    n = int(value)
    if n > 1000: raise SourceRejection('constant_scope')
    if n % 2 == 0: return ('mul', constant_tree(Fraction(n//2)), ('constant', '2'))
    return ('add', constant_tree(Fraction(n-1)), ('constant', '1'))


def unique(trees):
    result = sorted(set(trees), key=repr)
    if len(result) > MAX_ALTERNATIVES: raise SourceRejection('binding_alternatives_overflow')
    return result


def compile_expression(node, lookup, *, names=None):
    if isinstance(node, ast.Name) and names is not None:
        if node.id not in names: raise SourceRejection('unbound_code_name')
        return names[node.id]
    if isinstance(node, ast.Constant): return lookup(literal(node))
    if isinstance(node, ast.UnaryOp) and type(node.op) in (ast.USub, ast.UAdd):
        items = compile_expression(node.operand, lookup, names=names)
        return items if isinstance(node.op, ast.UAdd) else unique([('neg', x) for x in items])
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        left = compile_expression(node.left, lookup, names=names)
        right = compile_expression(node.right, lookup, names=names)
        return unique([(OPS[type(node.op)], a, b) for a, b in product(left, right)])
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
        exponent = literal(node.right)
        if exponent.denominator != 1 or not 0 <= exponent <= 4:
            raise SourceRejection('power_scope')
        items = compile_expression(node.left, lookup, names=names)
        if exponent == 0:
            # The base is evaluated even at exponent zero. Preserve partial
            # domains such as (1/x)**0 instead of silently returning a total 1.
            return unique([('add', ('mul', x, ('constant', '0')), ('constant', '1')) for x in items])
        if exponent == 1: return items
        if exponent == 2: return unique([('square', x) for x in items])
        if exponent == 3: return unique([('mul', ('square', x), x) for x in items])
        return unique([('square', ('square', x)) for x in items])
    if names is not None and isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        name = node.func.id
        if node.keywords or name not in ('abs', 'min', 'max') or len(node.args) != (1 if name == 'abs' else 2):
            raise SourceRejection('code_call_scope')
        # Built-ins may not be shadowed by a source argument or assignment.
        if name in names: raise SourceRejection('shadowed_code_builtin')
        args = [compile_expression(a, lookup, names=names) for a in node.args]
        return unique([(name, *parts) for parts in product(*args)])
    raise SourceRejection('code_expression_scope' if names is not None else 'arithmetic_syntax')


def graph_from_tree(tree, arity, slots=8):
    nodes, memo = [], {}
    def visit(part):
        if part[0] == 'input': return part[1]
        if part[0] == 'constant': return 4+CONSTANTS.index(Fraction(part[1]))
        if part in memo: return memo[part]
        a = visit(part[1]); b = visit(part[2]) if len(part) == 3 else a
        if len(nodes) >= slots: raise SourceRejection('instruction_capacity')
        ref = BASE+len(nodes); nodes.append([part[0], a, b]); memo[part] = ref
        return ref
    output = visit(tree)
    while len(nodes) < slots: nodes.append(['neg', 6, 6])
    return validate({'arity': arity, 'nodes': nodes, 'output': output})


def source_identity(row):
    return {'id': row['identity'], 'group': row['group'], 'source_sha256': row['source_sha256'],
            'source_record': row['source_record'], 'origin': row['origin'],
            'source_record_sha256': identity(row), 'split': row['split']}


def question_inventory(text):
    values, spans = [], []
    for match in NUMBER.finditer(text):
        value = str(rational(match.group().replace(',', '')))
        if value not in values: values.append(value)
        spans.append({'start': match.start(), 'end': match.end(), 'input': values.index(value)})
    return values, spans


def mathematics_view(row):
    question, solution = row['prompt'], row['teacher']['worked_solution']
    annotations = list(ANNOTATION.finditer(solution))
    if not 1 <= len(annotations) <= 64: raise SourceRejection('marked_calculation_count')
    if solution.count('####') != 1: raise SourceRejection('final_answer_marker')
    try: answer = rational(solution.rsplit('####', 1)[1].strip().replace(',', ''))
    except (ValueError, ZeroDivisionError) as error: raise SourceRejection('final_answer_literal') from error
    checks = []
    for match in annotations:
        left, equal, right = match.group(1).rpartition('=')
        if not equal: raise SourceRejection('annotation_equality')
        try:
            result = check_arithmetic(expression(left))
            if result != rational(right.strip().replace(',', '')):
                raise SourceRejection('annotation_arithmetic_mismatch')
        except ZeroDivisionError as error: raise SourceRejection('annotation_zero_division') from error
        checks.append({'expression': left, 'value': str(result), 'span': [match.start(), match.end()]})
    if Fraction(checks[-1]['value']) != answer: raise SourceRejection('last_calculation_not_final_answer')
    values, spans = question_inventory(question)
    result = {**source_identity(row), 'track': 'whole_human_mathematics', 'question': question,
        'inputs': values, 'numeric_spans': spans, 'answer': str(answer), 'checked_calculations': checks,
        'programs': [], 'binding_ambiguities': [], 'graph_status': 'pending',
        'qualification': 'exact annotated calculations and original numeric instance; human semantic target supplied'}
    if not 1 <= len(values) <= 4:
        result['graph_status'] = 'input_capacity'; return result
    choices = {Fraction(v): [('input', i)] for i, v in enumerate(values)}
    def lookup(value):
        candidates = list(choices.get(value, []))
        if value in CONSTANTS: candidates.append(('constant', str(value)))
        if not candidates: candidates = [constant_tree(value)]
        candidates = unique(candidates)
        if len(candidates) > 1:
            record = {'value': str(value), 'alternatives': len(candidates),
                      'candidate_identity': identity(candidates)}
            if record not in result['binding_ambiguities']: result['binding_ambiguities'].append(record)
        return candidates
    try:
        trees = []
        for step in checks:
            trees = compile_expression(expression(step['expression']), lookup)
            value = Fraction(step['value'])
            choices[value] = unique(choices.get(value, [])+trees)
        programs = []; excluded = 0
        for tree in unique(trees):
            try: program = graph_from_tree(tree, len(values))
            except SourceRejection as error:
                if str(error) != 'instruction_capacity': raise
                excluded += 1; continue
            if (Fraction(execute(program, values)['value']) != answer or
                    independently_execute(program, values) != answer):
                raise SourceRejection('independent_graph_mismatch')
            if program not in programs: programs.append(program)
        result['programs'] = programs; result['over_capacity_alternatives'] = excluded
        result['graph_status'] = 'qualified_numeric_instance' if programs else 'instruction_capacity'
    except SourceRejection as error:
        result['graph_status'] = str(error)
    return result


def programming_view(row):
    source = row['teacher']['reference_program']
    if row['teacher']['setup'].strip(): raise SourceRejection('code_setup_scope')
    try: module = ast.parse(source)
    except SyntaxError as error: raise SourceRejection('code_syntax') from error
    if sum(1 for _ in ast.walk(module)) > 1024: raise SourceRejection('code_size')
    mark_literals(module, source)
    if len(module.body) != 1 or not isinstance(module.body[0], ast.FunctionDef):
        raise SourceRejection('code_module_scope')
    fn = module.body[0]; args = fn.args
    if (fn.decorator_list or args.vararg or args.kwarg or args.kwonlyargs or args.defaults or args.posonlyargs
            or not 1 <= len(args.args) <= 4): raise SourceRejection('code_signature_scope')
    names = {arg.arg: [('input', i)] for i, arg in enumerate(args.args)}
    body = list(fn.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        body = body[1:]
    if not body or not isinstance(body[-1], ast.Return): raise SourceRejection('code_statement_scope')
    constants = lambda value: [constant_tree(value)]
    evaluated = []
    for statement in body[:-1]:
        if not isinstance(statement, ast.Assign) or len(statement.targets) != 1 or not isinstance(statement.targets[0], ast.Name):
            raise SourceRejection('code_statement_scope')
        names[statement.targets[0].id] = compile_expression(statement.value, constants, names=names)
        evaluated.extend(names[statement.targets[0].id])
    trees = compile_expression(body[-1].value, constants, names=names)
    def contains(tree, part):
        return tree == part or any(contains(child, part) for child in tree[1:] if isinstance(child, tuple))
    for part in evaluated:
        # A discarded source assignment can still raise division by zero. Keep
        # its evaluation in the output graph without changing a finite result.
        trees = [tree if contains(tree, part) else ('add', tree, ('mul', part, ('constant', '0'))) for tree in trees]
    programs = [graph_from_tree(tree, len(args.args)) for tree in trees]
    cases = []
    for test in row['teacher']['tests']:
        try: test_tree = ast.parse(test)
        except SyntaxError as error: raise SourceRejection('code_test_syntax') from error
        mark_literals(test_tree, test)
        if len(test_tree.body) != 1 or not isinstance(test_tree.body[0], ast.Assert): raise SourceRejection('code_test_scope')
        comparison = test_tree.body[0].test
        if (not isinstance(comparison, ast.Compare) or len(comparison.ops) != 1
                or not isinstance(comparison.ops[0], ast.Eq) or not isinstance(comparison.left, ast.Call)):
            raise SourceRejection('code_test_scope')
        call = comparison.left
        if not isinstance(call.func, ast.Name) or call.func.id != fn.name or call.keywords or len(call.args) != len(args.args):
            raise SourceRejection('code_test_scope')
        inputs = [str(check_arithmetic(arg)) for arg in call.args]
        target = check_arithmetic(comparison.comparators[0])
        for program in programs:
            if Fraction(execute(program, inputs)['value']) != target or independently_execute(program, inputs) != target:
                raise SourceRejection('code_assertion_mismatch')
        cases.append({'inputs': inputs, 'output': str(target)})
    if not cases: raise SourceRejection('no_code_assertions')
    return {**source_identity(row), 'track': 'human_scalar_programming', 'question': row['prompt'],
        'arguments': [a.arg for a in args.args], 'function': fn.name, 'programs': programs, 'cases': cases,
        'graph_status': 'qualified_human_assertions', 'qualification': 'supplied scalar signature and human assertions; no universal semantic claim'}


def public_input(row):
    """The sole learner view excludes solutions, checked traces and target graphs."""
    if row['track'] == 'whole_human_mathematics':
        inventory = ', '.join(f'x{i}={value}' for i, value in enumerate(row['inputs']))
        return {'context': row['question']+'\nQuestion-number inventory: '+inventory,
                'question': 'Return a scalar program answering the original question.', 'arity': len(row['inputs'])}
    return {'context': row['question']+'\nSupplied function arguments: '+', '.join(row['arguments']),
            'question': 'Return a scalar program implementing the requested function.', 'arity': len(row['arguments'])}
