# ADR-019: Python and Rust share one persistence contract
Status: Accepted

EngineeringOS migration does not create a second durable-state format. Python research code and Rust `eos-core` must read and write the same append-only EventEnvelope JSONL and snapshot schema.

Required compatibility:
- identical `seq` / `event_id` semantics;
- identical torn-tail recovery rule;
- identical optimistic version/CAS rule;
- identical snapshot schema and SHA-256 digest over canonical JSON state;
- cross-language readers must accept records produced by the other runtime;
- cross-language stale writers must conflict rather than overwrite.

A Rust migration is therefore a runtime substitution behind a stable state contract, not a history migration.
