# Acquisition connected to five uses

The next implementation addresses the latest synthesis's five-way concept test.
The unit of transfer is a single acquired response law and its observation/evidence
identity, reused without further fitting by prediction, inverse inference,
counterfactuals, planning and bounded language.

[Conditional Neural Processes](https://proceedings.mlr.press/v80/garnelo18a.html)
learn to map observed input-output pairs to a conditional predictor. This motivates
retaining the current observation encoder as the starting prior. [Attentive Neural
Processes](https://arxiv.org/abs/1901.05761) diagnose observation underfitting and use
attention to improve conditioning; that makes context fidelity a concrete competing
mechanism rather than an assumption about an averaged encoder.

[MAML](https://proceedings.mlr.press/v70/finn17a.html) learns an initialization that
adapts through new-task observations. The finite construction here instead learns
the precision governing a small observation-conditioned update. The posterior
solve is engineered and differentiable; its precision and bounded semantic mapping
are trained. A strong fixed ridge control receives the same observations. This
separates the value of acquisition itself from the value of learned regularization.

The parameter family and action search are supplied. A new episode contributes
its actual measurements only; none of its hidden environment parameters are
passed into the learner. Independent DOP853 outcomes check the plan. Measurement
residuals check adequacy separately from disagreement between the three hypotheses.

This is an executable bridge toward the source proposal. Positive-definite
precision is a specific mathematical contract, not a renamed implementation of
SPD stalks, Schubert growth, topological semantic storage or unrestricted
self-improvement. Those directions remain in the original source audit.
