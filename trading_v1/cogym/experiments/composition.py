from __future__ import annotations

from ..state.pathway import ContextPathway, PathwayStep


def compose(a: ContextPathway, b: ContextPathway, *, mode: str = "a_then_b") -> ContextPathway:
    if mode == "a_then_b":
        steps = (*a.steps, *b.steps)
    elif mode == "b_then_a":
        steps = (*b.steps, *a.steps)
    elif mode == "interleave":
        steps_list = []
        n = max(len(a.steps), len(b.steps))
        for i in range(n):
            if i < len(a.steps): steps_list.append(a.steps[i])
            if i < len(b.steps): steps_list.append(b.steps[i])
        steps = tuple(steps_list)
    else:
        raise ValueError("invalid composition mode")
    normalized = tuple(PathwayStep(f"{i+1}:{s.id}", s.prompt, s.tags) for i, s in enumerate(steps))
    return ContextPathway(f"{a.name}+{b.name}:{mode}", normalized, system=a.system or b.system, purpose=f"composition experiment {mode}")
