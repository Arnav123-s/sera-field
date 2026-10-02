"""SERA expresses itself (plan revision 2, P2c; the author: "it must be able to express itself", "prove it to us").

After a world, SERA says what it knows, how it knows it and what it does not know. Each sentence is a Statement: a
kind, the numbers it asserts, and the words.
- **The words are rendered from the numbers alone** (`render`).
- **`check`** re-renders the words and re-derives every number from the raw sources, so a sentence is verified the way
  a law is (independent review review Ex-2):
  - the ledger's evidence;
  - the certificate;
  - its committed predictions (foresight);
  - its grade (sera.grade).
- **A false sentence fails the check.**
- **It claims certainty only for a PROVEN law:** certified and confirmed by the independent checker. A certificate the
  checker did not confirm is reported as such (independent review Ex-1).

v1's words come from fixed patterns over its own records. Grounded, learned language (no pretrained model) comes at
B8, trained only on sentences this checker verified.
"""
import dataclasses
import math

import numpy as np

from ccops5.core import grammar

TOL = 1e-6
DISTURBED = 20.0                 # as sera.mind.DISTURBED
GRID_X, GRID_V = np.linspace(-3.0, 3.0, 61), np.linspace(-4.0, 4.0, 81)


@dataclasses.dataclass(frozen=True)
class Statement:
    kind: str
    numbers: dict
    text: str


def _close(a, b):
    a, b = float(a), float(b)
    if not (math.isfinite(a) and math.isfinite(b)):     # rev 5.1: the same infinity is the same number (a failed
        return a == b                                    # rival fit is -inf evidence; nan never matches)
    return abs(a - b) <= TOL * max(1.0, abs(a), abs(b))


def _disturbed(r):
    return sorted({k for k, e in (r.events or ()) if e == 'disturbed'})


def render(kind, n):
    """The words of a statement, from its numbers alone."""
    nm = grammar.name
    if kind == 'belief':
        if n['sure']:
            return (f"I am sure the force is {nm(n['law'])} where I looked (position {n['x0']:.2g} to {n['x1']:.2g}, "
                    f"speed {n['v0']:.2g} to {n['v1']:.2g}).")
        return f"My best guess is {nm(n['law'])}, but I am not sure."
    if kind == 'unverified':
        return (f"My judge accepted {nm(n['law'])}, but the independent checker did not confirm it, so I do not claim "
                f"it.")
    if kind == 'submitted':
        return (f"Every check I can make here passes for {nm(n['law'])}; the judge's full audit is still to come, so I "
                f"do not claim it yet.")
    if kind == 'unsure':
        return 'I am not sure because ' + '; '.join(n['reasons']) + '.'
    if kind == 'sureness':
        return (f"No other law I weighed comes closer than {n['evidence']:.1f} units of evidence (I needed "
                f"{n['needed']:.1f}); the closest was {nm(n['weakest'])}.")
    if kind == 'ruled_out':
        return f"I ruled out {nm(n['law'])}: it trails by {n['evidence']:.1f} units of evidence."
    if kind == 'still_possible':
        return (f"{nm(n['law'])} is still possible: it trails by only {n['evidence']:.1f} units (I need "
                f"{n['needed']:.1f}).")
    if kind == 'parting':
        a, b = nm(n['rival']), nm(n['law'])
        if n['worst_inside'] > n['eps']:                 # R5: only what was computed; no promise of what would settle it
            return (f"{a} and {b} differ by up to {n['worst_inside']:.2g} where I pushed, more than my tolerance "
                    f"{n['eps']:g}, but my throws have not yet told them apart.")
        if n['point'] is None:
            return (f"{a} and {b} agree within {n['eps']:g} everywhere I looked (position -3 to 3, speed -4 to 4); "
                    f"there they are one law to my senses.")
        return (f"{a} and {b} agree within {n['eps']:g} everywhere I pushed; they part only near position "
                f"{n['point'][0]:.2g}, speed {n['point'][1]:.2g}, which my pushes did not reach.")
    if kind == 'question':
        return (f"After the teacher's pushes {nm(n['law'])} was still possible; my own pushes gathered "
                f"{n['per_push']:.1f} units of evidence per push against it.")
    if kind == 'band':
        if not math.isfinite(n['band']):                 # rev 5.1 (Stage 1, teach-04): no bound is no size
            return (f"I cannot put any bound on something else acting here where I looked (my tolerance is "
                    f"{n['eps']:g}).")
        return (f"Anything else acting here is at most {n['band']:.2g} in size where I looked (my tolerance is "
                f"{n['eps']:g}).")
    if kind == 'foresight':
        return (f"Before each of my {n['pushes']} own pushes on undisturbed objects I said what would happen; my leading "
                f"law was off by {n['median']:.1f} times the sensor noise (median).")
    if kind == 'disturbed':
        return (f"Object {n['object']} is being knocked by something outside every law I weigh: my predictions for it "
                f"missed by at least {n['rms']:.0f} times the sensor noise, so I stopped pushing it.")
    if kind == 'imaginations':
        if n['gated']:
            return (f"I imagined {n['imagined']} laws at the start; {n['tested']} were weighed, but something else is "
                    f"here, so I do not grade them against each other.")
        return (f"I imagined {n['imagined']} laws at the start; {n['tested']} were weighed: {n['close']} are still "
                f"close, {n['refuted']} are ruled out.")
    if kind == 'assumption':
        return ('I assume the force depends only on position, speed and time, is the same law for every object, and '
                'that each object keeps its own mass.')
    if kind == 'rests_on':
        if 'premises' not in n:                         # a certificate from before the premise ledger (truth-v2)
            return ('My proof also rests on two things not yet proven: that my forecast before each throw is a proper '
                    'probability (I compute it by an approximation), and that my search found the best fit of each '
                    'rival law.')
        parts = [f"{PREMISE_WORDS[k]} ({'checked by tests, not proven' if s == 'measured' else 'assumed'})"
                 for k, s in n['premises']]
        if not parts:
            return 'My proof rests on nothing unproven.'
        return f"My proof also rests on {len(parts)} things not yet proven: " + '; '.join(parts) + '.'
    raise ValueError(kind)


