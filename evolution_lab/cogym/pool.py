"""C4: bounded-concurrency evaluation pool.

Evaluates (genome, layer) tuples with a thread pool; per-(genome,world,seed)
results are cached on disk keyed by content hash so repeated campaigns skip
identical work. Model factories that block on HTTP release the GIL, so
threads give real parallelism for inference-bound runs.
"""
from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib, json, os

from .schema import AgentGenome, BenchmarkResult
from .suite import BenchmarkSuite
from .agent import RuleBasedModel

def default_model_factory():
    return RuleBasedModel()

class EvalPool:
    def __init__(self, model_factory, workers: int = 4, cache_dir: str | None = None,
                 executor: str = "process"):
        # NOTE: model_factory must be picklable for process executor (e.g. RuleBasedModel).
        # For HTTP-backed models prefer executor='thread' (GIL released during I/O).
        self.model_factory = model_factory
        self.workers = max(1, workers)
        self.cache_dir = cache_dir
        if cache_dir: os.makedirs(cache_dir, exist_ok=True)
        self.executor_kind = executor

    def _cache_key(self, suite: BenchmarkSuite, genome: AgentGenome, horizon) -> str:
        payload = json.dumps({"w": suite.worlds, "s": suite.seeds,
                              "g": genome.genome_id, "h": horizon}, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    def _eval_one(self, suite: BenchmarkSuite, genome: AgentGenome, horizon):
        return suite.evaluate(genome, self.model_factory, end=horizon)

    def evaluate_many(self, jobs: list[tuple[BenchmarkSuite, AgentGenome]], horizon=None):
        """jobs: list of (suite, genome). Returns {genome_id: BenchmarkResult}."""
        results = {}
        futures = []
        pool_cls = ProcessPoolExecutor if self.executor_kind == "process" else ThreadPoolExecutor
        with pool_cls(max_workers=self.workers) as ex:
            for suite, genome in jobs:
                key = None
                if self.cache_dir:
                    key = self._cache_key(suite, genome, horizon)
                    cf = os.path.join(self.cache_dir, key + ".json")
                    if os.path.exists(cf):
                        d = json.load(open(cf))
                        results[genome.genome_id] = BenchmarkResult(**d["agg"])
                        continue
                    futures.append((ex.submit(self._eval_one, suite, genome, horizon), key, cf, genome))
                else:
                    futures.append((ex.submit(self._eval_one, suite, genome, horizon), None, None, genome))
            for fut, key, cf, genome in futures:
                agg, parts = fut.result()
                results[genome.genome_id] = agg
                if cf:
                    json.dump({"agg": {k: getattr(agg, k) for k in agg.__dataclass_fields__ if k not in ("metadata",)},
                               "parts": [{k: getattr(p, k) for k in p.__dataclass_fields__ if k != "metadata"} for p in parts]},
                              open(cf, "w"))
        return results
