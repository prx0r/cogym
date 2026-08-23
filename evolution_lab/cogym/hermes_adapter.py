"""N2: HermesProfileAdapter - reproducible experimental subjects.
A subject = hermes -z invocation in isolated session with optional injected
treatment material. Treatments map to STX A-G / persistence P0-P3.
"""
from __future__ import annotations
import os, subprocess, time
from dataclasses import dataclass

@dataclass(frozen=True)
class SubjectSpec:
    name: str
    treatment: str            # G F E D C B A (or P0..P3)
    model: str | None = None  # None => hermes default
    profile: str | None = None
    context_path: str | None = None

def run_subject(spec: SubjectSpec, task_prompt: str, timeout: int = 600,
                log_dir: str = "/root/cogym/logs") -> dict:
    os.makedirs(log_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    log = os.path.join(log_dir, f"subject-{spec.name}-{ts}.log")
    cmd = ["hermes"]
    if spec.model: cmd += ["-m", spec.model]
    if spec.profile: cmd += ["--profile", spec.profile]
    content = ""
    if spec.context_path and os.path.exists(spec.context_path):
        content = open(spec.context_path).read()
    full_prompt = (content + "\n\n" if content else "") + task_prompt
    cmd += ["-z", full_prompt]
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        out, rc = r.stdout or r.stderr or "", r.returncode
    except subprocess.TimeoutExpired:
        out, rc = "", -9
    dur = time.time() - t0
    with open(log, "w") as f:
        f.write(f"=== subject {spec.name} treatment={spec.treatment} rc={rc} dur={dur:.0f}s\n")
        f.write(f"--- TASK ---\n{task_prompt[:2000]}\n--- CONTEXT ({len(content)} chars) ---\n--- OUTPUT ---\n{out}")
    return {"subject": spec.name, "treatment": spec.treatment,
            "exit": rc, "duration_s": round(dur,1), "output": out, "log": log}

def make_treatments(base_name: str, materials_dir: str) -> list[SubjectSpec]:
    mat = lambda f: os.path.join(materials_dir, f)
    return [
        SubjectSpec(base_name+"-A", "live",       None, None, mat("A_live.md")),
        SubjectSpec(base_name+"-B", "checkpoint", None, None, mat("B_checkpoint.json")),
        SubjectSpec(base_name+"-C", "pack",       None, None, mat("C_pack.md")),
        SubjectSpec(base_name+"-D", "teaching",   None, None, mat("D_teaching.md")),
        SubjectSpec(base_name+"-E", "primer",     None, None, mat("E_primer.md")),
        SubjectSpec(base_name+"-F", "summary",    None, None, mat("F_summary.md")),
        SubjectSpec(base_name+"-G", "control",    None, None, None),
    ]
