from cogym.agents.model import HarnessTraderModel
from cogym.experiments.dose import pathway_dose_response
from cogym.experiments.factory import synthetic_trading_world
from cogym.state.pack import load_pack

model = HarnessTraderModel()
world = synthetic_trading_world(4, 99)
pathway = load_pack("packs/loss_salience_induction_v1.json").pathway
for row in pathway_dose_response(model, world, pathway, repeats=3, indices=[35,65,95,125,155]):
    print(row.steps, row.summary.mean_log_score, row.summary.mean_signature)
