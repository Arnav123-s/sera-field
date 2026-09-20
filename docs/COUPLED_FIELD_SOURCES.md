# Primary-source contracts for the coupled field

The latest supplied bibliography was checked against primary papers. The following
are implementation contracts, not evidence that a proposed SERA capability already
exists. Source versions are pinned where available.

- [SPD sheaves, Peng et al., v1](https://arxiv.org/html/2604.20308v1): orthogonal
  congruence restrictions and the group law `exp(log P + log Q)` provide the
  explicit matrix-valued construction. The implementation chooses this log-group
  metric and tests its operators directly; broad expressive-superiority claims
  in the paper are not needed for correctness.
- [Recurrent Hamiltonian Echo Learning, v1](https://arxiv.org/html/2506.05259v1):
  reverse timed sources and loss impulses for reversible discrete dynamics.
  Finite perturbation errors require gradient checks. Input history, returned
  sequence outputs and scratch work remain in memory accounting.
- [Diffusive Fitzhugh-Nagumo equilibrium credit, v1](https://arxiv.org/html/2605.21568v1):
  the result concerns a specified stationary/spatial construction. It does not
  license reversing arbitrary dissipative temporal trajectories.
- [Nonreciprocal conserved fields, v3](https://arxiv.org/html/2306.08868v3):
  phase separation and nonreciprocal coupling have distinct stability contracts.
  The initial memory operator uses reciprocal scalar conserved flow so its
  energy and mass can be audited; nonreciprocal modes require separate evidence.
- [Discrete Chern calculation, Fukui et al.](https://arxiv.org/abs/cond-mat/0503172):
  normalized overlap links on a periodic momentum lattice provide a numerical
  charge audit. The semantic codec, finite range and revision protocol are new
  engineering choices. A spectral gap and specified perturbation class matter.
- [Wetterich effective-action equation](https://arxiv.org/abs/1710.05815) and
  [NN/QFT finite models, v2](https://arxiv.org/html/2108.01403v2): a regulator and
  effective-action truncation must be stated. A capacity-attachment rule is an
  additional hypothesis, not a consequence of the trace equation alone.
- [Measurement-only topological computation](https://arxiv.org/abs/0802.0279):
  fusion measurements have outcomes and resource costs. A simulated application
  must retain all branches and specify its computational encoding.
- [Eligibility propagation](https://arxiv.org/abs/1901.09049): local eligibility
  derivatives and learning signals are distinct from activation strength or
  an arbitrary surprise score. Existing score-function traces keep their own name.

The larger proposal combines these sources into a new architecture. The coupled
update, semantic maps, curriculum and acceptance tests therefore require their
own evidence even when an individual mathematical operator is valid.
