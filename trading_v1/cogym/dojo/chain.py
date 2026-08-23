from __future__ import annotations

from dataclasses import dataclass

from ..agents.model import ChatModel, Message
from ..state.pathway import ContextPathway, run_live_pathway
from ..state.transmission import Transmission, TransmissionPrediction


@dataclass(frozen=True)
class ChainHop:
    teacher_model_id: str
    student_model_id: str
    checkpoint_id: str
    next_transmission_id: str


def transmission_chain(models: list[ChatModel], initial: Transmission, *, seed: int = 0) -> tuple[ChainHop, ...]:
    """A -> B -> C transmission experiment.

    Each recipient undergoes the current transmission, then authors a successor transmission from its conditioned context.
    The function records the chain; evaluation against a Cogym benchmark is intentionally separate.
    """
    if len(models) < 2:
        return ()
    current = initial
    out: list[ChainHop] = []
    for i in range(len(models) - 1):
        teacher = models[i]
        student = models[i + 1]
        checkpoint = run_live_pathway(current.pathway, student, temperature=0.2, seed=seed + i * 100)
        prompt = (
            "You have just undergone a teaching pathway. Create a successor pathway that would transmit the most useful operational lesson to another fresh instance. "
            "Return exactly three numbered prompts, one per line."
        )
        raw = student.complete([*checkpoint.messages, Message("user", prompt)], temperature=0.2, seed=seed + i * 100 + 50)
        lines = [x.strip() for x in raw.splitlines() if x.strip()][:3]
        if not lines:
            lines = ["Reconstruct the key decision crux yourself.", "Attack it with a counterexample.", "State the revised operational rule."]
        from ..state.pathway import PathwayStep
        next_path = ContextPathway(
            f"chain-{i+1}",
            tuple(PathwayStep(f"c{j+1}", line) for j, line in enumerate(lines)),
            purpose="successor-authored transmission",
        )
        next_t = Transmission(f"chain-{i+1}", student.model_id, next_path, TransmissionPrediction("inherited", "preserve useful regime", 0.5), parent_transmission_id=current.transmission_id)
        out.append(ChainHop(teacher.model_id, student.model_id, checkpoint.checkpoint_id, next_t.transmission_id))
        current = next_t
    return tuple(out)
