from __future__ import annotations
from dataclasses import replace
from .world import WorldSpec, RegimeSegment, SyntheticMarketWorld

WORLD_SUITE={
 "smooth_bull": WorldSpec(segments=(RegimeSegment(220,0.0008,0.006,label="bull"),),difficulty=2),
 "smooth_bear": WorldSpec(segments=(RegimeSegment(220,-0.0008,0.006,label="bear"),),difficulty=2),
 "regime_flip": WorldSpec(segments=(RegimeSegment(100,0.001,0.008,label="bull"),RegimeSegment(120,-0.0012,0.012,label="bear")),difficulty=5),
 "chop_trap": WorldSpec(segments=(RegimeSegment(220,0,0.018,mean_reversion=0.22,label="chop"),),difficulty=6),
 "shock_then_recover": WorldSpec(segments=(RegimeSegment(80,0.0005,0.007,label="calm"),RegimeSegment(30,-0.001,0.03,label="shock",shock_prob=.12,shock_scale=.08),RegimeSegment(110,0.001,0.012,label="recovery")),difficulty=8),
 "pattern_break": WorldSpec(segments=(RegimeSegment(80,0.0012,0.006,label="momentum"),RegimeSegment(80,0.0012,0.006,label="momentum"),RegimeSegment(80,0,0.016,mean_reversion=.3,label="broken_pattern")),difficulty=9),
}

def make_world(name:str,seed:int)->SyntheticMarketWorld:
    return SyntheticMarketWorld(WORLD_SUITE[name],seed)
