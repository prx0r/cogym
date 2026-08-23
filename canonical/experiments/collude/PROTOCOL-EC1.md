# PROTOCOL E-C1 — Team production function at fixed budget (FROZEN before run)
2026-08-23 · COLLUDE L1 · model: ox-alpha-free (OpenCode Go)

## Hypothesis
H1 (diversity): role-diverse teams (bull/bear/quant) beat a same-prompt ensemble at equal
call count, because homogeneous members' errors correlate (2602.03794).
H2 (supervision): confidence-exposing aggregation beats plain majority vote.
H3 (exploratory): an LLM supervisor adds value above the best deterministic aggregator
(conf-weighted). Reported but NOT expected to clear the bar at this n.

## Design
Episode bank: 8 frozen decisions = SPY, QQQ, TLT, GLD × bar indices {300, 430}
(2y daily Alpaca IEX bars, 2024-08-01→2026-08-22). Point-in-time window = 60 bars ending
at t-1. Realized outcome = forward 5-day return. Bank hash recorded in outputs.

Conditions (subjects temp=0.7, seeds logged; god temp=0.0):
| condition | calls/decision | what happens |
|-----------|----------------|--------------|
| solo          | 1 | one homogeneous agent decides |
| ensemble3     | 3 | same prompt ×3 seeds → majority vote |
| roles3        | 3 | bull/bear/quant independent → majority vote |
| roles3_conf   | 3 | bull/bear/quant independent → confidence-weighted vote |
| god_g2        | 4 | 3 roles + 1 supervisor call seeing answers+confidence |

Budget honesty: god_g2 spends +1 call; raw J and cost-adjusted J_c = J/calls both reported.

## Endpoints
Primary: mean signed utility per decision (correct=+|r|, wrong=-|r|, abstain=0), Wilson CI
on direction-decision accuracy vs 0.5 for conditions with n_decided ≥ 30 (pilot will not
reach this — pilot classifies as PROVISIONAL at best).
Secondary: up-share (bias check), Brier on confidence, UNPARSEABLE rate, latency.

## Anti-theatre commitments
- Episode bank frozen + hashed BEFORE first inference.
- Fresh session per call; no cross-condition memory.
- Aggregation/scoring deterministic Python; no self-grading.
- UNPARSEABLE kept as data. Errors ≠ selections.
- No claim of significance from this pilot; it gates whether E-C1b (n≥30 decisions) runs.

## Kill criteria
- If UNPARSEABLE+error rate > 20% → fix adapter before interpreting anything.
- If all conditions within ±1bp utility → worlds too easy → move to hardworlds families.
