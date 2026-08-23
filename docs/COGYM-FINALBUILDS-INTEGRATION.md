# Cogym × FinalBuilds Integration + Multi-World Architecture
2026-08-23 · Operator review of cogym direction

## Core insight
Cogym is NOT a trading product. Trading is the first lab organism.
The real product is the **reasoning-policy evaluation engine** that works across domains.

## The meta-science layer
Cogym should discover which cognitive/research protocols make the FinalBuilds scientist better.

Example treatments to A/B test:
CONTROL (normal) | T1 contradiction search | T2 evidence clustering |
T3 causal mechanism first | T4 KG-neighbourhood search | T5 independent agents → synthesis |
T6 persistent research memory | T7 compressed checkpoint | T8 forced alternative hypotheses |
T9 Bayesian forecast before explanation

Cogym disposes. Hermes proposes.

## New organism: ResearchWorld
Historical scientific decision frozen at time t.

VISIBLE: tool adoption reports, MCP activity, model pricing, existing APIs, prior outcomes, papers before Aug 1.
HIDDEN: Aug 1 → Oct 1 outcomes.

TASK: generate hypotheses → assign probabilities → choose research → choose experiment → choose product.
REVEAL future. Score: forecast log score, Brier, calibration, hypothesis predictive skill,
product outcome, information gain, research cost, tokens, experiment regret.

## Generalized Decision object
TradingDecision → ScientificDecision:
{
  hypothesis_candidates: [],
  probabilities: {},
  supporting_claim_ids: [],
  contradicting_claim_ids: [],
  mechanism: "...",
  missing_information: [],
  proposed_experiment: "...",
  expected_information_gain: 0.31,
  falsifiers: [],
  forecast_distribution: {}
}

## ScientistPolicy evolution
ScientistPolicy v17 vs v18 across hidden ResearchWorlds.
Only policies improving held-out forecasting survive.
= empirically evolved scientific method.

## SkillRegistry warning
Steal the principle (counterfactual gating), not the code.
Current implementation needs hardening before shared infrastructure.

## Multi-world architecture
Different worlds = different products from same engine:
- TradingWorld → Cogym Trading Lab
- ResearchWorld → FinalBuilds Scientist
- HackathonWorld → HackathonHelp matcher
- ProductDecisionWorld → product strategy engine

Codebase must be organized so these variations are CLEAR and separate.
