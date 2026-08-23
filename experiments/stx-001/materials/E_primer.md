=== PRIMER: Ranking AI providers correctly ===
Score = Normalized Performance within Intent (75% of total). This weights correctness by task difficulty: hard tasks count more.
Control these biases: position (order effects), verbosity (length≠quality), sycophancy (agreement≠correct), self-preference (style-similarity).
Output calibrated probability confidences; calibration error target < 0.15.
Probe each provider ≥3 times across difficulty tiers. Log timeouts/refusals separately from quality rankings.
