# Cogym Trading v1

A **trading-first deterministic laboratory for stochastic LLM cognition**.

Cogym does not claim an LLM has a hidden mental state we can directly inspect. It tests a narrower empirical question:

> Can a sequential context pathway reliably move a model into a different observable decision regime, and can that regime be replayed, transmitted, taught, combined, disrupted, or recovered?

Trading is the first environment because it supplies delayed numerical outcomes, non-stationary regimes, repeated decisions, social/game-theory structure, and clean counterfactual scoring. Everything here is paper/simulation only.

## The core invariant

```text
DETERMINISTIC WORLD
       |
       +-- stochastic model sample 1
       +-- stochastic model sample 2
       +-- stochastic model sample 3
       +-- ...
       |
       v
DISTRIBUTION OF OBSERVABLE BEHAVIOR
```

The market world is exactly replayable. LLM indeterminism is measured, not wished away.

## What is implemented

- deterministic synthetic market curriculum levels 0..6;
- canonical world and artifact commitments;
- point-in-time context with `observed_at` and `available_at` to block future leakage;
- EvoLabz-inspired state features: direction, strength, volatility and their changes, drawdown and volume surprise;
- CSV OHLCV loader for real historical data;
- generic OpenAI-compatible model adapter;
- structured paper-trading decision contract;
- repeated stochastic sampling with per-run seeds and variance summaries;
- live context pathways and exact pathway checkpoints;
- A-F state-transfer experiment:
  - A live self-path;
  - B exact own trace replay;
  - C same-model other trace;
  - D other-model trace;
  - E paraphrased trace;
  - F summary only;
- state-transfer fidelity using decisions, behavioral phenotype and observable reasoning artifacts;
- pathway dose-response experiments (0,1,2,3... steps);
- persistent-vs-reset decision chains;
- peer reveal + revision experiments;
- persistent Master -> fresh Student dojo loop;
- multiple independent Masters plus optional faculty roundtable;
- transmission chains A -> B -> C;
- candidate Pack manifests for regime-shift, falsification, social herding, loss/upside salience, master teaching and self-reference probes;
- append-oriented local SQLite evidence graph;
- provider-neutral HydraDB projection export;
- challenge commit/reveal seed protocol inspired by deterministic competition systems;
- experiment receipts and external DeepProve verifier boundary;
- no fake zkML proof generator;
- no fake "state convergence" tests.

## Quick start

```bash
python -m pytest -q
python -m cogym.cli smoke
python -m cogym.cli dojo-demo
```

The offline demos use `HarnessTraderModel`, which exists **only** to test the machinery. It is not evidence for LLM state induction.

For a real model:

```python
from cogym.agents.model import OpenAICompatible

model = OpenAICompatible(
    model_id="your-model",
    base_url="https://provider.example/v1",
    api_key="...",
)
```

Then use `run_abcdef`, `pathway_dose_response`, `run_world`, or the Dojo classes.

## First real experiment

Start deliberately small:

1. one model;
2. one 3-step trading pathway;
3. 20 hidden deterministic synthetic worlds from levels 2-6;
4. 5-10 samples per world/condition;
5. A-F comparison;
6. repeat with persistent vs reset context.

Do **not** add HydraDB, evolution, blockchain or proofs to the inference hot loop until the basic state-transfer effect survives held-out evaluation.

## Object model

```text
World          deterministic environment
Snapshot       point-in-time observation
AgentSession   a model instance + current transcript
Pathway        ordered prompts the recipient must answer live
Checkpoint     exact transcript artifact from a pathway
Transmission   teacher-authored pathway + precommitted prediction
Pack           portable candidate/certified pathway/checkpoint/social policy
Run            one model trajectory through one world
Master         persistent teacher context across students
Student        fresh model instance receiving a transmission
EvidenceGraph  durable experiment/culture store
Receipt        cryptographic commitment to experiment artifacts
```

## What a Pack is

A Pack is **not automatically intelligence** and not a giant memory dump. A candidate Pack is a reproducible intervention protocol. It only becomes `certified` after it has evidence IDs from held-out Cogym evaluations.

## Anti-theatre rule

No deterministic mock can establish a cognitive effect. No hash proves capability. No zk proof proves that a Pack made a model better. See `specs/ANTI_THEATRE.md`.
