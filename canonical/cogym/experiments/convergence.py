from __future__ import annotations

from dataclasses import dataclass

from ..agents.model import ChatModel, Message
from ..canonical import commitment


@dataclass(frozen=True)
class RevisionRound:
    round_index: int
    master_output: str
    student_output: str
    revised_output: str


@dataclass(frozen=True)
class ConvergenceRun:
    task: str
    rounds: tuple[RevisionRound, ...]

    @property
    def run_id(self) -> str:
        return commitment("COGYM:CONVERGENCE:v1", self)


def teacher_reference_revision_loop(master: ChatModel, student: ChatModel, task: str, *, rounds: int = 3, seed: int = 0) -> ConvergenceRun:
    """Formalize the common manual workflow: same task -> compare master/student -> student diagnoses gap -> revise.

    This is not a Transmission by definition because the Master is primarily providing an exemplar/reference output rather than interactively diagnosing a student state. It is useful as a baseline and possible speedup.
    """
    student_history: list[Message] = []
    out: list[RevisionRound] = []
    current_task = task
    for i in range(rounds):
        master_raw = master.complete([Message("user", current_task)], temperature=0.2, seed=seed+i*10)
        student_raw = student.complete([*student_history, Message("user", current_task)], temperature=0.2, seed=seed+i*10+1)
        revise_prompt = (
            "Here is a reference answer from another instance. Compare it against your answer at the level of assumptions, evidence selection, structure and decision procedure. "
            "Explain internally what made your result differ, then produce a revised answer only.\n"
            f"REFERENCE={master_raw}\nYOUR_PREVIOUS={student_raw}\nTASK={current_task}"
        )
        revised = student.complete([*student_history, Message("user", revise_prompt)], temperature=0.2, seed=seed+i*10+2)
        student_history.extend([Message("user", revise_prompt), Message("assistant", revised)])
        out.append(RevisionRound(i, master_raw, student_raw, revised))
        current_task = task
    return ConvergenceRun(task, tuple(out))
