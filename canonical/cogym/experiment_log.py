"""Full experiment logging with explicit outcome states.
CORRECT / INCORRECT / MALFORMED / INFRA_FAILURE are separate. Never collapse."""
from __future__ import annotations
import json, os, time, hashlib
from datetime import datetime, timezone

def utcnow(): return datetime.now(timezone.utc).isoformat()

def content_hash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, default=str).encode()).hexdigest()

class ExperimentLog:
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
        self._save()

    def log_subject(self, treatment: str, subject_name: str, world_family: str,
                    world_seed: int, prompt: str, raw_output: str,
                    parsed_response, outcome: str,  # CORRECT|INCORRECT|MALFORMED|INFRA_FAILURE|MISSING
                    confidence: float | None, duration_s: float,
                    tokens_approx: int = 0) -> dict:
        """outcome must be one of the five states. Never silently collapse."""
        assert outcome in ("CORRECT","INCORRECT","MALFORMED","INFRA_FAILURE","MISSING"), \
            f"invalid outcome: {outcome}"
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
            "outcome": outcome,
            "confidence": confidence,  # None means not stated
            "duration_seconds": round(duration_s, 2),
            "tokens_approx": tokens_approx,
        }
        self.metadata["runs"].append(entry)
        self._save()
        return entry

    def summary_by_treatment(self) -> dict:
        """Accuracy only counts CORRECT/INCORRECT (not MALFORMED/INFRA/MISSING)."""
        out = {}
        by_treatment = {}
        for r in self.metadata["runs"]:
            t = r["treatment"]
            by_treatment.setdefault(t, []).append(r)
        for t, runs in by_treatment.items():
            gradeable = [r for r in runs if r["outcome"] in ("CORRECT", "INCORRECT")]
            malformed = [r for r in runs if r["outcome"] == "MALFORMED"]
            infra = [r for r in runs if r["outcome"] == "INFRA_FAILURE"]
            confidences = [r["confidence"] for r in runs if r["confidence"] is not None]
            out[t] = {
                "n_total": len(runs),
                "n_gradeable": len(gradeable),
                "accuracy": sum(1 for r in gradeable if r["outcome"]=="CORRECT") / max(1,len(gradeable)),
                "malformed_rate": len(malformed)/len(runs),
                "infra_failure_rate": len(infra)/len(runs),
                # confidence stats only from non-null values
                "mean_confidence": sum(confidences)/len(confidences) if confidences else None,
                "confidence_n": len(confidences),
                "total_duration_s": round(sum(r.get("duration_seconds",0) for r in runs),1),
            }
        return out

    def _save(self):
        path = os.path.join(self.dir, "experiment-record.json")
        json.dump(self.metadata, open(path, "w"), indent=1, default=str)
