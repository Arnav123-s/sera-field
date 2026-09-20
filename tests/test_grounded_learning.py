"""Regression checks for the real training path, not claims of learned capability."""
import copy
from dataclasses import asdict
from fractions import Fraction
import json
from pathlib import Path
import random
import subprocess
import sys

import numpy as np
import pytest
import torch

from sera_field.grounded_owner import GroundedOwner
from sera_field.model import weight_hash
from sera_field.study_data import (tokens, sentences, number_pool, math_views,
                                   expression_value, canonical_expression, reading_view)
from sera_field.study_training import Engine, reading_batch, pair_inputs, math_batch, physical_batch
from sera_field.study_world import Environment, draw, probes, analytic_probe

torch.set_num_threads(1)


def model():
    torch.manual_seed(1931)
    return GroundedOwner(width=12)


def test_hidden_label_changes_never_reach_reading_inputs():
    owner = model()
    row = {'identity': 'q', 'source_sha256': 'a'*64, 'group': 'article',
           'prompt': 'Alice saw a flower. Bob saw the bridge.\n\nWhat did Alice see?',
           'teacher': {'context_length': len('Alice saw a flower. Bob saw the bridge.'),
                       'question': 'What did Alice see?', 'answers': [{'answer_start': 12, 'text': 'flower'}]}}
    other = copy.deepcopy(row)
    other['teacher']['answers'] = [{'answer_start': 31, 'text': 'bridge'}]
    a, b = reading_view(row), reading_view(other)
    assert a['targets'] != b['targets']
    assert a['options'] == b['options'] and a['question'] == b['question']
    torch.testing.assert_close(owner.rank([a['question']], [a['options']]),
                               owner.rank([b['question']], [b['options']]), rtol=0, atol=0)


def test_all_tokens_contribute_past_the_old_prefix_limit():
    owner = model()
    common = 'unrelated prose ' * 400
    a = owner.encode_texts([common + ' red flower'])
    b = owner.encode_texts([common + ' blue bridge'])
    assert not torch.equal(a, b)
    a.sum().backward()
    assert owner.words.weight.grad[tokens('flower')[0]].abs().sum() > 0


def test_padding_and_other_batch_members_do_not_change_encoding():
    owner = model()
    single = owner.encode_texts(['A small flower.'])
    batch = owner.encode_texts(['A small flower.', 'much longer ' * 70])
    torch.testing.assert_close(single[0], batch[0], rtol=1e-5, atol=1e-6)


def test_question_field_and_links_receive_real_gradients():
    owner = model()
    scores = owner.rank(['Where is the flower?'], [['A flower grows near the wall.', 'The lake is deep.']])
    torch.nn.functional.cross_entropy(scores, torch.tensor([0])).backward()
    assert owner.words.weight.grad.abs().sum() > 0
    assert owner.field.links.grad.abs().sum() > 0
    assert owner.text_boundary.weight.grad.abs().sum() > 0


def test_math_targets_not_available_to_proposal_inputs():
    row = {'identity': 'human-1', 'group': 'g', 'source_sha256': 'a'*64,
           'prompt': 'I have 5 apples and buy 3 more. How many apples?',
           'teacher': {'worked_solution': 'There are <<5+3=8>> apples. #### 8'}}
    item = list(math_views(row))[0]
    assert '8' not in item['question'] and item['answer'] == '8'
    owner = model()
    before = owner.math_logits([item['question']], [item['values']])
    item['target'] = [1, 0, 1]
    after = owner.math_logits([item['question']], [item['values']])
    torch.testing.assert_close(before, after, rtol=0, atol=0)
    assert canonical_expression(0, '3', '5') == canonical_expression(0, '5', '3')
    assert canonical_expression(1, '3', '5') != canonical_expression(1, '5', '3')
    assert expression_value(3, '1', '3') == Fraction(1, 3)


def test_hidden_physics_values_masked_and_interventions_checked():
    owner = model()
    observed = torch.tensor([[[1., 2., .3], [1., 4., 10.]]])
    mask = torch.tensor([[1., 0.]])
    a = owner.world(observed, mask)['coefficients']
    observed[0, 1] = torch.tensor([-100., 500., 9999.])
    b = owner.world(observed, mask)['coefficients']
    torch.testing.assert_close(a, b, rtol=0, atol=0)
    world = Environment(1., .3, 0., .1)
    receipt = world.intervene([2., 2.], actuator_scale=.5)
    assert not receipt['actuation_matched'] and receipt['performed'] == [2., 1.]
    assert receipt['observation'][2] == pytest.approx(.5)


def test_independent_worlds_are_reproducible_and_split_disjoint():
    a, *data = draw(1103, 42, 'teaching')
    b, *same = draw(1103, 42, 'teaching')
    c, *_ = draw(1103, 42, 'final')
    assert asdict(a) == asdict(b) != asdict(c)
    for x, y in zip(data, same):
        np.testing.assert_array_equal(x, y)
    assert 0 <= analytic_probe(data[0], probes(), data[1]) < len(probes())


