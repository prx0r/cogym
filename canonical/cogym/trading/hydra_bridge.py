"""HydraDB bridge: projects validated experiment results into the knowledge graph.
SQLite PatternStore remains canonical. HydraDB is derived, never source of truth."""
from __future__ import annotations
import json

def project_pattern(pattern_id: str, name: str, description: str,
                    world_family: str, mean_utility: float,
                    improved: bool, treatment: str) -> dict:
    """Format a pattern for HydraDB ingestion via Bolt/OpenCypher."""
    return {
        "node": {
            "label": "ReasoningPattern",
            "props": {
                "pattern_id": pattern_id,
                "name": name,
                "description": description,
                "discovered_from": treatment,
            }
        },
        "edges": [
            {
                "type": "IMPROVED_ON" if improved else "REGRESSED_ON",
                "target_label": "WorldFamily",
                "target_props": {"name": world_family},
                "properties": {"mean_utility": round(mean_utility, 6)},
            }
        ]
    }

def project_skill_lineage(skill_id: str, parent_ids: list[str],
                          status: str, domain: str) -> dict:
    return {
        "node": {
            "label": "Skill",
            "props": {"skill_id": skill_id, "status": status, "domain": domain}
        },
        "edges": [
            {"type": "DESCENDED_FROM", "target_id": pid}
            for pid in parent_ids
        ]
    }

def export_hydra_ready(patterns: list[dict], skills: list[dict]) -> dict:
    """Full export bundle ready for batch insertion into HydraDB."""
    return {
        "patterns": patterns,
        "skills": skills,
        "format_version": "hydra_cogym_v1",
        "note": "SQLite is canonical. HydraDB is derived projection only."
    }
