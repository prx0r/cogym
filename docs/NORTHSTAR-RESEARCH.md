# Cogym Northstar Research — LLM Trading Landscape
2026-08-23 · Full frontier review of 37 repos/papers

## Central finding
LLMs are unstable direct execution policies. Use them as hypothesis generators,
strategy designers, planners and adaptive reasoning components. Keep execution,
accounting, risk, evaluation and statistics deterministic.

## Tier S Repos (clone first)
1. AlphaForgeBench - LLM generates executable alpha-factor code, not BUY/SELL
2. FINSABER - 100+ symbols, 20 years, shows LLM advantages disappear at scale
3. Agent Market Arena (WWW 2026) - agent architecture matters more than model backbone
4. Agent-Trading-Arena / DecoupledMarket (EMNLP 2025 / ICML 2026) - interactive market
5. StockBench - 82 trading days, most LLMs don't beat passive baselines
6. DeepFund (NeurIPS 2025) - configurable analysts, planner on/off ablation
7. FinMem - layered memory architecture for trading
8. TradingAgents - multi-agent debate architecture
9. QuantCode-Bench - 400 NL strategy problems, compile+backtest evaluation

## Quant Infrastructure
- Qlib (microsoft) - best general substrate
- FinRL - PPO/SAC/TD3/DDPG/A2C implementations
- FinRL-Meta - reusable market environments
- TradeMaster - RL research environment

## Scientific Validation (mandatory)
- Deflated Sharpe Ratio (Bailey & Lopez de Prado 2014)
- Probability of Backtest Overfitting (PBO)
- CPCV: Combinatorial Purged Cross Validation with embargo
- Barra-style attribution: separate beta from alpha

## Key Research Findings
1. AlphaForgeBench: direct LLM trading actions have severe run-to-run instability.
   Ask for executable strategy code instead of BUY/SELL/HOLD.
2. FINSABER: LLM advantages disappear over 20 years and 100+ assets.
   Too conservative in bull, too aggressive in bear.
3. Agent Market Arena: agent architecture matters more than model backbone.
4. KTD-Fin: apparent returns reduce to market/style exposure after attribution.
5. ContinualSkillBench: explicit skill maintenance ~= ordinary adaptation on average.
6. EvoMemBench: strong long-context baselines competitive; retrieval helps knowledge-heavy tasks.
7. SkillsBench: curated skills +16.2pp but self-generated skills ~0 gain.
8. PACE-Bench: memory anchors agents to obsolete designs under env mutation.

## Evaluation Layers (E0-E6)
E0 Validity: legal decision?
E1 Forecast: direction/ranking/calibration
E2 Decision: optimal given available info?
E3 Portfolio: net return/drawdown/turnover/risk
E4 Attribution: beta/factor exposure/genuine alpha
E5 Robustness: regimes/assets/CPCV/seeds
E6 Significance: DSR/PBO/bootstrap confidence

## The Real Research Target
NOT: which LLM makes the most money?
INSTEAD: which reasoning architecture x information representation x memory x
communication topology x learning method produces statistically defensible,
out-of-distribution decision improvement after transaction costs, factor
exposure, leakage and multiple-testing effects are removed?

## Clone Order
Core: AlphaForgeBench, FINSABER, Agent Market Arena, Agent-Trading-Arena, StockBench, DeepFund, FinMem, TradingAgents, QuantCode-Bench
Quant: Qlib, FinRL, FinRL-Meta, TradeMaster
Validation: purgedcv, deflated-sharpe, pbo
Reference: Open Alpha Arena, AmadeusGB/alpha-arena, LLM Trading Arena, Nof1 Tracker