PREMISE_WORDS = {'P': 'how I chose my pushes and my claim', 'M': 'my model of the noise and the knocks',
                 'N': 'my forecast before each throw being a proper probability',
                 'U': 'my search having found the best fit of each rival law',
                 'S': 'the true law being among the laws I checked',
                 'F': 'any force I missed having a shape my band can see',
                 'Q': "the band's approximation"}


def _rests(cert):
    """truth-v3: the certificate's premises that are measured or assumed (its premise ledger), or None when it has
    no ledger."""
    led = getattr(cert, 'premises', ()) or ()
    return [[k, s] for k, s, _ in led if s in ('measured', 'assumed')] if led else None


def _say(kind, numbers):
    return Statement(kind, numbers, render(kind, numbers))


def _force(ledger, family, X, V):
    from ccops5.core import paths
    fit = ledger.mle(family)
    kind, a, b = grammar.codes(family)
    T = grammar.tie(family)
    F = np.zeros_like(X)
    for c, k, aa, bb in zip(fit.coef if T is None else T @ fit.coef, kind, a, b):   # Decision 12: tied shapes
        F += c * np.vectorize(lambda x, v: paths.term(int(k), int(aa), int(bb), x, v, 1.0, 1.0))(X, V)
    return F


def _parting(r, law, rival):
    """(largest force gap inside the region its pushes reached, the nearest grid point outside it where the two
    fitted laws part by more than eps, or None)."""
    cert, ledger = r.certificate, r.ledger
    if any(t[0] == 'drive' for t in law + rival):
        return None
    X, V = np.meshgrid(GRID_X, GRID_V, indexing='ij')
    gap = np.abs(_force(ledger, law, X, V) - _force(ledger, rival, X, V))
    (x0, x1), (v0, v1) = cert.scope['x'], cert.scope['v']
    inside = (X >= x0) & (X <= x1) & (V >= v0) & (V <= v1)
    worst_in = float(gap[inside].max()) if inside.any() else 0.0
    far = (~inside) & (gap > cert.eps)
    if not far.any():
        return worst_in, None
    dx = np.maximum(np.maximum(x0 - X, X - x1), 0) / max(x1 - x0, 1e-9)
    dv = np.maximum(np.maximum(v0 - V, V - v1), 0) / max(v1 - v0, 1e-9)
    d = np.where(far, np.hypot(dx, dv), np.inf)
    i = np.unravel_index(int(np.argmin(d)), d.shape)
    return worst_in, (float(X[i]), float(V[i]))


