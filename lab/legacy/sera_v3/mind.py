"""SERA's mind (B3): imagine -> sense the gap -> experiment -> certify, on one world.

1. Look at the teacher's throws (all objects).
2. Imagine: the imagination proposes K laws with probabilities (sera.imagine). Invented terms it believes in
   (probability mass >= OPEN_MASS, at most MAX_OPEN) enter the judge's evidence ledger from the start, with the
   exponent neighbours of any imagined power (the evidence, not the imagination, picks p). M1 had to wait for an alarm.
3. Evidence: the frozen judge's own ledger (ccops5 truth.Ledger) over the base laws plus those invented terms.
4. Experiment: while not sure and budget remains, make the push, on whichever object and from the push menu, that best
   separates the leading law from what blocks it (the runner-up by evidence, or the band where it is widest). The
   judge is asked for a certificate only when a cheap necessary condition holds (the leader's evidence already clears
   its threshold against every rival by the prequential screen), which saves most certificate computations.
5. Re-imagine every REIMAGINE own pushes with all throws; newly believed invented terms extend the ledger (replayed).
6. At the end: the certificate (checked by the independent checker by whoever calls), the "something else" alarm,
   and a plain-words gap report.
7. Grow (truth-v2, B4; only with grow=True): when no law it can say fits (the alarm, or the judge's "something else"
   reasons), find where the gap lives, weigh grown formulas, experiment again; if no formula can be certified, weigh a
   free curve (a cell) there. A grown claim must also rule out every wide rival (truth.wide_rivals); one that is not
   ruled out joins the ledger, and the experiments separate the two.
Everything the judge decides is unchanged: the imagination only chooses what is tested and which pushes are made.

Plan revision 5 (the one agent; each part is off unless asked for, so every earlier runner behaves as before):
- vocab: the Field weighs only the laws of the terms SERA knows (sera.field.Vocab); a term found or grown during a
  world joins its working vocabulary for the rest of that world (the long-term vocabulary changes only in memory).
- discover: as soon as an idea is missing (the judge's "something else is here", or a shared misfit), the sparse
  proposer (sera.sparse) looks through every term of the judge's dictionary for what the data want, and up to
  DISCOVER_K terms it is not yet weighing join the ledger. The judge weighs them at its own fixed prices.
- stop: a StopRule replaces "always spend the whole budget": it leaves when the proof stops coming closer.
- caretaker: a teacher (sera.caretaker) may describe the law in words, demonstrate a push, or give a hint when SERA
  is stuck. Words act on the Field's belief only (sera.words); a demonstration is one more throw.
- narration: live sentences (sera.narrate), each checked at the world's end against the mind's own records.
- defer_memory: the world's memory is not consolidated here; the caller (sera.agent) consolidates it once, with the
  grade's credit.
"""
import dataclasses
import math

import numpy as np

from ccops5.core import checker, grammar, likelihood as L, mind as M1, truth
from . import design as DS, field as F, imagine as I, lawspace as LS, memory as MV, narrate as NR, proofs as PR, \
    words as WD

LEDGER_REUSE = True     # T3-a: reuse each family's state across ledger rebuilds within a world (exact; see _ledger)
AUDIT_SHARE = True      # T3-b3: the audit's fits are shared across ledger rebuilds within a world (exact; truth.audit_fit)

OPEN_MASS = 0.05        # an invented term enters the ledger when the imagination gives its laws this much probability
MAX_OPEN = 4
REIMAGINE = 4
DISTURBED = 20.0        # v3.1: a push whose committed predictions all miss by this many sensor sigmas (RMS) makes the
                        # object a suspect; if the next push, on another object, holds, the object is disturbed by
                        # something outside any law it weighs (a knock) and is not pushed again (R4-1)
DISCOVER_K = 3          # rev 5: new terms weighed per discovery
MAX_HINTS = 3           # rev 5: at most this many hints per world (Stage 2)


@dataclasses.dataclass(frozen=True)
class StopRule:
    """Revision 5 (WP1): leave a world when the proof stops coming closer, instead of always spending the budget (the
    P2 gate: every unproven world spent all 24 pushes). After each own push the mind records what blocks its leader and
    how far the leader is from passing that step (the shortfall): the screen's deficit in nats; the certificate's
    weakest rival's deficit in nats; log(band / eps) for the band. It stops when, over the last `window` pushes, neither
    the leader nor the blocking step changed and the shortfall fell by less than `min_nats` (`min_band` for the band),
    or when at that pace it would need more pushes than it has left. A step without a number (a misfit, an extra idea)
    stops it after `window` unchanged pushes. The hard budget stays. A decision on past data only, so premise P
    holds and no certificate is touched."""
    window: int = 4
    min_nats: float = 0.5
    min_band: float = 0.02

    def check(self, hist, own, budget):
        if len(hist) < self.window + 1:
            return None
        recent = hist[-1 - self.window:]
        last, first = recent[-1], recent[0]
        if any(h['leader'] != last['leader'] or h['kind'] != last['kind'] for h in recent):
            return None
        if last['kind'] in ('misfit', 'extra', 'other'):
            return 'stuck'
        gain = first['short'] - last['short']
        if gain < (self.min_band if last['kind'] == 'band' else self.min_nats):
            return 'no progress'
        if last['short'] / (gain / self.window) > budget - own:
            return 'too slow'
        return None


