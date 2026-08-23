# Cogym Protocol v1

## Experimental unit

A Cogym trial commits to:

- world ID and snapshot indices;
- model ID/provider metadata;
- condition/pathway/Pack ID;
- temperature and requested sample seed;
- transcript/input commitment;
- observable structured outputs;
- delayed outcome;
- evaluator version.

The exact world is replayable. The model may remain stochastic.

## Frozen world rule

All compared conditions receive the same point-in-time information. Any external datum must carry `available_at`; data unavailable at the snapshot time is excluded before prompt construction.

## Repeated samples

A trial condition is normally repeated. Three repetitions are a smoke test, not a strong scientific default. Increase repeats until uncertainty is narrow enough for the effect under study.

## Observable reasoning artifacts

Cogym stores concise structured artifacts (`crux`, `claims`, `evidence`, `uncertainties`, `falsifiers`, `reasoning_summary`) rather than requiring private hidden chain-of-thought. The benchmark should remain usable with black-box APIs.

## History modes

- `reset`: pathway context may be present, but each market decision starts from the same initial history.
- `persistent`: previous decisions remain in context.
- optional outcome reveal: realized paper outcome is appended after a decision.

This separates immediate induction from path-dependent learning/habit effects.
