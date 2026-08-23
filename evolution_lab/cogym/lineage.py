from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any
from .schema import AgentGenome
from .utils import sha256_id

@dataclass(frozen=True)
class LineageNode:
    lineage_id: str
    genome: AgentGenome
    parent_id: str | None
    generation: int
    mutation_note: str = ""
    inherited_memory_policy: str = "none"
    metadata: dict[str, Any] | None = None

    @staticmethod
    def root(genome: AgentGenome, name: str = "root") -> "LineageNode":
        lid=sha256_id(name,genome.genome_id,prefix="lin_")
        return LineageNode(lid,genome,None,0)

    def child(self, genome: AgentGenome, mutation_note: str = "") -> "LineageNode":
        lid=sha256_id(self.lineage_id,genome.genome_id,self.generation+1,mutation_note,prefix="lin_")
        return LineageNode(lid,genome,self.lineage_id,self.generation+1,mutation_note,genome.memory_policy)
