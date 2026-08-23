"""Golden fixture: generic refactor must reproduce this byte-identical episode."""
import json, os
import pytest

FIXTURE = os.path.join(os.path.dirname(__file__), "golden", "trading_v1_episode.json")

@pytest.mark.skipif(not os.path.exists(FIXTURE), reason="golden fixture missing")
def test_trading_golden_episode():
    from cogym.experiments.factory import synthetic_trading_world
    expected = json.load(open(FIXTURE))
    w = synthetic_trading_world(level=expected["world_level"], seed=expected["seed"])
    obs = w.snapshot(expected["snapshot_index"], lookback=25)
    last_ret = obs.recent_returns[-1] if obs.recent_returns else 0
    action = "LONG" if last_ret > 0 else "FLAT"
    realized = w.realized_return(expected["snapshot_index"], 5)
    assert obs.metadata["world_id"] == expected["world_id"], "world_id drifted"
    assert round(obs.price, 10) == round(expected["price"], 10), "price drifted"
    assert round(last_ret, 12) == round(expected["last_return"], 12), "return drifted"
    assert action == expected["action"]
    assert round(realized, 10) == round(expected["realized_return"], 10)
