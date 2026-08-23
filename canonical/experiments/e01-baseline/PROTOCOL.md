# E01 Protocol — Baseline Measurement
Frozen: 2026-08-23. Simplest possible experiment.

## Question
What is the natural decision quality of ox-alpha-free across different market regimes?

## Hypothesis
Decision quality varies significantly across market regimes even with identical model and no treatment.

## Independent Variable
World type (level 0-6): smooth trend, reversal, shock, choppy, pattern break, etc.

## Dependent Variables (all deterministic)
1. mean_log_score — how well-calibrated probability estimates are
2. brier_score — prediction accuracy
3. direction_correct — % of correct LONG/SHORT/FLAT calls
4. paper_utility — directional profit

## Control Variables
- Same model: ox-alpha-free via OpenCode Go
- Same temperature: 0.2
- Same history_mode: reset (no memory between decisions)
- Same horizon_steps: 5
- Same number of decision points per world

## Sample Size
5 worlds × 5 stochastic samples = 25 runs

## Why this first
You can't measure improvement without knowing the baseline.
This also validates that the pipeline produces reproducible results.

## Frontier Papers
- SEA-Eval (2604.08988): equal success rates can differ 31x in token cost. Measure cost.
- SEAGym (2606.17546): needs train/test/replay separation from the start.
