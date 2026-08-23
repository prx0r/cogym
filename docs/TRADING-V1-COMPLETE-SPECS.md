# Trading V1 — Complete Spec Inventory
2026-08-23 · What the original implementation actually built

## Modules (all tested, 16/16 green)

| Module | Lines | Purpose |
|--------|-------|---------|
| market/world.py | 55 | TradingWorld + WorldManifest + MarketPacket (point-in-time safe) |
| market/synthetic.py | 90 | WorldSpec generator, levels 0-6, Regime dataclass |
| market/challenge.py | 43 | Commit-reveal anti-theatre protocol |
| market/features.py | ~40 | EvoLabz state geometry: direction, vol, drawdown, momentum |
| market/csvio.py | ~30 | CSV OHLCV ingestion for real historical data |
| agents/model.py | ~60 | ChatModel protocol + OpenAICompatible + HarnessTraderModel |
| agents/decision.py | 57 | Decision dataclass w/ stance, probs, confidence, crux, claims, falsifiers |
| agents/trader.py | 38 | market_query() + decide() using DECISION_CONTRACT prompt |
| agents/session.py | 24 | AgentSession for conversation management |
| experiments/runner.py | 80 | run_world() + summarize_repeats() — THE core experiment loop |
| experiments/transfer.py | 137 | run_abcdef() A-F state transfer + fidelity scoring |
| experiments/dose.py | ~40 | pathway_dose_response(): depth 0-5 |
| experiments/social.py | ~50 | run_social_round(): peer reveal conditions |
| experiments/persistence.py | ~30 | run_persistence_matrix(): reset/persistent/outcomes |
| experiments/scoring.py | 20 | score_decision(): log_score, brier, direction_correct, paper_utility |
| experiments/composition.py | ~30 | compose(): pack collision and interleaving |
| experiments/team.py | ~30 | run_team(): multi-agent topologies |
| experiments/contagion.py | ~30 | contagion experiments |
| experiments/convergence.py | ~40 | teacher_reference_revision_loop() |
| experiments/treatments.py | ~30 | Treatment class + matrix runner |
| state/signature.py | 85 | BehaviorSignature: 11-field fingerprint + distance metric |
| state/pathway.py | 61 | ContextPathway + PathwayStep + run_live_pathway() |
| state/pack.py | 57 | PackManifest: immutable cognitive pack |
| state/transmission.py | 57 | Transmission + parse_master_transmission() |
| state/compiler.py | ~20 | ablation_candidates() |
| dojo/master.py | 115 | PersistentMaster + StudentEvaluation |
| dojo/chain.py | ~40 | transmission_chain(): A→B→C→D multi-hop |
| dojo/population.py | ~30 | MasterScore + faculty_roundtable() |
| culture/hydra.py | ~30 | HydraProjectionRecord + write_hydra_projection() |
| culture/store.py | ~40 | EvidenceGraph: local SQLite evidence store |
| proofs/receipt.py | ~30 | ExperimentReceipt + ModelExecutionClaim |
| canonical.py | 55 | commitment(), canonical_json(), sha256 helpers |

## Key insight
trading_v1 already implements EVERYTHING cogym needs:
- Sequential deterministic worlds with point-in-time safety
- A-F transfer with live pathway generation (not static files)
- Behavior signatures with 11 measurable dimensions
- Social experiments with configurable visibility
- Dose-response testing
- Pack composition and collision
- Dojo master→student training chains
- HydraDB projection boundary (SQLite primary, graph optional)

The current evolution_lab campaign runner adds:
- Layered evaluation (dev/validation/secret)
- Successive halving
- Persistent registry
- Hidden secret seeds from OS entropy
- Paired incumbent acceptance

These should be MERGED INTO trading_v1's experiment system, not kept separate.

## The correct next step is NOT more infrastructure.
## It is: wire muse-spark into trading_v1's existing run_abcdef() and run it.
## That produces the first scientifically valid result because it uses
## the ACTUAL live pathway machinery that was designed for this purpose.
