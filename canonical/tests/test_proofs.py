from cogym.proofs.receipt import ExperimentReceipt, ModelExecutionClaim


def test_receipt_commits_claims():
    claim = ModelExecutionClaim("m", "in", "out")
    receipt = ExperimentReceipt("c", "w", "cond", "pack", (claim,), "r", "eval-v1")
    assert receipt.receipt_id
