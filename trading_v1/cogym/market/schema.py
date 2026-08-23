from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Bar:
    instrument: str
    ts: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


@dataclass(frozen=True)
class PointInTimeDatum:
    key: str
    value: Any
    observed_at: datetime
    available_at: datetime
    source: str = ""
    provenance: str = ""


@dataclass(frozen=True)
class MarketFeatures:
    direction: float
    strength: float
    volatility: float
    direction_change: float
    strength_change: float
    volatility_change: float
    drawdown: float
    volume_z: float


@dataclass(frozen=True)
class MarketPacket:
    instrument: str
    as_of: datetime
    price: float
    features: MarketFeatures
    recent_returns: tuple[float, ...]
    context: tuple[PointInTimeDatum, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)
