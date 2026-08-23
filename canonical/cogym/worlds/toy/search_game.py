"""Toy world: 10 hidden boxes, one holds the prize, each probe costs.

Zero market concepts. Proves GenericRunner works end-to-end (factminer.md §13).
Policy must find the box while minimizing probes (cost) subject to finding it (quality gate).
"""
from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Any

from ...core.contracts import (ActionResult, ActionSpec, Metric, MetricVector,
                               PolicyDecision, WorldSpec, content_id)

N_BOXES = 10


@dataclass
class ToyState:
    rng_seed: int
    prize_box: int
    probed: tuple[int, ...]
    found: bool


class SearchGameWorld:
    """Deterministic given seed. Actions: PROBE(i). Terminal on found or all probed."""

    def __init__(self, n_boxes: int = N_BOXES):
        self.n = n_boxes
        self._spec = None

    @property
    def world_spec(self) -> WorldSpec:
        if self._spec is None:
            self._spec = WorldSpec(
                world_kind="toy.search_game", version="1",
                instance_set_hash=content_id("inst", {"n": self.n}),
                environment_hash="deterministic-rng",
                oracle_hash="hidden-prize-index")
        return self._spec

    def reset(self, *, instance_id: str, seed: int) -> ToyState:
        rng = random.Random(seed)
        return ToyState(rng_seed=seed, prize_box=rng.randrange(self.n),
                        probed=(), found=False)

    def observe(self, state: ToyState) -> dict:
        return {"n_boxes": self.n,
                "probed_results": [{"box": b, "hit": b == state.prize_box}
                                   for b in state.probed]}

    def actions(self, state: ToyState) -> tuple[ActionSpec, ...]:
        if state.found:
            return ()
        return tuple(ActionSpec(kind="PROBE", payload={"box": i},
                               executor_kind="deterministic",
                               estimated_cost=0.01)
                     for i in range(self.n) if i not in state.probed)

    def apply(self, state: ToyState, action: ActionSpec,
              result: ActionResult) -> ToyState:
        box = action.payload["box"]
        hit = box == state.prize_box
        return ToyState(rng_seed=state.rng_seed, prize_box=state.prize_box,
                        probed=state.probed + (box,), found=hit)

    def terminal(self, state: ToyState) -> bool:
        return state.found or len(state.probed) >= self.n

    def score(self, state: ToyState) -> MetricVector:
        probes = len(state.probed)
        cost = round(0.01 * probes, 6)
        return MetricVector(metrics=(
            Metric(name="found", value=1.0 if state.found else 0.0, direction="max"),
            Metric(name="probes", value=float(probes), direction="min"),
            Metric(name="cash_cost", value=cost, direction="min"),
            Metric(name="wall_latency_ms", value=float(probes * 5), direction="min"),
        ))


# ---------- policies ----------

class SequentialPolicy:
    """Probe 0,1,2,... until hit."""
    policy_id = "toy.sequential"

    def initialize(self, world_spec):
        return {}

    def act(self, obs, available_actions, pstate) -> PolicyDecision:
        if not available_actions:
            raise RuntimeError("no actions left")
        # lowest unprobed box
        best = min(available_actions, key=lambda a: a.payload["box"])
        return PolicyDecision(action=best)


class BinarySearchStylePolicy:
    """Probe middle of remaining range — near-optimal for ordered hidden target."""
    policy_id = "toy.binary"

    def initialize(self, world_spec):
        return {"lo": 0, "hi": N_BOXES - 1}

    def act(self, obs, available_actions, pstate) -> PolicyDecision:
        hits = [r["box"] for r in obs["probed_results"] if r["hit"]]
        lo, hi = pstate["lo"], pstate["hi"]
        if hits:
            return PolicyDecision(action=min(available_actions,
                                             key=lambda a: abs(a.payload["box"] - hits[0])))
        mid = (lo + hi) // 2
        cand = [a for a in available_actions if a.payload["box"] == mid]
        action = cand[0] if cand else available_actions[0]
        # shrink window toward unprobed side heuristically (probe result comes next round)
        pstate["lo"], pstate["hi"] = lo, hi
        return PolicyDecision(action=action)
