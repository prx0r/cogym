# AGENTS.md — Cogym Trading Lab

## What this is
A deterministic reasoning laboratory using simulated trading as the experimental organism.
Measures WHICH REASONING PATTERNS causally improve decisions and survive transfer.
Trading is not the product. It is the first lab organism because it gives objective
numerical outcomes, sequential decisions, regime changes, noisy evidence, calibration
pressure, delayed feedback and deterministic replay.

## The ONE rule
Hermes proposes. Cogym disposes. No LLM grades itself.

## Repo layout (canonical/ is the ONLY active code)

```
canonical/
├── cogym/
│   ├── market/           # deterministic worlds, synthetic generator, CSV ingest
│   │   ├── world.py      #   TradingWorld + WorldManifest + MarketPacket
│   │   ├── synthetic.py  #   WorldSpec generator (levels 0-6 = increasing difficulty)
│   │   ├── challenge.py  #   commit/reveal anti-theatre protocol
│   │   └── features.py   #   EvoLabz-style state geometry + momentum
│   ├── agents/           # model adapters + trader agent + decision artifacts
│   │   ├── model.py      #   ChatModel protocol + OpenAICompatible + HarnessTraderModel
│   │   ├── decision.py   #   structured Decision dataclass (stance/confidence/claims/falsifiers)
│   │   ├── trader.py     #   CognitiveAgent that uses memory + model to decide
│   │   └── session.py    #   agent session management
│   ├── experiments/      # pre-built experiment modules
│   │   ├── transfer.py   #   run_abcdef: A-F transfer conditions
│   │   ├── dose.py       #   dose-response (pathway depth 0-5)
│   │   ├── social.py     #   social reveal conditions
│   │   ├── persistence.py#   persistent vs reset context
│   │   ├── contagion.py  #   belief spread through teams
│   │   ├── composition.py#   pack collision / interleaving / debate
│   │   ├── team.py       #   team formation experiments
│   │   ├── factory.py    #   synthetic_trading_world() helper
│   │   └── runner.py     #   shared experiment infrastructure
│   ├── state/            # pathways, checkpoints, packs, transmissions, signatures
│   │   ├── pathway.py    #   ContextPathway + PathwayStep + run_live_pathway()
│   │   ├── signature.py  #   BehaviorSignature fingerprinting
│   │   ├── pack.py       #   immutable cognitive pack
│   │   ├── transmission.py # master→student state transfer
│   │   └── compiler.py   #   experience → pack compilation
│   ├── dojo/             # master→student training architecture
│   │   ├── master.py     #   persistent Master agent
│   │   ├── chain.py      #   multi-generation transmission chains
│   │   └── curriculum.py #   curriculum design
│   ├── culture/          # HydraDB projection layer
│   │   ├── hydra.py      #   provider-neutral graph projection
│   │   ├── lore.py       #   accumulated cultural knowledge
│   │   └── store.py      #   evidence graph store
│   ├── proofs/           # experiment receipts + verification boundary
│   ├── core/             # AgentSpec, Episode, EventLedger (hash-chained)
│   ├── hardworlds.py     # 5 world families where naive ≠ oracle
│   ├── skill_registry.py # counterfactual skill gating + lineage
│   ├── sealed_eval.py    # sandbox contract + integrity canaries
│   └── cli.py            # cogym smoke / cogym dojo-demo / cogym evolve
├── tests/                # 16 tests green
├── examples/             # runnable demos  
├── specs/                # protocol contracts
└── packs/                # candidate intervention packs

evolution_lab/            # REFERENCE — sealed evaluator, campaign runner, hardworlds
docs/                     # design docs, northstar, build plans
data/                     # hackathonhelp discovery data (separate project)
logs/                     # hermes/experiment run logs
```

## Conventions
1. Frozen dataclasses for all spec objects
2. Content-hash IDs everywhere
3. Append-only ledgers, never rewrite history  
4. Unknown = null, never inferred
5. Hermes proposes; benchmark disposes
6. ox-alpha-free via OpenCode Go (LOCKED by daemon)
7. Whole tiles clickable; official source always linked
8. set:html for HTML strings in Astro; never template literals inside JSX expressions

## Running experiments
```bash
cd canonical
source .venv/bin/activate
python -m pytest tests/ -q                    # 16 tests
cogym smoke                                    # quick demo
cogym dojo-demo                               # master→student demo
python /tmp/opencode/run-stx.py              # real LLM transfer experiment
```

## Model config
ox-alpha-free via https://opencode.ai/zen/go/v1
Key: OPENCODE_GO_API_KEY in ~/.bashrc
LOCKED by /root/.hermes/lock-ox-alpha.sh daemon (checks every 30s)

## User-Agent requirement
OpenCode Go endpoint blocks requests without a User-Agent header.
OpenAICompatible class in model.py includes "User-Agent": "CogymLab/1.0".
If you get HTTP 403 error code 1010, check this header exists.

## Key files to understand (read in this order)
1. `cogym/market/world.py` — TradingWorld: deterministic price series
2. `cogym/agents/model.py` — OpenAICompatible: how LLM inference works
3. `cogym/agents/decision.py` — Decision: structured output from each step
4. `cogym/state/pathway.py` — ContextPathway: the treatment being tested
5. `cogym/experiments/transfer.py` — run_abcdef: THE main experiment
6. `cogym/state/signature.py` — BehaviorSignature: how we measure cognition
7. `cogym/hardworlds.py` — worlds designed to expose reasoning failures
8. `AGENTS.md` — this file
