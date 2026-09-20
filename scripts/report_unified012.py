"""Collate completed evidence without rerunning or selecting on final outcomes."""
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from sera_field.records import write_json,sha256


def main():
    runs=ROOT/'runs/UNIFIED-012';report=ROOT/'reports/UNIFIED-012';report.mkdir(exist_ok=True)
    read=lambda path:json.loads(path.read_text())
    names=('coupled','capture_disconnected','parent','coupled-no_memory','coupled-no_covariance')
    metrics={a:read(runs/'final'/a/'RESULTS.json') for a in names}
    replay=read(runs/'replay/coupled/RESULTS.json')
    candidate,parent=metrics['coupled'],metrics['parent']
    mean_pair=lambda m:sum(x['accuracy'] for x in m['pairs'].values())/len(m['pairs'])
    gates={'reading_retention':candidate['reading']['accuracy']>=parent['reading']['accuracy']-.03,
           'mathematics_retention':candidate['math']['accuracy']>=parent['math']['accuracy']-.03,
           'mean_pair_retention':mean_pair(candidate)>=mean_pair(parent)-.03,
           'physical_retention':candidate['physics']['mse']<=1.15*parent['physics']['mse'],
           'exact_replay':candidate['cases_sha256']==replay['cases_sha256'],
           'immutable_inference':all(m['weights_before']==m['weights_after'] for m in metrics.values())}
    for a in names:
        target=report/'final'/a;target.mkdir(parents=True,exist_ok=True)
        for name in ('RESULTS.json','OPENED_GROUPS.json'):
            shutil.copyfile(runs/'final'/a/name,target/name)
    shutil.copyfile(runs/'replay/coupled/RESULTS.json',report/'REPLAY.json')
    shutil.copyfile(runs/'FINAL_REGISTRATION.json',report/'FINAL_REGISTRATION.json')
    teaching={a:read(runs/a/'COMPLETE.json') for a in ('coupled','capture_disconnected')}
    write_json(report/'TEACHING.json',teaching)
    write_json(report/'QUALIFICATION.json',{'gates':gates,'all_gates':all(gates.values()),
               'selected':candidate['selection'],'whole_architecture_completed':False})
    costs=[read(p) for p in (ROOT/'runs').glob('unified012-*/state.json')]
    compact=[{k:v for k,v in r.items() if k!='sources'} for r in costs]
    write_json(report/'COSTS.json',{'attempts':compact,'wall_seconds':sum(r['wall_seconds'] for r in costs),
        'cpu_seconds':sum(r.get('resources',{}).get('cpu_seconds',0) for r in costs),
        'peak_bytes':max(r.get('resources',{}).get('peak_committed_bytes',0) for r in costs)})
    rows='\n'.join(f"| {a} | {m['reading']['accuracy']:.2%} | {m['math']['accuracy']:.2%} | {mean_pair(m):.2%} | {m['physics']['mse']:.6f} | {m['omitted']['mse']:.6f} |" for a,m in metrics.items())
    chosen=teaching['coupled']
    text=f'''# UNIFIED-012 — coupled covariance, temporal credit and verified bulk

The continuing owner now executes matrix-valued sheaf transport, timed Hamiltonian
echo learning and a verified condensate-memory feedback path. The exact same
field remains in its reading, arithmetic-program, human-pair and physical routes.
This completes a coupled implementation/evaluation package within the still-open
[whole architecture](../../docs/WHOLE_ARCHITECTURE.md).

I trained two matched arms for 3,072 updates of batch 24 each: **147,456 total task
presentations**, with the same source sampling. These are continuing presentations
of the qualified human corpus and new simulated physical cases, not 147,456 new
human documents. There were also 96 capture-policy attempts per arm, each graded
on 12 independent simulated query outcomes (2,304 outcome evaluations in total).
The capture policy received score-function credit; field processing received
temporal echo credit. All failures and the discarded proposals remain recorded.

| Owner / ablation | Reading accuracy | Math-program accuracy | Mean human-pair accuracy | Physical MSE | Omitted-response MSE |
|---|---:|---:|---:|---:|---:|
{rows}

The candidate selected at update **{chosen['selected']['step']}** retains
**{chosen['selected_captures']}** field captures; the last training state records
**{chosen['all_captures']}**. Positive training reward qualifies a scoped capture.
Useful memory transfer is assessed by the matched arm and inference ablation in
the table, separately from mathematical conservation and successful persistence.
No candidate was selected or adjusted using these final outcomes.

Prospective release gates: **{sum(gates.values())}/{len(gates)}** passed.
The exact case replay is **{gates['exact_replay']}**. Individual decisions and the
full retention comparisons are in [QUALIFICATION.json](QUALIFICATION.json).

## What was learned and what was supplied

Teaching updated this laboratory's own encoders/readouts, geometric field and
coupling parameters. No external pretrained model was imported. New learned
capture decisions alter the actual retained bulk when independently measured
progress is positive. The retained CONCEPT-011 operator/interface weights remain
the reference for exact mathematical behavior and the earlier supported task route.

I supplied the finite geometry, covariance lift, free energy, finite band codec,
source contracts, data sampling and independent assessments. The Chern code stores
bounded quantized field values under explicit gap conditions. Its charge does not
certify a fact. Scalar concentration is conserved during fixed-potential relaxation;
the externally qualified capture is a separate write/reservoir event.

The first test attempt failed on module placement and was corrected before
training. Mathematical tests checked timed input/parameter gradients, reversal,
SPD covariance, adjoints, concentration/energy, charge/quantization, rejected
capture and exact resume. Detailed equations are in
[COUPLED_EQUATIONS.md](../../docs/COUPLED_EQUATIONS.md).

## Evidence and continuation

[Teaching and selection](TEACHING.json), [final registration](FINAL_REGISTRATION.json),
[replay](REPLAY.json), [all attempt costs](COSTS.json), and the final directories
retain source/checkpoint/result identities. Full per-case and optimizer histories
remain under `runs/UNIFIED-012/` in the local lab. Independent assessment uses
unopened human groups and fresh simulated worlds. Parent readback is a retention
reference, not a ranking of equally trained architectures.

The next connected package is GROW-013: learn residual representations from
measurements, qualify an extension on separate observations and carry that same
acquired relation through five uses. It preserves this result, including any failed
gate, rather than replacing the whole-research objective with this component score.
'''
    (report/'REPORT.md').write_text(text,encoding='utf-8')
    print(json.dumps({'gates':gates,'selected':chosen['selected']['step']},indent=2))


if __name__=='__main__':main()
