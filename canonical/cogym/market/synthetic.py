from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import math
import random

from ..canonical import commitment
from .schema import Bar


@dataclass(frozen=True)
class Regime:
    steps: int
    drift: float
    volatility: float
    mean_reversion: float = 0.0
    jump_probability: float = 0.0
    jump_scale: float = 0.0
    label: str = ""


@dataclass(frozen=True)
class WorldSpec:
    seed: int
    instrument: str
    start_price: float
    regimes: tuple[Regime, ...]
    start_time: datetime = datetime(2025, 1, 1, tzinfo=timezone.utc)
    step_seconds: int = 60
    version: str = "synthetic-v2"

    @property
    def world_id(self) -> str:
        return commitment("COGYM:WORLD:v2", self)


LEVELS: dict[int, str] = {
    0: "clean trend",
    1: "trend then reversal",
    2: "calm then shock then recovery",
    3: "fake breakout and reversal",
    4: "chop then crisis then repair",
    5: "repeating edge that abruptly stops working",
    6: "multi-shock adversarial nonstationarity",
}


def level_world(level: int, seed: int, instrument: str = "SYNTH") -> WorldSpec:
    if level == 0:
        regimes = (Regime(180, 0.0012, 0.003, label="trend"),)
    elif level == 1:
        regimes = (Regime(90, 0.0012, 0.004, label="bull"), Regime(90, -0.0016, 0.005, label="reversal"))
    elif level == 2:
        regimes = (
            Regime(70, 0.0002, 0.002, label="calm"),
            Regime(25, -0.004, 0.014, jump_probability=0.12, jump_scale=0.035, label="shock"),
            Regime(85, 0.0015, 0.006, label="recovery"),
        )
    elif level == 3:
        regimes = (
            Regime(65, 0.0007, 0.003, label="build"),
            Regime(25, 0.0025, 0.006, label="breakout"),
            Regime(90, -0.0018, 0.008, label="trap"),
        )
    elif level == 4:
        regimes = (
            Regime(60, 0.0, 0.006, mean_reversion=0.18, label="chop"),
            Regime(45, -0.003, 0.015, jump_probability=0.08, jump_scale=0.04, label="crisis"),
            Regime(75, 0.0010, 0.009, mean_reversion=0.08, label="repair"),
        )
    elif level == 5:
        regimes = (
            Regime(70, 0.0011, 0.004, label="edge_a"),
            Regime(45, -0.0010, 0.004, mean_reversion=0.12, label="edge_break"),
            Regime(65, 0.0001, 0.009, mean_reversion=0.25, label="anti_edge"),
        )
    elif level == 6:
        regimes = (
            Regime(45, 0.0010, 0.003, label="calm_trend"),
            Regime(25, -0.0035, 0.014, jump_probability=0.15, jump_scale=0.05, label="crash"),
            Regime(35, 0.0028, 0.012, label="violent_rebound"),
            Regime(30, 0.0, 0.010, mean_reversion=0.28, label="whipsaw"),
            Regime(45, -0.0010, 0.006, label="slow_decay"),
        )
    else:
        raise ValueError("level must be 0..6")
    return WorldSpec(seed=seed, instrument=instrument, start_price=100.0, regimes=regimes)


def generate(spec: WorldSpec) -> list[Bar]:
    rng = random.Random(spec.seed)
    price = spec.start_price
    anchor = price
    t = spec.start_time
    out: list[Bar] = []
    for regime in spec.regimes:
        for _ in range(regime.steps):
            noise = rng.gauss(0.0, regime.volatility)
            reversion = regime.mean_reversion * ((anchor / max(price, 1e-9)) - 1.0)
            jump = 0.0
            if regime.jump_probability and rng.random() < regime.jump_probability:
                jump = rng.gauss(0.0, regime.jump_scale)
            ret = regime.drift + noise + reversion + jump
            open_ = price
            price = max(0.01, price * math.exp(ret))
            span = abs(rng.gauss(0.0, max(regime.volatility, 0.0005))) * price
            high = max(open_, price) + span * 0.35
            low = max(0.001, min(open_, price) - span * 0.35)
            volume = max(0.0, 1000.0 * (1.0 + abs(ret) * 80 + rng.random() * 0.3))
            out.append(Bar(spec.instrument, t, open_, high, low, price, volume))
            t += timedelta(seconds=spec.step_seconds)
        anchor = price
    return out
