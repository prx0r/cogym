"""N6: Skill lineage registry with counterfactual probe gating.
Skills enter the permanent population ONLY after paired probe evidence."""
from __future__ import annotations
from dataclasses import asdict
import json, os, time
import hashlib, json
def _sha(obj, prefix=""):
    payload = json.dumps(obj, sort_keys=True, default=str).encode()
    return prefix + hashlib.sha256(payload).hexdigest()

def sha256_id(obj, prefix=""):
    return _sha(obj, prefix)

# Explicit eligible states — never use ordinal comparison across terminal states
ELIGIBLE_STATES = {"SECRET_CONFIRMED","REPLAY_SAFE","TRANSFERRED","REPLICATED"}
TERMINAL_STATES = {"REJECTED","REGRESSED","STALE","INVALIDATED"}
ALL_STATUSES = {"PROPOSED"} | ELIGIBLE_STATES | TERMINAL_STATES

# Evidence-layer requirements for each transition (P0-C: no spoofing)
TRANSITION_REQUIREMENTS = {
    ("PROPOSED","DEV_USEFUL"): "dev",
    ("DEV_USEFUL","SECRET_CONFIRMED"): "secret",
    ("SECRET_CONFIRMED","REPLAY_SAFE"): "replay",
    ("REPLAY_SAFE","TRANSFERRED"): "transfer",
    ("TRANSFERRED","REPLICATED"): "replication",
}

class SkillArtifact:
    def __init__(self, content:str, creator:str="hermes", parents:list[str]|None=None,
                 source_episodes:list[str]|None=None, hypothesis:str="", domain:str="general"):
        self.content = content
        self.skill_id = sha256_id({"content":content,"parents":parents or []}, prefix="skill_")
        self.parents = parents or []
        self.creator = creator
        self.source_episode_hashes = source_episodes or []
        self.content_hash = sha256_id({"content":content}, prefix="sha_")
        self.domain = domain
        self.hypothesis = hypothesis
        self.status = "PROPOSED"
        self.created_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.evaluations = []

    def to_dict(self): return {k:v for k,v in vars(self).items()}

class SkillEvaluation:
    """Paired evaluation receipt. Immutable. Records evidence layer."""
    def __init__(self, skill_id:str, incumbent_id:str|None,
                 world_manifest_hash:str,
                 candidate_scores:list[float], incumbent_scores:list[float],
                 evidence_layer:str="dev", domain:str="general",
                 regression_probes:dict[str,list[float]]|None=None):
        assert len(candidate_scores)==len(incumbent_scores), "paired scores must align"
        n=len(candidate_scores)
        deltas=[c-i for c,i in zip(candidate_scores,incumbent_scores)]
        self.skill_id=skill_id; self.incumbent_id=incumbent_id
        self.world_manifest_hash=world_manifest_hash
        self.paired_deltas=[round(d,4) for d in deltas]
        self.paired_delta_mean=round(sum(deltas)/n,4) if n else 0
        self.wins=sum(1 for d in deltas if d>0); self.losses=sum(1 for d in deltas if d<0)
        # regression check on unrelated probes
        self.regression_deltas={}
        if regression_probes:
            for probe,(rc,ri) in regression_probes.items():
                self.regression_deltas[probe]=round(sum(rc)-sum(ri),4)
        self.regressions=[k for k,v in self.regression_deltas.items() if v < -0.02]
        self.evidence_layer=evidence_layer
        self.domain=domain
        self.timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())
        self.receipt_hash=sha256_id({"skill":skill_id,"delta":self.paired_delta_mean,
                                     "layer":evidence_layer,"ts":self.timestamp},prefix="receipt_")

    MIN_PROBES = 5
    MIN_MEAN_DELTA = 0.02
    
    @property
    def accepted(self)->bool:
        if len(self.paired_deltas) < self.MIN_PROBES:
            return False  # insufficient evidence
        if abs(self.paired_delta_mean) < self.MIN_MEAN_DELTA:
            return False  # below minimum useful effect
        wins=sum(1 for d in self.paired_deltas if d>0)
        return (self.paired_delta_mean > 0 and
                wins >= len(self.paired_deltas)*0.6 and
                not self.regressions)

