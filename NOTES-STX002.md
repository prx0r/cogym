# STX-002 Test Notes + Next Steps
2026-08-23, running autonomously

## What's being tested
15 hard worlds (3 per family x 5 families) x 7 treatments = 105 runs.
Each world provably has naive != oracle. Grading is string comparison only.

## What we expect to see
Control (G) should score lower than treated subjects on at least some families.
If control scores 100% too, the worlds still are not discriminating enough.

## What to do with results
- If separation exists: compute which families show strongest treatment effect.
  Those become the core of the confirmatory experiment (n=5 per world).
- If NO separation: probe is STILL too easy even with hard worlds.
  Next step would be sequential multi-step environments, not more single-prompt probes.

## Tests written
- test_p0.py: 5 tests (secret seeds differ, ledger chain, hardworld invariant,
  hermes prompt interpolation, STF v2 missingness)
- Original 6 tests still green
- Total: 11 green

## Known issues (not blocking)
1. Docker daemon failed on this box - HydraDB can't run
2. lablab.ai CF-walled for curl - manual entries only
3. Some Brabble/Unstop pages lack structured rules - validator correctly rejects
4. STF v2 bootstrap resamples signatures not sessions - needs session-level bootstrapping

## After STX-002 completes
1. Analyze per-family accuracy
2. If any treatment beats control by >10% on any family -> confirmatory run n=5
3. If no separation -> pivot to interactive regime_shift environment
4. Import hackathonhelp contracts when batch finishes
5. llmdeals research loop should run weekly (prompt ready in data/RESEARCHER-PROMPT.md)
