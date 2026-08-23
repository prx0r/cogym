from __future__ import annotations
from dataclasses import replace
import random
from .schema import AgentGenome, BenchmarkResult

INDUCTIONS=["neutral","loss_salience","missed_upside","time_pressure","supportive","critical","contrarian_pressure"]
REPS=["plain","formal","bayesian","compressed","socratic","metaphoric"]
REASON=["falsification_first","base_rate_first","causal","scenario_tree","evidence_balance","novelty_search"]
MEM=["recent","failures_first","successes_first","none"]
SOCIAL=["independent","all_to_all"]
REVEAL=["none","decision","decision_confidence","full"]

class GenomeMutator:
    def __init__(self, seed:int=1): self.rng=random.Random(seed)
    def mutate(self,g:AgentGenome,rate:float|None=None)->AgentGenome:
        p=rate if rate is not None else max(0.05,g.plasticity)
        kw={}
        for name,space in [("induction",INDUCTIONS),("representation",REPS),("reasoning_policy",REASON),
                           ("memory_policy",MEM),("social_topology",SOCIAL),("reveal",REVEAL)]:
            if self.rng.random()<p: kw[name]=self.rng.choice(space)
        if self.rng.random()<p: kw["memory_depth"]=self.rng.randint(0,8)
        if self.rng.random()<p: kw["revision_rounds"]=self.rng.randint(0,1)
        if self.rng.random()<p: kw["plasticity"]=min(0.8,max(0.02,g.plasticity*self.rng.uniform(0.6,1.6)))
        return replace(g,**kw)


def fitness(r:BenchmarkResult)->float:
    # Multi-objective scalar only for selection; raw metrics are retained.
    return (r.mean_reward + 0.35*r.downside_reward - 0.25*r.calibration_error
            - 0.02*r.max_drawdown - 0.005*r.adaptation_latency + 0.05*r.revision_gain)

class EvolutionController:
    """Population-level selection with stagnation-triggered exploration."""
    def __init__(self,seed:int=1,elite_fraction:float=0.3):
        self.mutator=GenomeMutator(seed); self.elite_fraction=elite_fraction; self.best_history=[]
    def next_generation(self,population:list[AgentGenome],results:list[BenchmarkResult])->list[AgentGenome]:
        score={r.genome_id:fitness(r) for r in results}
        ranked=sorted(population,key=lambda g:score.get(g.genome_id,-1e9),reverse=True)
        n_elite=max(1,int(len(ranked)*self.elite_fraction)); elites=ranked[:n_elite]
        best=score.get(elites[0].genome_id,-1e9); self.best_history.append(best)
        stagnant=len(self.best_history)>=4 and max(self.best_history[-4:])-min(self.best_history[-4:])<1e-4
        rate=0.55 if stagnant else None
        children=elites.copy()
        while len(children)<len(population):
            parent=self.mutator.rng.choice(elites)
            children.append(self.mutator.mutate(parent,rate=rate))
        return children
