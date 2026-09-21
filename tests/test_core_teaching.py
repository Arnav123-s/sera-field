import copy
from fractions import Fraction

import pytest
import torch

from sera_field.core_owner import CoreOwner
from sera_field.core_programs import execute
from sera_field.core_teaching import (SourceRejection, check_arithmetic, expression,
    mathematics_view, programming_view, public_input)
from sera_field.core_teaching_loss import teaching_loss, assess_program_rows


def math_row(question='There were 48 clips; half as many were sold later. What was the total?',
             solution='Half <<48/2=24>>24. Total <<48+24=72>>72.\n#### 72'):
    return {'identity': 'fixture-math', 'source_record': 'fixture', 'source_sha256': 'a'*64,
        'group': 'fixture-group', 'origin': 'engineering', 'split': 'train', 'prompt': question,
        'teacher': {'worked_solution': solution}}


def code_row(code='def combine(a, b):\n    c = a + b\n    return c*c', tests=None):
    result = math_row(); result['prompt'] = 'Return the squared sum of two arguments.'
    result['teacher'] = {'reference_program': code, 'setup': '',
        'tests': tests or ['assert combine(2,3) == 25', 'assert combine(-2,3) == 1']}
    return result


def test_original_question_retains_full_dependency_without_answer_input():
    row = mathematics_view(math_row())
    assert row['answer'] == '72' and row['inputs'] == ['48'] and len(row['checked_calculations']) == 2
    assert row['programs'] and all(execute(p, ['48'])['value'] == '72' for p in row['programs'])
    view = public_input(row)
    assert '24' not in view['context'] and '72' not in view['context']
    altered = copy.deepcopy(row); altered['answer'] = '999'; altered['programs'] = []; altered['checked_calculations'] = []
    assert public_input(altered) == view


def test_source_calculations_and_final_checked_even_when_unreachable():
    with pytest.raises(SourceRejection, match='annotation_arithmetic_mismatch'):
        mathematics_view(math_row(solution='<<7+2=10>> <<48/2=24>> <<48+24=72>> #### 72'))
    with pytest.raises(SourceRejection, match='last_calculation_not_final_answer'):
        mathematics_view(math_row(solution='<<48/2=24>> #### 72'))
    assert check_arithmetic(expression('0.123456789012345678901 + 0.1')) == Fraction('0.223456789012345678901')


def test_numeric_binding_ambiguities_preserved_and_capacity_not_silently_truncated():
    row = mathematics_view(math_row('A 3 by 2 quantity is added to 6. Total?', '<<3*2=6>> <<6+6=12>> #### 12'))
    assert len(row['programs']) > 1 and row['binding_ambiguities']
    assert all(execute(p, row['inputs'])['value'] == '12' for p in row['programs'])
    limited = mathematics_view(math_row('The values are 3, 4, 5, 6, 7.', '<<3+4=7>> #### 7'))
    assert limited['graph_status'] == 'input_capacity' and len(limited['inputs']) == 5 and not limited['programs']


def test_human_code_compiles_assignments_and_checks_each_assertion():
    row = programming_view(code_row())
    assert row['cases'] == [{'inputs': ['2', '3'], 'output': '25'}, {'inputs': ['-2', '3'], 'output': '1'}]
    assert row['programs'] and row['arguments'] == ['a', 'b']
    with pytest.raises(SourceRejection, match='code_assertion_mismatch'):
        programming_view(code_row(tests=['assert combine(2,3) == 24']))
    with pytest.raises(SourceRejection):
        programming_view(code_row("def combine(a, b):\n    return __import__('os').system('echo must-never-run')"))
    with pytest.raises(SourceRejection): programming_view(code_row('def combine(a, b):\n    while a: a-=1\n    return b'))
    with pytest.raises(SourceRejection, match='shadowed_code_builtin'):
        programming_view(code_row('def combine(abs, b):\n    return abs(b)'))
    with pytest.raises(ZeroDivisionError):
        programming_view(code_row('def combine(a, b):\n    unused = 1/(a-2)\n    return (a+b)**2'))
    with pytest.raises(ZeroDivisionError):
        programming_view(code_row('def combine(a, b):\n    return (1/(a-2))**0', tests=['assert combine(2,3) == 1']))


def test_program_teaching_reaches_shared_core_and_preserves_distinct_assessment():
    torch.manual_seed(22241)
    owner = CoreOwner(program_slots=8)
    rows = [mathematics_view(math_row()), programming_view(code_row())]
    loss, _ = teaching_loss(owner, rows)
    assert torch.isfinite(loss) and loss > 0
    loss.backward()
    norms = {name: float(p.grad.norm()) for name,p in owner.named_parameters() if p.grad is not None}
    for prefix in ('core.', 'flow.', 'fusion.', 'program_map.'):
        assert any(k.startswith(prefix) and v > 0 for k,v in norms.items()), prefix
    cases = assess_program_rows(owner, rows)
    assert len(cases) == 2 and len(cases[1]['checks']) == 2
    assert all('proposal' in c and 'correct' in c for c in cases)
