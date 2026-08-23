from __future__ import annotations

import math
import statistics
from dataclasses import replace
from datetime import datetime

from .schema import Bar, MarketFeatures, MarketPacket, PointInTimeDatum


def pct_returns(bars: list[Bar]) -> list[float]:
    out: list[float] = []
    for a, b in zip(bars, bars[1:]):
        out.append((b.close / a.close) - 1.0 if a.close else 0.0)
    return out


def _mean(xs: list[float]) -> float:
    return statistics.mean(xs) if xs else 0.0


def _stdev(xs: list[float]) -> float:
    return statistics.pstdev(xs) if len(xs) > 1 else 0.0


def _clip(x: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))


def feature_vector(bars: list[Bar], *, fast: int = 6, slow: int = 24) -> MarketFeatures:
    if len(bars) < max(slow + 1, 8):
        raise ValueError("not enough bars for features")
    closes = [b.close for b in bars]
    rets = pct_returns(bars)
    fast_r = rets[-fast:]
    slow_r = rets[-slow:]
    prev_fast = rets[-2 * fast:-fast] if len(rets) >= 2 * fast else rets[:-fast]
    prev_slow = rets[-2 * slow:-slow] if len(rets) >= 2 * slow else rets[:-slow]

    # Direction is normalized drift; strength is trend signal-to-noise.
    slow_mu = _mean(slow_r)
    slow_sd = _stdev(slow_r)
    fast_mu = _mean(fast_r)
    fast_sd = _stdev(fast_r)
    direction = _clip(slow_mu / max(slow_sd, 1e-6) / 3.0)
    strength = _clip(abs(slow_mu) / max(slow_sd, 1e-6) / 3.0, 0.0, 1.0)
    volatility = _clip(slow_sd * math.sqrt(slow) * 12.0, 0.0, 1.0)

    prev_mu = _mean(prev_slow)
    prev_sd = _stdev(prev_slow)
    prev_direction = _clip(prev_mu / max(prev_sd, 1e-6) / 3.0) if prev_slow else 0.0
    prev_strength = _clip(abs(prev_mu) / max(prev_sd, 1e-6) / 3.0, 0.0, 1.0) if prev_slow else 0.0
    prev_vol = _clip(prev_sd * math.sqrt(max(len(prev_slow), 1)) * 12.0, 0.0, 1.0) if prev_slow else 0.0

    peak = max(closes[-slow:])
    drawdown = (closes[-1] / peak - 1.0) if peak else 0.0

    vols = [b.volume for b in bars[-slow:]]
    vmu = _mean(vols)
    vsd = _stdev(vols)
    volume_z = _clip((vols[-1] - vmu) / max(vsd, 1e-6) / 3.0) if vols else 0.0

    return MarketFeatures(
        direction=direction,
        strength=strength,
        volatility=volatility,
        direction_change=direction - prev_direction,
        strength_change=strength - prev_strength,
        volatility_change=volatility - prev_vol,
        drawdown=drawdown,
        volume_z=volume_z,
    )


def available_context(items: list[PointInTimeDatum], as_of: datetime) -> tuple[PointInTimeDatum, ...]:
    return tuple(sorted((x for x in items if x.available_at <= as_of), key=lambda x: (x.available_at, x.key)))


def packet_from_bars(
    bars: list[Bar],
    context: list[PointInTimeDatum] | None = None,
    *,
    metadata: dict | None = None,
    return_window: int = 12,
) -> MarketPacket:
    if not bars:
        raise ValueError("bars required")
    feat = feature_vector(bars)
    rets = pct_returns(bars)[-return_window:]
    as_of = bars[-1].ts
    return MarketPacket(
        instrument=bars[-1].instrument,
        as_of=as_of,
        price=bars[-1].close,
        features=feat,
        recent_returns=tuple(rets),
        context=available_context(context or [], as_of),
        metadata=metadata or {},
    )
