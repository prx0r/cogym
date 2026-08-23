from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from ..agents.model import ChatModel, Message
from ..canonical import commitment


@dataclass(frozen=True)
class PathwayStep:
    id: str
    prompt: str
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class ContextPathway:
    name: str
    steps: tuple[PathwayStep, ...]
    system: str = ""
    purpose: str = ""

    @property
    def pathway_id(self) -> str:
        return commitment("COGYM:PATHWAY:v2", self)


@dataclass(frozen=True)
class ContextCheckpoint:
    model_id: str
    messages: tuple[Message, ...]
    source_pathway_id: str
    run_seed: int | None
    metadata: dict = field(default_factory=dict)

    @property
    def checkpoint_id(self) -> str:
        return commitment("COGYM:CHECKPOINT:v2", self)


def run_live_pathway(
    pathway: ContextPathway,
    model: ChatModel,
    *,
    temperature: float = 0.0,
    seed: int | None = None,
    initial: Iterable[Message] = (),
) -> ContextCheckpoint:
    messages = list(initial)
    if pathway.system and not any(m.role == "system" for m in messages):
        messages.append(Message("system", pathway.system))
    for i, step in enumerate(pathway.steps):
        messages.append(Message("user", step.prompt))
        reply = model.complete(messages, temperature=temperature, seed=None if seed is None else seed + i)
        messages.append(Message("assistant", reply))
    return ContextCheckpoint(model.model_id, tuple(messages), pathway.pathway_id, seed, {"temperature": temperature})


def replay_messages(checkpoint: ContextCheckpoint) -> list[Message]:
    return list(checkpoint.messages)
