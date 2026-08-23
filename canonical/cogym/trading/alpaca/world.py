"""AlpacaTradingWorld: real market data as a deterministic cogym world."""
from __future__ import annotations
from ..source import fetch_bars
from ...market.world import TradingWorld, WorldManifest
from ...market.synthetic import WorldSpec
from datetime import datetime

def create_alpaca_world(symbol: str, start: str, end: str,
                        key_id: str, secret_key: str) -> TradingWorld:
    """Fetch real bars from Alpaca and build a deterministic TradingWorld."""
    raw = fetch_bars(symbol, start, end, api_key_id=key_id, api_secret_key=secret_key)
    
    # Convert to Bar-like objects compatible with existing system
    from ...market.schema import Bar
    from datetime import timezone
    bars = []
    for b in raw:
        bars.append(Bar(
            ts=datetime.fromisoformat(b["t"].replace("Z", "+00:00")),
            open=b["o"], high=b["h"], low=b["l"], close=b["c"], volume=b["v"]
        ))
    
    digest = f"alpaca:{symbol}:{start}:{end}"
    manifest = WorldManifest(
        name=f"alpaca-{symbol}-{start[:10]}-{end[:10]}",
        instrument=symbol,
        source=f"alpaca:{symbol}",
        bars_digest=digest,
        context_digest="",
        start=bars[0].ts if bars else None,
        end=bars[-1].ts if bars else None,
        resolution_seconds=86400,  # daily
        metadata={"source": "alpaca", "n_bars": len(bars)},
    )
    return TradingWorld(manifest=manifest, bars=bars, context=[])
