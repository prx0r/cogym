"""C5: Hermes proposal adapter.

Turns DEV-layer failure data + elite archive into CandidateSpec mutations via
`hermes -z` (deterministic post-processing: only fields from the genome's own
mutation spaces are accepted; everything else is dropped).

Extraction proposes. The benchmark disposes.
"""
from __future__ import annotations
import json, os, re, subprocess, tempfile

from .schema import AgentGenome
from .evolution import INDUCTIONS, REPS, REASON, MEM, SOCIAL, REVEAL

SPACES = {
    "reasoning_policy": REASON, "representation": REPS,
    "induction": INDUCTIONS, "memory_policy": MEM,
    "social_topology": SOCIAL, "reveal": REVEAL,
}

PROMPT_TEMPLATE = """You are proposing cognitive-architecture mutations for an evolving market agent.

CHAMPION/ELITE GENOME:
{genome_json}

DEV FAILURES (world_name, seed, mean_reward, calibration_error, adaptation_latency):
{failures_json}

MUTATION SPACES (only these fields may change; values must come exactly from these lists):
reasoning_policy: {reason}
representation: {reps}
induction: {inductions}
memory_policy: {mem}
social_topology: {social}
reveal: {reveal}
memory_depth: integer 0..8
revision_rounds: integer 0..1

TASK: propose {n} mutations most likely to fix the observed failures without
breaking what works. Prefer hypotheses that explain WHY a change addresses the
failure pattern.

Return ONLY a JSON array like:
[{{{{"hypothesis":"...", "changes":{{{{"reasoning_policy":"causal","memory_depth":6}}}}}}}}]
"""

def _run_hermes(prompt: str, timeout: int = 420) -> str:
    env = dict(os.environ)
    out = subprocess.run(["hermes", "-z", prompt], capture_output=True,
                         text=True, timeout=timeout, env=env)
    return out.stdout or out.stderr or ""

def propose_mutations(parents: list[AgentGenome], failures: list[dict],
                      n: int = 8, model: str | None = None) -> list[dict]:
    """Returns [{'hypothesis':str,'changes':dict,'parent_index':i}] validated against spaces."""
    if not parents:
        return []
    # P0-5: cycle through ALL parents so each proposal derives from its stated parent
    parent_idx = 0
    parent = parents[0]
    prompt = PROMPT_TEMPLATE.format(
        genome_json=json.dumps({k: v for k, v in
            {"reasoning_policy":parent.reasoning_policy,"representation":parent.representation,
             "induction":parent.induction,"memory_policy":parent.memory_policy,
             "memory_depth":parent.memory_depth,"social_topology":parent.social_topology,
             "reveal":parent.reveal,"revision_rounds":parent.revision_rounds}.items()}, indent=1),
        parent_index=0,
        failures_json=json.dumps(failures[:12], indent=1),
        reason=", ".join(REASON), reps=", ".join(REPS),
        inductions=", ".join(INDUCTIONS), mem=", ".join(MEM),
        social=", ".join(SOCIAL), reveal=", ".join(REVEAL), n=n)
    raw = _run_hermes(prompt)
    m = re.search(r"\[.*\]", raw, re.S)
    if not m:
        return []
    try:
        props = json.loads(m.group(0))
    except Exception:
        return []

    out = []
    for i, p in enumerate(props[:n]):
        changes = {}
        for k, allowed in SPACES.items():
            v = p.get("changes", {}).get(k)
            if v in allowed:
                changes[k] = v
        md = p.get("changes", {}).get("memory_depth")
        if isinstance(md, int) and 0 <= md <= 8:
            changes["memory_depth"] = md
        rr = p.get("changes", {}).get("revision_rounds")
        if rr in (0, 1):
            changes["revision_rounds"] = rr
        if not changes:
            continue
        out.append({"hypothesis": str(p.get("hypothesis", ""))[:300],
                    "changes": changes, "parent_index": i % max(1,len(parents))})
    return out

def apply_mutations(parents: list[AgentGenome], proposals: list[dict]) -> list[AgentGenome]:
    from dataclasses import replace
    kids = []
    for pr in proposals:
        idx = pr.get("parent_index", 0) % max(1, len(parents))
        meta = dict(parents[idx].metadata or {})
        meta["hypothesis"] = pr.get("hypothesis", "")
        meta["origin"] = "hermes"
        kids.append(replace(parents[idx], metadata=meta, **pr["changes"]))
    return kids
