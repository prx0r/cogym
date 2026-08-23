# COLLUDE Harness Spec — Game Theory Experiments
## System Prompts (collude.py:18-24)
- homogeneous: "disciplined discretionary trader, 5-day call"
- bull: momentum, continuation, breakouts
- bear: risk, distribution, failed rallies
- quant: base rates, vol regimes, mean reversion
- god: supervisor weighing 3 analysts + confidence

## Harness Topologies (run_ec2.py, run_ec3.py)
1. solo, ensemble3 (same prompt x3), roles3 (bull/bear/quant)
2. indep3 → majority, conf-weighted, random, bayes(train-split)
3. chat3: reveal R1 → R2 revise (V_comm)
4. seq3: A→B→C sequential
5. debate3: bull→bear→judge
6. god G1/G2/G3/G6 vs deterministic bars

## Game Theory Extensions (TODO)
- E-C4: adversarial (bull vs bear zero-sum) vs cooperative (shared reward α=1) — sweep α {0,0.25,0.5,1}
- E-C5: expert suppression (plant 90% expert among 60% noise)
- E-C6: faulty teammate LOO Li = J(T)-J(T\{i})
- E-C7: Shapley value over coalitions ≤3
- E-C8: cheap talk (nonbinding messages, identity on/off, horizon known/unknown)
- Private signals: s_i = V_t + ε_i, D_KL vs Bayes posterior
- Minority game: crowding, replicator dynamics

## Variables
One variable per experiment per AGENTS.md. Episode bank frozen a621a0e19fa81566. Fresh session/call, Wilson CI, n≥30 for CONFIRMED.
