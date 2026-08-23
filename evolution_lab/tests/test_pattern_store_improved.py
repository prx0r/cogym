"""Regression: record_result must write computed `improved`, not mean_reward>0."""
import os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from cogym.pattern_store import PatternStore

def test_improved_uses_control_not_zero():
    db = tempfile.mktemp(suffix=".db")
    ps = PatternStore(db)
    # reward positive BUT below matched control => must be improved=0
    ps.record_result("p1", "wf", 1, "treat", mean_reward=0.5, control_mean_reward=0.9)
    row = ps.conn.execute("SELECT improved FROM pattern_world_results WHERE pattern_id='p1'").fetchone()
    assert row[0] == 0, f"expected improved=0 (below control), got {row[0]}"
    # negative reward with no control (control defaults to 0) => not improved
    ps.record_result("p2", "wf", 2, "treat", mean_reward=-0.1)
    row = ps.conn.execute("SELECT improved FROM pattern_world_results WHERE pattern_id='p2'").fetchone()
    assert row[0] == 0
    # beats control => improved
    ps.record_result("p3", "wf", 3, "treat", mean_reward=0.7, control_mean_reward=0.4)
    row = ps.conn.execute("SELECT improved FROM pattern_world_results WHERE pattern_id='p3'").fetchone()
    assert row[0] == 1
    os.remove(db)