@dataclasses.dataclass
class Report:
    claim: tuple
    sure: bool
    certificate: object
    alarm: bool
    reasons: tuple
    throws: int
    own_pushes: int
    certify_calls: int
    families_tracked: int
    proposals: list              # [(family, probability)] at the start
    proposals_end: list
    events: tuple
    ledger: object
    gap: str
    q_start: dict = None         # v3.1: every family's evidence after the teacher's throws (question credit, sera.grade)
    foresight: list = None       # v3.1: committed predictions of its own pushes, scored after each push
    stage: str = 'law'           # truth-v2: 'law' (no growth), 'formula' or 'cell' (certified after growth), 'grown-unsure'
    growth: object = None        # truth-v2: the growth report (address, candidates, what each stage claimed)
    calls: list = None           # rev 5: every certify call (after how many own pushes, the law, accepted, reason, band)
    blocks: list = None          # rev 5: what blocked the leader after each own push, and by how much
    discoveries: list = None     # rev 5: every search for a missing idea and what it found
    stop: dict = None            # rev 5: why it stopped (None: sure, or the old fixed budget)
    stops: list = None           # rev 5: every stop (the search, then growth's own searches, may each stop)
    narration: list = None       # rev 5: its live sentences
    heard: list = None           # rev 5: words heard, as (slot, word index)
    heard_words: list = None     # rev 5: the same, as (slot, word)
    demos: list = None           # rev 5: the caretaker's demonstrated pushes
    belief_leader: float = None  # rev 5: the Field's belief in the claimed law at the end
    memory_state: tuple = None   # rev 5 (defer_memory): (snapshot, tags, context, verified) for the caller
    vocab_used: tuple = None     # rev 5: the working vocabulary's terms at the end
    submitted: bool = False      # rev 5.1: the claim passed every part but the universe audit and went to the office
    second_look: dict = None     # rev 5.1: a return to a refused world: the terms of the judge's rival it now weighs


def _open_terms(proposals):
    mass = {}
    for fam, p in proposals:
        for t in fam:
            if LS.is_open(t):
                mass[t] = mass.get(t, 0.0) + p
    chosen = [t for t, m in sorted(mass.items(), key=lambda kv: -kv[1]) if m >= OPEN_MASS][:MAX_OPEN]
    props = [{'term': t, 'gain': mass[t], 'name': grammar.term_name(t)} for t in chosen]
    return tuple(p['term'] for p in M1.bracket_exponents(props))


def _screen(ledger, leader, alpha=1e-3):
    """Necessary for a certificate: every rival not containing the leader trails it by the claim's threshold."""
    thr = grammar.log_threshold(leader, alpha)
    if not math.isfinite(thr):
        return False
    q = ledger.Q[leader]
    return all(q - ledger.Q[b] >= thr for b in ledger.families if b != leader and not grammar.contains(b, leader))


def _shortfall(ledger, leader, alpha=1e-3):
    """(how many nats the leader still lacks against its closest rival by the screen, that rival)."""
    thr = grammar.log_threshold(leader, alpha)
    q = ledger.Q[leader]
    rivals = [b for b in ledger.families if b != leader and not grammar.contains(b, leader)]
    if not rivals or not math.isfinite(thr):
        return math.inf, None
    b = max(rivals, key=lambda b: ledger.Q[b])
    return thr - (q - ledger.Q[b]), b


def _blocker(ledger, leader, cert):
    """What stands between the leader and a certificate: a rival family to separate it from, an extra idea it needs,
    or None (the band). As ccops5.core.mind.blocker, except that truth-v2's per-knot curve checks (the finest cell
    on each input of a grown claim) are read as the band: a free curve is never a rival (revision 5's first assembled
    run found that the M1 blocker cannot read them, which would also have stopped the never-run B4 gate)."""
    thr = grammar.log_threshold(leader, cert.alpha)
    weak = [b for b, e in cert.rivals.items() if e < thr and b in ledger.Q]
    if weak:
        return max(weak, key=lambda b: ledger.Q[b])
    wide = [(iv[1] - iv[0], i) for i, iv in cert.nested.items()
            if not (iv and isinstance(iv[0], tuple)) and not truth.zero_inside(iv)]
    if wide:
        return grammar.canonical(leader + (max(wide)[1],))
    return None


def _runner_up(ledger, leader):
    rivals = [b for b in ledger.families if b != leader and not grammar.contains(b, leader)]
    return max(rivals, key=lambda b: ledger.Q[b]) if rivals else None


def _jsonable(family):
    return [list(t) for t in family] if family is not None else None


