# PnL Optimization Experiments — arxiv-backed (2026-08-23)
Goal: maximize risk-adjusted P&L of the COLLUDE team on Alpaca paper. 10 experiments,
each grounded in a frontier paper, each one-variable, all on frozen banks where possible.

| ID | Source paper | Idea | Metric |
|----|--------------|------|--------|
| E-P1 | FinPos 2510.27251 / FinRS 2511.12599 | separate Sizing agent using Kelly×CVaR cap from direction agent | net PnL, MDD |
| E-P2 | FinPos | dual-agent: direction then quantity/risk review | PnL vs single-agent |
| E-P3 | FinRS | multi-timescale reward (1d/7d/30d momentum) in reflection prompt | stability, Calmar |
| E-P4 | MadEvolve 2605.23007 | fitness = impact-adjusted PnL not Sharpe (avoid trading-too-little bias) | impact-adj PnL |
| E-P5 | MadEvolve §5.1 | sizing-only counterfactual: is gain real or just scaled-up? ratio>1 test | PnL_evol/PnL_sized |
| E-P6 | 2604.10996 | treat system prompt as hyperparameter; select on IC not vibes | Spearman IC |
| E-P7 | ATLAS 2510.15949 | regime-gated modality: news only in calm regime, drop in macro shock | OOS Sharpe by regime |
| E-P8 | 2605.16895 P4 | calibration gate: ECE/reliability of LLM confidence BEFORE sizing uses it | ECE, Brier |
| E-P9 | 2605.16895 P5 | gross→net: subtract spread+slippage+commission+token cost from every backtest | net PnL |
| E-P10 | 2605.16895 P6 | LLM as upstream signal ONLY; deterministic calibration/sizing/execution modules own stages 4-6 | full-pipeline PnL |

## Anti-theatre rules (binding)
- All banks point-in-time; frictions ALWAYS applied (P5) — no gross-alpha illusions.
- LLM confidence never controls size until it passes ECE gate (P8/P4).
- Sizing gains must beat scale-counterfactual (P5/E-P5) to count as algorithmic.
- Every experiment reports BOTH raw and friction-adjusted numbers.

## Queue order (after E-C3/C4 finish)
E-P8 → E-P1+E-P2 (sizing harness) → E-P9 audit of ALL prior results →
E-P4/E-P5 tournament → E-P6 prompt evolution → E-P7 regime gating → E-P10 assembly.
