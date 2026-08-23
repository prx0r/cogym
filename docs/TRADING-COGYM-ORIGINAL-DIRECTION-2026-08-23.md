# Trading Cogym — Original Direction Restored (2026-08-23)
This is the correct scope. The broader "artificial society" framing (NORTHSTAR.md) is
the long-term vision, NOT the current build target. This document supersedes NORTHSTAR
for the next sprint.

## Core identity
Cogym = controlled reasoning laboratory built around deterministic trading worlds.
Object of study: **which reasoning patterns causally improve decisions under different environments, and which survive transfer?**

## Architecture (restored from original design)

DETERMINISTIC MARKET WORLD -> agent observes -> reasoning/evidence gathering ->
structured decision -> deterministic outcome/oracle -> measure reasoning+outcome ->
BehaviorSignature -> Pattern Extraction -> HydraDB

PZL philosophy: commit(world_definition) before agent acts, reveal+verify after.
Anti-theatre by construction, not by policy.

## Four research loops (ALL of cogym v1)
1. Reasoning discovery - hermes proposes strategies; which improve hidden worlds?
2. Reasoning evolution - mutate/recombine; retain only genuinely better descendants
3. Reasoning transfer - checkpoint vs memory vs pack vs teaching vs skill
4. Reasoning transmission - master learns something; can fresh student acquire it?

## World families (already implemented in hardworlds.py)
- base_rate_shift: salient recent evidence vs historical rate
- confounded_choice: correlation vs causation
- regime_flip: optimal rule becomes harmful mid-episode
- costly_evidence: value of information vs cost
- difficulty_weighted_rank: raw success != difficulty-adjusted quality
- falsification: everything supports H except one disconfirming observation

## Killer experiment v1 (narrowed from "BASE vs SOCIETY")
FRESH AGENT vs LIVE-EXPERIENCE AGENT vs FRESH+CHECKPOINT vs FRESH+MEMORY
vs FRESH+PACK vs FRESH+TEACHING vs FRESH+TESTED SKILL
Same model. Same budget. Hundreds of unseen deterministic market worlds.
Measure: reward, decision quality, calibration, evidence efficiency,
falsification rate, adaptation latency, revision behavior, token cost.

## What to KEEP from current repo
AgentSpec + Episode + EventLedger | hermes_adapter | BehaviorSignature/STF |
sealed evaluator concept | HardWorld generator | SkillRegistry w/ counterfactual gating

## What to FREEZE (Phase 5-10, not now)
Social contagion, reputation experiments, economic societies, cultural topology,
meta-evolution of scientist agents, weight training/RL/SFT, agent economies.

## Trading = laboratory organism, not end goal
Once strategy S reliably causes agents to seek disconfirming evidence before committing,
test the SAME strategy on tool selection, coding, research, planning. If it survives,
you found a portable cognitive technique.

## HydraDB role
Not raw data storage. An evolving phylogeny of cognition:
Agent -EXHIBITED-> ReasoningPattern -> IMPROVED_ON -> RegimeShiftWorld
Skill -INDUCED-> ReasoningPattern
Transmission FROM Master TO Student TRANSFERRED ReasoningPattern
Query: which techniques improve regime-change performance without hurting calibration?
