"""The judge before and after a change (Decision 16's paired regression, review 11 and S14): fixed rails (seeds 1-3),
fixed old claims (the empty law; free curves on inputs at every grid, on lenses and on dimensions; two- and
three-part laws; registered shapes alone and beside a curve, under a fixed library), each certified as a functional
claim and checked. One line per claim with its full structural family and every invariant the comparison needs;
timing is kept apart. Run it at two commits and compare the files: every old claim must come out the same.

  python scripts/judge_regression.py OUT.jsonl [--quick]
  JUDGE_ROOT=<an older package> PYTHONPATH=<it> python <this script> OUT.jsonl     (the older judge)
Not covered (say so when reporting): exact and scoped claims, novel-force worlds, alone and teaching sequences.
"""
import json
import os
import sys
import time
from pathlib import Path

for key, val in dict(CCOPS5_SHAPES='library', CCOPS5_CLAIM='functional', CCOPS5_BAND='claim',
                     CCOPS5_NUMERATOR='laplace', CCOPS5_KNOCK='throw').items():
    os.environ[key] = val
sys.path.insert(0, os.environ.get('JUDGE_ROOT') or str(Path(__file__).resolve().parents[1]))   # JUDGE_ROOT: an older
#                                                                                     package's judge, to compare

import numpy as np  # noqa: E402

from ccops5.core import checker, grammar as G, truth  # noqa: E402
from sera import tasks as TS  # noqa: E402

WORLDS = [((('position', 'straight'),), 1), ((('speed', 'straight'),), 1), ((('position', 'cubic'),), 1),
          ((('position', 'straight'), ('speed', 'straight')), 1), ((('position', 'wave'),), 2),
          ((('speed', 'growing'),), 2)]
G33 = np.linspace(-1.0, 1.0, 33)
LIBRARY = (G.shape_term('position', 33, 1, tuple(float(v) for v in G33 ** 3)),      # a cubic drawn on position
           G.shape_term('speed', 33, 2, tuple(float(v) for v in G33)))            # a line drawn on speed
CLAIMS = [(), (('cell', 'position', 9),), (('cell', 'position', 17),), (('cell', 'position', 33),),
          (('cell', 'speed', 17),), (('cell', 'time', 9),),
          (('cell', 'position', 9), ('cell', 'speed', 9)),
          (('cell', 'position', 9), ('cell', 'speed', 9), ('cell', 'time', 9)),
          (('cell', 'dim:x.x.x.mul.mul@4', 9),), (('cell', 'dim:1.x.x.x.mul.mul.add@6', 9),),
          (('cell', 'dim:x.v.mul@6', 9),), (('cell', 'dim:0.x.sub@4', 9),),
          (('cell', 'position@1:1', 33),), (('cell', 'speed@2:3', 17),),
          (LIBRARY[0],), (LIBRARY[0], LIBRARY[1]), (LIBRARY[0], ('cell', 'speed', 9))]


def main():
    out = Path(sys.argv[1])
    quick = '--quick' in sys.argv
    G.use_library(LIBRARY)
    rows = []
    for seed in ((3,) if quick else (1, 2, 3)):
        for wi, (law, level) in enumerate(WORLDS[:2] if quick else WORLDS):
            w, signs = TS.rail_world(seed, 80400 + wi, law, level)
            task = TS.Rail(w, f'regression {seed}/{wi}', (), signs)
            for fam in (CLAIMS[:4] if quick else CLAIMS):
                fam = G.canonical(fam)
                t0 = time.time()
                cert = truth.certify(task.ledger([fam]), fam, TS.EPS, claim='functional')
                ok, why = checker.check(cert, task.throws, task.sigma) if cert.accepted else (None, ())
                grade = task.grade(cert, bool(cert.accepted and ok))
                row = dict(seed=seed, world=wi, law=G.name(law), family=repr(fam), name=G.name(fam),
                           accepted=bool(cert.accepted),
                           band=None if cert.band is None else float(cert.band),
                           adequacy=None if cert.adequacy is None else float(cert.adequacy),
                           prior=float(cert.log_prior), checks=repr(truth.functional_checks(fam)),
                           scope=repr(cert.scope), digest=cert.digest, library=G.library_digest(),
                           reasons=list(cert.reasons), checker=ok, checker_reasons=list(why),
                           verdict=grade.get('verdict'), gap=grade.get('gap'))
                rows.append(row)
                print(json.dumps(dict(row, seconds=round(time.time() - t0, 1))), flush=True)
    out.write_text('\n'.join(json.dumps(r) for r in rows) + '\n', encoding='utf-8')
    print('REGRESSION DONE', len(rows), flush=True)


if __name__ == '__main__':
    main()