class TinyCurriculum:
    """Clearly synthetic engineering fixtures, never production teaching data."""
    manifest_sha = 'b' * 64
    def __init__(self):
        reading = [{'id': str(i), 'track': 'fixture', 'question': 'Where does a flower grow?',
                    'options': ['By a wall.', 'In the garden.'], 'targets': [i % 2]} for i in range(7)]
        math = [{'id': 'm'+str(i), 'track': 'fixture_math', 'question': 'I have 5 and add 3.',
                 'values': ['5', '3', '1'], 'target': [0, 0, 1]} for i in range(5)]
        pairs = [{'id': 'p'+str(i), 'track': 'fixture_pair', 'question': 'question '+str(i),
                  'answer': 'answer '+str(i)} for i in range(9)]
        self.train = {'reading': reading, 'math': math, 'pairs': pairs}
        self.pairs = {'fixture_pair': pairs}
        self.tracks = ['fixture_pair']


def test_exact_next_update_after_resume_in_new_process(tmp_path):
    engine = Engine(TinyCurriculum(), width=12)
    for _ in range(4):
        engine.update(batch=3)
    engine.save(tmp_path / 'revisions')
    # This is a new interpreter, not only save/load in the same process.
    script = tmp_path / 'resume_check.py'
    tests_path = str(Path(__file__).resolve().parent)
    script.write_text('import sys, json\nsys.path.insert(0, '+repr(tests_path)+')\n'
                      'from test_grounded_learning import TinyCurriculum\n'
                      'from sera_field.study_training import Engine\n'
                      'from sera_field.model import weight_hash\n'
                      'e=Engine(TinyCurriculum(), width=12)\n'
                      'e.resume('+repr(str(tmp_path / 'revisions'))+')\n'
                      'result=e.update(batch=3)\n'
                      'print(json.dumps({"result":result,"weights":weight_hash(e.owner),"cursor":e.physics_cursor}))\n')
    child = json.loads(subprocess.check_output([sys.executable, str(script)], text=True))
    expected = engine.update(batch=3)
    assert child['result'] == expected
    assert child['weights'] == weight_hash(engine.owner)
    assert child['cursor'] == engine.physics_cursor


def test_resume_preserves_human_sampler_and_rng(tmp_path):
    a = Engine(TinyCurriculum(), width=12)
    for _ in range(3):
        a.update(batch=3)
    a.save(tmp_path)
    b = Engine(TinyCurriculum(), width=12)
    b.resume(tmp_path)
    expected = a.update(batch=3)
    actual = b.update(batch=3)
    assert actual == expected and weight_hash(a.owner) == weight_hash(b.owner)
    assert a.seen == b.seen and a.samplers == b.samplers and a.exposures == b.exposures


def test_attempts_advance_on_wrong_predictions_as_well_as_correct():
    engine = Engine(TinyCurriculum(), width=12)
    for _ in range(12):
        engine.update(batch=2)
    assert engine.step == 12 and sum(engine.exposures.values()) == 24
    assert engine.physics_cursor == 6


def test_real_inquiry_credits_actual_assessment_and_retains_goal(tmp_path):
    from sera_field.study_inquiry import Investigator
    agent = Investigator(model())
    before = weight_hash(agent.owner)
    episode = agent.attempt(0)
    assert episode['decision_commit']['goal'] == episode['event']['outcome']['goal']
    assert episode['original_goal_returned'] and len(episode['returned_answer']) == 12
    assert episode['event']['accepted'] and episode['event']['weights_changed']
    assert weight_hash(agent.owner) != before
    assert episode['event']['outcome']['source_sha256'] == agent.source_sha
    assert len(episode['decision_commit']['imagined_goal_alternatives']) == 3
    assert episode['before_loss'] >= 0 and episode['after_loss'] >= 0
    agent.save(tmp_path)
    replay = Investigator(model())
    replay.resume(tmp_path)
    a, b = agent.attempt(1), replay.attempt(1)
    assert a == b and weight_hash(agent.owner) == weight_hash(replay.owner)


def test_reward_control_equal_attempt_and_failed_actuation_not_credited():
    from sera_field.study_inquiry import Investigator
    rewarded, control = Investigator(model()), Investigator(model(), reward=False)
    original = weight_hash(control.owner)
    a, b = rewarded.attempt(0), control.attempt(0)
    assert a['decision_commit'] == b['decision_commit']
    assert a['cost'] == b['cost'] and not b['event']['weights_changed']
    assert weight_hash(control.owner) == original
    failed = rewarded.attempt(40)
    assert not failed['intervention_receipt']['actuation_matched']
    assert not failed['event']['accepted'] and not rewarded.book.pending
