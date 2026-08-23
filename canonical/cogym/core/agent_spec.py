"""AgentSpec: typed, reproducible organism definition (v0.2 of AgentGenome).

Frozen dataclass + content-hash id. Extends genome with tools/skills/context
modules while staying inside typed fields so evolution remains reproducible.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass, field, replace
from typing import Any
import hashlib, json as _json
def _sha256_id(obj, prefix=""):
    payload = _json.dumps(obj, sort_keys=True, default=str).encode()
    return prefix + hashlib.sha256(payload).hexdigest()

def sha256_id(obj, prefix=""):
    return _sha256_id(obj, prefix)

@dataclass(frozen=True)
class AgentSpec:
    # model plane
    model: str = "rulebased-v1"
    temperature: float = 0.0
    system_variant: str = "default"

    # cognition plane (inherited from AgentGenome spaces)
    reasoning_policy: str = "falsification_first"
    representation: str = "plain"
    induction: str = "neutral"

    # memory plane
    memory_policy: str = "none"
    memory_depth: int = 0

    # social plane
    social_topology: str = "independent"
    reveal: str = "none"
    revision_rounds: int = 0
    plasticity: float = 0.1

    # open planes (typed containers; content evolves via Pack/modules)
    context_modules: tuple[str, ...] = ()      # names of attached markdown modules
    skills: tuple[str, ...] = ()               # skill registry ids
    tools_policy: str = "standard"             # discovery policy id

    def spec_id(self) -> str:
        return sha256_id(asdict(self), prefix="spec_")

    def with_changes(self, **kw) -> "AgentSpec":
        return replace(self, **kw)

    @classmethod
    def from_genome(cls, g) -> "AgentSpec":
        d = asdict(g)
        allowed = {k: v for k, v in d.items() if k in cls.__dataclass_fields__}
        return cls(**allowed)
