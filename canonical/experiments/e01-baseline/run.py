import os
"""E01: Baseline measurement. 5 worlds x 5 samples. Deterministic scoring."""
import os, json, time, sys
sys.path.insert(0, "/root/cogym/canonical")
from cogym.agents.model import OpenAICompatible, Message
from cogym.experiments.factory import synthetic_trading_world
from cogym.experiments.runner import run_world, summarize_repeats
from cogym.experiments.scoring import DecisionScore

WORLDS = [
    {"level": 0, "name": "smooth_trend"},
    {"level": 1, "name": "reversal"},
    {"level": 2, "name": "shock_jumps"},
    {"level": 4, "name": "regime_flip"},
    {"level": 5, "name": "pattern_break"},
]
SAMPLES = 5
BASE_SEED = 42

def main():
    api_key = os.environ.get("OPENCODE_GO_API_KEY",
        os.environ["OPENCODE_GO_API_KEY"])
    model = OpenAICompatible(
        model_id="ox-alpha-free",
        base_url="https://opencode.ai/zen/go/v1",
        api_key=api_key,
    )

    all_results = {}
    total_start = time.time()

    for winfo in WORLDS:
        wname = winfo["name"]
        print(f"\n{'='*50}")
        print(f"World: {wname} (level {winfo['level']})")
        
        world = synthetic_trading_world(level=winfo["level"], seed=BASE_SEED)
        runs = []
        
        for sample in range(SAMPLES):
            t0 = time.time()
            result = run_world(
                model=model, world=world,
                condition=f"{wname}_sample_{sample}",
                history_mode="reset",
                temperature=0.2,
                sample_seed=BASE_SEED + sample * 100,
            )
            dur = time.time() - t0
            runs.append(result)
            
            ml = result.mean_log_score
            mu = result.mean_paper_utility
            dir_ok = sum(1 for r in result.records if r.score.direction_correct) / len(result.records)
            n_decisions = len(result.records)
            
            print(f"  sample {sample+1}: log_score={ml:.3f} utility={mu:.4f} "
                  f"dir_correct={dir_ok:.0%} decisions={n_decisions} ({dur:.0f}s)")
        
        summary = summarize_repeats(runs, f"baseline_{wname}")
        all_results[wname] = {
            "mean_log_score": summary.mean_log_score,
            "sd_log_score": summary.sd_log_score,
            "mean_utility": summary.mean_paper_utility,
            "sd_utility": summary.sd_utility,
            "mean_signature": {k: v for k, v in vars(summary.mean_signature).items()},
            "n_runs": SAMPLES,
            "decisions_per_run": len(runs[0].records),
        }
        print(f"  SUMMARY: log_score={summary.mean_log_score:.3f}±{summary.sd_log_score:.3f} "
              f"utility={summary.mean_paper_utility:.4f}±{summary.sd_utility:.4f}")

    elapsed = time.time() - total_start
    
    # Save full results
    outpath = os.path.join(os.path.dirname(__file__), "outputs", "baseline-results.json")
    os.makedirs(os.path.dirname(outpath), exist_ok=True)
    
    serializable = {}
    for wname, data in all_results.items():
        serializable[wname] = {
            k: (round(v, 4) if isinstance(v, float) else 
                {kk: round(vv, 4) if isinstance(vv, float) else vv for kk, vv in v.items()} if isinstance(v, dict) else v)
            for k, v in data.items()
        }
    serializable["total_duration_s"] = round(elapsed, 0)
    serializable["model"] = "ox-alpha-free"
    serializable["samples_per_world"] = SAMPLES
    json.dump(serializable, open(outpath, "w"), indent=1)
    
    print(f"\n{'='*50}")
    print(f"E01 BASELINE COMPLETE | {elapsed:.0f}s total")
    for wname, data in all_results.items():
        print(f"  {wname:20s} log={data['mean_log_score']:.3f}±{data['sd_log_score']:.3f} "
              f"util={data['mean_utility']:.4f}")

if __name__ == "__main__":
    import time as time_module
    main()
