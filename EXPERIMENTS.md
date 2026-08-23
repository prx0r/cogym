# Cogym Experiment Registry
All experiments follow the same structure: preregistered hypothesis, identified
independent/dependent/control variables, deterministic grading, reproducible setup.
No LLM-as-judge where deterministic verification is possible.

## Template
Each experiment lives in `experiments/<id>/` containing:
- `PROTOCOL.md` — frozen before subjects run (hypothesis, variables, controls)
- `materials/` — treatment materials injected into subjects  
- `outputs/` — graded results (JSON)
- `run-log.txt` — raw hermes output per subject
- `RESULTS.md` — findings after grading

## Current experiments
| ID | Status | Question | Worlds |
|----|--------|----------|--------|
| STX-001 | ✅ Complete | Does reasoning strategy transfer? | 1 probe (too easy) |
| STX-002 | ✅ Complete | Same on hard worlds? | 15 hard worlds (5 families) |
| STX-003 | Planned | Dose-response: how much pathway depth helps? | Same + depth 0-5 |
| STX-004 | Planned | Persistence: does learned behavior survive washout? | Regime flip |
| STX-005 | Planned | Falsification: do agents seek disconfirmation? | Falsification family |

## Frontier papers anchoring our methodology
| Paper | What we borrow |
|-------|---------------|
| PACE (2606.08106) | Anytime-valid acceptance testing; false commit rates under adaptive testing |
| SkillMaster (2605.08693) | Counterfactual skill evaluation; skills must justify themselves on probes |
| SkillsBench (2602.12670) | Self-generated skills ≈ no gain; curated > generated. Can Cogym fix this? |
| DGM (2505.22954) | Archive stepping stones; open-ended evolution beats hill-climbing |
| GEPA (ICLR 2026) | Parallel proposals = 3-4x faster evolution at same budget |
| GEA (2602.04837) | Experience sharing across lineages beats isolated evolution |
| MAC (2606.04455) | Optimization pressure causes evaluator targeting — hence sealed eval |
| EvoMemBench (2605.18421) | Memory type matters by task; long-context baselines competitive |
| PACE-Bench (2608.14441) | Memory anchors agents to obsolete designs under env mutation |
| SEAGym (2606.17546) | Train/update-val/test/replay/cost views needed for longitudinal eval |
| SEA-Eval (2604.08988) | Equal success ≠ equal efficiency; token cost varies 31x |
| A-Evolve (github) | Evolve workspace files; gate on held-out; rollback regressions |
