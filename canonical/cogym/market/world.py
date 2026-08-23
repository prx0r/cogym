from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ..canonical import commitment
from .features import packet_from_bars
from .schema import Bar, MarketPacket, PointInTimeDatum


@dataclass(frozen=True)
class WorldManifest:
    name: str
    instrument: str
    source: str
    bars_digest: str
    context_digest: str
    start: datetime
    end: datetime
    resolution_seconds: int
    metadata: dict = field(default_factory=dict)

    @property
    def world_id(self) -> str:
        return commitment("COGYM:MARKET_WORLD:v1", self)


@dataclass
class TradingWorld:
    manifest: WorldManifest
    bars: list[Bar]
    context: list[PointInTimeDatum] = field(default_factory=list)

    def snapshot(self, index: int, *, lookback: int = 72) -> MarketPacket:
        if index < 0 or index >= len(self.bars):
            raise IndexError(index)
        lo = max(0, index - lookback + 1)
        window = self.bars[lo:index + 1]
        if len(window) < 25:
            raise ValueError("snapshot requires at least 25 bars")
        return packet_from_bars(window, self.context, metadata={
            "world_id": self.manifest.world_id,
            "bar_index": index,
            "source": self.manifest.source,
        })

    def realized_return(self, index: int, horizon_steps: int) -> float:
        j = min(index + horizon_steps, len(self.bars) - 1)
        p0 = self.bars[index].close
        return self.bars[j].close / p0 - 1.0 if p0 else 0.0
