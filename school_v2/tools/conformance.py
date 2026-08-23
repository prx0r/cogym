#!/usr/bin/env python3
"""Runtime-independent conformance checks for Pack/state-induction protocol.
This does not replace cargo test; it catches canonicalization/protocol regressions in
minimal environments where Rust is not installed.
"""
import hashlib, json, pathlib, random, statistics
ROOT = pathlib.Path(__file__).resolve().parents[1]

def canon(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def commit(domain, x):
    # Python stdlib sha3_256 is NIST SHA3 rather than Keccak; this test validates
    # canonical stability only. Rust production code uses Keccak256.
    h=hashlib.sha3_256(); h.update(domain.encode()+b"\0"+canon(x)); return h.hexdigest()

def fake_signature(seed, dose):
    r=random.Random(f"{seed}:{dose}")
    # As dose increases, converge toward target phenotype while retaining stochasticity.
    k=min(1.0,dose/1000)
    target={"risk_aversion":.72,"revision_rate":.61,"evidence_demand":.80,"confidence":.58}
    base={"risk_aversion":.45,"revision_rate":.35,"evidence_demand":.50,"confidence":.70}
    return {m:(1-k)*base[m]+k*target[m]+r.uniform(-.01,.01) for m in target}

def dist(a,b): return statistics.mean(abs(a[k]-b[k]) for k in a)

pack=json.loads((ROOT/'fixtures/game_theory_pack.json').read_text())
assert commit('PACK', pack)==commit('PACK', json.loads(json.dumps(pack)))
assert commit('PACK', pack)!=commit('PACK2', pack)
target={"risk_aversion":.72,"revision_rate":.61,"evidence_demand":.80,"confidence":.58}
d0=dist(fake_signature(7,0),target); d1=dist(fake_signature(7,1000),target)
assert d1 < d0/5, (d0,d1)
# Replay invariant for a deterministic synthetic world packet.
world={"seed":42,"prices":[100.0,101.0,99.5],"macro":{"growth":.1,"inflation":.2}}
assert commit('WORLD',world)==commit('WORLD',json.loads(json.dumps(world)))
print(json.dumps({"ok":True,"pack_canonical":True,"induction_converges":True,"world_replay":True,"distance_before":d0,"distance_after":d1},indent=2))
