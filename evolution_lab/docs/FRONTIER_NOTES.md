# Frontier grounding (August 2026)

These notes explain why Cogym separates integrity, inference proof, and capability evidence.

- Lagrange DeepProve reports end-to-end zero-knowledge proofs of LLM inference, including full transformer execution; this supports an optional external proof adapter for supported open models.
- A proof that a specified model executed on a specified committed input establishes execution integrity, not that the resulting decision is economically good or that a cognitive pack generalizes.
- Current agent-trading literature emphasizes large differences caused by agent architecture and poor reproducibility/evaluation standards across studies. Cogym therefore freezes world instances, private decisions, social revision, and outcome horizons explicitly.
- Multi-agent/economic benchmarks show useful emergent behavior only when full trajectories and economic state are logged, reinforcing the decision to preserve immutable run records rather than only final PnL.

Primary public references consulted during design:
- https://lagrange.dev/engineering-updates/inside-deepprove-proving-an-llm-end-to-end
- https://lagrange.dev/deepprove
- https://arxiv.org/abs/2510.11695
- https://arxiv.org/abs/2605.19337
- https://arxiv.org/abs/2604.05523
