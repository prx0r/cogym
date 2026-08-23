from __future__ import annotations

from datetime import timedelta

from ..canonical import commitment
from ..market.synthetic import generate, level_world
from ..market.world import TradingWorld, WorldManifest


def synthetic_trading_world(level: int, seed: int, instrument: str = "SYNTH") -> TradingWorld:
    spec = level_world(level, seed, instrument)
    bars = generate(spec)
    bars_digest = commitment("COGYM:BARS:v1", bars)
    manifest = WorldManifest(
        name=f"level-{level}-{seed}",
        instrument=instrument,
        source=f"synthetic:{spec.version}:level={level}:seed={seed}",
        bars_digest=bars_digest,
        context_digest=commitment("COGYM:CONTEXT:v1", []),
        start=bars[0].ts,
        end=bars[-1].ts,
        resolution_seconds=spec.step_seconds,
        metadata={"level": level, "synthetic_world_id": spec.world_id},
    )
    return TradingWorld(manifest, bars, [])
