# E03 Protocol — Reasoning Route
Frozen: 2026-08-23.

## Question
Does the ROUTE to a conclusion matter, or only the information content?
Same world data presented via different reasoning pathways.

## Independent Variable  
Reasoning route (from original experiment backlog #3):
- R0 direct: "Here's market data. What do you think?"
- R1 told principle: "The key principle is X. Here's data."
- R2 derive principle: "Here's data. What principle applies?"
- R3 predict-before-seeing: "Predict what you'll see before looking."
- R4 falsify-first: "What would disprove your initial guess?"

## Dependent Variables
1. mean_log_score
2. direction_correct %
3. confidence calibration

## Control Variables
Same model, same worlds, same total token budget per decision.

## Why this matters
If R3 (predict-first) consistently outperforms R0 (direct), that validates
the "generate hypothesis first" pedagogy from cognitive science literature.
If all routes perform identically, the model ignores prompt structure.

## Frontier Papers
- GEPA (ICLR 2026): reflective evolution of prompts outperforms RL with 35x fewer rollouts
- Original cogym backlog item #3: "tell vs derive vs predict-before-seeing vs peer-derived"
