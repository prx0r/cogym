"""PR4+PR7 acceptance: generic campaign on toy world + tape replay determinism."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def _make_world(inst):
    from cogym.worlds.toy.search_game import SearchGameWorld
    return SearchGameWorld()

def _policy_for(cand):
    from cogym.worlds.toy.search_game import SequentialPolicy, BinarySearchStylePolicy
    return SequentialPolicy() if cand.config["probe"] == "seq" else BinarySearchStylePolicy()

def test_tape_replay_deterministic():
    from cogym.core.campaign import ReplayTape, RecordingExecutor, TapeExecutor
    from cogym.core.toy_executor import DeterministicExecutor
    from cogym.core.contracts import ActionSpec
    tape = ReplayTape()
    live = RecordingExecutor(DeterministicExecutor(), tape)
    a1 = ActionSpec(kind="PROBE", payload={"box": 3}, estimated_cost=0.01)
    r_live = live.execute(a1)
    assert len(tape) == 1
    replay = TapeExecutor(tape).execute(a1)
    assert replay.receipt_hash == r_live.receipt_hash
    # unknown action must ERROR, never silently go live
    bogus = ActionSpec(kind="PROBE", payload={"box": 99})
    r_bad = TapeExecutor(ReplayTape()).execute(bogus)
    assert r_bad.status == "error"

def test_generic_campaign_runs_toy_world():
    from cogym.core.campaign import Campaign, CampaignConfig, EvaluatedCandidate, aggregate
    from cogym.core.runtime import GenericRunner
    from cogym.core.toy_executor import DeterministicExecutor
    from cogym.core.contracts import CandidateArtifact
    from cogym.core.evaluation import QualityGate

    runner = GenericRunner(executors={"deterministic": DeterministicExecutor()})
    cfg = CampaignConfig(
        world_kind="toy.search_game",
        suite=tuple((f"inst{i}", 42 + i) for i in range(3)),
        gates=(QualityGate(metric="found", mode="min", value=1.0),),
        generations=2, population=4, elite_k=1)
    seeds = [CandidateArtifact(kind="toy_policy", version=str(i),
                               config={"probe": "seq" if i % 2 == 0 else "bin"})
             for i in range(4)]
    camp = Campaign(cfg, runner, _make_world,
                    propose_fn=lambda parents, n: seeds[:n])
    winners = camp.run(seeds, _policy_for)
    assert winners, "campaign must produce at least one gate-passing winner"
    assert all(w.kind == "toy_policy" for w in winners)

def test_gate_blocks_never_passes_dead_population():
    """Fail-closed: impossible quality gate kills the campaign (no silent promotion)."""
    from cogym.core.campaign import Campaign, CampaignConfig
    from cogym.core.runtime import GenericRunner
    from cogym.core.toy_executor import DeterministicExecutor
    from cogym.core.contracts import CandidateArtifact
    from cogym.core.evaluation import QualityGate
    runner = GenericRunner(executors={"deterministic": DeterministicExecutor()})
    cfg = CampaignConfig(world_kind="toy.search_game",
                         suite=(("i", 1),),
                         gates=(QualityGate(metric="probes", mode="min", value=0.5),),
                         generations=3, population=2, elite_k=1)
    seeds = [CandidateArtifact(kind="t", version="0", config={"probe": "seq"})]
    camp = Campaign(cfg, runner, _make_world, propose_fn=lambda p, n: [])
    assert camp.run(seeds, _policy_for) == [], "impossible gate must yield zero winners"
