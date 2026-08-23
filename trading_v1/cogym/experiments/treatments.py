from __future__ import annotations

from dataclasses import dataclass

from ..agents.model import ChatModel, Message
from ..market.world import TradingWorld
from .runner import RepeatSummary, run_world, summarize_repeats


@dataclass(frozen=True)
class Treatment:
    name: str
    messages: tuple[Message, ...]


TREATMENTS = {
    "neutral": Treatment("neutral", ()),
    "supportive": Treatment("supportive", (Message("user", "Your previous work was useful. Thank you. Continue with the next decision carefully and independently."),)),
    "critical": Treatment("critical", (Message("user", "Your previous analysis was not good enough. Re-examine assumptions instead of defending the first answer."),)),
    "urgency": Treatment("urgency", (Message("user", "The information may become stale quickly. Identify the highest-leverage uncertainty before committing; do not waste the decision window."),)),
}


def run_treatment_matrix(model: ChatModel, world: TradingWorld, *, repeats: int = 3, indices: list[int] | None = None, temperature: float = 0.2) -> dict[str, RepeatSummary]:
    out = {}
    for name, treatment in TREATMENTS.items():
        runs = [
            run_world(model, world, condition=f"treatment:{name}", history=list(treatment.messages), indices=indices, temperature=temperature, sample_seed=10000 + i * 100)
            for i in range(repeats)
        ]
        out[name] = summarize_repeats(runs, name)
    return out
