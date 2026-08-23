# PACK: Telegraph Miner Evaluation Principles

## Rank by intent-normalized performance, never raw accuracy.
Easy-task perfection < hard-task near-success. Weight by difficulty.

## Control four known biases before trusting any ranking:
1. Position bias → randomize order
2. Verbosity bias → judge content only
3. Sycophancy → don't reward agreement
4. Self-preference → ignore style match

## State confidence as probabilities. Calibration target < 0.15 error.

## Sample minimum 3× per provider across difficulty tiers.
Timeouts/refusals are availability data, not quality data — track separately.
