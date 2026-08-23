from cogym.culture.store import EvidenceGraph


def test_evidence_graph(tmp_path):
    g = EvidenceGraph(tmp_path / "g.sqlite")
    event = g.append_event("run", {"x": 1})
    g.upsert_node("agent", "a", {"name": "A"})
    g.upsert_node("pack", "p", {"name": "P"})
    edge = g.link("a", "used", "p", event)
    assert event and edge
    assert len(g.events("run")) == 1
    p = g.export_jsonl(tmp_path / "events.jsonl")
    assert p.exists()
    g.close()
