from cogym.agents.model import HarnessTraderModel
from cogym.experiments.factory import synthetic_trading_world
from cogym.experiments.transfer import run_abcdef
from cogym.state.pack import load_pack


def test_abcdef_has_all_conditions_and_fidelity_metrics():
    m = HarnessTraderModel()
    w = synthetic_trading_world(3, 42)
    p = load_pack("packs/trading_regime_shift_v1.json").pathway
    report = run_abcdef(m, w, p, repeats=3, indices=[35, 55, 75, 95])
    assert [x.label for x in report.conditions] == list("ABCDEF")
    assert set(report.decision_fidelity) == set("ABCDEF")
    assert report.decision_fidelity["A"] == 1.0
    assert report.experiment_id
