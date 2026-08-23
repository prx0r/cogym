from cogym.benchmark import make_world
from cogym.schema import AgentGenome
from cogym.memory import SQLiteMemory
from cogym.agent import CognitiveAgent, RuleBasedModel
from cogym.experiment import ExperimentRunner

def test_run_and_social_revision():
    w=make_world("regime_flip",7); mem=SQLiteMemory(":memory:")
    a=CognitiveAgent("a",AgentGenome(memory_policy="recent",memory_depth=2),RuleBasedModel(),mem)
    b=CognitiveAgent("b",AgentGenome(social_topology="all_to_all",reveal="decision_confidence",revision_rounds=1,memory_policy="failures_first",memory_depth=2),RuleBasedModel(),mem)
    r=ExperimentRunner(w,[a,b]); recs=r.run(start=24,end=32)
    assert len(recs)==18
    assert len(r.results())==2
    assert any(x.decision.private_action is not None for x in recs if x.agent_id=="b")
