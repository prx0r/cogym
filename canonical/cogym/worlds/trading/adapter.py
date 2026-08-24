"""Trading world adapter: legacy TradingWorld behind the generic World contract.

Per docs/factminer.md PR6/§14 — trading becomes a world plugin. Domain structures
(MarketPacket, Bar, WorldManifest) stay here and stop leaking into generic core.
Golden fixture tests/golden/trading_v1_episode.json must still match (parity).
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

from ...core.contracts import (ActionResult, ActionSpec, Metric, MetricVector,
                               PolicyDecision, WorldSpec, content_id)
from ...experiments.factory import synthetic_trading_world
from ...market.world import TradingWorld

STANCES = ("LONG", "FLAT", "SHORT")


def parse_instance(instance_id: str) -> int:
    """instance_id format 'start=<bar_index>'."""
    prefix = "start="
    if not instance_id.startswith(prefix):
        raise ValueError(f"trading instance_id must look like '{prefix}<int>'")
    return int(instance_id[len(prefix):])


@dataclass
class TradingState:
    index: int                      # current decision bar
    horizon: int
    decisions: tuple[tuple[int, str, float], ...] = ()
    # each entry: (bar_index, stance, realized_return_over_horizon)


class TradingWorldAdapter:
    """Walk-forward multi-decision episode over a frozen TradingWorld.

    reset(instance_id='start=N') → at each step the policy sees a public
    observation dict (no future bars) and commits a stance for the next
    `horizon` bars. Non-overlapping horizons keep episodes deterministic.
    """

    def __init__(self, world: TradingWorld, *, horizon: int = 5, lookback: int = 25):
        self.world = world
        self.horizon = horizon
        self.lookback = lookback
        self._spec = None

    @property
    def world_spec(self) -> WorldSpec:
        if self._spec is None:
            m = self.world.manifest
            self._spec = WorldSpec(
                world_kind="trading.synthetic", version="1",
                instance_set_hash=m.bars_digest,
                environment_hash=f"synthetic:{m.metadata.get('level')}:{m.instrument}",
                oracle_hash="future-bars-hidden")
        return self._spec

    def reset(self, *, instance_id: str, seed: int) -> TradingState:
        return TradingState(index=parse_instance(instance_id), horizon=self.horizon)

    def observe(self, state: TradingState) -> dict:
        pkt = self.world.snapshot(state.index, lookback=self.lookback)
        return {
            "world_id": pkt.metadata["world_id"],
            "instrument": pkt.instrument,
            "as_of": pkt.as_of.isoformat(),
            "price": pkt.price,
            "recent_returns": list(pkt.recent_returns),
            "features": {
                "direction": pkt.features.direction,
                "strength": pkt.features.strength,
                "volatility": pkt.features.volatility,
                "drawdown": pkt.features.drawdown,
            },
        }

    def actions(self, state: TradingState) -> tuple[ActionSpec, ...]:
        return tuple(
            ActionSpec(kind="DECIDE", payload={"stance": s},
                       executor_kind="deterministic", estimated_cost=0.0)
            for s in STANCES)

    def apply(self, state: TradingState, action: ActionSpec,
              result: ActionResult) -> TradingState:
        stance = action.payload["stance"]
        realized = self.world.realized_return(state.index, state.horizon)
        return TradingState(
            index=state.index + state.horizon,
            horizon=state.horizon,
            decisions=state.decisions + ((state.index, stance, realized),))

    def terminal(self, state: TradingState) -> bool:
        return state.index + self.horizon >= len(self.world.bars)

    def score(self, state: TradingState) -> MetricVector:
        n = len(state.decisions)
        active = [(s, r) for _, s, r in state.decisions if s in ("LONG", "SHORT")]
        correct = sum(1 for s, r in active
                      if (r >= 0) == (s == "LONG"))
        utility_bps = sum((r if s == "LONG" else -r) * 1e4 for s, r in active)
        return MetricVector(metrics=(
            Metric(name="direction_accuracy",
                   value=correct / len(active) if active else 0.0, direction="max"),
            Metric(name="paper_utility_bps", value=round(utility_bps, 4), direction="max"),
            Metric(name="n_decisions", value=float(n), direction="max"),
            Metric(name="cash_cost", value=0.0, direction="min"),
            Metric(name="wall_latency_ms", value=5.0 * n, direction="min"),
        ))


# ---------- generic policies ----------

class MomentumRulePolicy:
    """The golden-fixture rule as a generic Policy: LONG if last return > 0 else FLAT."""
    policy_id = "trading.momentum_rule_v1"

    def initialize(self, world_spec: WorldSpec) -> Any:
        return {}

    def act(self, obs: dict, available_actions: tuple[ActionSpec, ...],
            policy_state: Any) -> PolicyDecision:
        rets = obs.get("recent_returns") or [0.0]
        want = "LONG" if (rets[-1] if rets else 0.0) > 0 else "FLAT"
        action = next(a for a in available_actions if a.payload["stance"] == want)
        return PolicyDecision(action=action)


class StaticStancePolicy:
    """Always one stance. Used as the cheap-garbage control under quality gates."""

    def __init__(self, stance: str):
        assert stance in STANCES
        self.stance = stance
        self.policy_id = f"trading.static_{stance.lower()}"

    def initialize(self, world_spec: WorldSpec) -> Any:
        return {}

    def act(self, obs, available_actions, policy_state) -> PolicyDecision:
        action = next(a for a in available_actions if a.payload["stance"] == self.stance)
        return PolicyDecision(action=action)


def first_decision(world: TradingWorld, start_index: int, *, horizon: int = 5,
                   lookback: int = 25, policy: MomentumRulePolicy | None = None):
    """One manual step — used by the golden parity test to pin exact values."""
    adapter = TradingWorldAdapter(world, horizon=horizon, lookback=lookback)
    policy = policy or MomentumRulePolicy()
    state = adapter.reset(instance_id=f"start={start_index}", seed=0)
    obs = adapter.observe(state)
    decision = policy.act(obs, adapter.actions(state), policy.initialize(adapter.world_spec))
    new_state = adapter.apply(state, decision.action, ActionResult(
        action_id=decision.action.action_id, status="ok"))
    index, stance, realized = new_state.decisions[0]
    return {"obs": obs, "index": index, "stance": stance, "realized": realized}
