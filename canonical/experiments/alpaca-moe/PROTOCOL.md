# PROTOCOL — ALPACA-MOE-001/002 (frozen before scoring)
2026-08-23 · Real Alpaca IEX daily bars · deterministic, no LLM inference

## Hypothesis
H1: Cogym's state geometry (direction/strength/volatility) segments real equity,
bond and gold daily bars into distinct regimes (world states) without lookahead.
H2: Each regime favors a different trading policy (specialization exists).
H3 (002): A regime-routed team of specialists beats every individual fixed policy.

## Data
SPY, QQQ, TLT, GLD · 2024-08-01 → 2026-08-22 · 1Day bars · feed=iex · ~516 bars/symbol.
World built via cogym.trading.alpaca.world.create_alpaca_world (content-hashed manifest;
refetch determinism verified: identical sha256 bars_digest).

## Variables
Independent: regime classification thresholds (calibrated to empirical p25-p75 of
features BEFORE scoring, frozen in moe001_regimes.py).
Dependent: forward 5-day returns per (regime × policy); equity curves.
Controls: point-in-time features only (window ends at t-1); non-overlapping steps;
no parameter search inside loop; single frozen pass.

## Policies (experts)
momentum | always_long | defensive | dip_buyer | (002v2) short-capable bear via -1 position.

## Known limitations (declared upfront)
- Bull-dominated sample: long-bias rewarded; results are regime-sample-dependent.
- n=364 non-overlapping steps pooled across symbols; symbols correlated (SPY/QQQ).
- No transaction costs/slippage.
