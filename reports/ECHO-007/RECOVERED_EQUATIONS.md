# Equations recovered from the preserved original

The new pasted copy has 19 literal `image` placeholders. The earlier original
does retain LaTeX: `intake/original-proposal.txt`, SHA-256
`b0be4b4aea776bcdfd580e000aebbb1bd7b56523e6b0df32f0c1fdb89fbfc9cd`.
These two equations are copied from that user-provided source, not reconstructed:

$$
\frac{\partial \mathcal{A}_\mu}{\partial t}
=\mathcal{D}^{\nu}\mathcal{F}_{\nu\mu}
+\mathcal{P}_{\mathrm{boundary}}\left(\frac{\delta\Gamma_k}{\delta\Phi}\right).
$$

$$
k\frac{\partial\Gamma_k}{\partial k}
=\frac12\operatorname{Tr}\left[(\Gamma_k^{(2)}+\mathcal R_k)^{-1}
k\partial_k\mathcal R_k\right]
+\mathcal H_{\mathrm{bridge}}\left(\int dt\;\mathcal F_{\mu\nu}\mathcal F^{\mu\nu}\right).
$$

## Executable scope and repair

In a Euclidean metric with the usual positive gauge action and vanishing boundary
flux, the first term is a gradient flow. If the boundary projection is zero,
`d S / dt = - ||D F||^2`. The absence of an explicit term named damping does not
make that flow reversible. A concrete abelian transverse mode is
`A_y(x,t)=exp(-t) sin(x)`, `A_x=0`: the stated flow satisfies
`partial_t A_y=partial_x^2 A_y`, and its energy decreases as `exp(-2t)`.
This is a scoped mathematical diagnosis, not a verdict about the whole proposal.
The operator is consistent with the [Wilson-flow formulation](https://arxiv.org/abs/1006.4518).

The implemented repair separates the operations: the trained SCFE field retains
its explicit dissipative settling, while ECHO-007 introduces position/momentum
and a reversible Hamiltonian flow for the echo-learning experiment. Parameter
capture/optimization occurs afterward. It tests the intended reversible-credit
behavior without describing the original gradient flow as reversible.

The second equation needs a field space, regulator, functional approximation and
definitions of both bridging maps. Changing effective interactions with scale
does not specify a coordinate-attachment operator. Those concrete choices and
retention tests are required before labeling any growth rule the supplied ERG.
The recovered source does not define them. The later Singular Ecosystem instead
proposes cohomology-based attachment; both directions remain preserved.
[Wetterich's original equation](https://arxiv.org/abs/1710.05815) describes the
scale dependence of an effective action; the proposed cognitive attachment and
semantic maps are additional research constructions.

Gauge changes leave observables unchanged. A changed mass requires a different
physical assumption or intervention. The factual/hypothetical separation must
also be enforced by the actual coupling and evidence paths, not inferred from
names such as boundary and bulk. Existing independent checks remain in place
while those operators are developed.
