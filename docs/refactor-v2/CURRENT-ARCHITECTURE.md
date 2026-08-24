# Current Architecture — where things actually live (2026-08-24)

## canonical/ (active code, package now named `cogym` v2.0.0)

```
cogym/core/            GENERIC — zero domain concepts
  contracts.py         World/Policy/Executor/ActionSpec/ActionResult/MetricVector/
                       CandidateArtifact/EpisodeRecord/WorldSpec   (PR2)
  evaluation.py        QualityGate + lexicographic comparator +
                       paired non-inferiority bootstrap            (PR3)
  campaign.py          Campaign runner + ReplayTape/TapeExecutor/
                       RecordingExecutor                           (PR4+PR7)
  runtime.py           GenericRunner: world+policy+executor → EpisodeRecord
  toy_executor.py      deterministic executor (simulated cost/latency)
  events.py, episode.py, agent_spec.py   legacy v1 support

cogym/worlds/          WORLDS — the only place domains are named
  registry.py          kind string → factory ("toy.search_game", "trading.synthetic")
  toy/search_game.py   10-box search; proves genericity             (PR5)
  trading/adapter.py   TradingWorldAdapter behind generic contract;
                       MomentumRulePolicy / StaticStancePolicy      (PR6)

cogym/market/          legacy trading internals (world/schema/synthetic/features/challenge)
cogym/trading/         alpaca source, regime worlds, paper engine
cogym/experiments/     v1 transfer/dose/social/persistence experiments (still trading-coupled)
cogym/agents/, state/, dojo/, culture/  v1 agent machinery (untouched)
experiments/collude/   COLLUDE E-C1..E-C4 scripts + frozen outputs

evolution_lab/         REFERENCE ONLY — sealed evaluator, pool evaluator,
                       campaign runner with successive halving (to mine for PR11-era work)
tests/                 38 green:
  test_generic_core.py        PR2/3/5 acceptance
  test_campaign_replay.py     PR4+PR7 acceptance
  test_golden_trading_episode.py  migration parity
  test_trading_adapter.py     PR6 acceptance (parity + cross-world runner/campaign)
```

## Import-direction rule

```
worlds/* → core/*        ALLOWED
core/*   → worlds/*      FORBIDDEN (would reintroduce domain coupling)
market/, trading/        imported only by worlds/trading/ and legacy v1 paths
```

## What is still v1-shaped (deliberately untouched)

- `cogym/experiments/*` A–F transfer machinery (works, trading-coupled)
- `agents/model.py` OpenAICompatible (used by COLLUDE subject plane)
- `culture/hydra.py` projection layer (already provider-neutral)
- `cli.py smoke/dojo-demo` commands
