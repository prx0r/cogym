from __future__ import annotations
from dataclasses import dataclass
import math, random
from typing import Iterable
from .schema import WorldPacket, WorldSnapshot
from .utils import sha256_id, clamp

@dataclass(frozen=True)
class RegimeSegment:
    length: int
    drift: float
    vol: float
    mean_reversion: float = 0.0
    volume_level: float = 1.0
    label: str = "neutral"
    shock_prob: float = 0.0
    shock_scale: float = 0.0

@dataclass
class WorldSpec:
    instrument: str = "SYNTH_X"
    start_price: float = 100.0
    segments: tuple[RegimeSegment, ...] = (
        RegimeSegment(80, 0.0008, 0.008, label="bull"),
        RegimeSegment(40, 0.0, 0.018, mean_reversion=0.15, label="chop"),
        RegimeSegment(70, -0.0010, 0.014, label="bear"),
    )
    difficulty: float = 5.0
    observation_window: int = 24
    macro_features: tuple[tuple[str, float], ...] = ()

class SyntheticMarketWorld:
    """Deterministic, forkable synthetic market world.

    Same spec+seed -> same sequence. A fork can start from any snapshot and mutate
    only future-generation parameters while preserving the prefix.
    """
    def __init__(self, spec: WorldSpec, seed: int):
        self.spec = spec
        self.seed = seed
        self.world_id = sha256_id(spec.__dict__, seed, prefix="world_")
        self._prices, self._volumes, self._labels = self._generate()

    def _generate(self):
        rng = random.Random(self.seed)
        prices = [self.spec.start_price]
        volumes = [1.0]
        labels = [self.spec.segments[0].label]
        anchor = self.spec.start_price
        for seg in self.spec.segments:
            for _ in range(seg.length):
                p = prices[-1]
                mr = seg.mean_reversion * math.log(anchor / p) if p > 0 else 0.0
                r = seg.drift + mr + rng.gauss(0, seg.vol)
                if rng.random() < seg.shock_prob:
                    r += rng.gauss(0, seg.shock_scale)
                p2 = max(0.01, p * math.exp(r))
                prices.append(p2)
                volumes.append(max(0.01, seg.volume_level * math.exp(rng.gauss(0, 0.25))))
                labels.append(seg.label)
            anchor = prices[-1]
        return prices, volumes, labels

    @property
    def length(self) -> int:
        return len(self._prices) - 1

    def _features(self, t: int) -> WorldPacket:
        w = self.spec.observation_window
        lo = max(1, t - w + 1)
        rets = [math.log(self._prices[i] / self._prices[i-1]) for i in range(lo, t+1)]
        if not rets:
            rets = [0.0]
        mean = sum(rets) / len(rets)
        var = sum((x-mean)**2 for x in rets) / max(1, len(rets)-1)
        vol = math.sqrt(var)
        direction = clamp(mean / (vol + 1e-9) * 2.0, -10, 10)
        strength = clamp(abs(direction), 0, 10)
        vols = self._volumes[lo:t+1]
        vm = sum(vols)/len(vols)
        vs = math.sqrt(sum((v-vm)**2 for v in vols)/max(1, len(vols)-1))
        vz = (self._volumes[t]-vm)/(vs+1e-9)

        prev_t = max(1, t-4)
        prev_lo = max(1, prev_t-w+1)
        prev_rets = [math.log(self._prices[i]/self._prices[i-1]) for i in range(prev_lo, prev_t+1)] or [0.0]
        pm = sum(prev_rets)/len(prev_rets)
        pv = math.sqrt(sum((x-pm)**2 for x in prev_rets)/max(1,len(prev_rets)-1))
        pdir = clamp(pm/(pv+1e-9)*2.0, -10, 10)
        pstr = clamp(abs(pdir),0,10)
        conf = clamp(min(1.0, len(rets)/w) * (0.5 + min(0.5, strength/20)), 0, 1)
        return WorldPacket(
            timestamp=t,
            instrument=self.spec.instrument,
            price=self._prices[t],
            returns=tuple(rets[-w:]),
            volatility=vol,
            volume_z=vz,
            direction=direction,
            strength=strength,
            regime_confidence=conf,
            direction_change=direction-pdir,
            strength_change=strength-pstr,
            volatility_change=vol-pv,
            macro=dict(self.spec.macro_features),
            metadata={"latent_regime": self._labels[t]},
        )

    def snapshot(self, t: int) -> WorldSnapshot:
        if t < 1 or t >= self.length:
            raise IndexError("snapshot step out of range")
        pkt = self._features(t)
        state_hash = sha256_id(self._prices[:t+1], self._volumes[:t+1], self._labels[:t+1], prefix="state_")
        return WorldSnapshot(
            world_id=self.world_id, seed=self.seed, step=t, packet=pkt,
            engine_state_hash=state_hash, difficulty=self.spec.difficulty,
            tags=(self._labels[t],),
        )

    def realized_return(self, t: int, horizon: int = 1) -> float:
        j = min(self.length, t+horizon)
        return math.log(self._prices[j]/self._prices[t])

    def iter_snapshots(self, start: int = 24, end: int | None = None) -> Iterable[WorldSnapshot]:
        end = min(end or self.length-1, self.length-1)
        for t in range(max(1,start), end+1):
            yield self.snapshot(t)

    def fork(self, at_step: int, new_seed: int, future_segments: tuple[RegimeSegment, ...]) -> "ForkedMarketWorld":
        return ForkedMarketWorld(self, at_step, new_seed, future_segments)

class ForkedMarketWorld(SyntheticMarketWorld):
    def __init__(self, parent: SyntheticMarketWorld, at_step: int, seed: int,
                 future_segments: tuple[RegimeSegment, ...]):
        self.parent_id = parent.world_id
        self.fork_step = at_step
        self.spec = WorldSpec(
            instrument=parent.spec.instrument,
            start_price=parent._prices[at_step],
            segments=future_segments,
            difficulty=parent.spec.difficulty,
            observation_window=parent.spec.observation_window,
            macro_features=parent.spec.macro_features,
        )
        self.seed = seed
        suffix_prices, suffix_volumes, suffix_labels = self._generate()
        self._prices = parent._prices[:at_step+1] + suffix_prices[1:]
        self._volumes = parent._volumes[:at_step+1] + suffix_volumes[1:]
        self._labels = parent._labels[:at_step+1] + suffix_labels[1:]
        self.world_id = sha256_id(parent.world_id, at_step, seed, self.spec.__dict__, prefix="fork_")
