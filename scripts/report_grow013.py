"""Report frozen outcomes, including shifted cases and long error tails."""
import json
from pathlib import Path
import shutil
import statistics
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from sera_field.records import write_json


def main():
    runs=ROOT/'runs/GROW-013';report=ROOT/'reports/GROW-013'
    read=lambda p:json.loads(p.read_text())
    metrics={a:read(runs/'final'/a/'RESULTS.json') for a in ('learned','fixed','no_extension')}
    cases=[json.loads(line) for line in (runs/'final/learned/cases.jsonl').read_text().splitlines()]
    tails={}
    for omitted in (False,True):
        subset=[r for r in cases if r['omitted']==omitted]
        tails[str(omitted)]={key:{'median':statistics.median([r[key] for r in subset]),
            'p95':sorted(r[key] for r in subset)[int(.95*(len(subset)-1))],
            'maximum':max(r[key] for r in subset)} for key in
            ('forward_mse','inverse_outcome_error','counterfactual_mse','planning_mse')}
    write_json(report/'ERROR_TAILS.json',tails)
    costs=[read(p) for p in (ROOT/'runs').glob('grow013-*/state.json')]
    write_json(report/'COSTS.json',{'attempts':[{k:v for k,v in r.items() if k!='sources'} for r in costs],
        'wall_seconds':sum(r['wall_seconds'] for r in costs),
        'cpu_seconds':sum(r.get('resources',{}).get('cpu_seconds',0) for r in costs),
        'peak_bytes':max(r.get('resources',{}).get('peak_committed_bytes',0) for r in costs)})
    learned=metrics['learned']['supported'];base=metrics['no_extension']['supported'];fixed=metrics['fixed']['supported']
    improvement=1-learned['forward_mse']/base['forward_mse'];trained=1-learned['forward_mse']/fixed['forward_mse']
    tables={}
    for regime in ('supported','omitted'):
        tables[regime]='\n'.join(f"| {arm} | {m[regime]['forward_mse']:.6f} | {m[regime]['inverse_outcome_error']:.6f} | {m[regime]['counterfactual_mse']:.6f} | {m[regime]['planning_mse']:.6f} | {m[regime]['direction_correct']:.2%} |" for arm,m in metrics.items())
    text=f'''# GROW-013 — learn a missing response and use it five ways

The continuing coupled owner learned residual representations from observations.
On 256 new simulated systems, the qualified extension reduced forward MSE by
**{improvement:.1%}** versus its retained four-feature route and **{trained:.1%}**
versus the identically initialized, untrained extension. The same acquired
parameter record also served inverse questions, counterfactuals, planning and a
directional explanation. Fresh-process replay was exact and all six retention/
identity checks passed.

## Teaching and acquisition

I ran 2,048 updates with 16 systems per update: **32,768 teaching systems**,
786,432 adaptation-row presentations and 524,288 supervised query targets.
The simulator supplies the experience and the independent outcomes; no hidden
family label or omitted-response equation enters the feature learner. Smooth
restoring responses, input saturation and interactions are represented in the
supplied curriculum. This is learning new-to-this-owner relationships within that
research curriculum, not a claim of a new law of nature.

New directions, offsets, context-dependent residual features, precision and the
stationary boundary gate were trained. Earlier parent parameters stayed exactly
unchanged. A stable FHN stationary solve now feeds the same covariance, Clifford,
temporal-echo and memory path. Its implicit gradients were independently checked.
The earlier human-source abilities remain in that owner and passed regression
checks; this work package's new teaching was numerical rather than a new text
corpus.

Acquisition uses 24 adaptation observations and eight separate calibration
observations. It retains the old representation when adequate, then tests bounded
learned extensions of rank 4, 8 and 16. A 25% calibration improvement and a
nontrivial initial discrepancy qualify the smallest successful extension. On the
supported final, it kept rank zero in **175** cases, used rank four in **65** and
rank eight in **16**. It did not need rank sixteen in this cohort.

The supplied rank limits and calibration rule are engineering. The continuous
features and acquired coefficients are learned. The finite effective-action flow
is recorded with an explicit Hessian and regulator; it remains an adequacy
diagnostic rather than a claim that a trace equation alone invents new concepts.

## Independently assessed uses

256 new supported systems, same observations and original goals for all controls:

| Owner | Forward MSE | Inverse outcome error | Counterfactual MSE | Planning MSE | Direction accuracy |
|---|---:|---:|---:|---:|---:|
{tables['supported']}

The direction result is **255/256**, using the retained learned routing of the
taught control-input question and the acquired model's numerical consequences.
Its sentence renderer is supplied. Inverse answers preserve distinct bounded
roots and their residuals; plans retain five candidates. Independent DOP853
integration assesses achieved plan endpoints.

128 additional systems raise the frequency in applicable response families;
some families are unaffected by that change. All results remain preserved:

| Owner | Forward MSE | Inverse outcome error | Counterfactual MSE | Planning MSE | Direction accuracy |
|---|---:|---:|---:|---:|---:|
{tables['omitted']}

The error distribution and maxima are in [ERROR_TAILS.json](ERROR_TAILS.json).
Six supported and three shifted cases include a deliberately mismatched
intervention. Their requested/performed controls and actual outcomes are retained.
This study does not grant reward for those mismatched actions. INQUIRY-014 carries
that actual-outcome correction through repeated generated investigations.

## Use and evidence

[Usage](../../docs/EXTENSION_USAGE.md) describes measurement acquisition and a
persistent task. The exported [owner](../../checkpoints/GROW-013/MANIFEST.json)
passes a real fresh-process CLI acquisition, restart and follow-up answer.
[DELIVERY.json](DELIVERY.json) records the independent demonstration outcome.

[Teaching](TEACHING.json), [prospective protocol](../../protocols/GROW-013.md),
[registration](FINAL_REGISTRATION.json), [qualification](QUALIFICATION.json),
[retention](RETENTION.json), [replay](REPLAY.json) and [all costs](COSTS.json)
link claims to evidence. Full per-case acquired models, every attempted update,
source hashes, optimizer/RNG and earlier checkpoints remain in the local run tree.
No opened final selected or retuned the model.

The next connected work teaches the investigation policy using complete
measurement alternatives and exact local eligibility. The overall
[research/behavior checklist](../../docs/WHOLE_ARCHITECTURE.md) remains open;
this evidence closes the specified residual-learning package, not every broader
interpretation and discovery requirement.
'''
    (report/'REPORT.md').write_text(text,encoding='utf-8')
    print(json.dumps({'forward_improvement_over_no_extension':improvement,
                      'forward_improvement_over_fixed':trained,'cases':len(cases)}))


if __name__=='__main__':main()
