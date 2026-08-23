# Status: Cogym Trading v1

## Executed in this artifact build

- Python compile/import path exercised through pytest.
- 16 unit/integration tests pass.
- offline A-F smoke experiment runs all six conditions;
- offline persistent Master -> successive Students loop runs end-to-end;
- canonical world replay, point-in-time filtering, commit/reveal, Pack validation, social revision, dose response, persistence, team and evidence graph paths are tested.

The offline model is a **harness test double only**. Its behavioral differences are deliberately not scientific evidence for LLM induction.

## Implemented and ready for real-model experiments

- OpenAI-compatible chat adapter;
- deterministic market worlds;
- A-F runner;
- stochastic repeats;
- structured decision scoring;
- Master/Student Dojo;
- treatment/persistence/team/social/contagion experiments;
- candidate Packs;
- local evidence graph and Hydra projection format;
- proof/receipt boundaries.

## Explicitly not claimed as integrated

- HydraDB remote write API: export boundary exists, deployment adapter must map to the current account/schema and be tested with credentials.
- DeepProve: external proof registration/verifier hook exists; Cogym does not generate proofs itself.
- blockchain settlement: chain-agnostic commit/reveal is implemented, no chain contract is shipped.
- proprietary-model attestation: provider dependent.
- mechanistic activation tracing: requires open-model inference instrumentation.
- real market feed collection: CSV ingestion is implemented; provider collectors are intentionally outside the core.
- TTS/rendering/Molts.live: extension contract only, not part of the trading research MVP.

## Why these boundaries are intentional

The first empirical gate is whether live sequential context pathways produce reproducible, held-out behavioral/capability changes in actual LLMs. Infrastructure that does not help answer that question stays outside the hot loop.
