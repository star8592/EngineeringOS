# EXP-029: Checkpoint + CAS recovery

Date: 2026-10-03

Implemented the first checkpoint and compare-and-swap commit contract on top of the append-only JSONL research store.

Verified invariants:
1. snapshot persists `last_seq` and state with an integrity digest;
2. snapshot + tail replay equals full event replay;
3. a writer using the current version can append;
4. a stale concurrent writer is rejected with `VERSION_CONFLICT`;
5. snapshot state tampering is detected through `SNAPSHOT_DIGEST_MISMATCH`.

Existing event-store, replay, queue, lease, dependency, scheduler, and Rust core regression suites remained green.

This experiment does not yet designate JSONL as the production database. It establishes the storage-independent semantics that a later Rust/SQLite/PostgreSQL adapter must preserve.
