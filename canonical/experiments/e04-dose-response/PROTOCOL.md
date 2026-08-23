# E04 Protocol — Pathway Depth / Dose Response
Frozen: 2026-08-23.

## Question
How many reasoning steps are optimal? Does more thinking always help?

## Independent Variable
Pathway depth: 0 (immediate) through 5 (full multi-stage analysis)

## Dependent Variables
1. mean_log_score at each depth
2. mean_paper_utility
3. tokens consumed (efficiency)

## Hypothesis from original design
Dose 0 < 1 < 2 < 3 (normal learning curve)
OR possibly 0 < 1 < 2 > 3 > 5 (over-conditioning / analysis paralysis)

## Frontier Papers
- Original trading_v1 dose_response.py already implements this
- ContinualSkillBench (2608.03874): explicit skill maintenance ≈ ordinary adaptation on average
