"""E02: Reset vs Persistent vs Persistent+Outcomes."""
import os, json, time, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from cogym.agents.model import OpenAICompatible
from cogym.experiments.factory import synthetic_trading_world
from cogym.experiments.persistence import run_persistence_matrix
from cogym.state.pathway import ContextPathway, PathwayStep

model = OpenAICompatible(
    model_id="muse-spark-1.2-contributor",
    base_url="https://opencode.ai/zen/go/v1",
    api_key=os.environ["OPENCODE_GO_API_KEY"],
)
pathway = ContextPathway(
    name="falsification_first",
    steps=(
        PathwayStep(id="s1", prompt="What does the market believe?", tags=("hypothesis",)),
        PathwayStep(id="s2", prompt="What would falsify that belief?", tags=("falsifier",)),
        PathwayStep(id="s3", prompt="Check evidence. Revise if needed.", tags=("revision",)),
    ),
    system="You value falsification over confirmation.",
)

WORLDS = [
    {"level": 1, "name": "reversal"},
    {"level": 4, "name": "regime_flip"},
]
all_results = {}

for w in WORLDS:
    world = synthetic_trading_world(level=w["level"], seed=42)
    print(f"\n=== {w['name']} ===", flush=True)
    
    matrix = run_persistence_matrix(model=model, world=world, pathway=pathway,
                                    repeats=3)
    
    for label in ["reset", "persistent", "persistent_with_outcomes"]:
        summary = getattr(matrix, label.replace("_with_outcomes", "_with_outcomes"))
        all_results[f"{w['name']}_{label}"] = {
            "mean_log_score": round(summary.mean_log_score, 4),
            "sd_log_score": round(summary.sd_log_score, 4),
            "mean_utility": round(summary.mean_utility, 6),
            "sd_utility": round(summary.sd_utility, 6),
            "signature": {k: round(v,4) if isinstance(v,float) else v 
                         for k,v in vars(summary.mean_signature).items()},
        }
        print(f"  {label:25s} log={summary.mean_log_score:.3f} util={summary.mean_utility:+.5f}")

outpath = os.path.join(os.path.dirname(__file__), "outputs", "persistence-results.json")
json.dump(all_results, open(outpath, "w"), indent=1)
print(f"\nE02 COMPLETE. Results: {outpath}")
