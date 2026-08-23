"""Cogym v2 evaluation: constraint gates + lexicographic comparator + paired non-inferiority.

Quality is a CONSTRAINT, never traded away by cost (factminer.md §9-§12).
Selection: quality gate → cost → latency → simplicity.
"""
from __future__ import annotations
import math
import statistics
from dataclasses import dataclass, field
from typing import Literal

from .contracts import MetricVector


@dataclass(frozen=True)
class QualityGate:
    metric: str
    mode: Literal["min", "max", "noninferior"] = "max"
    value: float | None = None          # hard threshold for min/max
    baseline: str | None = None         # for noninferior
    margin: float = 0.0                 # allowed regression margin for noninferior


@dataclass(frozen=True)
class GateResult:
    gate: QualityGate
    passed: bool
    observed: float | None
    detail: str = ""


def check_gate(gate: QualityGate, metrics: MetricVector,
               baseline_metrics: MetricVector | None = None) -> GateResult:
    v = metrics.get(gate.metric)
    if v is None:
        return GateResult(gate, False, None, f"metric '{gate.metric}' missing")
    if gate.mode == "min":
        ok = v <= (gate.value if gate.value is not None else math.inf)
        return GateResult(gate, ok, v, f"{v:.6g} <= {gate.value}")
    if gate.mode == "max":
        ok = v >= (gate.value if gate.value is not None else -math.inf)
        return GateResult(gate, ok, v, f"{v:.6g} >= {gate.value}")
    # noninferior vs baseline
    b = baseline_metrics.get(gate.metric) if baseline_metrics else None
    if b is None:
        return GateResult(gate, False, v, "baseline metric missing")
    ok = v >= b - gate.margin
    return GateResult(gate, ok, v, f"delta {v-b:+.6g} >= -{gate.margin}")


def run_gates(gates: tuple[QualityGate, ...], metrics: MetricVector,
              baseline_metrics: MetricVector | None = None) -> tuple[GateResult, ...]:
    return tuple(check_gate(g, metrics, baseline_metrics) for g in gates)


@dataclass(frozen=True)
class Objective:
    metric: str
    direction: Literal["min", "max"] = "min"
    epsilon: float = 1e-9              # materiality threshold


def lexicographic_compare(a: MetricVector, a_pass: bool,
                          b: MetricVector, b_pass: bool,
                          objectives: tuple[Objective, ...] = (
                              Objective("cash_cost", "min"),
                              Objective("wall_latency_ms", "min"))) -> Literal[-1, 0, 1]:
    """Return -1 if a preferred, +1 if b preferred, 0 tie. Gates dominate everything."""
    if a_pass != b_pass:
        return -1 if a_pass else 1
    for obj in objectives:
        av, bv = a.get(obj.metric), b.get(obj.metric)
        if av is None and bv is None:
            continue
        if av is None:
            return 1     # missing objective loses to present
        if bv is None:
            return -1
        better = (av < bv) if obj.direction == "min" else (av > bv)
        if abs(av - bv) > obj.epsilon:
            return -1 if better else 1
    return 0


# ---------- paired non-inferiority ----------

def paired_deltas(baseline_scores: list[float], candidate_scores: list[float]) -> list[float]:
    assert len(baseline_scores) == len(candidate_scores), "paired requires matched instances"
    return [c - b for b, c in zip(baseline_scores, candidate_scores)]


def bootstrap_ci(deltas: list[float], n_boot: int = 2000, alpha: float = 0.05,
                 seed: int = 7) -> tuple[float, float]:
    """Percentile bootstrap CI on mean delta. Deterministic given seed."""
    import random
    rng = random.Random(seed)
    if not deltas:
        return (float("nan"), float("nan"))
    means = []
    n = len(deltas)
    for _ in range(n_boot):
        sample = [deltas[rng.randrange(n)] for _ in range(n)]
        means.append(statistics.mean(sample))
    means.sort()
    lo = means[int((alpha / 2) * n_boot)]
    hi = means[min(int((1 - alpha / 2) * n_boot), n_boot - 1)]
    return (lo, hi)


def non_inferior_paired(baseline_scores: list[float], candidate_scores: list[float],
                        margin: float = 0.005, seed: int = 7) -> dict:
    deltas = paired_deltas(baseline_scores, candidate_scores)
    lo, hi = bootstrap_ci(deltas, seed=seed)
    mean_delta = statistics.mean(deltas) if deltas else float("nan")
    return {
        "mean_delta": mean_delta,
        "ci95": [lo, hi],
        "lcb": lo,
        "margin": margin,
        "non_inferior": lo >= -margin - 1e-12,
        "n_pairs": len(deltas),
        "method": "paired percentile bootstrap (frozen seed)",
    }
