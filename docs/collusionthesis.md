# COLLUDE THESIS — Artificial Society Market Laboratory
Project codename: **COLLUDE** · saved 2026-08-23
Framing: an experimental economics + complexity-science laboratory in which artificial traders
form teams, communicate, compete, cooperate, deceive, specialize, herd, form coalitions, and
adapt inside a controlled market.

> Collusion/coordination experiments stay ENTIRELY inside the synthetic simulator.
> The scientific question is when cooperation or tacit coordination emerges — never how to
> manipulate a real market.

## Core insight
The god agent isn't the endgame. The endgame is making ORGANIZATIONAL STRUCTURE itself an
experimental variable:

Intelligence = f(agents, information, incentives, network, communication, hierarchy,
memory, market ecology)

Central question:
**Under what conditions does a society of reasoning agents become more intelligent than its
strongest individual — and under what conditions does interaction make the society
collectively stupid?**

## Frontier anchors (verified 2026)
- 2602.03794 Agent scaling via diversity: homogeneous teams saturate (correlated errors);
  two diverse agents can match/exceed larger homogeneous groups; effective channel count K*.
- 2604.18005 Diversity collapse: dense communication → premature convergence, correlated failure.
- 2408.14597 Centralized critics: extra global information can add bias/variance.
- 2407.04622 Debate outperforms consultancy under information asymmetry.
- 2510.05748 Cheap-talk channel changes cooperation in Stag Hunt.
- 2605.03604 Multi-agent strategic games: signaling/reciprocity, finite-horizon unraveling.
- 2602.01011 Self-organizing teams dilute their best member through compromise; worse with size.
- 2506.11285 Shapley Machine: cooperative-game credit assignment for ad hoc teamwork.
- 2510.07799 Communication topology should be learned (AGP, AMAS, Guided Topology Diffusion).
- 2510.22422 Group-size phase transitions; large-N approaches mean-field dynamics.

---

## The ladder (progressive complexity — build ONE rung at a time)

### Track 1 — Controlled causal science (frozen world, World A)
- **L1 Team-size production function**: N ∈ {1,2,3,4,8} at FIXED total inference budget.
  J(n) = performance(n agents, fixed compute); Δ_n = J(n)−J(n−1); cost-adjusted J_c = J − λC.
- **L2 Independent vs talking**: independent | group chat | sequential | debate | god.
  Communication value V_comm = J_chat − J_independent.
- **L3 God variants G0-G6**: nothing | answers | +confidence | +reasoning | +evidence |
  interrogation | answer-first-then-see-workers (anti-anchoring).
  V_G = J_god − best deterministic aggregator; V_R = reasoning-exposure value;
  V_I = interrogation value.
- **L4 Wisdom vs herding**: answers-only / +confidence / +reasoning / discuss-to-consensus.
  Measure pairwise action correlation H and decision entropy. Watch for
  "individual errors moderately correlated → communication → SAME error".
- **L5 Expert suppression**: plant one 90% expert among 60% agents; does the team beat the
  expert or dilute them? Conditions: told/inferred/not.
- **L6 Faulty teammate**: leave-one-out contribution L_i = J(T) − J(T∖{i}); L_i<0 = toxic member.

### Track 2 — Incentives & private information
- Private noisy signals s_i = V_t + ε_i with known Bayes-optimal posterior → score
  D_KL(agent posterior ∥ Bayes posterior).
- Mixed motives R_i = αR_team + (1−α)R_individual, α sweep {0,.25,.5,.75,1}.
- Cheap talk markets: nonbinding messages, identity on/off, repeated games, reputation.
- Shapley credit assignment across all coalitions of ≤3-4 agents.
- Coalition formation + stability (core).

### Track 3 — Endogenous ecology (World B)
- Minority game: strategy crowding, does coordination become overcrowding.
- Replicator dynamics over strategy populations; endogenous alpha decay (∂f_A/∂x_A < 0).
- Topology zoo: independent/complete/ring/star/hierarchy/small-world/dynamic; evolve G*.
- Five god objects: executive, judge, router, critic, regulator.
- PSRO meta-game via OpenSpiel; measure exploitability (NashConv), not just winnings.
- Mean-field limit as N→1000; look for phase transitions, hysteresis, metastability.

## Worlds
- **World A frozen counterfactual**: identical immutable market state per team; actions cannot
  move prices. Clean causal comparisons. (cogym deterministic worlds + real Alpaca replay.)
- **World B endogenous**: actions change prices/liquidity/spreads/observations (ABIDES later,
  JAX-LOB for massive sweeps). Reasoning science in A; game theory/ecology in B.

## Aggregator baselines (always include)
majority vote · confidence-weighted · mean/median · Bayesian (when reliabilities known) ·
best historical agent · random pick. An LLM god must beat THESE, not just "help".

## First factorial flagship (after L1-L3 validate)
N ∈ {1,2,3} × topology {independent, chat, god} × diversity {homo, role, model} ×
information {shared, partitioned, private-noisy} = 81 conditions over a fixed episode bank.
Five headline metrics: Team Gain, Communication Gain, God Gain, Diversity Gain,
Information-Aggregation Gain.

## Infrastructure mapping (reuse cogym, don't rebuild)
cogym EventLedger = append-only truth · SQLite PatternStore canonical · HydraDB projection =
social graph/lineage/influence only · hermes(ox-alpha-free) = subject plane via fresh sessions ·
deterministic Python = control plane/aggregation/scoring · Alpaca replay = World A today,
ABIDES = World B later. PettingZoo-style API only when World B arrives.
