"""E-C3: What does the supervisor need to see? God variants G0-G6 (thesis §5).

Workers: 3 role-diverse independent calls (shared across all god conditions —
same worker outputs, different reveal granularity = ONE variable per comparison).

God conditions (each one supervisor call over the SAME 3 worker outputs):
  G1 answers      : stances only
  G2 +confidence  : stances + confidence
  G3 +reasoning   : stances + confidence + reasons
  G6 answer-first : supervisor commits to own view BEFORE seeing workers,
                    then sees G3 material and may revise; final call scored

Deterministic bars computed from the same workers:
  MAJ (majority vote) and CW (confidence-weighted).
V_G(god_k) = J(god_k) − max(J_MAJ, J_CW) per condition.
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

GOD_BASE = ("You are the portfolio supervisor. Three analysts worked this problem independently. "
            "Emit your final call.\n" + C.DECISION_FORMAT)


def main():
    model = OpenAICompatible(model_id=C.MODEL_ID, base_url=C.BASE_URL,
                             api_key=os.environ["OPENCODE_GO_API_KEY"], timeout=300)
    eps, bank_hash = C.build_episode_bank(SYMBOLS, START, END, HORIZON, INDICES)
    trials_path = os.path.join(OUT_DIR, "ec3-trials.jsonl")
    conds = ["MAJ", "CW", "G1", "G2", "G3", "G6"]
# trials-file reconstruction keys episodes by bare date; map episode->date
EPISODE_DATE = {}

def key_date(key: str) -> str:
    return key.split("@")[1]
    agg = {c: {} for c in conds}

    def log(t):
        rec = vars(t)
        rec["episode"] = f"{t.episode.symbol}@{t.episode.as_of}"
        with open(trials_path, "a") as fh:
            fh.write(json.dumps(rec | {"symbol": t.episode.symbol}) + "\n")

    for ei, ep in enumerate(eps):
        key = f"{ep.symbol}@{ep.as_of}"
        print(f"[{ei+1}/{len(eps)}] {key} realized={ep.realized:+.2%}", flush=True)

        # shared workers
        workers = []
        for r, s in zip(ROLES, SEEDS):
            t = C.call_subject(model, ep, C.ROLE_PROMPTS[r], 0.7, s)
            t.condition = "workers"; t.role = r
            log(t); workers.append(t)

        maj = C.majority([w.stance or "" for w in workers])
        cw = C.conf_weighted(workers)
        agg["MAJ"][key] = maj
        agg["CW"][key] = cw

        answers = "\n".join(f"- {r}: {w.stance}" for r, w in zip(ROLES, workers))
        with_conf = "\n".join(f"- {r}: {w.stance} (confidence {w.confidence})"
                              for r, w in zip(ROLES, workers))
        with_reason = "\n".join(f"- {r}: {w.stance} (conf {w.confidence}) because: "
                                f"{(w.raw or '')[-160:]}" for r, w in zip(ROLES, workers))

        for name, ctx, temp, seed in [
            ("G1", "Analyst views:\n" + answers, 0.0, 41),
            ("G2", "Analyst views:\n" + with_conf, 0.0, 42),
            ("G3", "Analyst views:\n" + with_reason, 0.0, 43),
        ]:
            g = C.call_subject(model, ep, GOD_BASE, temp, seed, extra_context=ctx)
            g.condition = name; g.role = "supervisor"
            log(g); agg[name][key] = C.parse_stance(g)

        # G6: answer-first then revise (anti-anchoring)
        prior = C.call_subject(model, ep, GOD_BASE + "\nCommit BEFORE seeing anyone.", 0.0, 44)
        prior.condition = "G6"; prior.role = "prior"
        log(prior)
        rev = C.call_subject(model, ep, GOD_BASE, 0.0, 45,
                             extra_context=f"Your independent prior: {prior.stance} "
                                           f"(conf {prior.confidence}).\nAnalyst views:\n{with_reason}")
        rev.condition = "G6"; rev.role = "post"
        log(rev)
        agg["G6"][key] = C.parse_stance(rev)

    results = {"bank_hash": bank_hash, "conditions": {}, "per_episode": []}

    # ---- deterministic extra bars: RANDOM + BAYES(train-reliability) ----
    import hashlib
    def random_bar(key: str) -> str:
        h = int(hashlib.sha256(key.encode()).hexdigest(), 16)
        return "UP" if h % 2 == 0 else "DOWN"

    ep_keys = [f"{e.symbol}@{e.as_of}" for e in eps]
    outcome_up = {f"{e.symbol}@{e.as_of}": e.realized >= 0 for e in eps}
    train_keys, test_keys = ep_keys[:len(ep_keys)//2], ep_keys[len(ep_keys)//2:]

    def role_accuracy(role_idx: int) -> float:
        hit = n = 0
        for k in train_keys:
            w = workers_by_key[k][role_idx]
            if w.stance in ("UP", "DOWN"):
                n += 1
                hit += (w.stance == ("UP" if outcome_up[k] else "DOWN"))
        return hit / n if n else 0.5

    def bayes_bar(key: str) -> str:
        import math as _m
        score_ = 0.0
        for i in range(len(ROLES)):
            w = workers_by_key[key][i]
            if w.stance not in ("UP", "DOWN"):
                continue
            acc = min(0.9, max(0.6, role_accuracy(i)))
            lw = _m.log(acc / (1 - acc))
            score_ += lw * (1 if w.stance == "UP" else -1)
        if score_ == 0.0:
            return "ABSTAIN"
        return "UP" if score_ > 0 else "DOWN"

    workers_by_key = {}
    # reconstruct shared-worker stances from trials file (single source of truth)
    with open(trials_path) as fh:
        for line in fh:
            rec = json.loads(line)
            if rec.get("condition") == "workers":
                k = rec["episode"]
                workers_by_key.setdefault(k, []).append(rec)
    for k in workers_by_key:
        workers_by_key[k] = [w for r in ROLES
                             for w in workers_by_key[k] if w["role"] == r][:len(ROLES)]
    agg["RANDOM"] = {k: random_bar(k) for k in ep_keys}
    agg["BAYES"] = {k: (bayes_bar(k) if k in test_keys else None) for k in ep_keys}
    results["bayes_train_split"] = train_keys
    results["bayes_note"] = ("role reliabilities estimated on train split only, applied to "
                             "test split; weights clipped to logit([0.6,0.9])")

    for cond in conds + ["RANDOM", "BAYES"]:
        utils, ok, decided = [], 0, 0
        for key, d in agg[cond].items():
            if d is None:
                continue
            ep = next(e for e in eps if f"{e.symbol}@{e.as_of}" == key)
            utils.append(C.score(d, ep))
            if d in ("UP", "DOWN"):
                decided += 1
                ok += (d == ("UP" if ep.realized >= 0 else "DOWN"))
        results["conditions"][cond] = {
            "mean_utility_bps": round(sum(utils) / len(utils) * 1e4, 2),
            "direction_accuracy": round(ok / decided, 3) if decided else None,
            "n_decided": decided}
    best_det = max(v["mean_utility_bps"] for k, v in results["conditions"].items()
                   if k in ("MAJ", "CW", "RANDOM", "BAYES"))
    for cond in ["G1", "G2", "G3", "G6"]:
        results["conditions"][cond]["V_G_vs_best_deterministic_bps"] = round(
            results["conditions"][cond]["mean_utility_bps"] - best_det, 2)
    results["claim_status"] = "PILOT n=8 — PROVISIONAL"

    with open(os.path.join(OUT_DIR, "ec3-results.json"), "w") as fh:
        json.dump(results, fh, indent=2)
    print(json.dumps(results["conditions"], indent=1))


if __name__ == "__main__":
    main()
