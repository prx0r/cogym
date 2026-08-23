from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Literal
from .utils import sha256_id

Action = Literal["LONG", "FLAT", "SHORT"]

@dataclass(frozen=True)
class WorldPacket:
    timestamp: int
    instrument: str
    price: float
    returns: tuple[float, ...]
    volatility: float
    volume_z: float
    direction: float
    strength: float
    regime_confidence: float
    direction_change: float = 0.0
    strength_change: float = 0.0
    volatility_change: float = 0.0
    macro: dict[str, float] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def packet_hash(self) -> str:
        return sha256_id(asdict(self), prefix="pkt_")

@dataclass(frozen=True)
class WorldSnapshot:
    world_id: str
    seed: int
    step: int
    packet: WorldPacket
    engine_state_hash: str
    difficulty: float
    tags: tuple[str, ...] = ()

    @property
    def snapshot_id(self) -> str:
        return sha256_id(self.world_id, self.seed, self.step, self.packet.packet_hash,
                         self.engine_state_hash, prefix="snap_")

@dataclass(frozen=True)
class AgentGenome:
    model: str = "rulebased-v1"
    reasoning_policy: str = "falsification_first"
    representation: str = "plain"
    induction: str = "neutral"
    memory_policy: str = "none"
    memory_depth: int = 0
    social_topology: str = "independent"
    reveal: str = "none"
    revision_rounds: int = 0
    plasticity: float = 0.1
    temperature: float = 0.0
    system_variant: str = "default"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def genome_id(self) -> str:
        return sha256_id(asdict(self), prefix="gen_")

@dataclass
class Decision:
    agent_id: str
    snapshot_id: str
    action: Action
    expected_return: float
    confidence: float
    rationale: str
    evidence: list[str] = field(default_factory=list)
    private_action: Action | None = None
    revised: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class RunRecord:
    run_id: str
    world_id: str
    seed: int
    agent_id: str
    genome_id: str
    step: int
    snapshot_id: str
    decision: Decision
    realized_return: float
    reward: float
    regret: float
    context_hash: str
    parent_run_id: str | None = None
    fork_reason: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class BenchmarkResult:
    benchmark_id: str
    genome_id: str
    episodes: int
    mean_reward: float
    downside_reward: float
    calibration_error: float
    max_drawdown: float
    adaptation_latency: float
    revision_gain: float = 0.0
    novelty: float = 0.0
    cost_units: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class CognitivePack:
    name: str
    version: str
    genome: AgentGenome
    context_modules: tuple[str, ...]
    memory_seeds: tuple[dict[str, Any], ...] = ()
    behavioral_contract: dict[str, Any] = field(default_factory=dict)
    benchmark_results: tuple[BenchmarkResult, ...] = ()
    provenance: dict[str, Any] = field(default_factory=dict)
    proof_manifest: dict[str, Any] = field(default_factory=dict)

    @property
    def pack_id(self) -> str:
        body = {
            "name": self.name,
            "version": self.version,
            "genome": asdict(self.genome),
            "context_modules": self.context_modules,
            "memory_seeds": self.memory_seeds,
            "behavioral_contract": self.behavioral_contract,
            "provenance": self.provenance,
            "proof_manifest": self.proof_manifest,
        }
        return sha256_id(body, prefix="pack_")
