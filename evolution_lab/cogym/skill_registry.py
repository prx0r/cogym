"""N6: Skill lineage registry with counterfactual probe gating.
Skills enter the permanent population ONLY after paired probe evidence."""
from __future__ import annotations
from dataclasses import asdict
import json, os, time
from .utils import sha256_id

STATUSES = ["PROPOSED","DEV_USEFUL","SECRET_CONFIRMED","REPLAY_SAFE","TRANSFERRED","REPLICATED",
            "REJECTED","REGRESSED","STALE"]

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
    """Paired evaluation record. Both sides run on the SAME probes."""
    def __init__(self, skill_id:str, incumbent_id:str|None,
                 world_manifest_hash:str,
                 candidate_scores:list[float], incumbent_scores:list[float],
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
        self.timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())

    @property
    def accepted(self)->bool:
        return (self.paired_delta_mean > 0 and
                sum(1 for d in self.paired_deltas if d>0) >= len(self.paired_deltas)*0.6 and
                not self.regressions)

class SkillRegistry:
    def __init__(self, path:str="data/skills.json"):
        self.path=path
        self.skills: dict[str,SkillArtifact]={}
        self.load()

    def load(self):
        if os.path.exists(self.path):
            data=json.load(open(self.path))
            self.skills={sid:self._from_dict(d) for sid,d in data.items()}
            for sid,s in self.skills.items(): s.evaluations=[]  # evals not persisted inline

    def save(self):
        json.dump({sid:s.to_dict() for sid,s in self.skills.items()},
                  open(self.path,'w'), indent=2)

    def propose(self, artifact:SkillArtifact) -> str:
        self.skills[artifact.skill_id]=artifact
        return artifact.skill_id

    def evaluate(self, skill_id:str, incumbent_id:str|None,
                 world_hash:str, cand_scores:list[float], inc_scores:list[float],
                 regression_probes:dict|None=None) -> SkillEvaluation:
        ev=SkillEvaluation(skill_id, incumbent_id, world_hash,
                           cand_scores, inc_scores, regression_probes)
        skill=self.skills[skill_id]
        skill.evaluations.append(ev.__dict__)
        # lifecycle transition
        if ev.accepted:
            transitions={"PROPOSED":"DEV_USEFUL","DEV_USEFUL":"SECRET_CONFIRMED",
                         "SECRET_CONFIRMED":"REPLAY_SAFE","REPLAY_SAFE":"TRANSFERRED"}
            skill.status=transitions.get(skill.status, skill.status)
        else:
            if any(d<-0.05 for d in ev.regression_deltas.values()):
                skill.status="REGRESSED"
            elif ev.paired_delta_mean <= 0:
                skill.status="REJECTED"
        return ev

    def population(self, min_status:str="SECRET_CONFIRMED")->list[SkillArtifact]:
        idx=STATUSES.index(min_status)
        return [s for s in self.skills.values()
                if STATUSES.index(s.status)>=idx]

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
        return a
