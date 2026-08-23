from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from ..canonical import canonical_json, commitment


class EvidenceGraph:
    """Small local append-oriented graph for evidence-bearing Cogym culture.

    This is the authoritative local experiment store. HydraDB is an optional projection target,
    not required for deterministic execution.
    """
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS events(
              event_id TEXT PRIMARY KEY,
              kind TEXT NOT NULL,
              payload_json TEXT NOT NULL,
              created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS nodes(
              node_id TEXT PRIMARY KEY,
              kind TEXT NOT NULL,
              payload_json TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS edges(
              edge_id TEXT PRIMARY KEY,
              src TEXT NOT NULL,
              predicate TEXT NOT NULL,
              dst TEXT NOT NULL,
              evidence_event_id TEXT,
              FOREIGN KEY(evidence_event_id) REFERENCES events(event_id)
            );
            """
        )
        self.db.commit()

    def append_event(self, kind: str, payload: Any) -> str:
        if is_dataclass(payload):
            payload = asdict(payload)
        event_id = commitment("COGYM:EVENT:v1", kind, payload)
        self.db.execute("INSERT OR IGNORE INTO events(event_id,kind,payload_json) VALUES(?,?,?)", (event_id, kind, canonical_json(payload)))
        self.db.commit()
        return event_id

    def upsert_node(self, kind: str, node_id: str, payload: Any) -> str:
        if is_dataclass(payload):
            payload = asdict(payload)
        self.db.execute(
            "INSERT INTO nodes(node_id,kind,payload_json) VALUES(?,?,?) ON CONFLICT(node_id) DO UPDATE SET kind=excluded.kind,payload_json=excluded.payload_json",
            (node_id, kind, canonical_json(payload)),
        )
        self.db.commit()
        return node_id

    def link(self, src: str, predicate: str, dst: str, evidence_event_id: str | None = None) -> str:
        edge_id = commitment("COGYM:EDGE:v1", src, predicate, dst, evidence_event_id or "")
        self.db.execute("INSERT OR IGNORE INTO edges(edge_id,src,predicate,dst,evidence_event_id) VALUES(?,?,?,?,?)", (edge_id, src, predicate, dst, evidence_event_id))
        self.db.commit()
        return edge_id

    def events(self, kind: str | None = None) -> list[dict]:
        cur = self.db.execute("SELECT event_id,kind,payload_json,created_at FROM events" + (" WHERE kind=?" if kind else "") + " ORDER BY rowid", ((kind,) if kind else ()))
        return [{"event_id": a, "kind": b, "payload": json.loads(c), "created_at": d} for a, b, c, d in cur]

    def export_jsonl(self, path: str | Path) -> Path:
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as f:
            for event in self.events():
                f.write(json.dumps(event, sort_keys=True) + "\n")
        return out

    def close(self) -> None:
        self.db.close()
