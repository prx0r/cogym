"""ALPACA-MOE-001: Do market regimes exist in real Alpaca data, and does each
regime favor a different policy?

Foundation test for the mixture-of-specialists trading team. Deterministic,
no LLM inference. Point-in-time safe: regime at step t uses features computed
from bars [.., t-1] only; forward return measured over [t, t+h).

Outputs experiments/alpaca-moe/outputs/moe-001-results.json
"""
from __future__ import annotations
import json
import math
import os
import statistics
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from cogym.trading.alpaca.world import create_alpaca_world
from cogym.market.features import feature_vector

HORIZON = 5          # business days ahead
LOOKBACK = 60        # feature window (matches TradingWorld.snapshot default)
STRIDE = 1

SYMBOLS = ["SPY", "QQQ", "TLT", "GLD"]
START, END = "2024-08-01", "2026-08-22"


def classify(f) -> str:
    """Deterministic regime router over cogym's own state geometry.

    Thresholds calibrated on the empirical distribution of real Alpaca daily
    bars 2024-08..2026-08 (strength p75≈0.08, |direction| median≈0.03,
    volatility p75≈0.55). Frozen before scoring.
    """
    if f.strength >= 0.08 and f.direction >= 0.04:
        return "BULL_TREND"
    if f.strength >= 0.08 and f.direction <= -0.04:
        return "BEAR_TREND"
    if f.volatility >= 0.55:
        return "HIGH_VOL_CHOP"
    return "QUIET_RANGE"


REGIMES = ["BULL_TREND", "BEAR_TREND", "HIGH_VOL_CHOP", "QUIET_RANGE"]


def policies() -> dict[str, callable]:
    """Each specialist is one expert. Position in [-1 (short via inverse), 0, +1]."""
    def momentum(win):
        return 1.0 if win[-1].close > win[-7].close else 0.0

    def always_long(win):
        return 1.0

    def defensive(win):
        return 0.5 if win[-1].close >= min(b.close for b in win[-21:]) * 1.02 else 0.0

    def dip_buyer(win):
        d = win[-1].close / max(b.close for b in win[-21:]) - 1.0
        return 1.0 if d <= -0.03 else 0.25

    def cash(win):
        return 0.0

    return {
        "momentum": momentum,
        "always_long": always_long,
        "defensive": defensive,
        "dip_buyer": dip_buyer,
        "cash": cash,
    }


def main():
    key_id = os.environ["ALPACA_KEY_ID"]
    secret = os.environ["ALPACA_SECRET_KEY"]

    results = {"spec": "alpaca-moe-001", "horizon": HORIZON, "lookback": LOOKBACK,
               "symbols": {}, "router_prior": {}, "transition_counts": {}}

    trans = {r: {r2: 0 for r2 in REGIMES} for r in REGIMES}
    # forward returns keyed by [regime][policy]
    fwd = {r: {p: [] for p in policies()} for r in REGIMES}

    for sym in SYMBOLS:
        w = create_alpaca_world(sym, START, END, key_id=key_id, secret_key=secret)
        bars = w.bars
        n = len(bars)
        obs = []
        prev_reg = None
        for i in range(LOOKBACK, n - HORIZON, STRIDE):
            feat = feature_vector(bars[max(0, i - LOOKBACK):i])   # PIT-safe: excludes bar i onward
            reg = classify(feat)
            if prev_reg is not None:
                trans[prev_reg][reg] += 1
            prev_reg = reg
            entry = bars[i].close
            exit_ = bars[min(i + HORIZON, n - 1)].close
            r_fwd = exit_ / entry - 1.0
            window = bars[:i]
            for pname, p in policies().items():
                pos = p(window)
                fwd[reg][pname].append(pos * r_fwd)
            obs.append({"ts": bars[i].ts.date().isoformat(), "regime": reg})

        counts = {}
        for o in obs:
            counts[o["regime"]] = counts.get(o["regime"], 0) + 1
        results["symbols"][sym] = {
            "n_bars": n, "n_obs": len(obs),
            "regime_distribution": {k: round(v / max(len(obs), 1), 4) for k, v in sorted(counts.items())},
        }

    # Router prior: P(next | current)
    for r, row in trans.items():
        tot = sum(row.values())
        results["router_prior"][r] = {k: round(v / tot, 3) for k, v in row.items()} if tot else {}

    # Which policy wins inside each regime?
    results["regime_specialists"] = {}
    for r in REGIMES:
        stats = {}
        for p, xs in fwd[r].items():
            if len(xs) < 10:
                continue
            mu = statistics.mean(xs)
            sd = statistics.pstdev(xs)
            stats[p] = {
                "mean_h_return_bps": round(mu * 1e4, 2),
                "ann_sharpe": round(mu / sd * math.sqrt(252 / HORIZON), 3) if sd else None,
                "n": len(xs),
            }
        best = max(stats, key=lambda p: stats[p]["mean_h_return_bps"]) if stats else None
        results["regime_specialists"][r] = {"winner": best, "policies": stats}

    out_dir = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "moe-001-results.json"), "w") as fh:
        json.dump(results, fh, indent=2)

    print(json.dumps(results["symbols"], indent=1))
    print("winners:", {r: v["winner"] for r, v in results["regime_specialists"].items()})
    print("saved -> outputs/moe-001-results.json")


if __name__ == "__main__":
    main()
