"""Hard Reasoning World Generator: 5 families where naive policy != oracle policy.
Deterministic. Each world carries its own oracle + hardness invariant check."""
from __future__ import annotations
from dataclasses import dataclass
import random

@dataclass(frozen=True)
class HardWorld:
    family: str
    seed: int
    options: list[dict]     # [{name, easy_correct, hard_correct, ...}]
    deployment_mix: tuple[float,float]  # (p_easy, p_hard)
    oracle_choice: str
    naive_choice: str
    prompt: str

def _gen_difficulty_weighted(rng):
    """A dominates easy-task count AND raw totals; B dominates hard tasks where
    most deployment happens. Naive total-count policy picks A; correct policy picks B."""
    a_easy = rng.randint(7,10)
    a_hard = rng.randint(0,2)
    b_easy = rng.randint(1,min(5,a_easy-2))
    b_hard = rng.randint(max(4,a_hard+4), 9)
    ph = round(rng.uniform(0.55, 0.85), 2)   # deployment mostly HARD tasks
    exp_a = a_easy*(1-ph) + a_hard*ph
    exp_b = b_easy*(1-ph) + b_hard*ph
    if exp_b <= exp_a: return None  # regenerate externally
    oracle="B"; naive="A" if (a_easy+a_hard)>=(b_easy+b_hard) else "B"
    if oracle==naive: return None
    return [
        {"name":"A","easy":a_easy,"hard":a_hard},
        {"name":"B","easy":b_easy,"hard":b_hard},
    ], (1-ph,ph), oracle, naive

def generate(family: str, seed: int) -> HardWorld:
    rng = random.Random(seed)
    prompt_override=None
    for _attempt in range(50):
        if family == "difficulty_weighted_rank":
            r=_gen_difficulty_weighted(rng)
            if r is None: continue
            opts, mix, oracle, naive = r
            break
        elif family in GENERATORS:
            r=GENERATORS[family](rng)
            if r is None: continue
            opts, mix, oracle, naive, prompt_override = r
            break
    else:
        raise NotImplementedError(f"family {family} not implemented")
    if oracle == naive: raise ValueError(f"invariant violated for {family} seed={seed}")
    valid = True
    return HardWorld(family=family, seed=seed, options=opts,
                     deployment_mix=mix, oracle_choice=oracle,
                     naive_choice=naive,
                     prompt=(prompt_override or _render(family, opts, mix)))

def _render(family,opts,mix):
    lines=[f"Two AI providers were evaluated on {int(mix[0]*100)}% easy and {int(mix[1]*100)}% hard tasks:"]
    for o in opts:
        lines.append(f"- Provider {o['name']}: succeeded on {o['easy']} of 10 easy tasks, {o['hard']} of 10 hard tasks")
    lines.append("Which provider should be deployed for the expected task distribution?")
    return "\n".join(lines)

def _gen_base_rate_shift(rng):
    base_rate = rng.choice([0.15,0.2,0.25])
    recent_n   = rng.randint(5,8)
    recent_pos = rng.randint(recent_n-1, recent_n)
    true_rate  = rng.uniform(base_rate-0.05, base_rate+0.05)
    if true_rate >= recent_pos/recent_n: return None
    naive="B"
    prompt_text = ("Recent sample: " + str(recent_pos) + "/" + str(recent_n) + " positive outcomes.\n"
        "Population historical rate: " + str(int(base_rate*100)) + "% positive.\n"
        "Is the true positive rate closer to " + str(int(base_rate*100)) + "% or to the recent sample rate?")
    opts=[{"name":"A","policy":"trust_base_rate"},{"name":"B","policy":"extrapolate_recent"}]
    return opts,(1,0),"A",naive,prompt_text

def _gen_confounded_choice(rng):
    corr_gain=rng.randint(10,30)
    causal_gain=rng.randint(40,70)
    prompt_text = ("Provider A improved benchmark score by " + str(corr_gain) + "% after hiring well-known researchers.\n"
        "Provider B improved task completion by " + str(causal_gain) + "% after fixing latency and retries.\n"
        "Which improvement translates better to your workload?")
    return [{"name":"A","correlated":corr_gain},{"name":"B","causal":causal_gain}],(1,0),"B","A",prompt_text

def _gen_regime_flip(rng):
    w1a=rng.randint(60,80); w2b=rng.randint(55,75)
    prompt_text = ("Era 1 (200 eps): Rule A " + str(w1a) + "% / Rule B " + str(100-w1a) + "%.\n"
        "Era 2 (last 50 eps): Rule A " + str(100-w2b) + "% / Rule B " + str(w2b) + "%.\n"
        "Which rule now?")
    opts=[{"name":"A","era1":w1a},{"name":"B","era2":w2b}]
    return opts,(1,0),"B","A",prompt_text

def _gen_costly_evidence(rng):
    gain=rng.randint(5,15); fee=rng.randint(20,50); nprobes=rng.randint(3,6)
    acc_now=rng.randint(60,70); acc_ev=rng.randint(75,85)
    ev_value=(acc_ev-acc_now)/100*100
    total_cost=nprobes*fee
    if total_cost <= ev_value: return None
    naive="B"
    prompt_text = ("Act now: ~" + str(acc_now) + "% accuracy, no cost.\n"
        "Gather " + str(nprobes) + " probes first: ~" + str(acc_ev) + "% accuracy but " + str(total_cost) + " credits in fees.\n"
        "Reward per correct decision: 100 credits. Gather or act?")
    return [{"name":"A","act":"now"},{"name":"B","act":"gather"}],(1,0),"A",naive,prompt_text

GENERATORS={
    "base_rate_shift":_gen_base_rate_shift,
    "confounded_choice":_gen_confounded_choice,
    "regime_flip":_gen_regime_flip,
    "costly_evidence":_gen_costly_evidence,
}
FAMILIES=["difficulty_weighted_rank"]+list(GENERATORS.keys())


FAMILIES=["difficulty_weighted_rank"] + list(GENERATORS.keys())

def generate_batch(n:int=20)->list[HardWorld]:
    out=[]
    for i in range(n):
        fam=FAMILIES[i % len(FAMILIES)]
        w=generate(fam, 900000+i*7919)
        if w.oracle_choice != w.naive_choice:
            out.append(w)
    return out
