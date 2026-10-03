"""Executable questions, independent assessment and shared-owner credit.

This mixin owns no model or optimizer. CoreSession supplies the same state,
weights, history replay and AdamW used for language and physical investigation.
"""
import copy

import torch

from .core_programs import method, render
from .core_program_verifier import ProgramContract
from .core_proposals import sample, log_probability
from .model import weight_hash
from .native_data import identity
from .native_owner import detached_state


class ExecutableInvestigation:
    def initialize_portfolio(self):
        self.portfolio = []; self.program_reviews = []; self.goal_history = []

    @staticmethod
    def program_goal(goal):
        if set(goal) != {'kind', 'hypothesis', 'arity', 'assumptions'} or goal['kind'] != 'program':
            raise ValueError('Program question requires kind, original wording, arity and assumptions')
        if not isinstance(goal['hypothesis'], str) or not goal['hypothesis'].strip():
            raise ValueError('Original executable question is required')
        if type(goal['arity']) is not int or not 1 <= goal['arity'] <= 4:
            raise ValueError('Declare one to four scalar inputs')
        if not isinstance(goal['assumptions'], list) or any(not isinstance(a, str) or not a for a in goal['assumptions']):
            raise ValueError('Declare the assumption scope')
        return {**copy.deepcopy(goal), 'assumptions': sorted(set(goal['assumptions']))}

    def continue_with_goal(self, goal, *, source):
        self.checked_owner()
        if self.pending is not None or self.transition is not None:
            raise ValueError('Resolve the pending decision and assessment before changing the goal')
        if not source: raise ValueError('Source identity required')
        normalized = self.validate_goal(goal)
        self.goal_history.append({'goal': copy.deepcopy(self.goal), 'source': self.source,
                                  'returned_answer': self.answer()})
        self.goal = normalized; self.source = str(source)
        return self.answer()

    def executable_question(self):
        if self.goal.get('kind') != 'program':
            raise ValueError('Begin an executable question before proposing programs')
        return self.goal['hypothesis']+'\nAssumptions: '+'; '.join(self.goal['assumptions'])

    def program_answer(self):
        self.checked_owner()
        qualified = [p for p in self.portfolio if identity(self.goal) in p['goals']]
        returned = [{'claim': p['claim'], 'method': p['method']['id'], 'program': p['program'],
            'expression': p['expression'], 'review_id': p['review']['id'],
            'scope': p['review']['scope'], 'assumptions': p['review']['assumptions'],
            'contract': p['review']['contract']} for p in qualified]
        return {'original_goal': copy.deepcopy(self.goal), 'source': self.source,
            'weights': self.weights, 'state': self.state_id(),
            'qualified_programs': copy.deepcopy(returned), 'observed_events': int(self.state['events'][0]),
            'status': 'qualified executable answers' if qualified else 'executable investigation remains open',
            'explanation': 'Expressions and proof scopes are rendered from independently checked graphs'}

    @torch.no_grad()
    def propose_programs(self, count=16):
        self.checked_owner(); question = self.executable_question()
        if self.pending is not None:
            if self.pending.get('kind') != 'program': raise ValueError('Another investigation is pending')
            return copy.deepcopy(self.pending)
        distribution = self.owner.program_distribution(self.state, [question], [self.goal['arity']])
        proposals = sample(distribution, count)
        content = {'kind': 'program', 'goal': copy.deepcopy(self.goal), 'source': self.source,
            'weights': self.weights, 'state': self.state_id(), 'events_sha256': identity(self.events),
            'observed_prefix': len(self.events), 'proposals': proposals,
            'policy': 'sampled parallel graphs from the existing conditional field',
            'assessment_seen': False}
        self.pending = {'id': identity(content), **content}
        return copy.deepcopy(self.pending)

    def grade_programs(self, decision, contract):
        self.checked_owner(); question = self.executable_question()
        pending = self.pending
        if (pending is None or pending.get('kind') != 'program' or pending['id'] != decision
                or identity({k:v for k,v in pending.items() if k != 'id'}) != decision
                or pending['goal'] != self.goal or pending['source'] != self.source
                or pending['weights'] != self.weights or pending['state'] != self.state_id()
                or pending['events_sha256'] != identity(self.events)):
            raise ValueError('Current committed program decision required')
        if type(contract) is not ProgramContract:
            raise ValueError('Independent frozen program contract required')
        specification = contract.record; contract_id = contract.id
        if (specification['goal_id'] != identity(self.goal) or specification['arity'] != self.goal['arity']
                or specification['assumptions'] != self.goal['assumptions']):
            raise ValueError('Assessment belongs to a different original goal or assumption scope')
        if any(r['contract'] == contract_id or r['assessment_id'] == specification['assessment_id'] for r in self.program_reviews):
            raise ValueError('Repeated independent program assessment')

        # Contract names, source names and goal wording do not confer novelty.
        semantic_target = specification.get('terms', sorted(specification.get('cases', []), key=identity))
        # An exact total polynomial identity already covers all rational inputs;
        # renaming its assumptions cannot make it a new mathematical finding.
        # Finite coverage is identified by actual input/output pairs instead.
        claim = identity([self.goal['arity'], specification['kind'], semantic_target])
        working = copy.deepcopy(self.portfolio)
        covered = {c for entry in working for c in entry['review']['coverage']}
        seen = {(entry['claim'], entry['method']['id']) for entry in working}
        failures = set()
        assessments = []; rewards = []; new_events = []
        for index, proposal in enumerate(pending['proposals']):
            graph = proposal['program']; construction = method(graph)
            review = contract.review(graph); key = (claim, construction['id'])
            novelty = 0.; progress = 0.; reason = 'independent obligation failed'
            if review['qualified']:
                same_claim = [p for p in working if p['claim'] == claim]
                if key in seen:
                    reason = 'canonical method already retained'
                    existing = next(p for p in working if (p['claim'], p['method']['id']) == key)
                    if identity(self.goal) not in existing['goals']: existing['goals'].append(identity(self.goal))
                else:
                    progress = len(set(review['coverage'])-covered)/max(1, len(review['coverage']))
                    if review['kind'] == 'polynomial_identity' and len(same_claim) < 8:
                        # A finite, diminishing exact-method allocation; never
                        # use the number of unverified branches as reward.
                        novelty = .1/(1+len(same_claim))**2
                    elif same_claim:
                        previous = min(p['method']['cost'] for p in same_claim)
                        novelty = .05*max(0, previous-construction['cost'])/(1+previous)
                    reason = 'new independently qualified contribution'
                    entry = {'claim': claim, 'method': construction, 'program': copy.deepcopy(graph),
                        'expression': render(graph), 'review': review, 'goals': [identity(self.goal)],
                        'decision': decision, 'proposal_index': index, 'weights': self.weights}
                    working.append(entry); seen.add(key); covered.update(review['coverage'])
                    new_events.append({'kind': 'text', 'id': identity(['qualified-program', decision, index]),
                        'source': contract_id, 'evidence_kind': review['kind'], 'assessment': review['id'],
                        'text': 'Independently checked expression '+entry['expression']+'. Scope: '+review['scope']+
                                '. Assumptions: '+'; '.join(self.goal['assumptions'])})
                reward = min(1., progress+novelty)
            else:
                reward = 0. if key in failures else -.1*(1-review['quality'])
                failures.add(key)
            assessments.append({'proposal_index': index, 'review': review, 'method': construction,
                'progress_credit': progress, 'method_bonus': novelty, 'reward': reward, 'reason': reason})
            rewards.append(reward)

        previous_weights = self.weights
        previous_owner = copy.deepcopy(self.owner.state_dict())
        previous_optimizer = copy.deepcopy(self.optimizer.state_dict())
        updated = False; gradient_norm = 0.
        signed_credit = sum(rewards)/len(rewards)
        credit_event = {'kind': 'credit', 'id': identity(['program-credit', decision, contract_id]),
                        'source': contract_id, 'signed_progress': signed_credit}
        # A proof receipt is a real observation about a program. It is explicitly
        # scoped as algebra or finite tests, never as a physical measurement.
        events = [*self.events, *new_events, credit_event]
        try:
            if any(rewards):
                self.optimizer.zero_grad(set_to_none=True)
                state = self.rebuild()
                distribution = self.owner.program_distribution(state, [question], [self.goal['arity']])
                logs = torch.stack([log_probability(distribution, p['program'], p['branch']) for p in pending['proposals']])
                if logs.detach().tolist() != [p['log_probability'] for p in pending['proposals']]:
                    raise ValueError('Reconstructed executable decision differs')
                objective = -(logs*logs.new_tensor(rewards)).mean()
                objective.backward()
                gradient_norm = float(torch.nn.utils.clip_grad_norm_(self.owner.parameters(), 1., error_if_nonfinite=True))
                self.optimizer.step()
                if not all(torch.isfinite(p).all() for p in self.owner.parameters()):
                    raise ValueError('Nonfinite executable-credit update')
                updated = True
            with torch.no_grad(): rebuilt = detached_state(self.rebuild(events))
            if not all(bool(torch.isfinite(v).all()) for v in rebuilt.values()):
                raise ValueError('Nonfinite retained program evidence')
        except Exception:
            self.owner.load_state_dict(previous_owner); self.optimizer.load_state_dict(previous_optimizer)
            self.optimizer.zero_grad(set_to_none=True)
            raise
        self.weights = weight_hash(self.owner); self.state = rebuilt; self.events = events
        self.portfolio = working; self.pending = None; self.transition = None
        record = {'kind': 'program', 'decision': decision, 'original_goal': copy.deepcopy(self.goal),
            'contract': contract_id, 'assessment_id': specification['assessment_id'],
            'contract_record': specification, 'independent_evidence_id': contract_id,
            'committed_proposals': pending, 'assessments': assessments,
            'before_weights': previous_weights, 'after_weights': self.weights,
            'updated': updated, 'gradient_norm': gradient_norm, 'mean_signed_credit': signed_credit,
            'optimizer': 'same session AdamW', 'history_reencoded_under_updated_owner': True,
            'returned_answer': self.answer()}
        record['id'] = identity(record)
        self.program_reviews.append({k:record[k] for k in ('id', 'decision', 'contract', 'assessment_id')})
        self.credits.append(record)  # one full assessment ledger, compact index
        return copy.deepcopy(record)

    def portfolio_snapshot(self):
        return {'portfolio': copy.deepcopy(self.portfolio), 'program_reviews': copy.deepcopy(self.program_reviews),
                'goal_history': copy.deepcopy(self.goal_history)}

    def restore_portfolio(self, record):
        self.portfolio = copy.deepcopy(record.get('portfolio', []))
        self.program_reviews = copy.deepcopy(record.get('program_reviews', []))
        self.goal_history = copy.deepcopy(record.get('goal_history', []))
