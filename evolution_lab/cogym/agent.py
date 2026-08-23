from __future__ import annotations
from dataclasses import asdict
import json, math, os, urllib.request
from typing import Protocol
from .schema import AgentGenome, Decision, WorldSnapshot
from .induction import INDUCTIONS, REPRESENTATIONS, REASONING_POLICIES
from .memory import MemoryBackend
from .utils import clamp, canonical_json, sha256_id

class Model(Protocol):
    name: str
    def complete(self, system: str, user: str, temperature: float = 0.0) -> str: ...

class RuleBasedModel:
    """Deterministic model for harness tests. It is not intended as an intelligent baseline."""
    name = "rulebased-v1"
    def complete(self, system: str, user: str, temperature: float = 0.0) -> str:
        data = json.loads(user.split("WORLD_JSON:",1)[1].split("\nEND_WORLD_JSON",1)[0])
        p = data["packet"]
        signal = p["direction"] + 0.6*p["direction_change"] - 30*p["volatility_change"]
        action = "LONG" if signal > 0.35 else "SHORT" if signal < -0.35 else "FLAT"
        er = clamp(signal*0.002, -0.05, 0.05)
        conf = clamp(0.5 + abs(signal)/12, 0.5, 0.95)
        return json.dumps({"action":action,"expected_return":er,"confidence":conf,
                           "rationale":"deterministic regime/momentum baseline", "evidence":["direction","direction_change","volatility_change"]})

class OpenAICompatibleModel:
    """Optional adapter for OpenAI-compatible chat endpoints (e.g. local gateways).

    Requires explicit base URL/API key by the caller. Core tests never make network calls.
    """
    def __init__(self, model: str, base_url: str, api_key: str):
        self.name = model; self.base_url = base_url.rstrip("/"); self.api_key = api_key
    def complete(self, system: str, user: str, temperature: float = 0.0) -> str:
        body = json.dumps({"model":self.name,"temperature":temperature,
                           "messages":[{"role":"system","content":system},{"role":"user","content":user}]}).encode()
        req = urllib.request.Request(self.base_url+"/chat/completions", data=body,
            headers={"Authorization":f"Bearer {self.api_key}","Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=120) as r:
            out = json.load(r)
        return out["choices"][0]["message"]["content"]

class CognitiveAgent:
    def __init__(self, agent_id: str, genome: AgentGenome, model: Model, memory: MemoryBackend):
        self.agent_id=agent_id; self.genome=genome; self.model=model; self.memory=memory

    def context(self, snapshot: WorldSnapshot, peers: list[Decision] | None = None) -> tuple[str,str,str]:
        memories = self.memory.retrieve(self.agent_id, snapshot.packet.metadata.get("latent_regime", "market"),
                                        limit=self.genome.memory_depth, policy=self.genome.memory_policy) if self.genome.memory_depth else []
        system = "\n".join([
            "You are participating in a simulated research benchmark. Do not assume access to future data.",
            INDUCTIONS.get(self.genome.induction, INDUCTIONS["neutral"]),
            REPRESENTATIONS.get(self.genome.representation, REPRESENTATIONS["plain"]),
            REASONING_POLICIES.get(self.genome.reasoning_policy, REASONING_POLICIES["falsification_first"]),
            "Return JSON only with: action LONG|FLAT|SHORT, expected_return, confidence 0..1, rationale, evidence[]."
        ])
        world = {"snapshot_id":snapshot.snapshot_id,"packet":asdict(snapshot.packet),"difficulty":snapshot.difficulty}
        peer_blob=[]
        for d in peers or []:
            item={"agent_id":d.agent_id,"action":d.action}
            if self.genome.reveal in ("decision_confidence","full"):
                item["confidence"]=d.confidence
            if self.genome.reveal=="full":
                item["rationale"]=d.rationale; item["evidence"]=d.evidence
            peer_blob.append(item)
        user = f"WORLD_JSON:{canonical_json(world)}\nEND_WORLD_JSON\n"
        if memories:
            user += "EXPERIENTIAL_MEMORY:\n" + "\n".join(f"- {m.kind}: {m.text} [score={m.score:.3f}]" for m in memories) + "\n"
        if peer_blob:
            user += "PEER_OUTPUTS:"+canonical_json(peer_blob)+"\nYou may KEEP, AMEND, or REVERSE your private decision based on peer evidence."
        return system,user,sha256_id(system,user,prefix="ctx_")

    def decide(self, snapshot: WorldSnapshot, peers: list[Decision] | None = None, private_action=None) -> tuple[Decision,str]:
        system,user,ctx_hash=self.context(snapshot, peers)
        raw=self.model.complete(system,user,self.genome.temperature)
        try:
            start=raw.find("{"); end=raw.rfind("}")+1
            obj=json.loads(raw[start:end])
            action=obj.get("action","FLAT")
            if action not in ("LONG","FLAT","SHORT"): action="FLAT"
            er=float(obj.get("expected_return",0.0)); conf=clamp(float(obj.get("confidence",0.5)),0,1)
            rationale=str(obj.get("rationale","")); evidence=list(obj.get("evidence",[]))
        except Exception:
            action="FLAT"; er=0.0; conf=0.0; rationale="parse_failure"; evidence=[]
        d=Decision(self.agent_id,snapshot.snapshot_id,action,er,conf,rationale,evidence,
                   private_action=private_action,revised=(private_action is not None and action != private_action))
        return d,ctx_hash
