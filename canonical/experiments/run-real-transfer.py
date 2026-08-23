#!/usr/bin/env python3
"""Run the canonical A-F transfer experiment using ox-alpha-free.
This is the REAL experiment: live pathway generation vs static transfers.
Uses trading_v1's own run_abcdef() which calls run_live_pathway() at experiment time."""
import os, json, time, sys
sys.path.insert(0, os.path.dirname(__file__))

from cogym.agents.model import OpenAICompatible
from cogym.experiments.transfer import run_abcdef
from cogym.experiments.factory import synthetic_trading_world
from cogym.state.pathway import ContextPathway, PathwayStep

def main():
    api_key = os.environ.get("OPENCODE_GO_API_KEY", "")
    if not api_key:
        print("ERROR: OPENCODE_GO_API_KEY not set"); return

    model = OpenAICompatible(
        model_id="ox-alpha-free",
        base_url="https://opencode.ai/zen/go/v1",
        api_key=api_key,
    )

    world = synthetic_trading_world(level=4, seed=42)

    pathway = ContextPathway(
        name="agent_evaluation_falsification",
        steps=(
            PathwayStep(id="s1", prompt="Before deciding, identify what the market currently BELIEVES. What is the consensus trade and why?", tags=("hypothesis",)),
            PathwayStep(id="s2", prompt="What specific evidence would FALSIFY that consensus? Name one observation that would prove the crowd wrong.", tags=("falsification",)),
            PathwayStep(id="s3", prompt="Now check: is that falsifying evidence present in the current data? If yes, revise your view. If not, commit with calibrated confidence (output a probability).", tags=("revision", "decision")),
        ),
        system="You are a careful trader who values falsification over confirmation.",
    )

    print("=== CANONICAL ABCDEF TRANSFER EXPERIMENT ===")
    print(f"World: {world.manifest.world_id[:20]}... level=4 seed=42")
    print(f"Model: ox-alpha-free")
    print(f"Pathway: {pathway.name} ({len(pathway.steps)} steps)")
    print()

    t0 = time.time()
    report = run_abcdef(
        target_model=model,
        world=world,
        pathway=pathway,
        repeats=1,
        base_seed=42,
    )
    dur = time.time() - t0
    print(f"Completed in {dur:.0f}s\n")

    # Extract results from StateTransferReport
    if hasattr(report, '__dict__'):
        for attr_name in ['conditions', 'results', 'buckets', 'fidelities']:
            val = getattr(report, attr_name, None)
            if val and isinstance(val, dict):
                print(f"{attr_name}:")
                for cond, data in sorted(val.items()):
                    if hasattr(data, 'mean_log_score'):
                        print(f"  {cond}: log_score={data.mean_log_score:.3f}")
                    elif isinstance(data, list) and len(data) > 0:
                        r = data[0]
                        if hasattr(r, 'mean_log_score'):
                            print(f"  {cond}: log_score={r.mean_log_score:.3f}")
                        elif hasattr(r, 'mean_reward'):
                            print(f"  {cond}: reward={r.mean_reward:.4f}")

    # Save full report
    out = {}
    for k, v in vars(report).items() if hasattr(report, '__dict__') else []:
        try: out[k] = str(v)[:500]
        except: pass
    json.dump(out, open("/root/cogym/logs/real-transfer-oxalpha.json", "w"), indent=1, default=str)
    print("\nSaved to /root/cogym/logs/real-transfer-oxalpha.json")

if __name__ == "__main__":
    import time
    main()
