"""Does SERA's own step move find 'where is X' with the teacher's worked steps (who it is about, their sentence), on
the general SERA's Field? A diagnostic of ours: its _step on lesson_where, teaching, at growth level 3, with all its
ideas or its language ideas only (the others masked).
  python trace_step.py FIELD.pkl [all|language] [box seconds] [level]"""
import pickle
import sys
import time

sys.path.insert(0, '.')
from sera import lang as LG, one as O, tasks as TS  # noqa: E402

path = sys.argv[1]
which = sys.argv[2] if len(sys.argv) > 2 else 'all'
box = float(sys.argv[3]) if len(sys.argv) > 3 else 1800.0
level = int(sys.argv[4]) if len(sys.argv) > 4 else 3
got = pickle.load(open(path, 'rb'))
field = got['field'] if isinstance(got, dict) else got
TS.adopt(getattr(field, 'vocab', None) or {})
s = O.Sera(3, field)
task = TS.lesson_where(3)
def calls(p, out):
    if p[0] == 'c':
        out.add(p[1])
    for k in p[2:]:
        if isinstance(k, tuple):
            calls(k, out)
    return out


byid = {c['id']: c for c in field.concepts}
keep = {c['id'] for c in field.concepts if c['subject'] == 'language'}
more = set(keep)
while more:                                   # and what the language ideas call
    new = set()
    for k in more:
        new |= calls(byid[k]['body'], set()) - keep
    keep |= new
    more = new
other = [c['id'] for c in field.concepts if c['id'] not in keep]
masked = other if which == 'language' else ()
concepts = s._concepts(masked=masked)
print('ideas used', len([k for k in concepts if k != '_sig']), 'masked', len(masked), 'sees', s._sees(), flush=True)
s._level = level
if not hasattr(s, '_open_steps'):
    s._open_steps = []


def speak(kind, text, **kw):
    print(f'  [{kind}] {text}', flush=True)


LG.DEADLINE[0] = time.time() + box
t0 = time.time()
out = s._step(task, concepts, speak, set(), {'steps': 0, 'teaching': True})
LG.DEADLINE[0] = float('inf')
print(f'{which}: {len(out)} answers in {time.time() - t0:.0f} s', flush=True)
for prog, origin in out:
    print('   ', LG.show(prog, field.names())[:120], origin, 'fits:', task.consistent(prog, concepts), flush=True)
print('STEP TRACE DONE', flush=True)
