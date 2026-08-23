"""COLLUDE core: frozen episode bank + team topologies + deterministic scoring.

Subjects are ox-alpha-free via cogym.agents.model.OpenAICompatible (fresh session
per call). Aggregation and scoring are deterministic. No LLM grades itself.
"""
from __future__ import annotations
import hashlib
import json
import math
import os
import re
import sys
import time
from dataclasses import dataclass, field

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from cogym.agents.model import OpenAICompatible, Message
from cogym.trading.alpaca.world import create_alpaca_world

MODEL_ID = "ox-alpha-free"
BASE_URL = "https://opencode.ai/zen/go/v1"

DECISION_FORMAT = ('Reply with ONLY a JSON object: '
                   '{"stance":"UP"|"DOWN","confidence":<0-100>,"reason":"<=25 words"}')

ROLE_PROMPTS = {
    "homogeneous": "You are a disciplined discretionary trader making a 5-day directional call on one instrument.",
    "bull": "You are a momentum trader. You look for continuation setups and upside breakouts.",
    "bear": "You are a risk-focused short-biased analyst. You look for distribution patterns, failed rallies, and downside catalysts.",
    "quant": "You are a quantitative strategist. You weight base rates, volatility regimes, and mean reversion over narratives.",
}
GOD_SYSTEM = ("You are the portfolio supervisor. You receive independent stances from three "
              "analysts with confidence levels. Weigh them, discount overconfidence, and emit your own call. "
              + DECISION_FORMAT)

STANCE_RE = re.compile(r'"stance"\s*:\s*"?(UP|DOWN)"?', re.I)
CONF_RE = re.compile(r'"confidence"\s*:\s*([0-9]{1,3})')


@dataclass
class Episode:
    symbol: str
    as_of: str          # decision date (features end at prior close)
    price: float
    realized: float     # forward HORIZON-day return, hidden from subjects
    window: str         # compact point-in-time market summary


@dataclass
class Trial:
    episode: Episode
    condition: str
    role: str
    raw: str = ""
    stance: str | None = None      # UP/DOWN/UNPARSEABLE
    confidence: float | None = None
    latency_s: float = 0.0
    error: str | None = None


def build_episode_bank(symbols, start, end, horizon, indices) -> list[Episode]:
    """Frozen BEFORE any inference. Deterministic selection by index."""
    key_id = os.environ["ALPACA_KEY_ID"]
    secret = os.environ["ALPACA_SECRET_KEY"]
    eps = []
    for sym in symbols:
        w = create_alpaca_world(sym, start, end, key_id=key_id, secret_key=secret)
        bars = w.bars
        for i in indices:
            win = bars[max(0, i - 60):i]           # PIT: ends before decision bar
            entry, exit_ = bars[i].close, bars[min(i + horizon, len(bars) - 1)].close
            rets = [(win[j].close / win[j - 1].close - 1) * 100 for j in range(1, len(win))]
            hi = max(b.high for b in win[-21:])
            lo = min(b.low for b in win[-21:])
            sd = (sum((r - sum(rets) / len(rets)) ** 2 for r in rets) / len(rets)) ** .5
            window = (
                f"{sym} daily bars. Decision date {bars[i].ts.date()}. Last close ${entry:.2f}. "
                f"Returns % last 10 days: {[round(r, 2) for r in rets[-10:]]}. "
                f"21d range: ${lo:.2f}-${hi:.2f}. 60d daily vol: {sd:.2f}%. "
                f"Distance from 21d high: {(entry / hi - 1) * 100:.1f}%."
            )
            eps.append(Episode(symbol=sym, as_of=bars[i].ts.date().isoformat(), price=entry,
                               realized=exit_ / entry - 1.0, window=window))
    bank_hash = hashlib.sha256(json.dumps(
        [(e.symbol, e.as_of, e.price, round(e.realized, 6)) for e in eps]).encode()).hexdigest()
    return eps, bank_hash


def call_subject(model: OpenAICompatible, ep: Episode, system: str, temperature: float,
                 seed: int, extra_context: str = "") -> Trial:
    t0 = time.time()
    user = ep.window + "\n\nCommit to a 5-day directional view.\n" + DECISION_FORMAT
    if extra_context:
        user += "\n\nTeammate input:\n" + extra_context
    try:
        raw = model.complete(
            [Message(role="system", content=system), Message(role="user", content=user)],
            temperature=temperature, seed=seed)
    except Exception as e:
        return Trial(episode=ep, condition="", role="", raw="", error=str(e)[:300],
                     latency_s=time.time() - t0)
    ms = STANCE_RE.search(raw)
    mc = CONF_RE.search(raw)
    return Trial(episode=ep, condition="", role="",
                 stance=(ms.group(1).upper() if ms else "UNPARSEABLE"),
                 confidence=(float(mc.group(1)) if mc else None),
                 raw=raw[-800:], latency_s=time.time() - t0)


def parse_stance(t: Trial) -> str:
    return t.stance or "UNPARSEABLE"


def majority(stances: list[str]) -> str:
    up = sum(1 for s in stances if s == "UP")
    down = sum(1 for s in stances if s == "DOWN")
    if up > down: return "UP"
    if down > up: return "DOWN"
    return "ABSTAIN"


def conf_weighted(trials: list[Trial]) -> str:
    up = sum((t.confidence or 50) for t in trials if t.stance == "UP")
    down = sum((t.confidence or 50) for t in trials if t.stance == "DOWN")
    if not up and not down: return "ABSTAIN"
    if up == down: return majority([t.stance for t in trials])
    return "UP" if up > down else "DOWN"


# ---- deterministic god baselines (the bar an LLM supervisor must clear) ----
def god_mean_conf(trials: list[Trial]) -> str:
    return conf_weighted(trials)


def score(direction: str, ep: Episode) -> float:
    """Signed utility: correct direction earns |realized|, wrong pays it."""
    if direction in ("UP", "DOWN"):
        want = "UP" if ep.realized >= 0 else "DOWN"
        return abs(ep.realized) if direction == want else -abs(ep.realized)
    return 0.0


def brier(direction: str, conf: float | None, ep: Episode) -> float | None:
    if direction not in ("UP", "DOWN"):
        return None
    p_up = ((conf or 50) / 100.0) if direction == "UP" else 1 - ((conf or 50) / 100.0)
    y = 1.0 if ep.realized >= 0 else 0.0
    return (p_up - y) ** 2


def summarize(name: str, calls: list[Trial], aggregated: dict) -> dict:
    utils, briers, decided = [], [], 0
    n_decided = 0
    per_ep: dict[str, dict] = {}
    for ep_key, agg in aggregated.items():
        ep = next(e for e in calls[0:1])  # placeholder; real lookup below
    # aggregate-level scoring done by caller; here we do per-call stats
    unparseable = sum(1 for c in calls if c.stance == "UNPARSEABLE")
    errors = sum(1 for c in calls if c.error)
    lat = [c.latency_s for c in calls if c.latency_s]
    up_share = 0.0
    valid = [c for c in calls if c.stance in ("UP", "DOWN")]
    if valid:
        up_share = sum(1 for c in valid if c.stance == "UP") / len(valid)
    return {
        "condition": name,
        "n_calls": len(calls), "unparseable": unparseable, "errors": errors,
        "up_share": round(up_share, 3),
        "mean_latency_s": round(sum(lat) / len(lat), 1) if lat else None,
    }
