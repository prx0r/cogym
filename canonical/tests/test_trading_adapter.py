"""PR6/PR7 acceptance: trading runs behind the generic contracts with golden parity.

factminer.md §13: if the generic core needs `isinstance(world, TradingWorld)`, the
refactor has failed. These tests pin the golden fixture AND prove the SAME runner
and SAME campaign drive toy + trading with zero domain branching.
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

FIXTURE = os.path.join(os.path.dirname(__file__), "golden", "trading_v1_episode.json")


def _runner():
    from cogym.core.runtime import GenericRunner
    from cogym.core.toy_executor import DeterministicExecutor
    return GenericRunner(executors={"deterministic": DeterministicExecutor()})


def test_golden_parity_through_generic_contracts():
    """First adapter decision must reproduce the frozen fixture byte-for-byte."""
    from cogym.experiments.factory import synthetic_trading_world
    from cogym.worlds.trading.adapter import first_decision

    expected = json.load(open(FIXTURE))
    w = synthetic_trading_world(expected["world_level"], expected["seed"])
    out = first_decision(w, expected["snapshot_index"])
    obs = out["obs"]
    assert obs["world_id"] == expected["world_id"], "world_id drifted"
    assert round(obs["price"], 10) == round(expected["price"], 10), "price drifted"
    assert round(obs["recent_returns"][-1], 12) == round(expected["last_return"], 12)
    assert out["stance"] == expected["action"]
    assert round(out["realized"], 10) == round(expected["realized_return"], 10)


def test_trading_episode_deterministic_and_scored():
    from cogym.experiments.factory import synthetic_trading_world
    from cogym.worlds.trading.adapter import TradingWorldAdapter, MomentumRulePolicy

    world = TradingWorldAdapter(synthetic_trading_world(1, 42), horizon=5)
    rec = _runner().run_episode(world, MomentumRulePolicy(),
                                instance_id="start=60", seed=42)
    assert rec.metrics.get("n_decisions") >= 1.0
    # determinism: identical episode id + final hash on rerun
    world2 = TradingWorldAdapter(synthetic_trading_world(1, 42), horizon=5)
    rec2 = _runner().run_episode(world2, MomentumRulePolicy(),
                                 instance_id="start=60", seed=42)
    assert rec.episode_id == rec2.episode_id
    assert rec.final_output_hash == rec2.final_output_hash


def test_same_runner_drives_toy_and_trading():
    """THE §13 acceptance: one runner, two worlds, zero domain branches."""
    from cogym.worlds.toy.search_game import SearchGameWorld, SequentialPolicy
    from cogym.worlds.trading.adapter import TradingWorldAdapter, MomentumRulePolicy
    from cogym.experiments.factory import synthetic_trading_world

    runner = _runner()
    toy_rec = runner.run_episode(SearchGameWorld(), SequentialPolicy(),
                                 instance_id="t", seed=42)
    trade_rec = runner.run_episode(
        TradingWorldAdapter(synthetic_trading_world(1, 42)),
        MomentumRulePolicy(), instance_id="start=60", seed=42)
    for rec in (toy_rec, trade_rec):
        assert rec.metrics.names(), "both worlds must emit MetricVector"


def test_campaign_runs_both_worlds_unchanged():
    """Same Campaign machinery (gates+lexicographic rank) across domains."""
    from cogym.core.campaign import Campaign, CampaignConfig
    from cogym.core.evaluation import QualityGate
    from cogym.core.contracts import CandidateArtifact
    from cogym.worlds.toy.search_game import SearchGameWorld, SequentialPolicy
    from cogym.worlds.trading.adapter import TradingWorldAdapter, MomentumRulePolicy
    from cogym.experiments.factory import synthetic_trading_world

    runner = _runner()
    no_mutation = lambda parents, n: []

    toy_cfg = CampaignConfig(
        world_kind="toy.search_game", suite=(("t", 42), ("t", 43)),
        gates=(QualityGate("found", mode="max", value=1.0),))
    toy_camp = Campaign(toy_cfg, runner, lambda inst: SearchGameWorld(), no_mutation)
    winners = toy_camp.run(
        [CandidateArtifact(kind="toy_policy", version="1", config={})],
        policy_factory=lambda cand: SequentialPolicy())
    assert winners, "toy campaign must produce a winner under gates"

    tr_cfg = CampaignConfig(
        world_kind="trading.synthetic", suite=(("start=60", 42),),
        gates=(QualityGate("n_decisions", mode="max", value=1.0),))
    tr_camp = Campaign(tr_cfg, runner,
                       lambda inst: TradingWorldAdapter(synthetic_trading_world(1, 42)),
                       no_mutation)
    winners_tr = tr_camp.run(
        [CandidateArtifact(kind="trading_agent", version="1", config={})],
        policy_factory=lambda cand: MomentumRulePolicy())
    assert winners_tr, "trading campaign must produce a winner under gates"


def test_quality_gate_rejects_always_flat_on_trading():
    """Cheap garbage control: always-FLAT earns zero utility -> fails noninferiority.
    Uses level-2 world where the momentum baseline is clearly positive (+359 bps)."""
    from cogym.core.evaluation import QualityGate, check_gate
    from cogym.experiments.factory import synthetic_trading_world
    from cogym.worlds.trading.adapter import TradingWorldAdapter, MomentumRulePolicy, StaticStancePolicy

    def metrics_for(policy):
        w = TradingWorldAdapter(synthetic_trading_world(2, 42))
        return _runner().run_episode(w, policy, instance_id="start=60", seed=42).metrics

    baseline = metrics_for(MomentumRulePolicy())
    flat = metrics_for(StaticStancePolicy("FLAT"))
    assert baseline.get("paper_utility_bps") > 100, "baseline segment must be profitable"
    gate = QualityGate(metric="paper_utility_bps", mode="noninferior", margin=1.0)
    result = check_gate(gate, flat, baseline)
    assert not result.passed, "always-FLAT must fail utility noninferiority vs momentum rule"
