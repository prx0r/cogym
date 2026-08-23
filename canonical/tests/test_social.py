from cogym.agents.model import HarnessTraderModel
from cogym.experiments.factory import synthetic_trading_world
from cogym.experiments.social import run_social_round


def test_social_round_preserves_private_and_revised():
    world = synthetic_trading_world(3, 5)
    agents = {"a": HarnessTraderModel(), "b": HarnessTraderModel(), "c": HarnessTraderModel()}
    rows = run_social_round(agents, world.snapshot(100), horizon_steps=5, seed=3)
    assert len(rows) == 3
    assert all(r.private.stance in {"LONG","FLAT","SHORT"} for r in rows)
    assert all(r.revised.stance in {"LONG","FLAT","SHORT"} for r in rows)
