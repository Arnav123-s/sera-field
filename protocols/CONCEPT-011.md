# CONCEPT-011: repair measured routing interference

Freeze before training. CONCEPT-010 completed and its final is closed. Its
post-final diagnostic on 80 unique already-opened questions measured 71.25%
for the frozen head, 93.75% for its learned residual alone and 85% for their sum.
This is diagnostic evidence, not a fresh qualification. The residual was trained
to compensate for a highly confident frozen head; retaining its sum can override
useful new lexical evidence. Preserve that entire failed study.

Train a direct word/character-hash routing map from new zero-initialized weights
on the same 388 supplied training phrases and identical 2,048 x 32 schedule,
seed 10110, lr .01, weight decay .001, noise .01 and losses as CONCEPT-010.
Start from the selected CONCEPT-009 owner; all of its parameters are protected.
The old question-head weights stay in the checkpoint but this bounded interface
uses the new learned map alone. No other behavior changes.

Freeze 64 development and 96 final questions with new sentence forms and taught
variable vocabulary before training. Require exact disjointness and no reuse
of the CONCEPT-010 development/final phrases. Select by development accuracy,
loss, then earliest step. There is one candidate and no hyperparameter search.
Keep exact RNG/optimizer resume state and count all 65,536 presentations.

Register five owners before opening a fresh 512 supported +128 omitted-system
cohort: direct candidate, frozen CONCEPT-010 residual candidate, CONCEPT-009,
CONCEPT-008 reward owner, and ECHO-007. Same cases and five uses per owner.
Five independent fresh-process replays are required. Frozen controls are exactly
named, not presented as newly matched retraining.

Keep the original gates: routing >=90%, joint direction >=80%, joint direction
at least .1 above CONCEPT-008; exact four numerical outputs versus CONCEPT-009;
all parent weights retained; forward/inverse/counterfactual MSE <=.8 ECHO-007,
plan MSE <=.9 ECHO-007. Record uncertainty failures on omitted mechanisms.
No repeated tuning on this final. Passing ends this repair cycle and permits
the persistent five-use task release. Earlier failures stay in the report.

One numerical CPU thread, exclusive shared lease, 2 GiB process-tree cap,
no paid services. The added router is learned from supplied annotations; it
does not establish unrestricted language interpretation or concept discovery.
