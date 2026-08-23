from cogym.agents.model import HarnessTraderModel
from cogym.experiments.contagion import run_state_contagion
from cogym.experiments.factory import synthetic_trading_world
from cogym.experiments.persistence import run_persistence_matrix
from cogym.experiments.team import run_team
from cogym.experiments.treatments import run_treatment_matrix
from cogym.state.pack import load_pack


def test_treatment_persistence_team_and_contagion_execute():
    m = HarnessTraderModel()
    w = synthetic_trading_world(3, 88)
    indices = [35,65,95]
    treatments = run_treatment_matrix(m, w, repeats=2, indices=indices)
    assert set(treatments) == {"neutral","supportive","critical","urgency"}
    p = load_pack("packs/trading_regime_shift_v1.json").pathway
    pm = run_persistence_matrix(m, w, p, repeats=2, indices=indices)
    assert pm.reset.run_ids and pm.persistent.run_ids
    team = run_team([m,m], w.snapshot(100), horizon_steps=5, seed=5)
    assert len(team.private_decisions) == 2
    cont = run_state_contagion(m, m, p, rounds=2, seed=7)
    assert cont.rounds == 2
