from __future__ import annotations

from dataclasses import replace

from .pathway import ContextPathway


def ablation_candidates(pathway: ContextPathway) -> list[tuple[str, ContextPathway]]:
    """Generate one-step ablations. Selection must be based on actual hidden-probe results."""
    out = []
    for step in pathway.steps:
        candidate = replace(pathway, name=f"{pathway.name}-minus-{step.id}", steps=tuple(s for s in pathway.steps if s.id != step.id))
        out.append((step.id, candidate))
    return out
