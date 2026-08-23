from cogym.agents.model import HarnessTraderModel
from cogym.state.pathway import ContextPathway, PathwayStep, run_live_pathway


def test_pathway_checkpoint_replay_artifact_is_stable():
    p = ContextPathway("x", (PathwayStep("1", "first"), PathwayStep("2", "second")))
    m = HarnessTraderModel()
    a = run_live_pathway(p, m, seed=4)
    b = run_live_pathway(p, m, seed=4)
    assert a.checkpoint_id == b.checkpoint_id
    assert len(a.messages) == 4
