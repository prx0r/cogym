# COLLUDE Implementation Ledger
Maps every recommendation in docs/collusionthesis.md → code → status.
Rule: nothing counts as implemented until it ran and its outputs exist.

## Deterministic aggregator baselines (thesis §20 — "the best god may be deterministic")
| Baseline | Where | Status |
|----------|-------|--------|
| majority vote | collude.majority | ✅ running in E-C1/C3 |
| confidence-weighted | collude.conf_weighted | ✅ running in E-C1/C3 |
| random pick (seeded, content-hash of episode key) | run_ec3.random_bar | ✅ in E-C3 |
| Bayesian w/ known reliability (train-split est., logit-clipped weights) | run_ec3.bayes_bar | ✅ in E-C3 (test split only) |
| mean/median continuous aggregation | n/a until stance becomes position-sized | ⏳ L2+ |
| best historical agent | needs sequential repeated game | ⏳ Track 2 |

## Track 1 ladder
| Rung | Recommendation | Status |
|------|----------------|--------|
| L1 | N∈{1,2,3,4,8} fixed budget | 🟡 partial: solo/ensemble3/roles3/roles3_conf/god_g2 done; N=2,4,8 arms queued as E-C1b after pilot signal |
| L1 | cost-adjusted J_c = J/calls | ✅ utility_per_call_bps |
| L2 | independent vs chat vs sequential vs debate | ✅ run_ec2.py |
| L2 | V_comm = J_chat − J_indep | ✅ computed |
| L2 | pairwise agreement H + decision entropy 𝓗 (diversity collapse) | ✅ diversity_metrics() patched into ec2 results |
| L3 | god G1 answers / G2 +conf / G3 +reasoning / G6 answer-first | ✅ run_ec3.py scaffolded |
| L3 | V_G vs BEST deterministic bar (incl. RANDOM/BAYES) | ✅ |
| L3 | G4 evidence / G5 interrogation | ⏳ after C3 review |
| L3 | five god objects: executive/judge/router/critic/regulator | 🟡 executive+judge only |
| L4 | reveal granularity wisdom-vs-herding incl. discuss-to-consensus | 🟡 G1-G3 cover granularity; consensus loop missing |
| L5 | expert suppression (planted 90% expert) | ⏳ E-C5 |
| L6 | faulty teammate, leave-one-out L_i | ⏳ E-C6 |

## Track 2 (incentives/private info)
| Item | Status |
|------|--------|
| private noisy signals s_i = V_t + ε_i, D_KL vs Bayes posterior | ⏳ E-T2a (math known ground truth — highest scientific priority next) |
| incentive α-sweep R_i = αR_team+(1−α)R_ind | ⏳ |
| cheap talk: identity/horizon/reputation manipulations | ⏳ |
| Shapley credit assignment over coalitions ≤3 | ⏳ (exact computation feasible at n=3) |
| coalition formation/stability | ⏳ |

## Track 3 (ecology)
minority game · replicator dynamics ∂f/∂x<0 alpha decay · topology evolution ·
PSRO/NashConv exploitability via OpenSpiel · mean-field limit | ⏳ all — gated on one CONFIRMED Track-1 finding

## Diversity arms (§8)
homogeneous ✅ · role-diverse ✅ · model-diverse 🟡 (muse-spark-1.2 fallback approved as 2nd family per AGENTS.md rotation rule) · memory/tool-diverse ⏳

## Statistical discipline
Wilson CI on direction accuracy | 🟡 util wired in repo analysis/, must be added to collude result summaries before any CONFIRMED claim
n_decided ≥ 30 gate | ✅ protocols declare pilot=PROVISIONAL
fresh session/call, temp+seed logged, UNPARSEABLE kept | ✅

## Alpaca data utilization audit (2026-08-23)
| Capability | Used today | Plan |
|-----------|-----------|------|
| daily bars (iex) 4 ETFs | ✅ episode bank v1 | keep as frozen bank |
| hourly/min bars | ❌ | bank v2: intraday confirmation context |
| volume/vwap | ⚠️ volume dropped | v2: include vw premium + volume trend |
| quotes/trades | ❌ | not needed for daily decisions |
| option chains + Greeks/IV | ❌ REQUIRED by hackathon | v2: IV regime context; execution: protective puts/collars for BEAR specialist |
| news API | ❌ | v2: headline sentiment as context arm (isolated variable!) |
| crypto/orderbook | ❌ | out of scope |
| index data (VIX) | ❌ | v2: VIX level as router feature — classic regime signal |
| Trading MCP server (65 tools) | ❌ | wire into hermes for EXECUTION phase (judging: Technology Implementation) |
| paper trading account | ✅ ACTIVE $400k BP, options lvl 3 | deploy selected team Sep window |

## Execution stack decision
World A experiments = direct OpenAICompatible calls (deterministic, logged).
Live deployment = ox-alpha-free supervisor + specialist prompts through official
alpaca-mcp-server (uvx alpaca-mcp-server serve, ALPACA_PAPER_TRADE=true), hermes as host.
