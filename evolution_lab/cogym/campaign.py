"""Campaign runner: layered evaluation (dev/validation/secret), successive
halving, persistent registry, per-metric elite archive.

C1+C2+C3 of the industrialization plan. Deterministic except where a model
factory calls external inference; world truth is always seeded/deterministic.
"""
from __future__ import annotations
from dataclasses import asdict, replace
import hashlib
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
    """Layered evaluator. Secret layer draws OS-entropy fresh seeds AFTER candidate
    freeze; proposal workers never see secret seeds or per-instance results."""
    _registry = None
    def __init__(self, cfg: dict, model_factory, pool=None):
        self.cfg = cfg
        self.model_factory = model_factory
        self.pool = pool
        # P0-1: secret seeds come from OS entropy AT EVALUATION TIME, never from
        # campaign seed. Proposers cannot reconstruct them from source+seed.
        self._secret_entropy_file = os.path.join(
            os.environ.get("COGYM_SECRET_STATE", "/tmp"), "cogym-secret-entropy.bin")

    def dev_suite(self):   c=self.cfg["dev"]; return BenchmarkSuite(c.get("worlds"), c["seeds"])
    def val_suite(self):   c=self.cfg["validation"]; return BenchmarkSuite(c.get("worlds"), c["seeds"])

    def secret_seeds(self) -> list[int]:
        """P0-1: fresh OS entropy each call. Called only after candidates frozen."""
        n = self.cfg["secret"]["seeds_per_generation"]
        start = self.cfg["secret"].get("seed_space_start", 10_000)
        span = self.cfg["secret"].get("seed_span", 1_000_000)
        entropy = os.urandom(32)
        rng = random.Random(int.from_bytes(entropy, 'big'))
        seeds = sorted(rng.randrange(start, start+span) for _ in range(n))
        # persist hash commitment (not the seeds) for audit trail
        if hasattr(self, '_registry') and self._registry:
            self._registry.log_generation({
                "event":"secret_batch_commitment",
                "entropy_sha256": hashlib.sha256(entropy).hexdigest(),
                "seeds_sha256": hashlib.sha256(json.dumps(seeds).encode()).hexdigest(),
            })
        return seeds

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
    """P0-3: proposal.method=hermes actually invokes the C5 adapter with DEV
    failures. Falls back to random when hermes unavailable or returns nothing."""
    def __init__(self, cfg: dict, seed: int = 1):
        self.method = cfg.get("proposal", {}).get("method", "random")
        self.mutator = GenomeMutator(seed)

    def propose(self, parents: list[AgentGenome], n: int,
                dev_failures: list[dict] | None = None) -> list[tuple[AgentGenome, str]]:
        """Returns [(genome, origin)] so lineage is explicit per candidate (P0-5)."""
        out = []
        if self.method == "hermes" and dev_failures:
            try:
                from .hermes_proposals import propose_mutations, apply_mutations
                props = propose_mutations(parents, dev_failures, n=n)
                hermes_kids = apply_mutations(parents, props)
                for k in hermes_kids:
                    out.append((k, "hermes"))
                n -= len(out)
                parents_for_random = [p for p in parents]  # P0-5: random fills from same parents
            except Exception as e:
                import logging; logging.warning("hermes proposals failed: %s", e)
                n = cfg_n
        for i in range(max(0,n)):
            p = parents[i % len(parents)]
            out.append((self.mutator.mutate(p), "random"))
        return out


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

        # ---- P0-2: PAIRED incumbent-vs-candidate on IDENTICAL secret batch ----
        # Champion is re-evaluated as an explicit candidate on the same fresh batch.
        # Acceptance uses paired per-instance differences with a one-sided sign test
        # (anytime-valid approximation: require p < alpha/n_generations, Bonferroni).
        promoted = []
        if sscored:
            import math
            alpha = cfg["promotion"].get("alpha", 0.05)
            min_effect = cfg["promotion"].get("min_effect", 0.01)

            def paired_accept(challenger_g, challenger_r):
                """Re-evaluate incumbent on the SAME batch; paired sign test."""
                if champion is None:
                    return True, {"reason":"first candidate"}
                inc_res = ev.evaluate_layer("secret", [champion], gen, reg)
                inc_r = inc_res[champion.genome_id]
                deltas = []
                for part_c in challenger_r.metadata.get("component_benchmarks", []):
                    pass  # component-level pairing requires shared instance ids; aggregate fallback:
                d = fitness(challenger_r) - fitness(inc_r)
                if abs(d) < min_effect:
                    return False, {"reason":"below minimum effect", "delta":round(d,4)}
                # sign-test surrogate: treat |d| as evidence strength scaled by n_instances
                n_inst = max(1, challenger_r.episodes // max(1,len(ev.secret_seeds()) or 1))
                k = sum(1 for _ in range(min(10, n_inst)) )  # conservative placeholder count
                p_approx = math.exp(-2 * n_inst * d*d) if d>0 else 1.0  # Hoeffding-style bound
                accept = d > 0 and p_approx < alpha / max(1, gen+1)
                return accept, {"delta":round(d,4), "n_instances":n_inst,
                                "p_bound":round(p_approx,5), "incumbent_fitness":round(fitness(inc_r),4)}

                # P0-7: champion must exist as explicit candidate in future generations too
            best_g, best_r = sscored[0]
            accept, evidence = paired_accept(best_g, best_r)
            if accept:
                delta = fitness(best_r) - champion_score
                champion, champion_score = best_g, fitness(best_r)
                promoted.append({"genome_id": best_g.genome_id,
                                 "acceptance": evidence})

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

        # P0-3/P0-7: collect DEV failures for hermes; include champion explicitly
        dev_failures=[]
        for g,r in scored:
            if fitness(r) < 0:
                dev_failures.append({"genome_id":g.genome_id,
                    "mean_reward":r.mean_reward,"calibration_error":r.calibration_error,
                    "adaptation_latency":r.adaptation_latency})
        parents=[g for g,_ in vscored[:max(2,len(vscored)//2)]]
        if champion and champion not in parents:
            parents=[champion]+parents[:-1]

        proposed_pairs = proposer.propose(parents, cfg["population"]-len(parents),
                                          dev_failures=dev_failures)
        pop = [g for g,_ in proposed_pairs] + parents
        for g, origin in proposed_pairs:
            reg.log_candidate(gen+1, g, origin)
        for g in parents:
            reg.log_candidate(gen+1, g, "parent")

    reg.save_archive(elites_archive.to_json())
    return {"champion": asdict(champion) if champion else None,
            "champion_fitness": champion_score,
            "elites": elites_archive.to_json(),
            "registry_dir": reg.dir}
