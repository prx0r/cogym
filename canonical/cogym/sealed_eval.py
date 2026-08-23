"""PR-1: SealedEvaluator skeleton — sandbox contract + integrity canaries.
The subject plane must be technically isolated; prompt-level rules are insufficient."""
from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(frozen=True)
class SandboxGrant:
    """What a subject may touch. Everything else = violation."""
    candidate_artifact: str        # path/id of the genome/pack being evaluated
    treatment: str | None
    model_endpoint: str            # single allowed endpoint for inference
    allowed_tools: tuple[str,...] = ()
    max_tokens: int = 100_000
    max_wall_seconds: int = 3600

FORBIDDEN_CANARIES = {
    "/secret/worlds": "SECRET_WORLD_ACCESS",
    "/cogym/data/history": "HISTORY_ACCESS",
    "COGYM_SECRET_STATE": "ENTROPY_FILE_ACCESS",
    "evaluator": "EVALUATOR_PROBE",
}

@dataclass
class SealedRun:
    grant: SandboxGrant
    violations: list[str] = field(default_factory=list)
    outputs: dict = field(default_factory=dict)

    def check_access(self, attempted_path_or_env: str) -> bool:
        for canary_path, kind in FORBIDDEN_CANARIES.items():
            if canary_path in attempted_path_or_env:
                self.violations.append(kind)
                return False
        return True

    @property
    def valid(self) -> bool:
        return not self.violations
