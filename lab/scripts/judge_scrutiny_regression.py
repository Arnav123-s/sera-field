"""U4 paired replay of the SAVED b1 claim rows, never a replacement fixture.

  python scripts/judge_scrutiny_regression.py --saved sera-runs/ab-b1/judge --out development tool/out/U4-regression.json
  python scripts/judge_scrutiny_regression.py --claims OLD.jsonl --claims NEW.jsonl --out OUT.json

Each saved arm must contain 306 unique (seed, world, structural family) rows.
Missing rows are an error, even if summary.txt says that the old run passed.
Both arms are replayed independently; only received judge refutations train the
on-arm history. No observer grade or hidden law is used to choose scrutiny.
"""
import argparse
import ast
from contextlib import contextmanager
import json
import math
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def claim_key(row):
    return row['seed'], row['world'], row['family']


def saved_accepted(row):
    return bool(row['accepted'] and row.get('checker', True))


def load_claims(path, expected=306):
    rows = [json.loads(line) for line in Path(path).read_text(encoding='utf-8-sig').splitlines() if line.strip()]
    if len(rows) != expected or len({claim_key(row) for row in rows}) != expected:
        raise ValueError(f'{path}: expected {expected} unique saved claims, found {len(rows)}')
    for row in rows:
        if type(row['accepted']) is not bool or 'band' not in row or 'checker' not in row:
            raise ValueError(f'{path}: incomplete saved judge row: {claim_key(row)}')
        if not isinstance(ast.literal_eval(row['family']), tuple):
            raise ValueError('A saved structural tuple family is required')
    return rows


def replay(rows, runner):
    """Pure paired comparison; runner(row, enabled) also supports cheap test stubs."""
    paired, violations, extra = [], [], []
    for row in rows:
        off, on = runner(row, False), runner(row, True)
        key = claim_key(row)
        if off['accepted'] != saved_accepted(row) or off['band'] != row['band']:
            violations.append(dict(claim=key, reason='off does not reproduce the saved verdict/band'))
        # Other deterministic core fields are checked when the runner supplies them.
        for name, value in off.get('core', {}).items():
            if name in row and row[name] != value:
                violations.append(dict(claim=key, reason='off core mismatch: '+name))
        if on['accepted'] and not off['accepted']:
            violations.append(dict(claim=key, reason='a refused claim was accepted'))
        if on['accepted'] and (on['band'] is None or off['band'] is None
                               or not math.isfinite(on['band']) or not on['band'] <= off['band']):
            violations.append(dict(claim=key, reason='accepted band widened or is not finite'))
        if off['accepted'] and not on['accepted']:
            witness = on.get('scrutiny', {}).get('counterexample')
            extra.append(dict(claim=key, counterexample=witness, reason=on.get('reason')))
            if not witness:
                violations.append(dict(claim=key, reason='extra refusal has no counterexample/witness'))
        record = on.get('scrutiny', {})
        if not (0 <= record.get('used', 0) <= record.get('budget', 0) <= 4
                and 0 <= record.get('candidates', 0) <= 32):
            violations.append(dict(claim=key, reason='rail scrutiny budget exceeded'))
        pair = dict(claim=key, off=off, on=on)
        paired.append(pair)
    return dict(passed=not violations, claims=len(paired),
                accepted_off=sum(p['off']['accepted'] for p in paired),
                accepted_on=sum(p['on']['accepted'] for p in paired),
                extra_refusals=extra, violations=violations, paired=paired)


class RailReplay:
    def __init__(self):
        # Match the saved script's policies BEFORE importing the judge.
        for key, val in dict(CCOPS5_SHAPES='library', CCOPS5_CLAIM='functional', CCOPS5_BAND='claim',
                             CCOPS5_NUMERATOR='laplace', CCOPS5_KNOCK='throw').items():
            os.environ[key] = val
        sys.path.insert(0, str(ROOT))
        from scripts import judge_regression as fixture
        from sera import crutches as CR, tasks as TS
        from ccops5.core import grammar as G, likelihood as L, truth
        if (truth.BAND, truth.NUMERATOR, L.KNOCK) != ('claim', 'laplace', 'throw'):
            raise ValueError('Judge imported with different policies; replay in a fresh process')
        self.fixture, self.CR, self.TS, self.G, self.truth = fixture, CR, TS, G, truth
        self.history = TS.JudgeScrutiny()
        G.use_library(fixture.LIBRARY)

    @contextmanager
    def switch(self, enabled):
        on, off = set(self.CR.ON), set(self.CR.OFF)
        try:
            self.CR.ON = on | {'judge_scrutiny'} if enabled else on - {'judge_scrutiny'}
            self.CR.OFF = off - {'judge_scrutiny'} if enabled else off | {'judge_scrutiny'}
            yield
        finally:
            self.CR.ON, self.CR.OFF = on, off

    def __call__(self, row, enabled):
        law, level = self.fixture.WORLDS[row['world']]
        world, signs = self.TS.rail_world(row['seed'], 80400 + row['world'], law, level)
        task = self.TS.Rail(world, f"regression {row['seed']}/{row['world']}", (), signs)
        family = self.G.canonical(ast.literal_eval(row['family']))
        with self.switch(enabled):
            if enabled:
                self.history.begin(task)
                task._scrutiny_prepared = True
            accepted, cert, reason = task.verify(family)
        result = dict(accepted=bool(accepted), band=cert.band, reason=reason)
        if enabled:
            result['scrutiny'] = dict(task._scrutiny_last)
        else:
            result['core'] = dict(accepted=bool(cert.accepted), adequacy=cert.adequacy,
                                  prior=cert.log_prior, checks=repr(self.truth.functional_checks(family)),
                                  scope=repr(cert.scope), digest=cert.digest,
                                  library=self.G.library_digest(), reasons=list(cert.reasons),
                                  checker=bool(accepted) if cert.accepted else None,
                                  checker_reasons=[] if accepted or not cert.accepted else reason.split('; '))
        return result


def main(argv=None, runner_factory=RailReplay):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--saved', type=Path, default=ROOT/'sera-runs/ab-b1/judge')
    parser.add_argument('--claims', type=Path, action='append', help='explicit saved arm JSONL; repeat for A/B')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args(argv)
    files = args.claims if args.claims is not None else sorted(args.saved.rglob('*.jsonl'))
    try:
        if len(files) != 2:
            raise ValueError(f'Need two saved A/B JSONL files (306 each), found {len(files)} in {args.saved}. '
                             'Restore the original b1 claim files or pass --claims twice; summary.txt is insufficient.')
        arms = [load_claims(path) for path in files]
        def identity(rows):
            return {claim_key(row): (row['accepted'], row['checker'], row['band']) for row in rows}
        if identity(arms[0]) != identity(arms[1]):
            raise ValueError('Saved A/B arms disagree on claim identity, verdict or band')
        reports = [dict(source=str(path), **replay(rows, runner_factory())) for path, rows in zip(files, arms)]
        report = dict(passed=all(r['passed'] for r in reports), arms=reports)
    except (OSError, ValueError, KeyError, SyntaxError) as exc:
        report = dict(passed=False, error=str(exc), arms=[])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    for arm in report['arms']:
        for refusal in arm['extra_refusals']:
            print(json.dumps(dict(source=arm['source'], extra_refusal=refusal)), flush=True)
    print(json.dumps({k: v for k, v in report.items() if k != 'arms'}), flush=True)
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
