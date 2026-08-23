from cogym.experiments.composition import compose
from cogym.state.pack import load_pack


def test_pathway_composition_orders_are_distinct():
    a = load_pack("packs/trading_regime_shift_v1.json").pathway
    b = load_pack("packs/trading_falsification_v1.json").pathway
    ab = compose(a,b,mode="a_then_b")
    ba = compose(a,b,mode="b_then_a")
    inter = compose(a,b,mode="interleave")
    assert ab.pathway_id != ba.pathway_id
    assert inter.pathway_id not in {ab.pathway_id, ba.pathway_id}
