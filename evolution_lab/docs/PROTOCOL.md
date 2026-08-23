# Core protocol

## Objects

1. **WorldConstructor** — deterministic rules and parameter space.
2. **WorldInstance** — constructor + parameters + seed.
3. **WorldSnapshot** — immutable observation/state commitment at time *t*.
4. **AgentGenome** — model, cognition, memory, social topology, plasticity.
5. **Decision** — private or socially revised output.
6. **RunRecord** — immutable snapshot→decision→outcome edge.
7. **Lineage** — ancestry across genome mutation and/or memory carryover.
8. **CognitivePack** — committed context program + genome + memory seeds + benchmark evidence.

## Scientific invariant

A comparison is causal only when the world prefix and all non-treatment variables are held fixed.
A fork therefore records parent world, fork step, new seed, and changed parameters.

## Memory invariant

World truth is not experiential memory. Raw observations/snapshots belong to the world store. Agent lessons, outcomes, habits, and peer reputations belong to memory.

## Two-phase social protocol

1. private decision is committed;
2. peer information is revealed according to topology;
3. revisions are committed separately;
4. both private and final scores are retained.

This measures individual intelligence separately from social integration/herding.

## Pack claim

A pack may claim only the empirical behavior measured on committed benchmarks. Pack composition is deterministic; model behavior generally is not. Optional zkML can prove a specific inference for supported models, not a universal future-performance claim.
