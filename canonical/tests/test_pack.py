from pathlib import Path
import pytest

from cogym.state.pack import PackManifest, load_pack


def test_candidate_packs_load():
    root = Path(__file__).resolve().parents[1] / "packs"
    packs = [load_pack(p) for p in root.glob("*.json")]
    assert len(packs) >= 6
    assert all(p.pack_id for p in packs)
    assert all(p.status == "candidate" for p in packs)


def test_certified_pack_requires_evidence():
    p = load_pack(Path(__file__).resolve().parents[1] / "packs" / "trading_regime_shift_v1.json")
    with pytest.raises(ValueError):
        PackManifest(p.name, p.version, p.kind, "certified", p.purpose, pathway=p.pathway)
