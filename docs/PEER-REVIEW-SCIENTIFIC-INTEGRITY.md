# Peer Review: Scientific Integrity Audit (2026-08-23)

## Status: Infrastructure ahead of experiments. Fix evaluator before running more.

## P0 Bugs Found
1. STX-002 live condition is NOT live - reads static file, does not generate pathway
2. delta_rec UnboundLocalError when champion is None (first generation)
3. PatternStore evaluates dev suite twice and writes same aggregate against every world
4. PatternStore "improved" = mean_reward > 0 instead of improvement vs matched control
5. ExperimentLog in evolution_lab instead of canonical (split-brain)
6. ExperimentLog: missing confidence averaged as 0; None correctness counted as wrong
7. API key exposed in source files

## Statistical Issues
- 100% vs 86.7% at n=15 paired is McNemar p ~ 0.5. NOT significant.
- Treatment materials differ 15x in token count (confound)
- Format matching confound: checkpoint/pack output JSON matches probe format

## Required Tests (Metascience)
Tests that verify the machinery MEASURES what it claims to measure:
- Deliberately-bad agent should FAIL
- Right tool with wrong parameters should FAIL
- Errored tool invocation should FAIL
- Equivalent seeds should replay identically
- Changing one treatment dimension leaves other manifest fields byte-identical

## Build Order
P0 fixes above -> sealed enforcement -> interactive regime shift world -> STX-002A
