# COLLUDE — multi-agent market laboratory (inside cogym)

Thesis: `docs/collusionthesis.md`. Rule of the house still applies:
**hermes proposes, cogym disposes** — aggregation/scoring is deterministic Python,
never the LLM.

## Ladder (one rung at a time, one variable per experiment)

| Rung | Experiment | Variable | Status |
|------|-----------|----------|--------|
| L1 | E-C1 production function | team composition at fixed budget | RUNNING |
| L2 | E-C2 communication value | independent vs chat vs debate | planned |
| L3 | E-C3 god variants G0-G6 | what the supervisor sees | planned |
| L4 | E-C4 wisdom vs herding | reveal granularity, correlation H | planned |
| L5 | E-C5 expert suppression | planted 90% expert | planned |
| L6 | E-C6 faulty teammate | leave-one-out L_i | planned |

Track 2 (private info/Bayes, incentives α-sweep, cheap talk, Shapley) and
Track 3 (minority game, replicator ecology, topology evolution, PSRO) come after
L1-L6 produce at least one CONFIRMED finding under Wilson CI discipline.

## Conventions (from AGENTS.md, binding)
1. Fresh session per subject call; no cross-trial memory unless memory IS the variable.
2. Deterministic aggregation + scoring. Parse failure = UNPARSEABLE, recorded, never dropped silently.
3. Every call logged: model, seed, temperature, timestamps, raw output.
4. Episode bank hash-frozen before first inference.
5. Abstention allowed. Failure ≠ change. n reported honestly; no claim below n_decided ≥ 30.
6. Budget policy declared per experiment; cost-adjusted J_c = J / calls reported alongside raw J.

## Run
```bash
cd canonical
set -a; source .env; set +a   # OPENCODE_GO_API_KEY (+ ALPACA keys for world building)
setsid nohup python3 experiments/collude/run_ec1.py > ../../logs/ec1.log 2>&1 &
tail -5 ../../logs/ec1.log    # watchdog every 30-60s
```
