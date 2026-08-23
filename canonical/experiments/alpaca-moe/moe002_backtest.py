"""ALPACA-MOE-002: Does regime-routed specialization beat any single fixed policy?

Walk-forward on real Alpaca daily bars. At each step t:
  - compute features from bars[.., t-1] (point-in-time safe)
  - route to the specialist whose policy classically matches the regime
  - take position for HORIZON days
Compare equity curves: routed team vs each individual policy held everywhere.

Honest-claims discipline: no lookahead, no parameter search inside the loop,
single frozen pass. Results are directional evidence, not alpha claims.
"""
from __future__ import annotations
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from cogym.trading.alpaca.world import create_alpaca_world

HORIZON = 5
LOOKBACK = 60
SYMBOLS = ["SPY", "QQQ", "TLT", "GLD"]
START, END = "2024-08-01", "2026-08-22"

# same calibrated thresholds as moe001
def classify(direction, strength, volatility):
    if strength >= 0.08 and direction >= 0.04:
        return "BULL_TREND"
    if strength >= 0.08 and direction <= -0.04:
        return "BEAR_TREND"
    if volatility >= 0.55:
        return "HIGH_VOL_CHOP"
    return "QUIET_RANGE"


def feat(bars):
    """Minimal PIT feature computation matching cogym's normalization."""
    import statistics
    rets = [(bars[i].close / bars[i - 1].close) - 1.0 for i in range(1, len(bars))]
    slow = rets[-24:]
    mu = statistics.mean(slow)
    sd = statistics.pstdev(slow)
    direction = max(-1.0, min(1.0, mu / max(sd, 1e-6) / 3.0))
    strength = max(0.0, min(1.0, abs(mu) / max(sd, 1e-6) / 3.0))
    volatility = max(0.0, min(1.0, sd * math.sqrt(len(slow)) * 12.0))
    return direction, strength, volatility


def pos_momentum(win):
    return 1.0 if win[-1].close > win[-7].close else 0.0


def pos_always(win):
    return 1.0


def pos_defensive(win):
    return 0.5 if win[-1].close >= min(b.close for b in win[-21:]) * 1.02 else 0.0


def pos_dip_buyer(win):
    d = win[-1].close / max(b.close for b in win[-21:]) - 1.0
    return 1.0 if d <= -0.03 else 0.25


SPECIALISTS = {
    "BULL_TREND": ("momentum", pos_momentum),
    "BEAR_TREND": ("dip_buyer", pos_dip_buyer),   # long-only account: stand aside unless capitulation dip
    "HIGH_VOL_CHOP": ("defensive", pos_defensive),
    "QUIET_RANGE": ("momentum", pos_momentum),
}


def main():
    key_id, secret = os.environ["ALPACA_KEY_ID"], os.environ["ALPACA_SECRET_KEY"]
    curves = {"routed_team": [1.0], **{k: [1.0] for k in ["momentum", "always_long", "defensive", "dip_buyer"]}}
    regime_path = []
    flips = 0
    prev_spec = None

    for sym in SYMBOLS:
        w = create_alpaca_world(sym, START, END, key_id=key_id, secret_key=secret)
        bars = w.bars
        n = len(bars)
        # non-overlapping steps so multi-symbol aggregation stays fair
        for i in range(LOOKBACK, n - HORIZON, HORIZON):
            d, s, v = feat(bars[i - LOOKBACK:i])
            reg = classify(d, s, v)
            entry, exit_ = bars[i].close, bars[i + HORIZON].close
            r = exit_ / entry - 1.0
            win = bars[:i]
            positions = {
                "momentum": pos_momentum(win),
                "always_long": pos_always(win),
                "defensive": pos_defensive(win),
                "dip_buyer": pos_dip_buyer(win),
            }
            spec_name, _ = SPECIALISTS[reg]
            if spec_name != prev_spec:
                flips += 1
                prev_spec = spec_name
            regime_path.append(reg)
            for name, pos in positions.items():
                curves[name].append(curves[name][-1] * (1.0 + pos * r))
            curves["routed_team"].append(curves["routed_team"][-1] * (1.0 + positions[spec_name] * r))

    summary = {}
    n_steps = len(curves["routed_team"]) - 1
    for name, c in curves.items():
        total = c[-1]
        yrs = n_steps * HORIZON / 252
        cagr = total ** (1 / yrs) - 1 if yrs > 0 else 0.0
        peak, mdd = -1e9, 0.0
        for x in c:
            peak = max(peak, x)
            mdd = min(mdd, x / peak - 1.0)
        summary[name] = {"total_return": round(total - 1.0, 4),
                         "cagr": round(cagr, 4),
                         "max_drawdown": round(mdd, 4)}

    out = {
        "spec": "alpaca-moe-002",
        "n_steps_per_symbol": n_steps,
        "specialist_switches": flips,
        "equity_summary": summary,
        "claim_status": "DIRECTIONAL — single frozen pass, no significance test",
    }
    out_dir = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "moe-002-backtest.json"), "w") as fh:
        json.dump(out, fh, indent=2)

    print(f"steps/symbol={n_steps} specialist switches={flips}")
    for name, s in sorted(summary.items(), key=lambda kv: -kv[1]["total_return"]):
        print(f"{name:>12}  total={s['total_return']:+.1%}  cagr={s['cagr']:+.1%}  mdd={s['max_drawdown']:.1%}")


if __name__ == "__main__":
    main()
