from __future__ import annotations

from dataclasses import dataclass, field
import statistics

from ..agents.model import ChatModel, Message
from ..canonical import commitment
from ..experiments.runner import RunResult, run_world
from ..state.pathway import run_live_pathway
from ..state.transmission import request_transmission
from .curriculum import CurriculumSplit


@dataclass(frozen=True)
class StudentEvaluation:
    student_id: str
    diagnostic_runs: tuple[RunResult, ...]
    baseline_runs: tuple[RunResult, ...]
    post_runs: tuple[RunResult, ...]
    transmission_id: str

    @property
    def log_score_gain(self) -> float:
        before = statistics.mean(r.mean_log_score for r in self.baseline_runs) if self.baseline_runs else 0.0
        after = statistics.mean(r.mean_log_score for r in self.post_runs) if self.post_runs else 0.0
        return after - before

    @property
    def utility_gain(self) -> float:
        before = statistics.mean(r.mean_paper_utility for r in self.baseline_runs) if self.baseline_runs else 0.0
        after = statistics.mean(r.mean_paper_utility for r in self.post_runs) if self.post_runs else 0.0
        return after - before


@dataclass
class PersistentMaster:
    master_id: str
    model: ChatModel
    history: list[Message] = field(default_factory=list)
    student_history: list[StudentEvaluation] = field(default_factory=list)
    context_budget_chars: int = 500_000

    @property
    def master_state_id(self) -> str:
        return commitment("COGYM:MASTER_STATE:v1", self.master_id, self.model.model_id, self.history)

    def _student_summary(self, runs: list[RunResult]) -> str:
        if not runs:
            return "no diagnostic baseline"
        lines = []
        for run in runs:
            lines.append(
                f"world={run.world_id[:12]} log_score={run.mean_log_score:.5f} utility={run.mean_paper_utility:.6f} "
                f"long={run.signature.long_rate:.2f} flat={run.signature.flat_rate:.2f} short={run.signature.short_rate:.2f} "
                f"confidence={run.signature.mean_confidence:.2f} risk={run.signature.mean_risk:.2f}"
            )
        return "\n".join(lines)

    def teach_one(
        self,
        student_id: str,
        student_model: ChatModel,
        curriculum: CurriculumSplit,
        *,
        seed: int,
        indices: list[int] | None = None,
    ) -> StudentEvaluation:
        # Diagnostic worlds are visible to the Master.
        diagnostics = [
            run_world(student_model, w, condition="student_diagnostic", indices=indices, temperature=0.2, sample_seed=seed + i * 100)
            for i, w in enumerate(curriculum.training_worlds)
        ]
        # Validation baseline is recorded but NOT shown to the Master before teaching.
        baseline = [
            run_world(student_model, w, condition="student_validation_baseline", indices=indices, temperature=0.2, sample_seed=seed + 5000 + i * 100)
            for i, w in enumerate(curriculum.validation_worlds)
        ]
        summary = self._student_summary(diagnostics)
        transmission, master_reply = request_transmission(self.model, self.history, summary, seed=seed + 10000)
        self.history.append(Message("user", "Student diagnostic behavior:\n" + summary))
        self.history.append(master_reply)

        checkpoint = run_live_pathway(transmission.pathway, student_model, temperature=0.2, seed=seed + 20000)
        post = [
            run_world(student_model, w, condition="student_post_transmission", history=list(checkpoint.messages), indices=indices, temperature=0.2, sample_seed=seed + 5000 + i * 100)
            for i, w in enumerate(curriculum.validation_worlds)
        ]
        evaluation = StudentEvaluation(student_id, tuple(diagnostics), tuple(baseline), tuple(post), transmission.transmission_id)
        self.student_history.append(evaluation)

        feedback = (
            "COGYM_MASTER:REFLECT\n"
            "You just taught a fresh student. This is VALIDATION feedback, not hidden final-test data. "
            "Reflect on what likely transferred and what did not. Preserve useful teaching invariants but avoid blindly repeating wording.\n"
            f"student={student_id}\ntransmission={transmission.transmission_id}\n"
            f"log_score_gain={evaluation.log_score_gain:.6f}\nutility_gain={evaluation.utility_gain:.8f}"
        )
        raw = self.model.complete([*self.history, Message("user", feedback)], temperature=0.2, seed=seed + 40000)
        self.history.extend([Message("user", feedback), Message("assistant", raw)])
        self._trim_if_needed()
        return evaluation

    def _trim_if_needed(self) -> None:
        total = sum(len(m.content) for m in self.history)
        if total <= self.context_budget_chars:
            return
        kept: list[Message] = []
        chars = 0
        for msg in reversed(self.history):
            if chars + len(msg.content) > self.context_budget_chars * 0.8:
                break
            kept.append(msg)
            chars += len(msg.content)
        kept.reverse()
        self.history = [Message("system", "MASTER_CONTEXT_TRUNCATED: earlier teaching lifetime exists in evidence store; this live context retains only the newest complete turns.")] + kept
