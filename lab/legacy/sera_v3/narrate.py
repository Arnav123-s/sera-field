"""SERA says what it finds while it works (plan revision 5, WP1; the author's end goal: "it says each finding out loud as
it goes"). Each live sentence is a kind plus the numbers it asserts; the words are rendered from the numbers alone,
as in sera.express, and at the world's end `check` re-derives every number from the mind's own records (its
certificate calls, discoveries, stopping decision, the words it heard). A sentence that fails is a false sentence:
the life's tripwire halts on it.
"""
from ccops5.core import grammar


def render(kind, n):
    nm = grammar.name
    if kind == 'first guess':
        return f"My first guess is {nm(n['law'])} ({100 * n['p']:.0f}% of my belief)."
    if kind == 'heard':
        return f"I heard \"{n['word']}\" ({n['slot']})."
    if kind == 'demo':
        return f"I was shown a push on object {n['object']}."
    if kind == 'leader':
        return f"Now I think it is {nm(n['law'])}."
    if kind == 'blocked':
        if n['block'] == 'band':
            return (f"I cannot yet rule out something else as large as {n['band']:.2g} (my tolerance is "
                    f"{n['eps']:g}).")
        if n['block'] in ('rival', 'screen'):
            return f"{nm(n['rival'])} is still within {n['short']:.1f} units of evidence of it."
        if n['block'] == 'misfit':
            return 'It misfits more objects than bumps explain: something else is here.'
        return 'An extra idea may be needed.'
    if kind == 'discover':
        if n['terms']:
            return ('Nothing I know fits, so I searched every piece I can imagine and will weigh '
                    + ', '.join(grammar.term_name(t) for t in n['terms']) + '.')
        return 'Nothing I know fits, and my search found no new piece to weigh.'
    if kind == 'sure':
        return f"I am sure: {nm(n['law'])}."
    if kind == 'submit':
        return f"Every check I can make passes for {nm(n['law'])}; I send it to the judge for the full proof."
    if kind == 'investigate':
        return (f"My answer {nm(n['law'])} is proven to within {n['eps']:g} wherever I looked, but {nm(n['rival'])} "
                f"agrees with it to {n['gap']:.2g} there. I come back to find out which one is right.")
    if kind == 'second look':
        if n['terms']:
            return ('I come back to this world: the judge found a law I had not weighed, so now I also weigh '
                    + ', '.join(grammar.term_name(t) for t in n['terms']) + '.')
        return 'I come back to this world: the judge could not rule out a law I already weigh.'
    if kind == 'judged':
        if n['proven']:
            return (f"The judge proved {nm(n['law'])} from world {n['world']}: it ruled out every other law it knows, "
                    f"and the checker agreed.")
        return f"The judge did not accept {nm(n['law'])} from world {n['world']}: {n['why']}."
    if kind == 'stop':
        if n['reason'] == 'proven':
            return f"I am done after {n['own']} of my own pushes: it is proven."
        why = {'no progress': 'the proof stopped coming closer', 'too slow': 'at this pace I would run out of pushes',
               'stuck': 'nothing changed in my last pushes', 'budget': 'I used every push I had',
               'cap: pushes': 'I reached the safety limit on pushes, unproven',
               'cap: wall time': 'I reached the safety limit on time, unproven'}[n['reason']]
        return f"I stop after {n['own']} of my own pushes: {why}."
    if kind == 'grow':
        if n['stage'] == 'formula':
            return (f"No law I can say fits, and the gap depends on {n['address']}: I grow new pieces there and weigh "
                    f"them.")
        return f"No piece I can name fits: I shape a free curve in {n['address']} from my own measurements."
    if kind == 'ask':
        return n['text']
    raise ValueError(kind)


def say(kind, at, **numbers):
    """A live sentence said after `at` own pushes in this world."""
    return dict(kind=kind, own=at, numbers=numbers, text=render(kind, numbers))


def judged_reason(res):
    """Why the office did not make a claim sure, in words, from its result."""
    cert = res['cert']
    if cert is None:
        return res['why']
    if not cert.accepted:
        return cert.reasons[0] if cert.reasons else 'refused'
    return f"the independent checker did not re-derive it ({res['why']})"


