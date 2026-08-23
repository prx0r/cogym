"""Full experiment logging: every agent run, every decision, every inference call.
Produces JSON files that are exact, reproducible records of what happened."""
from __future__ import annotations
import json, os, time, hashlib
from datetime import datetime, timezone

def utcnow(): return datetime.now(timezone.utc).isoformat()

def content_hash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()

class ExperimentLog:
    """One file per experiment. Every subject, every world, every output preserved."""
    
    def __init__(self, experiment_id: str, hypothesis: str,
                 independent_vars: dict, dependent_vars: list[str],
                 control_vars: dict, model_config: dict):
        self.experiment_id = experiment_id
        self.dir = f"/root/cogym/experiments/{experiment_id}"
        os.makedirs(self.dir, exist_ok=True)
        self.metadata = {
            "experiment_id": experiment_id,
            "hypothesis": hypothesis,
            "independent_variables": independent_vars,
            "dependent_variables": dependent_vars,
            "control_variables": control_vars,
            "model_config": model_config,
            "started_at": utcnow(),
            "status": "running",
            "runs": []
        }
        self._save_metadata()
    
    def log_subject(self, treatment: str, subject_name: str, world_family: str,
                    world_seed: int, prompt: str, raw_output: str,
                    parsed_response: any, correct: bool | None,
                    confidence: float | None, duration_s: float,
                    tokens_approx: int = 0):
        entry = {
            "timestamp": utcnow(),
            "treatment": treatment,
            "subject": subject_name,
            "world_family": world_family,
            "world_seed": world_seed,
            "prompt_hash": content_hash(prompt),
            "raw_output": raw_output,
            "output_hash": content_hash(raw_output),
            "parsed_response": parsed_response,
            "correct": correct,
            "confidence": confidence,
            "duration_seconds": round(duration_s, 2),
            "tokens_approx": tokens_approx,
        }
        self.metadata["runs"].append(entry)
        self._save_metadata()
        return entry
    
    def log_result_summary(self, results_by_treatment: dict):
        self.metadata["results"] = {
            t: {"accuracy": sum(1 for r in runs if r.get("correct")) / max(1,len(runs)),
                "n": len(runs),
                "mean_confidence": sum(r.get("confidence") or 0 for r in runs) / max(1,len(runs)),
                "total_duration_s": sum(r.get("duration_seconds",0) for r in runs)}
            for t, runs in results_by_treatment.items() if runs
        }
        self.metadata["completed_at"] = utcnow()
        self.metadata["status"] = "complete"
        self._save_metadata()
    
    def _save_metadata(self):
        path = os.path.join(self.dir, "experiment-record.json")
        json.dump(self.metadata, open(path, "w"), indent=1, default=str)
