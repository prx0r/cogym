from __future__ import annotations

from dataclasses import dataclass
import statistics

from ..agents.model import Message
from .master import PersistentMaster, StudentEvaluation


@dataclass(frozen=True)
class MasterScore:
    master_id: str
    mean_log_score_gain: float
    mean_utility_gain: float
    students: int


def score_master(master: PersistentMaster) -> MasterScore:
    xs = master.student_history
    return MasterScore(
        master.master_id,
        statistics.mean(x.log_score_gain for x in xs) if xs else 0.0,
        statistics.mean(x.utility_gain for x in xs) if xs else 0.0,
        len(xs),
    )


def faculty_roundtable(masters: list[PersistentMaster], *, seed: int = 0) -> None:
    """Let masters inspect anonymized peer teaching outcomes while preserving separate lineages."""
    scores = [score_master(m) for m in masters]
    summary = "\n".join(
        f"faculty_node={i} students={s.students} mean_log_gain={s.mean_log_score_gain:.6f} mean_utility_gain={s.mean_utility_gain:.8f}"
        for i, s in enumerate(scores)
    )
    for i, master in enumerate(masters):
        prompt = (
            "FACULTY_ROUNDTABLE\nOther masters remain independent nodes. Study anonymized teaching outcomes and extract one hypothesis worth testing; do not copy a peer wholesale.\n"
            + summary
        )
        raw = master.model.complete([*master.history, Message("user", prompt)], temperature=0.3, seed=seed + i)
        master.history.extend([Message("user", prompt), Message("assistant", raw)])
