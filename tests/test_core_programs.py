import copy
from fractions import Fraction
import random

import pytest

from sera_field.core_programs import BASE, OPERATIONS, UNARY, execute, method, render, validate
from sera_field.core_program_verifier import ProgramContract, independently_execute, polynomial, terms


def graph(nodes, output, arity=2):
    return {'arity': arity, 'nodes': nodes, 'output': output}


FACTORED = graph([['add', 0, 1], ['square', 9, 9]], 10)
EXPANDED = graph([['square', 0, 0], ['square', 1, 1], ['mul', 0, 1], ['mul', 11, 8],
                  ['add', 9, 10], ['add', 12, 13]], 14)
SQUARE_TERMS = [[[0, 2], '1'], [[1, 1], '2'], [[2, 0], '1']]


def contract(**kwargs):
    return ProgramContract(goal_id='a'*64, source_sha256='b'*64, assessment_id='fixture',
                           arity=2, assumptions=['rational inputs'], **kwargs)


def test_exact_polynomial_proof_and_independent_execution_agree():
    assessor = contract(polynomial_terms=SQUARE_TERMS)
    for program in (FACTORED, EXPANDED):
        assert terms(polynomial(program)) == SQUARE_TERMS
        assert assessor.review(program)['qualified']
        for x in range(-4, 5):
            for y in range(-3, 4):
                inputs = [str(Fraction(x, 3)), str(Fraction(y, 5))]
                actual = Fraction(execute(program, inputs)['value'])
                assert actual == independently_execute(program, inputs) == (Fraction(x, 3)+Fraction(y, 5))**2
    assert method(FACTORED)['id'] != method(EXPANDED)['id']


def test_aliases_and_dead_code_do_not_create_new_methods():
    commuted = graph([['add', 1, 0], ['mul', 9, 9], ['div', 0, 6]], 10)
    assert method(FACTORED)['id'] == method(commuted)['id']
    assert execute(commuted, [2, 3])['value'] == '25'  # unreachable division by zero
    first = graph([['add', 0, 1], ['add', 9, 7]], 10)
    second = graph([['add', 1, 7], ['add', 9, 0], ['mul', 10, 7]], 11)
    assert method(first)['id'] == method(second)['id']
    assert 'x0' in render(FACTORED)


def test_finite_success_does_not_become_an_algebraic_identity():
    absolute = graph([['abs', 0, 0]], 9)
    finite = contract(cases=[{'inputs': [1, 2], 'output': 1}, {'inputs': [2, 3], 'output': 2}])
    report = finite.review(absolute)
    assert report['qualified'] and report['kind'] == 'finite_inputs'
    assert 'no universal' in report['scope']
    proof = contract(polynomial_terms=[[[1, 0], '1']]).review(absolute)
    assert not proof['qualified'] and 'Piecewise' in proof['failure']
    assert execute(absolute, [-1, 2])['value'] == '1'


def test_partial_functions_cannot_purchase_a_total_polynomial_proof():
    division = graph([['div', 0, 0]], 9)
    report = contract(polynomial_terms=[[[0, 0], '1']]).review(division)
    assert not report['qualified'] and 'denominator' in report['failure']
    checked = contract(cases=[{'inputs': [0, 1], 'output': 1}, {'inputs': [2, 0], 'output': 1}]).review(division)
    assert not checked['qualified'] and checked['quality'] == .5
    assert checked['tests'][0]['error']
    assert method(division)['id'] != method(graph([['add', 7, 6]], 9))['id']


def test_forward_references_missing_inputs_and_numeric_blowup_reject():
    for bad in (graph([['add', 10, 0]], 9), graph([['add', 2, 0]], 9),
                graph([['eval', 0, 1]], 9), graph([['neg', 0, 1]], 9)):
        with pytest.raises(ValueError): validate(bad)
    oversized = graph([['square', 0, 0]]+[['square', 8+i, 8+i] for i in range(1, 8)], 16)
    with pytest.raises(ValueError, match='degree'): polynomial(oversized)
    with pytest.raises(ValueError, match='arithmetic bound'): execute(oversized, [2**200, 1])
    with pytest.raises(ValueError, match='Duplicate'):
        contract(cases=[{'inputs': [1, 2], 'output': 3}]*2)


def test_frozen_assessor_detects_mutation_and_bad_source():
    original = copy.deepcopy(SQUARE_TERMS); assessor = contract(polynomial_terms=original)
    original[0][1] = '999'
    assert assessor.review(FACTORED)['qualified']
    assessor._record['terms'][0][1] = '999'
    with pytest.raises(ValueError, match='changed'): assessor.review(FACTORED)
    with pytest.raises(ValueError, match='source hash'):
        ProgramContract(goal_id='a'*64, source_sha256='source', assessment_id='bad', arity=2,
                        assumptions=[], polynomial_terms=[])


def test_independent_executors_agree_across_all_primitives_and_random_graphs():
    rng = random.Random(22024); used = set()
    for _ in range(240):
        nodes = []
        for i in range(4):
            allowed = [0, 1, *range(4, BASE+i)]
            op = rng.choice(OPERATIONS); used.add(op)
            a = rng.choice(allowed); b = a if op in UNARY else rng.choice(allowed)
            nodes.append([op, a, b])
        program = graph(nodes, BASE+3)
        for inputs in ([0, 0], [-2, 3], ['2/3', '-7/5'], [4, -1]):
            results = []
            for evaluator in (lambda: Fraction(execute(program, inputs)['value']),
                              lambda: independently_execute(program, inputs)):
                try: results.append(('value', evaluator()))
                except (ValueError, ZeroDivisionError, OverflowError): results.append(('failed', None))
            assert results[0] == results[1]
    assert used == set(OPERATIONS)
