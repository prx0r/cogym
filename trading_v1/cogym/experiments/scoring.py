from __future__ import annotations

import math
from dataclasses import dataclass

from ..agents.decision import Decision


@dataclass(frozen=True)
class DecisionScore:
    log_score: float
    brier: float
    direction_correct: float
    return_error: float
    paper_utility: float


def outcome_class(realized_return: float, flat_band: float = 0.001) -> int:
    if realized_return > flat_band:
        return 0
    if realized_return < -flat_band:
        return 2
    return 1


def score_decision(decision: Decision, realized_return: float, *, flat_band: float = 0.001) -> DecisionScore:
    idx = outcome_class(realized_return, flat_band)
    probs = (decision.p_up, decision.p_flat, decision.p_down)
    p = max(probs[idx], 1e-12)
    log_score = math.log(p)
    y = [0.0, 0.0, 0.0]
    y[idx] = 1.0
    brier = sum((a - b) ** 2 for a, b in zip(probs, y)) / 3.0
    correct = float((decision.stance == "LONG" and idx == 0) or (decision.stance == "FLAT" and idx == 1) or (decision.stance == "SHORT" and idx == 2))
    return_error = abs(decision.expected_return - realized_return)
    sign = 1.0 if decision.stance == "LONG" else -1.0 if decision.stance == "SHORT" else 0.0
    # Paper utility is deliberately simple and never presented as a production trading strategy.
    paper_utility = sign * realized_return
    return DecisionScore(log_score, brier, correct, return_error, paper_utility)
