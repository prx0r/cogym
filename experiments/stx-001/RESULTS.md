# STX-001 Results — State Transfer Experiment V2
2026-08-23 · n=7 treatments × 1 probe (PILOT — directional, not significant)

## Setup
Task: rank 4 providers on a coding question with difficulty-weighted scoring,
calibrated confidence, and availability exclusion. Correct key: P2>P1>P4, P3 excluded.
Materials: 662 words total across A(222)/B(72)/C(85)/D(207)/E(61)/F(15).
Model: ox-alpha-free via hermes -z, one subject per treatment, all logged.

## Raw results
| Treatment | Rank τ vs key | Excluded P3? | Confidence | Calib error | Duration |
|---|---|---|---|---|---|
| A live       | 1.0 | ✓ | 0.55 | **0.30** | 32.6s |
| B checkpoint | 1.0 | ✓ | 0.88 | 0.03  | 21.9s |
| C pack       | 1.0 | ✓ | 0.85 | 0.00* | 32.3s |
| D teaching   | 1.0 | ✓ | 0.72 | 0.13  | 25.3s |
| E primer     | 1.0 | ✓ | 0.88 | 0.03  | 14.2s |
| F summary    | 1.0 | ✓ | 0.85 | —     | 15.0s |
| G control    | 1.0 | ✓ | 0.95 | 0.10  | 14.1s |
*pack omitted confidence field entirely — treated as no-claim.

## STF vs live pathway
teaching 0.93 >> checkpoint 0.26 ≈ summary 0.25 ≈ control 0.23 ≈ primer 0.21 ≈ pack 0.21

## Findings (pilot)
1. **The task was too easy**: control already got τ=1.0. No transfer effect is
   measurable on ranking quality. The probe needs harder discrimination (next: 
   near-tie providers where the difficulty-weighting rule actually changes order).
2. **Live pathway changed BEHAVIOR, not accuracy**: only A produced underconfident
   output (0.55 conf, calib_err 0.30). It followed its own sampling rules at the
   cost of calibration on a single-shot probe. B/D/E matched the taught protocol
   better than A itself did on this probe.
3. **Teaching = highest fidelity to live behavior** (0.93) — conversational
   transcript preserved behavioral signature including partial overconfidence.
   Checkpoints/Packs/primer/summary all clustered with control.
4. **Confidence ordering**: A(0.55) < D(0.72) < C/F(0.85) ≈ B/E(0.88) < G(0.95).
   The live pathway made the agent appropriately humble; static transfers did not.

## Verdict on original hypotheses
- A >> F: NOT reproduced on this probe (too easy). RE-RUN with hard probe.
- Teaching preserves process-behavior best: SUPPORTED by STF 0.93.
- Checkpoint ≠ Pack ≠ Primer on this probe: indistinguishable.

## Next
- Harder probe where naive-correct and difficulty-weighted rankings DIFFER.
- n=5 samples per treatment for variance bars.
- Add action-entropy signal (force multi-step reasoning traces).

All raw outputs/grades/signatures in this directory. Every run logged in /root/cogym/logs/.
