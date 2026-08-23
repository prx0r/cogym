"""Real LLM experiment. No infrastructure. Just run and log."""
import os, json, time, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cogym.agents.model import OpenAICompatible
from cogym.experiments.factory import synthetic_trading_world
from cogym.experiments.runner import run_world, summarize_repeats

API_KEY = os.environ.get("OPENCODE_GO_API_KEY", "")
model = OpenAICompatible(model_id="ox-alpha-free", base_url="https://opencode.ai/zen/go/v1", api_key=API_KEY)

worlds = [
    {"level": 0, "name": "smooth_trend"},
    {"level": 2, "name": "shock_jumps"},
    {"level": 4, "name": "regime_flip"},
]

all_results = {}
for w in worlds:
    world = synthetic_trading_world(level=w["level"], seed=42)
    print(f"\n=== {w['name']} ===")
    runs = []
    for sample in range(3):
        t0 = time.time()
        result = run_world(model=model, world=world,
                          condition=f"{w['name']}_s{sample}",
                          history_mode="reset", temperature=0.2,
                          sample_seed=42 + sample * 100)
        dur = time.time() - t0
        runs.append(result)
        
        # Log every decision
        for rec in result.records:
            print(f"  step {rec.index}: {rec.decision.stance} "
                  f"conf={rec.decision.confidence:.2f} "
                  f"realized={rec.realized_return:.5f} "
                  f"correct={rec.score.direction_correct}")
    
    summary = summarize_repeats(runs, f"baseline_{w['name']}")
    all_results[w["name"]] = {
        "mean_log_score": round(summary.mean_log_score, 4),
        "sd_log_score": round(summary.sd_log_score, 4),
        "mean_utility": round(summary.mean_utility, 6),
        "sd_utility": round(summary.sd_utility, 6),
        "n_samples": SAMPLES if (SAMPLES:=3) else 3,
        "signature": {k: round(v, 4) if isinstance(v, float) else v 
                      for k, v in vars(summary.mean_signature).items()},
    }
    print(f"  SUMMARY: log={summary.mean_log_score:.3f} util={summary.mean_utility:.4f}")

elapsed = time.time() - start_time if 'start_time' in dir() else 0

outpath = "/root/cogym/logs/e01-baseline-results.json"
json.dump({"model": "ox-alpha-free", "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
           **all_results}, open(outpath, "w"), indent=1)

print(f"\n{'='*50}")
print(f"E01 BASELINE COMPLETE | {elapsed:.0f}s")
print(f"Results saved: {outpath}")

for wname, data in all_results.items():
    print(f"  {wname:20s} log_score={data['mean_log_score']:.3f}±{data['sd_log_score']:.3f} "
          f"utility={data['mean_utility']:+.4f}±{data['sd_utility']:.4f}")
