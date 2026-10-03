"""The crutch ledger (plan Phase 3.3, 2026-10-01): every mechanism SERA did not learn, named, with a switch.

The author (2026-09-29): crutches first, then taught, then superposed, then its own; every crutch registered, taught,
superposed and removable, and reported as learned or fixed. A crutch here is a mechanism we coded into SERA's mind
after watching it fail; the fixed numbers (knobs) at the top of sera/one.py are the other kind, listed by
scripts/crutch_ledger.py from the code itself.

Switches, for an A/B without code edits:
  SERA_CRUTCH_OFF=name,name     those mechanisms off: SERA as it was before each was added
  SERA_CRUTCH_ON=teach_rechecking  opt in to S24's observation/teacher seam (default off)
  SERA_KNOBS=NAME=value,...     a knob of sera/one.py set to another value (e.g. BACK_ON=0, REFUTE_ECHO=0.5)
No switch or knob overrides is SERA exactly as before S24.
"""
import os
import math
import sys

# name -> what it does, where it lives, the commit that added it, how SERA has it (fixed: coded by us; taught: a
# teacher's way that fades; learned: its own), and the open question about it.
REGISTRY = {
    'own_operations': dict(what='own typed macros from repeated wishes, checked execution and exact substitution',
        where='sera_u/roadmap.py', commit='U13', status='learned', default_on=False, report_default=False,
        question='does changing the search basis reduce later composition cost?'),
    'rederive_concepts': dict(what='primitives-only reconstruction from own values, fresh audits, original preserved',
        where='sera_u/roadmap.py', commit='U13', status='learned', default_on=False, report_default=False,
        question='does an independently rebuilt concept compose better?'),
    'rough_estimates': dict(what='Field pre-act signed order estimates; calibration-earned learned candidate pruning',
        where='sera_u/roadmap.py', commit='U13', status='learned', default_on=False, report_default=False,
        question='do calibrated estimates help with unpruned fallback and recorded mistakes?'),
    'world_hologram': dict(what='Field-chosen U12 acquired-world habit: world_hologram',
        where='sera_u/darwin.py', commit='U12', status='learned', default_on=False, report_default=False,
        question='does this removable habit repay time on untaught lineage specimens?'),
    'patient_observation': dict(what='Field-chosen U12 acquired-world habit: patient_observation',
        where='sera_u/darwin.py', commit='U12', status='learned', default_on=False, report_default=False,
        question='does this removable habit repay time on untaught lineage specimens?'),
    'lineage_trees': dict(what='Field-chosen U12 acquired-world habit: lineage_trees',
        where='sera_u/darwin.py', commit='U12', status='learned', default_on=False, report_default=False,
        question='does this removable habit repay time on untaught lineage specimens?'),
    'change_mechanisms': dict(what='Field-chosen U12 acquired-world habit: change_mechanisms',
        where='sera_u/darwin.py', commit='U12', status='learned', default_on=False, report_default=False,
        question='does this removable habit repay time on untaught lineage specimens?'),
    'deep_time': dict(what='Field-chosen U12 acquired-world habit: deep_time',
        where='sera_u/darwin.py', commit='U12', status='learned', default_on=False, report_default=False,
        question='does this removable habit repay time on untaught lineage specimens?'),
    'one_change_experiments': dict(what='Field-learned one-coordinate experiments beside rival splitting and surprise',
        where='sera_u/scientists.py', commit='U11', status='learned', default_on=False, report_default=False,
        question='does varying one observed input or push command help law certification?'),
    'gap_predictions': dict(what='own structural law families, search-language parameter patterns, prospective missing members',
        where='sera_u/scientists.py', commit='U11', status='learned', default_on=False, report_default=False,
        question='do regularities across acquired laws predict unseen members?'),
    'number_conjectures': dict(what='relations conjectured from own concept executions and independently Exact audited',
        where='sera_u/scientists.py; scripts/sera_u_scientists.py', commit='U11', status='learned', default_on=False,
        report_default=False, question='do sampled relations help? Only checked identical expansions count as exact rewrites.'),
    'conserved_quantities': dict(what='own-language state expressions, nontrivial sampled constancy, held-throw audits and principles',
        where='sera_u/scientists.py; scripts/sera_u_scientists.py', commit='U11', status='learned', default_on=False,
        report_default=False, question='does one fading demonstration lead to useful conserved quantities?'),
    'anomaly_pursuit': dict(what='standing cross-item anomalies with learned keep/release and delayed certification returns',
        where='sera_u/scientists.py', commit='U11', status='learned', default_on=False, report_default=False,
        question='when does persistent pursuit repay its measured cost?'),
    'thought_experiments': dict(what='acquired laws imagined at observed-input limits; paradox questions and targeted experiments',
        where='sera_u/einstein.py', commit='U10', status='learned', default_on=False, report_default=False,
        question='does learned use of imagination locate useful conflicts before world queries?'),
    'symmetry_principles': dict(what='acquired inverse concepts; empirical invariance support and fallible search priors',
        where='sera_u/einstein.py', commit='U10', status='learned', default_on=False, report_default=False,
        question='do empirical principles reduce later certification work?'),
    'doubt_assumptions': dict(what='shared-structure revision order; every affected certified scope must pass the unchanged judge',
        where='sera_u/einstein.py', commit='U10', status='learned', default_on=False, report_default=False,
        question='does revising shared parts first help? It is no guarantee.'),
    'bold_predictions': dict(what='pre-experiment unseen-input predictions; own confirmation credit and failure doubts',
        where='sera_u/einstein.py', commit='U10', status='learned', default_on=False, report_default=False,
        question='do prospective tests help retained laws and principles earn search credit?'),
    'open_worlds': dict(what='observer-owned worlds without assigned questions; bounded RSI discovery share',
        where='sera_u/discovery.py; scripts/sera_u_discovery.py', commit='U9', status='fixed',
        default_on=False, report_default=False, question='does autonomous search rediscover withheld laws?'),
    'own_questions': dict(what='Field return-trained questions from its own surprise and rival predictions',
        where='sera_u/discovery.py', commit='U9', status='learned', default_on=False, report_default=False,
        question='do self-posed public questions improve discoveries per second?'),
    'designed_experiments': dict(what='learned choice of rival-splitting, surprise or random experiments',
        where='sera_u/discovery.py; sera/design.py', commit='U9', status='learned',
        default_on=False, report_default=False, question='do designed inputs beat random inputs?'),
    'unification_credit': dict(what='learned weight on two-part compression across certified worlds',
        where='sera_u/discovery.py', commit='U9', status='learned', default_on=False, report_default=False,
        question='does compression credit encourage reusable explanations? It is not proof of truth.'),
    'hidden_quantities': dict(what='unnamed per-object scalar fitted from own experiments if it saves bits',
        where='sera_u/discovery.py; scripts/sera_u_discovery.py', commit='U9', status='learned',
        default_on=False, report_default=False, question='does one fading taught demonstration help infer quantities?'),
    'memory_choice': dict(
        what='Field-learned consult/remember layers, charged returns and delayed memory eligibility',
        where='sera/phi.py MemoryChoice; sera_u/memory.py Memory; sera_u/mind.py',
        commit='U8', status='learned', default_on=False, report_default=False,
        question='does choosing memory improve time to right beside always-on and no-memory?'),
    'taught_not_yet': dict(
        what='taught answer/continue faculty choice, next untried method or step, pending talk and revisits',
        where='sera/phi.py NotYetWays; sera_u/mind.py Engine', commit='U7', status='learned',
        default_on=False, report_default=False,
        question='does learned persistence improve time to right and later revisit solutions?'),
    'abstain_bar': dict(
        what='U3 fixed Bayes-risk decision formula over learned wrong and missed-right costs',
        where='sera/phi.py InnerJudge.decide; sera_u/mind.py Engine.reply', commit='U7', status='fixed',
        default_on=False, report_default=False, response="I don't know",
        question='how does the U3 bar compare with taught answer/continue?'),
    'judge_scrutiny': dict(
        what='bounded extra fresh probes and targeted throws after the unchanged proof gate',
        where='sera/tasks.py JudgeScrutiny, Exact.verify, Rail.verify; sera/one.py Sera._prove',
        commit='U4', status='fixed', default_on=False, report_default=False,
        question='do received counterexample regions and inner overconfidence catch additional wrong claims?'),
    'gap_syndromes': dict(
        what='eight own-state self-checks and a return-trained Field decoder over gap locations',
        where='sera_u/sleep.py Curiosity; sera_u/mind.py Engine', commit='U6', status='fixed',
        default_on=False, report_default=False,
        question='do fixed syndromes with learned check/path weights locate useful knowledge gaps?'),
    'aimed_dreams': dict(
        what='return-trained aimed/random dream budget share; starts at half, uses the same two interpreters',
        where='sera_u/sleep.py Sleep.dream', commit='U6', status='learned',
        default_on=False, report_default=False,
        question='does aiming at decoded gaps improve acquisition per charged second?'),
    'field_ways': dict(
        what='settled Field faculty return readouts with fading teacher evidence and Thompson uncertainty',
        where='sera/phi.py FieldWays; sera_u/mind.py Engine', commit='U3', status='learned',
        default_on=False, report_default=False, question='do taught Field ways improve gain per second?'),
    'field_methods': dict(
        what='three hypothetical branches driven by taught lab imagination methods and learned returns',
        where='sera/phi.py FieldMethods; sera_u/mind.py Engine', commit='U3', status='learned',
        default_on=False, report_default=False, question='which methods help in which Field context?'),
    'field_roadmap': dict(
        what='whole Field sketch, then one learned next step and a fresh hypothetical read',
        where='sera/phi.py FieldSteps; sera_u/mind.py Engine._roadmap', commit='U3', status='learned',
        default_on=False, report_default=False, question='does re-dreaming after one step beat ordered decomposition?'),
    'inner_judge': dict(
        what='verdict-trained Field probability, contrastive corrections and adaptive answer costs',
        where='sera/phi.py InnerJudge; sera_u/mind.py Engine', commit='U3', status='learned',
        default_on=False, report_default=False, question='does calibration preserve coverage while reducing wrong talk?'),
    'memory_layer_a': dict(
        what='CoreOwner observed fast/slow/bulk/marks/flow memory; off removes its retained read and write path',
        where='sera_u/memory.py; sera/phi.py Ideas.u_memory_switches', commit='U2', status='fixed',
        default_on=False, report_default=False,
        question='does native memory improve recall beside or without holographic memory?'),
    'memory_layer_b': dict(
        what='2048-dimensional Ideas ringing through a learned gated boundary projection and reciprocal A cue',
        where='sera_u/memory.py; sera/phi.py Ideas.u_memory_switches', commit='U2; S12; S18', status='fixed',
        default_on=False, report_default=False,
        question='does holographic recall improve transfer with an independent native-memory history?'),
    'field_understanding': dict(
        what='S18 contextual U and exact two-role standing, pooled with a checked neural familiarity readout',
        where='sera_u/memory.py; sera/phi.py Ideas.u_memory_switches', commit='U2; S18', status='fixed',
        default_on=False, report_default=False,
        question='does Field understanding improve proposal and hypothesis ranking over the legacy counts?'),
    'course_worked_steps': dict(
        what='teacher-side intermediate values in composed course lessons; off: identical lessons without them',
        where='scripts/sera_course.py composed, sera/tasks.py Exact.worked', commit='S27', status='taught',
        course_only=True,
        question='does fading worked-step evidence improve transfer to untaught compositions?'),
    'course_told_wrong': dict(
        what='course test2 verdicts reach answer-kind reliability; refutations still reach standing when off',
        where='sera/one.py course_verdict, scripts/sera_course.py', commit='S27', status='taught', course_only=True,
        question='does verdict-only practice reduce confident wrong answers without losing coverage?'),
    'field_proposer': dict(
        what='fresh CoreOwner typed production prior, bounded beam and 20/80 search scheduling',
        where='sera_u/proposer.py', commit='U1; CORE-022 c67ed27; S28 section 6', status='fixed',
        default_on=False, report_default=False,
        question='does checked training reduce search time against an independent no-proposer history?'),
    'program_dreams': dict(
        what='bounded executable compositions checked by two interpreters; dream scope only',
        where='sera_u/sleep.py', commit='U1; S28 section 2', status='fixed',
        default_on=False, report_default=False,
        question='do executable dreams improve held-out acquisition versus matched wake replay?'),
    'sleep_library': dict(
        what='checked parameterized subexpressions through the existing inner ability mechanism',
        where='sera_u/sleep.py; sera/one.py _inner_ability', commit='U1; S28 section 2', status='fixed',
        default_on=False, report_default=False,
        question='does callable reuse beat expanded-body search at equal total cost?'),
    'field_input_ports': dict(
        what='allowlisted ordered raw public senses, stable token IDs, positions and missing masks',
        where='sera_u/ports.py; sera_u/proposer.py FieldOwner', commit='U1; S28 section 2', status='fixed',
        default_on=False, report_default=False,
        question='do ordered senses improve binding and permutation consistency over the native hash port?'),
    'teach_rechecking': dict(
        what='observable pushes since a judge report and fading teacher-only one-push/recheck advice; opt-in',
        where='sera/phi.py LoopField, sera/one.py Sera.teacher_way', commit='S24', status='taught',
        default_on=False, question='does its own evidence retain rechecking after teacher advice is masked?'),
    'lesson_words': dict(
        what="the words heard in a lesson are offered to SERA's search as words it can say (to answer 'is mary in "
             "the kitchen?' with yes or no). Built against our own warning: 'close to handing it the answer words'",
        where='sera/tasks.py Story.numbers', commit='86cf3e5', status='fixed',
        question="the author's decision: keep as a registered crutch, or teach positional lessons instead"),
    'convince_halving': dict(
        what='each push shown to the judge since its last report is worth half the one before (a fixed 0.5)',
        where="sera/one.py Sera.live, est['convince']", commit='140e36f', status='fixed',
        question='could SERA learn when showing the judge more stops paying?'),
    'nobody_said': dict(
        what="where nobody said an answer and it answered anyway, the idea that answered is moved away from the "
             "question's words",
        where='sera/one.py Sera._correct', commit='d85f30a', status='fixed',
        question="a teacher's silence as a lesson (fail and credit) rather than a coded rule?"),
    'talk_tally': dict(
        what="in a talk, it moves toward an idea only when that idea was right more often than not on that kind of "
             "question (a per-talk tally of right/asked)",
        where='sera/one.py Sera.converse, Sera._correct', commit='176de5a', status='fixed',
        question='the tally is a separate count, not Field state (plan 3.4)'),
    'leader_override': dict(
        what="when its leading idea fits no example and a lower one does, the lower one leads ('leader = "
             "fitting[0]')",
        where='sera/one.py Sera.live', commit='a291bd5', status='fixed',
        question='should fitting the examples weigh in Phi instead of overriding it?'),
    'teacher_none_fits': dict(
        what="the teacher shows a step (then a wish) when none of SERA's ideas fits and thinking bigger is no "
             "longer cheap (from level NOFIT_LEVEL)",
        where='sera/one.py Sera._none_fit_late', commit='e5666b4', status='taught',
        question="it fades as SERA's own way of working learns when to step"),
    'rail_cues': dict(
        what="a rail's situation as cues for the Field (with ONE_FIELD): its first perceived context in coarse buckets "
             "(correlations in half units, sizes in whole log units), weighed by how rare each is among the worlds",
        where='sera/one.py Sera._cues', commit='(plan 3.4)', status='fixed',
        question="its own senses should say what a rail's situation is; the buckets are ours (review 12 F7)"),
    'frame_identity': dict(
        what="a talk's kind of question (its recurring words) as one thing of the Field that holds each idea's signed "
             "record of being right (with ONE_FIELD; off: the per-talk tally)",
        where='sera/one.py Sera._reliable, Sera.converse', commit='(plan 3.4)', status='fixed',
        question='the frame is still formed per talk from words heard twice (review 12 F3)'),
    'way_back': dict(
        what='stuck, it imagines the last step back from the goal (the knob BACK_ON)',
        where='sera/one.py Sera._step', commit='cd5a9a7', status='fixed',
        question='an innate move; when to use it is its own (MethodField)'),
}


