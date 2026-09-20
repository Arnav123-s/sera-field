"""Summarize every matched arm, decision and exact supervised cost."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from sera_field.records import write_json


def read(path): return json.loads(Path(path).read_text())


def main():
    root = ROOT / 'reports/GENRE-017'
    qualification = read(root / 'QUALIFICATION.json'); teaching = read(root / 'TEACHING.json')
    delivery = read(root / 'DELIVERY.json'); arms = ('exact_noisy', 'exact_clean', 'gaussian_noisy', 'parent', 'no_imagination', 'no_action')
    metrics = {arm: {split: read(root / 'final' / arm / split / 'INDEPENDENT_METRICS.json')
                    for split in ('matched', 'mismatched')} for arm in arms}
    attempts = [read(p) for p in sorted((ROOT / 'runs').glob('genre017-*/state.json'))]
    if not attempts or any(r['status'] == 'RUNNING' for r in attempts):
        raise ValueError('Finish the supervised work before reporting exact costs')
    costs = {'attempts': [{k: v for k, v in row.items() if k != 'sources'} for row in attempts],
        'wall_seconds': sum(r['wall_seconds'] for r in attempts),
        'cpu_seconds': sum(r.get('resources', {}).get('cpu_seconds', 0.) for r in attempts),
        'peak_bytes': max(r.get('resources', {}).get('peak_committed_bytes', 0) for r in attempts),
        'source_preparation': read(ROOT / 'reports/SOURCE_INTAKE/MULTINLI-VIEWS.json')}
    write_json(root / 'COSTS.json', costs)
    table = '\n'.join(f"| {arm} | {split} | {result['accuracy']:.2%} | {result['log_loss']:.6f} | "
                     f"{result['expected_calibration_error_10_bins']:.6f} |"
                     for arm, by_split in metrics.items() for split, result in by_split.items())
    exposure = '\n'.join(f"| {arm} | {r['counts']['human_genre']:,} | "
        f"{sum(v for k, v in r['counts'].items() if k != 'human_genre'):,} | "
        f"{r['complete']['selected']['semantic_step']:,} |" for arm, r in teaching.items())
    failed = [key for key, value in qualification['gates'].items() if not value]
    decision = ('All frozen gates passed; the selected primary candidate is packaged as a qualified successor.'
                if not failed else 'The candidate and every control are preserved. The qualified parent remains available. '
                'The unmet gates are: ' + ', '.join(failed) + '.')
    report = f'''# GENRE-017: learned finite field action and broader human interpretation

{decision}

## What the continuing owner learned

Each of three matched arms received a full pass over the same **371,929 human
language pairs**, plus the identical ordered rehearsal curriculum. The primary
sources cover five training genres. Distinct matched and previously untaught
genres supply two independently reserved 4,096-pair evaluations. Source identities,
human annotation provenance and genre outcomes are retained.

| Arm | Primary presentations | Rehearsal presentations | Selected primary update |
|---|---:|---:|---:|
{exposure}

The new finite ensemble action changes the same boundary that enters the existing
history, curvature, stationary, covariance and temporal field. Four learned
covariant features define 16 exact conditional Gaussian-mixture configurations.
Their connected second and fourth moments and the corresponding action are
explicitly computed. The fourth-order expansion is measured against the normalized
mixture, with approximation failures retained. A conditional field distribution
is not labeled a proof of semantic truth.

The exact_noisy/exact_clean arms differ in the declared training perturbation.
The Gaussian arm uses the covariance-matched action and the same initial learned
parameters, source order and curriculum budget. New action and semantic weights
are trained, followed by controlled shared-encoder teaching with rehearsal. No
pretrained external weights or next-token objective are used. The supplied feature
generator, source annotations and dynamics are engineering; parameter changes are
the learner's acquired state.

## Frozen outcomes

| Route | Cohort | Accuracy | Log loss | Calibration error |
|---|---|---:|---:|---:|
{table}

These tables report every declared control. No-action and no-imagination are
inference dependence checks on the primary candidate. They are distinct from the
three separately trained arms. Per-genre confusion, calibration and probabilities'
identities are in the final evidence directories. The final assessment performs
no weight or factual-memory update. The [qualification](QUALIFICATION.json)
records the independent arithmetic and exact replay decision.

## Retention and actual use

[RETENTION.json](RETENTION.json) records earlier human interpretation, reading,
mathematics, dictionary/conversation routes and five uses of acquired physical
relationships. Protected parameter identities are checked separately from task
performance. The earlier source cohorts serve only as regression checks.

Fresh-process delivery reads three prospectively ordered human statements while
preserving the existing physical goal, then executes one actual measurement and
returns its checked result. Initial original-goal MSE was
**{delivery['initial_original_goal_mse']:.8f}** and returned MSE was
**{delivery['returned_original_goal_mse']:.8f}**. All positive or negative credit
is retained in [DELIVERY.json](DELIVERY.json); persistence is not itself counted
as an answer improvement.

## Reproduction and resources

[Frozen protocol](../../protocols/GENRE-017.md),
[action derivation](../../docs/FINITE_NEURAL_FIELD_ACTION.md),
[teaching](TEACHING.json), [splits](SPLITS.json),
[registration](FINAL_REGISTRATION.json) and [costs](COSTS.json) bind the evidence.
Successful and failed supervised attempts total **{costs['wall_seconds']/60:.2f}
wall minutes** and **{costs['cpu_seconds']/60:.2f} CPU minutes**, with peak
**{costs['peak_bytes']/1024**2:.1f} MiB** under one numerical thread and the 2 GiB
process-tree limit. Source intake/preparation costs are separately preserved.
Full optimizer, RNG, cursor, intermediate owners and failures remain local.

The [latest paper audit](../../docs/SDHA_UNIFIED_SOURCE_AUDIT.md) and
[whole-architecture tracker](../../docs/WHOLE_ARCHITECTURE.md) keep broader grounded
understanding, representation growth, active retry and reusable discoveries in
scope. This study closes only its measured integration and teaching contracts.
'''
    (root / 'REPORT.md').write_text(report, encoding='utf-8')
    print(json.dumps({'qualified': qualification['all_gates'], 'unmet_gates': failed}))


if __name__ == '__main__': main()
