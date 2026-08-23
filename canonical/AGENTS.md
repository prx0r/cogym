# AGENTS.md — Cogym (Trading Cogym Canonical)

## What this project IS
A deterministic experimental laboratory for discovering, testing, transmitting and
evolving reasoning strategies under uncertainty. Trading is the lab organism because
it provides objective numerical outcomes, sequential decisions and adversarial structure.

## What this project is NOT
Not a trading bot. Not a generic agent framework. Not a benchmark.
It measures WHICH REASONING PATTERNS causally improve decisions and survive transfer.

## The one rule
Hermes proposes. Cogym disposes. No LLM grades itself.

## Repo layout (canonical/ = the only active code)

```
canonical/
├── cogym/
│   ├── market/          # deterministic worlds, synthetic generator, point-in-time packets
│   ├── agents/          # model adapters, trader agent, decision artifacts
│   ├── experiments/     # transfer, dose-response, social, contagion, composition, persistence
│   ├── state/           # pathways, checkpoints, packs, transmissions, behavior signatures  
│   ├── dojo/            # master→student training, transmission chains
│   ├── culture/         # hydra projection, lore store
│   ├── proofs/          # experiment receipts, verification boundary
│   ├── core/            # AgentSpec, Episode, EventLedger (hash-chained)
│   ├── hardworlds.py    # 5 world families where naive≠oracle (reasoning traps)
│   ├── skill_registry.py# counterfactual skill gating + lineage
│   ├── sealed_eval.py   # sandbox contract + integrity canaries
│   └── cli.py           # cogym demo / cogym evolve
├── tests/               # 16 tests green
├── examples/            # runnable demos
└── specs/               # protocol contracts

evolution_lab/           # REFERENCE ONLY — sealed evaluator, campaign runner, pool
                         # merge into canonical when wiring LLM campaigns
docs/                    # NORTHSTAR, BUILD-PLAN, TRADING-COGYM direction docs
data/                    # hackathonhelp discovery data (separate project)
logs/                    # hermes run logs
```

## Current status (2026-08-23)
- trading_v1 core: 16/16 tests green, all modules importable
- HardWorlds: 5 families generating valid worlds where naive≠oracle
- SkillRegistry: counterfactual gating working
- STX-001 pilot: completed, found live-pathway underconfidence signal (n=1)
- STX-002: hard probe data collected, no treatment separation yet (probe needs harder worlds)
- HydraDB: NOT RUNNING (docker daemon failed on this box)

## Key conventions
1. Frozen dataclasses for all spec objects (AgentSpec, SubjectSpec, etc.)
2. Content-hash IDs everywhere (sha256 of serialized object)
3. Append-only ledgers — never rewrite history
4. Unknown = null, never inferred
5. Extraction proposes; benchmark disposes
6. ox-alpha-free via OpenCode Go endpoint (LOCKED — see /root/.hermes/lock-ox-alpha.sh)

## Running
```bash
cd canonical
source /tmp/opencode/tv1-venv/bin/activate  # or create fresh venv
pip install -e .
cogym demo --world regime_flip --seed 42
python -m pytest tests/ -q
```

## Contract extraction (hermes)
```bash
HERMES_MODEL=ox-alpha-free scripts/extract-contract.sh <slug> <url>
```

## Batch operations
```bash
scripts/batch-extract.sh [N]  # extracts N contracts from batch.tsv
scripts/watch-and-ship.sh     # waits for batch, rebuilds+deploys
```

## What to build next (in order — DO NOT skip ahead)
1. Wire a real LLM through TransferExperiment (not RuleBasedModel)
2. Run A-G treatments on hard worlds with n=5 samples
3. Extract reasoning patterns from RunRecords → classify strategies
4. Project validated patterns into HydraDB schema
5. Master→Student transmission experiment
6. Only then: social, culture, contagion

## Anti-theatre constitution
See ANTI_THEATRE_V2.md in evolution_lab/docs/. 20 rules. All binding.
Key rules: proposer never sees secret · paired evaluation on identical batch ·
malformed output is behavior · no LLM-as-judge where deterministic verification possible.
