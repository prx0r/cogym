"""STF v2: phenotype-vector comparison. Per-field robust normalization,
missingness mask, preregistered equal weights, subscales, bootstrap CI.
Task improvement is NEVER mixed into phenotypic similarity."""
from __future__ import annotations
import math, random

SUBSCALES = {
    "performance":   ["accuracy","ood_accuracy"],
    "epistemic":     ["calibration_error","evidence_requests","confidence_shift_mean","hypothesis_switches"],
    "policy":        ["action_entropy","revision_frequency","tool_choice_entropy"],
    "adaptation":    ["adaptation_latency","failure_recovery_rate"],
    "efficiency":    ["tokens_per_episode"],
}

def _normalize_fields(sigs: list[dict]) -> dict[str, tuple[float,float,float,float]]:
    """Per-field: (median, MAD-scale, min_observed_range) across ALL subjects being compared."""
    stats={}
    for f in {f for sig in sigs for f,v in sig.items() if isinstance(v,(int,float))}:
        vals=[s[f] for s in sigs if isinstance(s.get(f),(int,float))]
        if len(vals)<2: continue
        vals.sort()
        med=vals[len(vals)//2]
        mad=sorted(abs(v-med) for v in vals)[len(vals)//2] or 1.0
        rng=max(vals)-min(vals) or 1.0
        stats[f]=(med,mad,rng,min(vals),max(vals))
    return stats

def phenotype_vector(sig: dict, field_stats: dict) -> dict[str, float | None]:
    """Robust z-scores; missing fields -> None (explicit missingness)."""
    out={}
    for sub,fields in SUBSCALES.items():
        vals=[]
        for f in fields:
            st=field_stats.get(f)
            if not st or not isinstance(sig.get(f),(int,float)):
                vals.append(None); continue
            med,mad,rng,lo,hi=st
            z=(sig[f]-med)/(1.4826*mad)
            vals.append(max(-3,min(3,z)))
        known=[v for v in vals if v is not None]
        out[sub]= sum(known)/len(known) if known else None
    return out

def subscale_fidelity(src_vec: dict, dst_vec: dict) -> dict[str, float|None]:
    out={}
    for sub in SUBSCALES:
        a,b=src_vec.get(sub), dst_vec.get(sub)
        out[sub]= None if a is None or b is None else round(max(0.0,1-abs(a-b)/6.0),4)
    return out

def bootstrap_stf(src_sig,dst_sig,others:list[dict],n_boot:int=200)->dict:
    """Bootstrap CI on overall fidelity vs the comparison population."""
    rng=random.Random(42)
    vals=[]
    all_sigs=others+[src_sig,dst_sig]
    for _ in range(n_boot):
        sample=rng.choices(all_sigs,k=len(all_sigs))
        fs=_normalize_fields(sample)
        sv=phenotype_vector(src_sig,fs); dv=phenotype_vector(dst_sig,fs)
        subs=subscale_fidelity(sv,dv)
        known=[v for v in subs.values() if v is not None]
        if known: vals.append(sum(known)/len(known))
    vals.sort()
    if not vals: return {}
    return {"mean":round(sum(vals)/len(vals),4),
            "p5":vals[int(.05*len(vals))], "p95":vals[int(.95*len(vals))-1]}
