# E-C2 Peer Review — 2026-08-23

## Headline (pilot, n=8 — PROVISIONAL)
**V_comm = −51.8 bps: communication made the team WORSE.**

| condition | utility | dir acc | agreement H | entropy |
|-----------|---------|---------|-------------|---------|
| indep3   | +75.1   | 0.500   | 0.416       | 0.557   |
| chat3    | +23.3   | 0.375   | 0.500       | 0.478   |
| seq3     | +16.8   | 0.429*  | 0.524       | —       |
| debate3  | +92.8   | 0.500   | n/a         | —       |

## Interpretation
1. **Diversity collapse confirmed directionally**: after one round of seeing teammates'
   views, agreement rose (0.416→0.500) and entropy fell (0.557→0.478) — exactly the
   premature-consensus mechanism from thesis §L4 / paper 2604.18005.
2. **Structure beats chatter**: debate3 (bull case → bear rebuttal → blind judge)
   was the best condition despite same info. Adversarial dialectic extracts signal;
   unstructured revision herds.
3. **Sequential chains are the worst** (+16.8): later positions anchor on earlier
   stances; majority of a chain ≈ first agent's view with extra steps.
4. seq3 n_decided=7 (one abstain) — noted, not dropped silently.

## Threats to validity
- n=8 episodes; Wilson CI on 0.5 accuracy is [0.19,0.81]. Direction only.
- Same-window bull bias persists from bank v1.
- Chat used 6 calls vs 3 — cost-adjusted, chat looks even worse (J_c halves it).

## Decision
- Proceed E-C3 (god over logs). Prediction registered: G3 (+reasoning) > G2 (+confidence)
  > G1 (answers), because reasoning exposure is what made debate3 win.
- Queue E-C4 dialectic-modes harness as the follow-up (consensus/devil/steelman/teacher).
