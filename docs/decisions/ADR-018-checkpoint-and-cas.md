# ADR-018: Checkpoint recovery and optimistic versioned commits
Status: Accepted

EngineeringOS uses an append-only event log as recovery authority. Snapshots are acceleration artifacts only.

## Checkpoint rules

- a snapshot records `last_seq`, materialized state, schema version, and a SHA-256 digest of the state;
- snapshots are written to a temporary file, fsynced, atomically renamed, then the containing directory is fsynced;
- recovery loads a valid snapshot and replays only events with `seq > last_seq`;
- full replay and snapshot+tail replay MUST produce equivalent state;
- corrupt or digest-mismatched snapshots are rejected rather than trusted.

## Concurrent command rule

A state-changing command carries the version (`last_seq`) it observed. While holding the event-log writer lock, the store compares that version with the current durable version. A mismatch fails with `VERSION_CONFLICT`; the caller must refresh/re-evaluate rather than overwrite newer work.

This is optimistic concurrency control. The writer lock serializes the physical append; the expected version protects semantic correctness against stale concurrent decisions.
