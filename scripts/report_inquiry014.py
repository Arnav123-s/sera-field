"""Summarize completed evidence without selecting or rerunning a model."""
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sera_field.records import write_json


def read(path):
    return json.loads(path.read_text())


def main():
    report = ROOT / 'reports/INQUIRY-014'
    teaching = read(report / 'TEACHING.json')
    qualification = read(report / 'QUALIFICATION.json')
    delivery = read(report / 'DELIVERY.json')
    arms = ('learned', 'disconnected', 'initialized', 'uniform', 'information', 'retained_parent_memory')
    finals = {arm: read(report / 'final' / arm / 'RESULTS.json') for arm in arms}
    costs = [read(p) for p in sorted((ROOT / 'runs').glob('inquiry014-*/state.json'))]
    if any(r['status'] == 'RUNNING' for r in costs):
        raise ValueError('Report completed costs after owned workers finish')
    write_json(report / 'COSTS.json', {
        'attempts': [{k: v for k, v in r.items() if k != 'sources'} for r in costs],
        'wall_seconds': sum(r['wall_seconds'] for r in costs),
        'cpu_seconds': sum(r.get('resources', {}).get('cpu_seconds', 0) for r in costs),
        'peak_bytes': max(r.get('resources', {}).get('peak_committed_bytes', 0) for r in costs),
        'shared_test_note': 'Includes the joint INQUIRY-014/SEMANTIC-015 targeted checks once; '
                           'whole-repository tests are accounted under SEMANTIC-015.'})
    tables = {}
    for regime in ('supported', 'omitted'):
        tables[regime] = '\n'.join(f"| {arm} | {r[regime]['initial_mse']:.7f} | "
            f"{r[regime]['final_mse']:.7f} | {r[regime]['performed_probes']} |"
            for arm, r in finals.items())
    cases = [json.loads(line) for line in (ROOT / 'runs/INQUIRY-014/final/learned/cases.jsonl').read_text().splitlines()]
    tails = {}
    for omitted in (False, True):
        values = sorted(r['final_mse'] for r in cases if r['omitted'] == omitted)
        tails[str(omitted)] = {'median': statistics.median(values),
                              'p95': values[int(.95 * (len(values) - 1))], 'maximum': max(values)}
    write_json(report / 'ERROR_TAILS.json', tails)
    selected = finals['learned']['supported']
    improvement = 1 - selected['final_mse'] / selected['initial_mse']
    counts = teaching['learned']['counts']
    text = f'''# INQUIRY-014 — investigate, check the intervention and return to the goal

The continuing owner acquired new measurements and returned to every original
goal in 192 registered systems. Across 128 supported systems, three performed
measurements reduced mean answer error from **{selected['initial_mse']:.7f}** to
**{selected['final_mse']:.7f}**, a **{improvement:.1%}** reduction. The persistent
interface also passed exact restart, original-goal preservation and rejection of
credit for an incorrectly performed intervention.

## What was taught and selected

I taught two matched arms for 1,024 episodes each, with three probes per episode.
The 2,048 teaching episodes contain **6,144 performed probes**, **147,456 explicit
measurement branches**, **442,368 charge projections** and **98,304 independently
evaluated original-goal outcomes**. These are training counts; development, final,
replay, audit, delivery and test costs are preserved separately in the logs and
[cost ledger](COSTS.json).

The connected arm applied **{counts['parameter_updates']} policy updates**, captured
**{counts['captures']}** positively assessed observations and recorded
**{counts['positive_bonuses']}** first positive contributions under the canonical
method/scope key. Both arms preserve all 24 deliberately mismatched interventions
and rejected their credit. The three-probe budget and candidate construction are
supplied engineering. Distinct coordinates are not automatically distinct
scientific methods or discoveries.

Development selected **step zero**: later policy updates did not improve the
registered development objective. The published owner therefore retains the
already trained response mechanism from GROW-013 and the initialized inquiry
controller. It is not labelled a successfully reward-trained inquiry policy.
The same selected and initialized policies produced identical final predictions.
Every attempted policy checkpoint, reward, capture and negative outcome remains
available locally. The intervention loop's measured acquisition benefit is
separate from an improvement in its policy weights.

## Registered evaluation

The following controls use the same original goals and observations. The
information control chooses among the supplied candidates by a simple analytic
criterion. These comparisons assess this finite experiment, not general
architectural rankings.

128 supported systems:

| Controller | Initial MSE | Returned MSE | Performed probes |
|---|---:|---:|---:|
{tables['supported']}

64 systems with the registered higher-frequency change in applicable families:

| Controller | Initial MSE | Returned MSE | Performed probes |
|---|---:|---:|---:|
{tables['omitted']}

Every final goal returned an answer. Each round preserved all 24 measurement
outcomes, which canonicalized to 12 distinct probe coordinates. The finals contain
three supported and one shifted actuator mismatch. No final outcome updated a
weight or memory. The analytic information control has the lowest mean error in
both cohorts; the exact values and error tails remain part of this result.

## One connected process

The acquired response model feeds a recurrent investigation state. A finite
measurement-only Ising construction enumerates its complete outcome branches;
those branches propose conditional controls. A diagonal recurrent controller
retains exact forward derivative eligibility, independently checked against
autograd. The performed measurement updates acquisition. An assessor checks the
original-goal outcomes and binds credit to the decision, predictor, goal, source,
assessment and actual intervention. Positive capture returns to the same owner's
bulk memory. Imagined values do not become measured observations.

The new [persistent interface](../../docs/INQUIRY_USAGE.md) saves pending
eligibility, measurements, original goal, source/scope, RNG, optimizer and owner.
Its fresh-process demonstration performed three interventions and returned MSE
**{delivery['returned_mse']:.7f}**, from **{delivery['initial_mse']:.7f}** initially.
One deliberate actuator mismatch was retained as an actual observation while its
intended-action credit was rejected. Positive and negative checked rewards both
remain in [DELIVERY.json](DELIVERY.json).

## Verification and next connection

All five [qualification gates](QUALIFICATION.json) passed: source identities,
parent parameter preservation, teaching integrity, final integrity and earlier
human-task retention. The independent audit verified reward arithmetic,
canonical deduplication, complete branches, no repeated evidence, mismatch
handling and every final outcome. The fresh-process final replay has case hash
`{finals['learned']['cases_sha256']}`.

The [inference owner](../../checkpoints/INQUIRY-014/MANIFEST.json),
[teaching details](TEACHING.json), [retention](RETENTION.json),
[protocol](../../protocols/INQUIRY-014.md), [registration](FINAL_REGISTRATION.json),
[replay](REPLAY.json) and [costs](COSTS.json) preserve the full claim chain.
Failed learning attempts are retained; completion of the experiment does not
turn them into positive policy-learning evidence.

SEMANTIC-015 now carries human premise/hypothesis interpretation and true
closed-loop curvature tags through this same continuing field, with earlier
subject rehearsal and prospective regression gates. The complete
[architecture checklist](../../docs/WHOLE_ARCHITECTURE.md) remains the governing
acceptance record for the broader research.
'''
    (report / 'REPORT.md').write_text(text, encoding='utf-8')
    print(json.dumps({'acquisition_improvement': improvement,
                      'selected_step': qualification['selected']['step'], 'goals': len(cases)}))


if __name__ == '__main__':
    main()
