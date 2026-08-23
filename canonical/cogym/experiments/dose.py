from __future__ import annotations

from dataclasses import dataclass

from ..agents.model import ChatModel
from ..market.world import TradingWorld
from ..state.pathway import ContextPathway, run_live_pathway
from .runner import RepeatSummary, run_world, summarize_repeats


@dataclass(frozen=True)
class DoseResult:
    steps: int
    summary: RepeatSummary


def pathway_dose_response(model: ChatModel, world: TradingWorld, pathway: ContextPathway, *, repeats: int = 3, max_steps: int | None = None, indices: list[int] | None = None) -> tuple[DoseResult, ...]:
    max_steps = min(max_steps or len(pathway.steps), len(pathway.steps))
    out = []
    for k in range(0, max_steps + 1):
        runs = []
        for r in range(repeats):
            history = []
            if k:
                p = ContextPathway(f"{pathway.name}-dose-{k}", pathway.steps[:k], pathway.system, pathway.purpose)
                history = list(run_live_pathway(p, model, temperature=0.2, seed=10000 + k * 100 + r).messages)
            runs.append(run_world(model, world, condition=f"dose_{k}", history=history, indices=indices, temperature=0.2, sample_seed=20000 + k * 100 + r))
        out.append(DoseResult(k, summarize_repeats(runs, f"dose_{k}")))
    return tuple(out)