def where_they_part(r, law, rival):
    """Why a look-alike is still possible, in the world's own terms: where the two fitted laws differ, against where
    its pushes reached. None when the ledger cannot fit them here."""
    if not hasattr(r.ledger, 'mle') or r.certificate.scope is None:
        return None
    got = _parting(r, law, rival)
    if got is None:
        return None
    return _say('parting', dict(law=law, rival=rival, worst_inside=got[0], point=got[1], eps=r.certificate.eps))


def self_report(r, g):
    """Statements about one lived world: r is the mind's Report (with foresight and q_start), g its Grade."""
    cert = r.certificate
    fam = grammar.canonical(cert.family)
    out = []
    sc = cert.scope or {}
    (x0, x1), (v0, v1) = sc.get('x', (math.nan, math.nan)), sc.get('v', (math.nan, math.nan))
    proven = g.proven == fam
    out.append(_say('belief', dict(law=fam, sure=proven, x0=x0, x1=x1, v0=v0, v1=v1)))
    if cert.accepted and not proven:                  # rev 5.1: a submitted claim waits for the office's full proof
        out.append(_say('submitted' if getattr(r, 'submitted', False) else 'unverified', dict(law=fam)))
    if not cert.accepted:
        out.append(_say('unsure', dict(reasons=tuple(cert.reasons))))
    thr = grammar.log_threshold(fam, cert.alpha)
    if proven and cert.rivals:
        weakest = min(cert.rivals, key=cert.rivals.get)
        out.append(_say('sureness', dict(weakest=weakest, evidence=cert.rivals[weakest], needed=thr)))
    for rival in sorted(cert.rivals, key=cert.rivals.get)[:3]:
        e = cert.rivals[rival]
        kind = 'ruled_out' if e >= thr else 'still_possible'
        out.append(_say(kind, dict(law=rival, evidence=e, needed=thr)))
        if kind == 'still_possible':
            part = where_they_part(r, fam, rival)
            if part is not None:
                out.append(part)
    for law, per in sorted(g.questions.items(), key=lambda kv: -kv[1])[:3]:
        out.append(_say('question', dict(law=law, per_push=per)))
    if cert.band is not None:
        out.append(_say('band', dict(band=cert.band, eps=cert.eps)))
    bad = _disturbed(r)
    fs = [f for f in (r.foresight or []) if f['situation'] not in bad]
    if fs:
        out.append(_say('foresight', dict(pushes=len(fs), median=float(np.median([f['leader_rms'] for f in fs])))))
    for k in bad:
        out.append(_say('disturbed', dict(object=k, rms=_knock_rms(r, k))))
    out.append(_say('imaginations', _imaginations(r, g)))
    out.append(_say('assumption', {}))
    rests = _rests(r.certificate)                   # research R3, truth-v3 premise ledger: the unproven premises
    out.append(_say('rests_on', {} if rests is None else {'premises': rests}))
    return out


def _knock_rms(r, k):
    """The push that showed object k is knocked: the first whose committed predictions ALL missed by more than
    DISTURBED sigmas (the mind's own rule); its smaller miss. None if there is no such push. (P2 gate L3-01: the
    minimum over all the object's pushes included earlier, well-predicted ones.)"""
    for f in r.foresight or ():
        m = min(f['leader_rms'], f.get('rival_rms', math.inf))
        if f['situation'] == k and m > DISTURBED:
            return m
    return None


def _imaginations(r, g):
    imagined = [grammar.canonical(f) for f, _ in (r.proposals or [])]
    tested = [f for f in imagined if g.graded(f)]
    if g.gated:                                   # independent review Ex-3: after an alarm nothing is graded against the rest
        return dict(imagined=len(imagined), tested=len(tested), close=None, refuted=None, gated=True)
    close = sum(1 for f in tested if g.credit(f) > 0 or f == g.leader)
    return dict(imagined=len(imagined), tested=len(tested), close=close, refuted=len(tested) - close, gated=False)


