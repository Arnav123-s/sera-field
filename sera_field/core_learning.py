"""Practice, independent progress assessment and delayed shared-owner credit."""
import copy
from pathlib import Path
import random
import time

import torch

from .core_programs import OPERATIONS, UNARY, validate
from .core_program_verifier import ProgramContract
from .core_proposals import log_probability
from .model import weight_hash
from .native_data import identity
from .native_owner import detached_state, select_state


def greedy_graph(distribution, row=0):
    branch = int(distribution['branch_probabilities'][row].argmax())
    nodes = []
    for i in range(distribution['operations'].shape[-2]):
        op = OPERATIONS[int(distribution['operations'][row, branch, i].argmax())]
        a = int(distribution['left'][row, branch, i].argmax())
        b = a if op in UNARY else int(distribution['right'][row, branch, i].argmax())
        nodes.append([op, a, b])
    return {'arity': distribution['arities'][row], 'nodes': nodes,
            'output': int(distribution['output'][row, branch].argmax())}


class LearningContract:
    """Finite local practice and independent review; no external execution."""
    def __init__(self, lessons, plans, reviews):
        self.lessons = copy.deepcopy(lessons); self.plans = copy.deepcopy(plans)
        self.reviews = list(reviews)
        if not 2 <= len(plans) <= 4 or not 1 <= len(lessons) <= 256 or not 2 <= len(reviews) <= 256:
            raise ValueError('Two to four finite plans, practice and independent reviews required')
        groups = set(); views = set()
        for key, lesson in self.lessons.items():
            if not key or set(lesson) != {'context', 'question', 'program', 'source_sha256', 'group'}:
                raise ValueError('An attributed practice record is required')
            validate(lesson['program']); self.check_source(lesson)
            groups.add(lesson['group']); views.add(identity([lesson['context'], lesson['question']]))
        lengths = {len(plan['lessons']) for plan in self.plans}
        if len(lengths) != 1 or not 1 <= next(iter(lengths)) <= 64:
            raise ValueError('Plans must have the same finite update allowance, at most 64')
        for plan in self.plans:
            if set(plan) != {'name', 'description', 'lessons'} or not plan['name'] or not plan['description']:
                raise ValueError('Explicit practice schedule and public description required')
            if any(key not in self.lessons for key in plan['lessons']):
                raise ValueError('Plan names an unavailable practice record')
        if len({p['name'] for p in self.plans}) != len(self.plans):
            raise ValueError('Distinct schedule names required')
        seen = set(); kinds = set()
        for entry in self.reviews:
            if set(entry) != {'context', 'question', 'source_sha256', 'group', 'role', 'contract'}:
                raise ValueError('An independent attributed review record is required')
            self.check_source(entry)
            if type(entry['contract']) is not ProgramContract or entry['role'] not in ('acquisition', 'retention'):
                raise ValueError('Independent acquisition/retention program checks required')
            if entry['contract'].record['source_sha256'] != entry['source_sha256']:
                raise ValueError('Review source differs from the independent contract')
            public_goal = {'kind': 'program', 'hypothesis': entry['question'],
                'arity': entry['contract'].record['arity'], 'assumptions': entry['contract'].record['assumptions']}
            if identity(public_goal) != entry['contract'].record['goal_id']:
                raise ValueError('Review question differs from its independent proof obligation')
            view = identity([entry['context'], entry['question']])
            if entry['group'] in groups or view in views or view in seen:
                raise ValueError('Independent review overlaps current practice or duplicates a review')
            seen.add(view); kinds.add(entry['role'])
        if kinds != {'acquisition', 'retention'}:
            raise ValueError('Both acquisition and retention need independent assessment')
        self._identity = identity(self.record())

    @staticmethod
    def check_source(row):
        digest = row['source_sha256']
        if (not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest)
                or not isinstance(row['context'], str) or not isinstance(row['question'], str)
                or not row['question'].strip() or not row['group']):
            raise ValueError('Source hash, source group and public question required')

    def record(self):
        return {'lessons': self.lessons, 'plans': self.plans,
            'reviews': [{**{k:v for k,v in e.items() if k != 'contract'}, 'contract': e['contract'].record,
                         'verifier_sha256': e['contract'].verifier_sha256} for e in self.reviews]}

    @property
    def id(self):
        if identity(self.record()) != self._identity:
            raise ValueError('Frozen learning contract changed')
        return self._identity

    @torch.no_grad()
    def assess(self, owner):
        cases = []
        for entry in self.reviews:
            state, _ = owner.remember_texts([entry['context']])
            distribution = owner.program_distribution(state, [entry['question']], [entry['contract'].record['arity']])
            graph = greedy_graph(distribution)
            review = entry['contract'].review(graph)
            cases.append({'view': identity([entry['context'], entry['question']]), 'group': entry['group'],
                'role': entry['role'], 'proposal': graph, 'review': review})
        scores = {kind: sum(c['review']['qualified'] for c in cases if c['role'] == kind)/
                       sum(c['role'] == kind for c in cases) for kind in ('acquisition', 'retention')}
        return {'cases': cases, 'scores': scores, 'weights': weight_hash(owner), 'contract': self.id}


