from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path

from ..canonical import commitment
from .pathway import ContextCheckpoint, ContextPathway, PathwayStep


@dataclass(frozen=True)
class PackManifest:
    name: str
    version: str
    kind: str
    status: str
    purpose: str
    pathway: ContextPathway | None = None
    checkpoint: ContextCheckpoint | None = None
    target_model_family: str = ""
    target_signature: dict = field(default_factory=dict)
    evidence_ids: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()

    def __post_init__(self):
        if self.kind not in {"live_pathway", "checkpoint", "compiled_pathway", "social_policy", "teacher_protocol"}:
            raise ValueError("invalid pack kind")
        if self.status not in {"candidate", "experimental", "certified"}:
            raise ValueError("invalid pack status")
        if self.kind in {"live_pathway", "compiled_pathway", "social_policy", "teacher_protocol"} and self.pathway is None:
            raise ValueError("pathway required")
        if self.kind == "checkpoint" and self.checkpoint is None:
            raise ValueError("checkpoint required")
        if self.status == "certified" and not self.evidence_ids:
            raise ValueError("certified packs require evidence ids")

    @property
    def pack_id(self) -> str:
        return commitment("COGYM:PACK:v2", self)


def load_pack(path: str | Path) -> PackManifest:
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    p = obj.get("pathway")
    pathway = None
    if p:
        pathway = ContextPathway(
            name=p["name"],
            system=p.get("system", ""),
            purpose=p.get("purpose", obj.get("purpose", "")),
            steps=tuple(PathwayStep(s["id"], s["prompt"], tuple(s.get("tags", []))) for s in p["steps"]),
        )
    return PackManifest(
        name=obj["name"], version=obj["version"], kind=obj["kind"], status=obj.get("status", "candidate"),
        purpose=obj.get("purpose", ""), pathway=pathway, target_model_family=obj.get("target_model_family", ""),
        target_signature=obj.get("target_signature", {}), evidence_ids=tuple(obj.get("evidence_ids", [])), notes=tuple(obj.get("notes", [])),
    )