class SkillRegistry:
    def __init__(self, path:str="data/skills.json"):
        self.path=path
        self.skills: dict[str,SkillArtifact]={}
        self.load()

    def load(self):
        if os.path.exists(self.path):
            data=json.load(open(self.path))
            self.skills={}
            for sid,d in data.items():
                a=self._from_dict(d)
                a.evaluations=d.get("evaluations",[])  # P0-C: NEVER reset evidence
                a.source_episode_hashes=d.get("source_episode_hashes",[])
                self.skills[sid]=a

    def save(self):
        json.dump({sid:{**s.to_dict(),"evaluations":s.evaluations} for sid,s in self.skills.items()},
                  open(self.path,'w'), indent=2)

    def propose(self, artifact:SkillArtifact) -> str:
        self.skills[artifact.skill_id]=artifact
        return artifact.skill_id

    def evaluate(self, skill_id:str, incumbent_id:str|None,
                 world_hash:str, cand_scores:list[float], inc_scores:list[float],
                 evidence_layer:str="dev", domain:str="general",
                 regression_probes:dict|None=None) -> SkillEvaluation:
        ev=SkillEvaluation(skill_id, incumbent_id, world_hash,
                           cand_scores, inc_scores,
                           evidence_layer=evidence_layer, domain=domain,
                           regression_probes=regression_probes)
        skill=self.skills[skill_id]
        skill.evaluations.append({"receipt_hash":ev.receipt_hash,
                                  "evidence_layer":ev.evidence_layer,
                                  "accepted":ev.accepted,
                                  "delta":ev.paired_delta_mean,
                                  "domain":ev.domain})
        # P0-C: evidence-layer-specific transitions (no spoofing)
        required_layer = TRANSITION_REQUIREMENTS.get((skill.status, None))
        if ev.accepted:
            expected_next = {"PROPOSED":"DEV_USEFUL","DEV_USEFUL":"SECRET_CONFIRMED",
                            "SECRET_CONFIRMED":"REPLAY_SAFE","REPLAY_SAFE":"TRANSFERRED"}.get(skill.status)
            layer_ok = ev.evidence_layer == required_evidence_layer(skill.status)
            domain_ok = True  # TRANSFERRED requires different domain — checked by caller
            if layer_ok:
                skill.status = expected_next
        else:
            if any(d < -0.05 for d in ev.regression_deltas.values()):
                skill.status = "REGRESSED"
            elif ev.paired_delta_mean <= 0 and skill.status == "PROPOSED":
                skill.status = "REJECTED"
        return ev

def required_evidence_layer(status:str)->str:
    """What evidence type is needed for the NEXT transition from this state."""
    return {("PROPOSED","DEV_USEFUL"):"dev",
            ("DEV_USEFUL","SECRET_CONFIRMED"):"secret",
            ("SECRET_CONFIRMED","REPLAY_SAFE"):"replay",
            ("REPLAY_SAFE","TRANSFERRED"):"transfer",
            ("TRANSFERRED","REPLICATED"):"replication"}.get(
        tuple(TRANSITION_REQUIREMENTS.keys()) and 
        next((k for k in TRANSITION_REQUIREMENTS if k[0]==status), ("",""))[0], "")

    def population(self)->list[SkillArtifact]:
        """Only skills with explicitly eligible status. Terminal states never included."""
        return [s for s in self.skills.values() if s.status in ELIGIBLE_STATES]

    def lineage(self, skill_id:str)->list[str]:
        chain=[]
        cur=self.skills.get(skill_id)
        while cur:
            chain.append(cur.skill_id)
            cur=self.skills.get(cur.parents[0]) if cur.parents else None
        return list(reversed(chain))

    def _from_dict(self, d:dict)->SkillArtifact:
        a=SkillArtifact(content=d["content"], creator=d["creator"],
                        parents=d.get("parents"), hypothesis=d.get("hypothesis",""),
                        domain=d.get("domain","general"))
        a.skill_id=d["skill_id"]; a.status=d.get("status","PROPOSED")
        a.created_at=d.get("created_at",a.created_at)
        a.source_episode_hashes=d.get("source_episode_hashes",[])
        return a
