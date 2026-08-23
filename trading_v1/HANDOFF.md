# Coding-agent handoff

## Mission

Run the first real-model Trading Cogym experiment without expanding architecture.

Primary hypothesis:

> A live self-generated context pathway can produce a reproducibly different trading-decision regime from a static primer or summary, and state-transfer fidelity can be measured over deterministic hidden market worlds.

## Repository map

- `cogym/market/`: deterministic worlds, point-in-time packets, CSV ingestion, commit/reveal challenge.
- `cogym/agents/`: model adapters, structured observable decision artifacts, sessions.
- `cogym/state/`: pathways, checkpoints, transmissions, Packs, behavior signatures, ablation candidates.
- `cogym/experiments/`: A-F, repeated-run scoring, treatments, persistence, social, teams, contagion, dose, composition.
- `cogym/dojo/`: persistent Master, fresh Students, multiple Masters, transmission chains.
- `cogym/culture/`: append-oriented local evidence graph + provider-neutral Hydra projection.
- `cogym/proofs/`: experiment receipts and external proof verification boundary.
- `packs/`: candidate intervention protocols; none are certified.
- `specs/`: contracts and experimental rules.

## First real-model run

1. Pick one reasonably cheap chat model and one provider.
2. Freeze provider/model/version metadata.
3. Use synthetic levels 2-6, 4 seeds each = 20 hidden worlds.
4. Pick `trading_regime_shift_v1` or `trading_falsification_v1`.
5. Run A-F with 5 samples per condition initially.
6. Inspect within-condition variance and effect size; increase repetitions if noisy.
7. Repeat the strongest condition with reset vs persistent context.
8. Only then test dose 0/1/2/3 and Pack ablations.

## Real-model wiring

Use:

```python
OpenAICompatible(model_id, base_url, api_key)
```

Do not commit API keys. Provider-specific retry/rate-limit logic belongs in a wrapper outside the experimental objects so failed requests are visible rather than silently changing conditions.

Record provider request IDs if available by extending `ChatModel` with an instrumented adapter; do not change benchmark semantics.

## Evidence discipline

Every real run should append:

- full world/condition/model metadata;
- transcript/checkpoint commitment;
- raw output and parsed decision;
- sample seed request and temperature;
- score/outcome;
- evaluator version;
- failure metadata if a request failed.

Do not discard malformed outputs: parse failure is itself agent behavior. The current parser maps it to neutral for execution; store the raw text and parse-failure indicator when expanding evidence records.

## Hidden-test discipline

The Master may see diagnostic training worlds and post-teaching validation summary. It must not see final hidden-test worlds during iterative teaching. After the Master/Pack is frozen, evaluate once on hidden test.

## Next code changes justified by evidence

### If A significantly beats F (summary)
Implement better trace transforms and state-transfer metrics; study live-generation dependence.

### If B approaches A
Checkpoint Packs are promising; benchmark portability across sessions/providers.

### If A > B
Live self-generation appears important; prioritize transmission/pathway optimization rather than transcript packaging.

### If dose 3 beats dose 1/2
Search for minimal causal pathways via held-out step ablation.

### If persistent context hurts after regime shifts
Implement explicit washout/recovery protocols and memory-aperture experiments.

### If social revision helps
Expand social topology, identity/reputation visibility and leader/follower learning.

### If Master teaching gain improves across students
Persist Master evidence into the graph; add Master succession and multiple-master evolutionary selection.

## HydraDB wiring

Keep SQLite evidence as the canonical local experiment ledger. Map only outcome-bearing/validated events into HydraDB. Recommended conceptual mapping:

- knowledge: world-level validated market/method facts;
- memory: Master reflections, transmission outcomes, method lessons;
- relations: Master -> authored -> Transmission; Transmission -> changed -> BehaviorSignature; Run -> evaluated_on -> World.

Use `HydraProjectionRecord` as the stable boundary. Implement the remote adapter against the exact current HydraDB tenant/schema/API rather than changing core run objects.

## DeepProve / attestation wiring

Do not prove every development run. For a frozen candidate Pack/model:

1. commit exact model/input/output artifacts;
2. use the supported external prover for selected challenge executions;
3. register proof files with `ExternalProofArtifact`;
4. verify with the actual verifier command;
5. include proof refs in a higher-level certificate.

Capability delta remains a statistical benchmark claim, not a cryptographic theorem.

## RoboBladez/Molts.live

Do not merge repos. Reuse protocol ideas:

- sealed participant artifact;
- commit before exact seed;
- deterministic simulator truth;
- immutable replay/canon;
- presentation downstream.

A future generic `CogymWorld` protocol should only be extracted after Trading Cogym and RoboBladez both demonstrate the same boundary in practice.
