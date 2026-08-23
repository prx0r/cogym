from __future__ import annotations
from dataclasses import dataclass, asdict
import json, sqlite3
from pathlib import Path
from typing import Protocol, Any
from .utils import sha256_id

@dataclass
class MemoryItem:
    agent_id: str
    kind: str
    text: str
    score: float = 0.0
    step: int = 0
    metadata: dict[str, Any] | None = None

class MemoryBackend(Protocol):
    def add(self, item: MemoryItem) -> str: ...
    def retrieve(self, agent_id: str, query: str, limit: int = 5, policy: str = "recent") -> list[MemoryItem]: ...

class NullMemory:
    def add(self, item: MemoryItem) -> str:
        return sha256_id(asdict(item), prefix="mem_")
    def retrieve(self, agent_id: str, query: str, limit: int = 5, policy: str = "recent") -> list[MemoryItem]:
        return []

class SQLiteMemory:
    """Fully local episodic memory used by the benchmark and as a Hydra-compatible boundary.

    World truth never lives here; only agent experience does.
    """
    def __init__(self, path: str | Path = ":memory:"):
        self.conn = sqlite3.connect(str(path))
        self.conn.execute("""CREATE TABLE IF NOT EXISTS memories(
            id TEXT PRIMARY KEY, agent_id TEXT, kind TEXT, text TEXT, score REAL,
            step INTEGER, metadata TEXT
        )""")
        self.conn.commit()

    def add(self, item: MemoryItem) -> str:
        mid = sha256_id(asdict(item), prefix="mem_")
        self.conn.execute("INSERT OR REPLACE INTO memories VALUES(?,?,?,?,?,?,?)", (
            mid, item.agent_id, item.kind, item.text, item.score, item.step,
            json.dumps(item.metadata or {}, sort_keys=True)))
        self.conn.commit()
        return mid

    def retrieve(self, agent_id: str, query: str, limit: int = 5, policy: str = "recent") -> list[MemoryItem]:
        if policy == "failures_first":
            order = "score ASC, step DESC"
        elif policy == "successes_first":
            order = "score DESC, step DESC"
        else:
            order = "step DESC"
        rows = self.conn.execute(
            f"SELECT agent_id,kind,text,score,step,metadata FROM memories WHERE agent_id=? ORDER BY {order} LIMIT ?",
            (agent_id, limit)).fetchall()
        return [MemoryItem(r[0],r[1],r[2],r[3],r[4],json.loads(r[5])) for r in rows]

    def export_hydra_jsonl(self, path: str | Path) -> Path:
        """Export experience items as JSONL ready for ingestion by an external HydraDB sync job.

        This deliberately avoids inventing Hydra API credentials/endpoints in core benchmark code.
        """
        p = Path(path)
        rows = self.conn.execute("SELECT id,agent_id,kind,text,score,step,metadata FROM memories ORDER BY step").fetchall()
        with p.open("w") as f:
            for r in rows:
                payload = {
                    "id": r[0], "agent_id": r[1], "kind": r[2], "text": r[3],
                    "score": r[4], "step": r[5], "metadata": json.loads(r[6]),
                    "hydra_metadata": {"kind": r[2], "agent": r[1], "step": r[5]}
                }
                f.write(json.dumps(payload, sort_keys=True)+"\n")
        return p
