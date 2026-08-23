from cogym.agents.model import HarnessTraderModel
from cogym.experiments.factory import synthetic_trading_world
from cogym.experiments.runner import run_world, summarize_repeats


def test_repeat_runner_records_distribution():
    m = HarnessTraderModel()
    w = synthetic_trading_world(2, 3)
    indices = [35, 55, 75, 95, 115]
    runs = [run_world(m, w, condition="x", indices=indices, sample_seed=s, temperature=0.5) for s in (1,2,3)]
    summary = summarize_repeats(runs, "x")
    assert len(summary.run_ids) == 3
    assert len(runs[0].records) == len(indices)
    assert summary.mean_signature.signature_id
