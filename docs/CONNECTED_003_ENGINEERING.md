# Connected human learning and empirical imagination

`GroundedOwner` owns freshly initialized word embeddings, local phrase filters,
SU(2) links, the finite boundary action, task readouts and investigation policy.
No pretrained encoder, earlier SERA weights or delegated checkpoint is loaded.
The mathematical field action remains specified in CONNECTED_CORE.md.

SCFE-004 replaces that owner's field with `CliffordSheafField`: eight graded
Cl(3,0) coefficients per vertex, rotor-induced restriction maps, the true adjoint
coboundary and an explicit quartic phase potential. All task readouts use this
same field; its weights are trained from the first update. The two owners each
receive the frozen teaching schedule independently. `PRIMARY_OWNER.json` records
the Clifford/sheaf research choice before final opening. Both variants and their
distinct source/checkpoint identities remain preserved.

All text is tokenized with offsets under a stable hashed vocabulary. Long inputs
are chunked with two-token overlap around a five-token filter; every token
contributes exactly once to the pooled representation. No question or source is
prefix-truncated. This is pooled long input, not a claim of unrestricted narrative
memory. Learned question/candidate interactions and observed lexical overlap enter
the field; hidden annotations are read only by the loss/checker.

Human reading trains evidence-sentence selection from every sentence in the given
passage. Arithmetic trains a scored joint distribution over operation and operand
pointers, and constructs executable rational expressions from that distribution.
Teacher-forced earlier human calculations are explicit. The operation vocabulary
and candidate number inventory are supplied; outputs are generated before the
independent exact check. Commutative aliases share the training target and are
deduplicated in reporting.

Dictionary entries, consecutive conversation turns, book passages and human
programs provide source-pair teaching. Four candidates are formed without
correctness features; competing candidates come from the same source track.
Association accuracy does not certify a philosopher's intended meaning or arbitrary
program correctness. Those require additional independent behavioral assessments.

The physical path encodes measured velocity, force per mass and acceleration, plus
an explicit missing-observation mask. It infers three coefficient hypotheses in
a supplied observable basis. No true coefficient/family indicator reaches this
path. The hypotheses predict requested consequences and probe outcomes. A learned
policy sees those predictions and the original goal, then samples an intervention.

Before obtaining an outcome, CreditBridge records the policy derivative, policy
identity, chosen action, assumptions and original goal. A separate simulation
module performs the action, records actual actuation and evaluates pre/post goal
errors on withheld outcomes. Real progress supplies positive or negative credit;
imagination and confidence supply none. Incorrect actuation retires credit. The
scope/contribution key does not include the goal name, so renamed goals cannot
renew novelty. The reward study holds the acquired predictor fixed and updates
only the policy to isolate acquisition learning; this is not a claim of improving
every part of the owner at once.

All failed attempts remain in invocation-specific journals. Atomic, content-hashed
revisions include the owner, both relevant optimizer states, pending/consumed
credit, all RNGs, human permutations, stream cursors, unique-exposure inventory,
development history and best selection. A resume preserves uncommitted journals
as historical incurred work and starts a new invocation journal, without deleting
or double-counting them as accepted training state.

Design references, read as competing mechanisms rather than imported capabilities:

- [BiDAF](https://arxiv.org/abs/1611.01603): query/context interaction and avoiding
  premature loss of evidence. This implementation is a smaller pooled field
  reader, not the BiDAF architecture.
- [Eligibility propagation](https://arxiv.org/abs/1901.09049): distinction between
  temporal local traces and the exact single-decision score derivative used here.
- [MBPP authors](https://arxiv.org/abs/2108.07732) and the pinned publisher README:
  human program provenance and original split definitions.
- [Publisher repository license](https://raw.githubusercontent.com/google-research/google-research/4700efb9afa54286b0e04473ba80a13e8461e25f/LICENSE):
  the pinned repository-level Apache-2.0 notice; raw data are retained locally.
