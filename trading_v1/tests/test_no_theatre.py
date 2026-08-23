from pathlib import Path


def test_no_old_fake_induction_helpers():
    root = Path(__file__).resolve().parents[1] / "cogym"
    text = "\n".join(p.read_text(errors="ignore") for p in root.rglob("*.py"))
    assert "fake_signature" not in text
    assert "induction_converges" not in text
    assert "consciousness_score" not in text
