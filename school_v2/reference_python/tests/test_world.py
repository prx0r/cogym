from cogym.world import WorldSpec, SyntheticMarketWorld, RegimeSegment

def test_deterministic_world():
    s=WorldSpec()
    a=SyntheticMarketWorld(s,123); b=SyntheticMarketWorld(s,123)
    assert a.snapshot(30).snapshot_id==b.snapshot(30).snapshot_id
    assert a.realized_return(30,5)==b.realized_return(30,5)

def test_fork_preserves_prefix():
    a=SyntheticMarketWorld(WorldSpec(),1)
    f=a.fork(40,9,(RegimeSegment(30,0.002,0.01,label="x"),))
    assert a._prices[:41]==f._prices[:41]
    assert a.snapshot(40).packet.price==f.snapshot(40).packet.price
