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

## Frontier Methods (arxiv sweep 2026-08-23) — mapped to our harnesses
| Paper | Method | Our implementation |
|-------|--------|-------------------|
| 2603.06801 AceMAD (Martingale Curse) | peer-prediction: agents predict peers' beliefs; truth-holders anticipate crowd error; proper scoring rules weight aggregation | E-C4e peer_prediction: each agent predicts other's stance+confidence BEFORE reveal; disagreement-weighted vote |
| 2606.00820 Stance Decomposition | separate spontaneous instability vs conformity vs persuasion via self-reflection CONTROL arm | E-C4 adds solo_revote control: same agent re-answers with NO peer info; flips = instability baseline |
| 2509.21054 Persuasion Duality | sharing thinking content boosts persuasion AND resistance | amend mode already shares reasoning; add hidden-reasoning arm (stance-only reveal) to isolate |
| 2602.16639 AREG | persuasion vs resistance weakly coupled (ρ=0.33); verification-seeking beats refusal on defense | E-C5 adversarial peer: measure both how often attacker flips defender AND defender's resistance tactics |
| 2512.06573 Belief-box | belief statements + open-mindedness levels control persuadability | E-C4f belief_box: agents carry explicit belief ledger w/ strengths across rounds |
| EquiMem 2605.09278 | zero-trust memory game, equilibrium-based trust weighting | defer to Hydra memory phase |

## Design rule adopted
Every multi-round mode MUST have a self-reflection control (same rounds, no peer input)
so conformity ≠ instability. (2606.00820 shows ~40% of apparent influence is noise.)
