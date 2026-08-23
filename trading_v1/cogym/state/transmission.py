from __future__ import annotations

from dataclasses import dataclass
import json

from ..agents.model import ChatModel, Message
from ..canonical import commitment
from .pathway import ContextPathway, PathwayStep


@dataclass(frozen=True)
class TransmissionPrediction:
    diagnosis: str
    expected_change: str
    confidence: float = 0.5


@dataclass(frozen=True)
class Transmission:
    name: str
    teacher_id: str
    pathway: ContextPathway
    prediction: TransmissionPrediction
    generation_context_digest: str = ""
    parent_transmission_id: str = ""

    @property
    def transmission_id(self) -> str:
        return commitment("COGYM:TRANSMISSION:v1", self)


def parse_master_transmission(raw: str, teacher_id: str, name: str = "master-transmission") -> Transmission:
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start < 0 or end <= start:
        raise ValueError("master did not return JSON")
    obj = json.loads(raw[start:end])
    steps = tuple(PathwayStep(str(s["id"]), str(s["prompt"]), tuple(map(str, s.get("tags", [])))) for s in obj["steps"])
    return Transmission(
        name=name,
        teacher_id=teacher_id,
        pathway=ContextPathway(name, steps, purpose="teacher-designed state induction"),
        prediction=TransmissionPrediction(str(obj.get("diagnosis", "")), str(obj.get("prediction", "")), float(obj.get("confidence", 0.5))),
    )


def request_transmission(model: ChatModel, teacher_history: list[Message], student_summary: str, *, seed: int = 0) -> tuple[Transmission, Message]:
    prompt = (
        "COGYM_MASTER:DESIGN_TRANSMISSION\n"
        "You are a persistent teacher in a trading cognition dojo. Diagnose the student's observable decision behavior, then design the shortest live interaction likely to improve it. "
        "Do not merely dump facts: each step should make the student generate an intermediate judgment that conditions the next step. "
        "Return JSON only: {diagnosis,prediction,confidence,steps:[{id,prompt,tags[]}]}.\n"
        f"STUDENT_SUMMARY={student_summary}"
    )
    msgs = [*teacher_history, Message("user", prompt)]
    raw = model.complete(msgs, temperature=0.2, seed=seed)
    return parse_master_transmission(raw, model.model_id), Message("assistant", raw)