def check_judged(s, res, world, family):
    """(ok, why) for a 'judged' sentence against the office's result for the claim `family` of that world."""
    try:
        if s['text'] != render(s['kind'], s['numbers']):
            return False, 'the words do not say what the numbers say'
    except (KeyError, ValueError, TypeError):
        return False, 'the sentence cannot be rendered'
    n, cert = s['numbers'], res['cert']
    proven = bool(cert is not None and cert.accepted and res['verified'])
    ok = (n['world'] == world and bool(n['proven']) == proven and tuple(n['law']) == tuple(family) and
          (cert is None or tuple(cert.family) == tuple(family)) and (proven or n['why'] == judged_reason(res)))
    return ok, '' if ok else 'not what the judge decided'


def check(s, r):
    """(ok, why) for one live sentence against the mind's Report `r`."""
    try:
        if s['text'] != render(s['kind'], s['numbers']):
            return False, 'the words do not say what the numbers say'
    except (KeyError, ValueError, TypeError):
        return False, 'the sentence cannot be rendered'
    n, kind = s['numbers'], s['kind']
    if kind == 'first guess':
        top = r.proposals[0] if r.proposals else None
        ok = top is not None and tuple(top[0]) == tuple(n['law']) and abs(top[1] - n['p']) < 1e-9
        return ok, '' if ok else 'not its first guess'
    if kind == 'heard':
        ok = (n['slot'], n['word']) in [(sl, w) for sl, w in r.heard_words]
        return ok, '' if ok else 'it did not hear that'
    if kind == 'demo':
        ok = any(d['object'] == n['object'] for d in r.demos)
        return ok, '' if ok else 'no such demonstration'
    if kind == 'sure':
        ok = bool(r.sure) and tuple(r.claim) == tuple(n['law'])
        return ok, '' if ok else 'not what it was sure of'
    if kind == 'submit':
        ok = bool(getattr(r, 'submitted', False)) and tuple(r.claim) == tuple(n['law'])
        return ok, '' if ok else 'not what it submitted'
    if kind == 'investigate':
        sl = getattr(r, 'second_look', None)
        fam = lambda x: grammar.canonical(tuple(tuple(t) for t in x))
        ok = (sl is not None and sl.get('investigate') and sl.get('rival') and fam(sl['rival'][0]) == fam(n['rival'])
              and sl.get('gap') is not None and abs(sl['gap'] - n['gap']) <= 1e-9 * max(1.0, abs(n['gap'])))
        return bool(ok), '' if ok else 'not what it came back to investigate'
    if kind == 'second look':
        sl = getattr(r, 'second_look', None)
        ok = sl is not None and tuple(map(tuple, sl['terms'])) == tuple(map(tuple, n['terms']))
        return ok, '' if ok else 'not a second look at these terms'
    if kind == 'stop':                                  # any of its stops (growth searches may stop again)
        ok = any(st.get('reason') == n['reason'] and st.get('own') == n['own'] for st in (r.stops or [r.stop or {}]))
        return ok, '' if ok else 'not why it stopped'
    if kind == 'discover':
        ok = any(tuple(map(tuple, d['terms'])) == tuple(map(tuple, n['terms'])) and d['own'] == s['own']
                 for d in r.discoveries)
        return ok, '' if ok else 'no such search'
    if kind == 'blocked':
        calls = [c for c in r.calls if c['own'] == s['own']]
        if n['block'] == 'band':
            ok = any(c.get('band') is not None and abs(c['band'] - n['band']) <= 1e-9 * max(1.0, n['band'])
                     for c in calls)
            return ok, '' if ok else 'no such band'
        if n['block'] == 'misfit':
            ok = any('something else is here' in (c.get('reason') or '') for c in calls)
            return ok, '' if ok else 'no misfit refusal'
        ok = any(tuple(b['blocker'] or ()) == tuple(n.get('rival') or ()) for b in r.blocks if b['own'] == s['own'])
        return ok, '' if ok else 'not what blocked it'
    if kind == 'leader':
        ok = any(tuple(b['leader']) == tuple(n['law']) for b in r.blocks if b['own'] == s['own'])
        return ok, '' if ok else 'not its leader then'
    if kind == 'grow':                                  # rev 6: it grew where its growth report says the gap lives
        g = getattr(r, 'growth', None) or {}
        ok = n['address'] in (g.get('address'), g.get('address2')) and (
            n['stage'] == 'formula' or any(c.get('level') == 2 for c in (getattr(r, 'choices', None) or [])))
        return bool(ok), '' if ok else 'it did not grow there'
    if kind == 'ask':                                   # rev 6: it asked exactly this
        ok = any(a['text'] == n['text'] for a in (getattr(r, 'asked', None) or []))
        return ok, '' if ok else 'it did not ask that'
    return False, f'unknown kind {kind}'
