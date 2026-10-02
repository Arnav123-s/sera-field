"""Why the general SERA did not find 'where is X' (1800 s, twice) while the seed-3 Field did (355 s). A diagnostic
of ours (not SERA living): the target program said in its own ideas, then its plain search at each growth level with
all its ideas, its language ideas only (and what they call), and no ideas.
  python trace_where.py FIELD.pkl [seconds per level] [last level] [all|language|none]"""
import pickle
import sys
import time

sys.path.insert(0, '.')
from sera import lang as LG, one as O, tasks as TS  # noqa: E402

path = sys.argv[1]
cap = float(sys.argv[2]) if len(sys.argv) > 2 else 600.0
top = int(sys.argv[3]) if len(sys.argv) > 3 else 6
which = sys.argv[4] if len(sys.argv) > 4 else 'all'
got = pickle.load(open(path, 'rb'))
field = got['field'] if isinstance(got, dict) else got
TS.adopt(getattr(field, 'vocab', None) or {})
s = O.Sera(3, field)
task = TS.lesson_where(3)
allc = s._concepts()
names = field.names()
print('ideas', len(field.concepts), 'grown', sorted(getattr(field, 'grown', ())), flush=True)
for c in field.concepts:
    print('  ', c['id'], names[c['id']], c['subject'], c['sig'], LG.show(c['body'], names)[:70], flush=True)


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
while more:
    new = set()
    for k in more:
        new |= calls(byid[k]['body'], set()) - keep
    keep |= new
    more = new
langc = {k: v for k, v in allc.items() if k in keep}
langc['_sig'] = {k: v for k, v in allc['_sig'].items() if k in keep}
print('language ideas (and what they call):', sorted(keep), flush=True)

G = LG.node('var', payload='g')
E = LG.node('var', payload='e')
g0 = task.probes()[0]['g']
sent = g0[1]
lasts = [k for k, sig in allc['_sig'].items() if tuple(sig) == ('list', 'num')
         and LG.safe(LG.node('c', LG.node('var', payload='x'), payload=k), {'x': sent}, allc) == sent[-1]]
print('its ideas that give the last of a list:', [(k, names[k]) for k in lasts], flush=True)


def plain_last(x):
    return LG.node('foldn', LG.node('lam', E, payload='ae'), LG.node('zero'), x)


for label, last in [('plain', plain_last)] + [(names[k], (lambda x, k=k: LG.node('c', x, payload=k))) for k in lasts]:
    t = last(LG.node('head', LG.node('filter', LG.node('lam', LG.node('eq', LG.node('head', E), last(LG.node('head', G))),
                                                       payload='e'), G)))
    print(f'target with {label}: size {LG.size(t)}, fits the lesson: {task.consistent(t, allc)}, sees: {LG.sees(t)}',
          flush=True)

nums = task.numbers() if hasattr(task, 'numbers') else ()
for label, conc in [r for r in (('all', allc), ('language', langc), ('none', {'_sig': {}})) if r[0] == which]:
    for level in range(top + 1):
        LG.DEADLINE[0] = time.time() + cap
        t0 = time.time()
        found = LG.search(task.inputs, task.out, task.probes(), O.exact_size(level), conc,
                          lambda_size=O.lambda_size(level), constants=nums, values=True,
                          work=LG.MAX_WORK * 2 ** level, if_part=O.if_part(level), sees=O.seeing_size(level))
        done = LG.COMPLETE[0]
        fits = [e for e, _, _ in found if task.consistent(e, conc)]
        print(f'{label} | level {level} (size {O.exact_size(level)}, seeing body {O.seeing_size(level)}): '
              f'{len(found)} programs, {len(fits)} fit, complete {done}, {time.time() - t0:.0f} s', flush=True)
        if fits:
            print('   first fit:', LG.show(fits[0], names)[:120], flush=True)
            break
LG.DEADLINE[0] = float('inf')
print('TRACE DONE', flush=True)
