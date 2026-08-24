from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from .agents.model import HarnessTraderModel
from .dojo.curriculum import CurriculumSplit
from .dojo.master import PersistentMaster
from .experiments.factory import synthetic_trading_world
from .experiments.transfer import run_abcdef
from .state.pack import load_pack


def _cmd_smoke(_: argparse.Namespace) -> None:
    model = HarnessTraderModel()
    world = synthetic_trading_world(3, 42)
    pack = load_pack("packs/trading_regime_shift_v1.json")
    report = run_abcdef(model, world, pack.pathway, repeats=3, indices=[35, 55, 75, 95, 115, 135, 155])
    print(json.dumps({
        "experiment_id": report.experiment_id,
        "decision_fidelity": report.decision_fidelity,
        "behavior_distance": report.behavior_distance,
        "artifact_similarity": report.artifact_similarity,
    }, indent=2, sort_keys=True))


def _cmd_dojo(_: argparse.Namespace) -> None:
    model = HarnessTraderModel()
    master = PersistentMaster("master-harness", model)
    curriculum = CurriculumSplit(
        training_worlds=(synthetic_trading_world(1, 10), synthetic_trading_world(2, 11)),
        validation_worlds=(synthetic_trading_world(3, 12), synthetic_trading_world(4, 13)),
    )
    rows = []
    for i in range(3):
        ev = master.teach_one(f"student-{i}", model, curriculum, seed=1000 + i * 100000, indices=[35, 65, 95, 125, 155])
        rows.append({"student": ev.student_id, "transmission": ev.transmission_id, "log_score_gain": ev.log_score_gain, "utility_gain": ev.utility_gain})
    print(json.dumps(rows, indent=2))


def _cmd_worlds(_: argparse.Namespace) -> None:
    from .worlds.registry import kinds
    print(json.dumps(kinds(), indent=2, sort_keys=True))


def main() -> None:
    p = argparse.ArgumentParser(prog="cogym")
    sub = p.add_subparsers(required=True)
    smoke = sub.add_parser("smoke", help="run offline A-F harness smoke test")
    smoke.set_defaults(fn=_cmd_smoke)
    dojo = sub.add_parser("dojo-demo", help="run offline persistent-master teaching loop")
    dojo.set_defaults(fn=_cmd_dojo)
    worlds = sub.add_parser("worlds", help="list registered world kinds (v2 registry)")
    worlds.set_defaults(fn=_cmd_worlds)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