def _off():
    off = {n for n in os.environ.get('SERA_CRUTCH_OFF', '').split(',') if n}
    unknown = off - set(REGISTRY)
    if unknown:
        raise ValueError(f'SERA_CRUTCH_OFF names no crutch: {sorted(unknown)}')
    return off


def _on():
    names = {n for n in os.environ.get('SERA_CRUTCH_ON', '').split(',') if n}
    unknown = names - set(REGISTRY)
    if unknown:
        raise ValueError(f'SERA_CRUTCH_ON names no crutch: {sorted(unknown)}')
    return names


OFF = _off()
ON = _on()


def on(name):
    """Whether the crutch `name` is on (it must be registered)."""
    if name not in REGISTRY:
        raise KeyError(f'not a registered crutch: {name}')
    return name not in OFF and (REGISTRY[name].get('default_on', True) or name in ON)


def settings(include_course=False):
    """Raw switch provenance and the effective scalar constants, after runner overrides."""
    one = sys.modules.get('sera.one')
    phi = sys.modules.get('sera.phi')
    effective = {k: v for k, v in sorted(vars(one).items())
                 if k.isupper() and not k.startswith('_') and type(v) in (bool, int, float)} if one else {}
    return dict(crutches_off=sorted(OFF), crutches_on=sorted(ON),
                crutches_effective={name: on(name) for name in sorted(REGISTRY)
                                    if (include_course or not REGISTRY[name].get('course_only'))
                                    and (REGISTRY[name].get('report_default', True) or name in ON or name in OFF)},
                knobs=os.environ.get('SERA_KNOBS', ''), effective=effective,
                field_echo=getattr(phi, 'FIELD_ECHO', None),
                choice_rate_basis='total_cpu' if getattr(one, 'ONE_FIELD', False) else 'legacy_thinking_cpu')


