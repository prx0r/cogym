"""E-C1 runner: team production function at fixed budget.

Per PROTOCOL-EC1.md (frozen). Appends every raw call to outputs/ec1-trials.jsonl
and writes outputs/ec1-results.json at the end.
"""
from __future__ import annotations
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cogym.agents.model import OpenAICompatible
import collude as C

SYMBOLS = ["SPY", "QQQ", "TLT", "GLD"]
START, END = "2024-08-01", "2026-08-22"
HORIZON = 5
INDICES = [300, 430]
ROLES = ["bull", "bear", "quant"]
SEEDS = [11, 22, 33]

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)
TRIALS_PATH = os.path.join(OUT_DIR, "ec1-trials.jsonl")
RESULTS_PATH = os.path.join(OUT_DIR, "ec1-results.json")


def log_trial(obj):
    with open(TRIALS_PATH, "a") as fh:
        fh.write(json.dumps(obj) + "\n")


def main():
    model = OpenAICompatible(model_id=C.MODEL_ID, base_url=C.BASE_URL,
                             api_key=os.environ["OPENCODE_GO_API_KEY"], timeout=300)

    print("freezing episode bank...", flush=True)
    eps, bank_hash = C.build_episode_bank(SYMBOLS, START, END, HORIZON, INDICES)
    print(f"bank: {len(eps)} episodes, hash={bank_hash[:16]}", flush=True)

    aggregated = {c: {} for c in ["solo", "ensemble3", "roles3", "roles3_conf", "god_g2"]}
    all_trials = {c: [] for c in aggregated}

    for ei, ep in enumerate(eps):
        print(f"[{ei+1}/{len(eps)}] {ep.symbol} @ {ep.as_of} realized={ep.realized:+.2%}", flush=True)

        # solo
        t = C.call_subject(model, ep, C.ROLE_PROMPTS["homogeneous"], 0.7, SEEDS[0])
        t.condition = "solo"; t.role = "homogeneous"
        all_trials["solo"].append(t); log_trial(vars(t) | {"episode": ep.as_of, "symbol": ep.symbol})
        aggregated["solo"][f"{ep.symbol}@{ep.as_of}"] = {"dir": C.parse_stance(t), "conf": t.confidence}

        # ensemble3: same prompt, seed variation only
        ens = []
        for s in SEEDS:
            t = C.call_subject(model, ep, C.ROLE_PROMPTS["homogeneous"], 0.7, s)
            t.condition = "ensemble3"; t.role = f"seed{s}"
            all_trials["ensemble3"].append(t)
            log_trial(vars(t) | {"episode": ep.as_of, "symbol": ep.symbol})
            ens.append(t)
        aggregated["ensemble3"][f"{ep.symbol}@{ep.as_of}"] = {
            "dir": C.majority([x.stance or "" for x in ens]),
            "conf": sum((x.confidence or 50) for x in ens) / len(ens)}

        # roles3 independent
        roles = []
        for r in ROLES:
            t = C.call_subject(model, ep, C.ROLE_PROMPTS[r], 0.7, SEEDS[ROLES.index(r)])
            t.condition = "roles3"; t.role = r
            all_trials["roles3"].append(t)
            log_trial(vars(t) | {"episode": ep.as_of, "symbol": ep.symbol})
            roles.append(t)
        maj = C.majority([x.stance or "" for x in roles])
        confw = C.conf_weighted(roles)
        aggregated["roles3"][f"{ep.symbol}@{ep.as_of}"] = {"dir": maj, "conf": None}
        aggregated["roles3_conf"][f"{ep.symbol}@{ep.as_of}"] = {"dir": confw, "conf": None}

        # god_g2: supervisor sees answers + confidence (deterministic scoring of ITS output)
        ctx = "\n".join(f"- {r}: {x.stance} (confidence {x.confidence if x.confidence is not None else '?'})"
                        for r, x in zip(ROLES, roles))
        g = C.call_subject(model, ep, C.GOD_SYSTEM, 0.0, 7, extra_context=ctx)
        g.condition = "god_g2"; g.role = "supervisor"
        all_trials["god_g2"].append(g); log_trial(vars(g) | {"episode": ep.as_of, "symbol": ep.symbol})
        aggregated["god_g2"][f"{ep.symbol}@{ep.as_of}"] = {"dir": C.parse_stance(g), "conf": g.confidence}

    # ---- deterministic scoring ----
    results = {"bank_hash": bank_hash, "model": C.MODEL_ID,
               "n_episodes": len(eps), "conditions": {}, "per_episode": []}
    for cond, aggs in aggregated.items():
        utils, dirs_ok, n_decided = [], 0, 0
        for key, a in aggs.items():
            ep = next(e for e in eps if f"{e.symbol}@{e.as_of}" == key)
            u = C.score(a["dir"], ep)
            utils.append(u)
            if a["dir"] in ("UP", "DOWN"):
                n_decided += 1
                want = "UP" if ep.realized >= 0 else "DOWN"
                dirs_ok += (a["dir"] == want)
        calls_used = {"solo": 1, "ensemble3": 3, "roles3": 3, "roles3_conf": 3, "god_g2": 4}[cond]
        results["conditions"][cond] = {
            "mean_utility_bps": round(sum(utils) / len(utils) * 1e4, 2),
            "direction_accuracy": round(dirs_ok / n_decided, 3) if n_decided else None,
            "n_decided": n_decided,
            "calls_total": calls_used * len(eps),
            "utility_per_call_bps": round(sum(utils) / (calls_used * len(eps)) * 1e4, 3),
        }
        for key, a in aggs.items():
            ep = next(e for e in eps if f"{e.symbol}@{e.as_of}" == key)
            results["per_episode"].append({
                "episode": key, "realized": round(ep.realized, 4), "condition": cond,
                "dir": a["dir"], "utility_bps": round(C.score(a["dir"], ep) * 1e4, 1),
                "brier": C.brier(a["dir"], a.get("conf"), ep)})

    call_stats = {cond: C.summarize(cond, trials, {}) for cond, trials in all_trials.items()}
    for cond, cs in call_stats.items():
        results["conditions"][cond]["call_stats"] = cs

    with open(RESULTS_PATH, "w") as fh:
        json.dump(results, fh, indent=2)
    print("\n==== E-C1 RESULTS ====")
    for cond, r in sorted(results["conditions"].items(), key=lambda kv: -kv[1]["mean_utility_bps"]):
        print(f"{cond:>12} util={r['mean_utility_bps']:+8.1f}bps acc={r['direction_accuracy']} "
              f"decided={r['n_decided']}/8 util/call={r['utility_per_call_bps']:+.2f}")
    print("saved:", RESULTS_PATH)


if __name__ == "__main__":
    main()
