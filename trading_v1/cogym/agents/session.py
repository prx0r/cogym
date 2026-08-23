from __future__ import annotations

from dataclasses import dataclass, field

from .model import ChatModel, Message


@dataclass
class AgentSession:
    model: ChatModel
    messages: list[Message] = field(default_factory=list)
    temperature: float = 0.0
    next_seed: int = 0

    def ask(self, prompt: str, *, seed: int | None = None) -> str:
        self.messages.append(Message("user", prompt))
        use_seed = self.next_seed if seed is None else seed
        raw = self.model.complete(self.messages, temperature=self.temperature, seed=use_seed)
        self.messages.append(Message("assistant", raw))
        self.next_seed = use_seed + 1
        return raw

    def clone_fresh(self) -> "AgentSession":
        return AgentSession(self.model, [], self.temperature, self.next_seed)
