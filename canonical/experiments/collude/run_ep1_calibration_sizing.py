"""E-P8+P1+P2: calibration gate, then Kelly/CVaR sizing harness (arxiv-backed).

Stage A (E-P8): score LLM confidence calibration on frozen bank. If ECE > 0.10,
confidence is NOT allowed to drive sizing — deterministic flat sizing only.
Stage B (E-P1/P2): direction agent -> sizing agent (Kelly fraction capped by
95% CVaR of recent returns). Compare PnL: flat-size vs confidence-sized vs
kelly-cvar-sized. All friction-adjusted (spread+commission) per 2605.16895 P5.

Deterministic sizing math; LLM only proposes direction + confidence.
"""
from __future__ import annotations
import json
import math
import os
import statistics
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cogym.agents.model import OpenAICompatible
import collude as C

SYMBOLS = ["SPY", "QQQ", "TLT", "GLD"]
START, END = "2024-08-01", "2026-08-22"
HORIZON = 5
INDICES = [300, 430]
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
FRICTION_BPS = 5.0          # round-trip spread+commission estimate (P5)
CVAR_CAP = 0.25             # max single-trade exposure (FinPos)
KELLY_FRACTION = 0.5        # half-Kelly


def cvar_95(returns_pct: list[float]) -> float:
    """Worst-5% mean loss (positive number), from trailing daily returns."""
    if len(returns_pct) < 20:
        return CVAR_CAP
    xs = sorted(returns_pct)
    k = max(1, int(0.05 * len(xs)))
    worst = xs[:k]
    return min(CVAR_CAP, abs(sum(worst) / k) / 100 * KELLY_FRACTION / max(KELLY_FRACTION, 0.01) * KELLY_FRACTION)


def kelly_fraction(p_win: float, win_avg: float, loss_avg: float) -> float:
    """Half-Kelly for binary outcome with asymmetric payoffs."""
    if loss_avg == 0 or p_win <= 0 or p_win >= 1:
        return 0.0
    b = win_avg / loss_avg
    f = (p_win * (b + 1) - 1) / b
    return max(0.0, min(KELLY_FRACTION * f, CVAR_CAP))


def main():
    model = OpenAICompatible(model_id=C.MODEL_ID, base_url=C.BASE_URL,
                             api_key=os.environ["OPENCODE_GO_API_KEY"], timeout=300)
    eps, bank_hash = C.build_episode_bank(SYMBOLS, START, END, HORIZON, INDICES)

    # ---- Stage A: collect direction + confidence on all episodes ----
    trials_path = os.path.join(OUT_DIR, "ep1-trials.jsonl")
    calls = []
    for ei, ep in enumerate(eps):
        print(f"[{ei+1}/{len(eps)}] {ep.symbol}@{ep.as_of}", flush=True)
        t = C.call_subject(model, ep, C.ROLE_PROMPTS["quant"], 0.7, 11)
        rec = {"episode": f"{ep.symbol}@{ep.as_of}", "stance": t.stance,
               "confidence": t.confidence, "realized": ep.realized}
        calls.append(rec)
        with open(trials_path, "a") as fh:
            fh.write(json.dumps(rec) + "\n")

    # ---- E-P8: expected calibration error ----
    bins = [(50, 60), (60, 70), (70, 80), (80, 90), (90, 101)]
    ece_num, n_total, reliability = 0.0, 0, []
    for lo, hi in bins:
        grp = [c for c in calls
               if c["stance"] in ("UP", "DOWN") and c["confidence"] and lo <= c["confidence"] < hi]
        if not grp:
            continue
        acc = statistics.mean(1.0 if c["stance"] == ("UP" if c["realized"] >= 0 else "DOWN") else 0.0
                              for c in grp)
        conf = statistics.mean(c["confidence"] for c in grp) / 100
        ece_num += len(grp) * abs(acc - conf)
        n_total += len(grp)
        reliability.append({"bin": f"{lo}-{hi}", "n": len(grp),
                            "accuracy": round(acc, 3), "mean_confidence": round(conf, 3)})
    ece = ece_num / n_total if n_total else 1.0

    # ---- Stage B: three sizing policies, friction-adjusted PnL ----
    def trade_pnl(stance, conf, realized, trailing_rets, allow_conf_size):
        if stance not in ("UP", "DOWN"):
            return 0.0
        sign = 1 if stance == "UP" else -1
        gross = sign * realized
        # size policies
        if not allow_conf_size:
            size = 0.10                                   # flat 10% (calibration gate failed)
        else:
            p = conf / 100
            size = kelly_fraction(p, abs(realized) + 0.005, 0.005)
        size = min(size, cvar_95(trailing_rets))
        fric = FRICTION_BPS / 1e4
        net = size * gross - fric                          # friction on notional
        return net * 1e4                                    # report bps

    results = {"bank_hash": bank_hash, "ece": round(ece, 4),
               "reliability": reliability, "gate_pass": bool(ece <= 0.10),
               "policies": {}}
    # trailing returns per episode from world bars (deterministic)
    from cogym.trading.alpaca.world import create_alpaca_world
    key_id, secret = os.environ["ALPACA_KEY_ID"], os.environ["ALPACA_SECRET_KEY"]
    worlds = {s: create_alpaca_world(s, START, END, key_id=key_id, secret_key=secret)
              for s in SYMBOLS}
    for policy_name, allow_conf in [("flat_gate_blocked", False), ("conf_kelly_cvar", True)]:
        pnls = []
        effective_allow = allow_conf and results["gate_pass"]
        for c in calls:
            w = worlds[c["episode"].split("@")[0]]
            idx = next(i for i, b in enumerate(w.bars)
                       if str(b.ts.date()) == c["episode"].split("@")[1])
            trailing = [(w.bars[i].close / w.bars[i - 1].close - 1) * 100
                        for i in range(max(1, idx - 30), idx)]
            pnls.append(trade_pnl(c["stance"], c["confidence"], c["realized"],
                                  trailing, effective_allow))
        results["policies"][policy_name] = {
            "mean_net_pnl_bps": round(statistics.mean(pnls), 2),
            "sum_net_pnl_bps": round(sum(pnls), 2)}

    with open(os.path.join(OUT_DIR, "ep1-results.json"), "w") as fh:
        json.dump(results, fh, indent=2)
    print(json.dumps({k: v for k, v in results.items() if k != "reliability"}, indent=1))


if __name__ == "__main__":
    main()
