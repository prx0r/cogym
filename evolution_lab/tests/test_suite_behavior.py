from cogym.schema import AgentGenome
from cogym.agent import RuleBasedModel
from cogym.suite import BenchmarkSuite
from cogym.behavior import signature, distance
from cogym.benchmark import make_world
from cogym.memory import SQLiteMemory
from cogym.agent import CognitiveAgent
from cogym.experiment import ExperimentRunner

def test_suite_aggregates():
    s=BenchmarkSuite(worlds=["regime_flip"],seeds=[1,2])
    agg,parts=s.evaluate(AgentGenome(),RuleBasedModel,end=35)
    assert len(parts)==2 and agg.episodes==sum(x.episodes for x in parts)

def test_behavior_signature_stable_for_deterministic_model():
    g=AgentGenome(); sigs=[]
    for _ in range(2):
        a=CognitiveAgent("a",g,RuleBasedModel(),SQLiteMemory(":memory:"))
        r=ExperimentRunner(make_world("regime_flip",5),[a]); recs=r.run(end=40)
        sigs.append(signature([x.decision for x in recs]))
    assert distance(sigs[0],sigs[1])==0
