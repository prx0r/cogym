# Implementation Plan — Reference Document
Updated: 2026-08-23

## Phase 0 COMPLETE ✅ — trading_v1 core works
16 tests green. All modules importable. Deterministic worlds + experiments + dojo.

## Phase 1 COMPLETE ✅ — evolution_lab improvements merged
HardWorlds (5 families), SkillRegistry, SealedEval contract, AgentSpec/Episode/EventLedger,
Hermes proposal adapter, ANTI_THEATRE_V2 constitution.

## Phase 1.5 COMPLETE ✅ — Real LLM wired through TransferExperiment
OpenAICompatible → ox-alpha-free → zen/go/v1. UA header added for CF bypass.
First real transfer experiment executed with actual inference.

## Phase 2 — CURRENT (what needs doing now)
| Priority | Item | Status |
|----------|------|--------|
| **P0** | Run full A-F with ox-alpha-free on regime_flip world | 🔄 Script ready at /tmp/opencode/run-stx.py |
| **P0** | Collect results: which treatments produce different decisions? | pending |
| P1 | Run on 3+ world families × n=5 samples | ready after P0 |
| P1 | Extract reasoning patterns from Decision artifacts | not started |
| P2 | Falsification world family in market/synthetic.py | not started |
| P2 | Evidence-cost mechanics in ExperimentRunner | not started |
| P3 | HydraDB docker fix + projection | blocked (docker daemon) |

## STX-002A spec (next major experiment)
Interactive REGIME_SHIFT environment:
- 30 sequential trials, change point hidden at trial 16
- Actions: CHOOSE_A / CHOOSE_B / REQUEST_EVIDENCE / TEST_HYPOTHESIS (costed)
- Treatments: live, checkpoint, pack, teaching, skill, summary, control, sham-context, sham-teaching
- Primary endpoint: post_shift_cumulative_regret
- Secondary: detection_latency, adaptation_latency, evidence_cost, tokens
- Pilot gates: control not ceiling, not floor, variance nonzero, oracle deterministic

## After STX-002A
1. Representation-efficiency study (same info, different encodings)
2. Verified-self-generated-skills study (SkillsBench challenge)
3. Memory-poisoning/regime-change study (PACE-Bench)
4. Evolution-algorithm bake-off under identical budget
5. Social/cultural transmission (only after 1-4 produce results)

## What NOT to build yet
Social contagion topologies · Pack composition chemistry · Reputation/receipt selection ·
Evolution bake-off · Cross-domain transfer · Kanban orchestration · MCP server ·
HydraDB projection · Weight training · Agent economies · Dashboards