class Mind:
    def __init__(self, imagination, sigma, eps=0.1, K=16, budget=24, on_event=None, design=False, grow=False,
                 grow_budget=None, mask=(), field=False, memory=None, top_k=6, own_programs=4, vocab=None,
                 stop=None, discover=0, caretaker=None, defer_memory=False, on_say=None, prove='inline', claim=None):
        self.imagination = imagination
        self.sigma = sigma
        self.eps = eps
        self.K = K
        self.budget = budget
        self.on_event = on_event
        self.design = design          # v3.1: designed push programs (sera.design) and no pushes on disturbed objects
        self.grow = grow              # truth-v2: the growth stage (sera.grow)
        self.grow_budget = budget if grow_budget is None else grow_budget
        self.mask = frozenset(mask)   # T-S (truth-v3): terms the imagination may not propose (the judge's audit still
                                      # weighs them, and a rival it cannot rule out joins the ledger as usual)
        self.field = field            # T4 (docs/SERA_FIELD_THEORY.md v1.1): the exact belief over every law picks the
        self.memory = memory          # laws the judge weighs; Box-Hill over the top_k believed laws picks the push,
        self.top_k = top_k            # among the designed programs and own_programs SERA composes itself; memory (a
        self.own_programs = own_programs   # sera.field.Memory shared across worlds) is its faded prior
        self.vocab = vocab            # rev 5: a sera.field.Vocab (None: every truth-v1 term, as in v4)
        self.stop = stop              # rev 5: a StopRule (None: always the whole budget)
        self.discover = discover      # rev 5: searches for a missing idea per world (0: never)
        self.caretaker = caretaker    # rev 5: a sera.caretaker teacher (None: SERA is alone)
        self.defer_memory = defer_memory
        self.on_say = on_say
        self.prove = prove            # rev 5.1: 'defer' = the judge's office (sera.proofs): a claim that passes every
                                      # part of the certificate but the universe audit is submitted, not sure
        self.claim = claim            # Decision 11: None = the judge's policy; 'exact' on an investigation (SERA's own
                                      # stricter goal there: tell its answer from a look-alike by evidence)

    def _certify(self, ledger, leader):
        """The judge's certificate; deferred, the same certificate under the 'wide' audit (everything but the universe
        audit), and the office runs the full one on this ledger."""
        if self.prove == 'defer':
            return truth.certify(ledger, leader, self.eps, audit=PR.PRE_AUDIT, claim=self.claim)
        return truth.certify(ledger, leader, self.eps, claim=self.claim)

    def _ledger(self, terms, throws):
        """The judge's ledger over the space with `terms`, on `throws`. T3-a: a family already scored on a prefix of
        these throws (in the last ledger built, or earlier) keeps its running state and steps only the newer throws -
        exactly what Ledger.add computes, since each family's update depends on that family and the throws alone."""
        ledger = truth.Ledger(grammar.space(inventions=terms), self.sigma)
        if AUDIT_SHARE:
            ledger.audit_shared = self.__dict__.setdefault('_audit_share', {})
        if not LEDGER_REUSE:                                # the from-scratch path, kept for the golden comparison
            for t in throws:
                ledger.add(t)
            return ledger
        last = getattr(self, '_last_ledger', None)
        cache = self.__dict__.setdefault('_family_cache', {})
        if last is not None:                                # harvest the newest states (the mind adds to it directly)
            for f in last.families:
                cache[f] = (last.throws[:], last.Q[f], last.post[f])
        throws = list(throws)
        for f in ledger.families:
            k, q, post = 0, 0.0, ledger.post[f]
            hit = cache.get(f)
            if hit is not None and len(hit[0]) <= len(throws) and all(a is b for a, b in zip(hit[0], throws)):
                k, q, post = len(hit[0]), hit[1], hit[2]
            for t in throws[k:]:
                dq, post = L.step(ledger._models[f], post, t, self.sigma)
                q += dq
            ledger.Q[f], ledger.post[f] = q, post
            cache[f] = (throws[:], q, post)
        ledger.throws = throws
        self._last_ledger = ledger
        return ledger

    def live(self, world, resume=None):
        """Live one world. `resume` (rev 5.1, a second look): dict(ledger, cert, budget) - the judge's office refused
        this world's claim because a law outside SERA's ledger was not ruled out; SERA comes back to the same world
        with that law's terms added, from every throw it made there, and experiments again (the inline mind did this
        at once, in the same world)."""
        events = []
        self._family_cache, self._last_ledger = {}, None     # T3-a: family states are reused within a world only
        self._audit_share = {}                               # T3-b3: so are the audit's fits
        self._calls, self._blocks, self._disc, self._narr = [], [], [], []
        self._heard, self._heard_words, self._demos, self._stop, self._stops = [], [], [], None, []
        self._word, self._lex, self._n_disc, self._hints = {}, None, 0, 0
        self._misfit, self._said_block, self._t = False, None, 0
        self._second = None

        def emit(k, event):
            events.append((k, event))
            if self.on_event is not None:
                self.on_event(k, event)

        self._emit = emit
        throws = [t for sit in world.situations() for t in sit]
        self._snap, self._tags, self._skills = None, None, []
        self._vocab = self.vocab if self.vocab is not None else F.FULL
        if self.field:
            self._ctx = F.context(throws)
            if isinstance(self.memory, MV.Memory):            # memory v3 (R4-3b): frozen for the whole world
                self._snap, self._tags = self.memory.begin(self._ctx), MV.Tags()
                self._skills = self._snap.skill_programs(self._ctx)
                self._lex = self._snap.lexicon()
            elif self.memory is not None and self.vocab is not None:
                raise ValueError('the faded field.Memory holds the full vocabulary only; use memory v3')
            self._prior = self._prior_for(self._vocab)
            if self.caretaker is not None and resume is None:  # rev 5, Stage 1: it describes the law in words
                self._hear(self.caretaker.describe())
            if resume is not None:                            # rev 5.1: back to a refused world, with the judge's rival
                back, rc = resume['ledger'], resume['cert']
                if resume.get('investigate'):                 # Decision 11: its answer was proven up to eps, and a
                    looks = sorted(rc.lookalikes or {}, key=lambda b: rc.lookalikes[b]['gap'])   # look-alike agrees:
                    outside = [x for b in looks for x in b if x not in grammar.IDEAS    # find out which is right
                               and x not in rc.inventions]
                    outside = list(dict.fromkeys(outside))
                else:
                    outside = _outside_rivals(back, grammar.canonical(rc.family), rc, tuple(rc.inventions))
                    looks = [b for b, e in rc.rivals.items() if e < grammar.log_threshold(rc.family, rc.alpha)]
                self._extend_vocab(outside)
                terms = tuple(sorted(set(rc.inventions) | set(outside), key=grammar._key))
                throws = list(back.throws)
                self._second = dict(terms=[list(t) for t in outside], rival=[_jsonable(tuple(b)) for b in looks][:1],
                                    investigate=bool(resume.get('investigate')),
                                    gap=float(rc.lookalikes[looks[0]]['gap']) if resume.get('investigate') and looks
                                    else None)
                emit(-1, 'second look: ' + (', '.join(grammar.term_name(t) for t in outside) or 'nothing new'))
                if resume.get('investigate') and looks:
                    b = looks[0]
                    self._say('investigate', law=tuple(rc.family), rival=tuple(b), gap=float(rc.lookalikes[b]['gap']),
                              eps=float(rc.eps))
                else:
                    self._say('second look', terms=tuple(outside))
                log_b = self._belief(self._ledger(terms, throws))
                props = [(h, math.exp(log_b[h])) for h in F.top_laws(log_b, self.K)]
            else:
                log_b = self._belief(self._ledger((), throws))
                props = [(h, math.exp(log_b[h])) for h in F.top_laws(log_b, self.K)]
                terms = F.open_terms(log_b, MAX_OPEN, self.mask)
        else:
            assert resume is None, 'a second look needs the Field mind'
            props, _ = I.imagine_world(self.imagination, throws, self.K)
            terms = tuple(x for x in _open_terms(props) if x not in self.mask)
        if props and resume is None:
            self._say('first guess', law=tuple(props[0][0]), p=float(props[0][1]))
        ledger = self._ledger(terms, throws)
        demonstrate = getattr(self.caretaker, 'demonstrate', None) if resume is None else None
        if demonstrate is not None:                           # rev 5, Stage 1: it shows a push (one more throw)
            demo = demonstrate(ledger.throws, self.sigma)
            if demo is not None:
                k, action = demo
                ledger.add(world.push(k, action, 'demo'))
                self._demos.append(dict(object=int(k), program=[list(s) for s in action.segments]))
                emit(k, 'demo')
                self._say('demo', object=int(k))
        q_start = dict(ledger.Q)
        foresight, disturbed = [], set()
        budget = self.budget if resume is None else resume.get('budget', self.budget)
        ledger, terms, cert, own, calls, props_end = self._investigate(world, ledger, terms, budget, emit,
                                                                       props_end=props, foresight=foresight,
                                                                       disturbed=disturbed)
        alarm = truth.something_else(ledger, cert.family)[0]
        if alarm:
            emit(-1, 'alarm')
        stage, growth = 'law', None
        if self.grow and not cert.accepted and (alarm or any('something else' in r for r in cert.reasons)):
            ledger, cert, stage, growth, own2, calls2 = self._grow(world, ledger, terms, cert, emit, foresight,
                                                                   disturbed)
            own, calls = own + own2, calls + calls2
            alarm = truth.something_else(ledger, cert.family)[0]
        gap = gap_report(cert, alarm)
        belief_leader = None
        if self.field:
            try:
                belief_leader = math.exp(self._belief(ledger).get(grammar.canonical(cert.family), -math.inf))
            except (np.linalg.LinAlgError, ValueError, KeyError):
                belief_leader = None
        memory_state = None
        submitted = bool(cert.accepted) and self.prove == 'defer'   # rev 5.1: the office proves it later; not sure yet
        sure = bool(cert.accepted) and not submitted
        if self._snap is not None:                            # memory v3: the world grows it, once, at its end;
            verified = sure and checker.check(cert, ledger.throws, self.sigma)[0]                 # only what the
            if self.defer_memory:                                                                  # checker
                memory_state = (self._snap, self._tags, self._ctx, verified)                      # re-derives
            else:
                self.memory.consolidate(self._snap, self._tags, self._ctx, 'physics', verified)
        elif self.field and self.memory is not None:          # the world ends: its final belief joins the memory
            self.memory.fade()
            self.memory.add_world(self._ctx, self._belief(ledger))
        return Report(tuple(cert.family), sure, cert, bool(alarm), tuple(cert.reasons),
                      len(ledger.throws), own, calls, len(ledger.families), props, props_end, tuple(events), ledger, gap,
                      q_start=q_start, foresight=foresight, stage=stage, growth=growth, calls=self._calls,
                      blocks=self._blocks, discoveries=self._disc, stop=self._stop, stops=self._stops,
                      narration=self._narr,
                      heard=list(self._heard), heard_words=list(self._heard_words), demos=self._demos,
                      belief_leader=belief_leader, memory_state=memory_state,
                      vocab_used=tuple(self._vocab.terms) if self.vocab is not None else None, submitted=submitted,
                      second_look=self._second)

    def _investigate(self, world, ledger, terms, budget, emit, reimagine=True, props_end=None, foresight=None,
                     disturbed=None):
        """Experiment until sure, stuck (rev 5's StopRule) or out of budget (steps 4-5). Returns (ledger, terms,
        certificate of the final leader, own pushes, certificate calls, the last imagination). foresight and disturbed
        (v3.1) are shared with the caller, so the growth stage keeps the same committed predictions and the same
        knocked objects."""
        foresight = [] if foresight is None else foresight
        disturbed = set() if disturbed is None else disturbed
        suspect = None          # R4-1: an object whose push missed by DISTURBED, until a push on another object decides
        tools = getattr(world, 'tools', None) or {}
        durations, commands = tools.get('durations', M1.DURATIONS), tools.get('commands', M1.COMMANDS)
        own = calls = 0
        cert = None
        last_action = None                                  # memory v3: the push before each certificate
        hist, last_leader = [], None                        # rev 5: what blocked the leader after each own push
        while True:
            leader = ledger.best_family()
            screened = _screen(ledger, leader)
            cert_now = None
            if screened:
                calls += 1
                cert = cert_now = self._certify(ledger, leader)
                self._tag(cert, last_action)
                self._record_call(leader, cert)
                if cert.accepted:
                    break
                outside = _outside_rivals(ledger, leader, cert, terms)          # truth-v2 T2: a wide rival that
                if outside:                                                     # is not ruled out joins the ledger
                    terms = tuple(sorted(set(terms) | set(outside), key=grammar._key))
                    self._extend_vocab(outside)
                    ledger = self._ledger(terms, ledger.throws)
                    emit(-1, 'new rival')
                    continue
            if self.stop is not None or self.discover:          # rev 5: what blocks, and by how much
                kind, short, blocker = self._blocking(ledger, leader, screened, cert_now)
                entry = dict(own=self._t, leader=tuple(leader), kind=kind,
                             short=float(short) if math.isfinite(short) else 1e6,
                             blocker=tuple(blocker) if blocker is not None else None)
                self._blocks.append(entry)                                  # every record kept (narration checks)
                if hist and hist[-1]['own'] == entry['own']:                # the stop rule: one entry per push
                    hist[-1] = entry
                else:
                    hist.append(entry)
                if last_leader is not None and tuple(leader) != last_leader:
                    self._say('leader', law=tuple(leader))
                last_leader = tuple(leader)
                self._say_block(entry, cert_now)
                if kind == 'misfit':
                    self._misfit = True
                if self._misfit and self._n_disc < self.discover:           # an idea is missing: look for it now
                    self._misfit = False
                    new = self._discover(ledger, terms, disturbed)
                    if new:
                        terms = tuple(sorted(set(terms) | set(new), key=grammar._key))
                        self._extend_vocab(new)
                        ledger = self._ledger(terms, ledger.throws)
                        hist.clear()
                        continue
                    self._hint('discover failed')
                if own >= budget:
                    self._stop_at('budget', entry)
                    break
                if self.stop is not None:
                    why = self.stop.check(hist, own, budget)
                    if why and self._hint(why):                              # Stage 2: stuck -> a hint, then again
                        hist.clear()
                        why = None
                    if why:
                        self._stop_at(why, entry)
                        break
            elif own >= budget:
                break
            # what blocks the leader: the runner-up by evidence; or, past the screen, the certificate's own blocker
            # (a needed extra term), else None = the band is too wide
            rival = _blocker(ledger, leader, cert) if screened else _runner_up(ledger, leader)
            if rival is not None and own == 0:
                emit(-1, 'blocked')
            best, best_score = None, -math.inf
            model, post = ledger._models[leader], ledger.post[leader]
            nc = model.n_coef
            if rival is None:                                   # the band blocks: push where it is widest (D10)
                scope, worst = M1.worst_band_cells(ledger, leader)
                targets = set(worst)
            usable = [k for k in range(world.n_situations) if k not in disturbed and k != suspect] or \
                list(range(world.n_situations))
            if self.field and rival is not None:              # T4: Box-Hill among the most believed laws
                best, best_score = self._field_push(ledger, usable, durations, commands)
                usable = []
            for k in usable:
                mu = post.mean[nc + post.order.index(k)] if k in post.order else L.MU_PRIOR[0]
                options = (DS.programs(model, post.mean[:nc], mu, np.random.default_rng([len(ledger.throws), k]),
                                       durations, commands) if self.design
                           else M1.menu(model, post.mean[:nc], mu, durations, commands))
                options = list(options) + list(getattr(self, '_skills', ()))     # memory v3: remembered skills
                for a in options:
                    if rival is not None:
                        s = (DS.surviving_separation(ledger, leader, rival, k, a) if self.design     # R2: only the
                             else M1.separation(ledger, leader, rival, k, a))                      # gap a re-fit keeps
                    else:                                       # readings in the widest-band cells, across objects
                        p = M1.predicted(model, post, k, a)
                        s = sum(truth.cell_of(scope, float(x), float(v)) in targets
                                for x, v in zip(p[:len(p) // 2], p[len(p) // 2:])) - 1e-6 * float(np.max(np.abs(p)))
                    if np.isfinite(s) and s > best_score:
                        best, best_score = (k, a), s
            if best is None:                                    # nothing scores (all NaN): no informative push left
                break
            if self.design and rival is not None and not self.field:    # v3.1: refine the best program's switch times
                for a in DS.refine(best[1]):
                    s = DS.surviving_separation(ledger, leader, rival, best[0], a)
                    if np.isfinite(s) and s > best_score:
                        best, best_score = (best[0], a), s
            k, action = best
            said = _commit(ledger, leader, rival, k, action)          # v3.1: predict before pushing
            q0 = (ledger.Q[leader], ledger.Q[rival] if rival is not None and rival in ledger.Q else None)
            throw = world.push(k, action, 'own')
            last_action = action
            foresight.append(_score(said, throw, ledger.sigma))
            if self.design:     # R4-1: a knock is one object's; a missing idea misses on every object (T-S: 24 of 24
                missed = min(foresight[-1]['leader_rms'], foresight[-1].get('rival_rms', math.inf)) > DISTURBED
                if suspect is not None and k != suspect:              # pushes flagged in most masked worlds). The
                    if missed:                                        # control push on another object decides:
                        emit(k, 'shared misfit')                      # it missed too, so the law misses something
                        self._misfit = True                           # (rev 5: look for the missing idea)
                    else:
                        disturbed.add(suspect)                        # it held, so the suspect is knocked (B3 L1-07:
                        emit(suspect, 'disturbed')                    # 16 pushes went to a knocked object)
                    suspect = None
                elif missed and k not in disturbed:
                    suspect = k
                    emit(k, 'suspect')
            ledger.add(throw)
            foresight[-1]['program'] = [list(s) for s in action.segments]          # rev 5: for the question credit
            if q0[1] is not None:
                foresight[-1]['gain'] = float((ledger.Q[leader] - q0[0]) - (ledger.Q[rival] - q0[1]))
            own += 1
            self._t += 1
            if reimagine and own % REIMAGINE == 0:
                if self.field:                                # re-dream: the whole belief, re-conditioned
                    log_b = self._belief(ledger)
                    props_end = [(h, math.exp(log_b[h])) for h in F.top_laws(log_b, self.K)]
                    fresh = F.open_terms(log_b, MAX_OPEN, self.mask)
                else:
                    props_end, _ = I.imagine_world(self.imagination, ledger.throws, self.K)
                    fresh = {x for x in _open_terms(props_end) if x not in self.mask}
                new = tuple(sorted(set(terms) | set(fresh), key=grammar._key))
                if new != terms:
                    terms = new
                    ledger = self._ledger(terms, ledger.throws)
                    emit(k, 'new idea')
        leader = ledger.best_family()
        if cert is None or tuple(cert.family) != tuple(leader) or cert.digest != truth.digest(ledger.throws):   # never stale
            calls += 1
            cert = self._certify(ledger, leader)
            self._tag(cert, last_action)
            self._record_call(leader, cert)
        return ledger, terms, cert, own, calls, props_end

    # --- rev 5: the parts of the one agent ---
    def _record_call(self, leader, cert):
        band = cert.band if cert.band is not None and np.isfinite(cert.band) else None
        self._calls.append(dict(own=self._t, family=_jsonable(tuple(leader)), accepted=bool(cert.accepted),
                                reason=cert.reasons[0] if cert.reasons else None,
                                band=None if band is None else float(band)))
        if cert.accepted:
            self._say('submit' if self.prove == 'defer' else 'sure', law=tuple(leader))

    def _blocking(self, ledger, leader, screened, cert):
        """(kind, shortfall, the blocking law) for the leader now."""
        if not screened:
            short, rival = _shortfall(ledger, leader)
            return 'screen', short, rival
        reason = cert.reasons[0] if cert.reasons else ''
        if 'something else could be as large' in reason:
            band = cert.band if cert.band is not None and np.isfinite(cert.band) else 1e6
            return 'band', math.log(max(band, 1e-300) / self.eps), None
        if 'something else is here' in reason:
            return 'misfit', 1.0, None
        if 'rival family is not ruled out' in reason or 'rival fit failed' in reason:
            thr = grammar.log_threshold(leader, cert.alpha)
            weak = [b for b, e in cert.rivals.items() if e < thr]
            b = min(weak, key=lambda b: cert.rivals[b]) if weak else None
            return 'rival', (thr - cert.rivals[b]) if b is not None else 1.0, b
        if 'extra terms needed' in reason:
            return 'extra', 1.0, None
        return 'other', 1.0, None

    def _say(self, kind, **numbers):
        s = NR.say(kind, self._t, **numbers)
        self._narr.append(s)
        if self.on_say is not None:
            self.on_say(s)

    def _say_block(self, entry, cert):
        key = (entry['kind'], entry['blocker'])
        if key == self._said_block:
            return
        self._said_block = key
        if entry['kind'] == 'band' and cert is not None and cert.band is not None and np.isfinite(cert.band):
            self._say('blocked', block='band', band=float(cert.band), eps=self.eps)
        elif entry['kind'] in ('rival', 'screen') and entry['blocker'] is not None:
            self._say('blocked', block=entry['kind'], rival=entry['blocker'], short=entry['short'])
        elif entry['kind'] == 'misfit':
            self._say('blocked', block='misfit')
        elif entry['kind'] == 'extra':
            self._say('blocked', block='extra')

    def _stop_at(self, why, entry):
        self._stop = dict(reason=why, own=self._t, kind=entry['kind'], short=entry['short'])
        self._stops.append(self._stop)
        self._say('stop', reason=why, own=self._t)

    def _prior_for(self, vocab):
        """The Field's prior over the vocabulary's laws, fixed for this world (the memory is frozen)."""
        if self._snap is not None:
            return F.with_floor(self._snap.log_prior(self._ctx, vocab=vocab), vocab)
        if self.memory is not None:                        # the faded Polya tree (v4): the full vocabulary only
            return F.with_floor(self.memory.log_prior(self._ctx))
        return F.normalize(F.prior_logp(vocab))

    def _extend_vocab(self, terms):
        """A term found or grown in this world joins the working vocabulary (only when SERA has a vocabulary)."""
        if self.vocab is None or not self.field:
            return
        new = self._vocab.with_terms(terms)
        if new is not self._vocab:
            self._vocab = new
            self._prior = self._prior_for(new)
            if self._heard:
                self._word = WD.factor(self._lexicon(), self._heard, new.laws)

    def _lexicon(self):
        return self._lex if self._lex is not None else WD.flat()

    def _hear(self, sentences):
        """Words from the caretaker: they act on the Field's belief (sera.words), never on the judge."""
        sentences = [s for s in (sentences or ()) if s is not None]
        if not sentences or not self.field:
            return
        for slot, w in sentences:
            self._heard.append((slot, int(w)))
            self._heard_words.append((slot, WD.WORDS[slot][int(w)]))
            self._say('heard', slot=slot, word=WD.WORDS[slot][int(w)])
        self._word = WD.factor(self._lexicon(), self._heard, self._vocab.laws)

    def _hint(self, why):
        hint = getattr(self.caretaker, 'hint', None)
        if hint is None or self._hints >= MAX_HINTS:
            return False
        s = hint(why, self._t)
        if s is None:
            return False
        self._hints += 1
        self._emit(-1, f'hint: {why}')
        self._hear([s])
        return True

    def _discover(self, ledger, terms, disturbed):
        """The sparse proposer over the judge's whole dictionary (sera.sparse): the first terms along the exact lasso
        path that this world's ledger does not weigh yet. It proposes; the judge decides."""
        from . import sparse as SP
        self._n_disc += 1
        leader = ledger.best_family()
        post, nc = ledger.post[leader], ledger._models[leader].n_coef
        mu = {s: float(post.mean[nc + i]) for i, s in enumerate(post.order)
              if s not in disturbed and int(np.argmax(post.knock.get(s, (0.0,)))) == 0}
        new = []
        if mu:
            st = SP.stats(ledger.throws, mu)
            for j in SP.path(st, len(leader) + DISCOVER_K + 4):
                t = SP.DICT[j]
                if t not in grammar.IDEAS and t not in terms and t not in new:
                    new.append(t)
                if len(new) >= DISCOVER_K:
                    break
        self._disc.append(dict(own=self._t, terms=[list(t) for t in new]))
        self._emit(-1, 'discover: ' + (', '.join(grammar.term_name(t) for t in new) or 'nothing new'))
        self._say('discover', terms=tuple(new))
        return tuple(new)

    def _tag(self, cert, program):
        """Memory v3: every certificate call is a tag of the world's working memory (captured or dropped at its end)."""
        if getattr(self, '_tags', None) is not None:
            self._tags.certificate(cert, program)

    def _belief(self, ledger):
        """The Field's exact belief over the vocabulary's laws, on the evidence table with each object's inverse mass
        from the judge's leading fit; objects without one (knocked, or judged so) are left out. Words heard in this
        world multiply it (sera.words)."""
        leader = ledger.best_family()
        post, nc = ledger.post[leader], ledger._models[leader].n_coef
        mu = {s: float(post.mean[nc + i]) for i, s in enumerate(post.order)
              if int(np.argmax(post.knock.get(s, (0.0,)))) == 0}   # independent review review M3: a knocked object's throws
        self._st = F.evidence(ledger.throws, mu, vocab=self._vocab)   # would enter the table without their knock
        self._mu, self._var_mu = mu, {s: float(np.linalg.inv(post.prec)[nc + i, nc + i])
                                      for i, s in enumerate(post.order)}
        prior = self._prior if not self._word else {h: v + self._word.get(h, 0.0) for h, v in self._prior.items()}
        return F.belief(self._st, prior)

    def _field_push(self, ledger, usable, durations, commands):
        """The push that best tells the most believed laws apart (Box-Hill), over the designed programs and programs
        drawn from SERA's own action language."""
        log_b = self._belief(ledger)
        laws = F.top_laws(log_b, self.top_k)
        w = np.array([math.exp(log_b[h]) for h in laws])
        w = w / w.sum()
        rng = np.random.default_rng([len(ledger.throws), 17])
        leader = ledger.best_family()
        model, post = ledger._models[leader], ledger.post[leader]
        nc = model.n_coef
        best, best_score = None, -math.inf
        for k in usable:
            if k not in self._mu:
                continue
            mu = self._mu[k]
            opts = list(DS.programs(model, post.mean[:nc], mu, rng, durations, commands) if self.design
                        else M1.menu(model, post.mean[:nc], mu, durations, commands))
            opts += F.sample_programs(rng, self.own_programs) + list(getattr(self, '_skills', ()))
            for a in opts:
                s = F.box_hill([F.predictive(self._st, h, a, mu, self._var_mu.get(k, 0.0)) for h in laws], w,
                               ledger.sigma)
                if np.isfinite(s) and s > best_score:
                    best, best_score = (k, a), s
        if best is not None:                                   # SERA's own variations of the best program
            for a in [F.mutate(rng, best[1]) for _ in range(self.own_programs)]:
                s = F.box_hill([F.predictive(self._st, h, a, self._mu[best[0]], self._var_mu.get(best[0], 0.0))
                                for h in laws], w, ledger.sigma)
                if np.isfinite(s) and s > best_score:
                    best, best_score = (best[0], a), s
        return best, best_score

    def _grow(self, world, ledger, terms, cert, emit, foresight=None, disturbed=None):
        """Step 7: formulas first, then a free curve. Returns (ledger, certificate, stage, report, own, calls)."""
        from . import grow as GR
        formulas, cells, report = GR.plan(ledger, cert.family, extra_terms=terms)
        emit(-1, f'grow: the gap depends on {report["address"]}')
        self._extend_vocab([t for t in formulas if t[0] != 'cell'])       # rev 5: the Field weighs them too
        own = calls = 0
        f_ledger, _, f_cert, o, c, _ = self._investigate(world, self._ledger(formulas, ledger.throws), formulas,
                                                         self.grow_budget, emit, reimagine=False,
                                                         foresight=foresight, disturbed=disturbed)
        own, calls = own + o, calls + c
        report.update(formula=grammar.name(f_cert.family), formula_sure=bool(f_cert.accepted))
        if f_cert.accepted:
            return f_ledger, f_cert, 'formula', report, own, calls
        if cells:
            c_ledger, _, c_cert, o, c, _ = self._investigate(world, self._ledger(cells, f_ledger.throws), cells,
                                                             self.grow_budget, emit, reimagine=False,
                                                             foresight=foresight, disturbed=disturbed)
            own, calls = own + o, calls + c
            report.update(cell=grammar.name(c_cert.family), cell_sure=bool(c_cert.accepted))
            if c_cert.accepted:
                return c_ledger, c_cert, 'cell', report, own, calls
        return f_ledger, f_cert, 'grown-unsure', report, own, calls


def _outside_rivals(ledger, leader, cert, terms):
    """Grown or open terms of rivals the certificate could not rule out that the ledger does not weigh (T2)."""
    thr = grammar.log_threshold(leader, cert.alpha)
    out = []
    for b, e in cert.rivals.items():
        if e < thr and b not in ledger.Q:
            out += [x for x in b if x not in grammar.IDEAS and x not in terms and x not in out]
    return out


def _commit(ledger, leader, rival, k, action):
    """What it says will happen before it pushes: the readings the leading law predicts (and its rival's, when one
    blocks it), at their current estimates."""
    said = {'situation': k, 'leader': leader, 'f_leader': M1.predicted(ledger._models[leader], ledger.post[leader], k,
                                                                        action)}
    if rival is not None and rival in ledger._models:
        said.update(rival=rival, f_rival=M1.predicted(ledger._models[rival], ledger.post[rival], k, action))
    return said


def _score(said, throw, sigma):
    """How well each committed prediction held (RMS error in sensor sigmas over the readings)."""
    y = np.concatenate([throw.x, throw.v])
    scale = np.concatenate([np.full(len(throw.x), 1 / sigma[0]), np.full(len(throw.v), 1 / sigma[1])])
    rms = lambda f: float(np.sqrt(np.mean(((y - f) * scale) ** 2))) if np.all(np.isfinite(f)) else math.inf
    out = {'situation': said['situation'], 'leader': said['leader'], 'leader_rms': rms(said['f_leader'])}
    if 'f_rival' in said:
        out.update(rival=said['rival'], rival_rms=rms(said['f_rival']))
    return out


def gap_report(cert, alarm):
    """What SERA knows and does not know, in plain words."""
    name = grammar.name(cert.family)
    if cert.accepted:
        where = ''
        if cert.scope:
            (x0, x1), (v0, v1) = cert.scope['x'], cert.scope['v']
            where = f' where I looked (position {x0:.2g} to {x1:.2g}, speed {v0:.2g} to {v1:.2g})'
        tail = ' Something more may be there, but it is too small to see here.' if cert.band else ''
        return f'I am sure the force is {name}{where}.{tail}'
    if alarm:
        return f'Nothing I can say fits: my best guess, {name}, misfits more than chance allows. Something else is here.'
    return f'My best guess is {name}, but I am not sure: {"; ".join(cert.reasons)}.'
