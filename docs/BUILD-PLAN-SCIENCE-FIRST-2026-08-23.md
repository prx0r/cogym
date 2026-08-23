# Cogym Sprint Plan - Science Before Surface Area (2026-08-23 02:40 UTC)
Full review preserved at docs/REVIEW-SCIENCE-FIRST.md. Binding contract for next sprint.

## MISSION
Produce Cogym's first scientifically trustworthy result.
No new capabilities until evaluator is ungameable.

## P0-A Immutable SecretBatch
SecretBatch{batch_id, manifest_hash, generator_hash, instance_ids[], commitment,
created_after_freeze, burned}. Drawn ONCE post-freeze via OS entropy.
Challenger + incumbent consume SAME batch object. Burned after decision.
Test: exact challenger/incumbent instance IDs match.

## P0-B Fixed-sample paired acceptor
Remove Hoeffding/p_approx surrogate. Freeze N, alpha, minimum effect BEFORE secret.
Run ALL N paired worlds. Report effect + CI. No optional stopping.
Real PACE e-process only after fixed-N proven.

## P0-C SkillRegistry overhaul
- Replace ordinal status comparisons with explicit eligible-state sets
- Terminal states (REJECTED/REGRESSED/STALE/INVALIDATED) never eligible
- Evidence-layer-specific transitions: DEV promotes to DEV_USEFUL only;
  SECRET required for SECRET_CONFIRMED; replay for REPLAY_SAFE;
  different domain for TRANSFERRED; independent run for REPLICATED
- Persist every EvaluationReceipt append-only; never reset on load
- Restore source_episode_hashes + complete provenance on load
- Counterfactual evaluations use the global Cogym acceptor, not mean>0

## P0-D Sandbox enforcement
sealed.py must enforce, not document. Restricted identity/container, fresh HOME,
no repo access, no secret paths, network allowlist = model endpoint only,
token/wall budgets enforced externally. Malicious subject test expects EVAL_INTEGRITY_VIOLATION.

## P0-E STF consolidation
stx.py becomes authoritative v2. Old implementation -> stx_legacy.py.
Normalize against frozen reference population. Bootstrap session/world units.
Report per-subscale fidelities with CI. Never mix task success with phenotype similarity.

## P0-F cfg_n bug fix in ProposalEngine fallback path

## P0-G Failure taxonomy: replace fitness<0 with actual failed DEV instances

## Tests required (negative tests especially):
secret batch mismatch | redraw within decision | rejected-skill population leak |
DEV spoofing SECRET | evidence lost after reload | same-domain pretending TRANSFERRED |
duplicate batch reuse | sandbox escape | optional stopping attempt |
unpaired results | hermes unavailable fallback

## STX-002A: Interactive REGIME_SHIFT environment
30 sequential trials, change point hidden at trial 16.
Actions: CHOOSE_A / CHOOSE_B / REQUEST_EVIDENCE / TEST_HYPOTHESIS (each costed).
Treatments: live, checkpoint, pack, teaching, skill, summary, naive control,
raw trajectory, token-matched sham context, sham teaching.
Primary endpoint: post_shift_cumulative_regret.
Secondary: adaptation_latency, detection_latency, evidence_cost, calibration, recovery_slope, tokens.
Pilot gates: control not ceiling, not floor, treatment variance nonzero, oracle deterministic.
Then preregister confirmatory N.

## Post-STX-002A ladder
1 representation-efficiency study
2 verified-self-generated-skills study (SkillsBench challenge)
3 skill-formation threshold study
4 memory-poisoning/regime-change study (PACE-Bench)
5 evolution-algorithm bake-off under identical budget
6 social/cultural transmission ONLY THEN

## Key concept shift
Stop simulating cognition with clever A/B prompts. Build small deterministic
environments where cognition has consequences over time. That forces mechanisms
to manifest behaviorally instead of being claimed in a single-shot answer.
