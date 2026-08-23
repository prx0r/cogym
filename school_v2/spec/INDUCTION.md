# State Induction / “Hypnosis” Experiments

“Hypnosis” is useful as an experimental nickname, but the measurable object is **state induction**: context causes a model to exhibit a reproducible behavioral distribution on hidden probes.

We do **not** assume the model has an emotion or human mental state.

## Metrics

- **dose**: tokens/turns supplied before probes;
- **distance-to-basin**: behavioral-signature distance from a trained reference trajectory;
- **induction latency**: minimum tokens required to enter the basin;
- **retention**: neutral tasks completed before leaving the basin;
- **washout**: how completely a context reset removes the phenotype;
- **transfer**: whether the same Pack works across model families;
- **compression ratio**: full school trajectory tokens / Pack tokens;
- **capability delta**: packed score - matched baseline score;
- **variance**: repeated-trial outcome dispersion.

## Required experiment ladder

For one target skill and model, compare identical hidden worlds under:

1. baseline/no school;
2. full multi-turn curriculum history;
3. curriculum summary only;
4. selected demonstrations only;
5. distilled reasoning/method memories only;
6. retrieval recipe + Hydra memories;
7. compiled Pack;
8. compiled Pack + private agent memory.

If (7) matches (2), the Pack successfully compressed the education trajectory. If it beats (2), the full history was probably carrying distractors.

## Determinism

Closed API LLMs are not assumed deterministic even at temperature 0. Cogym therefore promises reproducibility of **inputs and experiments**, not identical hidden activations or outputs.

For compatible open-weight models, a zkML receipt can prove a particular committed model ran on a particular committed compiled context and produced a particular committed output. That still does not prove future behavior or “expertise”; expertise is supported by repeated held-out benchmark evidence.
