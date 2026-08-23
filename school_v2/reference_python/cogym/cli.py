from __future__ import annotations
import argparse, json
from dataclasses import asdict
from .benchmark import make_world, WORLD_SUITE
from .schema import AgentGenome
from .memory import SQLiteMemory
from .agent import CognitiveAgent, RuleBasedModel
from .experiment import ExperimentRunner


def main():
    p=argparse.ArgumentParser(prog="cogym")
    sub=p.add_subparsers(dest="cmd",required=True)
    b=sub.add_parser("demo"); b.add_argument("--world",choices=WORLD_SUITE.keys(),default="regime_flip"); b.add_argument("--seed",type=int,default=42)
    args=p.parse_args()
    if args.cmd=="demo":
        w=make_world(args.world,args.seed)
        m=SQLiteMemory(":memory:")
        gs=[AgentGenome(induction="neutral",memory_policy="recent",memory_depth=4),
            AgentGenome(induction="loss_salience",memory_policy="failures_first",memory_depth=4,
                        social_topology="all_to_all",reveal="decision_confidence",revision_rounds=1)]
        agents=[CognitiveAgent(f"agent_{i}",g,RuleBasedModel(),m) for i,g in enumerate(gs)]
        runner=ExperimentRunner(w,agents); runner.run(end=120)
        print(json.dumps([asdict(x) for x in runner.results()],indent=2))

if __name__ == "__main__":
    main()
