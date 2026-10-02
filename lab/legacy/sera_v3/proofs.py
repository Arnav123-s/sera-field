"""The judge's office (plan revision 5.1): SERA submits a claim and goes on; the full proof runs elsewhere.

Stage 0 measured where a proven world's time goes: about 1,100 s of CPU, almost all of it the judge's universe audit
(every one of the 878 dictionary terms ruled out, by nonlinear fits of about 110 superset laws per term of the claim)
and the independent checker's re-derivation of it. SERA's own thinking in the same world took about 30 s. Inline,
SERA waited for all of it before the next world.

Here nothing about the judge changes. In a world, the mind asks the judge for its certificate under the 'wide'
audit policy (sera.mind, prove='defer'): the same code, every part (the in-space rivals, the misfit test, the nested
intervals, the band, a grown claim's wide rivals) but the universe audit. A claim that passes is submitted: its
ledger (the exact object the judge would have read inline) goes to the office, which runs the full certificate
(truth.certify under the program's policy, universe audit included) and then checker.check - the same two calls
the mind made inline, on the same ledger - in other processes, while SERA lives its next worlds. Only a claim the
office certified and the checker re-derived is ever "sure".

What does change: inline, a claim the audit refused left SERA in the world to push again; deferred, SERA has already
left, and the refusal reaches it as a lesson. The verdicts on a submitted ledger are the same as inline.

The office is a folder (so jobs survive a restart of either side):
  <root>/queue/<key>.job   pickled job: key, ledger, family, eps, the judge's policy, the world (for the observer's
                           grade only; the judge never reads it)
  <root>/work/<key>.job    claimed by one worker (an atomic rename)
  <root>/done/<key>.res    pickled result: the certificate, verified, the checker's reason, CPU and wall seconds
  <root>/done/<key>.job    the job, kept for the grade
Run the workers with scripts/sera_judge.py; Office(None) proves inline, in this process (tests, and a laptop with no
spare cores).
"""
import os
import pickle
import time
from pathlib import Path

PRE_AUDIT = 'wide'              # the mind's pre-certificate: everything but the universe audit


def policy():
    """The judge's policy of this process (the office refuses a job made under another)."""
    from ccops5.core import grammar, likelihood as L, truth
    return dict(audit=truth.AUDIT, band=truth.BAND, numerator=truth.NUMERATOR, knock=L.KNOCK,
                claim=truth.CLAIM,                                # Decision 11: exact or scoped claims
                shapes=grammar.SHAPES_POLICY)                     # Decision 12: SERA's invented shapes


def prove(job):
    """The full certificate and the checker's re-derivation, exactly the calls the mind made inline."""
    from ccops5.core import checker, grammar, truth
    grammar.use_library(job.get('library', ()))      # Decision 12: the library the world was lived under
    if job['policy'] != policy():
        return dict(key=job['key'], cert=None, verified=False, why=f"policy mismatch: job {job['policy']}, "
                                                                     f"office {policy()}", cpu=0.0, wall=0.0)
    t0, w0 = time.process_time(), time.time()
    ledger = job['ledger']
    cert = truth.certify(ledger, job['family'], job['eps'])
    ok, why = checker.check(cert, ledger.throws, ledger.sigma) if cert.accepted else (False, None)
    return dict(key=job['key'], cert=cert, verified=bool(cert.accepted and ok), why=why,
                cpu=round(time.process_time() - t0, 1), wall=round(time.time() - w0, 1))


def _dump(obj, path):
    tmp = Path(str(path) + '.tmp')
    with open(tmp, 'wb') as f:
        pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
    os.replace(tmp, path)


def _load(path):
    with open(path, 'rb') as f:
        return pickle.load(f)


class Office:
    """SERA's side of the office: submit, and collect what is done. root=None proves inline."""

    def __init__(self, root=None):
        self.root = Path(root) if root else None
        self._inline = {}
        if self.root:
            for d in ('queue', 'work', 'done'):
                (self.root / d).mkdir(parents=True, exist_ok=True)

    def submit(self, key, ledger, family, eps, world=None):
        if getattr(ledger, 'audit_shared', None) is not None:
            ledger.audit_shared = None           # an exact cache (truth.audit_fit): dropping it changes no result
        from ccops5.core import grammar
        job = dict(key=key, ledger=ledger, family=tuple(family), eps=float(eps), policy=policy(), world=world,
                   submitted=time.time(), library=grammar.LIBRARY)
        if self.root is None:
            self._inline[key] = (prove(job), job)
            return
        _dump(job, self.root / 'queue' / f'{key}.job')

    def ready(self, key):
        return key in self._inline if self.root is None else (self.root / 'done' / f'{key}.res').exists()

    def take(self, key):
        """(result, job) of a finished proof; the files are kept (the record of what the judge did)."""
        if self.root is None:
            return self._inline.pop(key)
        return _load(self.root / 'done' / f'{key}.res'), _load(self.root / 'done' / f'{key}.job')

    def waiting(self):
        """Jobs not yet finished (queued or being proven), over every life using this office."""
        if self.root is None:
            return 0
        return len(list((self.root / 'queue').glob('*.job'))) + len(list((self.root / 'work').glob('*.job')))


def recover(root):
    """At the office's start: a job left in work/ by a stopped worker goes back to the queue."""
    root = Path(root)
    for p in (root / 'work').glob('*.job'):
        if not (root / 'done' / (p.stem + '.res')).exists():
            os.replace(p, root / 'queue' / p.name)


def claim(root):
    """The oldest queued job, claimed by an atomic rename (another worker may take it first): its path, or None."""
    root = Path(root)
    for p in sorted((root / 'queue').glob('*.job'), key=lambda p: (p.stat().st_mtime, p.name)):
        try:
            os.replace(p, root / 'work' / p.name)      # POSIX rename: exactly one worker's succeeds
        except OSError:
            continue
        return root / 'work' / p.name
    return None


def work_one(root):
    """Prove one queued job. Returns its result, or None when the queue is empty."""
    root = Path(root)
    p = claim(root)
    if p is None:
        return None
    job = _load(p)
    res = prove(job)
    _dump(res, root / 'done' / f"{job['key']}.res")
    os.replace(p, root / 'done' / p.name)
    return res
