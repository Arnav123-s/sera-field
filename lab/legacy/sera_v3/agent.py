"""SERA as one agent (plan revision 5, WP1): every part switched on together, for the first time.

The verification of 2026-09-27 found SERA's parts built and tested one by one (the Field, memory v3, growth, words,
the credit ladder) but never living a world together. Here one agent lives every world with:
- the Field mind (sera.mind, field=True) with v3.1's designed programs, the suspect rule and growth;
- memory v3 (sera.memory), frozen during each world and consolidated once after it, with the grade's credit
  (sera.credit): the wire through which teaching and correction reach its behaviour;
- its vocabulary (the terms it knows) and discovery of the terms it does not (sera.field.Vocab, sera.sparse);
- the stopping rule (sera.mind.StopRule) instead of a fixed number of pushes;
- the caretaker in Stages 1-2 (sera.caretaker), nobody in Stage 3;
- its own self-grade (sera.selfgrade), trusted only after it has matched the caretaker's grades;
- its choice of doors by learning progress and its own goals (sera.doors) in Stage 3;
- live, checked narration (sera.narrate) and the checked self-report (sera.express).
The judge (ccops5.core) is untouched and never reads anything SERA holds; every "sure" is re-derived by the checker.

Revision 5.1 (the judge's office, sera.proofs): with an office, SERA submits a claim that passed every part of the
certificate but the universe audit and lives its next world; `collect` takes the office's full verdicts as they come
(graded, written into memory, narrated). Without one, every proof runs inline, as before.
"""
import math
import pickle
import time
import types
from collections import Counter

import numpy as np

from ccops5.core import grammar
from . import (caretaker as CT, codedoor as CD, credit as CR, doors as DR, express as EX, grade as G, library as LB,
               memory as MV, mind as SM, narrate as NR, rooms as RM, selfgrade as SG, words as W)

EPS = 0.2
DISCOVER = 2                     # searches for a missing idea per world
GOAL_W = 0.1                     # how much a door's chance of meeting one of its goals adds to its value
MAX_WAITING = 8                  # rev 5.1: claims of this agent the office has not judged yet before SERA waits
MAX_LOOKS = 1                    # rev 5.1: second looks at a world whose claim the judge refused for a rival it named


def kind_of(term):
    return 'idea' if term in grammar.IDEAS else term[0]


