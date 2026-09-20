# ECHO-007: full reversible field credit in the actual continuing owner

Freeze this protocol and executable identities before training. Preserve the
SCFE-004/006 release and all its opened final cohorts. This is continuation from
weights trained from scratch in this lab, not an import from another model.

## Operators and qualification

Use the existing Cl(3,0) sheaf action as a canonical Hamiltonian potential.
Position and momentum evolve with symmetric velocity Verlet, 32 steps of 0.025.
Fixed coordinates are the source, prior, edge restrictions, stiffness and quartic
strength; their conjugate momenta accumulate the corresponding analytic local
forces. Symmetric terminal error impulses of magnitude 0.0001 produce credit for
all fixed coordinates and both initial canonical states. Internal arithmetic is
float64. The owner interface remains float32. The prior contributes both as a
potential parameter and as the initial position. Both paths must be included.

The numerical backward rule uses two echoes and no trajectory autograd tape.
Autograd remains available for local encoders, readouts and the restriction-to-
rotor chain rule. Do not call this a complete e-prop or all-biological learner.
Before training, require full-state reversal, independent autograd and directional
finite-difference agreement for every coordinate, initial-state chain-rule tests,
detached outputs, immutable source state and actual owner loss-gradient agreement.

## Finite teaching and selection

Three arms start from the same saved qualified owner and initialization seed 7107:
`echo`, identical dynamics with `autograd`, and `no_core_credit`. Each completes
2,048 updates of 24 examples, using the established mixed subject schedule and
human-source manifests. AdamW learning rate 0.0003, weight decay 0.0001, gradient
clip 3. The no-core arm detaches all field features; its field parameters do not
receive gradients. Investigation weights are retained and not retrained here.
Use distinct physics split `ECHO-007-teaching-v1`. Log every attempted update,
unique source exposure, selected and later revisions, RNG and optimizer state.

Development uses 128 reading, 128 arithmetic, up to 32 source pairs per available
track and 128 physics systems. Use deterministic ECHO-007 group ordering and
split `ECHO-007-development-v1`. Evaluate at zero and every 512 updates. Select
minimum equally weighted relative loss over reading, arithmetic, pairs and
physics; the denominator is that arm's zero-step loss. Earliest update wins ties.

## Independent evaluation and decision

Before opening final data, jointly freeze every selected file/weight identity.
Use 512 reading and 256 arithmetic examples from source groups untouched by the
CONNECTED-003 final. Record all selected groups, including unused group tails.
Use up to 64 eligible pairs per track from untouched groups; disclose shortfall.
New physics split `ECHO-007-final-v1` has 512 systems. Include 128 transferred
trajectories and 256 original-goal investigations with independent outcomes.
Evaluate echo, autograd, no-core and preserved parent on the same cases.

Promotion requires: echo reading accuracy at most 2 percentage points below the
parent; arithmetic, pair-loss and physics MSE at most 5% worse; investigation MSE
at most 10% worse; finite trajectories in all cases; no evidence/weight mutation;
and echo mean normalized objective no more than 5% worse than the exact-gradient
arm. Otherwise keep it as an experimental owner and preserve the useful release.
The check is finite and does not establish a universal architecture ranking.

Replay final raw records in a fresh process with frozen identities. A real defect
gets its own recorded repair and new evaluation if necessary; no final tuning.
Retain failures, all three arms and every supervised cost. One numerical CPU
thread, shared exclusive lease, 2 GiB process-tree cap, no paid compute.
