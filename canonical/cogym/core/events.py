"""Append-only event ledger. Never rewrite history: new interpretations are new
events. Every event is content-hashed and chained to the previous hash."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
import json, os, time
from ..utils import sha256_id

@dataclass(frozen=True)
class Event:
    kind: str                      # campaign_created | candidate_proposed | ...
    payload: dict                  # facts only
    ts: float = field(default_factory=lambda: time.time())
    prev_hash: str = "0"*64
    event_hash: str = ""

    def __post_init__(self):
        if not self.event_hash:
            object.__setattr__(self, "event_hash",
                sha256_id({"kind": self.kind, "payload": self.payload,
                           "ts": self.ts, "prev": self.prev_hash}, prefix="ev_"))

class EventLedger:
    """Append-only JSONL ledger per campaign/experiment."""
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self._prev = self._last_hash()

    def _last_hash(self) -> str:
        if not os.path.exists(self.path): return "0"*64
        last = None
        with open(self.path) as f:
            for line in f:
                last = line
        if not last: return "0"*64
        try: return json.loads(last)["event_hash"]
        except Exception: return "0"*64

    def append(self, kind: str, **payload) -> Event:
        ev = Event(kind=kind, payload=payload, prev_hash=self._prev)
        with open(self.path, "a") as f:
            f.write(json.dumps({**asdict(ev), "payload": payload}) + "\n")
        self._prev = ev.event_hash
        return ev

    def all_events(self) -> list[dict]:
        if not os.path.exists(self.path): return []
        return [json.loads(l) for l in open(self.path)]
