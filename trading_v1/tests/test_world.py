from cogym.experiments.factory import synthetic_trading_world


def test_synthetic_world_replays_exactly():
    a = synthetic_trading_world(6, 91)
    b = synthetic_trading_world(6, 91)
    c = synthetic_trading_world(6, 92)
    assert a.manifest.world_id == b.manifest.world_id
    assert a.bars == b.bars
    assert a.manifest.world_id != c.manifest.world_id
    assert a.bars != c.bars
