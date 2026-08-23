"""Reasoning-pattern store. SQLite now, HydraDB-ready schema.
Stores which reasoning patterns work, on which worlds, from which treatments."""
from __future__ import annotations
import sqlite3, json, time, os

SCHEMA = """
CREATE TABLE IF NOT EXISTS reasoning_patterns (
    pattern_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    discovered_from TEXT,           -- hermes | manual | evolved
    first_seen TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS pattern_world_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id TEXT NOT NULL,
    world_family TEXT NOT NULL,
    world_seed INTEGER NOT NULL,
    treatment TEXT NOT NULL,
    mean_reward REAL,
    calibration_error REAL,
    adaptation_latency REAL,
    improved INTEGER,
    recorded_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS skill_pattern_links (
    skill_id TEXT NOT NULL,
    pattern_id TEXT NOT NULL,
    link_type TEXT NOT NULL DEFAULT 'INDUCES',
    evidence_hash TEXT,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_pwr ON pattern_world_results(pattern_id, world_family);
"""

class PatternStore:
    def __init__(self, path: str = "data/patterns.db"):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.executescript(SCHEMA)

    def record_pattern(self, name: str, description: str = "",
                       discovered_from: str = "hermes") -> str:
        pid = f"pat_{hashlib.md5(name.encode()).hexdigest()[:12]}"
        self.conn.execute(
            "INSERT OR IGNORE INTO reasoning_patterns VALUES (?,?,?,?,?)",
            (pid, name, description, discovered_from, time.strftime("%Y-%m-%dT%H:%M:%SZ")))
        self.conn.commit()
        return pid

    def record_result(self, pattern_id: str, world_family: str, world_seed: int,
                      treatment: str, mean_reward: float,
                      control_mean_reward: float | None = None,
                      calibration_error: float = 0.0,
                      adaptation_latency: float = 0.0):
        """improved = better than matched control on same world, not just > 0."""
        improved = (mean_reward > (control_mean_reward if control_mean_reward is not None else 0))
        self.conn.execute(
            "INSERT INTO pattern_world_results VALUES (NULL,?,?,?,?,?,?,?,?,?)",
            (pattern_id, world_family, world_seed, treatment, mean_reward,
             calibration_error, adaptation_latency,
             int(improved), time.strftime("%Y-%m-%dT%H:%M:%SZ")))
        self.conn.commit()

    def best_patterns_for(self, world_family: str, limit: int = 5) -> list:
        return self.conn.execute("""
            SELECT rp.name, AVG(pwr.mean_reward) as avg_r, COUNT(*) as n
            FROM reasoning_patterns rp
            JOIN pattern_world_results pwr ON rp.pattern_id = pwr.pattern_id
            WHERE pwr.world_family = ? AND pwr.improved = 1
            GROUP BY rp.pattern_id ORDER BY avg_r DESC LIMIT ?
        """, (world_family, limit)).fetchall()

    def export_hydra_ready(self) -> list[dict]:
        """Export in a format ready for HydraDB ingestion when it matures."""
        nodes = []
        edges = []
        for row in self.conn.execute("SELECT * FROM reasoning_patterns"):
            nodes.append({"label": "ReasoningPattern", "props": dict(zip(
                ["pattern_id","name","description","discovered_from","first_seen"], row))})
        for row in self.conn.execute("""
            SELECT DISTINCT pwr.world_family FROM pattern_world_results pwr"""):
            nodes.append({"label": "WorldFamily", "props": {"name": row[0]}})
        for row in self.conn.execute("""
            SELECT pattern_id, world_family,
                   CASE WHEN AVG(mean_reward) > 0 THEN 'IMPROVES' ELSE 'REGRESSES_ON' END as rel
            FROM pattern_world_results GROUP BY pattern_id, world_family"""):
            edges.append({"from": row[0], "to": row[1], "type": row[2]})
        return {"nodes": nodes, "edges": edges}

import hashlib  # used by record_pattern
