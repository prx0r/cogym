"""Episode: canonical record of one subject-in-world interaction.
WorldSpec + AgentSpec + prior state + decisions + outcome. Immutable."""
from __future__ import annotations
from dataclasses import asdict, dataclass, field
from typing import Any
from ..utils import sha256_id

@dataclass(frozen=True)
class Decision:
    step: int
    action: str
    confidence: float
    expected_return: float
    revised: bool = False
    raw_output_hash: str | None = None   # commitment to exact raw output

@dataclass(frozen=True)
class Episode:
    episode_id: str
    world_name: str
    world_seed: int
    agent_spec_id: str
    treatment: str | None            # STX A-G / P0-P3 / dose level etc.
    decisions: tuple[Decision, ...]
    metrics: dict[str, float]
    started_at: float
    finished_at: float

    def record(self) -> dict:
        d = asdict(self)
        d["record_hash"] = sha256_id(d, prefix="ep_")
        return d