class LearningInvestigation:
    def initialize_learning(self):
        self.learning_trial = None; self.learning_history = []

    def learning_scores(self, plans):
        state = self.rebuild()
        indices = torch.zeros(len(plans), dtype=torch.int64)
        questions = [self.goal['hypothesis']+'\nPractice procedure: '+p['description'] for p in plans]
        imagined = self.owner.imagine(select_state(state, indices), self.owner.encode_texts(questions))
        return self.owner.choice(imagined).squeeze(-1).mean(1)

    def propose_learning(self, contract, directory):
        self.checked_owner()
        if self.pending is not None or self.transition is not None or self.learning_trial is not None:
            raise ValueError('Resolve the current investigation before a learning trial')
        if type(contract) is not LearningContract: raise ValueError('A frozen local learning contract is required')
        contract_id = contract.id
        if any(r['contract'] == contract_id for r in self.learning_history):
            raise ValueError('Learning procedure assessment already consumed')
        directory = Path(directory).resolve()
        if directory.exists(): raise ValueError('Use a fresh trial directory; preserve previous work')
        with torch.no_grad(): scores = self.learning_scores(contract.plans)
        action = int(torch.multinomial(scores.softmax(-1), 1))
        content = {'kind': 'learning', 'goal': copy.deepcopy(self.goal), 'source': self.source,
            'weights': self.weights, 'state': self.state_id(), 'events': identity(self.events),
            'contract': contract_id, 'plans': copy.deepcopy(contract.plans), 'action': action,
            'probabilities': scores.softmax(-1).tolist(), 'assessment_seen': False}
        self.pending = {'id': identity(content), **content}
        try:
            parent = self.save(directory/'parent')
            baseline = contract.assess(self.owner)
        except Exception:
            self.pending = None
            raise
        self.learning_trial = {'parent_path': str(directory/'parent'), 'parent_identity': parent,
            'directory': str(directory), 'decision': self.pending['id'], 'contract': contract_id,
            'baseline': baseline, 'cursor': 0, 'updates': [], 'weights': self.weights}
        self.save(directory/'current')
        return copy.deepcopy(self.pending)

    def check_learning(self, contract):
        self.checked_owner()
        if (self.learning_trial is None or self.pending is None or self.pending.get('kind') != 'learning'
                or self.learning_trial['decision'] != self.pending['id']
                or identity({k:v for k,v in self.pending.items() if k != 'id'}) != self.pending['id']
                or self.learning_trial['contract'] != contract.id or self.pending['contract'] != contract.id
                or self.learning_trial['weights'] != self.weights or self.pending['goal'] != self.goal
                or self.pending['source'] != self.source or self.pending['events'] != identity(self.events)):
            raise ValueError('Current bound learning trial required')
        trial, plan = self.learning_trial, contract.plans[self.pending['action']]
        if trial['cursor'] != len(trial['updates']) or not 0 <= trial['cursor'] <= len(plan['lessons']):
            raise ValueError('Practice cursor differs from its completed update receipts')
        previous = self.pending['weights']
        for index, update in enumerate(trial['updates']):
            lesson_id = plan['lessons'][index]
            if (update['cursor'] != index or update['lesson'] != lesson_id or update['before_weights'] != previous
                    or update['lesson_identity'] != identity(contract.lessons[lesson_id])):
                raise ValueError('Practice receipt chain changed')
            previous = update['after_weights']
        if previous != self.weights: raise ValueError('Practice predictor chain differs from owner')
        return trial, plan

    def practice_learning(self, contract):
        """Exactly one completed update, with a durable next cursor."""
        trial, plan = self.check_learning(contract)
        if trial['cursor'] >= len(plan['lessons']): raise ValueError('All registered practice updates completed')
        key = plan['lessons'][trial['cursor']]; lesson = contract.lessons[key]
        if len(lesson['program']['nodes']) != self.owner.program_slots:
            raise ValueError('Practice graph differs from the owner instruction space')
        previous_owner = copy.deepcopy(self.owner.state_dict()); previous_optimizer = copy.deepcopy(self.optimizer.state_dict())
        started = time.perf_counter()
        try:
            self.optimizer.zero_grad(set_to_none=True)
            state, _ = self.owner.remember_texts([lesson['context']])
            distribution = self.owner.program_distribution(state, [lesson['question']], [lesson['program']['arity']])
            # Marginalize the latent conditional path, not an arbitrary teacher
            # assignment to one of its three possible branches.
            scores = torch.stack([log_probability(distribution, lesson['program'], b) for b in range(3)])
            loss = -torch.logsumexp(scores, 0)
            loss.backward()
            gradient_norm = float(torch.nn.utils.clip_grad_norm_(self.owner.parameters(), 1., error_if_nonfinite=True))
            self.optimizer.step()
            if not all(bool(torch.isfinite(p).all()) for p in self.owner.parameters()):
                raise ValueError('Nonfinite practice update')
            with torch.no_grad(): rebuilt = detached_state(self.rebuild())
            if not all(bool(torch.isfinite(v).all()) for v in rebuilt.values()):
                raise ValueError('Nonfinite re-encoded goal during practice')
        except Exception:
            self.owner.load_state_dict(previous_owner); self.optimizer.load_state_dict(previous_optimizer)
            self.optimizer.zero_grad(set_to_none=True)
            raise
        before = self.weights; self.weights = weight_hash(self.owner); self.state = rebuilt
        record = {'cursor': trial['cursor'], 'lesson': key, 'lesson_identity': identity(lesson),
            'source_sha256': lesson['source_sha256'], 'loss': float(loss.detach()),
            'gradient_norm': gradient_norm, 'before_weights': before, 'after_weights': self.weights,
            'wall_seconds': time.perf_counter()-started}
        trial['updates'].append(record); trial['cursor'] += 1; trial['weights'] = self.weights
        self.save(Path(trial['directory'])/'current')
        return copy.deepcopy(record)

    def finish_learning(self, contract):
        trial, plan = self.check_learning(contract)
        if trial['cursor'] != len(plan['lessons']): raise ValueError('Complete the registered practice before assessment')
        after = contract.assess(self.owner)
        before_scores = trial['baseline']['scores']; after_scores = after['scores']
        gain = after_scores['acquisition']-before_scores['acquisition']
        lost = max(0., before_scores['retention']-after_scores['retention'])
        reward = min(1., max(-1., gain-lost-.001*trial['cursor']))
        # Replay only the decision-time eligibility; constructing/loading that
        # earlier owner must not roll back the live random stream.
        rng, python_rng = torch.get_rng_state(), random.getstate()
        try:
            parent = type(self).load(trial['parent_path'])
            if parent.pending != self.pending or parent.weights != self.pending['weights']:
                raise ValueError('Changed decision-time learning owner')
            import json
            pointer = json.loads((Path(trial['parent_path'])/'CURRENT.json').read_text())
            if pointer['identity'] != trial['parent_identity']:
                raise ValueError('Parent learning revision advanced')
            scores = parent.learning_scores(contract.plans)
            if scores.detach().softmax(-1).tolist() != self.pending['probabilities']:
                raise ValueError('Reconstructed practice decision differs')
            eligible = torch.autograd.grad(scores.log_softmax(-1)[self.pending['action']],
                                          tuple(parent.owner.parameters()), allow_unused=True)
            gradients = {name: None if g is None else g.detach().clone()
                         for (name, _), g in zip(parent.owner.named_parameters(), eligible)}
            del parent, eligible, scores
        finally:
            torch.set_rng_state(rng); random.setstate(python_rng)
        old_owner = copy.deepcopy(self.owner.state_dict()); old_optimizer = copy.deepcopy(self.optimizer.state_dict())
        before_credit = self.weights; gradient_norm = 0.
        try:
            if reward:
                self.optimizer.zero_grad(set_to_none=True)
                for name, parameter in self.owner.named_parameters():
                    gradient = gradients[name]
                    parameter.grad = None if gradient is None else -reward*gradient.to(parameter)
                gradient_norm = float(torch.nn.utils.clip_grad_norm_(self.owner.parameters(), 1., error_if_nonfinite=True))
                self.optimizer.step()
            if not all(bool(torch.isfinite(p).all()) for p in self.owner.parameters()):
                raise ValueError('Nonfinite delayed learning-procedure credit')
            credited = contract.assess(self.owner)
            with torch.no_grad(): rebuilt = detached_state(self.rebuild())
            if not all(bool(torch.isfinite(v).all()) for v in rebuilt.values()):
                raise ValueError('Nonfinite original-goal state after procedure credit')
        except Exception:
            self.owner.load_state_dict(old_owner); self.optimizer.load_state_dict(old_optimizer)
            self.optimizer.zero_grad(set_to_none=True)
            raise
        self.weights = weight_hash(self.owner); self.state = rebuilt
        record = {'kind': 'learning', 'decision': self.pending['id'], 'contract': contract.id,
            'original_goal': copy.deepcopy(self.goal), 'source': self.source, 'selected_plan': copy.deepcopy(plan),
            'baseline': trial['baseline'], 'after_practice': after, 'after_procedure_credit': credited,
            'gain': gain, 'retention_loss': lost, 'reward': reward, 'practice_updates': copy.deepcopy(trial['updates']),
            'predictor_at_decision': self.pending['weights'], 'weights_after_practice': before_credit,
            'weights_after_credit': self.weights, 'policy_credit_update': bool(reward), 'gradient_norm': gradient_norm,
            'independent_evidence_id': contract.id, 'parent_identity': trial['parent_identity'],
            'returned_answer': self.answer(), 'next_action': 'retry the saved original goal with the updated owner',
            'scope': 'supplied schedule selection; benefit on future capabilities requires a matched course'}
        record['id'] = identity(record)
        directory = Path(trial['directory'])
        self.learning_history.append({k: record[k] for k in ('id', 'decision', 'contract')})
        self.credits.append(record)
        self.pending = None; self.learning_trial = None; self.transition = None
        self.save(directory/'completed')
        return copy.deepcopy(record)
