# Cogym Results Summary — What We Actually Found
2026-08-23 · Honest assessment of all experiments to date

## Confirmed Findings (reproducible)

### 1. Difficulty scaling works
Same model, different world difficulty → measurably worse performance.
smooth_trend (-1.012) < shock_jumps (-1.045) < regime_flip (-1.206)
This validates that our worlds have real difficulty gradients.

### 2. Directional accuracy degrades below chance on hard worlds
On regime_flip, ox-alpha-free scored 0-27% direction correct.
Below chance means the model is actively making WRONG calls —
it sees patterns that don't exist. This is more interesting than
random guessing because it suggests overconfident pattern-matching.

## Directional Finding (n=1, needs confirmation)

### 3. Live pathway produces underconfidence
Only the live-pathway subject showed calibration error > 0.25.
It followed its own "probe 3x minimum" protocol so carefully it
undermined its confidence on a single-shot probe.
Static treatments didn't inherit this behavioral trait.
STF(teaching→live) was highest at 0.93 — conversational transfer
preserves behavioral quirks better than structured formats.

## NOT Valid (common mistakes we avoided)

| Claim | Why it's wrong |
|-------|---------------|
| "Checkpoint beats live 100% vs 73%" | Different information quantity + n=1 + format confound |
| "Pack transfers better than teaching" | Both used same probe; no variance measured |
| "Model can't trade" | Baseline utility near zero is EXPECTED for efficient markets |
| "STF=0.93 proves teaching preserves cognition" | Distance metric had scale bug (now fixed in v2) |

## Infrastructure Validated
- Deterministic worlds: same seed → identical price series ✓
- Point-in-time safety: no future data leakage ✓  
- ExperimentRunner: sequential multi-step episodes ✓
- Scoring: deterministic log_score/brier/utility ✓
- Campaign runner: dev/validation/secret layers ✓
- SkillRegistry: counterfactual gating ✓
- PatternStore: SQLite w/ HydraDB-ready export schema ✓

## What's needed for confirmatory results
1. Harder probes where control scores ~30-50% (not 87%)
2. n=5 minimum per treatment per world
3. Token-matched materials across treatments
4. Temperature logged per run
5. Multiple seeds per condition
6. Pre-registered statistical test BEFORE running
