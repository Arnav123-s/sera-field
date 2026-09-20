# One acquired model, five uses

I connected the latest proposal's single-concept test to the actual continuing
SERA Field owner. Its previously taught word and observation encoders, Clifford
sheaf field, reversible field-credit implementation, mathematical readouts and
investigation policy remain in the same checkpoint. The new learning procedure
turns a small set of observations into a reusable local response model.

## Observed situations and learned updates

Each observation records velocity `v`, calibrated control input `u` and measured
acceleration `a`, together with a source identity. The supplied representation is

```
phi(v,u) = [u, v, v*abs(v), 1]
a(v,u)   = phi(v,u) c
```

The four coefficients represent input gain, linear velocity response, signed
quadratic response and a constant offset. This finite curriculum includes both
actuator orientations, resistive and active responses, and zero terms. It is an
identified local control/response family. Observation noise has standard deviation
0.03. An additional sinusoidal influence is reserved for adequacy diagnostics.

The existing field produces three prior coefficient hypotheses and a situation
vector. A trained network maps that vector to a positive-definite precision
matrix `P = L L^T + 1e-4 I`. Given the observed design matrix `X` and outcomes `y`,
each prior `c_h` is revised through

```
c'_h = c_h + solve(X^T X + P, X^T (y - X c_h)).
```

Differentiation through this small solve teaches the precision network how to
condition a response model on a new set of observations. Full and diagonal
precision receive matched training; fixed ridge receives identical observations
as a separate control. The solve and basis are engineering. Precision weights
and the observation-conditioned coefficients are acquired through teaching and
evidence. Hidden simulator coefficients are never learner inputs.

## Transfer without refitting the acquired concept

The content-addressed concept contains its three coefficient hypotheses,
observation rows, evidence identities and predictor hash. The same concept is
reused for all of the following, without a separate task-specific fit:

| Use | Operation | Independent check |
|---|---|---|
| Prediction | Evaluate new velocity/input points | Simulator outcomes withheld from acquisition |
| Inverse answer | Solve for input given desired acceleration | Actual input that generated the target |
| Counterfactual | Change velocity and input on a conditional branch | Outcomes under the changed inputs |
| Planning | Imagine trajectories under 41 bounded constant controls | Separate DOP853 integration of the chosen action |
| Grounded explanation | Learn the requested variable and direction at an operating point | Independently measured finite difference |

The direction head is taught decreases / approximately unchanged / increases for
a +0.5 variable change, using a 0.08 acceleration tolerance. Its input is the
acquired coefficients, operating point and selected variable. A supplied sentence
form renders the learned decision. The final question cohorts test new phrasing
of the two taught variable roles. Their phrase counts and system counts are
reported separately because repeated question forms are not independent language
examples.

Planning retains five ranked action alternatives and the three corresponding
imagined endpoints. A route to an endpoint is qualified by its independent
outcome, not by the owner's confidence. An inverse response with near-zero input
gain has an explicit validity guard.

## Investigation and actual reward

The existing policy receives the situation, candidate probes and original goal
queries. It selects an observation. An independent simulator reports both the
requested and actually performed action. New measured evidence updates the
concept; the learner then answers the original goal again. The checker measures
before/after error on independent goal outcomes.

Credit binds goal, decision, predictor, policy version, source, verifier and
evidence. Duplicate or stale credit is rejected. Periodically mismatched
actuators retain their actual observations but earn no credit for the requested
action. Imagined outcomes remain conditional records and never become measured
facts. The new reward study preserves all 2,048 attempts and its selected policy,
as well as unchanged, random and analytic alternatives.

## Persistent use and audit

A task session stores the original goal, acquired concept and predictor identity.
New measurements append a new revision; the original revision remains available.
Optimistic single-writer checks reject stale updates. Repeated questions reuse
the acquired concept. Earlier human-reading and mathematical weights remain
exactly retained, with contract checks for their actual outputs.

Every final cohort is frozen and opened once, then replayed in a new process.
Failed qualification creates a new named repair study, fresh cohort and retained
cost record. The unchanged earlier result is never overwritten by its repair.

## Relationship to the research proposal

This integration implements the proposal's finite five-use concept connection.
It uses the actual Clifford/sheaf owner and preserves the previously trained
reversible field operator. Positive precision has the specific contract above;
its name does not establish an SPD-valued sheaf. The original mathematical
contracts for time-dependent Hamiltonian credit, condensate memory, semantic
topological storage, structural growth and anyonic alternatives remain in the
[source-by-source audit](../reports/ECHO-007/NEW_SYNTHESIS_AUDIT.md).

Research sources and the alternatives considered are linked in
[the acquisition review](CONCEPT_008_RESEARCH.md). Training objectives, supplied
information, preserved failures and exact metrics are in the numbered reports.
