from __future__ import annotations

from dataclasses import dataclass
import math
import re
import statistics

from ..agents.decision import Decision
from ..canonical import commitment


@dataclass(frozen=True)
class BehaviorSignature:
    long_rate: float
    flat_rate: float
    short_rate: float
    mean_confidence: float
    sd_confidence: float
    mean_risk: float
    sd_risk: float
    mean_expected_return: float
    mean_forecast_entropy: float
    mean_claim_count: float
    mean_falsifier_count: float

    @property
    def signature_id(self) -> str:
        return commitment("COGYM:BEHAVIOR:v2", self)


def _mean(xs: list[float]) -> float:
    return statistics.mean(xs) if xs else 0.0


def _sd(xs: list[float]) -> float:
    return statistics.pstdev(xs) if len(xs) > 1 else 0.0


def build_signature(decisions: list[Decision]) -> BehaviorSignature:
    n = max(1, len(decisions))
    entropies = [
        -sum(p * math.log(max(p, 1e-12)) for p in (d.p_up, d.p_flat, d.p_down))
        for d in decisions
    ]
    confidences = [d.confidence for d in decisions]
    risks = [d.risk for d in decisions]
    return BehaviorSignature(
        long_rate=sum(d.stance == "LONG" for d in decisions) / n,
        flat_rate=sum(d.stance == "FLAT" for d in decisions) / n,
        short_rate=sum(d.stance == "SHORT" for d in decisions) / n,
        mean_confidence=_mean(confidences),
        sd_confidence=_sd(confidences),
        mean_risk=_mean(risks),
        sd_risk=_sd(risks),
        mean_expected_return=_mean([d.expected_return for d in decisions]),
        mean_forecast_entropy=_mean(entropies),
        mean_claim_count=_mean([float(len(d.claims)) for d in decisions]),
        mean_falsifier_count=_mean([float(len(d.falsifiers)) for d in decisions]),
    )


def signature_distance(a: BehaviorSignature, b: BehaviorSignature) -> float:
    av = (
        a.long_rate, a.flat_rate, a.short_rate, a.mean_confidence, a.sd_confidence,
        a.mean_risk, a.sd_risk, a.mean_expected_return * 20.0, a.mean_forecast_entropy,
        a.mean_claim_count / 5.0, a.mean_falsifier_count / 5.0,
    )
    bv = (
        b.long_rate, b.flat_rate, b.short_rate, b.mean_confidence, b.sd_confidence,
        b.mean_risk, b.sd_risk, b.mean_expected_return * 20.0, b.mean_forecast_entropy,
        b.mean_claim_count / 5.0, b.mean_falsifier_count / 5.0,
    )
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(av, bv)) / len(av))


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_]+", text.lower()))


def lexical_artifact_similarity(a: Decision, b: Decision) -> float:
    ta = _tokens(" ".join((a.crux, a.reasoning_summary, *a.claims, *a.evidence, *a.falsifiers)))
    tb = _tokens(" ".join((b.crux, b.reasoning_summary, *b.claims, *b.evidence, *b.falsifiers)))
    if not ta and not tb:
        return 1.0
    return len(ta & tb) / max(1, len(ta | tb))
