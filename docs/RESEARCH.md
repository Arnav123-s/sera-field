# Research decisions and source identities

The original proposal is preserved byte for byte locally. SHA-256: `b0be4b4aea776bcdfd580e000aebbb1bd7b56523e6b0df32f0c1fdb89fbfc9cd`. I read it before implementation and retain it for the final alignment audit.

## Primary literature

| Source | Relevant result | Decision in this lab |
|---|---|---|
| Favoni, Ipp, Müller and Schuh, [Lattice Gauge Equivariant Convolutional Neural Networks](https://arxiv.org/abs/2012.12901) | Gauge-equivariant operations and loop observables for lattice gauge fields | Implement actual local-frame transport, invariant contractions and learned group links; test the transformation law |
| Lüscher, [Properties and uses of the Wilson flow in lattice QCD](https://arxiv.org/html/1006.4518v3) | The Euclidean gauge flow follows action descent; smoothness and gauge covariance coexist with dissipation | Do not call the source equation nondissipative without specifying a different convention and proving the property |
| Wetterich, [Exact evolution equation for the effective potential](https://arxiv.org/html/1710.05815v1) | Scale-dependent effective action with a regulator and a specified field content | Record regulator, action and representation-birth operator as required definitions; test explicit neural expansion independently |
| Bellec et al., [Biologically inspired alternatives to backpropagation through time](https://arxiv.org/abs/1901.09049) | Forward eligibility information combined with a suitable learning signal approximates recurrent gradient learning | Curvature is not silently substituted for eligibility; initial optimization is explicit and all update states are saved |
| Yoon et al., [Lifelong Learning with Dynamically Expandable Networks](https://arxiv.org/abs/1708.01547) | Selective learning and capacity expansion are classical competing approaches | Compare a fixed-width successor with expansion rather than assume extra dimensions are necessary |
| Assran et al., [V-JEPA 2](https://arxiv.org/abs/2506.09985) | Observation learning, action-conditioned modeling and planning are included | Do not repeat the proposal's blanket claim that this class lacks action-conditioned planning |

The link parameterization and small graph here are my finite engineering interpretation, not an implementation copied from those papers. The physical simulator, action search, verification, context statistics and scientific measurements are also supplied engineering. The learned content is recorded separately: group-link coordinates, radial gains, readouts, physical coefficient functions and context-conditioned residual behavior.

## Why these first tests

A model that uses one learned mechanism for several tasks is a direct way to test the user's intended integration. Coordinate changes should leave physical conclusions consistent; a changed mass should change a conditional conclusion. The same distinction applies later to grammatical perspective and semantic change, but physical covariance alone does not establish language grounding.

The new weights begin as random Lie-algebra coordinates, radial gains and scalar readouts. They are trained on position-derived physical consequences. No pretrained language model or earlier SERA checkpoint supplies the answers. A simple fitted power-law control provides a strong comparison for this first physics family; its structural assumptions and small parameter count are disclosed.

I treat boundary activity as transient and persistent connections as learned state. Exact counterfactual isolation is implemented and tested explicitly. Memory robustness, empirical correctness and formal proof remain separate contracts so that stable errors cannot earn verification credit.
