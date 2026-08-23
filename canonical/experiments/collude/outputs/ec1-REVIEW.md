# E-C1 Peer Review — 2026-08-23

## Verdict: PROVISIONAL (n=8, pilot)
All conditions 62.5% direction accuracy — indistinguishable at this n.
Wilson CI at n=8 is ~ [0.30, 0.86] — never significant. Need n≥30 per AGENTS.md for CONFIRMED.

## Findings (directional only)
- solo 106bps / ensemble3 106bps — homogeneous ensemble added zero diversity (up_share 0.875 both). As expected from thesis (homogeneous errors correlated).
- roles3 80bps / god_g2 80bps — role diversity *hurt* here (small sample, bull-window bias). God G2 just parroted majority; V_G = 0 vs roles3. Need G3 (+reasoning) to test V_R.
- roles3_conf bug: call_stats n_calls=0, brier=0.25 — conf-weighted was derived not separately called, and confidence not captured for aggregation. Fix: compute CW Brier properly.

## Pristine fixes queued
1. Fix roles3_conf Brier → compute from actual confidences
2. De-duplicate ec1-trials.jsonl (127 lines vs 64 expected — stale append)
3. Add Wilson CI to results.json even at pilot n
4. E-C1b: expand to n=30+ frozen episodes for real power

## Next
E-C2 (communication value) now running — will show H (pairwise agreement) and entropy.
