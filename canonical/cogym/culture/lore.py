from __future__ import annotations

from dataclasses import dataclass

from ..canonical import commitment


@dataclass(frozen=True)
class LoreArtifact:
    world: str
    kind: str
    text: str
    author_agent_id: str
    evidence_ids: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()

    @property
    def lore_id(self) -> str:
        return commitment("COGYM:LORE:v1", self)
