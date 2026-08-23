# Cogym Pack Protocol v1

A **Pack** is a portable, content-addressed context program that attempts to reproduce a tested behavioral/capability phenotype in an LLM **without changing model weights**.

It is not a model, fine-tune, memory database, or claim about subjective/internal state.

## Pack = manifest + immutable blobs + benchmark certificate

The manifest declares:

1. induction sequence — ordered context modules;
2. exemplars — selected demonstrations/experience traces;
3. retrieval recipes — what to fetch from a compatible memory backend;
4. tool-policy modules — schemas/instructions needed for the role;
5. output contract — canonical machine-readable phenotype;
6. target behavioral signature — empirical target, never treated as proof of an internal state;
7. provenance — school/curriculum/parent packs.

All components are content addressed. The final compiled context is committed separately from the Pack itself because compilation is model/context-window dependent.

## Why not ship Hydra inside a Pack?

Hydra is an evolving school memory. A Pack is a portable **compiled slice + retrieval recipe**. Keeping them separate means:

- Packs remain small and inspectable.
- A school can improve its memory without silently mutating old packs.
- Historical certificates remain reproducible.
- Different agents can attach private memory while sharing the same Pack.

## Pack optimization target

The important quantity is not prompt length or benchmark score alone:

`utility = competence_gain - inference_cost - instability_penalty - transfer_penalty`

The pack compiler should search for the smallest context that remains inside the desired behavioral basin on held-out worlds.
