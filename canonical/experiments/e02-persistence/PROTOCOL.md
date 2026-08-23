# E02 Protocol — Context Persistence
Frozen: 2026-08-23.

## Question
Does persistent context (agent remembers previous decisions and outcomes)
improve or hurt decision quality compared to fresh context each time?

## Hypothesis
Persistent context improves calibration (agent learns from mistakes) but
may introduce anchoring (overweights its own previous position).

## Independent Variable
history_mode: "reset" vs "persistent"

## Dependent Variables
1. mean_log_score
2. mean_paper_utility  
3. direction_correct %
4. revision behavior

## Control Variables
Same model, same worlds, same temperature, same samples.
Only history_mode differs.

## Sample Size
3 worlds × 5 samples × 2 conditions = 30 runs

## Frontier Papers
- EvoMemBench (2605.18421): memory helps knowledge-heavy tasks, can hurt execution
- PACE-Bench (2608.14441): memory anchors agents to obsolete designs under mutation
