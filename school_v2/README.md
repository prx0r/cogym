# Cogym School v0.2

A minimal production-oriented protocol for **backtesting cognition, evolving task-specific schools, and compiling their learned intelligence into portable Cognitive Packs**.

Cogym treats market environments as one benchmark substrate, not as a real-money execution system. The included examples are simulation/research only.

## Core objects

- **World** — deterministic/forkable benchmark state.
- **Agent** — model + private memory + current Pack.
- **School** — curriculum + participant runs + evolving Hydra memory.
- **Pack** — content-addressed context program compiled from school intelligence.
- **Behavioral basin** — empirically measured output distribution a Pack tries to reproduce.
- **Certificate** — benchmark evidence, optionally linked to zkML inference proofs.

## Minimal stack

- Rust protocol core: canonical commitments, Pack/world/school objects.
- Rust adapters: HydraDB REST, OpenAI-compatible LLM APIs, external DeepProve wrapper.
- HydraDB: distilled experiential/method memory only.
- Files/object storage: immutable worlds, blobs, traces, certificates.
- Optional chain: commitments/licensing/settlement only; never the simulation hot path.

## Pack thesis

A long curriculum may move an agent into a useful behavioral/capability basin. A Pack asks whether that trajectory can be compressed into a smaller context program that reproduces the same held-out behavior. This is context engineering, not weight training.

See `spec/INDUCTION.md`, `spec/PACK.md`, `spec/SCHOOL.md`, and `spec/PROOFS.md`.

## Validation

`python tools/conformance.py`

A tested Python reference harness from Cogym v0.1 is retained in `reference_python/` for deterministic world/social/pack regression tests. The Rust workspace is the intended production core.
