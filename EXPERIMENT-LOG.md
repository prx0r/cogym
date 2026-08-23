# Experiment Log — All Runs Tracked

| # | ID | Date | Model | Worlds | Samples | Status | Key Finding |
|---|-----|------|-------|--------|---------|--------|-------------|
| 1 | STX-001 | 2026-08-23 | ox-alpha-free | 1 (too easy) | 1/treat | ✅ Done | Probe at ceiling — no discrimination |
| 2 | STX-002 | 2026-08-23 | ox-alpha-free | 15 hard | 1/treat | ✅ Done | checkpoint/pack=100%, live=73%, control=87% |
| 3 | E01-baseline | 2026-08-23 | muse-spark-1.2 | 3 sequential | 3/world | 🔄 Running | First real LLM inference through trading_v1 |
| 4 | ALPACA-MOE-001/002 | 2026-08-23 | none (deterministic) | SPY/QQQ/TLT/GLD real bars | 364 steps | ✅ Done | Regimes segment cleanly; hand-routed team LOSES to buy&hold in bull window; shorts whipsawed. Specialists must be tournament-selected, not hand-assigned |
| 5 | COLLUDE E-C1 | 2026-08-23 | ox-alpha-free | 8 frozen Alpaca episodes | 64 calls | 🔄 Running | Team production function: solo vs ensemble3 vs roles3 vs conf-weighted vs god_g2 |
| 6 | COLLUDE E-C2 | queued | ox-alpha-free | same bank a621a0e1 | ~104 calls | ⏳ | Communication value V_comm = chat − independent; diversity collapse check |

## Peer Review Findings
### STX-001
- Probe at ceiling — no discrimination possible
- Calibration DID vary: live=0.30 vs checkpoint=0.03
- Lesson: need harder probes

### STX-002  
- Checkpoint/pack = 100% but n=1 per world per treatment
- Live pathway UNDERPERFORMED control (-13.4%)
- Base-rate shift hardest family for all treatments
- Material token counts vary 15x — confound not controlled
- Format matching confound: checkpoint/pack output JSON matches probe format

## What's Next After E01
1. If E01 shows meaningful variation across worlds → proceed to E02 persistence test
2. If E01 shows no variation → need harder worlds or more complex decisions
3. Import ChatGPT discovery candidates into hackathonhelp
4. Run STX-003 with n=5 on best-performing world families from E01/E02
