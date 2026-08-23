# Trading World

Trading is the first Cogym domain, not because simulated PnL is the only useful objective, but because markets combine delayed scoring with non-stationarity.

## State packet

Every snapshot contains:

- instrument and as-of time;
- current price;
- direction;
- strength;
- volatility;
- changes in direction/strength/volatility;
- drawdown;
- volume surprise;
- recent returns;
- point-in-time external context.

The initial feature family is intentionally compact and descended from the useful state-vector ideas in the earlier EvoLabz work. Add new features only when a documented experiment needs them.

## Synthetic levels

0. clean trend;
1. trend -> reversal;
2. calm -> shock -> recovery;
3. fake breakout -> reversal;
4. chop -> crisis -> repair;
5. repeating edge -> edge stops working;
6. multi-shock adversarial non-stationarity.

A future adversarial generator may search for worlds that maximize regret/adaptation latency for a target population, but static deterministic constructors remain necessary for comparable benchmarks.

## Real data

Store the highest reliable raw resolution available plus provenance. Do not require 1-minute bars for every small token if only trades/swaps or coarser bars are trustworthy. Deterministically derive higher-level bars from the rawest reliable source.
