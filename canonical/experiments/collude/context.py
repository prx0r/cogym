"""Rich market context for COLLUDE subjects: classic algo-trading indicators,
PIT-safe news headlines, intraday confirmation. All deterministic Python.

Point-in-time discipline: every feature computed from bars strictly BEFORE the
decision bar; news filtered to created_at < decision date. Current-only data
(options IV snapshots) is NEVER used in replay banks — deployment only.
"""
from __future__ import annotations
import json
import os
import statistics
import urllib.request
from collections import deque


# ---------- core indicator helpers ----------

def sma(xs, n):
    return sum(xs[-n:]) / min(n, len(xs)) if xs else None


def ema_series(xs, n):
    k = 2 / (n + 1)
    out = [xs[0]]
    for x in xs[1:]:
        out.append(x * k + out[-1] * (1 - k))
    return out


def rsi(closes, n=14):
    if len(closes) < n + 1:
        return None
    gains, losses = [], []
    for i in range(len(closes) - n, len(closes)):
        d = closes[i] - closes[i - 1]
        gains.append(max(d, 0)); losses.append(max(-d, 0))
    ag, al = sum(gains) / n, sum(losses) / n
    if al == 0:
        return 100.0
    rs = ag / al
    return 100 - 100 / (1 + rs)


def macd(closes):
    if len(closes) < 35:
        return None, None, None
    e12, e26 = ema_series(closes, 12), ema_series(closes, 26)
    line = [a - b for a, b in zip(e12, e26)]
    sig = ema_series(line[-63:], 9)
    hist = line[-1] - sig[-1]
    return line[-1], sig[-1], hist


def atr(bars, n=14):
    if len(bars) < n + 1:
        return None
    trs = []
    for i in range(len(bars) - n + 1, len(bars)):
        h, l, pc = bars[i].high, bars[i].low, bars[i - 1].close
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    return sum(trs) / len(trs)


def bollinger(closes, n=20, k=2.0):
    w = closes[-n:]
    mu = sum(w) / n
    sd = statistics.pstdev(w)
    if sd == 0:
        return None, None
    pb = (closes[-1] - (mu - k * sd)) / (2 * k * sd)
    return pb, (2 * k * sd) / mu * 100


def ret(closes, n):
    return (closes[-1] / closes[-1 - n] - 1) * 100 if len(closes) > n else None


# ---------- the big one ----------

def rich_window_text(bars, vw=None) -> str:
    """Full technical panel from a PIT bar window. ~220 words, stable field order."""
    closes = [b.close for b in bars]
    c = closes[-1]
    s20, s50 = sma(closes, 20), sma(closes, 50)
    mline, msig, mhist = macd(closes)
    r = rsi(closes)
    pb, bw = bollinger(closes)
    a = atr(bars)
    hi21, lo21 = max(b.high for b in bars[-21:]), min(b.low for b in bars[-21:])
    rng_pos = (c - lo21) / (hi21 - lo21) * 100 if hi21 > lo21 else 50.0
    dd60 = (c / max(b.close for b in bars[-60:]) - 1) * 100
    v10 = statistics.pstdev([bars[i].close / bars[i - 1].close - 1
                             for i in range(len(bars) - 10, len(bars))])
    v60 = statistics.pstdev([bars[i].close / bars[i - 1].close - 1
                             for i in range(len(bars) - 60, len(bars))])
    vol_ratio = v10 / v60 if v60 else None
    vols = [b.volume for b in bars]
    vol_z = (vols[-1] - sum(vols[-21:]) / 21) / (statistics.pstdev(vols[-21:]) or 1e-9)
    up_days = sum(1 for i in range(len(closes) - 10, len(closes))
                  if closes[i] > closes[i - 1])
    lines = [
        f"Price ${c:.2f} | 1d {ret(closes,1):+.1f}% 5d {ret(closes,5):+.1f}% "
        f"10d {ret(closes,10):+.1f}% 21d {ret(closes,21):+.1f}%",
        f"SMA20 ${s20:.2f} ({(c/s20-1)*100:+.1f}%) SMA50 ${s50:.2f} ({(c/s50-1)*100:+.1f}%) "
        f"trend={'UP' if s20>s50 else 'DOWN'}",
        f"RSI14 {r:.0f} | MACD hist {mhist:+.2f} ({'bull' if mhist>0 else 'bear'})",
        f"Bollinger %B {pb*100:.0f} bandwidth {bw:.1f}% | ATR14 {(a/c)*100:.1f}%",
        f"21d range position {rng_pos:.0f}% | drawdown from 60d high {dd60:+.1f}%",
        f"Vol regime: 10d/60d sigma {vol_ratio:.2f}x {'(calming)' if vol_ratio<1 else '(heating)'}",
        f"Volume: today z={vol_z:+.1f}, up-days {up_days}/10",
    ]
    if vw:
        v21 = [x for x in vw[-21:] if x]
        if v21:
            vwap21 = sum(v21) / len(v21)
            lines.append(f"Close vs 21d VWAP: {(c/vwap21-1)*100:+.1f}%")
    return "\n".join(lines)


# ---------- news (PIT-filtered) ----------

def fetch_news(symbol: str, before_iso: str, limit: int = 4, max_words: int = 22) -> list[str]:
    url = (f"https://data.alpaca.markets/v1beta1/news?symbols={symbol}"
           f"&end={before_iso[:10]}T23:59:59Z&limit={limit}&sort=desc")
    req = urllib.request.Request(url, headers={
        "APCA-API-KEY-ID": os.environ["ALPACA_KEY_ID"],
        "APCA-API-SECRET-KEY": os.environ["ALPACA_SECRET_KEY"],
        "User-Agent": "CogymLab/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            items = json.load(r).get("news", [])
        out = []
        for it in items:
            if it.get("created_at", "") >= before_iso[:10] + "T23:59:59Z":
                continue  # PIT guard
            words = " ".join((it.get("headline") or "").split()[:max_words])
            out.append(f"[{it['created_at'][:10]}] {words}")
        return out
    except Exception:
        return []


# ---------- hourly intraday confirmation ----------

def hourly_confirmation_text(symbol: str, day_before: str,
                             key_id: str, secret_key: str, hours: int = 48) -> str | None:
    """Last `hours` of hourly bars ending BEFORE the decision date."""
    import datetime as dt
    end = dt.date.fromisoformat(day_before[:10])
    start = end - dt.timedelta(days=3)
    from cogym.trading.alpaca.source import fetch_bars
    raw = fetch_bars(symbol, start.isoformat(), end.isoformat(), timeframe="1Hour",
                     api_key_id=key_id, api_secret_key=secret_key)
    if not raw:
        return None
    raw = raw[-hours:]
    closes = [b["c"] for b in raw]
    chg = (closes[-1] / closes[0] - 1) * 100
    up = sum(1 for i in range(1, len(closes)) if closes[i] > closes[i - 1])
    return (f"Last {len(raw)}h: {chg:+.1f}% with {up}/{len(raw)-1} rising hours "
            f"(last close ${closes[-1]:.2f})")
