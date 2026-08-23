# Data and provenance

## Market data

Archive rawest reliable source data with:

- instrument/venue/chain/pool identity;
- source;
- retrieval time;
- native resolution;
- normalization version;
- file/content digest.

For small tokens, individual swaps/trades may be a better primitive than pretending one venue's 1-minute OHLCV is canonical.

## External context

Every datum carries:

- `observed_at`: when the represented event/value belongs in the world;
- `available_at`: earliest time the agent could have known it;
- source/provenance.

Backtests filter by `available_at`, not merely event date.

## Experiment data

Store exact prompts/messages, model identifier, provider parameters, sample seed request, raw output hash, parsed structured output, evaluator version and outcomes.
