from __future__ import annotations
from dataclasses import asdict
import statistics
from .benchmark import WORLD_SUITE, make_world
from .schema import AgentGenome, BenchmarkResult
from .memory import SQLiteMemory
from .agent import CognitiveAgent, Model
from .experiment import ExperimentRunner
from .utils import sha256_id

class BenchmarkSuite:
    """Evaluate one genome across multiple deterministic world families/seeds."""
    def __init__(self, worlds: list[str] | None=None, seeds: list[int] | None=None):
        self.worlds=worlds or list(WORLD_SUITE)
        self.seeds=seeds or [7,19,43]

    def evaluate(self, genome:AgentGenome, model_factory, end:int|None=None)->tuple[BenchmarkResult,list[BenchmarkResult]]:
        parts=[]
        for wname in self.worlds:
            for seed in self.seeds:
                mem=SQLiteMemory(":memory:")
                model:Model=model_factory()
                agent=CognitiveAgent("candidate",genome,model,mem)
                world=make_world(wname,seed)
                runner=ExperimentRunner(world,[agent]); runner.run(end=end)
                r=runner.results()[0]
                r.metadata.update({"world_name":wname,"seed":seed})
                parts.append(r)
        agg=BenchmarkResult(
            benchmark_id=sha256_id(self.worlds,self.seeds,genome.genome_id,prefix="suite_"),
            genome_id=genome.genome_id,episodes=sum(x.episodes for x in parts),
            mean_reward=statistics.mean(x.mean_reward for x in parts),
            downside_reward=statistics.mean(x.downside_reward for x in parts),
            calibration_error=statistics.mean(x.calibration_error for x in parts),
            max_drawdown=max(x.max_drawdown for x in parts),
            adaptation_latency=statistics.mean(x.adaptation_latency for x in parts),
            revision_gain=statistics.mean(x.revision_gain for x in parts),
            metadata={"component_benchmarks":[x.benchmark_id for x in parts]}
        )
        return agg,parts
