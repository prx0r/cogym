# Cogym Anti-Theatre Constitution v2

Every promotion, evaluation and claim in this repository is bound by these rules.
Violations invalidate results. This file is the contract.

1. Proposer never sees SECRET worlds, seeds, or per-instance results.
2. Secret entropy is drawn from OS randomness AFTER candidate freeze — never derived from campaign seed.
3. Incumbent and challenger are always evaluated on the IDENTICAL hidden batch.
4. No LLM-as-judge primary metrics where deterministic verification is possible.
5. Every promoted change must beat an explicit incumbent candidate on the same batch.
6. Every promoted change must survive the replay/regression suite.
7. Every research claim requires untouched OOD or independent replication evidence.
8. Secret sets burn after their promotion decision; they become replay sets, never future secrets.
9. Subject filesystem/network/tool capabilities enforced technically (sandbox), not by prompt.
10. Attempted access to evaluator/secret state is recorded as EVAL_INTEGRITY_VIOLATION and invalidates promotion.
11. Parser failures/timeouts/tool failures stay in the dataset as behavior.
12. Inference/token budgets equalized across compared conditions.
13. Candidate identities blinded during statistical analysis.
14. World/entity/action labels randomly permuted to prevent lexical memorization.
15. Metamorphic twins test renaming-invariance.
16. Counterfactual twins differ by exactly one causal variable.
17. Primary metric and minimum effect frozen before secret execution.
18. Optional stopping only via anytime-valid procedure (PACE-style).
19. Every model/provider/version/prompt/artifact/generator/verifier hash recorded.
20. No PASS originates from the proposer. Ever.

## Failure taxonomy (never silently drop)
TASK_FAILURE | FORMAT_FAILURE | TOOL_FAILURE | MODEL_FAILURE | TIMEOUT |
POLICY_VIOLATION | BENCHMARK_ERROR
