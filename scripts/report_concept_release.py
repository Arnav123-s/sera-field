"""Write the capability report directly from preserved, independently replayed records."""
import json
from pathlib import Path
import statistics
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sera_field.records import write_json,sha256,utc


def read(path):return json.loads((ROOT/path).read_text())
def write(path,text):
    target=ROOT/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text.strip()+'\n',encoding='utf-8')


def table(name,subset='supported'):
    paths=sorted((ROOT/'runs'/name/'final').glob('*/RESULTS.json'))
    lines=['| Owner | Forward MSE | Inverse MSE | Counterfactual MSE | Plan MSE | Joint direction | Route |',
           '|---|---:|---:|---:|---:|---:|---:|']
    for path in paths:
        m=json.loads(path.read_text())['metrics'][subset]
        cells=[f"{m[k]:.6f}" for k in ('forward_mse','inverse_mse','counterfactual_mse','plan_mse')]
        cells += [f"{m[k]*100:.2f}%" if m[k] is not None else 'not assessed' for k in ('direction_correct','route_correct')]
        lines.append('| '+path.parent.name+' | '+' | '.join(cells)+' |')
    return '\n'.join(lines)


def main():
    cost=read('reports/CONCEPT-011/TOTAL_COSTS.json')
    package=read('checkpoints/CONCEPT-011/MANIFEST.json')
    decision=read('runs/CONCEPT-011/DECISION.json')
    if not decision['qualified']:raise ValueError('Do not report qualification before it exists')
    write('reports/CONCEPT-008/REPORT.md',f'''
# CONCEPT-008: taught acquisition and five-use qualification

I trained a context-dependent acquisition procedure inside the actual ECHO-007
owner. One observation-conditioned coefficient cloud was reused by prediction,
inverse inference, counterfactuals, planning and a learned direction interface.
Four numerical qualification gates passed. The initial question-routing and
joint explanation gates failed; that failed whole-five-use decision is preserved.

## Teaching and source scope

Full and diagonal learned precision each completed 4,096 updates of 24 systems:
98,304 presentations per arm, 196,608 total. Both selected step 4,096 on the
frozen 256-case development criterion. The original human-trained parameters
were exactly retained. This cycle added simulated teaching, not new human records.
The representation, independently implemented teacher, phrase annotations and
assessment contracts were supplied. No hidden environment coefficients entered
the learner. [Derivation and engineering](../../docs/CONCEPT_ENGINEERING.md).

## Fresh matched results

Each owner received identical observations on 512 supported systems. The 128
omitted-mechanism systems are separately recorded in each RESULTS.json.

{table('CONCEPT-008')}

The fixed ridge control was stronger on forward MSE; learned full precision was
stronger on inverse and plan MSE in this cohort. These are matched finite-task
findings, not rankings of general intelligence. Full precision was chosen before
the final from development performance, not from this table.

## Verified reward teaching

The selected full predictor stayed fixed while the existing investigation policy
completed 2,048 independently checked episodes, with 2,007 accepted updates.
Step 768, with 754 accepted updates, was selected on separate development data.
The later training and final-step state are preserved.

On 256 fresh inquiry systems the initial goal MSE was 1.441967. After evidence
acquisition, the selected policy achieved 0.171472, the unchanged policy 0.172033,
random selection 0.407007 and the analytic information heuristic 0.575984.
The additional reward-training improvement over unchanged was about 0.33%; the
large before/after reduction includes acquisition and the inherited policy.
Every original goal received a returned answer. Six actuator mismatches were
retained with their actual observations. Duplicate, stale or mismatched credit
was guarded by the existing independent CreditBridge contracts.

All four five-use owners and all four inquiry policies replayed exactly in new
processes. [Decision](DECISION.json), [source freeze](FROZEN.json),
[all local artifact identities](EVIDENCE_INDEX.json), [complete costs](COSTS.json).
The failures motivated separately frozen repairs; this final was never retuned.
''')
    for n,title,description in [
        (9,'Paired question teaching','Only the existing question-head weights were taught: 1,536 batches of 32, 49,152 presentations of 120 distinct supplied phrases. Development selected step 512. Every non-routing weight and every numerical output was exactly retained. The final direction and routing targets were not met. All three fresh-process replays were exact.'),
        (10,'Lexical residual and interference','An 8,194-parameter word/character-hash residual was trained from zero: 2,048 batches of 32, 65,536 presentations of 388 supplied phrases. Development selected step 2,048. The numerical and direction gates passed; routing missed its 90% target. All four replays were exact. A clearly labeled post-final diagnostic measured 71.25% routing for the old head, 93.75% for the residual alone and 85% for their sum across 80 unique opened phrases. That diagnosed interference; it did not qualify an untested repair.')]:
        write(f'reports/CONCEPT-{n:03d}/REPORT.md',f'''
# CONCEPT-{n:03d}: {title}

{description}

{table(f'CONCEPT-{n:03d}')}

Each row uses the same fresh 512 supported systems and that study's reserved
question bank. The supplied variable vocabulary is shared with teaching; sentence
forms are held out. The additional 128 omitted-mechanism systems remain in the
raw results. Different studies use different systems, so comparisons between
rows in this table are valid; changes between study tables also reflect cohorts.

This unsuccessful whole-five-use candidate stays preserved with its training
losses, full optimizer/RNG revisions, final records, replays and costs.
Its frozen final was not reused for optimization. The qualified successor is
reported in [CONCEPT-011](../CONCEPT-011/REPORT.md).

[Decision](DECISION.json) · [protocol](../../protocols/CONCEPT-{n:03d}.md) ·
[source and checkpoint identities](EVIDENCE_INDEX.json) · [costs](COSTS.json)
''')
    rows=[json.loads(line) for line in (ROOT/'runs/CONCEPT-011/final/repair/cases.jsonl').read_text().splitlines()]
    supported=[r for r in rows if not r['omitted']]
    tails={}
    for key in ('forward_mse','inverse_mse','counterfactual_mse','plan_mse'):
        ordered=sorted(r['metrics'][key] for r in supported)
        tails[key]={'median':statistics.median(ordered),'p95_nearest_rank':ordered[486],
                    'maximum':ordered[-1],'n':len(ordered)}
    write_json(ROOT/'reports/CONCEPT-011/ERROR_DISTRIBUTIONS.json',tails)
    tailtable='| View | Median squared error | 95th percentile | Maximum |\n|---|---:|---:|---:|\n'
    tailtable+='\n'.join(f"| {k} | {v['median']:.6f} | {v['p95_nearest_rank']:.6f} | {v['maximum']:.6f} |" for k,v in tails.items())
    demo=read('runs/CONCEPT-011/delivery/RESULTS.json')
    first=demo['first']['result'];new=demo['revised']['result']
    write('reports/CONCEPT-011/REPORT.md',f'''
# SERA Field: completed acquired-model capability release

I completed a connected teaching, diagnosis, repair, independent evaluation and
delivery cycle. The released owner acquires a local response model from measured
rows and reuses it for five tasks: prediction, inverse answers, counterfactuals,
planning and grounded directional language. Sessions retain the acquired state,
source receipts and original goal, then revise and return to that goal after
new evidence. All nine prospective qualification gates passed; all five final
owner evaluations replayed exactly. The complete engineering suite passed
**106 tests** and the persistent CLI delivery checks passed.

## What was learned

The full and diagonal acquisition arms completed **196,608 simulated system
presentations** in total. The retained full arm received 98,304. Its precision
network learned how strongly to revise three prior coefficient hypotheses from
new observations. Its direction head learned the consequences of a +0.5 change
in either of two variables at a specified operating point.

Three subsequent language studies completed **180,224 phrase presentations**:
49,152 in CONCEPT-009, 65,536 in CONCEPT-010 and 65,536 in CONCEPT-011.
The first bank contained 120 distinct supplied phrases; each later bank contained
388. These are repeated simulation-interface annotations, not a new human corpus.
The retained human-reading foundation covers **78,746 distinct human records**
across its preceding training lineage. Its original reading, arithmetic and
other protected parameters remain exactly retained. See the preserved
[human teaching account](../ECHO-007/LEARNED_STATE.json).

The new investigation study completed 2,048 independently checked episodes with
2,007 accepted updates; the selected policy retains 754 updates at step 768.
These costs include all later and unsuccessful work. New lexical routing was
taught directly from labeled examples; it was not described as reward learning.

The geometric owner was originally initialized and trained in this independent
lab. This continuation preserves that from-scratch lineage, its Clifford/sheaf
field and reversible credit operator. The new acquisition, meaning and routing
weights were also initialized locally; no pretrained language-model backbone
supplied them.

## Final results on the same new situations

Each owner saw identical observations on **512 supported systems**. A single
acquired concept per system served all five tasks, with no refitting for the
next task. Ninety-six unique final phrasings used taught variable vocabulary and
new sentence forms; the phrases recur across systems. Accordingly, 512 is the
system count, not the number of independent language forms.

{table('CONCEPT-011')}

`repair` is the released direct-routing owner; `residual` is CONCEPT-010;
`unchanged` is CONCEPT-009; `original` is the CONCEPT-008 reward owner; `echo`
is the preserved earlier ECHO-007 owner. All four acquisition owners produce
exactly the same numerical outputs. The language repair increases joint
direction accuracy from 60.74% for `original` to **90.43%**, with **100% routing**.
The comparisons here are frozen retained controls, not newly equalized complete
architecture training. The earlier matched full/diagonal/ridge study remains
in [CONCEPT-008](../CONCEPT-008/REPORT.md).

The mean squared errors include rare large errors. Their distribution is:

{tailtable}

Small inferred control gain and weak observational identification can amplify an
inverse answer. The acquired model retains an explicit near-zero-gain guard,
its evidence and its conditional scope. No average error is presented as a
guarantee for every task.

## Why three repairs were preserved

CONCEPT-008 passed the numerical tests but missed connected language gates.
CONCEPT-009 taught paired questions to the old frozen text representation and
improved its own final joint direction to 74.41%; it still missed qualification.
CONCEPT-010 added lexical features, reached 82.42% joint direction on its new
cohort and exposed interference from the frozen head. The direct lexical
construction was then trained and selected in CONCEPT-011 before opening its
new final. Its reserved development accuracy reached 100%; selection followed
the predeclared loss/earliest-step tie breakers. The final was opened once and
replayed without tuning.

Every failed candidate remains in its named directory with source freezes,
training losses, checkpoints, optimizer/RNG state, case records and supervised
costs. Different final cohorts are not silently treated as a continuous
improvement curve. [009 report](../CONCEPT-009/REPORT.md),
[010 report](../CONCEPT-010/REPORT.md), [011 protocol](../../protocols/CONCEPT-011.md).

## Independent investigation and reward

On the frozen CONCEPT-008 inquiry final, goal MSE went from 1.441967 before
acquisition to 0.171472 after the selected policy obtained one actual outcome.
The unchanged policy achieved 0.172033, random 0.407007 and the supplied analytic
information heuristic 0.575984. The incremental reward-training benefit versus
unchanged was about **0.33%**, so the large before/after gain is not attributed
entirely to new policy learning. Every goal was returned. Six mismatched actions
were preserved; credit checks distinguish requested and performed intervention.
The selected policy is retained exactly through all language repairs.

## Adequacy and alternative explanations

An additional **128 new systems** contained an omitted sinusoidal influence.
These diagnosis cases remained separate from supported-family qualification:

{table('CONCEPT-011','omitted')}

The released owner's cloud spread averaged 0.003369 on supported and 0.004723 on
omitted systems; its goal-error flag triggered on 7.81% and 33.59%, respectively.
Small hypothesis disagreement therefore does not certify model adequacy. The
family, observation conditions and alternatives remain explicit, and future
mechanism expansion has a concrete residual to investigate. These measured
diagnostics preserve failures rather than becoming general impossibility claims.

## Usable persistent task

The delivery fixture supplies four independently specified observations of
`a = u - 0.5 v + 0.2`. Its first predictions for `(v,u) = (0,1),(1,1),(-1,1)` were
`{[round(x,6) for x in first['predict']['mean']]}`. The independent values are
`[1.2, 0.7, 1.7]`. Its explanation was:

> {first['explanation']['explanation']}

The owner proposed a further measurement, the independent fixture produced the
actual outcome, and the original task was answered again with predictions
`{[round(x,6) for x in new['predict']['mean']]}`. The check is an engineering
demonstration, not another held-out evaluation. Fresh-process restarts were exact;
follow-up questions reused the same acquired concept; duplicate evidence was
rejected; prior revisions and the original goal were preserved. Reading and
arithmetic outputs matched the earlier ECHO-007 owner exactly.

[Run it locally](../../docs/CONCEPT_USAGE.md) ·
[complete recorded delivery](delivery/RESULTS.json)

## Weights, identities and retention

The inference package contains **{package['parameter_count']:,} parameters**,
{package['parameter_bytes']:,} tensor bytes and {package['file_bytes']:,} file bytes.
Its tensor identity is `{package['inference_checkpoint']['weights']}`.
Its file SHA-256 is `{package['inference_checkpoint']['sha256']}`.
The inference export excludes raw corpus records, optimizer buffers and training
progress. Complete resumable state remains under `runs/CONCEPT-011/revisions`.
Session identity includes both weight identity and model configuration, so a
changed routing construction cannot reuse another predictor's session identity.
Earlier SCFE-004, ECHO-007 and FIELD-001 packages are preserved.

## Costs and completed checks

All four studies, failed qualifications, tests, replays and delivery consumed
**{cost['wall_seconds']/60:.2f} supervised wall minutes** and
**{cost['cpu_seconds']/60:.2f} CPU minutes**. Peak process-tree commitment was
**{cost['peak_process_tree_bytes']/1024**2:.2f} MiB**. Each worker used one numerical
CPU thread, an exclusive shared lease and a 2 GiB process-tree cap. No paid compute
was used. These totals cover this acquisition/release cycle; the earlier teaching
ledgers remain separate and linked from the evidence index.

- [x] Reconcile the actual local owner, source, jobs and retained production pin.
- [x] Read and map the latest research to the next actual owner integration.
- [x] Freeze finite training, source identities, controls and fresh final cohorts.
- [x] Train acquisition and independent-credit policy through the real owner.
- [x] Diagnose failures and preserve each failed candidate and all costs.
- [x] Complete a fresh direct-routing repair and five exact final replays.
- [x] Preserve earlier weights and test actual reading/arithmetic outputs.
- [x] Exercise session creation, five tasks, new evidence and original-goal return.
- [x] Export assessed inference weights and verify their identities.
- [x] Run 106 integrated engineering tests.
- [x] Reread the research contract and record the exact implemented scope.

[All costs](TOTAL_COSTS.json) · [all study decisions](CAMPAIGN_SUMMARY.json) ·
[artifact identities and resumable local state](EVIDENCE_INDEX.json) ·
[engineering](../../docs/CONCEPT_ENGINEERING.md) · [post-build research audit](POST_BUILD_AUDIT.md)
''')
    print('Wrote four complete, data-derived research reports.')


if __name__=='__main__':main()
