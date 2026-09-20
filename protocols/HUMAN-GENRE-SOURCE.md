# Human genre source preparation

This is a data-preparation contract, frozen before model use of MultiNLI. It does
not alter the active HISTORY-016 training or open that study's final predictions.
The official MultiNLI 1.0 archive is preserved with its byte identity, attribution,
license references and intake costs. Only source views are created.

1. Keep the original premise and hypothesis text unchanged in each view. Retain
   original pair/prompt IDs, genre, label votes, member name and line number.
2. Use normalized premise text only to identify shared situations, with Unicode
   normalization, case folding and collapsed whitespace. All rows describing that
   same premise stay on one side of a split.
3. Exclude premises already present anywhere in the prior SNLI source bank. This
   conservative rule protects old assessments and makes the new source's later
   transfer cohort distinct. Record every excluded ID and reason locally.
4. Preserve the released matched and mismatched validation groups for later sealed
   evaluation. If a normalized premise appears in both, mismatched takes priority
   and its matched rows are excluded. Do not train on either released view.
5. Split eligible original training groups by the SHA-256 of
   `SERA-human-genre-v1|` plus the normalized-premise digest: remainder zero modulo
   20 goes to development, all others to training. This rule uses no label.
6. Exclude missing-consensus labels. Exclude all occurrences of a normalized
   premise/hypothesis pair with conflicting supplied labels. Deduplicate matching
   text/label pairs within their assigned split, preserving source records and
   exclusion identities. The raw archive always retains the original ambiguity.
7. Save immutable view hashes, source-group partition hashes, per-genre and label
   counts, exclusions, producer identity and exact wall/CPU preparation costs.

No model predicts these records during preparation. Final labels remain outside
model training and selection. Any subsequent numerical curriculum, noise study,
procedure repair or broader transfer claim requires its own prospective protocol
and an identified qualified parent. Raw corpus views stay local.

Sources: [authors' corpus page](https://cims.nyu.edu/~sbowman/multinli/) and
[Williams, Nangia and Bowman, 2018](https://aclanthology.org/N18-1101/).
