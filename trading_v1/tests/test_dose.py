from cogym.agents.model import HarnessTraderModel
from cogym.experiments.dose import pathway_dose_response
from cogym.experiments.factory import synthetic_trading_world
from cogym.state.pack import load_pack


def test_dose_runs_zero_to_full_pathway():
    model = HarnessTraderModel()
    world = synthetic_trading_world(4, 8)
    p = load_pack("packs/loss_salience_induction_v1.json").pathway
    rows = pathway_dose_response(model, world, p, repeats=2, indices=[35,65,95])
    assert [r.steps for r in rows] == [0,1,2,3]
