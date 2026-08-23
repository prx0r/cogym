"""Campaign runner: layered evaluation (dev/validation/secret), successive
halving, persistent registry, per-metric elite archive.

C1+C2+C3 of the industrialization plan. Deterministic except where a model
factory calls external inference; world truth is always seeded/deterministic.
"""
from __future__ import annotations
from dataclasses import asdict, replace
import json, os, random, statistics, time
import yaml

from .schema import AgentGenome, BenchmarkResult
from .evolution import GenomeMutator, fitness
from .suite import BenchmarkSuite

DEFAULT_CAMPAIGN = {
    "population": 12,
    "generations": 3,
    "horizon": None,
    "dev": {"worlds": None, "seeds": [7, 19, 43, 71]},
    "validation": {"worlds": None, "seeds": [101, 103, 107, 109, 113, 127]},
    "secret": {"worlds": None, "seeds_per_generation": 16, "seed_space_start": 10_000},
    "halving": {"after_dev": 0.5, "after_validation": 8},
    "proposal": {"method": "random"},
    "selection": {"elites": 4},
    "promotion": {"min_secret_fitness_delta": 0.0},
}

def _deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


class CampaignRegistry:
    """Persistent campaign artifacts under campaigns/<id>/."""
    def __init__(self, root: str, campaign_cfg: dict):
        cid = f"{time.strftime('%Y%m%d-%H%M%S')}-{campaign_cfg.get('name','campaign')}"
        self.dir = os.path.join(root, "campaigns", cid)
        os.makedirs(self.dir, exist_ok=True)
        self.manifest_path = os.path.join(self.dir, "manifest.json")
        self.candidates_path = os.path.join(self.dir, "candidates.jsonl")
        self.evals_path = os.path.join(self.dir, "evaluations.jsonl")
        self.generations_path = os.path.join(self.dir, "generations.jsonl")
        self.archive_path = os.path.join(self.dir, "archive.json")
        json.dump({"config": campaign_cfg, "started_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())},
                  open(self.manifest_path, "w"), indent=2)

    def log_candidate(self, gen: int, genome: AgentGenome, origin: str):
        with open(self.candidates_path, "a") as f:
            f.write(json.dumps({"gen": gen, "origin": origin,
                                "genome_id": genome.genome_id,
                                "genome": asdict(genome)}) + "\n")

    def log_eval(self, gen: int, layer: str, result: BenchmarkResult):
        with open(self.evals_path, "a") as f:
            f.write(json.dumps({"gen": gen, "layer": layer,
                                "genome_id": result.genome_id,
                                "benchmark_id": result.benchmark_id,
                                "fitness": round(fitness(result), 6),
                                **{k: getattr(result, k) for k in
                                   ("mean_reward","downside_reward","calibration_error",
                                    "max_drawdown","adaptation_latency","revision_gain")},
                                }) + "\n")

    def log_generation(self, record: dict):
        with open(self.generations_path, "a") as f:
            f.write(json.dumps(record) + "\n")

    def save_archive(self, archive: dict):
        json.dump(archive, open(self.archive_path, "w"), indent=2)


class HiddenEvaluator:
    """Layered evaluator. Secret layer draws fresh seeds each generation from a
    wide space; proposal workers never see secret seeds or per-seed results."""
    def __init__(self, cfg: dict, model_factory, pool=None):
        self.cfg = cfg
        self.model_factory = model_factory
        self.pool = pool   # optional EvalPool; enables concurrent + cached evaluation
        self._secret_rng = random.Random(cfg.get("seed", 1) ^ 0x5EED)

    def dev_suite(self):   c=self.cfg["dev"]; return BenchmarkSuite(c.get("worlds"), c["seeds"])
    def val_suite(self):   c=self.cfg["validation"]; return BenchmarkSuite(c.get("worlds"), c["seeds"])

    def secret_seeds(self) -> list[int]:
        n = self.cfg["secret"]["seeds_per_generation"]
        start = self.cfg["secret"].get("seed_space_start", 10_000)
        span = self.cfg["secret"].get("seed_span", 1_000_000)
        return sorted(self._secret_rng.randrange(start, start+span) for _ in range(n))

    def evaluate_layer(self, layer: str, genomes: list[AgentGenome], gen: int,
                       registry: CampaignRegistry | None = None):
        suite = {"dev": self.dev_suite, "validation": self.val_suite}.get(layer)
        if suite:
            s = suite()
        else:
            s = BenchmarkSuite(self.cfg["secret"].get("worlds"), self.secret_seeds())
        results = {}
        if self.pool is not None:
            res_map = self.pool.evaluate_many([(s, g) for g in genomes],
                                              horizon=self.cfg.get("horizon"))
            results.update(res_map)
        else:
            for g in genomes:
                agg, parts = s.evaluate(g, self.model_factory, end=self.cfg.get("horizon"))
                results[g.genome_id] = agg
            if registry:
                registry.log_eval(gen, layer, agg)
                if layer == "dev":
                    for part in parts:
                        registry.log_eval(gen, f"dev_part:{part.metadata.get('world_name','?')}", part)
        return results


class ElitesArchive:
    """Per-metric champions so specialists survive scalar selection."""
    METRICS = {
        "overall": lambda r: fitness(r),
        "best_calibration": lambda r: -r.calibration_error,
        "fastest_adapter": lambda r: -r.adaptation_latency,
        "best_downside": lambda r: r.downside_reward,
        "best_shock_response": lambda r: r.mean_reward,
        "lowest_cost": lambda r: -getattr(r, "cost_units", 0.0),
    }
    def __init__(self): self.archive = {}

    def update(self, genome: AgentGenome, res_dev, res_val=None, res_secret=None):
        ref = res_secret or res_val or res_dev
        for name, fn in self.METRICS.items():
            src = ref if name != "overall" else res_dev
            v = fn(src)
            cur = self.archive.get(name)
            if cur is None or v > cur["value"]:
                self.archive[name] = {"value": v, "genome_id": genome.genome_id,
                                      "genome": asdict(genome)}

    def to_json(self): return self.archive


class ProposalEngine:
    """Mutation proposals. method=random uses GenomeMutator; method=hermes calls
    the adapter (C5) when HERMES is available; both can mix."""
    def __init__(self, cfg: dict, seed: int = 1):
        self.method = cfg.get("proposal", {}).get("method", "random")
        self.mutator = GenomeMutator(seed)

    def propose(self, parents: list[AgentGenome], n: int, context=None) -> list[AgentGenome]:
        kids = []
        for i in range(n):
            p = parents[i % len(parents)]
            kids.append(self.mutator.mutate(p))
        return kids


def run_campaign(cfg_path: str, model_factory, root: str = ".") -> dict:
    raw = yaml.safe_load(open(cfg_path)) or {}
    cfg = _deep_merge(DEFAULT_CAMPAIGN, raw)
    reg = CampaignRegistry(root, cfg)
    ev = HiddenEvaluator(cfg, model_factory)
    proposer = ProposalEngine(cfg)

    rng = random.Random(cfg.get("seed", 1))
    pop = [AgentGenome(model="rulebased-v1",
                       reasoning_policy=rng.choice(["falsification_first","base_rate_first","causal"]),
                       representation=rng.choice(["plain","bayesian"]),
                       memory_policy=rng.choice(["recent","failures_first","none"]),
                       memory_depth=rng.choice([0,3,6])) for _ in range(cfg["population"])]

    elites_archive = ElitesArchive()
    champion = None
    champion_score = -1e18

    for gen in range(cfg["generations"]):
        t0 = time.time()
        # DEV: everyone
        dev_res = ev.evaluate_layer("dev", pop, gen, reg)
        scored = [(g, dev_res[g.genome_id]) for g in pop]
        scored.sort(key=lambda t: fitness(t[1]), reverse=True)

        # HALVE after dev
        keep_n = max(2, int(len(scored) * cfg["halving"]["after_dev"]))
        survivors = scored[:keep_n]

        # VALIDATION: survivors only
        val_res = ev.evaluate_layer("validation", [g for g,_ in survivors], gen, reg)
        vscored = [(g, val_res[g.genome_id]) for g,_ in survivors]
        vscored.sort(key=lambda t: fitness(t[1]), reverse=True)
        final_n = min(len(vscored), cfg["halving"]["after_validation"])
        finalists = vscored[:final_n]

        # SECRET: finalists, fresh seeds every generation
        sec_res = ev.evaluate_layer("secret", [g for g,_ in finalists], gen, reg)
        sscored = [(g, sec_res[g.genome_id]) for g,_ in finalists]
        sscored.sort(key=lambda t: fitness(t[1]), reverse=True)

        # promotion gate vs running champion (secret-to-secret comparison)
        promoted = []
        if sscored:
            best_g, best_r = sscored[0]
            delta = fitness(best_r) - champion_score
            if champion is None or delta >= cfg["promotion"]["min_secret_fitness_delta"]:
                champion, champion_score = best_g, fitness(best_r)
                promoted.append({"genome_id": best_g.genome_id, "delta": round(delta, 4)})

        # elites archive on dev numbers + secret ref
        for g, r in sscored[:3]:
            elites_archive.update(g, dev_res[g.genome_id], val_res[g.genome_id], sec_res[g.genome_id])
        for g, r in scored[:3]:
            elites_archive.update(g, r)

        reg.log_generation({
            "gen": gen, "population": len(pop),
            "dev_best": round(fitness(scored[0][1]), 4),
            "val_best": round(fitness(vscored[0][1]), 4) if vscored else None,
            "secret_best": round(fitness(sscored[0][1]), 4) if sscored else None,
            "champion": champion.genome_id if champion else None,
            "promoted": promoted,
            "secs": round(time.time()-t0, 1),
        })
        print(f"[gen {gen}] dev={fitness(scored[0][1]):.3f} "
              f"val={fitness(vscored[0][1]):.3f} secret={fitness(sscored[0][1]):.3f} "
              f"champion={'yes' if promoted else 'held'} ({time.time()-t0:.0f}s)")

        # propose next generation from top half of validation ranking
        parents=[g for g,_ in vscored[:max(2,len(vscored)//2)]]
        pop = proposer.propose(parents, cfg["population"]-len(parents)) + parents
        for g in pop:
            reg.log_candidate(gen+1, g, proposer.method)

    reg.save_archive(elites_archive.to_json())
    return {"champion": asdict(champion) if champion else None,
            "champion_fitness": champion_score,
            "elites": elites_archive.to_json(),
            "registry_dir": reg.dir}
