from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ..canonical import sha256_file


@dataclass(frozen=True)
class ExternalProofArtifact:
    prover: str
    proof_path: str
    proof_sha256: str
    metadata_path: str = ""


def register_external_proof(path: str | Path, *, prover: str = "DeepProve", metadata_path: str = "") -> ExternalProofArtifact:
    p = Path(path)
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(p)
    return ExternalProofArtifact(prover, str(p), sha256_file(p), metadata_path)


def verify_with_command(proof: ExternalProofArtifact, command: list[str], *, timeout: int = 600) -> bool:
    """Invoke a real external verifier. No fake zkML proof generation exists in Cogym."""
    if not command:
        raise ValueError("verifier command required")
    env = {"COGYM_PROOF_PATH": proof.proof_path, "COGYM_PROOF_SHA256": proof.proof_sha256}
    import os
    proc = subprocess.run(command, timeout=timeout, capture_output=True, text=True, env={**os.environ, **env})
    return proc.returncode == 0
