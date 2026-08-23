"""Cogym v2 PR4: generic campaign runner + PR7 replay tapes.

Campaign: population of CandidateArtifacts -> paired dev evaluation ->
lexicographic selection under quality gates -> generational archive.
ReplayTape: record ActionResults once; TapeExecutor replays deterministically.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable

from .contracts import (ActionResult, ActionSpec, CandidateArtifact,
                        EpisodeRecord, MetricVector, World)
from .evaluation import Objective, QualityGate, lexicographic_compare


# ---------- PR7: replay ----------

class ReplayTape:
    """action_id -> ActionResult. Recorded from live runs; replayed byte-identical."""

    def __init__(self):
        self._store: dict[str, ActionResult] = {}

    def record(self, result: ActionResult) -> None:
        self._store[result.action_id] = result

    def lookup(self, action_id: str) -> ActionResult | None:
        return self._store.get(action_id)

    def __len__(self):
        return len(self._store)


class TapeExecutor:
    """Executor that serves frozen observations. Unknown actions are ERRORS,
    never silent live fallbacks — mixing live+replay invalidates experiments."""

    executor_id = "tape-v1"

    def __init__(self, tape: ReplayTape):
        self.tape = tape

    def execute(self, action: ActionSpec) -> ActionResult:
        hit = self.tape.lookup(action.action_id)
        if hit is None:
            return ActionResult(action_id=action.action_id, status="error",
                                error=f"action {action.action_id} not in tape")
        return hit


class RecordingExecutor:
    """Wraps a live executor; records every result into the tape."""

    def __init__(self, inner, tape: ReplayTape):
        self.inner = inner
        self.tape = tape
        self.executor_id = f"recording[{getattr(inner, 'executor_id', '?')}]"

    def execute(self, action: ActionSpec) -> ActionResult:
        result = self.inner.execute(action)
        self.tape.record(result)
        return result


# ---------- PR4: campaign ----------

WorldFactory = Callable[[str], World]           # instance_id -> fresh world view
PolicyFactory = Callable[[CandidateArtifact], object]  # candidate -> policy object
RunnerFn = Callable[..., EpisodeRecord]          # GenericRunner.run_episode


@dataclass
class CampaignConfig:
    world_kind: str
    suite: tuple[tuple[str, int], ...]         # (instance_id, seed) pairs — frozen
    gates: tuple[QualityGate, ...]
    objectives: tuple[Objective, ...] = (
        Objective("cash_cost", "min"), Objective("wall_latency_ms", "min"))
    generations: int = 3
    population: int = 6
    elite_k: int = 2


@dataclass
class EvaluatedCandidate:
    candidate: CandidateArtifact
    records: list[EpisodeRecord] = field(default_factory=list)
    baseline_metrics: MetricVector | None = None
    quality_pass: bool = False

    @property
    def metrics(self) -> MetricVector:
        return self.records[-1].metrics if self.records else MetricVector(metrics=())


def run_episode_suite(world_fn, policy, runner, suite) -> list[EpisodeRecord]:
    return [runner.run_episode(world_fn(inst), policy, instance_id=inst, seed=seed)
            for inst, seed in suite]


def aggregate(records: list[EpisodeRecord]) -> MetricVector:
    """Mean of each metric name across episodes."""
    from .contracts import Metric
    names: set[str] = set()
    for r in records:
        names |= set(r.metrics.names())
    out = []
    for n in sorted(names):
        vals = [r.metrics.get(n) for r in records if r.metrics.get(n) is not None]
        if vals:
            out.append(Metric(name=n, value=sum(vals) / len(vals),
                              direction="min" if any(
                                  m.name == n and m.direction == "min"
                                  for r in records for m in r.metrics.metrics) else "max"))
    return MetricVector(metrics=tuple(out))


def gates_pass(gates, metrics, baseline_metrics) -> bool:
    from .evaluation import run_gates
    return all(g.passed for g in run_gates(gates, metrics, baseline_metrics))


def rank_population(cands: list[EvaluatedCandidate],
                    objectives: tuple[Objective, ...]) -> list[EvaluatedCandidate]:
    """Insertion sort with lexicographic comparator; gates dominate objectives."""
    ranked = sorted(cands, key=lambda c: c.candidate.candidate_id)  # deterministic base
    for i in range(1, len(ranked)):
        cur = ranked[i]
        j = i - 1
        while j >= 0:
            cmp = lexicographic_compare(
                cur.metrics, cur.quality_pass,
                ranked[j].metrics, ranked[j].quality_pass, objectives)
            if cmp == -1:
                ranked[j + 1] = ranked[j]
                j -= 1
            else:
                break
        ranked[j + 1] = cur
    return ranked


class Campaign:
    """Minimal generic evolution loop: evaluate -> gate -> rank -> keep elites.
    Mutation/proposal is pluggable (Hermes adapter later); campaign itself never
    inspects domain internals."""

    def __init__(self, config: CampaignConfig, runner,
                 world_fn: WorldFactory, propose_fn: Callable[
                     [list[CandidateArtifact], int], list[CandidateArtifact]]):
        self.cfg = config
        self.runner = runner
        self.world_fn = world_fn
        self.propose_fn = propose_fn      # (parents, n_children) -> children
        self.archive: list[CandidateArtifact] = []

    def _evaluate(self, cand: CandidateArtifact, policy_factory: PolicyFactory,
                  baseline_metrics: MetricVector | None) -> EvaluatedCandidate:
        recs = run_episode_suite(self.world_fn, policy_factory(cand),
                                 self.runner, self.cfg.suite)
        ec = EvaluatedCandidate(candidate=cand, records=recs,
                                baseline_metrics=baseline_metrics)
        ec.quality_pass = gates_pass(self.cfg.gates, aggregate(recs), baseline_metrics)
        return ec

    def run(self, seeds: list[CandidateArtifact], policy_factory: PolicyFactory,
            baseline_metrics: MetricVector | None = None) -> list[CandidateArtifact]:
        population = seeds[: self.cfg.population]
        winners: list[CandidateArtifact] = []
        for gen in range(self.cfg.generations):
            evaluated = [self._evaluate(c, policy_factory, baseline_metrics)
                         for c in population]
            passing = [e for e in evaluated if e.quality_pass]
            if not passing:
                break  # whole population dead under gates — fail closed
            ranked = rank_population(passing, self.cfg.objectives)
            elites = ranked[: self.cfg.elite_k]
            winners = [e.candidate for e in elites]
            self.archive.extend(winners)
            if gen < self.cfg.generations - 1:
                population = self.propose_fn(winners, self.cfg.population - len(winners))
                population = winners + population
        return winners
