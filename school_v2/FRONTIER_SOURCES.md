# Frontier sources consulted (Aug 20 2026)

- Geoffrey Huntley, Loom: https://github.com/ghuntley/loom
  - Rust agent architecture; modular provider/tool abstractions; persisted threads; server-side LLM proxy; structured telemetry. Repository warns it is experimental/unstable and is proprietary, so Cogym uses it only as an architectural reference.
- Lagrange Labs, DeepProve: https://github.com/Lagrange-Labs/deep-prove
- Lagrange engineering deep dive, Aug 3 2026: https://lagrange.dev/engineering-updates/inside-deepprove-proving-an-llm-end-to-end
  - End-to-end LLM inference proving for supported open models; proves the computation for a committed model/input/output, not downstream expertise.
- HydraDB API: https://docs.hydradb.com/api-reference
  - Official Python/TypeScript SDKs; Rust integration here uses the documented REST API directly.
- BEAM/LIGHT: https://github.com/mohammadtavakoli78/BEAM
  - Episodic memory + working memory + compressed scratchpad.
- ReasoningBank: https://arxiv.org/abs/2509.25140
  - Distills reusable reasoning memories from success and failure.
- MemEvolve: https://arxiv.org/abs/2512.18746
  - Evolves memory encode/store/retrieve/manage architectures.
- Enhancing Reasoning with Collaboration and Memory: https://arxiv.org/abs/2503.05944
  - Varied contexts and exemplar memories can help or distract; supports benchmarking context policies instead of assuming more memory is always better.
