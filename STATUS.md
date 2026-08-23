# Cogym Status — Honest Assessment
2026-08-23, 03:00 UTC

## What is scientifically valid RIGHT NOW
Nothing confirmatory. One directional pilot finding (n=1).

### Valid finding (n=1, directional only)
Live-pathway subject produced underconfident ranking (0.55 conf vs control's 0.95)
while still getting the correct order. Static treatments did not inherit this humility.
This is consistent with the hypothesis that experienced agents know what they don't know.
n=1. Not significant. Needs harder probe + n=5 minimum.

### Infrastructure that works (verified by tests)
- Deterministic market worlds (6 families, seeded, forkable)
- ExperimentRunner (sequential multi-step episodes)
- Campaign runner with dev/validation/secret layers + successive halving
- Process pool evaluator (2.4x speedup, disk cache)
- EventLedger (hash-chained, append-only)
- Hermes proposal adapter + deterministic validation
- SkillRegistry with lifecycle gating
- HardWorld generator (5 families where naive != oracle)

## What is NOT valid yet
- STX-001 probe too easy (all tau=1.0). Only calibration varied. n=1.
- STF=0.93 for teaching is an artifact of scale mismatch in the distance metric.
- HardWorlds generated but never used in a real evaluation.
- No LLM inference tested through campaign runner.
- HydraDB not running (docker daemon failed).
- SkillRegistry never evaluated real skills.

## The one thing to do next
Run ONE experiment with an actual LLM model on hard worlds where naive != oracle.
If that produces different accuracy across treatments, we have something.
If it doesn't, cogym needs a different probe design, not more infrastructure.

## Repo structure after cleanup
```
evolution_lab/
  cogym/           # engine (worlds, agents, campaign, contracts, skills)
  core/            # AgentSpec, Episode, EventLedger  
  tests/           # 11 tests green
  examples/        # campaign yamls
experiments/
  stx-001/         # pilot data (materials, outputs, grades, signatures)
  stx-002/         # empty - waiting for hard worlds integration
logs/              # hermes run logs
docs/              # NORTHSTAR, BUILD-PLAN, TRADING-COGYM, REVIEW docs
data/
  seed.json        # hackathonhelp discovery data (separate project)
  manual-events.json
  builder-profile.json
  history/          # snapshots
  candidates/       # researcher output queue
```
