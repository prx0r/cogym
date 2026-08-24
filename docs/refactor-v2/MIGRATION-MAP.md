# Migration Map — v1 concepts → generic contracts

| v1 (trading-coupled) | v2 (generic) | Status |
|---|---|---|
| `TradingWorld` + `WorldManifest.world_id` | `World` protocol + `WorldSpec` | ✅ adapted (`worlds/trading/adapter.py`) |
| `MarketPacket` observation | plain dict from `world.observe(state)` | ✅ done |
| `Decision(LONG/FLAT/SHORT)` | `ActionSpec(kind="DECIDE", payload={"stance": …})` | ✅ done |
| `AgentGenome` (reasoning/memory/social fields) | `CandidateArtifact(kind, version, config)` | ✅ done (PR2) |
| `BenchmarkResult(mean_reward, calibration_error, max_drawdown…)` | `MetricVector(Metric(name, value, direction, slice))` | ✅ done (PR8 of core) |
| `fitness()` scalar | `QualityGate` tuple + lexicographic comparator | ✅ done (PR3) |
| unpaired score comparison | `non_inferior_paired` bootstrap CI on matched instances | ✅ done (PR3) |
| evolution_lab campaign internals | `Campaign` + `CampaignConfig` in core | ✅ minimal port (PR4); successive halving still to port |
| live-only execution | `ReplayTape` / `TapeExecutor` / `RecordingExecutor` | ✅ done (PR7) |
| ad-hoc parallel receipts | wave canonicalization: sort by action_id | ✅ done (PR7) |
| package name `cogym-trading` | package name `cogym` v2.0.0 | ✅ done (§2) |
| no world discovery | `cogym worlds` CLI + `worlds/registry.py` | ✅ done (§53) |

## Still to migrate (in spec order, factminer.md §67)

| PR | What | Source material |
|----|------|-----------------|
| PR8 | FactWorld offline (dataset adapter, phenotypes, attacks, static baselines P0–P5) | FactJudge frozen splits; new `worlds/factcheck/` |
| PR9 | Retrieval providers (Tavily/extract/registry, async waves, instrumentation) | new `executors/search.py` |
| PR10 | Verified graph cache + EvidenceGraph promotion out of culture/ + Hydra projection | `culture/evidence_graph.py`, `culture/hydra.py` |
| PR11 | Adaptive policies (typed routing, early stopping, attack ordering) | new |
| PR12 | Constrained cost/latency campaign on factcheck.replay | Campaign machinery (done) |
| PR13 | Live retrieval → capture replay tapes | RecordingExecutor (done) |
| PR14 | Telegraph adapter | blocked until PR12 produces a validated policy |

## Successive-halving port backlog (from evolution_lab, §11)

- fresh secret seeds generated after candidate freeze
- per-metric elites → replace with config-driven archive niches
- dev/validation/secret three-layer suite as `evaluation/suite.py`
- proposal provenance records → `optimization/proposal.py`
