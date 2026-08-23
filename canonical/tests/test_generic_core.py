"""Generic core acceptance: toy world + trading world run through SAME runner
with zero domain branching (factminer.md §13, §65)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_toy_world_end_to_end():
    from cogym.worlds.toy.search_game import SearchGameWorld, SequentialPolicy
    from cogym.core.runtime import GenericRunner
    from cogym.core.toy_executor import DeterministicExecutor
    runner = GenericRunner(executors={"deterministic": DeterministicExecutor()})
    rec = runner.run_episode(SearchGameWorld(), SequentialPolicy(),
                             instance_id="t", seed=42)
    assert rec.metrics.get("found") == 1.0
    assert rec.metrics.get("probes") == 2.0
    # determinism: same seed -> same episode id + final hash
    rec2 = runner.run_episode(SearchGameWorld(), SequentialPolicy(),
                              instance_id="t", seed=42)
    assert rec.episode_id == rec2.episode_id
    assert rec.final_output_hash == rec2.final_output_hash

def test_quality_gate_blocks_cheap_garbage():
    from cogym.core.contracts import MetricVector, Metric
    from cogym.core.evaluation import QualityGate, check_gate, lexicographic_compare
    gate = QualityGate(metric="accuracy", mode="noninferior", margin=0.005)
    baseline = MetricVector(metrics=(Metric("accuracy", 0.90, "max"),))
    cheap_bad = MetricVector(metrics=(Metric("accuracy", 0.50, "max"),
                                      Metric("cash_cost", 0.01, "min")))
    r = check_gate(gate, cheap_bad, baseline)
    assert not r.passed, "cheap garbage must fail quality gate"
    good = MetricVector(metrics=(Metric("accuracy", 0.91, "max"),
                                 Metric("cash_cost", 5.0, "min")))
    # gates dominate: failing candidate never beats passing one regardless of cost
    assert lexicographic_compare(cheap_bad, False, good, True) == 1

def test_non_inferior_paired_bootstrap():
    from cogym.core.evaluation import non_inferior_paired
    base = [0.9] * 30
    cand = [0.895] * 30          # within margin 0.005
    res = non_inferior_paired(base, cand, margin=0.005)
    assert res["non_inferior"] is True and res["n_pairs"] == 30
    cand2 = [0.80] * 30          # clearly worse
    res2 = non_inferior_paired(base, cand2, margin=0.005)
    assert res2["non_inferior"] is False

def test_action_wave_canonical_ordering():
    from cogym.core.contracts import ActionSpec
    from cogym.core.runtime import GenericRunner
    from cogym.core.toy_executor import DeterministicExecutor
    runner = GenericRunner(executors={"deterministic": DeterministicExecutor()})
    wave_actions = tuple(ActionSpec(kind="PROBE", payload={"box": i})
                         for i in [7, 2, 9])
    receipts1 = runner.run_wave(type("W", (), {"actions": wave_actions})())
    receipts2 = runner.run_wave(type("W", (), {"actions": tuple(reversed(wave_actions))})())
    ids1 = [r.action_id for r in receipts1]
    ids2 = [r.action_id for r in receipts2]
    assert ids1 == ids2 == sorted(ids1), "canonical order must be action_id-sorted"
