# Design synthesis

Cogym combines four older ideas into one minimal protocol:

- **EvoLabz:** compile noisy raw markets into compact multiscale world-state geometry and transition dynamics.
- **PZL:** Constructor -> bounded scenario -> seeded instance; deterministic engine contract and exact replay.
- **Hydra-style memory:** longitudinal experiential memory for an agent/lineage rather than storage of raw world truth.
- **Evolution loop:** variation -> objective outcome -> retained patterns -> descendants, with increased exploration on plateaus.

## World packet geometry

A packet is intentionally both raw-ish and compressed. Agents receive rolling returns plus normalized state descriptors. Future extensions can add standardized macro, fundamentals, order-book, news, project revenue or on-chain features while preserving the same object interface.

The target is not "more data always". It is maximal ability to reconstruct what information existed at decision time.

## Two evolutionary layers

1. **Organism evolution** — mutate model composition, reasoning policy, representation, memory, social structure and plasticity.
2. **Curriculum evolution** — mutate worlds toward the current capability boundary: shocks, regime breaks, deceptive patterns, social traps, information asymmetry.

The most interesting long-run experiment is coevolution, but fixed exogenous worlds remain mandatory as scientific controls.

## Blockchain

Blockchain is optional and belongs at the trust/market layer, not the inner simulation loop. Useful commitments include pack ID, world ID, benchmark suite ID and external proof reference. Heavy raw trajectories remain off-chain.

A future marketplace could therefore verify that a purchased pack is the committed artifact and, where zkML supports the chosen model, verify specific benchmark inferences. Economic settlement can be added later without making the research engine dependent on a chain.
