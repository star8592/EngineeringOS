# EXP-030: Rust Persistence Parity

Date: 2026-10-03

Rust `eos-core` now implements the same durable EventEnvelope JSONL and snapshot contract as the Python research layer.

Verified:
- Python append -> Rust read;
- Rust append -> Python read;
- Python snapshot -> Rust verification;
- Rust snapshot -> Python verification;
- identical SHA-256 state digest;
- both runtimes ignore only a torn final record;
- Rust stale writer returns `VERSION_CONFLICT`;
- a real Python-vs-Rust process race from the same expected version produces exactly one winner and one version conflict;
- the resulting log contains exactly one new event, proving no lost update.

Rust regression suite: 17 tests passed. Storage cross-language/concurrency assertions: 8 passed.
