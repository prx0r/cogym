# Proof Model

Cogym separates three claims that are easy to conflate.

## 1. Commitment proof

Cryptographically bind exact world snapshot, Pack manifest, compiled context, decision, outcome and evaluator version. This is cheap and should always be available.

## 2. Inference proof

For a model supported by a reviewed zkML system such as DeepProve, prove that a committed model executed a committed input/context to produce a committed output. Closed provider APIs generally cannot provide this unless the provider exposes compatible weights/attestation.

## 3. Capability certificate

Empirical claim: on benchmark suite S, model M + Pack P outperformed the matched baseline with measured uncertainty. This is statistical evidence, not a ZK theorem.

A useful certificate combines all three where available.

## Minimal chain role

Keep simulation/evolution off-chain. A chain may register content commitments, certificates, proof receipts, Pack ownership/licensing and settlement. It must not sit in the hot inference/evolution loop.
