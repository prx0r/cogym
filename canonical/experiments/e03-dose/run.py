"""E03: Pathway depth dose-response. 0 to max reasoning steps."""
import os, json, time, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from cogym.agents.model import OpenAICompatible
from cogym.experiments.factory import synthetic_trading_world
from cogym.experiments.dose import pathway_dose_response
from cogym.state.pathway import ContextPathway, PathwayStep

model = OpenAICompatible(
    model_id="ox-alpha-free",
    base_url="https://opencode.ai/zen/go/v1",
    api_key=os.environ["OPENCODE_GO_API_KEY"],
)
world = synthetic_trading_world(level=4, seed=42)  # regime flip

pathway = ContextPathway(
    name="full_reasoning_pathway",
    steps=(
        PathwayStep(id="s0", prompt="What is the current market direction and volatility?"),
        PathwayStep(id="s1", prompt="What is the market consensus and why?", tags=("hypothesis",)),
        PathwayStep(id="s2", prompt="What would FALSIFY the consensus?", tags=("falsification",)),
        PathwayStep(id="s3", prompt="Is that falsifying evidence present? Check carefully.", tags=("evidence_check",)),
        PathwayStep(id="s4", prompt="Given everything, what is your calibrated position?", tags=("decision",)),
    ),
    system="You are a careful quantitative trader.",
)

print("Running dose-response: 0 to 5 reasoning steps...", flush=True)
results = pathway_dose_response(model=model, world=world, pathway=pathway, repeats=3)

outpath = os.path.join(os.path.dirname(__file__), "outputs", "dose-results.json")
out = []
for dr in results:
    out.append({
        "depth": dr.steps,
        "mean_log_score": round(dr.summary.mean_log_score, 4),
        "sd_log_score": round(dr.summary.sd_log_score, 4),
        "mean_utility": round(dr.summary.mean_utility, 6),
        "signature": {k: round(v,4) if isinstance(v,float) else v 
                      for k,v in vars(dr.summary.mean_signature).items()},
    })
    print(f"  depth {dr.steps}: log={dr.summary.mean_log_score:.3f} util={dr.summary.mean_utility:+.5f}")
json.dump(out, open(outpath, "w"), indent=1)
print(f"\nE03 COMPLETE. Results: {outpath}")