def set_knobs(module_globals):
    """Set nonnegative scalar knobs atomically. Collections and malformed/nonfinite values are refused;
    MAX_WALL=inf remains a supported unbounded deadline. Return the names set in input order."""
    pending = {}
    for kv in os.environ.get('SERA_KNOBS', '').split(','):
        if not kv:
            continue
        name, sep, val = kv.partition('=')
        if not sep or not name.isupper() or name.startswith('_') or name not in module_globals:
            raise ValueError(f'SERA_KNOBS names no knob: {name}')
        old = module_globals[name]
        if type(old) not in (bool, int, float):
            raise ValueError(f'SERA_KNOBS supports scalar knobs only: {name}')
        if isinstance(old, bool):
            if val.lower() not in ('0', '1', 'false', 'true', 'off', 'on'):
                raise ValueError(f'SERA_KNOBS malformed boolean: {kv}')
            value = val.lower() in ('1', 'true', 'on')
        else:
            try:
                value = type(old)(val)
            except ValueError as exc:
                raise ValueError(f'SERA_KNOBS malformed value: {kv}') from exc
            if value < 0 or (isinstance(value, float) and not math.isfinite(value)
                             and not (name == 'MAX_WALL' and value == math.inf)):
                raise ValueError(f'SERA_KNOBS invalid value: {kv}')
        pending[name] = value
    module_globals.update(pending)
    return list(pending)
