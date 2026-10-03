# Durable Event Log

EngineeringOS state recovery is defined by an append-only event stream plus deterministic replay. Materialized state and future snapshots are projections/caches, not independent truth.

Initial durability contract:
- one monotonically increasing sequence per stream;
- globally unique event IDs within the stream;
- writer takes an exclusive file lock;
- each accepted append ends with newline and `fsync` before success;
- recovery may discard only an incomplete final record (torn append);
- malformed complete records are corruption and hard-fail;
- replay validates event ordering and domain invariants.

The JSONL store is deliberately a reference durability adapter, not a final storage commitment. SQLite or another backend may replace it only if it preserves the same externally tested event semantics.
