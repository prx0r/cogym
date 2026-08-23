from __future__ import annotations

from dataclasses import dataclass

from ..agents.model import ChatModel
from ..market.world import TradingWorld
from ..state.pathway import ContextPathway, run_live_pathway
from .runner import RepeatSummary, run_world, summarize_repeats


@dataclass(frozen=True)
class PersistenceMatrix:
    reset: RepeatSummary
    persistent: RepeatSummary
    persistent_with_outcomes: RepeatSummary


def run_persistence_matrix(model: ChatModel, world: TradingWorld, pathway: ContextPathway | None = None, *, repeats: int = 3, indices: list[int] | None = None) -> PersistenceMatrix:
    buckets = {"reset": [], "persistent": [], "outcomes": []}
    for r in range(repeats):
        seed = 1000 + r * 10000
        history = list(run_live_pathway(pathway, model, temperature=0.2, seed=seed).messages) if pathway else []
        buckets["reset"].append(run_world(model, world, condition="reset", history=history, indices=indices, temperature=0.2, sample_seed=seed+100, history_mode="reset"))
        buckets["persistent"].append(run_world(model, world, condition="persistent", history=history, indices=indices, temperature=0.2, sample_seed=seed+200, history_mode="persistent"))
        buckets["outcomes"].append(run_world(model, world, condition="persistent_outcomes", history=history, indices=indices, temperature=0.2, sample_seed=seed+300, history_mode="persistent", reveal_outcomes=True))
    return PersistenceMatrix(
        summarize_repeats(buckets["reset"], "reset"),
        summarize_repeats(buckets["persistent"], "persistent"),
        summarize_repeats(buckets["outcomes"], "persistent_outcomes"),
    )
