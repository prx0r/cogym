# Frontier Papers Relevant to Cogym
Organized by which part of Cogym they validate or challenge.
All papers verified to exist as of 2026-08-23.

## Evaluation Integrity
| arXiv ID | Paper | Key Finding for Cogym |
|----------|-------|----------------------|
| [2606.08106](https://arxiv.org/abs/2606.08106) | PACE: Anytime-Valid Acceptance Tests | Greedy self-evolution commits 30-42% false edits. Anytime-valid paired testing largely eliminates them. Cogym must use this before trusting campaign results. |
| [2606.04455](https://arxiv.org/abs/2606.04455) | Meta-Agent Challenge | High optimization pressure causes agents to target evaluator/extract ground truth. Validates sealed evaluator + canary approach. |
| [2605.02964](https://arxiv.org/abs/2605.02964) | Reward Hacking Benchmark | Simple environmental hardening substantially reduces exploit behavior. |

## Skill Evolution
| arXiv ID | Paper | Key Finding |
|----------|-------|-------------|
| [2605.08693](https://arxiv.org/abs/2605.08693) | SkillMaster | Skills evaluated via counterfactual utility on other tasks, not agent self-report. Directly validates our SkillRegistry gating. |
| [2602.12670](https://arxiv.org/abs/2602.12670) | SkillsBench | Curated skills: +16.2pp average pass rate. Self-generated skills: ≈0 gain, some negative. Can Cogym's counterfactual selection fix this? |
| [2608.03874](https://arxiv.org/abs/2608.03874) | ContinualSkillBench | Sequential experience helps but explicit skill maintenance ≈ ordinary in-context adaptation on average. Skills help most when procedures are genuinely reusable. |

## Evolution Architecture
| arXiv ID | Paper | Key Finding |
|----------|-------|-------------|
| [2505.22954](https://arxiv.org/abs/2505.22954) | Darwin Gödel Machine | Archive of stepping stones (not just champion) enables 20%→50% SWE-bench. Removing open-ended exploration weakens progress. Validates our ElitesArchive. |
| [2602.04837](https://arxiv.org/abs/2602.04837) | GEA (Group-Evolving Agents) | Experience sharing between lineages beats isolated tree evolution at same budget. Validates planned cultural transmission experiments. |
| [proceedings.iclr.cc](https://proceedings.iclr.cc/paper_files/paper/2026/hash/0e9e708b6f48e14fd0ac29e167413f76-Abstract-Conference.html) | GEPA (ICLR 2026) | Parallel proposals = 3-4x wall-clock improvement. Reflective prompt evolution beats GRPO with up to 35× fewer rollouts. Hermes parallel proposals map directly. |

## Memory & Adaptation  
| arXiv ID | Paper | Key Finding |
|----------|-------|-------------|
| [2605.18421](https://arxiv.org/abs/2605.18421) | EvoMemBench | Compared 15 memory methods. Strong long-context baselines remain competitive. Retrieval helps knowledge-heavy tasks; procedural memory helps execution when structure matches. |
| [2608.14441](https://arxiv.org/abs/2608.14441) | PACE-Bench | Memory anchors agents to obsolete designs under env mutation. Verified simulator feedback improves adaptation. Even revealing the change doesn't solve redesign. |
| [2604.08988](https://arxiv.org/abs/2604.08988) | SEA-Eval | Same success rate can differ 31.2× in token consumption. Must measure cost alongside performance. |

## Evaluation Frameworks
| arXiv ID | Paper | Key Finding |
|----------|-------|-------------|
| [2606.17546](https://arxiv.org/abs/2606.17546) | SEAGym | Needs train/update-validation/test/replay/cost views. Seemingly useful updates can collapse later or fail OOD transfer. |
| [2602.00359](https://arxiv.org/abs/2602.00359) | Agentic Evolution Position Paper | Evolution compute is a distinct scaling axis from inference and training compute. Cogym can test evolution-budget scaling laws. |
