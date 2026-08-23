from __future__ import annotations

from dataclasses import dataclass, field
import statistics

from ..agents.decision import Decision
from ..agents.model import ChatModel, Message
from ..agents.trader import decide
from ..canonical import commitment
from ..market.world import TradingWorld
from ..state.signature import BehaviorSignature, build_signature
from .scoring import DecisionScore, score_decision


@dataclass(frozen=True)
class DecisionRecord:
    index: int
    sample_seed: int
    decision: Decision
    realized_return: float
    score: DecisionScore


@dataclass(frozen=True)
class RunResult:
    model_id: str
    world_id: str
    condition: str
    horizon_steps: int
    records: tuple[DecisionRecord, ...]
    signature: BehaviorSignature
    history_mode: str
    metadata: dict = field(default_factory=dict)

    @property
    def run_id(self) -> str:
        return commitment("COGYM:RUN:v2", self)

    @property
    def mean_log_score(self) -> float:
        return statistics.mean(r.score.log_score for r in self.records) if self.records else 0.0

    @property
    def mean_paper_utility(self) -> float:
        return statistics.mean(r.score.paper_utility for r in self.records) if self.records else 0.0


@dataclass(frozen=True)
class RepeatSummary:
    condition: str
    run_ids: tuple[str, ...]
    mean_log_score: float
    sd_log_score: float
    mean_utility: float
    sd_utility: float
    mean_signature: BehaviorSignature


def run_world(
    model: ChatModel,
    world: TradingWorld,
    *,
    condition: str,
    history: list[Message] | None = None,
    indices: list[int] | None = None,
    horizon_steps: int = 5,
    temperature: float = 0.2,
    sample_seed: int = 0,
    history_mode: str = "reset",
    reveal_outcomes: bool = False,
) -> RunResult:
    if history_mode not in {"reset", "persistent"}:
        raise ValueError("history_mode must be reset or persistent")
    if indices is None:
        indices = list(range(30, len(world.bars) - horizon_steps, 10))
    persistent = list(history or [])
    records: list[DecisionRecord] = []
    decisions: list[Decision] = []
    for n, idx in enumerate(indices):
        current_history = persistent if history_mode == "persistent" else list(history or [])
        packet = world.snapshot(idx)
        seed = sample_seed + n * 1009
        decision, reply = decide(model, current_history, packet, horizon_steps=horizon_steps, temperature=temperature, seed=seed)
        realized = world.realized_return(idx, horizon_steps)
        score = score_decision(decision, realized)
        decisions.append(decision)
        records.append(DecisionRecord(idx, seed, decision, realized, score))
        if history_mode == "persistent":
            from ..agents.trader import market_query
            persistent.append(Message("user", market_query(packet, horizon_steps)))
            persistent.append(reply)
            if reveal_outcomes:
                persistent.append(Message("user", f"PAPER_OUTCOME: realized_return={realized:.8f}. Update only if this evidence warrants it."))
    return RunResult(model.model_id, world.manifest.world_id, condition, horizon_steps, tuple(records), build_signature(decisions), history_mode, {"sample_seed": sample_seed, "reveal_outcomes": reveal_outcomes})


def summarize_repeats(runs: list[RunResult], condition: str) -> RepeatSummary:
    if not runs:
        raise ValueError("runs required")
    logs = [r.mean_log_score for r in runs]
    utils = [r.mean_paper_utility for r in runs]
    # Signature of all decisions is more stable than averaging signature coordinates by hand.
    all_decisions = [rec.decision for run in runs for rec in run.records]
    return RepeatSummary(
        condition,
        tuple(r.run_id for r in runs),
        statistics.mean(logs), statistics.pstdev(logs) if len(logs) > 1 else 0.0,
        statistics.mean(utils), statistics.pstdev(utils) if len(utils) > 1 else 0.0,
        build_signature(all_decisions),
    )
