# Cognitive Packs

A cognitive pack is the smallest sellable/reusable object in Cogym.

It is **not** a fine-tuned model and does not claim to permanently alter weights. It is a deterministic context program plus optional seeded experience and a benchmark certificate.

```text
CognitivePack
├── genome
│   ├── reasoning policy
│   ├── representation
│   ├── induction
│   ├── memory policy/depth
│   └── social policy
├── context modules
├── seeded experience
├── provenance
├── benchmark commitments
└── optional external inference proof refs
```

## Specialism experiment

Example hypothesis: reading/encoding a compact corpus of game-theory methods improves repeated social-market decisions.

Protocol:

1. freeze model version + decoding;
2. freeze a suite of world instances;
3. run baseline agent;
4. apply pack to the same model;
5. replay exact worlds;
6. compare reward, calibration, adaptation latency, revision gain and behavior signature;
7. repeat on held-out world seeds;
8. only then publish a specialization claim.

## Behavior programmability

A pack can additionally report a *behavior signature*. Repeated runs estimate how tightly the pack concentrates behavior under a specified model/decoding configuration. This is empirical predictability, not proof of universal determinism.

## Proof boundary

Three layers should remain distinct:

- **Commitment proof:** hashes show which pack/context/world/output were used.
- **Inference proof:** external zkML may prove a supported model executed on a committed input to produce a committed output.
- **Capability evidence:** held-out benchmarks support a statistical claim that the pack improves a measured behavior.

Never collapse these into one claim.
