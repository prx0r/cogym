from __future__ import annotations
from dataclasses import asdict
import json
from pathlib import Path
from typing import Any
from .schema import CognitivePack, AgentGenome, BenchmarkResult
from .utils import canonical_json, sha256_id

class PackBuilder:
    """Creates immutable cognitive packs from a genome + context modules + evidence."""
    @staticmethod
    def build(name:str,version:str,genome:AgentGenome,context_modules:list[str],
              benchmark_results:list[BenchmarkResult],memory_seeds:list[dict[str,Any]]|None=None,
              provenance:dict[str,Any]|None=None)->CognitivePack:
        contract={
            "claim_type":"empirical_behavioral_specialization",
            "guarantees":["deterministic pack composition","committed benchmark configuration"],
            "non_guarantees":["future behavior","sentience/emotion","unseen-distribution performance","model-weight identity without external proof"]
        }
        proof={"context_commitment":sha256_id(context_modules,prefix="ctxcommit_"),
               "benchmark_commitment":sha256_id([asdict(r) for r in benchmark_results],prefix="benchcommit_")}
        return CognitivePack(name,version,genome,tuple(context_modules),tuple(memory_seeds or []),
                             contract,tuple(benchmark_results),provenance or {},proof)

    @staticmethod
    def save(pack:CognitivePack,path:str|Path)->Path:
        p=Path(path)
        obj=asdict(pack); obj["pack_id"]=pack.pack_id
        p.write_text(json.dumps(obj,sort_keys=True,indent=2))
        return p

    @staticmethod
    def verify_file(path:str|Path)->dict[str,Any]:
        obj=json.loads(Path(path).read_text())
        claimed=obj.pop("pack_id")
        # Rebuild only commitment-bearing body according to CognitivePack.pack_id semantics.
        g=AgentGenome(**obj["genome"])
        br=[BenchmarkResult(**x) for x in obj.get("benchmark_results",[])]
        pack=CognitivePack(obj["name"],obj["version"],g,tuple(obj["context_modules"]),
                           tuple(obj.get("memory_seeds",[])),obj.get("behavioral_contract",{}),
                           tuple(br),obj.get("provenance",{}),obj.get("proof_manifest",{}))
        return {"valid":pack.pack_id==claimed,"claimed":claimed,"computed":pack.pack_id}


def compose_pack_context(pack:CognitivePack,base_system:str="")->str:
    """Deterministically compose a pack into an agent system context."""
    pieces=[base_system.strip()] if base_system.strip() else []
    pieces.extend(pack.context_modules)
    if pack.memory_seeds:
        pieces.append("PACK_SEEDED_EXPERIENCE:\n"+"\n".join(canonical_json(x) for x in pack.memory_seeds))
    return "\n\n".join(pieces)
