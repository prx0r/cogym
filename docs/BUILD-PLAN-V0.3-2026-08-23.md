# Cogym Build Plan v0.3 — Scientific Hardening (2026-08-23)
Full review preserved at docs/REVIEW-SCIENTIFIC-INTEGRITY.md. This is the implementation contract.

## P0 — Scientific correctness patch (BEFORE any headline experiment)
1. Secret RNG -> OS entropy drawn AFTER candidate freeze (not seed^0x5EED)
2. Paired incumbent-vs-candidate on IDENTICAL fresh secret batch; anytime-valid acceptance (PACE-style), not naive delta
3. Wire proposal.method=hermes into campaign (C5 currently unused by runner)
4. Fix {failures} interpolation bug in hermes_proposals prompt template
5. Parent-specific proposals (parent_index lineage correctness)
6. STF v2: per-field robust normalization, missingness mask, subscales, bootstrap CI; task improvement separate from phenotypic similarity
7. Campaign logs every candidate/layer incl pooled execution
8. Champion must exist as explicit candidate in every comparison
9. Tests for: secret secrecy, paired acceptor, C5 wiring+interpolation, EventLedger chain, STF v2, campaign logging

## PR-1 — SealedEvaluator
Subject sandbox: candidate artifact + treatment + observations + declared tools + budgets.
NEVER: generator source, oracle, secret seeds, other candidates, prior results, fs outside sandbox, kanban, extra keys.
Canary identifiers in forbidden paths => EVAL_INTEGRITY_VIOLATION invalidates run.

## STX-002 — Hard Reasoning World Generator
5 families: difficulty_weighted_rank | base_rate_shift | confounded_choice | regime_flip | costly_evidence
Each world: oracle + hardness invariant (naive != oracle AND margin>=threshold AND no surface cue).
Ecological arm + budget-matched arm + SHAM-LIVE + SHAM-CONTEXT controls.
n=5/treatment pilot; confirmatory 8-12 sessions x 20-30 paired worlds.

## Phenotypes replace single STF headline
performance / epistemic / policy / adaptation / efficiency vectors.
Statements like "teaching preserved 82% epistemic while retaining 31% policy, improved reward 14pp".

## Experiment ladder after hardening
E1 STX-002 transfer · E2 dose · E3 persistence/washout · E4 representation-per-token
(E4 metric: Transfer Efficiency = hidden improvement / transmitted tokens) · E5 counterfactual
skill utility · E6 curator bake-off (SkillsBench reproduction) · E7 env-change adaptation ·
E8 master/student · E9 cultural chains · E10 cumulative culture · E11 error contagion ·
E12 reputation/receipts · algorithm bake-off (random vs hill-climb vs DGM vs GEPA vs GEA vs hermes)
· KILLER: BASE vs GENOME vs MEMORY vs SKILL vs PACK vs SCHOOL vs SOCIETY -> cross-domain transfer

## ANTI_THEATRE_V2 constitution (20 rules) — repo file ANTI_THEATRE_V2.md

## N6 SkillRegistry spec
SkillArtifact{skill_id=hash,parents[],creator,content_hash,hypothesis,status} +
SkillEvaluation{paired_delta,calibration_delta,cost_delta,replay_delta,OOD_delta}
Lifecycle PROPOSED->DEV_USEFUL->SECRET_CONFIRMED->REPLAY_SAFE->TRANSFERRED->REPLICATED | REJECTED/REGRESSED/STALE

## Frontier anchors
PACE anytime-valid acceptance · DGM archive stepping stones · GEA experience sharing ·
GEPA reflection sample-efficiency · SkillMaster counterfactual gates · SkillOS frozen executor +
evolving curator · SkillsBench self-gen skills ~= no gain · SEAGym train/update-val/test/replay/cost views ·
SEA-Eval equal success can differ 10x tokens · PACE-Bench memory anchoring under env mutation ·
telephone-game cultural attractors · opportunity-cost neglect · Meta-Agent evaluator targeting ·
Reward Hacking Benchmark environmental hardening works.

## Sequencing
P0 -> SealedEvaluator -> HardWorld gen -> STF v2 -> STX-002 -> dose/washout/representation ->
N6 skill registry w/ counterfactual probes -> curator evolution -> master/student -> chains ->
contagion/reputation -> algorithm bake-off -> KILLER STUDY -> cross-domain transfer (Telegraph).
