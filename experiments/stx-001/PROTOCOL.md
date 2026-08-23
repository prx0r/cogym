# STX-001 Protocol
Frozen: 2026-08-23 (retrospective — experiment ran before formal preregistration)

## Hypothesis
A live self-generated context pathway produces a reproducibly different decision
regime than static transfer conditions (checkpoint/pack/primer/summary).

## Independent Variable
Treatment type: A live | B checkpoint | C pack | D teaching | E primer | F summary | G control

## Dependent Variables
1. Rank accuracy (Kendall τ vs correct ordering)
2. Calibration error (|stated confidence − actual correctness|)
3. Response duration

## Control Variables
- Same model: ox-alpha-free via OpenCode Go
- Same probe task for all treatments
- Same temperature (0.0)
- Materials differ ONLY in representation format, not information content

## Confounds Identified Post-Hoc
- Probe too easy: all treatments achieved rank_tau = 1.0 (ceiling effect)
- n=1 per treatment (no variance measurement)
- STF metric had scale-mismatch bug (fixed in v2)

## Frontier Papers
- SkillMaster (arXiv:2605.08693): counterfactual evaluation of skill edits
- GEPA (ICLR 2026): reflective prompt evolution outperforms RL with fewer rollouts
