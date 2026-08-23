# Experiment Log — All Runs Tracked

| # | ID | Date | Model | Worlds | Samples | Status | Key Finding |
|---|-----|------|-------|--------|---------|--------|-------------|
| 1 | STX-001 | 2026-08-23 | ox-alpha-free | 1 (too easy) | 1/treat | ✅ Done | Probe at ceiling — no discrimination |
| 2 | STX-002 | 2026-08-23 | ox-alpha-free | 15 hard | 1/treat | ✅ Done | checkpoint/pack=100%, live=73%, control=87% |
| 3 | E01-baseline | 2026-08-23 | muse-spark-1.2 | 3 sequential | 3/world | 🔄 Running | First real LLM inference through trading_v1 |

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
