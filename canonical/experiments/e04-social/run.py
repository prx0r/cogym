"""E04: Social reveal conditions — do agents herd or improve after seeing peers?"""
import os, json, time, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from cogym.agents.model import OpenAICompatible
from cogym.experiments.social import run_social_round
from cogym.experiments.factory import synthetic_trading_world

model = OpenAICompatible(
    model_id="ox-alpha-free",
    base_url="https://opencode.ai/zen/go/v1",
    api_key=os.environ["OPENCODE_GO_API_KEY"],
)
world = synthetic_trading_world(level=4, seed=42)

agents = {
    "analyst_a": model,
    "analyst_b": model,
    "analyst_c": model,
}

conditions = ["decision_only", "decision_confidence", "full_artifact"]
results = {}

for vis in conditions:
    print(f"\n=== Visibility: {vis} ===", flush=True)
    rounds = []
    for seed_offset in range(3):
        social = run_social_round(
            agents=agents, packet=world.snapshot(50),
            horizon_steps=5, visibility=vis,
            seed=1000 + seed_offset * 100,
        )
        for sd in social:
            private_correct = sd.private.stance == "LONG"  # simplified scoring
            revised_correct = sd.revised.stance == "LONG"
            rounds.append({
                "agent": sd.agent_id,
                "private_stance": sd.private.stance,
                "revised_stance": sd.revised.stance,
                "changed": sd.changed,
                "private_conf": sd.private.confidence,
                "revised_conf": sd.revised.confidence,
            })
    
    n_changed = sum(1 for r in rounds if r["changed"])
    results[vis] = {
        "rounds": rounds,
        "n_agents": len(rounds) // 3,
        "changed_pct": round(n_changed / len(rounds), 2) if rounds else 0,
    }
    print(f"  {len(rounds)} decisions | {n_changed} changed after seeing peers")

outpath = os.path.join(os.path.dirname(__file__), "outputs", "social-results.json")
json.dump(results, open(outpath, "w"), indent=1)
print(f"\nE04 COMPLETE")
