# V2 Refactor Baseline — frozen 2026-08-24

Reference commit at PR1: `6f1e75c` (receipts recorded after PR2–PR7 landed).

## Verified state

| Item | Value |
|------|-------|
| Python | 3.11.2 |
| Test suite | 38 passed (`cd canonical && pytest tests/ -q`) |
| Golden fixture | `canonical/tests/golden/trading_v1_episode.json` (world_id 809356de…, pinned price/action/realized) |
| COLLUDE episode bank | hash `a621a0e19fa81566` (frozen, 8 Alpaca episodes) |
| PatternStore bug | FIXED in PR1 (commit 2f86978) — `improved` now writes computed control comparison |

## Known experiment results (pre-refactor, all PILOT mode)

- E-C1: solo == ensemble3 == roles3 utility (106 bps); god_g2 no gain; ensemble costs 3x calls
- E-C2: V_comm = −51.8 bps (communication HURT); debate3 best (+92.8); diversity collapse directionally confirmed
- E-C3: inference complete (64/64 calls), aggregation crashed on dict/attr bug; trials preserved in ec3-trials.jsonl for score-only recovery
- STX-001/002: probe ceiling issues; directional only
- E01 baseline: difficulty scaling confirmed smooth(-1.012) < shock(-1.045) < regime_flip(-1.206)

## What must never drift

1. Golden trading episode through generic contracts
2. World manifest hashes (content-hash commitment scheme)
3. Episode bank hash a621a0e19fa81566 for COLLUDE experiments
4. Determinism property: same seed → identical episode_id + final_output_hash

See `invariants.json` for the machine-readable list.
