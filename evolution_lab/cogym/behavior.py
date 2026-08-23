from __future__ import annotations
from dataclasses import dataclass
import statistics
from .schema import Decision

@dataclass(frozen=True)
class BehaviorSignature:
    long_rate: float
    flat_rate: float
    short_rate: float
    mean_confidence: float
    mean_expected_return: float
    revision_rate: float


def signature(decisions:list[Decision])->BehaviorSignature:
    n=max(1,len(decisions))
    return BehaviorSignature(
        sum(d.action=="LONG" for d in decisions)/n,
        sum(d.action=="FLAT" for d in decisions)/n,
        sum(d.action=="SHORT" for d in decisions)/n,
        statistics.mean([d.confidence for d in decisions]) if decisions else 0,
        statistics.mean([d.expected_return for d in decisions]) if decisions else 0,
        sum(d.revised for d in decisions)/n,
    )


def distance(a:BehaviorSignature,b:BehaviorSignature)->float:
    vals=[abs(a.long_rate-b.long_rate),abs(a.flat_rate-b.flat_rate),abs(a.short_rate-b.short_rate),
          abs(a.mean_confidence-b.mean_confidence),min(1,abs(a.mean_expected_return-b.mean_expected_return)*20),
          abs(a.revision_rate-b.revision_rate)]
    return sum(vals)/len(vals)
