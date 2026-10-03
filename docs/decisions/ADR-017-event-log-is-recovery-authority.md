# ADR-017: Event log is the recovery authority
Status: Accepted

Durable EngineeringOS work state is reconstructed from an append-only event stream. Snapshots and dashboard projections are accelerators, not competing sources of truth.

A crash may leave a torn final append; recovery may ignore only that incomplete tail. Corruption of any complete record is a hard error. Storage backends may evolve, but sequence, idempotency, durability acknowledgement, and replay semantics are contract-level behavior.
