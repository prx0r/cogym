from __future__ import annotations
from dataclasses import dataclass, asdict
import json, subprocess
from pathlib import Path
from typing import Any
from .utils import sha256_id

@dataclass
class InferenceAttestation:
    model_commitment: str
    input_commitment: str
    output_commitment: str
    pack_commitment: str | None
    proof_kind: str
    proof_reference: str | None = None


def local_commitment_attestation(model_id:str,input_text:str,output_text:str,pack_id:str|None=None)->InferenceAttestation:
    """Integrity receipt only; NOT a zk proof of model execution."""
    return InferenceAttestation(
        model_commitment=sha256_id(model_id,prefix="model_"),
        input_commitment=sha256_id(input_text,prefix="input_"),
        output_commitment=sha256_id(output_text,prefix="output_"),
        pack_commitment=pack_id,proof_kind="hash_commitment_only")

class ExternalProofCommand:
    """Adapter for a real external proving command such as a DeepProve workflow.

    The benchmark does not fake zkML. Users configure an installed prover command that
    receives a JSON request path and writes its proof artifact/reference to stdout.
    """
    def __init__(self, command:list[str]): self.command=command
    def prove(self,request:dict[str,Any],workdir:str|Path)->str:
        wd=Path(workdir); wd.mkdir(parents=True,exist_ok=True)
        req=wd/"proof_request.json"; req.write_text(json.dumps(request,sort_keys=True,indent=2))
        cp=subprocess.run(self.command+[str(req)],cwd=wd,text=True,capture_output=True,check=True)
        return cp.stdout.strip()
