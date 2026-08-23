# COGYM NORTHSTAR — Development Plan (recovered + frontier-validated)
Saved verbatim-in-spirit 2026-08-23. Source: operator review of repo state + self-evolving-agent frontier (DGM, SkillMaster, MAC, A-Evolve, GEA, GEPA).

## Identity
> Cogym = a controlled artificial society for autonomous agents in which
> cognition itself is an observable, transferable and evolvable artifact.

Not a benchmark. A laboratory.

## The central rule
Hermes generates hypotheses/skills/architectures/mutations.
COGYM decides whether they worked. Extraction proposes; benchmark disposes.

## Two planes, hard separation
CONTROL PLANE (knows the experiment): conductor, worldsmith, runner, statistician,
auditor, evolver, replication-agent, reporter — via Hermes Kanban profiles.
SUBJECT PLANE (knows nothing): subject_0001..N — no secret seeds, no evaluator,
no campaign results, no other subjects unless condition allows.

## Anti-theatre religion
Promotion requires DEV -> VALIDATION (hidden from proposers) -> SECRET
(sealed WorldSpecs: generator/evaluator/protocol/metric hashes published before,
random entropy after freeze, commitment+reveal) -> REPLICATION. Later TRANSFER.
Distinguish TASK/FORMAT/TOOL/MODEL/TIMEOUT/POLICY/BENCHMARK failures — malformed output is behavior.

## Next six milestones (the build order)
1. Unified AgentSpec + immutable Episode + append-only event ledger (hashes on every event; derived tables rebuildable)
2. HermesProfileAdapter: fresh/frozen/persistent/skill-only/memory-only profiles instantiated reproducibly
3. STATE_TRANSFER_V2 treatments: A live pathway | B checkpoint | C structured Pack |
   D generated teaching | E static primer | F summary | G naive control
   (A vs B reconstruction; B vs C compression loss; C vs D explicit-vs-teaching;
    D vs E adaptive-vs-fixed; E vs F verbosity; F vs G any transfer)
4. BehaviorSignature vector (accuracy/calibration/entropy/revisions/tool-choice/
   evidence-requests/confidence-shifts/hypothesis-switching/adaptation-latency/
   recovery/tokens/info-order) + StateTransferFidelity = 1 - distance(sig_src, sig_dst)
5. Kanban control plane w/ capability separation:
   worldsmith(no candidate access) / evolver(dev only) / runner(no mutation) /
   statistician(pseudonyms+metrics only) / auditor(hashes post-run) /
   secret-evaluator = deterministic code, NOT hermes
6. Skill lineage registry: skill mutations enter population only after
   counterfactual probe tasks + hidden validation; store parent/child/deltas/regressions

## Experiment families queued (after 1-6)
STX dose-response (0/1/2/3, quantity vs quality) · persistence P0-P3 curricula with
regime shifts · washout/half-life of learned behavior · skill transferability
(master±skill vs fresh±skill vs other-model±skill => model-independent cognitive artifacts?)
· Master->Student transmission metrics incl mistakes/confidence transfer ·
cultural chains A->B->C->D (checkpoint/pack/skill/language channels; fidelity,
myth formation, improvement) · vertical(mutation) vs cultural(transmission) evolution
· social reveal conditions 1-5 (herding/minority recovery) · reputation signals
(identity vs score vs outcomes vs receipts vs receipts+fingerprint) · contagion topologies
(line/star/full; authority/confidence modifiers) · composition topologies as genomes with
cost-normalized quality · pack collision (order/interleave/debate/synthesize) · recombination
(adaptation-module x calibration-module children) · MAP-Elites niches (best teacher/best
student/most robust...) · meta-evolution of the scientist architecture itself · evolution-budget
scaling law (proposals/gen vs hidden gain; Evolution Efficiency, Transfer Efficiency, Teaching
Efficiency) · Hermes-native vs Cogym-gated learning · curator/forgetting curves · era-shift
unlearning/relearning · AgentSEO discovery economy + adversarial overclaimers · synthetic-credit
economic agents · WorkReceipts selection study · phase-two weight training from trajectories
(rejection sampling -> SFT/preference/RL, same hidden eval)

## Repo convergence target
core/(agent_spec, world_spec, episode, events, receipts) worlds/(inference,routing,
resource,coding,discovery,social) organisms/(hermes,frozen,rule_based) state/(memory,skill,
pack,checkpoint,transmission) evolution/(mutation,recombination,archive,selection,hermes_evolver)
experiments/* evaluation/(dev,validation,secret,replication,metrics) orchestration/(hermes,kanban)
registry/ analysis/ cli/ + legacy/(evolution_lab, school_v2, trading_v1)

## Storage
Git=campaign configs · files/R2=world defs · Parquet=raw RunRecords · DuckDB=aggregates ·
SQLite=current episodic memory · Hydra later=lineage/technique relations.
Hydra answers "which technique descended from which"; Parquet answers "mean reward over 4M episodes".

## Compute schedule once stable
40% cognition evolution / 20% world red-team / 15% pack distillation / 10% social /
10% optimizer-vs-optimizer / 5% frontier techniques. Market env stays simulation-only.

## Killer experiment
BASE vs EVOLVED GENOME vs EVOLVED MEMORY vs EVOLVED PACK vs EVOLVED SCHOOL vs
EVOLVED SOCIETY — same model, same unseen worlds, same budget. Measure
generalization/adaptation/calibration/robustness/cost/transfer. Then take the best
Pack/process to a different domain (Ditto/Telegraph). Cross-domain mechanism transfer
is the headline result.

## Frontier anchors
DGM (archive stepping stones, 20->50 SWE-bench) · SkillMaster (counterfactual utility
gates skill edits) · MAC (optimization pressure causes benchmark gaming — hence anti-theatre)
· A-Evolve (evolve workspace files, gate on held-out, rollback regressions) · GEA
(experience sharing across lineages) · GEPA parallel proposals (3-4x wall clock same budget)
· Atropos archived 2026-07-04: borrow abstractions (environment/rollout/trajectory/reward),
never depend on it; export Atropos-like rollout contract for future trainers.
