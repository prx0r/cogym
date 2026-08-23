# Cogym Alpaca Variant — Trading Thesis & Hackathon Entry
2026-08-23 · This becomes the first real-world application of Cogym's reasoning evaluation engine.

## Goal
Build an autonomous AI trading agent on Alpaca's paper trading platform that generates P&L.
Use Cogym's deterministic evaluation framework to test and refine the agent's strategy
BEFORE deploying it. The agent that competes is the one that scored best in our lab.

## Judging Criteria (from hackathon)
1. **P&L Performance** — trading performance in Alpaca paper environment
2. **Technology Implementation** — effective use of Alpaca Trading API, MCP server, CLI
3. **Creativity & Originality** — novel approach, thoughtful use of technology
4. **Presentation & Execution** — clear communication of strategy, reasoning, results

## Our edge: Cogym's reasoning evaluation engine
Most entrants will build a simple bot and hope for the best.
We will use cogym to:
- Test multiple reasoning strategies against historical data
- Measure calibration, drawdown, adaptation latency per strategy
- Select the BEST strategy using deterministic scoring, not gut feeling
- Show judges the full experimental methodology

This IS cogym. Same engine, different world.

## What we need
- Alpaca paper trading API keys (free signup)
- Historical bars from Alpaca data API (free tier: 200 req/min, since 2016)
- Options trading component (required by hackathon)
- MCP server or CLI integration (required by hackathon)

## Architecture
```
cogym/canonical/cogym/trading/alpaca/
├── source.py         # fetch bars from Alpaca data API → Bar objects
├── world.py          # AlpacaTradingWorld (real data, deterministic replay)
├── agent.py          # LLM trading agent w/ Alpaca execution
├── options.py        # options strategy logic
├── evaluator.py      # cogym scoring engine applied to alpaca trades
└── config.py         # API keys, endpoints, parameters
```

## Timeline
Aug 23-25: Build core agent + alpaca integration
Aug 25-27: Test strategies in cogym lab, select winner
Aug 28-Sep 4: Deploy on Alpaca paper trading during hackathon window
Sep 4: Submit with full methodology documentation