class Agent:
    def __init__(self, seed, memory=None):
        self.seed = seed
        self.memory = memory if memory is not None else MV.Memory()
        self.library = LB.Library()
        self.curriculum = DR.Curriculum(seed=seed)
        self.selfgrader = SG.SelfGrader()
        self.graded = []                     # (features, the guess was the law) from Stages 1-2
        self.door_map = {}                   # door -> Counter of the kinds of terms it proved there
        self.done = Counter()                # worlds lived per stage
        self.cpu = 0.0
        self.proofs = 0
        self.pending = {}                    # rev 5.1: office key -> what to do when the judge's verdict comes
        self.office = None                   # rev 5.1: a sera.proofs.Office (None: every proof inline); not saved
        self.revisits = []                   # rev 5.1: refused worlds to look at again (the world, its ledger, the verdict)
        self.kinds = RM.Kinds()              # Stage 5: what a thing's look says about its mass (its own weighings)
        self.code_library = {}               # Stage 5: every program it proved, and how often it met it

    # --- one world ---
    def live(self, world, stage, door=None, learn=True, on_say=None, name=None, resume=None):
        """Live one world (or, with `resume` from self.revisits, look at a refused one again). Returns (the mind's
        report, the unit to save)."""
        t0 = time.process_time()
        care = CT.Caretaker(world, stage, self.seed) if (stage in ('teach', 'practice') and learn) else None
        vocab = self.memory.vocab()
        mind = SM.Mind(None, world.sigma, eps=EPS, budget=3 * world.n_situations, design=True, grow=True, field=True,
                       memory=self.memory, vocab=vocab, stop=SM.StopRule(), discover=DISCOVER, caretaker=care,
                       defer_memory=True, on_say=on_say, prove='defer' if self.office is not None else 'inline',
                       claim='exact' if (resume or {}).get('investigate') else None)
        looks = getattr(world, 'looks', None)                 # Stage 5, rooms: predict each thing's mass from its look
        guess = [self.kinds.predict(look) for look in looks] if looks is not None else None
        r = mind.live(world, resume=resume)
        snap, tags, ctx, verified = r.memory_state
        g = CT.grade(r, verified, world)                  # the observer's grade (the answer is known in dev worlds)
        feats = SG.features(r, EPS)
        self_p = self.selfgrader.p(feats) if self.selfgrader.w is not None else None
        named = care.name() if care is not None else None
        cr = CR.credit(r, stage, verified, named_law=named, self_p=self_p, trust_self=self.selfgrader.trusted)
        before = set(self.memory.vocab_terms())
        if learn:
            self.memory.consolidate(snap, tags, ctx, 'physics', verified, credit=cr)
            self.library.new_world()
            if verified and r.sure:
                self.library.offer(r.claim, r.certificate, (stage, int(self.done[stage])))
            if stage in ('teach', 'practice'):
                self.graded.append((feats.tolist(), grammar.canonical(r.claim) == grammar.canonical(world.spec.family)))
            if door is not None and not r.submitted:           # a submitted world counts when the judge decides
                self.curriculum.record(door, bool(verified and r.sure))
                if verified and r.sure:
                    self.door_map.setdefault(door, Counter()).update(kind_of(t) for t in r.claim)
            self.done[stage if resume is None else stage + ' second look'] += 1
        learned = sorted(set(self.memory.vocab_terms()) - before, key=grammar._key)
        gr = G.grade(r.ledger, r.certificate, bool(verified), q_start=r.q_start, alarm=r.alarm,
                     pushes=max(r.own_pushes, 1))
        statements = EX.self_report(r, gr)
        false = [s.text for s in statements if not EX.check(s, r, gr)[0]]
        false += [s['text'] for s in (r.narration or []) if not NR.check(s, r)[0]]
        cpu = time.process_time() - t0
        self.cpu += cpu
        self.proofs += int(bool(verified and r.sure))
        unit = dict(stage=stage, door=door, level=world.spec.level, seed=world.spec.seed, index=world.spec.index,
                    truth=g['truth'], claim=g['answer'], verdict=g['verdict'], wrong_frozen=g['wrong_frozen'],
                    outside=g['outside'], part=g['part_score'],
                    missing=g['missing_terms'], extra=g['extra_terms'], sure=bool(r.sure), verified=bool(verified),
                    throws=r.throws, own=r.own_pushes, calls=r.certify_calls, cpu=round(cpu, 1),
                    stop=r.stop, stage_reached=r.stage, discoveries=r.discoveries, heard=r.heard_words,
                    demos=len(r.demos or []), belief=r.belief_leader, self_p=self_p,
                    learned=[grammar.term_name(t) for t in learned], learned_terms=[list(t) for t in learned],
                    credit=dict(lessons=[dict(reason=l['reason'], source=l['source'],
                                              what=grammar.name(l['law']) if 'law' in l else list(l['node'][:3]))
                                         for l in cr['lessons']],
                                skills=len(cr['skills']), vocab=[(grammar.term_name(t), how) for t, how in cr['vocab']]),
                    narration=[s['text'] for s in (r.narration or [])],
                    report=[s.text for s in statements], false_sentences=false,
                    events=[str(e) for _, e in r.events], memory=self.memory.summary(),
                    vocab_size=len(self.memory.vocab_terms()), learn=learn,
                    proof='submitted' if r.submitted else None, second_look=r.second_look,
                    kinds=self._weigh(world, r, guess, learn) if looks is not None else None,
                    look=0 if resume is None else resume['k'], look_of=None if resume is None else resume['base'])
        if r.submitted:                                      # rev 5.1: to the office; SERA goes on
            key = f's{self.seed}-{name}-{time.time_ns()}'    # a re-lived world never meets an old verdict
            program = next((t['program'] for t in reversed(tags.items) if t['kind'] == 'proof'), None)
            self.pending[key] = dict(name=name, stage=stage, door=door, learn=learn, family=tuple(r.claim),
                                     context=np.asarray(ctx, float).tolist(), program=program,
                                     n=int(self.done[stage]), submitted=time.time(),
                                     level=self.library.alpha_now(), look=0 if resume is None else resume['k'],
                                     base=name if resume is None else resume['base'])
            self.office.submit(key, r.ledger, r.claim, EPS, world=world)
        return r, unit

    # --- Stage 5: the rooms and the code doors ---
    def _weigh(self, world, r, guess, learn):
        """Rooms: its prediction of each thing's mass from the look (made before the room), its own weighing, and (for
        the observer only) the hidden truth; its weighings join what it knows about looks."""
        meas = RM.measured_masses(r)
        out = []
        for k, look in enumerate(world.looks):
            p, n = guess[k]
            t = world.room.things[k]
            out.append(dict(look=list(look), predicted=p, weighed_before=n, measured=meas.get(k), true=world.masses[k],
                            kind=f'{t.size} {t.material} {t.shape}'))
            if learn and k in meas:
                self.kinds.learn(look, meas[k])
        return out

    def live_code(self, world, stage, door=None, learn=True, on_say=None, name=None):
        """A code task: SERA's loop on code (sera.synth), the observer's check on fresh inputs, the library."""
        t0 = time.process_time()
        res = CD.solve(world)
        verdict = CD.grade(world, res)
        prog = CD.name(res['program'])
        met = self.code_library.get(prog, 0) if res['accepted'] else 0
        said = []
        if res['accepted']:
            said.append(f"I claim the program {prog}: it fit every answer, and my audit passed it on {res['audit_n']} "
                        f"fresh inputs." + (' I have solved this one before.' if met else ''))
        else:
            said.append(f"I claim no program: {res['why'] or 'my audit did not pass'}.")
        for text in said:
            if on_say is not None:
                on_say(dict(own=res['asked'], text=text))
        if learn:
            if res['accepted']:
                self.code_library[prog] = met + 1
            if door is not None:
                self.curriculum.record(door, verdict == 'proven right')
            self.done[stage] += 1
        cpu = time.process_time() - t0
        self.cpu += cpu
        return res, dict(stage=stage, door=door, level='code', seed=world.seed, index=world.index,
                         truth=CD.name(world.program), claim=prog, verdict=verdict, wrong_frozen=verdict == 'SURE AND WRONG',
                         sure=bool(res['accepted']), verified=bool(res['accepted']), own=res['asked'], calls=0,
                         cpu=round(cpu, 1), stop=None, audit_n=res['audit_n'], survivors=res.get('survivors'),
                         met_before=met, narration=said, false_sentences=[], learned=[], vocab_size=len(self.code_library),
                         memory=self.memory.summary(), learn=learn, proof=None)

    # --- rev 5.1: the judge's office ---
    def collect(self, until=None, on_say=None, poll=5.0):
        """Take the office's verdicts that are ready; with `until`, wait until at most that many of this agent's claims
        are still waiting (0: all of them). Returns [(unit name, the unit's new fields)] in the order they came."""
        out = []
        while True:
            for key in [k for k in self.pending if self.office.ready(k)]:
                out.append(self._judged(key, on_say))
            if until is None or len(self.pending) <= until:
                return out
            time.sleep(poll)

    def _judged(self, key, on_say=None):
        """One verdict: the observer's grade of the full certificate (the P2 definitions of a world's end), its proof
        written into memory, the door's record, and SERA's sentence about it (checked against the verdict)."""
        meta = self.pending.pop(key)
        res, job = self.office.take(key)
        cert, name = res['cert'], meta['name']
        if cert is None:                                     # the office runs another judge policy: never a verdict
            return name, dict(proof='office refused', verdict='office policy mismatch', office_why=res['why'],
                              false_sentences=[f"office: {res['why']}"])
        verified = bool(res['verified'])
        sure = bool(cert.accepted)
        proven = sure and verified
        g = CT.grade(types.SimpleNamespace(claim=meta['family'], sure=sure, certificate=cert), verified, job['world'])
        learned = []
        if meta['learn']:
            vocab = [t for t in grammar.canonical(meta['family']) if t not in grammar.IDEAS and t[0] != 'cell'] \
                if proven else []
            before = set(self.memory.vocab_terms())
            self.memory.judged(np.asarray(meta['context'], float), cert, verified, meta['program'], vocab=vocab)
            learned = sorted(set(self.memory.vocab_terms()) - before, key=grammar._key)
            if proven:
                self.library.offer(meta['family'], cert, (meta['stage'], meta['n']), level=meta['level'])
            if meta['door'] is not None:
                self.curriculum.record(meta['door'], proven)
                if proven:
                    self.door_map.setdefault(meta['door'], Counter()).update(kind_of(t) for t in meta['family'])
        self.proofs += int(proven)
        rival = [b for b, e in cert.rivals.items() if e < grammar.log_threshold(cert.family, cert.alpha)]
        if not sure and rival and meta.get('look', 0) < MAX_LOOKS and job['world'] is not None:
            self.revisits.append(dict(base=meta.get('base', name), k=meta.get('look', 0) + 1, stage=meta['stage'],
                                      door=meta['door'], learn=meta['learn'], world=job['world'],
                                      ledger=job['ledger'], cert=cert, budget=job['world'].n_situations))
        looks = getattr(cert, 'lookalikes', None) or {}
        if proven and looks and meta.get('look', 0) < MAX_LOOKS and job['world'] is not None:
            self.revisits.append(dict(base=meta.get('base', name), k=meta.get('look', 0) + 1, stage=meta['stage'],
                                      door=meta['door'], learn=meta['learn'], world=job['world'],     # the author: close
                                      ledger=job['ledger'], cert=cert, budget=job['world'].n_situations,   # is a clue:
                                      investigate=True))                                       # find out which
        s = NR.say('judged', -1, law=tuple(meta['family']), world=name, proven=proven,
                   why='' if proven else NR.judged_reason(res))
        if on_say is not None:
            on_say(s)
        ok, _ = NR.check_judged(s, res, name, meta['family'])
        return name, dict(proof='judged', verdict=g['verdict'], wrong_frozen=g['wrong_frozen'], outside=g['outside'],
                          sure=sure, verified=verified, judged_sentence=s['text'],
                          judged=dict(accepted=sure, reasons=list(cert.reasons), audit=cert.audit,
                                      rivals=len(cert.rivals), band=cert.band, cpu=res['cpu'], wall=res['wall'],
                                      waited=round(time.time() - meta['submitted'], 1),
                                      claim=getattr(cert, 'claim_kind', 'exact'),
                                      lookalikes=[dict(law=grammar.name(b), gap=round(r['gap'], 5),
                                                       evidence=round(r['evidence'], 2) if 'evidence' in r else None)
                                                  for b, r in sorted(looks.items(), key=lambda kv: kv[1]['gap'])]),
                          learned_after=[grammar.term_name(t) for t in learned],
                          learned_terms_after=[list(t) for t in learned],
                          false_sentences=[] if ok else [s['text']], vocab_size=len(self.memory.vocab_terms()))

    # --- Stage 3: its own choices ---
    def goals(self):
        """Its own goals, in words: the kinds of law it failed to prove and still holds a lesson about, and the laws
        its library predicts it has not met."""
        out = []
        kinds = Counter()
        for law, reason, gap, weight, sim, source in self._all_lessons():
            if reason in (MV.REASONS['band'], MV.REASONS['something else'], MV.REASONS['graded wrong'],
                          MV.REASONS['doubted']) and isinstance(law, tuple) and law and isinstance(law[0], tuple):
                for t in law:
                    kinds[kind_of(t)] += weight
        for k, w in kinds.most_common(2):
            out.append(dict(kind=k, why='failed before', weight=round(w, 2),
                            words=f'I want to prove a law with {"a simple idea" if k == "idea" else "a " + k} '
                                  f'in it: I failed at one before.'))
        for law in self.library.empty_slots(limit=2) if self.library.entries else []:
            k = kind_of(next((t for t in law if t not in grammar.IDEAS), law[0])) if law else 'idea'
            out.append(dict(kind=k, why='predicted', law=grammar.name(law),
                            words=f'I predict {grammar.name(law)} exists; I want to meet it.'))
        return out

    def _all_lessons(self):
        out = []
        for l in self.memory.lessons:
            if l['status'] == MV.OPEN and l['law']:
                node = MV.NODES[l['law'] - 1]
                out.append((node[3] if len(node) == 4 else node, int(l['reason']), float(l['gap']), float(l['weight']),
                            1.0, int(l['source'])))
        return out

    def choose_door(self):
        goals = self.goals()
        bonus = {}
        for d in self.curriculum.doors:
            seen = self.door_map.get(d, Counter())
            total = sum(seen.values())
            if total:
                bonus[d] = GOAL_W * sum(seen[g['kind']] / total for g in goals)
        door, why = self.curriculum.choose(bonus)
        why.update(goals=[g['words'] for g in goals], bonus={d: round(b, 3) for d, b in bonus.items()})
        return door, why

    def train_selfgrader(self, held_out=40):
        """Fit on every graded world but the last `held_out`, measure on those (theory §11's apprentice rule)."""
        if len(self.graded) < held_out + 20:
            return None
        X = [x for x, _ in self.graded]
        y = [int(t) for _, t in self.graded]
        self.selfgrader.fit(X[:-held_out], y[:-held_out])
        return self.selfgrader.measure(X[-held_out:], y[-held_out:])

    # --- its whole state ---
    def save(self, path):
        import os
        blob = dict(seed=self.seed, memory=self.memory.to_bytes(), library=self.library, curriculum=self.curriculum,
                    selfgrader=self.selfgrader, graded=self.graded, door_map=self.door_map, done=self.done,
                    cpu=self.cpu, proofs=self.proofs, pending=self.pending, revisits=self.revisits, kinds=self.kinds,
                    code_library=self.code_library)
        tmp = str(path) + '.tmp'
        with open(tmp, 'wb') as f:
            pickle.dump(blob, f)
        os.replace(tmp, path)

    @classmethod
    def load(cls, path):
        with open(path, 'rb') as f:
            blob = pickle.load(f)
        a = cls(blob['seed'], MV.Memory.from_bytes(blob['memory']))
        for k in ('library', 'curriculum', 'selfgrader', 'graded', 'door_map', 'done', 'cpu', 'proofs'):
            setattr(a, k, blob[k])
        a.pending = blob.get('pending', {})
        a.revisits = blob.get('revisits', [])
        a.kinds = blob.get('kinds') or RM.Kinds()
        a.code_library = blob.get('code_library', {})
        return a

    def account(self):
        """What SERA holds now, in its own words (every sentence read off its memory)."""
        m = self.memory
        vocab = m.vocab_terms()
        taught = set(m.vocab_terms('taught'))
        found = [t for t in vocab if t not in taught]
        out = [f'I know {len(vocab)} pieces besides the simple ideas: {len(taught)} I was taught and {len(found)} I '
               f'found myself.']
        if found:
            out.append('The ones I found myself: ' + ', '.join(grammar.term_name(t) for t in found[:12]) + '.')
        for slot, word, meaning, p in W.grounded(m.lexicon()):
            out.append(f'I think "{word}" means {meaning} ({100 * p:.0f}% sure).')
        s = m.summary()
        out.append(f"I hold {s['lessons_open']} open lessons ({', '.join(f'{k} {v}' for k, v in sorted(s['lessons_by_reason'].items()))}), "
                   f"{s['skills_active']} active skills and {s['skills_candidate']} candidate skills, in "
                   f"{len(m.to_bytes())} bytes.")
        out.append(f'I have proven {self.proofs} laws in {sum(self.done.values())} worlds; my library holds '
                   f'{len(self.library.entries)} of them.')
        if self.pending:
            out.append(f'{len(self.pending)} of my claims are still with the judge.')
        out += self.kinds.statements()
        if self.code_library:
            out.append(f'I have proven {sum(self.code_library.values())} programs, {len(self.code_library)} different '
                       f'ones.')
        return out
