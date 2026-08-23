# Proofs and blockchain boundary

Cogym distinguishes three claims:

1. **commitment**: these exact artifacts were used;
2. **execution/attestation**: a particular model computation produced an output;
3. **capability evidence**: the intervention measurably improved behavior on held-out worlds.

A hash proves only #1. A model execution proof such as a compatible zkML/attestation system may support #2. Only benchmark evidence supports #3.

The deterministic challenge protocol can be anchored to a blockchain later:

```text
publish challenge
participants commit artifacts
server nonce already committed
reveal artifacts/nonces
derive seed from challenge + commitments + nonce
run off-chain world
commit replay/result digest
```

Do not put high-volume LLM inference or market simulation in the chain hot loop.
