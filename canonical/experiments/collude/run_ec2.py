"""E-C2: Communication value — does talking produce intelligence or correlation?

Conditions per decision (all role-diverse trios, temp=0.7):
  indep3   : 3 roles independent → majority            (3 calls)
  chat3    : round1 independent stances revealed → round2 revisions
             → majority of revised                      (6 calls)
  seq3     : A decides → B sees A → C sees A+B → last stance
             + majority fallback                        (3 calls)
  debate3  : bull writes case → bear rebuts → quant judges (3 calls)

Primary metric: V_comm = J(chat3) − J(indep3).
Also tests diversity collapse: pairwise stance agreement rate per condition.
Reuses frozen E-C1 episode bank hash a621a0e19fa81566 (identical decisions).
"""
from __future__ import annotations
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cogym.agents.model import OpenAICompatible, Message
import collude as C

SYMBOLS = ["SPY", "QQQ", "TLT", "GLD"]
START, END = "2024-08-01", "2026-08-22"
HORIZON = 5
INDICES = [300, 430]
ROLES = ["bull", "bear", "quant"]
SEEDS = [11, 22, 33]
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")


def ask(model, ep, system, temperature, seed, extra=""):
    return C.call_subject(model, ep, system, temperature, seed, extra_context=extra)


def main():
    model = OpenAICompatible(model_id=C.MODEL_ID, base_url=C.BASE_URL,
                             api_key=os.environ["OPENCODE_GO_API_KEY"], timeout=300)
    eps, bank_hash = C.build_episode_bank(SYMBOLS, START, END, HORIZON, INDICES)
    print(f"bank {len(eps)} eps hash={bank_hash[:16]} (must equal ec1)", flush=True)
    trials_path = os.path.join(OUT_DIR, "ec2-trials.jsonl")
    results = {"bank_hash": bank_hash, "conditions": {}}
    round_stances = {}

    def log(t, extra=None):
        rec = vars(t) | {"symbol": t.episode.symbol}
        if extra:
            rec |= extra
        with open(trials_path, "a") as fh:
            fh.write(json.dumps(rec) + "\n")

    aggregated = {}
    for ei, ep in enumerate(eps):
        key = f"{ep.symbol}@{ep.as_of}"
        print(f"[{ei+1}/{len(eps)}] {key} realized={ep.realized:+.2%}", flush=True)
        aggregated[key] = {}

        # indep3
        r1 = []
        for r, s in zip(ROLES, SEEDS):
            t = ask(model, ep, C.ROLE_PROMPTS[r], 0.7, s)
            t.condition = "indep3"; t.role = r
            log(t); r1.append(t)
        aggregated[key]["indep3"] = C.majority([t.stance or "" for t in r1])
        round_stances.setdefault("indep3", []).append([t.stance for t in r1])

        # chat3: reveal round-1 stances, allow one revision
        reveal = "\n".join(f"- {r} said {t.stance} (conf {t.confidence})"
                          for r, t in zip(ROLES, r1))
        r2 = []
        for r, s in zip(ROLES, SEEDS):
            msg = ("Your teammates' initial views:\n" + reveal +
                   "\nRevise or keep your view. Respond in the same JSON format.")
            t = ask(model, ep, C.ROLE_PROMPTS[r], 0.7, s + 100, extra=msg)
            t.condition = "chat3"; t.role = f"{r}-rev"
            log(t); r2.append(t)
        aggregated[key]["chat3"] = C.majority([t.stance or "" for t in r2])
        round_stances.setdefault("chat3", []).append([t.stance for t in r2])

        # seq3: sequential influence chain
        chain_ctx = ""
        seq = []
        for i, (r, s) in enumerate(zip(ROLES, SEEDS)):
            extra = f"Earlier teammates' views:\n{chain_ctx}" if chain_ctx else ""
            t = ask(model, ep, C.ROLE_PROMPTS[r], 0.7, s, extra=extra)
            t.condition = "seq3"; t.role = f"pos{i}"
            log(t); seq.append(t)
            chain_ctx += f"- {r}: {t.stance}\n"
        aggregated[key]["seq3"] = C.majority([t.stance or "" for t in seq])
        round_stances.setdefault("seq3", []).append([t.stance for t in seq])

        # debate3: bull case → bear rebuttal → quant judge
        bull_case = ask(model, ep, C.ROLE_PROMPTS["bull"], 0.7, 11,
                        extra="Argue your strongest bullish case in <=40 words.")
        bull_case.condition = "debate3"; bull_case.role = "bull-case"; log(bull_case)
        rebut = ask(model, ep, C.ROLE_PROMPTS["bear"], 0.7, 22,
                    extra=f"Bull case:\n{bull_case.raw[-400:]}\nRebut in <=40 words, then give your JSON.")
        rebut.condition = "debate3"; rebut.role = "bear-rebuttal"; log(rebut)
        verdict = ask(model, ep,
                      "You are an impartial judge. Weigh both cases, discount rhetoric. "
                      + C.DECISION_FORMAT, 0.0, 33,
                      extra=f"BULL:\n{bull_case.raw[-400:]}\n\nBEAR:\n{rebut.raw[-400:]}")
        verdict.condition = "debate3"; verdict.role = "judge"; log(verdict)
        aggregated[key]["debate3"] = C.parse_stance(verdict)
        round_stances.setdefault("debate3", []).append([verdict.stance])

    # score
    def diversity_metrics(rounds):
        """Pairwise stance agreement H and decision entropy over one round of stances."""
        import math as _m
        flat = [t.stance for t in rounds if t.stance in ("UP", "DOWN")]
        pairs, agree = 0, 0
        for i in range(len(flat)):
            for j in range(i + 1, len(flat)):
                pairs += 1
                agree += (flat[i] == flat[j])
        H_pair = agree / pairs if pairs else None
        counts = {}
        for s in flat:
            counts[s] = counts.get(s, 0) + 1
        n = len(flat)
        ent = -sum((c / n) * _m.log(c / n) for c in counts.values()) if n else None
        return {"pairwise_agreement": round(H_pair, 3) if H_pair is not None else None,
                "decision_entropy": round(ent, 3) if ent is not None else None,
                "n_valid_stances": n}

    for cond_i, cond in enumerate(["indep3", "chat3", "seq3", "debate3"]):
        utils, ok, decided = [], 0, 0
        agrees = []
        for key, d in aggregated.items():
            ep = next(e for e in eps if f"{e.symbol}@{e.as_of}" == key)
            utils.append(C.score(d, ep))
            if d in ("UP", "DOWN"):
                decided += 1
                ok += (d == ("UP" if ep.realized >= 0 else "DOWN"))
        results["conditions"][cond] = {
            "mean_utility_bps": round(sum(utils) / len(utils) * 1e4, 2),
            "direction_accuracy": round(ok / decided, 3) if decided else None,
            "n_decided": decided,
            "calls_per_decision": {"indep3": 3, "chat3": 6, "seq3": 3, "debate3": 3}[cond],
        }
        rounds = round_stances.get(cond, [])
        if rounds:
            import statistics as _st
            per = [diversity_metrics(r) for r in rounds]
            results["conditions"][cond]["diversity"] = {
                k: (round(_st.mean([p[k] for p in per if p[k] is not None]), 3)
                    if any(p[k] is not None for p in per) else None)
                for k in ["pairwise_agreement", "decision_entropy"]}

    v_comm = (results["conditions"]["chat3"]["mean_utility_bps"]
              - results["conditions"]["indep3"]["mean_utility_bps"])
    results["V_comm_bps"] = round(v_comm, 2)
    results["claim_status"] = "PILOT n=8 — PROVISIONAL at best, no significance claims"

    with open(os.path.join(OUT_DIR, "ec2-results.json"), "w") as fh:
        json.dump(results, fh, indent=2)
    print("\n==== E-C2 ====")
    for cond, r in results["conditions"].items():
        print(f"{cond:>8} util={r['mean_utility_bps']:+8.1f}bps acc={r['direction_accuracy']}")
    print(f"V_comm = {results['V_comm_bps']:+.1f} bps")


if __name__ == "__main__":
    main()
