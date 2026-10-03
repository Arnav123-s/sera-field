"""SERA: one mind (plan revision 6).

The author, 2026-09-27: "one SERA, one mind that's adaptive, not modules of each separate field or task - it should be
able to be taught and learn all fields"; "no predefined set of words, sentences, formulas"; "the loop is a superposed
behaviour, part of the Field"; "learn and discover from its imagination"; "if it cannot prove something, don't let it
stop - end to end".

There is one class and one way of living. A world (sera.tasks) says what can be seen and done and how an answer is
checked; SERA does the same things in every world:
- think in its one language (sera.lang): what can explain what it sees - its own concepts from any subject,
  expressions of its innate mechanisms, free curves - searched bigger and bigger as it chooses to grow;
- weigh every thought with the Field's three layers (sera.phi): understanding (parts that explained tasks like this),
  laws (description length in its own language, standing), beliefs (this world's evidence, and the words it hears);
- work in configurations it draws from the superposition of ways of working (sera.phi.LoopField): ask, explore, grow,
  imagine, perceive, prove, leave - several at once, each valued with every other's estimate in view, taught by the
  teacher at first and then shaped by its own results;
- improve its own senses and drawing (plan revision 6.2; the author: "it can improve its own drawing skills and get
  more abilities to perceive - why limit it"): where its best idea still misses, it can look closer - a lens on one
  input, 2^j times closer around a point it picks from where the misfit is - and draw finer there (its curves' knots
  across the lens's window). A lens that helped a proof stays one of its senses in every later world;
- keep going until the world's judge accepts its answer (a safety cap only: then it says so and asks us);
- afterwards: a proof becomes understanding and standing; what it proved that was new becomes a concept of its
  language (invention - a shape, a program, a rule, one mechanism); the words it heard are learned against what it now
  understands; it says what it found in its own words; what it set aside is kept, and recognized if it later explains
  something else (serendipity); two different explanations that both work are kept as a question (duality).
"""
import itertools
import math
import sys
import time

import numpy as np

from ccops5.core import grammar, paths, truth
from . import crutches as CR, lang as LG, phi as PH, tasks as TS, talk as TK

MAX_STEPS = 10 ** 6                # no limit of ours on a world (the author, 2026-09-27: 'why limit it')
MAX_WALL = float('inf')             # no limit of ours; the program sets it to the run's own end
PUSHES_PER_OBJECT = 24          # 2026-09-28: 12 -> 24 (the author: 'why limit it'; a law on time needs about 8)
S_MISS = 20.0                    # nats a missing idea stands for
BAND_NATS = 10.0
EXPLORE_W = 3.0                  # nats an unvisited region is worth, before its record corrects it
SURPRISE = TS.DISTURBED          # sigmas: a push its leading law misses by this much surprises it
COST0 = {'ask': 3.0, 'explore': 3.0, 'convince': 3.0, 'grow': 10.0, 'imagine': 2.0, 'prove': 20.0, 'leave': 0.1}
LOOK_NATS = 10.0                 # a place to look closer: a finer curve there explains this many nats more (about
                                 # log of the ~200 windows it weighs, and a margin)
TOP = 4                          # the leading thoughts it keeps a judge's ledger for (predictions, masses)
PART_SIZES = (3, 5, 8, 8)        # expression sizes of a part at growth levels 0-3 (free curves 17 from 2, 33 from 3)
EXACT_SIZES = (3, 5, 7, 8, 9, 10, 11, 12)      # 2026-09-28: it may think bigger while it has time
MAX_HYPS = 600


def part_size(level):
    """A part's expression size at a growth level: PART_SIZES, then 1 more at each level after (no ceiling)."""
    return PART_SIZES[level] if level < len(PART_SIZES) else PART_SIZES[-1] + (level - len(PART_SIZES) + 1)


def _digest(v):
    """A whole value's name (a counterexample's identity: S07 F2, reviewer)."""
    import hashlib
    return hashlib.blake2b(repr(v).encode('utf-8'), digest_size=12).hexdigest()


def exact_size(level):
    """A program's size at a growth level: EXACT_SIZES, then 1 more at each level after (no ceiling)."""
    return EXACT_SIZES[level] if level < len(EXACT_SIZES) else EXACT_SIZES[-1] + (level - len(EXACT_SIZES) + 1)


def lambda_size(level):
    """How big a λ's body may be at a growth level: 3, then one more every three levels (no ceiling: 2026-09-28, the
    user: "give it the freedom to build whatever it needs")."""
    return 3 + level // 3


def _peak_mb():
    """The process's peak memory so far in MB (Linux, macOS, Windows; None if unknown) - 2026-09-29, the Colab RAM
    spike and the laptop's."""
    if sys.platform == 'win32':
        try:
            c = LG._win_counters()
            return c.PeakWorkingSetSize / 1024.0 / 1024.0 if c is not None else None
        except (OSError, AttributeError):
            return None
    try:
        import resource
    except ImportError:
        return None
    kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return kb / 1024.0 if sys.platform != 'darwin' else kb / 1024.0 / 1024.0


def seeing_size(level):
    """How big the body of a function that sees the whole problem may be: the program's size less the few nodes
    around it (it does the program's work in its body), and never smaller than any function's."""
    return max(lambda_size(level), exact_size(level) - 4)


def if_part(level):
    """How big each part of a choice may be at a growth level: 3, then one more every three levels (no ceiling)."""
    return 3 + level // 3


WISH_DEPTH = 6                   # abilities within abilities it may wish for at once (each a smaller problem)
WISH_SHARE = 0.5                 # of its time left in a world, what a wish may take (and of that, a wish within it)
WISH_MAX = 600.0                 # seconds, at most, when a world has no time box of its own
WISH_VIEWS = 6                   # ways of seeing a problem as a smaller one it tries in one wish
WISH_PROBES = 40                 # inputs an ability is built on at most (its examples first)
STEP_LEVEL = 3                   # a step is a program of at most its level-3 size (a small step; the rest is its own)
STEP_TRY = 8                     # steps it tries at once, the best-looking (and the ones it was curious about) first
STEP_DEPTH = 3                   # steps it may take one after another before the rest
STEP_REST = 3                    # the rest is small: up to its level-3 size (8 nodes) from what the steps made
STEP_SEE = 20.0                  # seconds, at least, to see the steps it could take (they come in a few seconds)
NOFIT_LEVEL = 3                  # the teacher shows a step (or a wish) when none of its ideas fits from this level on
REFUTE_ECHO = 0.25               # a refutation's echo, against a proof's 1 (a knob to learn)
TALK_RATE = 0.25                 # how far one corrected reply in a talk moves what its words hold (a knob to learn)
BACK_ON = True                   # stuck, it imagines the way back from the goal (the author, 2026-09-29 night; False: as
#                                  before, for comparison)
BACK_SIZE = 2                    # the last step back from the goal is small: up to its level-2 size
BACK_TRY = 3                     # last steps it follows back at once, the nearest goal first (the fewest parts)
BACK_SHARE = 0.25                # of a world's time left, what imagining the way back may take (after forward steps)
BACK_MAX = 120.0                 # seconds, at most. Knobs to learn.
STEP_SHARE = 0.25                # of its time left in a world, what a try at small steps may take (a wish: half)
STEP_MAX = 240.0                 # seconds, at most (taught, 'where is' took 12 s; steps that are slow go back to the
                                 # whole: 2026-09-29, a step try that took half of a 600 s world starved its wish)
DIM_SIZE = 5                     # the new dimensions it writes: programs up to this many nodes (Decision 15)
QUESTION_SIZE = 7                # 'what is this curve?': formulas of its language up to this many nodes
QUESTION_TOL = 0.05              # that draw the curve's shape within this share of its largest value
PART_ATTEND = 60                 # attention on parts: at most this many drawn parts per input stay in mind
ATTEND_NATS = 40.0               # attention: imagined ideas it holds in mind are within this of its best idea
ATTEND_MAX = 300                 # and at most this many (the rest are let go; imagining itself is unbounded)
FOOTHOLD_NATS = 20.0             # the snowball: a part its idea cannot do without by this much is kept and built on
MAX_PARTS = 4                    # a law's parts, as it grows: 2, then 3 (level 2), then 4 (level 3)
ONE_FIELD = False                # One Field, parts 2 and 4 (plan 3.4, review 12): what it proved and believed is laid
#                                  into the Field's things and rings back by itself - no possibilities store, no
#                                  'recall' move, the talk's reliability in the Field (False: as before, for the A/B)
TENTATIVE_MOST = 1.0             # what a world's tentative beliefs lay in, at most, together (a proof lays in 1)
RING_MOST = 3                    # the loudest ideas a situation rings that become first thoughts
_TOK = {'zero': '0', 'one': '1', 'add': 'add', 'sub': 'sub', 'mul': 'mul', 'lt': 'lt', 'if': 'if'}


def _tokens(e):
    """A number expression of its language over x, v and t, in postfix (the judge's tokens for a dimension, Decision
    15), or None when it uses anything else."""
    if e[0] == 'var':
        return (e[1],) if e[1] in ('x', 'v', 't') else None
    if e[0] not in _TOK:
        return None
    out = ()
    for k in e[2:]:
        tk = _tokens(k)
        if tk is None:
            return None
        out += tk
    return out + (_TOK[e[0]],)


def kind_of(task):
    """What kind of task it perceives: the form of the answer and the kinds of input and output (never a subject)."""
    return f"{task.form}:{','.join(sorted(task.inputs.values()))}->{task.out}"


def _subst(e, old, new):
    if e[0] == 'var' and e[1] == old:
        return LG.node('var', payload=new)
    return (e[0], e[1]) + tuple(_subst(k, old, new) for k in e[2:])


def _aligned(x, y, d):
    """The pairs of elements of x and y at depth d, place by place; None when their shapes differ there."""
    if d == 0:
        return [(x, y)]
    if not (isinstance(x, tuple) and isinstance(y, tuple)) or len(x) != len(y):
        return None
    out = []
    for a, b in zip(x, y):
        got = _aligned(a, b, d - 1)
        if got is None:
            return None
        out += got
    return out


def _elements(x, d):
    if d == 0:
        return [x]
    return [a for v in (x if isinstance(x, tuple) else ()) for a in _elements(v, d - 1)]


def _each_down(c, v, d):
    """The ability c on every element d lists down in v: map(λe. c(e), v), or maps inside maps."""
    body = LG.node('c', LG.node('var', payload='e'), payload=c)
    for i in range(d):
        body = LG.node('map', LG.node('lam', body, payload='e'), v if i == d - 1 else LG.node('var', payload='e'))
    return body


def _put(e, old, sub):
    """e with the input `old` replaced by the expression `sub`."""
    if e[0] == 'var' and e[1] == old:
        return sub
    return (e[0], e[1]) + tuple(_put(k, old, sub) for k in e[2:])


def _ring_safe(value):
    """Lossless JSON identities; non-finite measurements are explicitly absent."""
    if isinstance(value, np.ndarray):
        return _ring_safe(value.tolist())
    if isinstance(value, np.generic):
        return _ring_safe(value.item())
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, (tuple, list)):
        return [_ring_safe(v) for v in value]
    if isinstance(value, dict):
        return {k: _ring_safe(v) for k, v in value.items()}
    return value


