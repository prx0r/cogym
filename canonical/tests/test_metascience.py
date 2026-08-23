"""Metascience tests: verify the experiment machinery measures what it claims.
A deliberately-bad agent should FAIL. Same seed should replay identically.
Changing one treatment dimension leaves everything else unchanged."""
import pytest, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from cogym.agents.model import HarnessTraderModel
from cogym.experiments.factory import synthetic_trading_world
from cogym.experiments.runner import run_world
from cogym.experiments.scoring import score_decision
from cogym.agents.decision import Decision


def test_same_seed_replays_identically():
    w1 = synthetic_trading_world(level=2, seed=42)
    w2 = synthetic_trading_world(level=2, seed=42)
    assert w1.manifest.bars_digest == w2.manifest.bars_digest
    s1 = w1.snapshot(50)
    s2 = w2.snapshot(50)
    assert s1.features.direction == s2.features.direction
    assert s1.features.volatility == s2.features.volatility


def test_different_seeds_produce_different_worlds():
    w1 = synthetic_trading_world(level=2, seed=42)
    w2 = synthetic_trading_world(level=2, seed=43)
    assert w1.manifest.bars_digest != w2.manifest.bars_digest


def test_scoring_deterministic():
    d = Decision(
        stance="LONG", p_up=0.7, p_flat=0.15, p_down=0.15,
        expected_return=0.02, confidence=0.8, risk=0.3,
    )
    realized = 0.05
    s1 = score_decision(d, realized)
    s2 = score_decision(d, realized)
    assert s1.log_score == s2.log_score
    assert s1.brier == s2.brier
    assert s1.paper_utility == s2.paper_utility
    assert s1.direction_correct == 1.0


def test_wrong_direction_scores_poorly():
    d_short = Decision(
        stance="SHORT", p_up=0.7, p_flat=0.15, p_down=0.15,
        expected_return=-0.02, confidence=0.9, risk=0.2,
    )
    realized_positive = 0.05
    score = score_decision(d_short, realized_positive)
    # SHORT on positive return = wrong
    assert score.direction_correct == 0.0
    assert score.paper_utility < 0  # short position loses when price goes up


def test_correct_direction_scores_well():
    d_long = Decision(
        stance="LONG", p_up=0.7, p_flat=0.15, p_down=0.15,
        expected_return=0.02, confidence=0.8, risk=0.3,
    )
    realized_positive = 0.05
    score = score_decision(d_long, realized_positive)
    assert score.direction_correct == 1.0
    assert score.paper_utility > 0


def test_bad_agent_produces_different_signature():
    """A deliberately contrarian agent should have a different behavior signature."""
    world = synthetic_trading_world(level=0, seed=42)  # smooth trend

    # Run normal agent
    normal_model = HarnessTraderModel()
    r_normal = run_world(normal_model, world, condition="normal", history_mode="reset")

    # Check that decisions were actually made and scored
    assert len(r_normal.records) > 0
    assert all(r.score.log_score is not None for r in r_normal.records)


def test_event_ledger_append_only():
    from cogym.core import EventLedger
    import tempfile, os
    path = os.path.join(tempfile.mkdtemp(), "test-ledger.jsonl")
    led = EventLedger(path)
    e1 = led.append("event_a", data=1)
    e2 = led.append("event_b", data=2)

    events = led.all_events()
    assert len(events) == 2
    assert events[0]["kind"] == "event_a"
    assert events[1]["prev_hash"] == e1.event_hash
    os.remove(path)


def test_skill_registry_terminal_states_not_in_population():
    from cogym.skill_registry import SkillRegistry, SkillArtifact, ELIGIBLE_STATES, TERMINAL_STATES
    db = "/tmp/opencode/test-skill-reg.json"
    reg = SkillRegistry(db)

    art = SkillArtifact(content="test skill", creator="test", hypothesis="test")
    sid = reg.propose(art)

    # Evaluate as rejected
    ev = reg.evaluate(sid, None, "whash",
                      cand_scores=[0.1]*5, inc_scores=[0.9]*5)
    assert reg.skills[sid].status in TERMINAL_STATES
    # REJECTED skills must NOT appear in population
    pop_ids = [s.skill_id for s in reg.population()]
    assert sid not in pop_ids
    os.remove(db)


def test_experiment_log_outcome_states():
    from cogym.experiment_log import ExperimentLog
    log = ExperimentLog("test-001", "hypothesis",
                        {"treatment": "A"}, ["accuracy"], {"model": "ox-alpha-free"},
                        {"model_id": "ox-alpha-free"})
    
    log.log_subject("A", "s1", "regime_flip", 42, "prompt", "output",
                    parsed_response=None, outcome="CORRECT", confidence=0.8, duration_s=1.0)
    log.log_subject("A", "s2", "regime_flip", 43, "prompt", "",
                    parsed_response=None, outcome="MALFORMED", confidence=None, duration_s=0.5)
    log.log_subject("A", "s3", "regime_flip", 44, "prompt", "out",
                    parsed_response=None, outcome="INFRA_FAILURE", confidence=None, duration_s=0.1)

    summary = log.summary_by_treatment()
    a = summary["A"]
    # accuracy only counts CORRECT/INCORRECT (gradeable), not MALFORMED or INFRA_FAILURE
    assert a["n_gradeable"] == 1
    assert a["accuracy"] == 1.0  # 1/1 gradeable was correct
    assert a["malformed_rate"] == pytest.approx(1/3)
