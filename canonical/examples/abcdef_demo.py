from cogym.agents.model import HarnessTraderModel
from cogym.experiments.factory import synthetic_trading_world
from cogym.experiments.transfer import run_abcdef
from cogym.state.pack import load_pack

model = HarnessTraderModel()
world = synthetic_trading_world(3, 4242)
pack = load_pack("packs/trading_regime_shift_v1.json")
report = run_abcdef(model, world, pack.pathway, repeats=3, indices=[35,55,75,95,115,135,155])
print(report.experiment_id)
print("decision fidelity", report.decision_fidelity)
print("behavior distance", report.behavior_distance)
print("artifact similarity", report.artifact_similarity)
