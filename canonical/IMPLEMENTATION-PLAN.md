# Cogym Implementation Plan — Reference Document
Last updated: 2026-08-23. This is the living map of what's built, what's next, what's frozen.

## PHASE 0 — COMPLETE ✅
| Item | Status | Location |
|------|--------|----------|
| Deterministic market worlds | ✅ Working | canonical/cogym/market/ |
| Point-in-time packet filtering | ✅ Working | canonical/cogym/market/ |
| Commit/reveal challenge protocol | ✅ Working | canonical/cogym/market/challenge.py |
| Sequential ExperimentRunner (220 steps) | ✅ Working | canonical/cogym/experiments/ |
| AgentGenome + mutation spaces | ✅ Working | evolution_lab reference |
| BehaviorSignature fingerprinting | ✅ Working | canonical/cogym/state/signature.py |
| Cognitive Packs (immutable bundles) | ✅ Working | canonical/cogym/state/pack.py |
| Master→Student Dojo architecture | ✅ Built | canonical/cogym/dojo/ |
| Transmission chains (A→B→C→D) | ✅ Built | canonical/cogym/dojo/chain.py |
| Culture/HydraDB projection layer | ✅ Built | canonical/cogym/culture/hydra.py |
| Social experiments (reveal conditions) | ✅ Built | canonical/cogym/experiments/social.py |
| Dose-response experiments | ✅ Built | canonical/cogym/experiments/dose.py |
| Composition experiments | ✅ Built | canonical/cogym/experiments/composition.py |
| Contagion experiments | ✅ Built | canonical/cogym/experiments/contagion.py |
| CSV ingestion / real data support | ✅ Working | canonical/cogym/market/csvio.py |
| Proofs/receipts boundary | ✅ Working | canonical/cogym/proofs/ |
| 16 tests green | ✅ Verified | canonical/tests/ |

## PHASE 1 — COMPLETE ✅ (from evolution_lab merge)
| Item | Status | Location |
|------|--------|----------|
| HardWorld generator (5 families) | ✅ Working | canonical/cogym/hardworlds.py |
| SkillRegistry w/ counterfactual gating | ✅ Working | canonical/cogym/skill_registry.py |
| SealedEvaluator contract + canaries | ✅ Skeleton | canonical/cogym/sealed_eval.py |
| AgentSpec (typed, content-hashed) | ✅ Working | canonical/cogym/core/agent_spec.py |
| EventLedger (append-only, hash-chained) | ✅ Working | canonical/cogym/core/events.py |
| Hermes proposal adapter | ✅ Working | evolution_lab (merge when needed) |
| Campaign runner (dev/val/secret layers) | ✅ Working | evolution_lab (needs LLM wiring) |
| ProcessPool evaluator (2.4x speedup) | ✅ Working | evolution_lab |
| ANTI_THEATRE_V2 constitution | ✅ Committed | evolution_lab/docs |

## PHASE 2 — NEXT (what to build now)
| Priority | Item | Effort | Why |
|----------|------|--------|-----|
| **P0** | Wire real LLM through TransferExperiment | ~2h | First actual result with inference |
| **P0** | Run A-G × hard worlds n=5 pilot | ~4h hermes | Real transfer data |
| **P1** | Reasoning-pattern extraction from RunRecords | ~4h | What strategy did the agent use? |
| **P1** | Evidence-cost mechanics in world snapshots | ~2h | Value-of-information experiments |
| **P2** | Falsification world family | ~2h | Does agent seek disconfirmation? |
| **P2** | HydraDB docker fix + projection schema | ~3h | Reasoning pattern phylogeny |
| P3 | Kanban cogym-lab board | ~1h | Multi-agent orchestration |
| P3 | Master→Student transmission experiment | ~6h | Cultural transmission study |

## PHASE 3+ — QUEUED (do not start until Phase 2 produces results)
Social contagion topology studies · Pack composition chemistry · Reputation/receipt
selection mechanism · Evolution algorithm bake-off · Cross-domain transfer to Telegraph/Ditto ·
Reasoning-pattern ontology in HydraDB · World bank at scale (15K+ worlds)

## Key files to understand first
1. `canonical/cogym/market/world.py` — SyntheticMarketWorld (sequential, 220 steps)
2. `canonical/cogym/experiment.py` — ExperimentRunner (runs agents over time)
3. `canonical/cogym/experiments/transfer.py` — TransferExperiment (the main experiment)
4. `canonical/cogym/state/signature.py` — BehaviorSignature (how we measure cognition)
5. `canonical/cogym/hardworlds.py` — reasoning trap generator
6. `canonical/AGENTS.md` — conventions and rules

## Model configuration
ox-alpha-free via OpenCode Go endpoint. LOCKED by daemon at /root/.hermes/lock-ox-alpha.sh
API key in .bashrc as OPENCODE_GO_API_KEY. Free unlimited tier.
