from __future__ import annotations
from dataclasses import asdict
import statistics
from .schema import AgentGenome, Decision, RunRecord, BenchmarkResult
from .world import SyntheticMarketWorld
from .agent import CognitiveAgent, Model
from .memory import MemoryBackend, MemoryItem
from .scoring import score_decision
from .utils import sha256_id

class ExperimentRunner:
    def __init__(self, world: SyntheticMarketWorld, agents: list[CognitiveAgent], horizon: int = 1):
        self.world=world; self.agents=agents; self.horizon=horizon; self.records:list[RunRecord]=[]

    def run(self, start: int = 24, end: int | None = None) -> list[RunRecord]:
        end=min(end or self.world.length-2,self.world.length-2)
        for snap in self.world.iter_snapshots(start,end):
            private:dict[str,tuple[Decision,str]]={}
            for a in self.agents:
                private[a.agent_id]=a.decide(snap)
            final:dict[str,tuple[Decision,str]]=private.copy()
            for a in self.agents:
                if a.genome.revision_rounds>0 and a.genome.social_topology!="independent":
                    peers=[d for aid,(d,_) in private.items() if aid!=a.agent_id]
                    final[a.agent_id]=a.decide(snap,peers=peers,private_action=private[a.agent_id][0].action)
            rr=self.world.realized_return(snap.step,self.horizon)
            for a in self.agents:
                d,ctx_hash=final[a.agent_id]
                reward,regret,cal=score_decision(d,rr)
                rec=RunRecord(
                    run_id=sha256_id(self.world.world_id,a.agent_id,snap.step,a.genome.genome_id,ctx_hash,prefix="run_"),
                    world_id=self.world.world_id,seed=self.world.seed,agent_id=a.agent_id,
                    genome_id=a.genome.genome_id,step=snap.step,snapshot_id=snap.snapshot_id,
                    decision=d,realized_return=rr,reward=reward,regret=regret,context_hash=ctx_hash,
                    metadata={"calibration_error":cal,"regime":snap.packet.metadata.get("latent_regime")}
                )
                self.records.append(rec)
                a.memory.add(MemoryItem(
                    agent_id=a.agent_id,kind="decision_outcome",
                    text=f"regime={rec.metadata['regime']} action={d.action} expected={d.expected_return:.4f} realized={rr:.4f}; rationale={d.rationale}",
                    score=reward,step=snap.step,
                    metadata={"snapshot_id":snap.snapshot_id,"genome_id":a.genome.genome_id,"regret":regret}
                ))
        return self.records

    def results(self) -> list[BenchmarkResult]:
        out=[]
        for a in self.agents:
            rs=[r for r in self.records if r.agent_id==a.agent_id]
            if not rs: continue
            rewards=[r.reward for r in rs]
            cals=[r.metadata["calibration_error"] for r in rs]
            eq=0.0; peak=0.0; maxdd=0.0
            for x in rewards:
                eq += x; peak=max(peak,eq); maxdd=max(maxdd,peak-eq)
            # adaptation latency: mean steps after a latent-regime change until action sign agrees with realized next return
            regime_changes=[]
            for i in range(1,len(rs)):
                if rs[i].metadata["regime"]!=rs[i-1].metadata["regime"]: regime_changes.append(i)
            lats=[]
            for idx in regime_changes:
                lat=10.0
                for j in range(idx,min(len(rs),idx+10)):
                    a_sign={"LONG":1,"FLAT":0,"SHORT":-1}[rs[j].decision.action]
                    r_sign=1 if rs[j].realized_return>0 else -1 if rs[j].realized_return<0 else 0
                    if a_sign==r_sign: lat=float(j-idx); break
                lats.append(lat)
            rev=[r for r in rs if r.decision.private_action is not None]
            revision_gain=sum(r.reward for r in rev)/len(rev) if rev else 0.0
            out.append(BenchmarkResult(
                benchmark_id=sha256_id(self.world.world_id,a.genome.genome_id,prefix="bench_"),
                genome_id=a.genome.genome_id,episodes=len(rs),mean_reward=statistics.mean(rewards),
                downside_reward=statistics.mean(sorted(rewards)[:max(1,len(rewards)//5)]),
                calibration_error=statistics.mean(cals),max_drawdown=maxdd,
                adaptation_latency=statistics.mean(lats) if lats else 0.0,revision_gain=revision_gain,
                metadata={"agent_id":a.agent_id,"world_id":self.world.world_id}
            ))
        return out
