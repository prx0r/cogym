# STX-002 Protocol
Frozen: 2026-08-23 03:50 UTC (before subjects ran)

## Hypothesis
Treated subjects (A-F) will outperform naive control (G) on hard reasoning worlds
where the naive answer differs from the oracle answer.

## Independent Variable
Treatment type: A live | B checkpoint | C pack | D teaching | E primer | F summary | G control

## Dependent Variables
1. Primary: accuracy = chosen choice matches oracle / 15 worlds
2. Secondary: calibration error per treatment
3. Per-family breakdown to identify which reasoning traps discriminate best

## Control Variables
- Same model: ox-alpha-free
- Same probe format across treatments
- Materials injected BEFORE probe; probe identical for all
- Control receives NO treatment material
- Grading is string comparison against stored oracle, not LLM judgment

## World Generation Invariant
Every world satisfies: naive_policy(world) != oracle_policy(world)
This is checked at generation time and enforced.

## Frontier Papers
- PACE (arXiv:2606.08106): anytime-valid acceptance testing for self-evolving agents
- PACE-Bench (arXiv:2608.14441): memory anchors agents to obsolete designs under env mutation
- SkillsBench (arXiv:2602.12670): curated skills improve pass rate; self-generated ≈ no gain

## Results Summary (post-hoc)
Checkpoint/Pack = 100% accuracy. Live pathway = 73.3% (below control 86.7%).
Base-rate shift is the hardest family (only checkpoint/pack pass).
See RESULTS.md for full analysis.
