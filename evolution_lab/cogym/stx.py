"""N4: BehaviorSignature + StateTransferFidelity.
Behavior is measured, never asked for. Fidelity = 1 - distance(sig_src, sig_dst).
"""
from __future__ import annotations
import math
from dataclasses import asdict

SIGNATURE_FIELDS = [
    "accuracy","calibration_error","action_entropy","revision_frequency",
    "tool_choice_entropy","evidence_requests","confidence_shift_mean",
    "hypothesis_switches","adaptation_latency","failure_recovery_rate",
    "tokens_per_episode",
]

def behavior_signature(episodes: list[dict]) -> dict:
    """episodes: per-episode dicts with metrics. Returns normalized signature."""
    if not episodes: return {f: None for f in SIGNATURE_FIELDS}
    def mean(k):
        vals=[e.get(k) for e in episodes if isinstance(e.get(k),(int,float))]
        return sum(vals)/len(vals) if vals else 0.0
    # action entropy: distribution over distinct actions
    acts=[d.get("action") for e in episodes for d in (e.get("decisions") or [])]
    ent=0.0
    if acts:
        from collections import Counter
        c=Counter(acts); n=len(acts)
        ent=-sum((v/n)*math.log2(v/n) for v in c.values())
    sig={}
    sig["accuracy"]=mean("accuracy")
    sig["calibration_error"]=mean("calibration_error")
    sig["action_entropy"]=round(ent,4)
    sig["revision_frequency"]=mean("revision_rate")
    sig["tool_choice_entropy"]=mean("tool_choice_entropy")
    sig["evidence_requests"]=mean("evidence_requests")
    sig["confidence_shift_mean"]=mean("confidence_shift")
    sig["hypothesis_switches"]=mean("hypothesis_switches")
    sig["adaptation_latency"]=mean("adaptation_latency")
    sig["failure_recovery_rate"]=mean("recovery_rate")
    sig["tokens_per_episode"]=round(mean("tokens"),1)
    return sig

def stf(src_sig: dict, dst_sig: dict) -> float:
    """State Transfer Fidelity: 1 - normalized euclidean distance. None fields skip."""
    num=0.0; den=0.0
    for k in SIGNATURE_FIELDS:
        a,b=src_sig.get(k), dst_sig.get(k)
        if a is None or b is None: continue
        scale=max(abs(a),abs(b),1.0)
        num+=(a-b)**2; den+=scale**2
    if den==0: return 0.0
    return round(max(0.0, 1.0 - math.sqrt(num/den)), 4)

def fidelity_matrix(sigs: dict[str,dict]) -> dict[str,dict[str,float]]:
    names=list(sigs)
    return {a:{b:stf(sigs[a],sigs[b]) if a!=b else 1.0 for b in names} for a in names}
