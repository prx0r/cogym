# Minimal Production Architecture

```
market/economic feeds + synthetic worlds
              |
        World Compiler
              |
      immutable snapshots
              |
     Experiment Runner  <---- Pack Compiler
              |                  |
       decisions/outcomes        |--- immutable Pack blobs
              |                  |--- Hydra retrieval
              v
       append-only events
              |
        distill experience
              v
           HydraDB
              |
       evolve/compile packs
              |
      held-out certification
              |
    optional DeepProve receipt
              |
      optional chain registry
```

## Why Rust

The canonicalization, hashing, event protocol, pack compiler boundary, world engine and proof adapters benefit from a small deterministic systems core. LLM providers and HydraDB are ordinary adapters behind narrow interfaces.

## Why not Loom as a dependency

Loom is an excellent architectural reference: Rust core abstractions, provider/tool separation, persisted threads, server-side provider proxy, structured telemetry and reproducible Nix builds. But its repository explicitly marks itself experimental/unstable and proprietary. Cogym copies the **principles**, not the implementation or dependency surface.

## HydraDB role

Use Hydra only for distilled world/method/experience memory. Raw ticks, world snapshots and immutable benchmark artifacts stay in the local/object-store corpus. The Rust adapter talks directly to Hydra's REST API because the official SDKs are currently Python/TypeScript.