class Sera:
    def __init__(self, seed=1, field=None, proposer=None, library_enabled=True):
        self.seed = seed
        self.proposer = proposer
        self.library_enabled = library_enabled
        self.field = field if field is not None else PH.Field(seed)
        self.field.migrate_loop()
        if not hasattr(self.field, 'costs'):
            self.field.costs = {}
        if not hasattr(self.field, 'rates'):
            self.field.rates = []
        if not hasattr(self.field, 'off_choice_rates'):
            self.field.off_choice_rates = list(self.field.rates)
        if not hasattr(self.field, 'senses'):
            self.field.senses = []      # its senses: lenses and dimensions it made (name, born, uses); unused ones fade
        self._task_senses = []
        self._built = []                # abilities it built in this world (wished for, built, used)
        self._dims_cache = None
        self._sync_aliases()                             # loaded Fields are repaired before the world starts

    def _channels(self):
        """What it can measure and draw on: every input, every sense it made (a lens, a new dimension) that has helped
        a proof, and the senses it made in this world."""
        own = [l['name'] for l in self.field.senses if l['uses'] > 0 or l['name'] in self._task_senses]
        return tuple(TS.CHANNELS) + tuple(dict.fromkeys(own))

    # ------------------------------------------------------------------ thinking
    def _concepts(self, masked=()):
        if not self.library_enabled:
            return {'_sig': {}}
        table = self.field.concept_table()
        if masked:
            table = {k: v for k, v in table.items() if k not in masked}
            table['_sig'] = {k: v for k, v in self.field.concept_table()['_sig'].items() if k not in masked}
        return table

    def _cost(self, kind, faculty):
        n, total = self.field.costs.get((kind, faculty), (0, 0.0))
        return (total + COST0[faculty]) / (n + 1)

    def _spend(self, kind, faculty, seconds):
        n, total = self.field.costs.get((kind, faculty), (0, 0.0))
        self.field.costs[(kind, faculty)] = (n + 1, total + seconds)

    def _parts_physics(self, task, level, concepts):
        """Parts a force law can be made of: its concepts and expressions of one input (up to the level's size), on
        each input; free curves from level 2."""
        probes = [{'s': float(v)} for v in (-5.0, -3.0, -1.5, -0.5, 0.0, 0.5, 1.0, 2.0, 4.0)]
        size = part_size(level)
        hit = getattr(self, '_exprs_seen', None)           # the same search again (a new sense at the same size):
        if hit is not None and hit[0] is concepts and hit[1] == size:          # its expressions, found once
            exprs = hit[2]
        else:
            exprs = [e for e, _ in LG.search({'s': 'num'}, 'num', probes, size, concepts)]
            self._exprs_seen = (concepts, size, exprs)
        parts = []
        for ch in self._channels():                       # its inputs, and its lenses (Decision 14)
            drawn = set()                                 # one part per function up to its strength (s, 2s, -s: one)
            for cid, sig in concepts.get('_sig', {}).items():
                if tuple(sig) == ('num', 'num'):
                    k = task.part_knots((ch, 'concept', cid), concepts)
                    if k is not None and self._shape_key(k) not in drawn:
                        drawn.add(self._shape_key(k))
                        parts.append((ch, 'concept', cid))
            for e in exprs:
                if e[0] == 'zero':
                    continue
                if e[0] == 'one' and ch != 'time':          # a steady push is the same on every input: keep it once
                    continue
                k = task.part_knots((ch, 'expr', e), concepts)
                if k is None or self._shape_key(k) in drawn:
                    continue
                drawn.add(self._shape_key(k))
                parts.append((ch, 'expr', e))
            if level >= 2:
                parts.append((ch, 'curve', 17))
            if level >= 3:
                parts.append((ch, 'curve', 33))
        return parts

    @staticmethod
    def _shape_key(knots):
        k = np.asarray(knots, float)
        i = int(np.argmax(np.abs(k)))
        return tuple(np.round(k * np.sign(k[i]), 6))

    def _bits(self, hyp, form, concepts):
        n = len([k for k in concepts if k != '_sig'])
        if form == 'exact':
            return LG.bits(hyp, [0] * n)
        b = 0.0
        for ch, kind, ref in hyp:
            if kind == 'expr':
                b += LG.bits(ref, [0] * n) + math.log2(3)
            elif kind == 'concept':
                b += math.log2(LG.alphabet_size([0] * n)) + math.log2(3)
            else:
                b += 4.0 * ref + math.log2(3)
        return b

    def _hparts(self, hyp, form):
        if form == 'exact':
            return LG.parts(hyp)
        out = []
        for ch, kind, ref in hyp:
            out.append(('input', TS.base(ch)))
            if grammar.is_lens(ch):
                out.append(('lens', ch))
            if kind == 'expr':
                out += [p for p in LG.parts(ref) if p != ('var', 's')]
            elif kind == 'concept':
                out.append(('concept', ref))
            else:
                out.append(('curve', ch))
        return tuple(dict.fromkeys(out))

    def _meanings(self, hyp, form, signs=None, new=None):
        """What SERA can tell about a hypothesis, as meanings for its words (sera.talk)."""
        new = new or {}
        if form == 'exact':
            ms = [('concept', p[1]) for p in LG.parts(hyp) if p[0] == 'concept']
            return [('concept', new['all'])] + ms if 'all' in new else ms
        ms = []
        for i, (ch, kind, ref) in enumerate(hyp):
            cid = ref if kind == 'concept' else new.get(i)
            if cid is not None:
                ms.append(('concept', cid))
            b = TS.base(ch)                                  # a lens is still its input, to its words
            ms.append(('input', b))
            if signs and signs.get(b) and b != 'time':
                ms.append(('sign', int(signs[b])))
        return list(dict.fromkeys(ms))

    def _laws(self, task, parts, evidence_single, level=0, footholds=None):
        """Laws: nothing, each part, and combinations of the best parts on different inputs - pairs always; as it thinks
        bigger, three parts (level 2) and four (level 3: Decision 15, "think in more dimensions") - with at most one
        free curve in a law (two free curves each hold a steady push, so their sum is never pinned down: no judge could
        bound it) and never two on one input (a lens and its own input: one would span the other).
        The snowball (the author: "if anything from its ideas was right, it can leverage and learn that part"): its
        footholds with every other part it can think of - a part that explains only what the footholds leave (small
        on its own) is still tried beside them, so small finds compound."""
        laws = [()] + [(p,) for p in parts]
        held = tuple(sorted(footholds or (), key=repr))
        if held:
            hb = {TS.base(p[0]) for p in held}
            laws.append(held)
            for q in parts:
                law = tuple(sorted(held + (q,), key=repr))
                if (q not in held and TS.base(q[0]) not in hb and len(law) <= MAX_PARTS
                        and sum(p[1] == 'curve' for p in law) <= 1):
                    laws.append(law)
        best = {}
        for p in parts:
            best.setdefault(p[0], []).append((evidence_single.get((p,), -math.inf), repr(p), p))
        ranked = {ch: [p for _, _, p in sorted(v, reverse=True)] for ch, v in best.items()}
        chans = sorted(ranked)
        n_max = min(MAX_PARTS, 2 + (level >= 2) + (level >= 3))
        width = {2: 8, 3: 3, 4: 2}
        for n in range(2, n_max + 1):
            for combo in itertools.combinations(chans, n):
                if len({TS.base(c) for c in combo}) < n:
                    continue
                for law in itertools.product(*[ranked[c][:width[n]] for c in combo]):
                    if sum(p[1] == 'curve' for p in law) > 1:
                        continue
                    laws.append(tuple(sorted(law, key=repr)))
        return list(dict.fromkeys(laws))

    # ------------------------------------------------------------------ living one world
    def live(self, task, teaching=False, masked=(), on_say=None, max_steps=None, ring_log=None,
             recheck_advice=True, on_schedule=None, answer_channel=None):
        """Live one world until its judge accepts an answer (or the safety cap). Returns the record of the world."""
        max_steps = MAX_STEPS if max_steps is None else max_steps
        F = self.field
        kind = kind_of(task)
        ctx = task.context()
        # Ephemeral observation only: never saved in the Field or consulted for a choice/credit.
        self._ring_observer = (dict(schema_version=1, task=task.name, subject=task.subject, form=task.form,
                                    teaching=bool(teaching), world_index=F.tasks, mind_seed=self.seed,
                                    initial_context=ctx, initial_cues=[],
                                    candidates=[], selected=[], events=[], writes=[], credited_object=None,
                                    projection_complete=False, trigger_complete=False) if ONE_FIELD else None)
        self._ring_selected = {}
        self._ring_log_path = ring_log if ONE_FIELD else None
        hints = F.take_hints(kind)                          # words we answered it with: heard in this task
        if hints:
            task.words = list(task.words) + [w for w in hints if w not in task.words]
        concepts = self._concepts(masked)
        grammar.use_library(F.shapes())                    # its shapes, fixed before this world (Decision 12)
        library = tuple(sh for c in F.concepts if c['id'] not in masked          # the ones it may claim with (a twin's
                        for sh in (c.get('shapes') or ([c['shape']] if c.get('shape') is not None else [])))  # hidden: none)
        rng = np.random.default_rng([self.seed, 7, F.tasks])
        t0, c0 = time.time(), time.process_time()
        LG.DEADLINE[0] = t0 + MAX_WALL                     # a search does not think past the world's time box
        LG.forget_searches()                               # another world's searches are no use here (2026-09-29)
        ideas = self._ideas()                              # it reads what the world gives it (2026-09-29): a passage
        for s in (task.reading() if hasattr(task, 'reading') else ()):          # to read first (closed book), and
            ideas.read(s, task.name)                                            # the stories of its examples; each
        if hasattr(task, 'sentences'):                                           # thing in them keeps an idea
            for x, _ in task.data:
                for s in task.sentences(x):
                    ideas.read(s, task.name)
        if hasattr(task, 'mind'):                          # its memory is part of how it perceives: what a question
            task.mind = ideas if ideas.read_n else None    # names that the situation does not tell comes to mind
        stops0 = LG.MEMORY_STOPS[0]                        # searches stopped at the memory wall, from here
        say = []

        def speak(what, text, **n):
            say.append(dict(step=st['steps'], what=what, text=text, **n))
            if on_say is not None:
                on_say(say[-1])

        st = dict(level=0, steps=0, proven=None, misfit=False, stuck=0, surprises=set(), explored=0, asked=0,
                  best_doubt=math.inf, since_best=0, judge_short=0.0, tested=set(), imagined=False, origins={},
                  dual=None, time={}, footholds={}, moved=set(), judge_where=None, method=None, thought=set(),
                  peak=[_peak_mb() or 0.0], peak_by={}, teaching=bool(teaching),
                  recheck_advice=bool(recheck_advice), pushes_since_report=0)
        self._task_senses = []
        self._built = []
        self._open_steps = []                              # steps it was curious about and has not finished (here)
        self._dims_cache = None
        self._level = 0
        self._footholds = st['footholds']
        extra = {}                                         # hypotheses it imagined or recalled: key -> origin
        mu = None
        led = None
        self.field.forget_traces()                         # nothing of this world has taken part yet (before it first
        hyps = self._generate(task, 0, concepts)           # perceives: S05 F5, reviewer)
        trigger0 = time.time()
        self._evoke(task, concepts, extra, speak, library, ctx)   # what the situation rings in the Field (the trigger)
        st['time']['trigger'] = round(time.time() - trigger0, 2)
        choices = []
        tension_log = []
        clock = [time.time()]

        def lap(phase):                                    # where its time goes (seconds per phase, this world)
            now = time.time()
            st['time'][phase] = round(st['time'].get(phase, 0.0) + now - clock[0], 2)
            clock[0] = now
            peak = _peak_mb()                              # and which phase raised the process's peak memory
            if peak is not None and peak > st['peak'][0]:
                st['peak_by'][phase] = round(st['peak_by'].get(phase, 0.0) + peak - st['peak'][0], 1)
                st['peak'][0] = peak

        while True:
            lap('other')
            # --- beliefs: every thought at once, the three layers ---
            if task.form == 'strengths':
                parts = hyps
                if mu is None:
                    mu = task.first_masses()                # sensed without a law (the empty law explains nothing)
                single = task.evidence([(p,) for p in parts], concepts, library, mu)
                if len(parts) > PART_ATTEND * 3:                # attention on parts: per input, the best by its own
                    by_ch = {}                                  # evidence, and every curve and foothold
                    for q in sorted(parts, key=lambda q: -single.get((q,), -math.inf)):
                        by_ch.setdefault(q[0], []).append(q)
                    keep = {q for qs in by_ch.values() for q in qs[:PART_ATTEND]}
                    keep |= {q for q in parts if q[1] == 'curve' or q in st['footholds']}
                    hyps = parts = [q for q in parts if q in keep]
                    single = {k: v for k, v in single.items() if k[0] in keep}
                laws = (self._laws(task, parts, single, st['level'], st['footholds'])
                        + [k for k in extra if k not in single])
                logE = task.evidence(laws, concepts, library, mu)
            else:
                laws = hyps + [k for k in extra if k not in hyps]
                logE = task.evidence(laws, concepts)
            raw = dict(logE) if task.form != 'strengths' else None    # what fits the examples, before the words
            if task.words:
                for h in list(logE):
                    logE[h] += F.lexicon.log_likelihood(task.words, self._meanings(h, task.form))
            if not logE:                                   # nothing it can think of fits: it must grow
                logE = {(): -1e6} if task.form == 'strengths' else {}
            H = list(logE)
            st['thought'].update(H)                            # every idea it has weighed here, kept or let go
            hparts = {h: self._hparts(h, task.form) for h in H}
            bits = {h: self._bits(h, task.form, concepts) for h in H}
            if H:
                logU, logL, logB, phi, tension = F.layers(kind, ctx, hparts, logE, bits)
                order = sorted(H, key=lambda h: -phi[h])
                if hasattr(self, '_u_syndrome'):
                    self._u_syndrome(task, order, logU, logB)
                if hasattr(self, '_u_order'):
                    order = self._u_order(task, order)
                leader = order[0]
                doubt = -phi[leader]
            else:
                phi, order, leader, doubt, tension = {}, [], None, S_MISS, 0.0
                if hasattr(self, '_u_syndrome'):
                    self._u_syndrome(task, [], {}, {})
            st['none_fit'] = st['leader_misfits'] = False  # what the examples say, fresh each time (S09 #4, reviewer: its
            if raw:                                        # doubt is relative - "0.0 nats" while its best idea fits
                fitting = [h for h in order if raw.get(h, -math.inf) > -1e-9]   # no example - and the judge's "it
                st['none_fit'] = not fitting                                       # does not fit" never reached it)
                st['fitting'] = set(fitting)
                st['leader_misfits'] = leader is not None and leader not in fitting
                if st['leader_misfits'] and fitting and CR.on('leader_override'):       # an idea it weighs lower fits: that one leads
                    leader = fitting[0]
                    doubt = -phi[leader]
            if self._ring_observer is not None:
                for h, item in self._ring_selected.items():
                    item['used'] |= h in logE
                    item['led'] |= h == leader
            tension_log.append(round(float(tension), 3))
            lap('beliefs')
            runner = order[1] if len(order) > 1 else None
            st['runner'] = runner
            tie = bool(runner is not None and st['proven'] is not None and
                       logE[leader] - logE[runner] < 2.0 and not (set(hparts[leader]) & set(hparts[runner]) - {
                           ('input', 'position'), ('input', 'speed'), ('input', 'time')}))
            # physics: the judge's ledger over the leading thoughts (their predictions, each thing's mass)
            fams, weights = [], []
            if task.form == 'strengths' and order:
                for h in order[:TOP]:
                    f = task.family(h, concepts, library)
                    if f is not None and f not in fams:
                        fams.append(f)
                        weights.append(math.exp(phi[h]))
                led = task.ledger(fams)
                if fams[0]:                                 # the leading law's own fit refines the masses
                    better = task.masses(led, fams[0])
                    if len(better) >= len(mu) - 1:
                        mu = better
            lap('ledger')
            p = st['proven']
            if p is not None and task.form == 'exact':    # what it proved, on what it now sees: checked again only
                seen = (self._n_data(task), getattr(self._ideas(), 'rev', 0))   # when an example came or its memory
                if p.get('checked') != seen:                                      # changed (S07 F1, reviewer)
                    if task.consistent(p['law'], concepts):
                        p['checked'] = seen
                    else:                                  # a new example goes against it: proved no more (S06 F8)
                        wit = next(((x, y) for x, y in task.data if hasattr(task, '_value')
                                    and task._value(p['law'], x, concepts) != y), None)
                        st['proven'] = None
                        self._refute(task, ('input', p['law'], _digest(wit if wit is not None else seen)), st, speak,
                                     'A new example goes against what I proved; I think again.')
            proven_now = st['proven'] is not None      # the judge accepted an answer here: it may leave (2026-09-28:
            # it was "the leader is the proven law"; on wind 1 a new idea led after the proof, and SERA stayed 1.6 hours)
            if doubt < st['best_doubt'] - 0.5:
                st['best_doubt'], st['since_best'] = doubt, 0
            else:
                st['since_best'] += 1
            stuck = st['since_best'] >= 12
            # --- what each faculty expects to return, per second ---
            cand = []
            if order and not (task.form == 'strengths' and task.pushes >= PUSHES_PER_OBJECT * task.world.n_situations):
                if task.form == 'strengths':
                    cand = task.actions(rng, led, fams, weights) if fams else []
                else:
                    top = order[:30]
                    cand = task.actions(rng, top, [math.exp(phi[h]) for h in top], concepts)
            if hasattr(self, '_u_actions'):
                cand = self._u_actions(task, cand)
            best_info = max((c['info'] for c in cand), default=0.0)
            best_novel = max((c['novel'] for c in cand), default=0.0)
            lap('actions')
            p_missing = (0.9 if (st['misfit'] or not order or stuck)     # no progress for a while: an idea is missing
            #   (none of its ideas fitting the examples is kept in st and said when it asks us, but is not fed to its
            #   ways of working yet: forcing growth, or its moment's 'misfit' - physics' alarm, to which its taught
            #   ways answer - made its list-then-numbers lesson take 832 s instead of under 200 s; a feature of its
            #   own, taught, is the way - S09 #4)
                         else 0.5 * (1 - math.exp(-max(0.0, tension - 8.0) / 8.0)))
            moves = self._moves_available(task, kind, leader, st, hyps, extra, concepts)
            trig = dict(doubt=min(doubt, 20.0) / 10, misfit=float(st['misfit']), short=float(st['judge_short'] > 0),
                        level=min(st['level'], 6) / 3, tension=min(tension, 50.0) / 10, stuck=float(stuck),
                        curve=float(task.form == 'strengths' and bool(leader) and any(p[1] == 'curve' for p in leader)),
                        proven=float(proven_now))
            untested = (leader is not None and (leader, self._n_data(task)) not in st['tested']
                        and not (st['proven'] is not None and st['proven']['law'] == leader))   # what it proved needs
            #                            no proof again: more examples are no new evidence for it (S06 F2, reviewer)
            avg_rate = self._world_rate()
            near = [self._closeness(c, st['judge_where']) for c in cand] if st['judge_where'] and cand else []
            est = {'ask': min(best_info, 20.0), 'explore': EXPLORE_W * best_novel,
                   'convince': min(st['judge_short'], S_MISS) * max(near, default=0.0)
                               * (0.5 ** st.get('shown', 0) if CR.on('convince_halving') else 1.0),
                   #   each push it made to show the judge since the judge last said where it is unsure is worth half
                   #   the one before, until it asks again (2026-09-30, the one-SERA run: 100+ pushes at one spot on
                   #   stiff 2, never asking whether they convinced it)
                   'grow': p_missing * S_MISS, 'imagine': F.methods.value(kind, moves, trig) if moves else 0.0,
                   'prove': (math.exp(-doubt) if untested else 0.0) * PH.V_DONE}
            est = {f: v / self._cost(kind, f) for f, v in est.items()}      # nats per second
            est['leave'] = avg_rate if proven_now else 0.0                   # what its time is worth elsewhere
            available = set()
            if cand:
                available.add('ask')
                if best_novel > 0:
                    available.add('explore')
            if st['level'] < self._max_level(task):
                available.add('grow')
            if moves:
                available.add('imagine')
            if near and max(near) > 0.05 and st['judge_short'] > 0:
                available.add('convince')
            if untested and leader is not None and not (task.form == 'exact' and (not order or not
                                                                            task.consistent(leader, concepts))):
                available.add('prove')
            if proven_now:
                available.add('leave')
            moment = dict(doubt=min(doubt, 20.0) / 10, tension=min(tension, 50.0) / 10, level=min(st['level'], 6) / 3,
                          proven=float(proven_now), misfit=float(st['misfit']), steps=math.log1p(st['steps']) / 5,
                          stuck=float(stuck), tie=float(tie), teaching=float(teaching),
                          shown=math.log1p(st['pushes_since_report']) if CR.on('teach_rechecking') else 0.0)
            if stuck and st['since_best'] == 12 and not proven_now:
                self._ask_us(task, leader, doubt, st, speak)
            if not available or st['steps'] >= max_steps or time.time() - t0 > MAX_WALL:
                if not proven_now:
                    self._ask_us(task, leader, doubt, st, speak, cap=True)
                break
            advice = None
            if teaching:                                   # the teacher shows its way of working here (evidence),
                shown = self.teacher_method(moment, moves, st)    # and its way of imagining (a method)
                if shown is not None:
                    F.methods.teach(kind, shown, trig)
                advice = self.teacher_way(moment, available, st, shown)
                F.loop.teach(kind, moment, est, available, advice)
            if hasattr(self, '_u_configuration'):
                st['u_teacher_advice'] = advice
                selected = self._u_configuration(task, leader, available, moves, moment, trig, st, rng, t0)
            else:
                selected = None
            config, vals = (F.loop.choose(kind, moment, est, available, rng) if selected is None else selected)
            if on_schedule is not None:
                on_schedule(dict(moment=dict(moment), estimates=dict(est), available=sorted(available),
                                 advice=advice, config=list(config), judge_where=st['judge_where'],
                                 pushes_since_report=st['pushes_since_report']))
            st['steps'] += 1
            if config == ['leave']:
                choices.append(dict(step=st['steps'], config=config, values={f: round(v[0], 3) for f, v in vals.items()}))
                F.loop.learn('leave', F.loop.features(moment, est, 'leave'), avg_rate)
                break
            # --- work in that configuration: the faculties together, the most valued first ---
            ret = {}
            before = doubt + st['judge_short']
            ran, js_drop = [], 0.0                          # what ran, in the order it ran (S07 F3, reviewer)
            for fac in config:
                c1 = time.process_time()
                if fac == 'prove':
                    js0 = st['judge_short']
                    ok = self._prove(task, leader, concepts, library, st, speak)
                    if ok and teaching and (answer_channel is None or getattr(task, 'course_lesson', False)):
                        wrong = self._teacher_says_wrong(task, leader, concepts, st)   # F4, reviewer: not after it was
                        if wrong is not None:                                           # rewarded) - fail and credit
                            ok, st['proven'], st['counter'] = False, None, wrong
                            if task.form == 'strengths':
                                st['misfit'] = True        # the law it claims is not the world's: think again
                            speak('refused', 'The teacher says my proof is wrong here'
                                  + (' and shows me an example' if wrong[0] == 'input' else '') + '; I keep looking.')
                    js_drop = js0 - st['judge_short']       # what the proof itself removed of the judge's doubt
                    ran.append('prove')
                    same = (leader if task.form != 'strengths' or st['proven'] is None   # physics: what was sent
                            else (st['proven']['family'], st['proven']['n']))            # and certified (S11b F3)
                    new_idea = ok and same not in st.setdefault('echoed', set())
                    ret['prove'] = PH.V_DONE if new_idea and answer_channel is None else 0.0
                    if ok:                                 # evidence: only its cost (S06 F2, reviewer). The echo, once
                        st['echoed'].add(same)             # this moment's ways of working are traced (S05 F6) - only
                        st['confirmed'] = new_idea         # for a new confirmation (2026-09-30, seed 3: it proved
                        #                                    who(g), then grew and re-proved it five times, each echo
                        #                                    crediting the growing, 1,789 s of a lesson)
                    else:                                  # refuted only by what goes against it - an input it gets
                        counter = st.pop('counter', None)  # wrong, a force it misses - not by a judge that is not
                        if counter is not None and counter not in st.setdefault('refuters', set()):   # yet sure
                            st['refuters'].add(counter)    # (S06 F1, reviewer); the same counterexample refutes once
                            self._observe_ring(task, 'refuted', counter[1], step=st['steps'],
                                               reason=counter[0], counter=counter)
                            st['refuted'] = True
                elif fac == 'grow':
                    st['level'] += 1
                    self._level = st['level']
                    hyps = self._generate(task, st['level'], concepts)
                    st['misfit'] = False
                    speak('grow', f'I think bigger (level {st["level"]}).', level=st['level'])
                    ret['grow'] = None
                    ran.append('grow')
                elif fac == 'imagine':                     # its methods of imagination: a draw from their superposition
                    st['methods'] = (self._u_methods(kind, moves, trig, rng, st) if hasattr(self, '_u_methods')
                                     else F.methods.choose(kind, moves, trig, rng))
                    st['trig'] = trig
                    for method in st['methods']:
                        new = self._imagine(method, task, kind, leader, concepts, library, mu, st, hyps, extra, speak,
                                            known=st['thought'])
                        st['thought'].update(new)              # never new again, even after attention lets it go
                        for key, (origin, m) in new.items():
                            extra[key] = origin
                            st['origins'][key] = m
                        speak('imagine', f"I imagine by {' then '.join(F.methods.expand(method))}: {len(new)} new "
                                         f"ideas.", method='+'.join(method), n=len(new))
                    held, let_go = self._attend(task, extra, logE, concepts, library, mu)
                    if let_go:
                        speak('attend', f'I keep {held} of my imagined ideas in mind and let {let_go} go.',
                              held=held, let_go=let_go)
                    if st.pop('regen', False):             # a new sense: think again with it
                        hyps = self._generate(task, max(st['level'], 2), concepts)
                    ret['imagine'] = None
                    ran.append('imagine')
                elif fac in ('ask', 'explore', 'convince'):
                    if fac in ret:
                        continue
                    pushers = [f for f in config if f in ('ask', 'explore', 'convince')]
                    wts = {f: max(vals[f][0], 1e-3) for f in pushers}
                    top_info = max(best_info, 1e-9)
                    pick = max(cand, key=lambda c: sum(wts[f] * (c['info'] / top_info if f == 'ask' else c['novel']
                                                                 if f == 'explore' else
                                                                 self._closeness(c, st['judge_where']))
                                                       for f in pushers))
                    if 'convince' in pushers:
                        w = st['judge_where']
                        speak('convince', f"The judge is least sure near position {w['x']:.2f}, speed {w['v']:.2f}, "
                                          f"time {w['t']:.2f}: I push to show it there.")
                        ret['convince'] = None
                        st['shown'] = st.get('shown', 0) + 1
                    result = task.act(pick['action'])
                    self._observe_push(st)
                    if ONE_FIELD and task.form == 'strengths':
                        st['support'] = {}                 # new throws require new representation support
                        st.pop('adequate', None)
                    st['asked'] += 1
                    if task.form == 'strengths':
                        sur = task.surprise(result, pick['predicted'])
                        if sur > SURPRISE:
                            st['surprises'].add(pick['action'][1])
                            if len(st['surprises']) >= 2:
                                st['misfit'] = True
                        ret_explore = math.log1p(sur / 5.0) if math.isfinite(sur) else 3.0
                    else:
                        ret_explore = 1.0 if pick['predicted'] != result[1] else 0.2
                    if 'explore' in pushers:
                        st['explored'] += 1
                        ret['explore'] = ret_explore
                    if 'ask' in pushers:
                        ret['ask'] = None                   # its return is the doubt it removes (below)
                    ran.extend(pushers)                     # one push: all of them ran here, together
                self._spend(kind, fac, time.process_time() - c1)
                lap(fac)
            # --- what the configuration returned, per faculty ---
            after_doubt = self._doubt_after(task, concepts, library, mu, extra, hyps, kind, ctx)
            lap('doubt')
            after = after_doubt + st['judge_short']
            gain = before - after
            if hasattr(self, '_u_moment_return'):
                self._u_moment_return(st, gain)
            F.fade_traces()                                # what took part before fades; what took part now is traced
            result = 'prove' in ran and (st.get('confirmed') or st.get('refuted'))
            causal = ran[:ran.index('prove')] if result else ran   # only what ran before the result led to it; the
            after_proof = set(ran[ran.index('prove') + 1:]) if 'prove' in ran else set()   # proving has its return now
            for fac in config:                             # (S06 F3, S07 F3, reviewer: a grow after the proof was credited
                r = ret.get(fac)                           # with it, and with the judge's doubt the proof removed)
                if r is None:
                    r = gain - (js_drop if fac in after_proof else 0.0)
                y = float(np.clip(r / self._cost(kind, fac), -5.0, 20.0))
                x_fac = F.loop.features(moment, est, fac)
                if answer_channel is not None and fac == 'prove' and st.get('confirmed'):
                    st['course_prove_return'] = (x_fac, self._cost(kind, fac))
                else:
                    F.loop.learn(fac, x_fac, y)
                if fac in causal:                          # its cost kept: the echo is worth per second, as here
                    F.trace(('loop', fac, x_fac, self._cost(kind, fac)))
            if 'imagine' in config:                        # what its methods of imagining returned, at those triggers
                for method in st.get('methods') or ():
                    returns = st.get('u_method_returns', {}).get(method)
                    earned = returns.pop(0) if returns else float(np.clip(gain, -20.0, 40.0))
                    F.methods.learn(kind, method, st['trig'], earned)
                    if 'imagine' in causal:
                        F.trace(('method', kind, method, dict(st['trig'])))
            if st.pop('confirmed', False):                 # the echo: the whole Field changes with a proof (the
                if answer_channel is None:                # course verdict precedes this credit, in _finish
                    self._echo(task, +1.0, speak)
            elif st.pop('refuted', False):                 # and with a refutation, the other way, more softly: one
                self._echo(task, -REFUTE_ECHO, speak)      # refuted idea says less against the ways that made it
            st.pop('refuted', None)
            st.pop('confirmed', None)
            st.pop('counter', None)
            choices.append(dict(step=st['steps'], config=config, gain=round(float(gain), 3),
                                values={f: round(v[0], 3) for f, v in vals.items()}))
        st['memory_stops'] = LG.MEMORY_STOPS[0] - stops0
        finish_args = (task, kind, ctx, concepts, library, st, leader, order, phi, logE, extra, choices,
                       tension_log, say, teaching, t0, c0, mu)
        if answer_channel is None:                        # preserve the existing caller/record path exactly
            return self._finish(*finish_args)
        return self._finish(*finish_args, answer_channel=answer_channel)

    # ------------------------------------------------------------------ pieces of living
    @staticmethod
    def _n_data(task):
        return len(task.throws) if task.form == 'strengths' else len(task.data)

    def _world_rate(self):
        # Keep the required off-arm choice policy: its historical thinking-cost estimate is separate from the
        # corrected measured rates. One Field learns and chooses using the total world cost.
        rates = self.field.rates if ONE_FIELD else self.field.off_choice_rates
        return float(np.mean(rates[-20:])) if rates else 0.1

    def _max_level(self, task):
        """No ceiling (2026-09-28, the author: "sera must not get stuck; if it's bad it must find the correct one"): after
        the stiff spring's 3,432 steps at the top level, thinking bigger is always there - each level a larger space
        of its own expressions, so an idea its language can say is reached in time (a larger level costs more)."""
        return math.inf

    def _search(self, task, *args, **kwargs):
        if self.proposer is not None and self.proposer.enabled:
            return self.proposer.search(task, *args, **kwargs)
        if self.proposer is not None:
            start = time.perf_counter()
            result = LG.search(*args, **kwargs)
            self.proposer.stats['search'] += time.perf_counter()-start
            self.proposer.stats['candidates'] += len(result)
            return result
        return LG.search(*args, **kwargs)

    def _generate(self, task, level, concepts):
        if task.form == 'strengths':
            return self._parts_physics(task, level, concepts)
        size = exact_size(level)
        nums = task.numbers() if hasattr(task, 'numbers') else ()
        if self.proposer is not None and self.proposer.enabled:
            preferred = self.proposer.preferred(task, concepts, nums)
            if preferred:
                return preferred[:MAX_HYPS]
        found = self._search(task, task.inputs, task.out, task.probes(), size, concepts, lambda_size=lambda_size(level),
                          constants=nums, values=True, work=LG.MAX_WORK * 2 ** level,   # bigger and harder: a size
                          if_part=if_part(level), sees=self._sees() and seeing_size(level))   # cut short is finished
                                                                                              # before a bigger one
        E = (task.evidence_values(found, concepts) if hasattr(task, 'evidence_values')   # its search has the values
             else task.evidence([e for e, _, _ in found], concepts))
        found = [e for e, _, _ in found]
        found.sort(key=lambda e: -E.get(e, -math.inf))  # the ones that fit first; then the nearest misses
        return found[:MAX_HYPS]

    def _doubt_after(self, task, concepts, library, mu, extra, hyps, kind, ctx):
        """Its doubt about its leading thought after acting (-log Phi of the leader), recomputed."""
        if task.form == 'strengths':
            single = task.evidence([(p,) for p in hyps], concepts, library, mu)
            laws = self._laws(task, hyps, single, self._level, self._footholds) + [k for k in extra]
            logE = task.evidence(laws, concepts, library, mu)
        else:
            laws = list(dict.fromkeys(hyps + list(extra)))
            logE = task.evidence(laws, concepts)
        if not logE:
            return S_MISS
        H = list(logE)
        _, _, _, phi, _ = self.field.layers(kind, ctx, {h: self._hparts(h, task.form) for h in H}, logE,
                                            {h: self._bits(h, task.form, concepts) for h in H})
        return -max(phi.values())

    def _scrutiny_begin(self, task, leader, remaining=None):
        if not CR.on('judge_scrutiny'):
            return
        policy = getattr(self.field, 'judge_scrutiny', None)
        if policy is None:
            policy = self.field.judge_scrutiny = TS.JudgeScrutiny()
        probability, calibration = None, ()
        # _u_predict has already read the candidate. Reuse that pre-verdict read;
        # do not ask the Field a second time or train on the pending result.
        x = getattr(self, '_u_predictions', {}).get((kind_of(task), leader))
        inner = getattr(self.field, 'inner', None)
        if x is not None and inner is not None and getattr(self, '_u_on', lambda _: False)('inner_judge'):
            probability = inner.probability(kind_of(task), x)
            calibration = inner.curves.get(kind_of(task), ())
        record = policy.begin(task, probability, calibration)
        if remaining is not None:
            record['budget'] = min(record['budget'], remaining)
        task._scrutiny_prepared = True

    @staticmethod
    def _scrutiny_record(task, leader, st):
        if CR.on('judge_scrutiny') and hasattr(task, '_scrutiny_last'):
            st.setdefault('scrutiny', []).append(dict(task._scrutiny_last, candidate=repr(leader)))

    def _prove(self, task, leader, concepts, library, st, speak):
        st['tested'].add((leader, self._n_data(task)))
        self._observe_ring(task, 'attempted', leader, step=st['steps'])
        if task.form == 'strengths':
            if ONE_FIELD:
                st.setdefault('support', {})
            tries = ([task.claim_terms(leader, concepts, library, ramp=True)] if TS.RAMP else []) + \
                [task.claim_terms(leader, concepts, library)]   # Decision 16: its formula first, then the curve
            said, fam = set(), None
            scrutiny_left = TS.SCRUTINY_THROWS
            for terms in tries:
                f, credit = terms if terms is not None else (None, None)
                if f is None or f in said or truth.functional_prior(f) == -math.inf:
                    continue
                said.add(f)
                fam = f
                if hasattr(self, '_u_predict'):
                    self._u_predict(task, leader)
                self._scrutiny_begin(task, leader, scrutiny_left)
                ok, cert, why = task.verify(fam)
                self._scrutiny_record(task, fam, st)
                if CR.on('judge_scrutiny'):
                    scrutiny_left -= task._scrutiny_last['used']
                if hasattr(self, '_u_verdict'):
                    self._u_verdict(task, leader, bool(ok), 'proof')
                self._observe_ring(task, 'judge_result', leader, step=st['steps'], accepted=bool(ok),
                                   family=fam, representation=credit, reason=why,
                                   band=getattr(cert, 'band', None), eps=getattr(cert, 'eps', None))
                self._observe_report(st)
                if ONE_FIELD and (ok or (cert is not None and cert.band is not None and np.isfinite(cert.band)
                                        and not (why and 'something else is here' in why))):
                    self._record_support(task, leader, fam, credit, concepts, st)
                if ok:
                    st.setdefault('adequate', set()).add(leader)
                    st['proven'] = dict(key=(leader, self._n_data(task)), law=leader, family=fam, cert=cert,
                                        n=len(task.throws), credit=credit,   # what the proof certifies of each part
                                        fit=task.ledger([fam]).mle(fam))    # keep the fit on those same throws
                    st['judge_short'], st['judge_where'] = 0.0, None   # the judge is convinced: nothing left to show
                    speak('proven', f'The judge accepts: {grammar.name(fam)} up to {cert.eps:g} where I looked.')
                    return True
                if any(p == 'formula' for _, p in credit) and len(said) < len(tries):
                    speak('refused', f'The judge does not accept {grammar.name(fam)} as my formula: {why}. I say it as '
                                     f'a curve.')                     # the ramp's refusal stays visible (S11)
            if fam is None:
                return False
            if why and 'something else is here' in why:     # a force its law misses: a counterexample; a band not yet
                st['misfit'], st['judge_short'] = True, S_MISS  # narrow enough is not one (S06 F1, reviewer)
                st['counter'] = ('misfit', leader)
            elif why == 'scrutiny: the band widened':
                st['judge_short'] = max(st.get('judge_short', 0.), 1.)
                st['judge_where'] = dict(truth.LAST_WHERE) or None
                st['shown'] = 0
            elif cert is not None and cert.band is not None and np.isfinite(cert.band):
                st.setdefault('adequate', set()).add(leader)   # the data support it; the band is not yet narrow
                st['judge_short'] = BAND_NATS * max(math.log(cert.band / cert.eps), 0.0)
                st['judge_where'] = dict(truth.LAST_WHERE) or None     # where the judge is least sure (revision 7)
                st['shown'] = 0                                        # nothing shown there yet
            else:
                st['judge_short'] = 5.0
            speak('refused', f'The judge does not accept {grammar.name(fam)}: {why}.')
            return False
        n = len([k for k in concepts if k != '_sig'])
        if hasattr(self, '_u_predict'):
            self._u_predict(task, leader)
        self._scrutiny_begin(task, leader)
        ok, n_audit, fail = task.verify(leader, concepts, LG.bits(leader, [0] * n), np.random.default_rng(
            [self.seed, 5, self.field.tasks, st['steps']]))
        self._scrutiny_record(task, leader, st)
        if hasattr(self, '_u_verdict'):
            self._u_verdict(task, leader, bool(ok), 'proof')
        self._observe_ring(task, 'judge_result', leader, step=st['steps'], accepted=bool(ok),
                           reason=None if ok else 'input', audit=n_audit)
        self._observe_report(st)
        if ok:
            st['proven'] = dict(key=(leader, self._n_data(task)), law=leader, audit=n_audit,
                                checked=(self._n_data(task), getattr(self._ideas(), 'rev', 0)))
            speak('proven', f'My audit passes {LG.show(leader, self.field.names())} on {n_audit} '
                            f'{getattr(task, "audit_words", "fresh inputs")}.')
            return True
        st['counter'] = ('input', leader, _digest(fail if fail is not None else ('examples', self._n_data(task))))
        #   the input it gets wrong, whole (S07 F2, reviewer: a cut key made two long ones one); a puzzle's own examples
        speak('refused', f'My audit found an input it gets wrong; I learn from it.')
        return False

    # ------------------------------------------------------------------ imagination: moves and its own methods
    def _moves_available(self, task, kind, leader, st, hyps, extra, concepts):
        """The innate moves of imagination it can make now (plan revision 7). Each move is a mechanism; which ones it
        chains, and when, is its own (sera.phi.MethodField). An idea it has already weighed here is not new (the stiff
        spring: recall brought back the same 4 ideas attention had let go, 3,432 times)."""
        have = set(hyps) | set(extra) | st['thought']
        out = set()
        if not ONE_FIELD and any(p['kind'] == kind and p['task'] != task.name and p['key'] not in have
                                 for p in self.field.possibilities):
            out.add('recall')
        if len([c for c in concepts if c != '_sig']) >= 1 and ('compose', leader) not in st['moved']:
            out.add('compose')
        if (task.form == 'exact' and len(task.inputs) == 1 and getattr(task, 'var', None)  # an ability it lacks: new
                and self._attempt('wish', task, concepts, st) not in st['moved']            # only when its abilities
                and not (leader is not None and task.consistent(leader, concepts))):       # changed since the last
            out.add('wish')
        if (task.form == 'exact' and len(task.inputs) == 1 and getattr(task, 'var', None)  # a small step, then the
                and task.var not in ('e', 'i', 'a')                                       # rest: again when it has
                and self._attempt('step', task, concepts, st) not in st['moved']            # grown or learned (not
                and not (leader is not None and task.consistent(leader, concepts))):       # an input a λ would bind:
            out.add('step')                                                                # S03, reviewer)
        if task.form == 'strengths' and leader:
            if ('keep', leader) not in st['moved']:
                out.add('keep')
            if any(p[1] == 'curve' or (p[1] == 'expr' and p[2][0] == 'tab') for p in leader) and \
                    ('question', leader) not in st['moved']:
                out.add('question')
            if len(leader) >= 2 and ('drop', leader) not in st['moved']:
                out.add('drop')
            if any(p[1] in ('concept', 'expr') for p in leader) and ('swap', leader) not in st['moved']:
                out.add('swap')
            if ('refine', leader) not in st['moved']:
                out.add('refine')
            if st.get('runner') and ('blend', leader) not in st['moved']:
                out.add('blend')
            if (st['misfit'] or st['judge_short'] > 0 or st['since_best'] >= 6):
                if ('closer', leader) not in st['moved']:
                    out.add('closer')
                if ('dimension', leader) not in st['moved']:
                    out.add('dimension')
        return out

    def _attend(self, task, extra, logE, concepts, library, mu):
        """Attention (2026-09-28, after the long run held 26,538 imagined ideas and slowed to 30 minutes a step):
        imagination stays unbounded, but what it holds in mind is what could still win - each imagined idea is weighed
        once, and it keeps those within ATTEND_NATS of its best idea, the best ATTEND_MAX of them; the rest are let go.
        Returns (kept, let go)."""
        if not extra:
            return 0, 0
        keys = list(extra)
        E = task.evidence(keys, concepts, library, mu) if task.form == 'strengths' else task.evidence(keys, concepts)
        best = max([v for v in E.values()] + [v for v in logE.values()] or [0.0])
        keep = sorted((k for k in keys if k in E and E[k] >= best - ATTEND_NATS), key=lambda k: -E[k])[:ATTEND_MAX]
        keep = set(keep)
        gone = [k for k in keys if k not in keep]
        for k in gone:
            del extra[k]
        return len(keep), len(gone)

    # --- the echo and the automatic trigger (2026-09-29 night; the author's HEB + e-prop, adapted) ---
    @staticmethod
    def _situation_things(task):
        """The things of a world's situation: what recurs in its examples' questions (for a story, its first sentence)
        - in at least half of them - the kind of situation, not one example's names (an idea laid into a name does not
        generalize, and blurred that name's own memories: ideas-7, 2026-09-29)."""
        counts, n = {}, 0
        for x, _ in task.data:
            for v in Sera._situation_things_of(x):
                counts[v] = counts.get(v, 0) + 1
            n += 1
        return sorted((v for v, c in counts.items() if c * 2 >= n and (c >= 2 or n == 1)), key=repr)

    @staticmethod
    def _situation_things_of(x):
        """The things of one example's question (for a story, its first sentence)."""
        q = x[0] if isinstance(x, (tuple, list)) and x and isinstance(x[0], (tuple, list)) else x
        seen, stack = set(), [q]
        while stack:
            v = stack.pop()
            if isinstance(v, (tuple, list)):
                stack.extend(v)
            elif isinstance(v, (int, str)) and not isinstance(v, bool):
                seen.add(v)
        return sorted(seen, key=repr)

    def _evoke(self, task, concepts, extra, speak, library=(), ctx=None):
        """The automatic trigger: the situation's things pressed on the Field; an idea it proved in situations like
        this rings back and is among its first thoughts - no recall, no list."""
        if not PH.FIELD_ECHO:
            return
        if ONE_FIELD:
            return self._ring_first(task, concepts, extra, speak, library, ctx)
        if not PH.FIELD_ECHO or task.form != 'exact' or len(task.inputs) != 1:
            return
        rang = self._ideas().evoked(self._situation_things(task),
                                    [('concept', c['id']) for c in self.field.concepts])[:3]
        var = next(iter(task.inputs))
        sig = concepts.get('_sig', {})
        names = self.field.names()
        heard = []
        for (_, cid), loud in rang:
            s = sig.get(cid)
            if s is None or not LG.fits(s, task.inputs[var], task.out):
                continue
            e = LG.node('c', LG.node('var', payload=var), payload=cid)
            if e not in extra:
                extra[e] = ('rang', cid)
                heard.append(f'{names.get(cid, cid)} ({loud:.2f})')
        if heard:
            speak('imagine', f"This rings in me: {', '.join(heard)}.")

    def _echo(self, task, signal, speak):
        """A result confirmed (or refuted) goes back through the Field: the ways of working and methods of imagining
        that took part (Field.echo), and the memories it rested on that hold what was confirmed (consolidated)."""
        n = self.field.echo(signal)
        m = 0
        if PH.FIELD_ECHO and signal > 0 and hasattr(task, 'perceive'):   # memories only for what is confirmed (a
            #                                                              refuted program may have read true ones)
            answers = [y for _, y in task.data]

            questions = [set(self._situation_things_of(x)) for x, _ in task.data]

            def holds(sent, cues):                        # a memory about an example's question (brought by its
                for q, y in zip(questions, answers):      # things) that holds its answer, in order (S05 F5, reviewer:
                    if not set(cues) <= q:                # a memory holding the answer's words was not enough)
                        continue
                    try:
                        if isinstance(y, tuple) and y:
                            if any(sent[i:i + len(y)] == y for i in range(len(sent) - len(y) + 1)):
                                return True
                        elif y in sent:
                            return True
                    except TypeError:
                        continue
                return False
            m = self._ideas().consolidate(signal, holds)
        elif PH.FIELD_ECHO and signal < 0:              # memories a refuted idea rested on are not weakened (they may
            self._ideas().forget_traces()               # be true) but are spent: not credited later (S06 C9, reviewer)
        if (n or m) and signal > 0:
            speak('imagine', f'It rings through the Field: {n} ways of working and imagining that led here'
                             + (f', and {m} memories it rested on,' if m else '') + ' are strengthened.')
        elif n:
            speak('imagine', f'The judge refuted it: the {n} ways of working and imagining that led there are '
                             f'weakened a little.')

    # ------------------------------------------------------------------ One Field, parts 2 and 4 (plan 3.4, review 12)
    @staticmethod
    def _cues(ctx):
        """What a rail's situation is to it (review 12 F7): its first perceived context as cues - the four
        correlations in half units, the size of the leftover motion in whole units of log10, how far and how fast
        things went in whole units of log2. A registered crutch (rail_cues); the kind of world is no cue."""
        if ctx is None or not CR.on('rail_cues'):
            return []
        out = []
        for i, c in enumerate(ctx):
            c = float(c)
            if not math.isfinite(c):
                continue
            b = round(2.0 * c) / 2.0 if i < 4 else float(round(c)) if i == 4 else float(round(math.log2(max(c, 0.125))))
            out.append(('sense', 'strengths', i, b + 0.0))
        return out

    def _things(self, task, ctx):
        """The things of a world's situation that ideas are laid into and rung from: a rail's cues; the recurring
        things of a one-input world's examples (its other forms: none yet)."""
        if task.form == 'strengths':
            return self._cues(ctx)
        if task.form == 'exact' and len(task.inputs) == 1:
            return self._situation_things(task)
        return []

    @staticmethod
    def _body_identity(body, representatives):
        """Normalize named duplicates inside executable bodies, leaving literal/table payloads intact."""
        return (body[0], representatives.get(body[1], body[1]) if body[0] == 'c' else body[1],
                *(Sera._body_identity(child, representatives) for child in body[2:]))

    def _canonical_identity(self, key, deadline=None):
        """First invented body wins, consistently for raw bodies and explicit concept applications."""
        stamp = (len(self.field.concepts), getattr(self.field, 'next_id', None))
        if getattr(self, '_body_count', None) != stamp:
            bodies, representatives, members, body_keys = {}, {}, {}, {}
            for c in self.field.concepts:
                if deadline is not None and time.time() >= deadline:
                    return None
                body = self._body_identity(c['body'], representatives)
                body_keys[c['id']] = body
                representatives[c['id']] = bodies.setdefault(body, c['id'])
                members.setdefault(body, []).append(c['id'])
            body_members = {}
            for c in self.field.concepts:
                if deadline is not None and time.time() >= deadline:
                    return None
                body_members[c['id']] = members[body_keys[c['id']]]
            self._body_count = stamp
            self._body_names, self._representatives = bodies, representatives
            self._body_members = body_members
        bodies, reps = self._body_names, self._representatives
        kind, ref = key
        if kind == 'concept':
            return (kind, reps.get(ref, ref))
        if kind != 'idea' or not isinstance(ref, tuple):
            return key
        if not ref or isinstance(ref[0], tuple):           # physics law
            parts = []
            for ch, form, value in ref:
                body = self._body_identity(_subst(value, 's', '_'), reps) if form == 'expr' else None
                if form == 'concept':
                    value = reps.get(value, value)
                elif body in bodies:
                    form, value = 'concept', bodies[body]
                elif form == 'expr':
                    value = self._body_identity(value, reps)
                parts.append((ch, form, value))
            return ('idea', tuple(sorted(parts, key=repr)))
        ref = self._body_identity(ref, reps)
        if ref[0] == 'c' and len(ref) == 3 and ref[2] == LG.node('var', payload='_'):
            return ('concept', reps.get(ref[1], ref[1]))
        return ('concept', bodies[ref]) if ref in bodies else ('idea', ref)

    def _sync_aliases(self, deadline=None):
        """Repair saved raw/concept names once on load and whenever invention changes the mapping."""
        stamp = (len(self.field.concepts), getattr(self.field, 'next_id', None))
        if not ONE_FIELD or getattr(self, '_aliases_at', None) == stamp:
            return True
        ideas = self._ideas()
        if self._canonical_identity(('idea', ()), deadline=deadline) is None:
            return False
        mapping = {}
        for cid, rep in self._representatives.items():
            if deadline is not None and time.time() >= deadline:
                return False
            if cid != rep:
                mapping[('concept', cid)] = ('concept', rep)
        for key in ideas.iter_identities(('idea', 'concept'), deadline=deadline):
            if deadline is not None and time.time() >= deadline:
                return False
            canonical = self._canonical_identity(key, deadline=deadline)
            if canonical is None:
                return False
            if canonical != key:
                mapping[key] = canonical
        if deadline is not None and time.time() >= deadline:
            return False
        if not ideas.redirect(mapping, deadline=deadline):
            return False
        self._aliases_at = stamp
        return True

    def _idea_key(self, task, h):
        """An idea's identity in the Field: a law with its parts in order (the empty law too: no force); a program
        with its input renamed '_' - a concept used as it is, or a program that became a concept, is that concept
        (one identity per idea: S15 F1); None for what has none."""
        if h is None:
            return None
        self._sync_aliases()
        if task.form == 'strengths':
            return self._canonical_identity(('idea', h))
        if len(task.inputs) != 1:
            return None
        var = next(iter(task.inputs))
        body = _subst(h, var, '_')
        return self._canonical_identity(('idea', body))

    def _proof_amounts(self, task, law, kept, new, credited):
        """What a credited proof lays in (S15 F1, the one writer): +1 to the proven idea - physics: the kept law with
        its curves as the tables it made of them; a program: the concept it became, or that it is - and +0.5 to each
        concept inside it (as _bind_proven did). Nothing when not credited."""
        if not credited:
            return {}
        if task.form == 'strengths':
            arguments = {c['id']: c['argument_input'] for c in self.field.concepts if 'argument_input' in c}
            # A composed table already evaluates its coordinate: apply it to the original input only once.
            k = self._idea_key(task, tuple((arguments.get(new[i], p[0]), 'concept', new[i]) if i in new else p
                                          for i, p in enumerate(kept)))
            return {} if k is None else {k: 1.0}
        self._sync_aliases()
        k = self._canonical_identity(('concept', new['all'])) if 'all' in new else self._idea_key(task, law)
        out = {} if k is None else {k: 1.0}
        for p in LG.parts(law):
            if p[0] == 'concept':
                inner = self._canonical_identity(('concept', p[1]))
                if inner != k:
                    out.setdefault(inner, 0.5)
        return out

    @staticmethod
    def _deps_ok(cid, concepts, memo, deadline=None):
        """A concept and every concept its body uses, all the way down, are in this world's table (S15 F3)."""
        if deadline is not None and time.time() >= deadline:
            return False
        if cid in memo:
            return memo[cid]
        memo[cid] = False                                  # a cycle is not an ability
        entry = concepts.get(cid)
        ok = entry is not None and all(Sera._deps_ok(p[1], concepts, memo, deadline)
                                       for p in LG.parts(entry[0]) if p[0] == 'concept')
        memo[cid] = ok
        return ok

    def _from_key(self, task, key, concepts, library, memo=None, judge=True, deadline=None):
        """The idea an identity names, made a thought of this world - or None when it does not fit here (review 12 F6,
        S15 F3-F5): its type; its concepts present and not hidden, all the way down; a law as SERA forms them (at most
        MAX_PARTS parts, one per input, at most one free curve) - and, with `judge`, one the judge can be told."""
        if deadline is not None and time.time() >= deadline:
            return None
        kind, ref = key
        memo = {} if memo is None else memo
        if task.form == 'strengths':
            if kind != 'idea' or not isinstance(ref, tuple) or (ref and isinstance(ref[0], str)):
                return None
            bases = [TS.base(p[0]) for p in ref]
            if (len(ref) > MAX_PARTS or len(set(bases)) < len(bases) or sum(p[1] == 'curve' for p in ref) > 1
                    or any(p[1] == 'concept' and not self._deps_ok(p[2], concepts, memo, deadline) for p in ref)):
                return None
            if not judge:
                return ref
            terms = task.claim_terms(ref, concepts, library)
            if deadline is not None and time.time() >= deadline:
                return None
            return ref if terms is not None and truth.functional_prior(terms[0]) > -math.inf else None
        if task.form != 'exact' or len(task.inputs) != 1:
            return None
        var = next(iter(task.inputs))
        sig = concepts.get('_sig', {})
        if kind == 'concept':
            if self._canonical_identity(key, deadline=deadline) is None:
                return None
            for cid in self._body_members.get(ref, [ref]):
                if deadline is not None and time.time() >= deadline:
                    return None
                s = sig.get(cid)
                if s is not None and LG.fits(s, task.inputs[var], task.out) and self._deps_ok(cid, concepts, memo, deadline):
                    return LG.node('c', LG.node('var', payload=var), payload=cid)
            return None
        if not isinstance(ref, tuple) or not ref or not isinstance(ref[0], str):
            return None
        if any(p[0] == 'concept' and not self._deps_ok(p[1], concepts, memo, deadline) for p in LG.parts(ref)):
            return None
        try:
            s = LG.infer(ref, concepts)
        except Exception:                                  # a body with no type here
            return None
        if s is None or not LG.fits(s, task.inputs[var], task.out):
            return None
        return _subst(ref, '_', var)

    def _ring_first(self, task, concepts, extra, speak, library, ctx):
        """The automatic trigger, for every world it can perceive (review 12): its things pressed on the Field, read
        against the Field's own identities of ideas - only those that fit here (eligibility first, then the loudest) -
        and the loudest few are among its first thoughts. No recall, no list."""
        deadline = LG.DEADLINE[0]
        observer = getattr(self, '_ring_observer', None)
        if observer is not None:
            observer['initial_cues'] = self._things(task, ctx)
        if not PH.FIELD_ECHO or time.time() >= deadline:
            return
        if not self._sync_aliases(deadline=deadline):
            return
        things = self._things(task, ctx)
        if not things:
            if observer is not None:
                observer['trigger_complete'] = True
            return
        ideas = self._ideas()
        cands, memo = [], {}
        for key in ideas.iter_identities(('concept', 'idea'), deadline=deadline):
            if time.time() >= deadline:
                return                                   # all-or-nothing cutoff, no partially selected thoughts
            h = self._from_key(task, key, concepts, library, memo, judge=False, deadline=deadline)
            if h is not None and h not in extra:
                cands.append((key, h))
        if not cands:
            if observer is not None:
                observer['trigger_complete'] = True
            return
        if observer is not None:
            observer['candidates'] = [dict(identity=k, identity_repr=repr(k), score=None, noise=None,
                                           threshold=None, above_noise=None) for k, _ in cands]
        def projected(scores, noise, threshold):
            observer['candidates'] = [dict(identity=k, identity_repr=repr(k), score=v, noise=noise,
                                           threshold=threshold, above_noise=v > threshold) for k, v in scores]
            observer['projection_complete'] = True

        loud = dict(ideas.evoked(things, [k for k, _ in cands], deadline=deadline,
                                observe=projected if observer is not None else None))
        if not loud or time.time() >= deadline:
            if observer is not None:
                observer['trigger_complete'] = time.time() < deadline
            return
        names = self.field.names()
        heard, seen = [], set()
        selected = []
        for key, h in sorted((c for c in cands if c[0] in loud), key=lambda c: (-loud[c[0]], repr(c[0]))):
            if time.time() >= deadline:
                return
            same = self._idea_key(task, h)                 # two names of one idea: one thought (S15 F1)
            if same in seen or (task.form == 'strengths'
                                and self._from_key(task, key, concepts, library, memo, deadline=deadline) is None):
                continue                                   # a law the judge cannot be told: not a thought here
            seen.add(same)
            selected.append((h, key))
            heard.append((names.get(key[1], key[1]) if key[0] == 'concept' else
                          LG.show(h, names) if task.form == 'exact' else repr(h)[:60]) + f' ({loud[key]:.2f})')
            if len(seen) >= RING_MOST:
                break
        if time.time() >= deadline:
            return
        if observer is not None:
            observer['trigger_complete'] = True
        for h, key in selected:
            extra[h] = ('rang', key)
            if observer is not None:
                item = dict(identity=key, identity_repr=repr(key), law=h, used=False, led=False)
                observer['selected'].append(item)
                self._ring_selected[h] = item
        if heard:
            speak('imagine', f"This rings in me: {', '.join(heard)}.")

    @staticmethod
    def _support_snapshot(task):
        return (len(task.throws), truth.digest(task.throws))

    def _record_support(self, task, law, family, credit, concepts, st):
        kept, _ = self._certified(law, credit, family, concepts)
        if kept is not None:
            snapshot = self._support_snapshot(task)
            st.setdefault('support', {})[(law, snapshot, family)] = kept

    def _lay_in_world(self, task, ctx, st, order, phi, proof, held):
        """What a world leaves in the Field (review 12 F2, F5): one amount per idea, laid into the world's things -
        a refuted idea -REFUTE_ECHO (the laws inside its counterexamples; a judge not yet sure refutes nothing); a
        credited proof its amounts (_proof_amounts); Phi's tentative beliefs exp(phi), only for ideas the data support
        - a program that fits the examples, a law the judge found adequate (its band only not yet narrow enough;
        S15 F2) - and were not refuted, the most of their sources, together at most TENTATIVE_MOST. Then the world
        counts as perceived."""
        if not PH.FIELD_ECHO:
            return
        self._sync_aliases()
        things = self._things(task, ctx)
        ideas = self._ideas()
        if things:
            amounts = {}
            for r in sorted(st.get('refuters', ()), key=repr):
                if isinstance(r, tuple) and len(r) >= 2 and r[0] in ('input', 'misfit', 'teacher'):
                    k = self._idea_key(task, r[1])
                    if k is not None:
                        amounts[k] = -REFUTE_ECHO
            for k, a in (proof or {}).items():
                if k is not None and k not in amounts:
                    amounts[k] = a
            skip = set(amounts)
            support = st.get('fitting') if task.form == 'exact' else st.get('adequate')
            if task.form == 'strengths' and 'support' not in st:
                # Compatibility for direct curve-writer callers (including the existing amplitude tests).
                # Live/proof states must supply evidence records; a bare adequate marker never supports a formula.
                support = ({law for law in support if all(p[1] == 'curve' for p in law)}
                           if support is not None and 'tested' not in st else None)
            if task.form == 'strengths' and 'support' in st:
                snapshot = self._support_snapshot(task)
                support = {law for (law, data, family), kept in st['support'].items()
                           if data == snapshot and kept == law}
                if st.get('unattributed') is not None:
                    support.discard(st['unattributed'])
            tent = {}
            for h in (order[:5] if support is not None else ()):   # no support known: no tentative belief
                k = self._idea_key(task, h)
                p = math.exp(phi[h]) if h in phi else 0.0
                if k is None or k in skip or p <= 0.02 or h not in support:
                    continue
                tent[k] = max(tent.get(k, 0.0), p)
            for h, a in held:
                k = self._idea_key(task, h)
                if k is not None and k not in skip:
                    tent[k] = max(tent.get(k, 0.0), a)
            total = sum(tent.values())
            for k, a in tent.items():
                amounts[k] = a * (TENTATIVE_MOST / total if total > TENTATIVE_MOST else 1.0)
            for k in sorted(amounts, key=repr):
                for t in things:
                    ideas.bind(t, k, amounts[k])
                observer = getattr(self, '_ring_observer', None)
                if observer is not None:
                    observer['writes'].append(dict(identity=k, identity_repr=repr(k), amount=amounts[k],
                                                   cues=things))
        if task.form == 'strengths':
            ideas.perceive_world(things)

    def _reliable(self, c, frame, tally):
        """Has idea c been right more often than not on this kind of question? On the old path, this talk's tally;
        with ONE_FIELD, the frame's own thing in the Field holds every idea's signed record, trusted above its noise
        (a frameless question: this talk's tally, never a global row; review 12 F3)."""
        if ONE_FIELD and CR.on('frame_identity') and frame:
            v, noise = self._ideas().signed(('frame', tuple(sorted(frame, key=repr))), ('right', c))
            return v > 0 and v > 2.0 * noise
        r, n = tally.get((c, frame), (0, 0))
        return 2 * r > n

    def _refute(self, task, key, st, speak, text):
        """A refutation found where it is found (S07 F3, reviewer: one found as a moment begins was echoed after that
        moment's new work, or lost): echoed at once through what took part before it, once per counterexample."""
        speak('refused', text)
        if key in st.setdefault('refuters', set()):
            return
        st['refuters'].add(key)
        self._observe_ring(task, 'refuted', key[1], step=st['steps'], reason=key[0], counter=key, explanation=text)
        self._echo(task, -REFUTE_ECHO, speak)

    def course_reliable(self, task):
        """The existing talk reliability test, for a perceived input/output kind; no task name or target."""
        if not CR.on('course_told_wrong'):
            return True
        kind = kind_of(task)
        c, frame = ('answer-kind', kind), frozenset((kind,))
        tally = getattr(self.field, 'course_tally', {})
        if ONE_FIELD and CR.on('frame_identity'):
            ideas = self._ideas()
            if ('frame', tuple(sorted(frame))) not in ideas._row or ('right', c) not in ideas._row:
                return True                              # no verdict evidence yet
        elif (c, frame) not in tally:
            return True
        return self._reliable(c, frame, tally)

    def course_verdict(self, task, law, right, source, reliability=False):
        """A verdict without an answer: use Field.answer's standing path and the existing signed/tally path.

        Only the course calls this. Book checks and teacher words differ only in recorded provenance; neither
        supplies a program, example, worked step, or word. The caller decides when corrections may be shown.
        """
        F = self.field
        kind = kind_of(task)
        qid = F.ask(task.name, 'check', 'Is my answer right?', key=law, kind=kind)
        F.answer(qid, 'right' if right else 'wrong')
        F.answers[qid]['source'] = source
        if not right:
            self._echo(task, -REFUTE_ECHO, lambda *a, **k: None)
            key = self._idea_key(task, law)
            if key is not None:
                for t in self._things(task, task.context()):
                    self._ideas().bind(t, key, -REFUTE_ECHO)
        if reliability:
            c, frame = ('answer-kind', kind), frozenset((kind,))
            if ONE_FIELD and CR.on('frame_identity'):
                self._ideas().bind(('frame', tuple(sorted(frame))), ('right', c), 1.0 if right else -1.0)
            else:
                tally = F.__dict__.setdefault('course_tally', {})
                r = tally.setdefault((c, frame), [0, 0])
                r[0] += int(right)
                r[1] += 1

    def _teacher_says_wrong(self, task, law, concepts, st):
        """The teacher's answer to a proof as it is made (taught worlds only): None when the teacher agrees, else what
        refutes it - an example it gets wrong, shown to it (a program), or the teacher's word that the law is not the
        world's (physics: the true law is the teacher's). Trying it on the teacher's examples leaves no trace in its
        memory (only a shown example is seen)."""
        if task.form == 'strengths':
            p = st['proven']
            g = task.grade(p['cert'], True, n_throws=p.get('n'))
            return None if g.get('verdict') == 'proven right' else ('teacher', law, self._n_data(task))
        if not hasattr(task, 'teacher_check'):
            return None
        ideas = self._ideas()
        came = dict(getattr(ideas, '_came', {}))
        try:
            shown = task.teacher_check(law, concepts, seed=self.seed)
        finally:
            ideas._came = came
        return None if shown is None else ('input', law, _digest(shown))

    @staticmethod
    def _credited(teaching, g, rec, say):
        """What a proof lets it keep (S06 F8, reviewer). Alone, its own proof - its audit, its judge - is what it believes:
        the observer's hidden grade never reaches its Field. Taught, the teacher's word decides, as in physics (teacher,
        then fail and credit): a proof the teacher says is wrong makes no concept, no meaning for the teacher's words and
        no idea that rings - it is a fail it learns from."""
        if not teaching or g.get('verdict') == 'proven right':
            return True
        rec['teacher_says'] = 'wrong'
        say.append(dict(step=rec['steps'], what='refused', text='The teacher shows me my proof is wrong here: I do not '
                                                                 'keep it.'))
        return False

    def _situation_ideas(self):
        """Its proven ideas that take a situation (a list of sentences): what a question in a talk may call for."""
        sig = self.field.concept_table().get('_sig', {})
        proven = self.field.proven_ideas()
        return [c['id'] for c in self.field.concepts
                if c['id'] in proven and tuple(sig.get(c['id'], ('', '')))[0] == 'list(list)']

    def reply(self, g, q=None):
        """Its reply to a question in a situation (the question first, then what it was told, what came to mind): the
        question pressed on its Field; the proven idea that rings loudest for it answers, in words - or it does not
        know (another idea's word is not an answer to this question: S06 F5, reviewer). Nothing but its Field chooses: the
        automatic trigger. Returns (the answer or None, the idea or None, [(idea, loudness)])."""
        fits = self._situation_ideas()
        q = g[0] if q is None else q
        rang = [(k[1], v) for k, v in self._ideas().evoked(q, [('concept', c) for c in fits])]
        if not rang:
            return None, None, []
        cid = rang[0][0]
        v = LG.safe(LG.node('c', LG.node('var', payload='g'), payload=cid), {'g': g}, self.field.concept_table())
        return (v if TS.is_words(v) else None), cid, rang

    def converse(self, task, teaching=True, on_say=None):
        """A talk (sera.tasks.Talk), as it comes: each story read, then its question replied to (Sera.reply) - a later
        story cannot answer an earlier question (S07 F7, reviewer: all stories were read first). Taught, the teacher then
        says the answer - or that nobody said - and a wrong reply is corrected at once (Sera._correct); alone, it
        replies and nothing is learned from the grade. Returns the record: right, and how often it answered at all
        (coverage), per kind."""
        F = self.field
        ideas = self._ideas()
        concepts = F.concept_table()
        fits = self._situation_ideas()
        names = F.names()
        rows, learned = [], []
        tally, heard = {}, {}                              # this talk's own counts, like traces: (idea, kind of
        t0 = time.time()                                   # question) -> [right, asked]; kept for the talk only
        for x, y, kind in task.items:
            for s in task.sentences(x):                    # its story, read as a lesson's is
                ideas.read(s, task.name)
            task.mind = ideas if ideas.read_n else None
            g = task.perceive(x)
            if hasattr(self, '_u_talk_tick'):
                self._u_talk_tick(on_say)
            got, cid, rang = self.reply(g, x[0])
            row = dict(kind=kind, question=TS.text(x[0]), said=None if got is None else TS.text(got),
                       idea=names.get(cid, cid) if cid is not None else None, right=got == y,
                       rang=[(names.get(c, c), round(v, 3)) for c, v in rang[:3]])
            u_inner = hasattr(self, '_u_on') and self._u_on('inner_judge')
            if u_inner:
                row['response'] = (TS.text(got) if got is not None else
                                   'not-yet' if self._u_on('taught_not_yet') else
                                   CR.REGISTRY['abstain_bar']['response'] if self._u_bar_on() else None)
            if hasattr(self, '_u_talk_record'):
                self._u_talk_record(g, x[0], got, row)
            # Observer annotation only: no target or digest enters reply, retrieval, or learning.
            row['observer_digest'] = _digest((tuple(TS.text(sentence) for sentence in x),
                                               ('absent',) if y is None else ('target', TS.text(y)), kind))
            if teaching:                                   # the teacher's answer, and at once what it teaches
                row['teacher'] = None if y is None else TS.text(y)
                told = {w for s in x[1:] for w in s}       # the question's own words: not what its story tells of
                words = sorted({t for t in self._situation_things_of(x) if t not in told}, key=repr)
                for t in words:                            # the kind of question: its own words that recur in the
                    heard[t] = heard.get(t, 0) + 1         # talk (a name asked about once is not a kind)
                frame = frozenset(t for t in words if heard[t] >= 2)
                said = {}
                for c in fits:
                    v = LG.safe(LG.node('c', LG.node('var', payload='g'), payload=c), {'g': g}, concepts)
                    said[c] = v if TS.is_words(v) else None
                    if u_inner:
                        continue
                    if ONE_FIELD and CR.on('frame_identity') and frame:   # the record in the Field (S12 F3) -
                        pass                                   # no tally beside it (S15 F6)
                    else:
                        k = tally.setdefault((c, frame), [0, 0])   # right: the teacher's answer, or silence where
                        k[0] += int(said[c] == y)                  # nobody said
                        k[1] += 1
                    if ONE_FIELD and CR.on('frame_identity') and frame:
                        ideas.bind(('frame', tuple(sorted(frame, key=repr))), ('right', c),
                                   1.0 if said[c] == y else -1.0)
                if u_inner:
                    self._u_talk_correct(g, x[0], y, got, cid, said)
                learned += self._correct(words, frame, y, got, cid, rang, fits, said, tally)
            if hasattr(self, '_u_talk_end_turn'):
                self._u_talk_end_turn(x[0])
            rows.append(row)
            if on_say is not None:
                on_say(row)
        by = {}
        for r in rows:
            k = by.setdefault(r['kind'], [0, 0, 0])
            k[0] += int(r['right'])
            k[1] += int(r['said'] is not None)
            k[2] += 1
        return dict(task=task.name, teaching=teaching, n=len(rows), right=sum(r['right'] for r in rows),
                    answered=sum(r['said'] is not None for r in rows),
                    by_kind={k: f'{a}/{c} (answered {b})' for k, (a, b, c) in sorted(by.items())},
                    learned=[(names.get(c, c), w, round(v, 2)) for c, w, v in learned], rows=rows,
                    wall=round(time.time() - t0, 1))

    def _correct(self, words, frame, y, got, cid, rang, fits, said, tally):
        """A reply, and the teacher's answer or "nobody said" (fail and credit, as in its lessons; S07 F5-F6, reviewer: a
        batch rule could not correct a wrong association nor tell "what is ladder" from "what is the first word").
        When the idea that rang was wrong (an answer where nobody said is wrong too) or silent, or a wrong idea rang
        nearly as loud as a right one (within TALK_RATE: a tie is luck, not knowing), the question's own words move
        away from the wrong ones, and toward the idea of its own that gave the teacher's answer (the loudest among
        them) - only when that idea has been right more often than not on this kind of question in this talk (its own
        words that recur; 2026-10-01: the general SERA, with no 'where' idea, was pulled to a shortcut that was right
        now and then, and answered about people nobody had told it of; a shortcut is not to be trusted for being right
        once - and counted per word, 'what' could not be learned for 'what is ladder', as 'what is the first word'
        shares it: the kind of question, not the word, says how reliable an idea is). A reply right by a clear
        margin changes nothing: talks that agree with what it holds do not pile up. The delta rule with a margin."""
        if not words or (y is None and not CR.on('nobody_said')):   # the crutch off: where nobody said, nothing
            return []                                                 # is learned (before d85f30a)
        loud = dict(rang)
        good = [c for c in fits if said.get(c) == y] if y is not None else []
        top = rang[0][1] if rang else 0.0
        right = got == y
        close = [c for c, v in rang if c != cid and said.get(c) != y and v >= top - TALK_RATE]
        if right and not close:
            return []
        away = ([] if right or cid is None else [cid]) + close
        ideas = self._ideas()
        out = []
        if good:
            best = max(good, key=lambda c: (loud.get(c, 0.0), -fits.index(c)))
            u_judge = hasattr(self, '_u_on') and self._u_on('inner_judge')
            trusted = self._reliable(best, frame, tally) if u_judge else (
                not CR.on('talk_tally') or self._reliable(best, frame, tally))
            if trusted:
                for t in words:
                    ideas.bind(t, ('concept', best), TALK_RATE)
                    out.append((best, TS.text(t) if isinstance(t, int) else str(t), TALK_RATE))
        for c in away:
            for t in words:
                ideas.bind(t, ('concept', c), -TALK_RATE)
                out.append((c, TS.text(t) if isinstance(t, int) else str(t), -TALK_RATE))
        return out

    def _bind_proven(self, task, law, new):
        """The proven idea (and the ideas inside it, more softly) laid into the state of the situation's things: when a
        situation like this is perceived again, it rings back by itself."""
        if not PH.FIELD_ECHO:
            return
        cid = new.get('all') or (law[1] if law[0] == 'c' else None)
        inner = sorted({p[1] for p in LG.parts(law) if p[0] == 'concept' and p[1] != cid}, key=repr)
        ideas = self._ideas()
        for t in self._situation_things(task):
            if cid is not None:
                ideas.bind(t, ('concept', cid), 1.0)
            for p in inner:
                ideas.bind(t, ('concept', p), 0.5)

    def _attempt(self, move, task, concepts, st):
        """What a wish or a step is made with: its abilities, the ways of seeing it has grown, the examples it has (and,
        for a step, its level). Made again only when one of these has changed (S04 R3, reviewer: a wish after it grew its
        seeing, or after new examples, is a new search, not the same one)."""
        grown = tuple(sorted(getattr(self.field, 'grown', None) or ()))
        key = (move, len(concepts), grown, len(task.data))
        return key + (st['level'],) if move == 'step' else key

    def _imagine(self, method, task, kind, leader, concepts, library, mu, st, hyps, extra, speak, known=()):
        """Run a method: its moves in a chain, each on the best new thought of the move before (or on its leading idea).
        Returns {thought: (origin, method)} - every new thought, unbounded."""
        focus = leader if leader is not None else ()
        out = {}
        for move in self.field.methods.expand(method):
            if move in ('wish', 'step') and self._attempt(move, task, concepts, st) in st['moved']:
                continue                                 # made already with the same abilities: the same search with
            #                                              less time finds nothing new (2026-09-29: "wish then compose
            #                                              then wish" wished again and again, 0.75 of the time left each
            #                                              time - 564 of a lesson's 600 s - and a step never came)
            st['moved'].add((move, focus))
            new = self._move(move, task, kind, focus, concepts, library, mu, st, hyps, extra, speak)
            new = [(law, origin) for law, origin in new if law not in out and law not in extra and law not in known]
            for law, origin in new:
                out[law] = (origin, method)
            if not new:
                continue
            if task.form == 'strengths':
                E = task.evidence([law for law, _ in new], concepts, library, mu)
                if E:
                    focus = max(E, key=E.get)
            else:
                focus = new[0][0]
        return out

    def _move(self, move, task, kind, focus, concepts, library, mu, st, hyps, extra, speak):
        """One move of imagination on a thought. Returns [(new thought, origin)]."""
        have = set(hyps) | set(extra)
        sig = concepts.get('_sig', {})
        if move == 'recall':                         # what it set aside in other tasks of this kind
            if ONE_FIELD:                            # no store to recall from (S15 F6)
                return []
            return [(p['key'], ('recalled', p['task'])) for p in self.field.possibilities
                    if p['kind'] == kind and p['task'] != task.name and p['key'] not in have]
        if move == 'compose':                        # two of its concepts together (across inputs; one inside another)
            out = []
            if task.form == 'strengths':
                ids = [c for c, sg in sig.items() if tuple(sg) == ('num', 'num')]
                chans = self._channels()
                for i in ids:
                    for j in ids:
                        for c1, c2 in itertools.combinations(chans, 2):
                            if TS.base(c1) != TS.base(c2):
                                key = tuple(sorted(((c1, 'concept', i), (c2, 'concept', j)), key=repr))
                                if key not in have:
                                    out.append((key, ('composed', (i, j))))
            else:
                var = next(iter(task.inputs))
                tin, tout = task.inputs[var], task.out
                between = LG.universe([tin, tout])         # the type one concept hands the other
                for i, s1 in sig.items():
                    for j, s2 in sig.items():
                        if any(LG.fits(s2, tin, mid) and LG.fits(s1, mid, tout) for mid in between):
                            e = LG.node('c', LG.node('c', LG.node('var', payload=var), payload=j), payload=i)
                            if e not in have and task.consistent(e, concepts):
                                out.append((e, ('composed', (i, j))))
            return out
        if move == 'keep':                           # the snowball: keep what of the thought was right, build on it
            self._keep_footholds(task, focus, concepts, library, mu, st, speak)
            held = tuple(sorted(st['footholds'], key=repr))
            if not held:
                return []
            laws = self._laws(task, hyps, {}, 0, st['footholds'])
            return [(law, ('kept', repr(held)[:120])) for law in laws if set(held) <= set(law) and law not in have]
        if move in ('closer', 'dimension'):          # a new sense: look closer, or a new dimension of its own
            look = self._where_to_look(task, focus, concepts, mu, library,
                                       what=('lens',) if move == 'closer' else ('dim',))
            if look is None:
                return []
            name, nats, law = look
            self._task_senses.append(name)
            if not any(x['name'] == name for x in self.field.senses):
                self.field.senses.append(dict(name=name, born=task.name, at=self.field.tasks, uses=0))
            st['regen'] = True
            if grammar.is_dim(name):
                speak('imagine', f'I make a new sense, {grammar.describe_input(name)}, and think along it too '
                                 f'({nats:.0f} nats better).', sense=name)
            else:
                lo, hi = grammar.input_range(name)
                speak('imagine', f'My idea misses most near {TS.base(name)} {0.5 * (lo + hi):g}: I look '
                                 f'{2 ** grammar.lens(name)[1]}x closer there, and draw finer ({nats:.0f} nats better).',
                      sense=name)
            return [(law, (move, name))]
        if move == 'question':                       # what is this curve, really? a formula of its own language
            return self._question(task, focus, concepts, mu, speak)
        if move == 'wish':                           # the ability it lacks: it builds it, and uses it
            st['moved'].add(self._attempt('wish', task, concepts, st))
            return self._wish(task, concepts, speak, have)
        if move == 'step':                           # the smallest good step, then the rest
            key = self._attempt('step', task, concepts, st)
            st['moved'].add(key)
            out = self._step(task, concepts, speak, have, st)
            if not out and self._step_cut and self._open_steps:   # its time ran out with steps not yet tried: not
                st['moved'].discard(key)             # "tried already" - it may take them up again, those first (S10,
            return out                               # reviewer: a chained step had what was left, and its key was spent)
        if task.form != 'strengths' or not focus:
            return []
        chans = self._channels()
        out = []
        if move == 'drop':                           # simpler: the idea without one of its parts
            out = [(tuple(q for q in focus if q != p), ('dropped', repr(p)[:60])) for p in focus]
        elif move == 'swap':                         # analogy: a part moved to another input
            used = {TS.base(p[0]) for p in focus}
            for p in focus:
                if p[1] not in ('concept', 'expr'):
                    continue
                for ch in chans:
                    if TS.base(ch) not in used:
                        out.append((tuple(sorted([q for q in focus if q != p] + [(ch, p[1], p[2])], key=repr)),
                                    ('swapped', f'{p[0]}->{ch}')))
        elif move == 'refine':                       # draw finer: a curve with more knots, a drawn part set free
            for p in focus:
                rest = [q for q in focus if q != p]
                if sum(q[1] == 'curve' for q in rest):
                    continue
                if p[1] == 'curve' and int(p[2]) < 33:
                    out.append((tuple(sorted(rest + [(p[0], 'curve', 33 if int(p[2]) >= 17 else 17)], key=repr)),
                                ('refined', p[0])))
                elif p[1] != 'curve':
                    out.append((tuple(sorted(rest + [(p[0], 'curve', 17)], key=repr)), ('freed', p[0])))
        elif move == 'blend':                        # two ideas as one: its idea with the runner-up's other parts
            other = st.get('runner') or ()
            used = {TS.base(p[0]) for p in focus}
            add = [q for q in other if TS.base(q[0]) not in used]
            law = tuple(sorted(list(focus) + add, key=repr))
            if add and len(law) <= MAX_PARTS and sum(q[1] == 'curve' for q in law) <= 1:
                out.append((law, ('blended', repr(other)[:60])))
        return [(law, o) for law, o in out if law and law not in have]

    # ------------------------------------------------------------------ building the abilities it needs
    def _wish(self, task, concepts, speak, have=()):
        """'If I could do this, the problem would be easy' (2026-09-28, the author: "sera builds that ability and uses it
        to tackle the problem; sera grows itself"). It looks at the problem in ways that make it a smaller one (its
        views), works out from the examples what the ability it lacks must do, builds that ability - by its own
        search, and by wishing again inside it - keeps it as a concept of its language, and uses it here. Returns
        [(the problem's answer through the new ability, origin)]. have: the ideas it holds already - an answer it has
        is no answer to the wish."""
        var = next(iter(task.inputs))
        tin, tout = task.inputs[var], task.out
        seen = task.perceive if hasattr(task, 'perceive') else (lambda x: x)   # the situation as it takes it in
        pairs = [(LG.freeze(seen(x)), LG.freeze(y)) for x, y in task.data]
        xs = [LG.freeze(seen(x)) for x in getattr(task, '_probe_inputs', [x for x, _ in task.data])]
        now = time.time()
        until = now + min(max(LG.DEADLINE[0] - now, 0.0) * WISH_SHARE, WISH_MAX)
        views = self._views(tin, tout, pairs, xs, concepts)[:WISH_VIEWS]
        start = len(self._built)
        out = []
        for k, spec in enumerate(views):
            left = until - time.time()
            if left <= 0:
                break
            got = self._build(spec, concepts, 0, time.time() + left / (len(views) - k), speak, task)
            if got is not None:
                e = spec['combine'](got, LG.node('var', payload=var))
                if task.consistent(e, concepts):                   # it solves the problem with what it built:
                    out.append((e, ('wished', spec['words'])))     # no more wishing
                    break
        if not [e for e, _ in out if e not in have] and not self._sees():     # nothing new: a new way of seeing,
            now = time.time()                            # with its own share of the time left (the views may have
                                                         # used all of theirs: 'where is', 600 s)
            grow_until = now + min(max(LG.DEADLINE[0] - now, 0.0) * WISH_SHARE, WISH_MAX)
            for e in self._grow_seeing(task, concepts, grow_until, speak):
                out.append((e, ('wished', 'see the whole problem from inside a function')))
        need = set()
        for e, _ in out:
            need |= self._abilities_in(e, concepts)
        drop = [b['id'] for b in self._built[start:] if b['id'] not in need]
        if drop:                                                  # what it built and did not need, it lets go
            self._retract(drop, concepts)
            speak('build', f'I let go of {len(drop)} abilities I built here that did not solve it.', n=len(drop))
        return out

    def _ideas(self):
        if getattr(self.field, 'ideas', None) is None:          # a Field saved before ideas had none
            self.field.ideas = PH.Ideas()
        return self.field.ideas

    def _stepfield(self):
        if getattr(self.field, 'steps', None) is None:          # a Field saved before steps had none
            self.field.steps = PH.StepField()
        return self.field.steps

    @staticmethod
    def _atoms(v):
        """The numbers a value holds, at every depth."""
        if isinstance(v, tuple):
            out = []
            for u in v:
                out += Sera._atoms(u)
            return out
        return [v]

    @staticmethod
    def _holds(v, y):
        """Is y inside v - the value itself, an element or part at any depth, or (for a list y) all its numbers?"""
        if v == y:
            return True
        if isinstance(v, tuple) and any(Sera._holds(u, y) for u in v):
            return True
        if isinstance(y, tuple) and y:
            have = Sera._atoms(v)
            return all(a in have for a in Sera._atoms(y))
        return False

    def _step_features(self, e, made, pairs, t, tout):
        """What a step makes, as its features (sera.phi.STEP_FEATURES) - never what the step is written as: the answer
        is inside what it makes; what it makes is smaller than the input; its type is nearer the answer's; it differs
        between examples; the step is simple."""
        inside = float(np.mean([self._holds(m, y) for m, (_, y) in zip(made, pairs)]))
        smaller = float(np.mean([1.0 - min(1.0, len(self._atoms(m)) / max(1, len(self._atoms(x))))
                                 for m, (x, _) in zip(made, pairs)]))
        toward = 1.0 / (1.0 + abs(LG.depth(t) - LG.depth(tout))) if t != 'bool' else 0.0
        varies = float(len({repr(m) for m in made}) > 1)
        simple = 1.0 / LG.size(e)
        return (inside, smaller, toward, varies, simple)

    def _step(self, task, concepts, speak, have, st):
        """One small step, then the rest (2026-09-29, the author: "break down ideas or problems into pieces, so it can
        search faster ... find the smallest and best step, do it correctly, then go to the next smallest step; older
        parts are already proven; when you are wrong, that is when you imagine the whole thing").
        A step is a small program of its own language over what it has (the problem's input, and the steps it has
        taken); what the step makes becomes one more input - a new dimension of the problem - so the rest is searched
        with the whole step as one symbol: an answer of n symbols with a step of k inside it is a search of n - k + 1.
        When the rest does not come soon it takes another small step from what it has now (up to STEP_DEPTH), solving
        as it goes. Which steps it looks at first is what it has learned makes a good step (sera.phi.StepField, a draw:
        it tries steps it is unsure of too), the ones it was curious about and has not finished first; a step is judged
        by whether the rest then comes (a small look ahead), and that teaches it what a good step is. A promising step
        left with no time stays in its curiosity for the next time, not forgotten. Only the whole answer goes to the
        judge; the steps inside it are not proven again. When no step works it still thinks of the whole (grow, wish):
        nothing it could find before is lost. Returns [(the answer through its steps, origin)]."""
        var = task.var
        tin, tout = task.inputs[var], task.out
        pairs = [(LG.freeze(x), LG.freeze(y)) for x, y in task.data]
        xs = [LG.freeze(x) for x in getattr(task, '_probe_inputs', [x for x, _ in pairs])]
        at = {repr(x): j for j, x in enumerate(xs)}
        where = [at.get(repr(x)) for x, _ in pairs]
        if any(j is None for j in where):                  # an example it asked about, not a probe: probe it too
            xs = xs + [x for (x, _), j in zip(pairs, where) if j is None]
            at = {repr(x): j for j, x in enumerate(xs)}
            where = [at[repr(x)] for x, _ in pairs]
        seen = task.perceive if hasattr(task, 'perceive') else (lambda x: x)   # the situation as it takes it in
        ctx = dict(task=task, concepts=concepts, pairs=[(seen(x), y) for x, y in pairs], where=where, xs=xs,
                   constants=tuple(task.numbers()) if hasattr(task, 'numbers') else (),   # what it perceives and
                   #                                                        the words it heard: the whole search's too
                   tout=tout, sf=self._stepfield(),
                   rng=np.random.default_rng([self.seed, st['steps'], len(concepts), 29]), names=self.field.names(),
                   teaching=st.get('teaching'), speak=speak)
        now = time.time()
        until = now + min(max(LG.DEADLINE[0] - now, 0.0) * STEP_SHARE, STEP_MAX)   # small steps are quick, or it
        saved = LG.DEADLINE[0]                                                     # goes back to the whole
        self._step_cut = False
        try:
            got = self._steps_from(ctx, {var: tin}, [{var: seen(x)} for x in xs], 0, until)   # forward: all its time
            self._step_cut = got is None and time.time() >= until      # cut by its time, not looked through
            back = None
            if got is None and BACK_ON and CR.on('way_back'):                   # stuck: imagine the way back from the goal, in a time of its
                now = time.time()                         # own (S05 F11, reviewer: a fixed share cut the forward steps)
                back_until = now + min(max(saved - now, 0.0) * BACK_SHARE, BACK_MAX)
                if back_until > now + 1.0:
                    back = self._backward(ctx, var, tin, [seen(x) for x in xs], back_until)
        finally:
            LG.DEADLINE[0] = saved
        if got is None and back is not None:
            prog, op, sub = back
            names = ctx['names']
            speak('build', f"I was stuck, so I imagined the last step to the answer - {LG.show(op, names)[:40]} of a "
                           f"part - and looked for that part: {LG.show(sub, names)[:50]}. Together: "
                           f"{LG.show(prog, names)[:90]}.", steps=1)
            return [(prog, ('imagined back', LG.show(op, names)[:40]))]
        if got is None:
            return []
        prog, chain, used = got
        if not task.consistent(prog, concepts):          # the whole does not fit: no evidence either way on its steps
            return []
        for f in used:                                    # only now, the whole answer fitting, do its steps count as
            ctx['sf'].learn(f, 1.0)                       # good ones, and leave its curiosity (S03, reviewer: success was
        self._open_steps = [s for s in self._open_steps if s['step'] not in chain]   # learned before the check)
        names = ctx['names']
        speak('build', f"I break it into {len(chain)} step{'s' if len(chain) > 1 else ''} "
                       f"({'; '.join(LG.show(e, names)[:50] for e in chain)}) and the rest follows: "
                       f"{LG.show(prog, names)[:90]}.", steps=len(chain))
        return [(prog, ('stepped', len(chain)))]

    def _backward(self, ctx, var, tin, xs_seen, until):
        """Stuck: it imagines how it would reach the goal (2026-09-29 night, the author: "it knows where it is and where
        it should go ... if it gets stuck it imagines how it would reach the goal and revises itself"). From the goal
        back one step: a small last operation of its own language that gives each example's answer from a part of
        what that example holds (a sentence, a word); the parts that do are a nearer goal, looked for forward from the
        input; the two ends meet in the answer, op(part). Returns (the answer, the last operation, the part's program)
        or None. Its language and abilities only: nothing about any task is given."""
        pairs, where, concepts = ctx['pairs'], ctx['where'], ctx['concepts']
        LG.DEADLINE[0] = until
        for T in ('list', 'num'):                        # the parts a situation holds: its sentences, its words
            if T == ctx['tout'] or time.time() > until:
                continue
            held = [LG._held_of(LG.freeze(x), T, [], 128) for x, _ in pairs]
            if any(not h for h in held):
                continue
            pool = list(dict.fromkeys(p for h in held for p in h))[:256]
            ops = []
            for level in range(BACK_SIZE + 1):           # the last operation: small, over one part
                for e, _, vals in self._search(ctx['task'], {'z': T}, ctx['tout'], [{'z': p} for p in pool], exact_size(level),
                                            concepts, lambda_size=lambda_size(level), values=True,
                                            constants=ctx.get('constants', ())):
                    if e[0] == 'var':
                        continue
                    got = {p: LG.seen_as(v) for p, v in zip(pool, vals)}
                    goal = [[p for p in h if got.get(p) == y] for h, (_, y) in zip(held, pairs)]
                    if all(goal):
                        ops.append((sum(len(g) for g in goal), LG.size(e), e, goal))
                if time.time() > until:
                    break
            ops.sort(key=lambda t: (t[0], t[1], repr(t[2])))           # the nearest goal first: fewest parts
            for _, _, op, goal in ops[:BACK_TRY]:
                wanted = [set(g) for g in goal]
                for level in range(STEP_REST + 1):       # then forward, from the input to that nearer goal
                    if time.time() > until:
                        return None
                    for e, _, vals in self._search(ctx['task'], {var: tin}, T, [{var: x} for x in xs_seen], exact_size(level),
                                                concepts, lambda_size=lambda_size(level), values=True,
                                                constants=ctx.get('constants', ()),
                                                work=LG.MAX_WORK * 2 ** level, if_part=if_part(level),
                                                sees=self._sees() and seeing_size(level)):
                        if all(LG.freeze(LG.seen_as(vals[j])) in w for j, w in zip(where, wanted)):
                            answer = _put(op, 'z', e)
                            if ctx['task'].consistent(answer, concepts):
                                return answer, op, e
        return None

    def _step_candidates(self, ctx, inputs, probes, until):
        """Steps it could take from what it has: small programs over its inputs, with what each makes on every probe
        and the features of what it makes on the examples. Not an input itself, nothing undefined on an example."""
        level = min(self._level, STEP_LEVEL)             # a step is small: sizes of its first levels
        types = LG.universe(list(inputs.values()) + [ctx['tout']])
        if isinstance(ctx['sf'], PH.FieldSteps):
            types = sorted(types, key=repr)
        out, seen = [], set()
        LG.DEADLINE[0] = until
        for t in types:
            if t == 'real':
                continue
            for e, _, vals in self._search(ctx['task'], inputs, t, probes, exact_size(level), ctx['concepts'],
                                        constants=ctx['constants'],
                                        lambda_size=lambda_size(level), values=True, work=LG.MAX_WORK * 2 ** level,
                                        if_part=if_part(level), sees=self._sees() and seeing_size(level)):
                if e[0] == 'var' or e in seen:
                    continue
                made = [LG.seen_as(vals[j]) for j in ctx['where']]
                if any(m is None for m in made):
                    continue
                seen.add(e)
                out.append((e, t, [LG.seen_as(v) for v in vals], made,
                            self._step_features(e, made, ctx['pairs'], t, ctx['tout'])))
            if time.time() > until:
                break
        if self.proposer is not None and self.proposer.enabled:
            for e, t, vals in self.proposer.step_fragments(inputs, probes, ctx['concepts'],
                                                          max_size=exact_size(level)):
                if e in seen:
                    continue
                made = [vals[j] for j in ctx['where']]
                out.append((e, t, vals, made, self._step_features(e, made, ctx['pairs'], t, ctx['tout'])))
                seen.add(e)
        return out

    def _rest(self, ctx, inputs, probes, until, step):
        """The rest, from everything it has now (the input and its steps): the smallest program that gives every
        example's answer and uses the step just taken (one that does not is no rest of it: a bug of 2026-09-29, 'what
        is' answered tail(tail(sare(g))) beside a step it never used), looked for up to STEP_REST sizes.
        Returns (the rest or None, whether it looked through every size - a step whose rest was cut by time is no
        evidence against it)."""
        LG.DEADLINE[0] = until
        complete = True
        for level in range(STEP_REST + 1):
            if time.time() > until:
                return None, False
            for e, _, vals in self._search(ctx['task'], inputs, ctx['tout'], probes, exact_size(level), ctx['concepts'],
                                        constants=ctx['constants'],
                                        lambda_size=lambda_size(level), values=True, work=LG.MAX_WORK * 2 ** level,
                                        if_part=if_part(level), sees=self._sees() and seeing_size(level)):
                if ('var', step) in LG.parts(e) and all(
                        LG.seen_as(vals[j]) == y for j, (_, y) in zip(ctx['where'], ctx['pairs'])):
                    return e, True
            complete = complete and LG.COMPLETE[0]         # a search cut by its work bound or a wall looked at
        return None, complete and time.time() <= until     # less than every size (S03, reviewer)

    def _steps_from(self, ctx, inputs, probes, depth, until):
        """Take a step from what it has, then find the rest, or take the next step (depth-first, time shared; no child
        is given time past its parent's: S03, reviewer). Returns (the answer as a program of the earlier inputs, the steps
        taken in it, their features - learned as good only once the whole answer fits) or None."""
        sf, rng = ctx['sf'], ctx['rng']
        now = time.time()
        cands = self._step_candidates(ctx, inputs, probes,           # seeing its steps: a quarter of its time, and
                                      min(until, now + max((until - now) * 0.25, STEP_SEE)))   # never too little
        if not cands:
            return None
        shown = set()                                    # the teacher's worked steps (teaching only): what each step
        worked = getattr(ctx['task'], 'worked', None)   # makes on the examples, never how - SERA finds its own step
        if ctx['teaching'] and worked is not None:      # that makes it; the teacher's word on steps (evidence, fading)
            ws = [worked(x) for x in ctx['xs']]          # every input it looks at that the teacher worked, not only
            at = [j for j, w in enumerate(ws) if w is not None and len(w) > depth]   # the examples (a step that
            if len(at) >= len(ctx['pairs']):             # agreed on 4 examples by luck: 'where', 2026-09-29)
                for k, c in enumerate(cands):
                    if all(c[2][j] == ws[j][depth] for j in at):
                        shown.add(k)
                        sf.teach(c[4], 1.0)
        curious = {repr(s['step']): k for k, s in enumerate(self._open_steps)}
        order = sorted(range(len(cands)), key=lambda k: (k not in shown,
                                                         curious.get(repr(cands[k][0]), len(curious)),
                                                         LG.size(cands[k][0]) if k in shown else 0,   # the simplest
                                                         -sf.score(cands[k][4], rng)))              # shown first
        cands = [cands[k] for k in order]
        if self.proposer is not None and self.proposer.enabled and not shown:
            cands = self.proposer.order_steps(ctx['task'], cands, ctx['concepts'])
        tried = cands[:STEP_TRY]
        name = f'w{depth + 1}'
        while name in inputs:                            # a name of its own, never an input's (S03 F4, reviewer)
            name += "'"
        for k, (e, t, vals, made, f) in enumerate(tried):
            left = until - time.time()
            if left <= 0:
                for c in tried[k:]:                      # curious, not forgotten: the next time, these first
                    if depth == 0 and all(s['step'] != c[0] for s in self._open_steps):
                        self._open_steps.append(dict(step=c[0], type=c[1], features=c[4]))
                break
            share = (left / min(len(shown) - k, 2) if k < len(shown)        # the teacher's steps (simplest first)
                     else left / (len(tried) - k))                           # have its time; others share it
            inputs2 = dict(inputs, **{name: t})
            probes2 = [dict(p, **{name: v}) for p, v in zip(probes, vals)]
            now = time.time()
            end = min(until, now + share)                 # never past the parent's time
            rest, looked = self._rest(ctx, inputs2, probes2,                       # a short look for the rest here,
                                      min(end, now + share * (0.3 if depth + 1 < STEP_DEPTH else 1.0)), name)
            chain, used = [], []
            if rest is None and depth + 1 < STEP_DEPTH:  # not soon: the next small step, from what it has now, with
                looked = False                           # what is left of this step's time (its rest may lie further)
                deeper = self._steps_from(ctx, inputs2, probes2, depth + 1, end)
                if deeper is not None and ('var', name) in LG.parts(deeper[0]):     # the next steps build on this one
                    rest, chain, used = deeper
            if rest is not None:
                return _put(rest, name, e), [e] + chain, [f] + used
            if looked:                                   # a real no - every size looked through - teaches it; a step
                sf.learn(f, -1.0)                       # whose rest was cut by time or a bound does not
        return None

    def _sees(self):
        """Has it grown functions that see the problem around them (its own grammar growth, _grow_seeing)?"""
        return 'see around' in getattr(self.field, 'grown', ())

    def _grow_seeing(self, task, concepts, until, speak):
        """A new kind of idea, not a new idea (2026-09-28, the author: SERA grows it itself). When no view makes the
        problem smaller, it wishes its functions could see the whole problem around them - not only the element they
        are given - and thinks again that way. The new way of seeing is kept only if it solves the problem here;
        from then on it is part of how it thinks, in every subject. Returns every answer that fits (the judge tells
        a lucky fit from the true one: on 'where is', two that compare words' numbers fit the examples and fail the
        audit), or []."""
        saved = LG.DEADLINE[0]
        LG.DEADLINE[0] = min(saved, until)
        nums = task.numbers() if hasattr(task, 'numbers') else ()
        try:
            level = 0
            while time.time() < until:
                found = self._search(task, task.inputs, task.out, task.probes(), exact_size(level), concepts,
                                  lambda_size=lambda_size(level), constants=nums, values=True,
                                  work=LG.MAX_WORK * 2 ** level, if_part=if_part(level), sees=seeing_size(level))
                fits = [e for e, _, _ in found if LG.sees(e) and task.consistent(e, concepts)]
                if fits:                                     # every one that fits: the judge tells them apart
                    if not hasattr(self.field, 'grown'):
                        self.field.grown = set()
                    self.field.grown.add('see around')
                    speak('build', 'I wish my functions could see the whole problem, not only the part they are '
                                   f'given. I grow that way of seeing, and {len(fits)} ideas fit this, first '
                                   f'{LG.show(fits[0], self.field.names())[:80]}.', grown='see around')
                    return fits
                level += 1
        finally:
            LG.DEADLINE[0] = saved
        return []

    def _inner_ability(self, law, var, task, concepts):
        """What a proven program does to the part of the input it works on (abstraction, 2026-09-28 night: in 'last
        word', foldn(λa,e. e, 5, head(tail(g))) - the last of the first sentence - holds 'the last of any list',
        foldn(λa,e. e, 5, _), which 'where is Mary' needs for another sentence). Going down from the top while only
        one branch holds the input (outside any λ), the largest such part is cut out; what is left, and that part
        itself ('the sentence about the one the question names', which 'what is' needs), each become a concept too if
        it is a program of its own: 3 nodes or more, a type it can infer, working on every value it met in this world,
        and not an idea it has already - by what it does on those values, not only by how it is written (S02, reviewer:
        foldn(λa,e. e, 0, _) and foldn(λa,e. e, 5, _) are one idea on sentences). A way of learning, the same in
        every subject, not an ability. Returns the concepts it kept."""
        if not self.library_enabled:
            return []
        path, q = [], law
        while True:                                          # down the one branch that holds the input
            kids = [(i, k) for i, k in enumerate(q[2:], 2) if ('var', var) in LG.parts(k)]
            if q[0] == 'lam' or len(kids) != 1:
                break
            i, k = kids[0]
            if k == LG.node('var', payload=var):
                break
            path.append(i)
            q = k
        if not path or LG.size(q) < 2:
            return []
        hole = LG.node('var', payload='_')

        def cut(p, where):
            if not where:
                return hole
            i = where[0]
            return p[:i] + (cut(p[i], where[1:]),) + p[i + 1:]
        part = law
        for i in path[:1]:
            part = part[i]                                   # the largest part that holds the input
        kept = []
        inputs = [LG.freeze(x) for x in getattr(task, '_probe_inputs', [x for x, _ in task.data])]
        parts_met = [LG.safe(part, {var: x}, concepts) for x in inputs]
        for body, built, args in ((cut(law, path[:1]), 'what it does to its part', parts_met),
                                  (_subst(part, var, '_'), 'the part it works on', inputs)):
            if LG.size(body) < 3 or ('var', var) in LG.parts(body):
                continue
            sig = LG.infer(body, concepts)
            if sig is None or any(c['body'] == body for c in self.field.concepts):
                continue
            args = [a for a in args if a is not None]
            vals = [LG.safe(body, {'_': a}, concepts) for a in args]
            if not args or any(v is None for v in vals):
                continue                                 # it must work on what it met here
            same = False
            for cid, entry in concepts.items():
                if cid == '_sig':
                    continue
                cbody, carg = entry
                if all(LG.safe(cbody, {carg: a}, concepts) == v for a, v in zip(args, vals)):
                    same = True                          # an idea it has, written another way
                    break
            if same:
                continue
            c = self.field.invent(body, sig, task.subject, f'{task.name} (inside)', LG.parts(body),
                                  extra=dict(built=built))
            self._register(c)
            concepts[c['id']] = (c['body'], '_')
            concepts.setdefault('_sig', {})[c['id']] = tuple(c['sig'])
            self.field.lexicon.word_for(('concept', c['id']), coin=True)
            kept.append(c)
        return kept

    def _abilities_in(self, e, concepts):
        """The concepts an expression uses, and the ones those are built on."""
        out, stack = set(), [e]
        while stack:
            q = stack.pop()
            for p in LG.parts(q):
                if p[0] == 'concept' and p[1] not in out and p[1] in concepts:
                    out.add(p[1])
                    stack.append(concepts[p[1]][0])
        return out

    def _retract(self, ids, concepts):
        F = self.field
        F.concepts = [c for c in F.concepts if c['id'] not in ids]
        for cid in ids:
            concepts.pop(cid, None)
            concepts.get('_sig', {}).pop(cid, None)
            F.lexicon.coined.pop(('concept', cid), None)
        self._built = [b for b in self._built if b['id'] not in ids]

    def _views(self, tin, tout, pairs, xs, concepts):
        """Ways of seeing a problem (examples `pairs` from type tin to tout; `xs`, every input it has seen) as a smaller
        one: [{words, tin, tout, pairs, xs, combine(ability, input expression)}].
        - each: a list in, a list of the same length out, and each element from its own element (one ability for an
          element, used on every one);
        - after one of its abilities: the answer from what that ability makes of the input (the rest is the new one);
        - before one of its abilities that undoes itself on the answers: the new ability makes what it then turns
          into the answer.
        Its abilities are ways of seeing too: every ability it builds makes the next problems smaller."""
        out = []
        node = LG.node
        depth = min(LG.depth(tin), LG.depth(tout))
        for d in sorted({depth, 1} - {0}, reverse=True):         # each element: all the way down, then one level
            obs = []
            for x, y in pairs:
                got = _aligned(x, y, d)
                if got is None:
                    obs = None
                    break
                obs += got
            if not obs:
                continue
            sub, ok = {}, True
            for a, b in obs:
                if sub.setdefault(a, b) != b:
                    ok = False
            if not ok or len(sub) == len(obs) or all(a == b for a, b in sub.items()):
                continue                    # an element must show that it decides what it becomes (seen more than once)
            elems = list(dict.fromkeys(a for x in xs for a in _elements(x, d)))
            tin_d, tout_d = tin, tout
            for _ in range(d):
                tin_d, tout_d = LG.elem(tin_d), LG.elem(tout_d)
            out.append(dict(words='make each element what it becomes' if d == 1 else
                            f'make each element, {d} lists down, what it becomes', tin=tin_d, tout=tout_d,
                            pairs=list(sub.items()), xs=elems, combine=lambda c, v, d=d: _each_down(c, v, d)))
        if tout == 'num' and len(pairs) >= 2:                   # cases: the special case first, then the rest
            ins = [a for a, _ in pairs]
            probe = [{'w': a} for a in ins]
            names = self.field.names()
            for cond, _, vals in LG.search({'w': tin}, 'bool', probe, 3, concepts, constants=TS.numbers_of(pairs),
                                           values=True):
                if len([v for v in out if v['words'].startswith('handle')]) >= 2:
                    break
                for side in (True, False):
                    one = {b for (_, b), v in zip(pairs, vals) if v is side}
                    rest = [(a, b) for (a, b), v in zip(pairs, vals) if v is not side]
                    if len(one) != 1 or not rest or len(rest) == len(pairs):
                        continue
                    k = next(iter(one))
                    if all(a == k for (a, _), v in zip(pairs, vals) if v is side):
                        continue                                  # a special case that changes nothing is none
                    keep = [x for x in xs if LG.safe(cond, {'w': x}, concepts) is not side]
                    out.append(dict(words=f'handle {LG.show(cond, names)} (it gives {k}), then the rest', tin=tin,
                                    tout=tout, pairs=rest, xs=keep,
                                    combine=lambda c, v, cond=cond, k=k, side=side: node(
                                        'if', _put(cond, 'w', v), *((node('lit', payload=k), node('c', v, payload=c))
                                                                    if side else
                                                                    (node('c', v, payload=c), node('lit', payload=k))))))
                    break
        names = self.field.names()
        sig = concepts.get('_sig', {})
        for cid in sorted(sig, key=lambda c: -next((x['uses'] for x in self.field.concepts if x['id'] == c), 0)):
            for mid in LG.universe([tin, tout]):
                if not LG.fits(sig[cid], tin, mid):
                    continue
                made = [LG.safe(node('c', node('var', payload='w'), payload=cid), {'w': x}, concepts) for x, _ in pairs]
                if any(m is None for m in made) or all(m == x for m, (x, _) in zip(made, pairs)):
                    break
                sub, ok = {}, True
                for m, (_, y) in zip(made, pairs):
                    if sub.setdefault(m, y) != y:
                        ok = False
                if ok:
                    seen = [LG.safe(node('c', node('var', payload='w'), payload=cid), {'w': x}, concepts) for x in xs]
                    out.append(dict(words=f'finish what {names.get(cid, cid)} starts', tin=mid, tout=tout,
                                    pairs=list(sub.items()), xs=[s for s in seen if s is not None],
                                    combine=lambda c, v, cid=cid: node('c', node('c', v, payload=cid), payload=c)))
                break
            if LG.fits(sig[cid], tout, tout):
                w = node('c', node('var', payload='w'), payload=cid)
                back = [LG.safe(w, {'w': y}, concepts) for _, y in pairs]
                if all(b is not None and LG.safe(w, {'w': b}, concepts) == y for b, (_, y) in zip(back, pairs)):
                    out.append(dict(words=f'make what {names.get(cid, cid)} turns into the answer', tin=tin, tout=tout,
                                    pairs=[(x, b) for (x, _), b in zip(pairs, back)], xs=xs,
                                    combine=lambda c, v, cid=cid: node('c', node('c', v, payload=c), payload=cid)))
        return out

    def _build(self, spec, concepts, depth, until, speak, task):
        """Build the ability a view asks for: a program of its language from spec['tin'] to spec['tout'] that gives
        every one of the view's examples - one it has already, or its own search, bigger and harder, and when that does
        not find it soon, a wish inside the wish (an ability within the ability). Kept as a concept of its language.
        Returns the concept's id, or None."""
        pairs = spec['pairs']
        w = LG.node('var', payload='w')
        for cid, sg in concepts.get('_sig', {}).items():                    # an ability it has already
            if LG.fits(sg, spec['tin'], spec['tout']) and all(
                    LG.safe(LG.node('c', w, payload=cid), {'w': a}, concepts) == b for a, b in pairs):
                return cid
        ins = [a for a, _ in pairs]
        known = set(ins)
        xs = (ins + [x for x in dict.fromkeys(spec['xs']) if x not in known])[:max(WISH_PROBES, len(ins))]
        probes = [{'w': x} for x in xs]
        nums = TS.numbers_of(pairs)
        saved = LG.DEADLINE[0]
        LG.DEADLINE[0] = min(saved, until)
        try:
            level = 0
            while time.time() < until:
                found = self._search(task, {'w': spec['tin']}, spec['tout'], probes, exact_size(level), concepts,
                                  lambda_size=lambda_size(level), constants=nums, values=True,
                                  work=LG.MAX_WORK * 2 ** level, if_part=if_part(level),
                                  sees=self._sees() and seeing_size(level))
                for e, _, vals in found:
                    if all(LG.seen_as(vals[j]) == b for j, (_, b) in enumerate(pairs)):
                        return self._keep_ability(e, spec, concepts, speak, task)
                if level == 2 and depth + 1 < WISH_DEPTH:              # not soon: an ability within the ability
                    views = self._views(spec['tin'], spec['tout'], pairs, xs, concepts)[:WISH_VIEWS]
                    for k, sub in enumerate(views):
                        left = until - time.time()
                        if left <= 0:
                            break
                        got = self._build(sub, concepts, depth + 1, time.time() + left * WISH_SHARE / (len(views) - k),
                                          speak, task)
                        if got is None:
                            continue
                        e = sub['combine'](got, w)
                        if all(LG.safe(e, {'w': a}, concepts) == b for a, b in pairs):
                            return self._keep_ability(e, spec, concepts, speak, task)
                level += 1
        finally:
            LG.DEADLINE[0] = saved
        return None

    def _keep_ability(self, program, spec, concepts, speak, task):
        """An ability it built becomes a concept of its language at once: usable here and everywhere after."""
        F = self.field
        body = _subst(program, 'w', '_')
        sig = LG.infer(body, concepts)
        if sig is None or not LG.fits(sig, spec['tin'], spec['tout']):
            sig = (spec['tin'], spec['tout'])
        c = F.invent(body, sig, task.subject, f'{task.name} (wished)', LG.parts(program),
                     extra=dict(built=spec['words']))
        self._register(c)
        concepts[c['id']] = (c['body'], '_')                               # usable in this world from now
        concepts.setdefault('_sig', {})[c['id']] = tuple(c['sig'])
        name = F.lexicon.word_for(('concept', c['id']), coin=True)
        text = f"I wish I could {spec['words']}: I build it ({name} = {LG.show(body, F.names())[:80]}) and use it."
        speak('build', text, ability=c['id'])
        self._built.append(dict(id=c['id'], name=name, words=spec['words'], body=LG.show(body, F.names())[:200]))
        return c['id']

    def _question(self, task, law, concepts, mu, speak):
        """'What is it?': for each drawn curve in the thought (a free curve's fitted knots, or a kept table), the
        expressions of its language (up to QUESTION_SIZE nodes) that draw the same shape, up to one strength, within
        QUESTION_TOL of its largest value - the thought with the curve replaced by the formula. Understanding a
        measurement as a law of its own."""
        out = []
        probes = [{'s': float(v)} for v in (-5.0, -3.0, -1.5, -0.5, 0.0, 0.5, 1.0, 2.0, 4.0)]
        exprs = None
        for part in law:
            ch, kind, ref = part
            if kind == 'curve':
                knots = task.fitted_curve(law, part, concepts, mu)
                g = TS.grid(ch, int(ref))
            elif kind == 'expr' and ref[0] == 'tab':
                g, knots = np.asarray(ref[1][0]), ref[1][1]
            else:
                continue
            if knots is None:
                continue
            knots = np.asarray(knots, float)
            if exprs is None:
                exprs = [e for e, _ in LG.search({'s': 'num'}, 'num', probes, QUESTION_SIZE, concepts)]
            found = []
            for e in exprs:
                vals = [LG.safe(e, {'s': float(x)}, concepts) for x in g]
                if any(v is None or isinstance(v, (bool, tuple)) for v in vals):
                    continue
                y = np.asarray(vals, float)
                if not np.all(np.isfinite(y)) or float(y @ y) < 1e-12:
                    continue
                c = float(y @ knots) / float(y @ y)
                if float(np.max(np.abs(c * y - knots))) <= QUESTION_TOL * float(np.max(np.abs(knots))):
                    found.append(e)
            for e in found[:3]:
                new = tuple(sorted([p for p in law if p != part] + [(ch, 'expr', e)], key=repr))
                out.append((new, ('questioned', LG.show(e, self.field.names())[:60])))
            if found:
                speak('imagine', f'I ask what my curve in {grammar.describe_input(ch)} is: it looks like '
                                 f'{LG.show(found[0], self.field.names())[:60]}.', formula=LG.show(found[0])[:80])
        return out

    def _ask_us(self, task, leader, doubt, st, speak, cap=False):
        names = self.field.names()
        what = ('nothing' if not leader else           # no idea at all (an exact task out of time, too)
                LG.show(leader, names) if task.form == 'exact' else
                ' + '.join(f"{k if k != 'expr' else LG.show(r, names)} of {ch}" for ch, k, r in leader))
        why = ('none of my ideas fits the examples' if st.get('none_fit') else   # its doubt is only against its
               f'{doubt:.1f} nats of doubt')                                      # other ideas (S09 #4)
        text = (f"In {task.name} my best idea is {what}, but I cannot finish ({why}"
                + (', and I reached my limit' if cap else '') + '). Is it right, or what am I missing?')
        qid = self.field.ask(task.name, 'cannot finish', text, key=leader, kind=kind_of(task),
                             meanings=self._meanings(leader, task.form) if leader is not None else (),
                             doubt=float(doubt), cap=bool(cap))
        speak('ask us', text, id=qid)

    def _where_to_look(self, task, leader, concepts, mu, library=(), what=('lens', 'dim')):
        """A new sense that would explain the most (its own perception; nothing about the world is given), by the
        Field's exact evidence (which pays for the knots), against its leading idea:
        - a lens: every window a lens can have over what it has seen (each input, 2^j times closer, j = 1 .. 6, centred
          on the lattice of half windows), its leading idea with that input's part replaced by a 33-knot curve there;
        - a new dimension (Decision 15; the author: "more dimensions of perception"): every program of its own language
          over position, speed and time that mixes at least two of them (sera.lang, searched up to DIM_SIZE nodes, one
          per behaviour), its leading idea's drawn parts plus a 17-knot curve along that combination.
        A law keeps at most one free curve. Returns (the sense, the nats it gains) for the best one it does not have
        yet, or None when none gains LOOK_NATS. `what`: the kinds of sense to weigh (the moves 'closer', 'dimension')."""
        have = set(self._channels())
        seen = task.seen()
        base_e = task.evidence([leader], concepts, library, mu).get(leader)
        if base_e is None:
            return None
        drawn = [p for p in leader if p[1] != 'curve']
        cands = []
        for b in (TS.CHANNELS if 'lens' in what else ()):
            slo, shi = seen[b]
            lo, hi = grammar.input_range(b)
            for j in grammar.LENS_J:
                half = (hi - lo) / 2 ** (j + 1)
                for m in range(0, 2 ** (j + 1) + 1):
                    name = grammar.lens_name(b, j, m)
                    c = lo + m * half
                    if name in have or c + half <= slo or c - half >= shi:      # it never looked there
                        continue
                    cands.append((name, [p for p in drawn if TS.base(p[0]) != b] + [(name, 'curve', TS.K_PART)]))
        for name in (self._dimensions(task) if 'dim' in what else ()):
            if name not in have:
                cands.append((name, drawn + [(name, 'curve', 17)]))
        best = None
        for name, law in cands:
            law = tuple(sorted(law, key=repr))
            e = task.evidence([law], concepts, library, mu).get(law)
            if e is not None and (best is None or e - base_e > best[1]):
                best = (name, e - base_e, law)
        return best if best is not None and best[1] >= LOOK_NATS else None

    def _keep_footholds(self, task, leader, concepts, library, mu, st, speak):
        """The snowball, within a world: every part of its leading idea that the idea cannot do without - its evidence
        falls by at least FOOTHOLD_NATS when the part is left out - is a foothold, kept for all its later thinking here
        (and said once, when it first holds)."""
        subs = {tuple(q for q in leader if q != p): p for p in leader}
        E = task.evidence([leader] + list(subs), concepts, library, mu)
        if leader not in E:
            return
        for sub, p in subs.items():
            gain = E[leader] - E.get(sub, -math.inf)
            if gain >= FOOTHOLD_NATS:
                if p not in st['footholds']:
                    how = (f'explains {gain:.0f} nats' if math.isfinite(gain)        # infinite: without it, the rest
                           else 'is all I have that fits')                          # cannot be weighed at all
                    speak('foothold', f'I keep what was right: {self._part_words(p)} {how}; I build on it and look '
                                      f'for the rest.', part=repr(p)[:120])
                st['footholds'][p] = float(min(gain, 1e6))

    def _part_words(self, part):
        ch, kind, ref = part
        where = grammar.describe_input(ch)
        if kind == 'concept':
            return f'{self.field.names().get(ref, ref)} of {where}'
        if kind == 'curve':
            return f'a curve in {where}'
        return f'{LG.show(ref, self.field.names())[:40]} of {where}'

    def _as_drawn(self, task, part, concepts, mu, st):
        """A foothold as a part other worlds can use: a drawn part as it is; a free curve as the table of its fitted
        values (a drawn shape, one strength) - an unproven, tentative idea."""
        ch, kind, ref = part
        if kind != 'curve':
            return part
        knots = task.fitted_curve(tuple(st['footholds']), part, concepts, mu)
        if knots is None:
            return None
        g = TS.grid(ch, int(ref))
        return (ch, 'expr', LG.node('tab', LG.node('var', payload='s'),
                                    payload=(tuple(float(x) for x in g), tuple(float(k) for k in knots))))

    @staticmethod
    def _affine(u, w):
        """Is u an affine function of w where it looked (a + b w)? Then a sense of u sees nothing w does not."""
        A = np.stack([np.ones_like(w), w], axis=1)
        coef, *_ = np.linalg.lstsq(A, u, rcond=None)
        return float(np.max(np.abs(A @ coef - u))) <= 1e-9 * max(float(np.max(np.abs(u))), 1.0)

    def _dimensions(self, task):
        """The new dimensions it can write: programs of its own language over position, speed and time (x, v, t), up to
        DIM_SIZE nodes, one per behaviour; each looked at over the smallest range 2^(r - 4) that holds what it has seen
        (Decision 15). A sense of one input counts when it is not that input rescaled (2026-09-28: the stiff spring is
        a straight line in position cubed, while no curve drawn in position passed the judge; senses had to mix two
        inputs before). Names, in the judge's form."""
        if self._dims_cache is not None:
            return self._dims_cache
        rng = np.random.default_rng(3)
        probes = [{'x': float(rng.uniform(-3, 3)), 'v': float(rng.uniform(-6, 6)), 't': float(rng.uniform(0, 2))}
                  for _ in range(12)]
        seen = task.throws
        xs = np.concatenate([t.x for t in seen])
        vs = np.concatenate([t.v for t in seen])
        ts = np.concatenate([np.arange(paths.N_OBS) * paths.DT_OBS for _ in seen])
        out = []
        by = {'x': xs, 'v': vs, 't': ts}
        for e, _ in LG.search({'x': 'num', 'v': 'num', 't': 'num'}, 'num', probes, DIM_SIZE):
            toks = _tokens(e)
            used = {t for t in toks if t in ('x', 'v', 't')} if toks is not None else set()
            if toks is None or not used or len(toks) > grammar.DIM_MAX:
                continue
            probe = grammar.dim_name(toks, grammar.DIM_R[-1])
            if not grammar.is_dim(probe):
                continue
            u = grammar.dim_eval(probe, xs, vs, ts)
            top = float(np.max(np.abs(u))) if u.size else 0.0
            if not (np.all(np.isfinite(u)) and top > 1e-9):
                continue
            if len(used) == 1 and self._affine(u, by[next(iter(used))]):
                continue                                  # the input itself, rescaled: nothing new to see
            r = next((r for r in grammar.DIM_R if 2.0 ** (r - 4) >= top), None)
            if r is not None:
                out.append(grammar.dim_name(toks, r))
        self._dims_cache = list(dict.fromkeys(out))
        return self._dims_cache

    @staticmethod
    def _none_fit_late(st):
        """None of its ideas fits the examples, and it has thought bigger past where that is cheap (a level-3 search
        and up: 16 s, then 74, 357 s for the general SERA). Before that, a bigger search is the quick way (shown a
        step at every level, its list-then-numbers lesson took 844 s instead of 3 s)."""
        return bool(st.get('none_fit')) and st.get('level', 0) >= NOFIT_LEVEL and CR.on('teacher_none_fits')

    @staticmethod
    def teacher_method(moment, moves, st):
        """The teacher's way of imagining here (shown in teaching only; evidence for SERA's own methods, fading): when
        the judge still finds a grown idea short, keep what was right and look closer (or make a new dimension); when
        a curve fits, ask what it is; in doubt, recall what worked elsewhere, or keep what was right and build on it."""
        short = moment['misfit'] or st['judge_short'] > 0
        lost = moment['doubt'] > 0.3 or Sera._none_fit_late(st)   # in doubt, or none of its ideas fits the examples
        #   and thinking bigger no longer comes cheap (the teacher sees what fits; SERA's doubt is only against its
        #   other ideas, 0 when none fits: the general SERA's 'where', 2026-10-01 - its step finds it in 68 s, but at
        #   "0.0 nats" the step was never shown)
        if st['level'] >= 2 and short and 'closer' in moves:
            return ('keep', 'closer') if 'keep' in moves else ('closer',)
        if st['level'] >= 2 and short and 'dimension' in moves:
            return ('dimension',)
        if 'question' in moves and not moment['misfit']:
            return ('question',)
        if 'step' in moves and lost:
            return ('step',)                # a big problem: take the smallest good step, then solve the rest (2026-09-29;
            #                                 from the start: the author, "find the smallest and best step ... when you
            #                                 are wrong, that is when you imagine the whole thing")
        if 'wish' in moves and st['level'] >= 2 and lost:
            return ('wish',)                # nothing it can say fits yet: wish for the ability it lacks, build it, use it
        if 'recall' in moves and moment['doubt'] > 0.5:
            return ('recall',)
        if 'keep' in moves and st['level'] >= 1 and moment['doubt'] > 0.5:
            return ('keep',)
        return None

    def _closeness(self, cand, where):
        """How near a push's predicted path passes the reading where the judge is least sure (1 through it, 0 far):
        a Gaussian in position, speed and time, at a tenth of each range's width."""
        if not where or cand.get('predicted') is None:
            return 0.0
        y = np.asarray(cand['predicted'], float)
        n = len(y) // 2
        xs, vs = y[:n], y[n:]
        ts = np.arange(n) * paths.DT_OBS
        d2 = ((xs - where['x']) / 0.6) ** 2 + ((vs - where['v']) / 1.2) ** 2 + ((ts - where['t']) / 0.2) ** 2
        return float(np.exp(-0.5 * np.min(d2))) if n else 0.0

    @staticmethod
    def _observe_push(st):
        if CR.on('teach_rechecking'):
            st['pushes_since_report'] = st.get('pushes_since_report', 0) + 1

    @staticmethod
    def _observe_report(st):
        if CR.on('teach_rechecking'):
            st['pushes_since_report'] = 0

    @staticmethod
    def teacher_way(moment, available, st, shown=None):
        """How the teacher works (shown in teaching only; it enters the Field as evidence and fades): grow when nothing
        fits; imagine when it has a way to (teacher_method); when the judge is unsure somewhere, show it there; ask
        while in doubt; prove when sure enough; look around once proven; then leave. Once proven, it does not chase a
        new idea (2026-09-28: wind 1, proven at step 5, then 200 more steps on an idea that led after the proof)."""
        if moment['proven']:
            if 'explore' in available and st['explored'] < 2:
                return ['explore']
            if 'leave' in available:
                return ['leave']
        if (CR.on('teach_rechecking') and st.get('teaching') and st.get('recheck_advice', True)
                and st.get('judge_short', 0) > 0 and st.get('pushes_since_report', 0) > 0
                and 'prove' in available):
            return ['prove']  # demonstration only: the LoopField still draws the configuration
        if moment['misfit'] and 'grow' in available and st['level'] < 2:
            return ['grow']
        if shown is not None and 'imagine' in available and (moment['misfit'] or moment['doubt'] > 0.5
                                                              or st['judge_short'] > 0 or Sera._none_fit_late(st)):
            return ['imagine']
        if moment['misfit'] and 'grow' in available:
            return ['grow']
        if 'convince' in available:
            return ['convince', 'ask'] if 'ask' in available else ['convince']
        if moment['doubt'] > 0.2 and 'ask' in available:
            return ['ask']
        if 'prove' in available:
            return ['prove']
        if moment['proven'] and 'explore' in available and st['explored'] < 2:
            return ['explore']
        if 'leave' in available:
            return ['leave']
        return sorted(available)[:1]

    # ------------------------------------------------------------------ after the world
    def _finish(self, task, kind, ctx, concepts, library, st, leader, order, phi, logE, extra, choices, tension_log,
                say, teaching, t0, c0, mu=None, answer_channel=None):
        F = self.field
        finish_wall, finish_cpu = time.time(), time.process_time()
        LG.DEADLINE[0] = math.inf                          # the world's time box is over
        proven = st['proven']
        rec = dict(task=task.name, subject=task.subject, form=task.form, kind=kind,
                   teaching=bool(teaching), steps=st['steps'],
                   answer=((proven['law'] if proven is not None else leader)          # what it proved, when it proved
                           if task.form == 'exact' else None),  # something (else its leading answer): a record that says
                   #                                              proven must carry the proven program (S04 R4, reviewer)
                   others=list(order[1:6]) if task.form == 'exact' else None,     # its next ideas (a second answer)
                   level=st['level'], asked=st['asked'], explored=st['explored'], choices=choices,
                   tension=tension_log, wall=round(time.time() - t0, 1), cpu=round(time.process_time() - c0, 1),
                   proven=proven is not None, invented=[], reused=[], words_heard=list(task.words), said=[],
                   false_words=[], serendipity=None, duality=None, senses=list(self._task_senses),
                   senses_used=[], timing=dict(st['time']), built=list(self._built),
                   peak_mb=st['peak'][0], peak_mb_by=dict(st['peak_by']), memory_stops=st['memory_stops'],
                   settings=CR.settings())
        if CR.on('judge_scrutiny'):
            rec['judge_scrutiny'] = list(st.get('scrutiny', ()))
        off_choice_cpu = rec['cpu']                       # compatibility estimate, never reported as total cost
        course_feedback = None
        course_credit = True
        if answer_channel is not None:
            law = proven['law'] if proven is not None else leader
            if law is not None and hasattr(self, '_u_predict'):
                self._u_predict(task, law)
            course_feedback = answer_channel(task, law, concepts, proven)
            if course_feedback is not None:
                course_credit = course_feedback.get('right') is True
                verdict_law = law
                if course_credit and proven is not None and task.form == 'strengths':
                    verdict_law, _ = self._certified(law, proven.get('credit'), proven['family'], concepts)
                    course_credit = verdict_law is not None  # credit only the certified curve/drawing/formula
                if verdict_law is not None and course_feedback.get('right') is not None:
                    self.course_verdict(task, verdict_law, course_feedback['right'], course_feedback['source'],
                                        course_feedback.get('reliability', False))
                    if not course_feedback['right']:
                        st.setdefault('refuters', set()).add(('teacher', law))
            if proven is not None and course_credit:
                self._echo(task, +1.0, lambda *a, **k: None)
            if 'course_prove_return' in st:
                features, cost = st['course_prove_return']
                F.loop.learn('prove', features, float(np.clip((PH.V_DONE if course_credit else 0.0) / cost,
                                                            -5.0, 20.0)))
        new, credited, proof, held, attributed = {}, False, None, [], True
        if proven is not None:
            law = proven['law']
            kept = law                                     # what it keeps of the proof (physics: what was certified)
            if task.form == 'strengths':
                cert = proven['cert']
                kept, certified = self._certified(law, proven.get('credit'), proven['family'], concepts)
                g = (task.grade(cert, True, n_throws=proven.get('n')) if answer_channel is None
                     else dict(verdict='proven'))         # course observer grades only outside the mind
                fit = proven.get('fit')
                if fit is None:                            # older/caller-supplied proof states
                    led = task.ledger([proven['family']])
                    fit = led.mle(proven['family'])
                signs = self._signs(proven['family'], fit)
                rec.update(claim=grammar.name(proven['family']), band=cert.band, verdict=g['verdict'],
                           gap=g.get('gap'), signs=signs, certified=certified)
                q = self._what_is_mass(task, fit)          # a deeper question, from what it measured
                if q is not None:
                    rec['question'] = q
                rec['attributed'] = attributed = kept is not None   # every part's certified object known; else it
                credited = (self._credited(teaching, g, rec, say) if answer_channel is None
                            else course_credit) and attributed
                kept = law if kept is None else kept
                for part in (kept if credited else ()):    # a lens that helped a proof stays one of its senses
                    for l in F.senses:
                        if l['name'] == part[0]:
                            l['uses'] += 1
                            rec['senses_used'].append(part[0])
                proved = {c['part']: c['as'] for c in certified}
                for i, part in enumerate(kept if credited else ()):
                    ch, k, ref = part
                    if k == 'concept':                     # its drawing proven, or its formula (a ramp): it is used
                        self._used(ref, rec)
                        continue
                    if not (k == 'curve' or (k == 'expr' and proved.get(i) == 'formula')):
                        continue                           # a curve, including one on a composed coordinate; a
                                                           # formula only by its own ramp (Decision 16)
                    t = proven['credit'][i][0]
                    c = self._invent_part(task, part, proven['family'], fit, concepts, ctx,
                                          proof=dict(claim=grammar.name(proven['family']), term=repr(t),
                                                     digest=cert.digest, eps=cert.eps, band=cert.band,
                                                     throws=proven.get('n'), at=F.tasks))   # its proof (S14 F3)
                    if c is not None:
                        new[i] = c['id']
                        rec['invented'].append(dict(id=c['id'], subject='physics', input=ch, how=k,
                                                    body=LG.show(c['body'])))
            else:
                came = dict(getattr(self._ideas(), '_came', {}))
                g = (task.grade(law, concepts, True, seed=self.seed) if answer_channel is None
                     else dict(verdict='proven'))         # no hidden grade enters course Field.log or credit
                self._ideas()._came = came                             # memory's traces (S07 F4, reviewer)
                rec.update(claim=LG.show(law, F.names()), verdict=g['verdict'], audit=proven['audit'])
                signs = None
                credited = (self._credited(teaching, g, rec, say) if answer_channel is None else course_credit)
                for p in LG.parts(law):
                    if p[0] == 'concept':
                        self._used(p[1], rec)
                        if credited:                       # an ability it wished, now in a proof: proven by use
                            F.audited_by(p[1], task.name)
                var = next(iter(task.inputs))
                pure = law[0] == 'c' and law[2] == LG.node('var', payload=var)      # a concept, reused as it is
                if self.library_enabled and credited and LG.size(law) >= 3 and not pure and len(task.inputs) == 1:
                    #                                                                          concept
                    body = _subst(law, var, '_')
                    sig = LG.infer(body, concepts)        # the most general type its body allows (2026-09-28)
                    if sig is None or not LG.fits(sig, task.inputs[var], task.out):
                        sig = (task.inputs[var], task.out)
                    c = F.invent(body, sig, task.subject, task.name, LG.parts(law))
                    self._register(c)
                    new['all'] = c['id']
                    rec['invented'].append(dict(id=c['id'], subject=task.subject, body=LG.show(c['body'], F.names())))
                    for inner in self._inner_ability(law, var, task, concepts):
                        rec['invented'].append(dict(id=inner['id'], subject=task.subject, inner=inner['built'],
                                                    body=LG.show(inner['body'], F.names())))
            meanings = self._meanings(kept, task.form, signs, new) if credited else ()
            if attributed:                                 # a proof it cannot attribute leaves nothing (S14 F1)
                F.understand(kind, ctx, kept,
                             self._hparts(kept, task.form) + tuple(m for m in meanings if m[0] == 'concept'),
                             credited, 1.0 if credited else 0.3, task.name)
            if credited and kept != law and not ONE_FIELD:   # its own formula: a curve was proven, not it - kept as
                F.keep_possibility(kind, None, law, law, ctx, task.name, 'a curve of it proven',   # an idea, without
                                   math.exp(min(phi.get(law, 0.0), 0.0)))                          # standing
            if ONE_FIELD:                                  # what the proof lays in (One Field: the one writer)
                proof = self._proof_amounts(task, law, kept, new, credited)
                if getattr(self, '_ring_observer', None) is not None:
                    self._ring_observer['credited_object'] = dict(
                        credited=bool(credited), source=law, kept=kept,
                        family=proven.get('family'), throws=proven.get('n'),
                        certificate_digest=getattr(proven.get('cert'), 'digest', None),
                        certified=rec.get('certified', []), amounts=[dict(identity=k, amount=a)
                                                                  for k, a in proof.items()])
            if task.words and credited:
                F.lexicon.hear(task.words, meanings)
            rec['said'] = (F.lexicon.say([('concept', new['all'])] if 'all' in new else meanings)   # its name for it
                           if credited else [])
            if task.form == 'exact' and credited and not ONE_FIELD:   # what it may believe is laid into the things
                self._bind_proven(task, law, new)          # (S05 F1; S06 F8: its own proof alone, a teacher's word
                #                                            when taught - never the hidden grade when alone)
            if credited and hasattr(task, 'sentences') and rec['said'] and task.form == 'exact':   # what its proven
                for x, y in task.data:                                                 # is, to it, a thing that
                    if isinstance(y, int) and not isinstance(y, bool):                 # ability gives: a role in the
                        self._ideas().role(y, rec['said'][0])                          # thing's idea
            own = set(F.lexicon.coined.values())
            rec['false_words'] = [w for w in rec['said'] if w not in own and not task.teacher_truth(w)]
            origin = extra.get(law)
            if credited and origin is not None and origin[0] in ('recalled', 'composed'):   # serendipity: from
                rec['serendipity'] = dict(origin=origin[0], source=str(origin[1]))              # elsewhere
                F.links.append(dict(task=task.name, origin=origin[0], source=str(origin[1]), at=F.tasks))
            method = st['origins'].get(law)
            if credited and method is not None:            # its imagination found the proven idea: that method
                rec['imagined_by'] = dict(method='+'.join(method), moves='+'.join(F.methods.expand(method)),
                                          origin=origin[0] if origin else None)
                nid = F.methods.name(method, task.name)    # becomes one of its own (once)
                if nid is not None:
                    rec['method_named'] = dict(id=nid, moves=' then '.join(F.methods.expand(method)))
            if len(order) > 1:
                r = order[1]
                if logE.get(law, -math.inf) - logE.get(r, -math.inf) < 2.0 and \
                        not (set(self._hparts(law, task.form)) & set(self._hparts(r, task.form))
                             - {('input', 'position'), ('input', 'speed'), ('input', 'time')}):
                    rec['duality'] = dict(other=repr(r)[:200])
                    F.wonder(task.name, 'duality', 'Two different ideas both explain this; where do they part?',
                             other=repr(r)[:200])
        else:
            rec.update(claim=None, verdict='not proven')
            if leader is not None:
                F.understand(kind, ctx, leader, self._hparts(leader, task.form), False, 0.3, task.name)
            for part, nats in st['footholds'].items():      # the snowball across worlds: what was right, unproven,
                kept = self._as_drawn(task, part, concepts, mu, st)       # kept as a tentative idea for elsewhere
                if kept is not None:
                    if ONE_FIELD:
                        held.append(((kept,), min(1.0, nats / 100)))
                    else:
                        F.keep_possibility(kind, None, (kept,), (kept,), ctx, task.name, 'foothold',
                                           min(1.0, nats / 100))
                    rec.setdefault('tentative', []).append(repr(kept)[:120])
        if ONE_FIELD:                                      # one writer: the world's proof and beliefs, into its things
            if not attributed and proven is not None:
                st['unattributed'] = proven['law']
            if task.form == 'strengths':
                rec['support'] = [dict(source=repr(law), throws=data[0], digest=data[1], family=repr(family),
                                       representation=repr(kept), supports_source=kept == law,
                                       attributed=law != st.get('unattributed'))
                                  for (law, data, family), kept in st.get('support', {}).items()]
            self._lay_in_world(task, ctx, st, order, phi, proof, held)
        else:
            for h in order[1:6]:                           # what it set aside, kept for elsewhere
                if phi.get(h, -math.inf) > math.log(0.02):
                    F.keep_possibility(kind, None, h, h, ctx, task.name, 'set aside', math.exp(phi[h]))
        F.loop.end_task(kind)
        F.methods.end_task()
        self._stepfield().end_task()
        end_wall, end_cpu = time.time(), time.process_time()
        rec['thinking_wall'] = round(finish_wall - t0, 1)
        rec['thinking_cpu'] = round(finish_cpu - c0, 1)
        rec['timing']['finish'] = round(end_wall - finish_wall, 2)
        rec['finish_cpu'] = round(end_cpu - finish_cpu, 2)
        rec['wall'], rec['cpu'] = round(end_wall - t0, 1), round(end_cpu - c0, 1)
        total_gain = sum(max(c.get('gain', 0.0), 0.0) for c in choices) + (
            PH.V_DONE if proven and (answer_channel is None or course_credit) else 0.0)
        F.rates.append(total_gain / max(end_cpu - c0, 1.0))
        F.off_choice_rates.append(total_gain / max(off_choice_cpu, 1.0))
        del F.rates[:-50]
        del F.off_choice_rates[:-50]
        rec['gain_rate'] = F.rates[-1]
        rec['choice_rate_basis'] = 'total_cpu' if ONE_FIELD else 'legacy_thinking_cpu'
        F.tasks += 1
        rec['say'] = say
        rec['configs'] = ['+'.join(c['config']) for c in choices]
        F.log.append({k: rec[k] for k in ('task', 'subject', 'kind', 'proven', 'verdict', 'steps', 'invented',
                                           'reused', 'serendipity', 'duality', 'wall')})
        del F.log[:-2000]
        observer = getattr(self, '_ring_observer', None)
        if observer is not None:
            observer.update(proven=rec['proven'], verdict=rec['verdict'], costs=dict(
                phases=dict(rec['timing']), wall=rec['wall'], cpu=rec['cpu'],
                thinking_wall=rec['thinking_wall'], thinking_cpu=rec['thinking_cpu'],
                finish_cpu=rec['finish_cpu']), steps=rec['steps'])
            # Invention can rename an identity. Keep both names to join event-time and terminal credit.
            bodies = {c['id']: c['body'] for c in F.concepts}
            stable, content_cache = {}, {}
            items = observer['candidates'] + observer['selected'] + observer['events'] + observer['writes']
            items += (observer['credited_object'] or {}).get('amounts', [])
            for item in items:
                key = item['identity']
                item['terminal_identity'] = self._canonical_identity(key) if key is not None else None
                # IDs created independently in clones need not match. Content fingerprints join them.
                if key not in stable:
                    stable[key] = self._ring_content(key, bodies, content_cache)
                item['content_identity'] = stable[key]
            for item in observer['selected']:
                events = [e for e in observer['events'] if e['content_identity'] == item['content_identity']]
                item['proof_attempts'] = sum(e['event'] == 'attempted' for e in events)
                item['accepted'] = any(e['event'] == 'judge_result' and e.get('accepted') for e in events)
                item['refutations'] = [e['reason'] for e in events if e['event'] == 'refuted']
                writes = [w for w in observer['writes'] if w['content_identity'] == item['content_identity']]
                item['terminal_amount'] = sum(w['amount'] for w in writes)
                item['written'] = bool(writes)
            observer = _ring_safe(observer)
            rec['ring_observer'] = observer
            if self._ring_log_path is not None:
                import json
                with open(self._ring_log_path, 'a', encoding='utf-8') as stream:
                    stream.write(json.dumps(observer, allow_nan=False) + '\n')
            self._ring_observer = None
            self._ring_selected = {}
        return rec

    def _observe_ring(self, task, event, law, **data):
        observer = getattr(self, '_ring_observer', None)
        if observer is not None:
            key = self._idea_key(task, law)
            observer['events'].append(dict(event=event, identity=key, identity_repr=repr(key), **data))

    @staticmethod
    def _ring_content(key, bodies, memo=None):
        """Observer identity across clones with different newly allocated concept IDs; no decoder reads this."""
        import hashlib
        memo = {} if memo is None else memo

        def digest(e):
            return hashlib.sha256(repr(e).encode('utf-8')).hexdigest()

        def concept(cid, visiting):
            if cid not in bodies or cid in visiting:
                return ('unresolved_concept', cid)
            if cid not in memo:
                memo[cid] = digest(body(bodies[cid], visiting + (cid,)))
            return memo[cid]

        def body(e, visiting=()):
            # Hash shared dependencies once; do not expand a repeated/composed concept exponentially.
            payload = concept(e[1], visiting) if e[0] == 'c' else e[1]
            return (e[0], payload, *(body(child, visiting) for child in e[2:]))

        if key is None:
            return None
        kind, ref = key
        if kind == 'concept':
            return ('body', concept(ref, ())) if ref in bodies else key
        if kind != 'idea' or not isinstance(ref, tuple):
            return key
        if not ref or isinstance(ref[0], tuple):
            parts = []
            for ch, form, value in ref:
                if form == 'concept' and value in bodies:
                    form, value = 'body', concept(value, ())
                elif form == 'expr':
                    form, value = 'body', digest(body(_subst(value, 's', '_')))
                parts.append((ch, form, value))
            return ('law', tuple(sorted(parts, key=repr)))
        return ('body', digest(body(ref)))

    def _what_is_mass(self, task, fit):
        """'Mass should not stay only mass' (the author): once a law is proven, it asks what the masses it measured are -
        how many kinds there are here, told apart by their own uncertainty (two masses are one kind when they differ by
        less than 3 standard deviations of their difference). It keeps the answer across worlds, so a pattern (things
        coming in a few kinds) can show. Returns its finding, or None."""
        order = list(fit.order)
        if len(order) < 3 or getattr(fit, 'cov', None) is None:
            return None
        nc = len(fit.coef)
        mus = np.array([fit.mu[s] for s in order], float)
        var = np.array([fit.cov[nc + i, nc + i] for i in range(len(order))], float)
        if not (np.all(np.isfinite(mus)) and np.all(mus > 0) and np.all(np.isfinite(var)) and np.all(var >= 0)):
            return None
        m, sm = 1.0 / mus, np.sqrt(var) / mus ** 2                  # a mass and its standard deviation
        idx = np.argsort(m)
        kinds, cur = [], [idx[0]]
        for a, b in zip(idx[:-1], idx[1:]):
            if abs(m[b] - m[a]) < 3.0 * math.hypot(sm[a], sm[b]):
                cur.append(b)
            else:
                kinds.append(cur)
                cur = [b]
        kinds.append(cur)
        found = dict(things=len(order), kinds=len(kinds),
                     masses=[round(float(np.mean(m[k])), 3) for k in kinds])
        F = self.field
        if not hasattr(F, 'masses_seen'):
            F.masses_seen = []
        F.masses_seen.append(dict(task=task.name, **found))
        if len(kinds) < len(order):
            text = (f"The {len(order)} things here have only {len(kinds)} kinds of mass "
                    f"({', '.join(f'{v:g}' for v in found['masses'])}). Why so few? What makes a mass?")
        else:
            text = f"The {len(order)} things here all have different masses."
        unit = self._unit_of(m, sm, kinds)                # deeper still: are the kinds whole multiples of one mass?
        if unit is not None:
            found['unit'] = round(unit[0], 3)
            found['multiples'] = unit[1]
            text += (f" They are {', '.join(str(n) for n in unit[1])} times one mass ({unit[0]:.3g}): maybe things are made"
                     f" of equal units.")
        worlds = [w for w in F.masses_seen if w['kinds'] < w['things']]
        if len(F.masses_seen) >= 3 and len(worlds) == len(F.masses_seen):
            text += (f" In all {len(worlds)} worlds I measured so far, things came in fewer kinds of mass than there"
                     f" were things.")
        F.wonder(task.name, 'mass', text, **found)
        return dict(text=text, **found)

    @staticmethod
    def _unit_of(m, sm, kinds, top=6):
        """A mass u of which every kind is a whole multiple (at most `top` times), each within 3 standard deviations,
        with at least three kinds (two alone always fit some unit): (u, the multiples), or None."""
        if len(kinds) < 3:
            return None
        means = [float(np.mean(m[k])) for k in kinds]
        sds = [float(np.sqrt(np.sum(sm[k] ** 2)) / len(k)) for k in kinds]
        for n0 in range(1, top + 1):
            u = means[0] / n0
            ns = [int(round(v / u)) for v in means]
            if all(1 <= n <= top for n in ns) and all(abs(v - n * u) <= 3.0 * s + 1e-9
                                                      for v, n, s in zip(means, ns, sds)):
                u = float(sum(v for v in means) / sum(ns))      # the unit that fits them all best
                return u, ns
        return None

    def _used(self, cid, rec):
        for c in self.field.concepts:
            if c['id'] == cid:
                c['uses'] += 1
        rec['reused'].append(cid)

    @staticmethod
    def _signs(family, fit):
        """Which way each part pushes (back, along) at its best fit, by input: the sign of force times input, averaged."""
        out = {}
        s = np.linspace(0.2, 2.0, 10)
        for term in family:
            sl = grammar.coef_slice(family, term)
            c = np.asarray(fit.coef[sl], float)
            ch = term[1] if term[0] in ('cell', 'shape') else None
            if ch is None or TS.base(ch) == 'time' or grammar.is_dim(ch):   # a dimension's sign is its coordinate's
                continue                                   # convention, not a direction of the push (S11b F4, reviewer)
            if term[0] == 'cell':
                vals = TS.hats(ch, s, term[2]) @ c
            else:
                vals = (TS.hats(ch, s, term[2]) @ np.asarray(term[4])) * float(c[0])
            m = float(np.mean(vals * np.sign(s)))
            out[TS.base(ch)] = -1 if m < 0 else 1 if m > 0 else 0          # by input (a lens is its input)
        return out

    def _said_as(self, part, channel, concepts):
        """Is `channel` what this part itself is said as: its own input or lens, or the dimension its own expression
        expands to (the program's tokens; its range may differ with the readings)?"""
        ch, kind, ref = part
        if channel == ch:
            return True
        if not grammar.is_dim(channel) or kind not in ('expr', 'concept') or TS.DIM_TOKEN.get(ch) is None:
            return False
        e = ref if kind == 'expr' else LG.node('c', LG.node('var', payload='s'), payload=ref)
        toks = TS._dim_program(e, {'s': (TS.DIM_TOKEN[ch],), '_': (TS.DIM_TOKEN[ch],)}, concepts)
        return toks is not None and tuple(toks) == grammar.dim(channel)[0]

    def _certified(self, law, credit, family=None, concepts=None):
        """What a physics proof certified, part by part (the honesty fix, 2026-10-01; review 11, S11b): (the law it keeps,
        how each part was proven), or (None, how) when a part cannot be attributed - then it keeps nothing (S11b F5).
        A part sent as a free cell is kept as that curve: on its input, or on the dimension its expression was said
        as (the dimension stays only itself, a coordinate: its expression's parts are not made familiar, S11b F1). A
        part sent as a registered shape is the drawing of the concept that owns the shape the judge saw (S11b F2).
        Neither certifies SERA's formula (1 + x^3 is accepted where x^3 is), so no formula is kept as proven."""
        if credit is None or len(credit) != len(law):
            return None, []
        if family is not None and grammar.canonical(tuple(t for t, _ in credit)) != grammar.canonical(family):
            return None, []                                # the credit is not what the judge accepted (S14 F1)
        concepts = self._concepts() if concepts is None else concepts
        kept, how = [], []
        for i, (part, (t, proved)) in enumerate(zip(law, credit)):
            ch = part[0]
            if proved == 'curve':
                if t[0] != 'cell' or not self._said_as(part, t[1], concepts):
                    return None, how
                kept.append((t[1], 'curve', int(t[2])))
                how.append({'part': i, 'as': proved, 'on': t[1]})
                continue
            if proved == 'formula':                        # Decision 16: its own ramp accepted - one strength
                if not (grammar.is_ramp(t) and part[1] in ('expr', 'concept')      # times exactly this expression -
                        and self._said_as(part, t[1], concepts)):                  # its own (S14 F1)
                    return None, how
                kept.append(part)
                how.append({'part': i, 'as': proved, 'on': t[1]})
                continue
            owner = next((c['id'] for c in self.field.concepts
                          for s in (c.get('shapes') or ([c['shape']] if c.get('shape') is not None else []))
                          if s == t), None)            # the whole shape the judge saw (S14 F1)
            if proved != 'drawing' or owner is None:
                return None, how
            kept.append((ch, 'concept', owner))
            how.append({'part': i, 'as': proved, 'on': t[1], 'shape': int(t[3]), 'concept': owner})
        return tuple(kept), how

    def _invent_part(self, task, part, family, fit, concepts, ctx, proof=None):
        """A part of a proven law that was not yet a concept becomes one: an expression as it is; a free curve as the
        table of its fitted values, composed with its coordinate when that uses one input. It also becomes a shape
        the judge may use in later worlds (its library)."""
        F = self.field
        ch, kind, ref = part
        extra = dict(input=ch, context=list(map(float, ctx)))
        if kind == 'expr':
            knots = task.part_knots(part, concepts)
            if knots is None or ref[0] in ('one',):
                return None
            body = _subst(ref, 's', '_')
        else:
            cells = [t for t in family if t[0] == 'cell' and t[1] == ch]
            if not cells:
                return None
            sl = grammar.coef_slice(family, cells[0])
            c = np.asarray(fit.coef[sl], float)
            grid = TS.grid(ch, cells[0][2])
            dim = grammar.dim(ch)[0] if grammar.is_dim(ch) else ()
            if len(dim) > 1:
                inputs = [inp for inp, tok in TS.DIM_TOKEN.items() if tok in dim]
                if len(inputs) != 1:                       # a mixed coordinate is not a function of one number
                    return None
                stack = []                                # the expanded postfix program from TS._dim_program
                for tok in dim:
                    if tok == TS.DIM_TOKEN[inputs[0]]:
                        stack.append(LG.node('var', payload='_'))
                    elif tok in ('0', '1'):
                        stack.append(LG.node('zero' if tok == '0' else 'one'))
                    elif tok in TS.DIM_OPS.values():
                        if len(stack) < 2:
                            return None
                        b, a = stack.pop(), stack.pop()
                        stack.append(LG.node(tok, a, b))
                    else:
                        return None                       # only the arithmetic _dim_program can say
                if len(stack) != 1:
                    return None
                # Keep the actual fitted cell, including its scale and clamping, applied to e(input).
                body = LG.node('tab', stack[0], payload=(tuple(float(g) for g in grid), tuple(float(v) for v in c)))
                extra.update(argument_input=inputs[0], certified='curve')
            else:
                g33 = TS.grid(ch)                          # plain input tables, including dim:x, stay as before
                vals = np.interp(g33, grid, c)
                m = float(np.max(np.abs(vals)))
                if not m > 1e-9:
                    return None
                knots = tuple(float(v) for v in vals / m)
                body = LG.node('tab', payload=(tuple(float(g) for g in g33), knots))
        if proof is not None:
            extra['proof'] = proof
        c = F.invent(body, ('num', 'num'), 'physics', task.name, self._hparts((part,), 'strengths'), extra=extra)
        self._register(c)
        return c

    def _register(self, c):
        """A concept that is a function of a number is drawn on every measured input's grid and registered in the
        judge's library of its shapes (Decision 12), in order: from the next world on it can be claimed there with one
        strength (a square learned from numbers can shape a force)."""
        if tuple(c['sig']) != ('num', 'num'):
            return
        F = self.field
        table = F.concept_table()
        shapes = []
        for ch in self._channels():                     # its inputs and its lenses (Decision 14)
            knots = TS.draw_knots((ch, 'concept', c['id']), table)
            if knots is None or np.ptp(knots) < 1e-9:
                continue
            shapes.append(grammar.shape_term(ch, TS.K_PART, len(F.shapes()) + len(shapes) + 1, knots))
        c['shapes'] = shapes


CR.set_knobs(globals())          # SERA_KNOBS=NAME=value,...: a knob set for an A/B (sera/crutches.py)
