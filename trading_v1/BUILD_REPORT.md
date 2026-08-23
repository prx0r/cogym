# Build report

- Version: 1.0.0
- Final validation date: 2026-08-20
- Tests: 16 passed
- Python compileall: passed
- Wheel build: passed with --no-build-isolation
- Wheel SHA-256: 09a73653ca1be362c955b5588b7e1605218149c77d34855f7d53bf2baeff190e
- Repository files: 95
- Python files (core/tests/examples): 66
- Python lines (core/tests/examples): 2347

## Smoke paths executed

- deterministic synthetic world replay;
- A-F transfer runner;
- persistent Master -> three fresh Students;
- point-in-time leakage filter;
- challenge commit/reveal;
- Pack loading/invariants;
- dose response;
- treatment/persistence/team/contagion;
- social private/revised decisions;
- local SQLite evidence graph;
- experiment receipts.

## Important limitation

The offline harness model validates protocol behavior only. No claim that real LLM cognition was changed is included in this build. Real-model runs are the next empirical gate.
