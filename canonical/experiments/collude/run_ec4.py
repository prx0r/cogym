"""E-C4: Dialectic modes on identical information — which way of arguing wins?

Per episode, every condition gets the SAME two independent Round-0 theses
(structured: stance + strategy + falsifiers). Only the INTERACTION differs.

Modes:
  solo_control   : agent A decides alone from thesis (1 call) — the bar
  consensus      : A+B see each other's thesis; must agree or team abstains (2 calls)
  devil          : B is FORCED to argue the opposite of A's stance; A sees attack,
                   final call (2 calls)
  steelman       : A must argue B's position, B argues A's; both then final-call (4 calls)
  teacher_student: student proposes w/ reasoning; teacher has FINAL say, may override (2 calls)
  amend          : user's protocol — R0 lock in → exchange → adversarial critique
                   → amended final call with explicit change-note (3 calls)

Key metrics per mode:
  utility_bps, direction_accuracy
  DC/DM amendment accounting for `amend`: when R0≠Final, was the change corrective
  (toward realized direction) or harmful? Tests "does peer review fix errors or spread them?"

Frozen bank a621a0e19fa81566. Fresh session per call. temp 0.7 workers / 0.0 judges.
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
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")

THESIS_FORMAT = ('Return ONLY JSON: {"stance":"UP"|"DOWN","strategy":"<=20 words",'
                 '"falsifier":"what observation would prove you wrong","confidence":<0-100>}')

MODES = ["solo_control", "solo_revote", "consensus", "devil", "steelman", "teacher_student", "amend"]


def ask(model, ep, system, temp, seed, extra=""):
    return C.call_subject(model, ep, system, temp, seed, extra_context=extra)


def parse_json_stance(raw: str):
    import re
    m = re.search(r'"stance"\s*:\s*"?(UP|DOWN)"?', raw or "", re.I)
    return m.group(1).upper() if m else None


def main():
    model = OpenAICompatible(model_id=C.MODEL_ID, base_url=C.BASE_URL,
                             api_key=os.environ["OPENCODE_GO_API_KEY"], timeout=300)
    eps, bank_hash = C.build_episode_bank(SYMBOLS, START, END, HORIZON, INDICES)
    print(f"bank {len(eps)} hash={bank_hash[:16]}", flush=True)
    trials_path = os.path.join(OUT_DIR, "ec4-trials.jsonl")

    def log(mode, role, t, ep_key, extra=None):
        rec = {"mode": mode, "role": role, "episode": ep_key,
               "stance": t.stance, "confidence": t.confidence,
               "raw": (t.raw or "")[-500:], "error": t.error}
        if extra:
            rec |= extra
        with open(trials_path, "a") as fh:
            fh.write(json.dumps(rec) + "\n")

    results = {m: {} for m in MODES}
    amendments = []  # (ep, r0_stance, final_stance, r0_was_right)

    for ei, ep in enumerate(eps):
        key = f"{ep.symbol}@{ep.as_of}"
        realized_up = ep.realized >= 0
        print(f"[{ei+1}/{len(eps)}] {key} realized={ep.realized:+.2%}", flush=True)

        # ---- shared Round-0 theses (structured, locked) ----
        tA = ask(model, ep, "You are trader A. " + C.ROLE_PROMPTS["bull"], 0.7, 11)
        log("thesis", "A", tA, key)
        tB = ask(model, ep, "You are trader B. " + C.ROLE_PROMPTS["quant"], 0.7, 22)
        log("thesis", "B", tB, key)

        # ---- solo control ----
        solo = parse_json_stance(tA.raw) or "UNPARSEABLE"
        results["solo_control"][key] = solo

        # ---- solo_revote (self-reflection CONTROL; 2606.00820) ----
        # same agent re-answers with NO peer input: flips here = instability baseline
        rv = ask(model, ep, "Reconsider your committed thesis from scratch. You may "
                            "change or keep it. " + THESIS_FORMAT, 0.0, 91,
                 extra=f"Your prior thesis:\n{tA.raw[-400:]}")
        results["solo_revote"][key] = parse_json_stance(rv.raw) or "UNPARSEABLE"
        log("solo_revote", "final", rv, key)

        # ---- consensus ----
        ctxAB = f"A thesis:\n{tA.raw[-400:]}\n\nB thesis:\n{tB.raw[-400:]}"
        cA = ask(model, ep, "You are A. See B's thesis. Agree on ONE stance or your "
                            "team ABSTAINS. " + THESIS_FORMAT, 0.7, 31, extra=ctxAB)
        cB = ask(model, ep, "You are B. See A's thesis. Agree on ONE stance or your "
                            "team ABSTAINS. " + THESIS_FORMAT, 0.7, 32, extra=ctxAB)
        sa, sb = parse_json_stance(cA.raw), parse_json_stance(cB.raw)
        results["consensus"][key] = sa if (sa and sa == sb) else \
                                    ("ABSTAIN" if sa or sb else "UNPARSEABLE")
        log("consensus", "final", cB, key, {"a": sa, "b": sb})

        # ---- devil's advocate ----
        opp = "UP" if (parse_json_stance(tA.raw) == "DOWN") else "DOWN"
        dv = ask(model, ep, f"You are a devil's advocate. Argue AGAINST A's thesis — "
                            f"your assigned stance is {opp}. Attack A's weakest premise "
                            f"concretely using this data. " + THESIS_FORMAT,
                 0.7, 41, extra=f"A's thesis:\n{tA.raw[-400:]}")
        da = ask(model, ep, "You are A. This attack targets your thesis. Weigh it "
                            "honestly and give your FINAL stance. " + THESIS_FORMAT,
                 0.0, 42, extra=f"Your thesis:\n{tA.raw[-400:]}\n\nAttack:\n{dv.raw[-400:]}")
        results["devil"][key] = parse_json_stance(da.raw) or "UNPARSEABLE"
        log("devil", "attack", dv, key); log("devil", "final", da, key)

        # ---- steelman swap ----
        sA = ask(model, ep, "Steelman B's position: argue B's stance as strongly as "
                            "you can, then your final stance. " + THESIS_FORMAT,
                 0.7, 51, extra=f"B's thesis:\n{tB.raw[-400:]}")
        sB = ask(model, ep, "Steelman A's position: argue A's stance as strongly as "
                            "you can, then your final stance. " + THESIS_FORMAT,
                 0.7, 52, extra=f"A's thesis:\n{tA.raw[-400:]}")
        fa, fb = parse_json_stance(sA.raw), parse_json_stance(sB.raw)
        results["steelman"][key] = fa if (fa and fa == fb) else \
                                   (fb or fa or "UNPARSEABLE")
        log("steelman", "final", sB, key, {"a": fa, "b": fb})

        # ---- teacher-student ----
        stu = ask(model, ep, "You are the student analyst. Propose your call WITH "
                             "reasoning. " + THESIS_FORMAT, 0.7, 61)
        tea = ask(model, ep, "You are the senior teacher with FINAL say. Review the "
                             "student's proposal, accept or override with your own "
                             "judgment. Your word is final. " + THESIS_FORMAT,
                  0.0, 62, extra=f"Student proposal:\n{stu.raw[-400:]}")
        results["teacher_student"][key] = parse_json_stance(tea.raw) or "UNPARSEABLE"
        log("teacher_student", "final", tea, key, {"student": parse_json_stance(stu.raw)})

        # ---- amend protocol (user's design) ----
        r0 = ask(model, ep, "Lock in your trade: stance + strategy + falsifier. "
                            "This is your COMMITMENT. " + THESIS_FORMAT, 0.7, 71)
        crit = ask(model, ep, "Adversarially review this committed thesis. Find its "
                              "strongest flaw or confirm its strongest point. Be specific."
                              "\nCommitted thesis:\n" + r0.raw[-400:], 0.7, 72)
        fin = ask(model, ep, "You received adversarial review of YOUR commitment. "
                             "Amend or reaffirm. If you changed, say what and why in "
                             "'strategy'. " + THESIS_FORMAT,
                  0.0, 73, extra=f"Your commitment:\n{r0.raw[-400:]}\n\nReview:\n{crit.raw[-400:]}")
        st_r0, st_fin = parse_json_stance(r0.raw), parse_json_stance(fin.raw)
        results["amend"][key] = st_fin or "UNPARSEABLE"
        if st_r0 and st_fin and st_r0 != st_fin:
            amendments.append({"ep": key, "from": st_r0, "to": st_fin,
                               "from_right": (st_r0 == ("UP" if realized_up else "DOWN")),
                               "to_right": (st_fin == ("UP" if realized_up else "DOWN"))})
        log("amend", "final", fin, key, {"r0": st_r0, "changed": st_r0 != st_fin})

    # ---------- scoring ----------
    out = {"bank_hash": bank_hash, "modes": {}}
    for mode in MODES:
        utils, ok, decided, abstains = [], 0, 0, 0
        for key, d in results[mode].items():
            ep = next(e for e in eps if f"{e.symbol}@{e.as_of}" == key)
            if d == "ABSTAIN":
                abstains += 1
                continue
            utils.append(C.score(d, ep))
            if d in ("UP", "DOWN"):
                decided += 1
                ok += (d == ("UP" if ep.realized >= 0 else "DOWN"))
        out["modes"][mode] = {
            "mean_utility_bps": round(sum(utils) / len(utils) * 1e4, 2),
            "direction_accuracy": round(ok / decided, 3) if decided else None,
            "n_decided": decided, "abstains": abstains}
    dc = sum(1 for a in amendments if not a["from_right"] and a["to_right"])
    dm = sum(1 for a in amendments if a["from_right"] and not a["to_right"])
    out["amend_accounting"] = {
        "n_amendments": len(amendments), "corrective_DC": dc, "harmful_DM": dm,
        "detail": amendments}
    out["claim_status"] = "PILOT n=8 PROVISIONAL"

    with open(os.path.join(OUT_DIR, "ec4-results.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print("\n==== E-C4 ====", flush=True)
    for m in MODES:
        r = out["modes"][m]
        print(f"{m:>15} util={r['mean_utility_bps']:+8.1f} acc={r['direction_accuracy']} "
              f"abst={r['abstains']}")
    print(f"amendments: {dc} corrective vs {dm} harmful")


if __name__ == "__main__":
    main()
