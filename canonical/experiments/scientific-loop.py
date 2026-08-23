"""Full scientific experiment loop: run, log every decision, grade, review."""
import os, json, time, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["OPENCODE_GO_API_KEY"] = os.environ.get("OPENCODE_GO_API_KEY", "")

from cogym.agents.model import OpenAICompatible
from cogym.experiments.factory import synthetic_trading_world
from cogym.experiments.runner import run_world, summarize_repeats

EXDIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "experiments", "e01-baseline")
os.makedirs(EXDIR + "/outputs", exist_ok=True)

model = OpenAICompatible(
    model_id="muse-spark-1.2-contributor",
    base_url="https://opencode.ai/zen/go/v1",
    api_key=os.environ["OPENCODE_GO_API_KEY"],
)
worlds = [
    {"level": 0, "name": "smooth_trend"},
    {"level": 2, "name": "shock_jumps"},
    {"level": 4, "name": "regime_flip"},
]
all_runs = []
all_results = {}
start = time.time()

for w in worlds:
    world = synthetic_trading_world(level=w["level"], seed=42)
    print(f"\n=== {w['name']} ===", flush=True)
    runs = []
    for sample in range(3):
        result = run_world(model=model, world=world,
            condition=f"{w['name']}_s{sample}",
            history_mode="reset", temperature=0.2,
            sample_seed=42 + sample * 100)
        runs.append(result)
        for rec in result.records:
            all_runs.append({
                "world": w["name"], "sample": sample,
                "step_index": rec.index,
                "stance": rec.decision.stance,
                "confidence": round(rec.decision.confidence, 3),
                "expected_return": round(rec.decision.expected_return, 5),
                "crux": rec.decision.crux[:100],
                "falsifiers": list(rec.decision.falsifiers)[:3],
                "reasoning_summary": rec.decision.reasoning_summary[:200],
                "realized_return": round(rec.realized_return, 6),
                "log_score": round(rec.score.log_score, 4),
                "direction_correct": rec.score.direction_correct == 1.0,
                "paper_utility": round(rec.score.paper_utility, 6),
            })
        ml = result.mean_log_score
        mu = result.mean_paper_utility
        dir_ok = sum(1 for r in result.records if r.score.direction_correct) / max(1,len(result.records))
        print(f"  s{sample+1}: log={ml:.3f} util={mu:+.4f} dir={dir_ok:.0%}", flush=True)
    summary = summarize_repeats(runs, f"baseline_{w['name']}")
    all_results[w["name"]] = {
        "mean_log_score": round(summary.mean_log_score, 4),
        "sd_log_score": round(summary.sd_log_score, 4),
        "mean_utility": round(summary.mean_utility, 6),
        "sd_utility": round(summary.sd_utility, 6),
        "signature": {k: round(v, 4) if isinstance(v, float) else v 
                      for k, v in vars(summary.mean_signature).items()},
    }
    print(f"  SUMMARY: log={summary.mean_log_score:.3f}", flush=True)

elapsed = time.time() - start
json.dump(all_runs, open(EXDIR + "/outputs/all-decisions.json", "w"), indent=1)
json.dump({"model": "muse-spark-1.2-contributor", "elapsed_s": round(elapsed),
           "total_llm_calls": len(all_runs), **all_results},
          open(EXDIR + "/outputs/baseline-results.json", "w"), indent=1)

# Peer review generation
lines = [f"# E01 Baseline Review\nModel: muse-spark-1.2-contributor | Calls: {len(all_runs)}\n"]
for wname, data in all_results.items():
    lines.append(f"### {wname}\n- log={data['mean_log_score']} ±{data['sd_log_score']} util={data['mean_utility']}")
stance_acc = {}
for d in all_runs:
    stance_acc.setdefault(d["stance"], []).append(d["direction_correct"])
lines.append("\nStance accuracy:")
for s, o in sorted(stance_acc.items()):
    lines.append(f"- {s}: {sum(o)/len(o):.0%} ({len(o)} decisions)")

with open(EXDIR + "/REVIEW.md", "w") as f:
    f.write("\n".join(lines))

print(f"\nE01 COMPLETE: {len(all_runs)} LLM calls in {elapsed:.0f}s")
for wname, data in all_results.items():
    print(f"  {wname:20s} log={data['mean_log_score']:.3f} util={data['mean_utility']:+.4f}")