def check(s, r, g):
    """(ok, why): re-render the words, then re-derive every number from the raw records."""
    try:
        if s.text != render(s.kind, s.numbers):
            return False, 'the words do not say what the numbers say'
    except (KeyError, ValueError, TypeError):
        return False, 'the statement cannot be rendered'
    cert, n = r.certificate, s.numbers
    fam = grammar.canonical(cert.family)
    proven = g.proven == fam
    thr = grammar.log_threshold(fam, cert.alpha)
    if s.kind == 'belief':
        sc = cert.scope or {}
        ok = (n['law'] == fam and n['sure'] == proven and
              all(_close(n[k], v) for k, v in zip(('x0', 'x1'), sc.get('x', (math.nan,) * 2)) if not math.isnan(v)) and
              all(_close(n[k], v) for k, v in zip(('v0', 'v1'), sc.get('v', (math.nan,) * 2)) if not math.isnan(v)))
        return ok, '' if ok else 'belief does not match the proof'
    if s.kind == 'unverified':
        ok = n['law'] == fam and cert.accepted and not proven and not getattr(r, 'submitted', False)
        return ok, '' if ok else 'not an unconfirmed certificate'
    if s.kind == 'submitted':
        ok = n['law'] == fam and cert.accepted and not proven and bool(getattr(r, 'submitted', False))
        return ok, '' if ok else 'not a submitted claim'
    if s.kind == 'unsure':
        ok = not cert.accepted and tuple(n['reasons']) == tuple(cert.reasons)
        return ok, '' if ok else 'reasons do not match'
    if s.kind == 'sureness':
        weakest = min(cert.rivals, key=cert.rivals.get)
        ok = (proven and n['weakest'] == weakest and _close(n['evidence'], cert.rivals[weakest]) and
              _close(n['needed'], thr) and cert.rivals[weakest] >= thr)
        return ok, '' if ok else 'sureness does not match the rivals'
    if s.kind in ('ruled_out', 'still_possible'):
        e = cert.rivals.get(n['law'])
        ok = e is not None and _close(n['evidence'], e) and _close(n['needed'], thr) and ((e >= thr) == (s.kind == 'ruled_out'))
        return ok, '' if ok else 'rival evidence does not match'
    if s.kind == 'parting':
        got = _parting(r, n['law'], n['rival']) if hasattr(r.ledger, 'mle') else None
        ok = (got is not None and _close(n['eps'], cert.eps) and _close(n['worst_inside'], got[0]) and
              ((n['point'] is None and got[1] is None) or
               (n['point'] is not None and got[1] is not None and all(_close(a, b) for a, b in zip(n['point'], got[1])))))
        return ok, '' if ok else 'where the laws part does not match their fits'
    if s.kind == 'question':
        ok = n['law'] in g.questions and _close(n['per_push'], g.questions[n['law']])
        return ok, '' if ok else 'question credit does not match the grade'
    if s.kind == 'band':
        b, c = n['band'], cert.band
        same = c is not None and ((not math.isfinite(b) and not math.isfinite(c)) or
                                  (math.isfinite(b) and math.isfinite(c) and _close(b, c)))
        ok = same and _close(n['eps'], cert.eps)
        return ok, '' if ok else 'band does not match'
    if s.kind == 'foresight':
        bad = _disturbed(r)
        fs = [f for f in r.foresight if f['situation'] not in bad]
        ok = n['pushes'] == len(fs) and _close(n['median'], float(np.median([f['leader_rms'] for f in fs])))
        return ok, '' if ok else 'foresight does not match'
    if s.kind == 'disturbed':
        k = n['object']
        rms = _knock_rms(r, k)
        ok = rms is not None and _close(n['rms'], rms) and rms > DISTURBED and k in _disturbed(r)
        return ok, '' if ok else 'disturbance not shown by the predictions'
    if s.kind == 'imaginations':
        ok = n == _imaginations(r, g)
        return ok, '' if ok else 'imagination counts do not match the grade'
    if s.kind == 'rests_on':                        # the certificate's own premise ledger, re-read
        rests = _rests(cert)
        ok = (n == {}) if rests is None else (n.get('premises') == rests)
        return ok, '' if ok else "the premises said are not the certificate's"
    if s.kind == 'assumption':                      # fixed words, already re-rendered above
        return True, ''
    return False, f'unknown kind {s.kind}'


def words(statements):
    return '\n'.join(s.text for s in statements)
