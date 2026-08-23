# STX-002 Protocol — Preregistered
Frozen: 2026-08-23 03:50 UTC. Do not modify after subjects run.

## Hypothesis
Treated subjects (A-F) will outperform naive control (G) on hard reasoning worlds
where the naive answer differs from the oracle answer.

## Worlds
15 worlds across 5 families (3 per family). Generated deterministically from
cogym.hardworlds.generate_batch(15). Stored in worlds.json with oracle answers.

## Treatments
A live | B checkpoint | C pack | D teaching | E primer | F summary | G control
Materials from stx-001 (same pathway, same domain).

## Samples
n=1 per treatment per world = 105 total runs. Pilot only.

## Grading (deterministic, no LLM judge)
- Primary: accuracy = chosen choice matches oracle, averaged across 15 worlds
- Secondary: calibration error = |stated confidence - actual accuracy rate|
- Per-family breakdown to identify which reasoning traps are hardest

## Controls
- Same model (ox-alpha-free) for all treatments
- Same probe order for all treatments
- Materials injected BEFORE probe; probe identical across treatments
- Control receives NO treatment material
- All outputs logged with timestamps and raw text preserved

## Anti-theatre
- Oracle answers stored in worlds.json but NOT included in prompts
- No treatment material contains the word "oracle" or the correct answers
- Grading is string comparison, not LLM judgment
- All raw outputs preserved regardless of quality
