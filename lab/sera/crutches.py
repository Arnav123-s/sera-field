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
    'course_worked_steps': dict(
        what='teacher-side intermediate values in composed course lessons; off: identical lessons without them',
        where='scripts/sera_course.py composed, sera/tasks.py Exact.worked', commit='S27', status='taught',
        course_only=True,
        question='does fading worked-step evidence improve transfer to untaught compositions?'),
    'course_told_wrong': dict(
        what='course test2 verdicts reach answer-kind reliability; refutations still reach standing when off',
        where='sera/one.py course_verdict, scripts/sera_course.py', commit='S27', status='taught', course_only=True,
        question='does verdict-only practice reduce confident wrong answers without losing coverage?'),
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
                                    if include_course or not REGISTRY[name].get('course_only')},
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
