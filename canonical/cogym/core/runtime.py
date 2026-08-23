"""Generic episode runner: world + policy + executor → EpisodeRecord.

World.apply() receives ActionResult; executor is the ONLY thing that touches
the outside (model/search/browser). Parallel waves canonicalize by action_id.
"""
from __future__ import annotations
import time
from typing import Any

from .contracts import (ActionResult, ActionWave, EpisodeRecord, Executor,
                        MetricVector, Policy, World, content_id, now_ns)


class GenericRunner:
    def __init__(self, executors: dict[str, Executor]):
        self.executors = executors  # keyed by executor_kind

    def _execute(self, action) -> ActionResult:
        ex = self.executors.get(action.executor_kind)
        if ex is None:
            return ActionResult(action_id=action.action_id, status="error",
                                error=f"no executor for kind '{action.executor_kind}'")
        t0 = now_ns()
        result = ex.execute(action)
        if not isinstance(result.started_ns, int) or result.started_ns == 0:
            result = ActionResult(**{**result.__dict__, "started_ns": t0,
                                     "finished_ns": now_ns(),
                                     "wall_ms": (now_ns() - t0) / 1e6})
        return result

    def run_wave(self, wave: ActionWave) -> tuple[ActionResult, ...]:
        """Sequential here; parallel scheduler plugs in later without changing
        canonicalization: receipts are ALWAYS sorted by action_id."""
        receipts = [self._execute(a) for a in wave.actions]
        return tuple(sorted(receipts, key=lambda r: r.action_id))

    def run_episode(self, world: World, policy: Policy, *, instance_id: str,
                    seed: int, treatment_id: str | None = None,
                    max_steps: int = 64) -> EpisodeRecord:
        state = world.reset(instance_id=instance_id, seed=seed)
        pstate = policy.initialize(world.world_spec)
        event_ids: list[str] = []
        steps = 0
        while not world.terminal(state) and steps < max_steps:
            obs = world.observe(state)
            avail = world.actions(state)
            decision = policy.act(obs, avail, pstate)
            result = self._execute(decision.action)
            state = world.apply(state, decision.action, result)
            event_ids.append(result.receipt_hash)
            steps += 1
        metrics = world.score(state) if hasattr(world, "score") else MetricVector(metrics=())
        finished = now_ns()
        return EpisodeRecord(
            episode_id=content_id("ep", {"world": world.world_spec.spec_id,
                                         "inst": instance_id, "seed": seed,
                                         "cand": policy.policy_id}),
            world_spec_id=world.world_spec.spec_id,
            instance_id=instance_id,
            candidate_id=policy.policy_id,
            treatment_id=treatment_id,
            event_ids=tuple(event_ids),
            final_output_hash=content_id("final", {"events": event_ids}),
            metrics=metrics,
            started_at_ns=0,  # caller-level timing; per-action timing in receipts
            finished_at_ns=finished)
