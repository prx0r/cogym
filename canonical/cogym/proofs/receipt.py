from __future__ import annotations

from dataclasses import dataclass

from ..canonical import commitment


@dataclass(frozen=True)
class ModelExecutionClaim:
    model_id: str
    input_digest: str
    output_digest: str
    provider: str = ""
    attestation_ref: str = ""


@dataclass(frozen=True)
class ExperimentReceipt:
    challenge_digest: str
    world_id: str
    condition_id: str
    pack_or_pathway_id: str
    execution_claims: tuple[ModelExecutionClaim, ...]
    result_digest: str
    evaluator_version: str

    @property
    def receipt_id(self) -> str:
        return commitment("COGYM:RECEIPT:v1", self)
