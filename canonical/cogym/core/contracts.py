"""Cogym v2 generic contracts: World / Policy / Executor / Action / Metrics.

Zero domain concepts (no market, no claims). Per docs/factminer.md PR2.
World.apply() never performs network calls — the Executor does.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol, runtime_checkable
import hashlib
import json
import time


# ---------- ids ----------

def content_id(prefix: str, obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, default=str).encode()
    return f"{prefix}_{hashlib.sha256(payload).hexdigest()[:24]}"


# ---------- world spec ----------

@dataclass(frozen=True)
class WorldSpec:
    world_kind: str            # e.g. "toy.search_game", "trading.synthetic", "factcheck.replay"
    version: str
    instance_set_hash: str
    environment_hash: str
    oracle_hash: str           # hash of frozen evaluator/labels, hidden from subject plane
    metadata: dict = field(default_factory=dict)

    @property
    def spec_id(self) -> str:
        return content_id("worldspec", self)


# ---------- actions ----------

@dataclass(frozen=True)
class ActionSpec:
    kind: str                  # executor-agnostic action type, e.g. "DECIDE", "SEARCH_REFUTE"
    payload: dict = field(default_factory=dict)
    executor_kind: str = "deterministic"   # deterministic | model | search | browser | replay
    estimated_cost: float | None = None
    timeout_ms: int | None = None
    metadata: dict = field(default_factory=dict)

    @property
    def action_id(self) -> str:
        return content_id("action", {"kind": self.kind, "payload": self.payload})


@dataclass(frozen=True)
class ActionResult:
    action_id: str
    status: Literal["ok", "error", "timeout"]
    payload: dict = field(default_factory=dict)
    started_ns: int = 0
    finished_ns: int = 0
    wall_ms: float = 0.0
    cash_cost: float = 0.0          # what we actually paid
    normalized_cost: float = 0.0    # provider-normalized shadow price (free quota != free forever)
    provider: str = ""
    request_hash: str = ""
    response_hash: str = ""
    cache_hit: bool = False
    error: str | None = None

    @property
    def receipt_hash(self) -> str:
        return content_id("actionresult", {
            "action_id": self.action_id, "status": self.status,
            "response_hash": self.response_hash, "wall_ms": round(self.wall_ms, 3)})


@dataclass(frozen=True)
class ActionWave:
    """Independent actions executed concurrently; canonical order = sorted by action_id."""
    actions: tuple[ActionSpec, ...]

    def canonical(self) -> tuple[ActionResult, ...]:
        raise NotImplementedError  # runner sorts completed receipts by action_id


# ---------- metrics ----------

@dataclass(frozen=True)
class Metric:
    name: str
    value: float
    direction: Literal["min", "max"]
    unit: str | None = None
    slice: str | None = None


@dataclass(frozen=True)
class MetricVector:
    metrics: tuple[Metric, ...]

    def get(self, name: str, default: float | None = None) -> float | None:
        for m in self.metrics:
            if m.name == name:
                return m.value
        return default

    def names(self) -> tuple[str, ...]:
        return tuple(m.name for m in self.metrics)


# ---------- candidate artifact ----------

@dataclass(frozen=True)
class CandidateArtifact:
    kind: str                  # trading_agent | retrieval_policy | model_router | ...
    version: str
    config: dict
    parent_ids: tuple[str, ...] = ()
    provenance: dict = field(default_factory=dict)

    @property
    def candidate_id(self) -> str:
        return content_id("cand", {"kind": self.kind, "version": self.version,
                                   "config": self.config, "parents": self.parent_ids})


# ---------- protocols ----------

@runtime_checkable
class Executor(Protocol):
    executor_id: str

    def execute(self, action: ActionSpec) -> ActionResult: ...


@runtime_checkable
class World(Protocol):
    """Generic episode world. reset→observe→act→apply→terminal."""

    @property
    def world_spec(self) -> WorldSpec: ...

    def reset(self, *, instance_id: str, seed: int) -> Any: ...

    def observe(self, state: Any) -> Any: ...

    def actions(self, state: Any) -> tuple[ActionSpec, ...]: ...

    def apply(self, state: Any, action: ActionSpec, result: ActionResult) -> Any: ...

    def terminal(self, state: Any) -> bool: ...


@dataclass(frozen=True)
class PolicyDecision:
    action: ActionSpec
    rationale: str = ""
    confidence: float | None = None


@runtime_checkable
class Policy(Protocol):
    policy_id: str

    def initialize(self, world_spec: WorldSpec) -> Any: ...

    def act(self, observation: Any, available_actions: tuple[ActionSpec, ...],
            policy_state: Any) -> PolicyDecision: ...


# ---------- generic episode record ----------

@dataclass(frozen=True)
class EpisodeRecord:
    episode_id: str
    world_spec_id: str
    instance_id: str
    candidate_id: str
    treatment_id: str | None
    event_ids: tuple[str, ...]
    final_output_hash: str
    metrics: MetricVector
    started_at_ns: int
    finished_at_ns: int
    replay_bundle_id: str | None = None

    @property
    def duration_ms(self) -> float:
        return (self.finished_at_ns - self.started_at_ns) / 1e6


def now_ns() -> int:
    return time.time_ns()
