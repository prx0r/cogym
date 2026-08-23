from __future__ import annotations

from dataclasses import dataclass
import secrets

from ..canonical import commitment


@dataclass(frozen=True)
class ChallengeSpec:
    challenge_id: str
    world_constructor_id: str
    rules_version: str
    public_parameters: dict

    @property
    def digest(self) -> str:
        return commitment("COGYM:CHALLENGE:v1", self)


def participant_commit(agent_id: str, artifact_digest: str, nonce: str) -> str:
    return commitment("COGYM:PARTICIPANT_COMMIT:v1", agent_id, artifact_digest, nonce)


@dataclass(frozen=True)
class CommitRevealRound:
    challenge: ChallengeSpec
    server_nonce_commitment: str
    participant_commits: tuple[str, ...]

    @classmethod
    def create(cls, challenge: ChallengeSpec, participant_commits: tuple[str, ...], server_nonce: str) -> "CommitRevealRound":
        return cls(challenge, commitment("COGYM:SERVER_NONCE:v1", server_nonce), participant_commits)

    def derive_seed(self, server_nonce: str) -> int:
        if commitment("COGYM:SERVER_NONCE:v1", server_nonce) != self.server_nonce_commitment:
            raise ValueError("server nonce does not match commitment")
        hex_digest = commitment("COGYM:SEED:v1", self.challenge.digest, server_nonce, self.participant_commits)
        return int(hex_digest[:16], 16)


def fresh_nonce() -> str:
    return secrets.token_hex(32)
