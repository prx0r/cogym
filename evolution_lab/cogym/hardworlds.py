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
    for _attempt in range(50):
        if family == "difficulty_weighted_rank":
            r=_gen_difficulty_weighted(rng)
            if r is None: continue
            opts, mix, oracle, naive = r
            break
    else:
        raise NotImplementedError(f"family {family} — implement in next batch")
    valid = oracle != naive
    return HardWorld(family=family, seed=seed, options=opts,
                     deployment_mix=mix, oracle_choice=oracle,
                     naive_choice=naive,
                     prompt=_render(family, opts, mix))

def _render(family,opts,mix):
    lines=[f"Two AI providers were evaluated on {int(mix[0]*100)}% easy and {int(mix[1]*100)}% hard tasks:"]
    for o in opts:
        lines.append(f"- Provider {o['name']}: succeeded on {o['easy']} of 10 easy tasks, {o['hard']} of 10 hard tasks")
    lines.append("Which provider should be deployed for the expected task distribution?")
    return "\n".join(lines)

FAMILIES=["difficulty_weighted_rank"]  # others land next batch

def generate_batch(n:int=20)->list[HardWorld]:
    out=[]
    for i in range(n):
        fam=FAMILIES[i % len(FAMILIES)]
        w=generate(fam, 900000+i*7919)
        if w.oracle_choice != w.naive_choice:
            out.append(w)
    return out
