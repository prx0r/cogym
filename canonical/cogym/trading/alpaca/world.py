"""AlpacaTradingWorld: real market data as a deterministic cogym world."""
from __future__ import annotations
import hashlib
from .source import fetch_bars
from ...market.world import TradingWorld, WorldManifest
from ...market.schema import Bar
from datetime import datetime

_RESOLUTIONS = {"1Min": 60, "1Hour": 3600, "1Day": 86400, "1Week": 604800, "1Month": 2592000}


def create_alpaca_world(symbol: str, start: str, end: str,
                        key_id: str, secret_key: str,
                        timeframe: str = "1Day", feed: str = "iex") -> TradingWorld:
    """Fetch real bars from Alpaca and build a deterministic TradingWorld.

    bars_digest is a content hash of the actual OHLCV payload (AGENTS.md
    convention 2: content-hash IDs everywhere), so two fetches of the same
    window produce identical world_ids and any upstream data revision is
    detectable.
    """
    raw = fetch_bars(symbol, start, end, timeframe=timeframe,
                     api_key_id=key_id, api_secret_key=secret_key, feed=feed)
    if not raw:
        raise RuntimeError(f"alpaca returned no bars for {symbol} {start}..{end}")

    bars = [
        Bar(
            instrument=symbol,
            ts=datetime.fromisoformat(b["t"].replace("Z", "+00:00")),
            open=b["o"], high=b["h"], low=b["l"], close=b["c"], volume=b["v"],
        )
        for b in raw
    ]

    payload = "".join(f"{b.ts.isoformat()}|{b.open}|{b.high}|{b.low}|{b.close}|{b.volume};"
                      for b in bars).encode()
    digest = hashlib.sha256(payload).hexdigest()

    manifest = WorldManifest(
        name=f"alpaca-{symbol}-{timeframe}-{start[:10]}-{end[:10]}",
        instrument=symbol,
        source=f"alpaca:{feed}:{symbol}",
        bars_digest=digest,
        context_digest="",
        start=bars[0].ts,
        end=bars[-1].ts,
        resolution_seconds=_RESOLUTIONS.get(timeframe, 86400),
        metadata={"source": "alpaca", "n_bars": len(bars), "timeframe": timeframe},
    )
    return TradingWorld(manifest=manifest, bars=bars, context=[])
