"""Deterministic executor for toy worlds — simulates cost/latency without I/O."""
from __future__ import annotations
from ..core.contracts import ActionResult, ActionSpec, Executor, content_id, now_ns


class DeterministicExecutor:
    executor_id = "det-v1"

    def execute(self, action: ActionSpec) -> ActionResult:
        t0 = now_ns()
        return ActionResult(
            action_id=action.action_id, status="ok",
            payload={"echo": action.payload},
            started_ns=t0, finished_ns=now_ns(),
            wall_ms=5.0,
            cash_cost=action.estimated_cost or 0.0,
            normalized_cost=action.estimated_cost or 0.0,
            provider="local",
            response_hash=content_id("resp", action.payload))
