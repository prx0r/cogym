import os
"""E02: Reset vs Persistent context. Same worlds, only history_mode differs."""
import os, json, time, sys
sys.path.insert(0, "/root/cogym/canonical")
from cogym.agents.model import OpenAICompatible
from cogym.experiments.factory import synthetic_trading_world
from cogym.experiments.runner import run_world, summarize_repeats

WORLDS = [
    {"level": 1, "name": "reversal"},
    {"level": 2, "name": "shock_jumps"},
    {"level": 4, "name": "regime_flip"},
]
SAMPLES = 5
BASE_SEED = 42
CONDITIONS = ["reset", "persistent"]

def main():
    api_key = os.environ.get("OPENCODE_GO_API_KEY",
        os.environ["OPENCODE_GO_API_KEY"])
    model = OpenAICompatible(
        model_id="ox-alpha-free",
        base_url="https://opencode.ai/zen/go/v1",
        api_key=api_key,
    )

    results = {}
    for winfo in WORLDS:
        wname = winfo["name"]
        world = synthetic_trading_world(level=winfo["level"], seed=BASE_SEED)
        
        for mode in CONDITIONS:
            key = f"{wname}_{mode}"
            print(f"\n{key}")
            runs = []
            
            for sample in range(SAMPLES):
                result = run_world(
                    model=model, world=world,
                    condition=f"{key}_s{sample}",
                    history_mode=mode,
                    temperature=0.2,
                    sample_seed=BASE_SEED + sample * 100,
                    reveal_outcomes=(mode == "persistent"),  # persistent agents see outcomes
                )
                runs.append(result)
                ml = result.mean_log_score
                mu = result.mean_paper_utility
                print(f"  s{sample+1}: log={ml:.3f} util={mu:.4f}")
            
            summary = summarize_repeats(runs, key)
            results[key] = {
                "mean_log_score": round(summary.mean_log_score, 4),
                "sd_log_score": round(summary.sd_log_score, 4),
                "mean_utility": round(summary.mean_paper_utility, 4),
                "sd_utility": round(summary.sd_utility, 4),
                "signature": {k: v for k, v in vars(summary.mean_signature).items()},
            }
            print(f"  → log={summary.mean_log_score:.3f}±{summary.sd_log_score:.3f}")

    # Compare
    print(f"\n{'='*50}")
    print("PERSISTENCE COMPARISON")
    for winfo in WORLDS:
        wname = winfo["name"]
        reset_key = f"{wname}_reset"
        persist_key = f"{wname}_persistent"
        r = results.get(reset_key, {})
        p = results.get(persist_key, {})
        if r and p:
            diff = p["mean_utility"] - r["mean_utility"]
            direction = "BETTER" if diff > 0 else "WORSE" if diff < 0 else "SAME"
            print(f"  {wname:20s} reset_util={r['mean_utility']:+.4f} "
                  f"persist_util={p['mean_utility']:+.4f} → {direction}")

    outpath = os.path.join(os.path.dirname(__file__), "outputs", "persistence-results.json")
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    json.dump(results, open(outpath, "w"), indent=1)

if __name__ == "__main__":
    import time as time_module
    main()
