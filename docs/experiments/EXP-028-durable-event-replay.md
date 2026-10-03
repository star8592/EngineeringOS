# EXP-028: Durable Event Replay

Implemented deterministic work-item replay in Python and Rust and a first durable JSONL reference store.

Evidence:
- Rust eos-core: 14 unit tests pass;
- Python replay: 4 invariants pass;
- Python↔Rust replay: 7 field-level parity assertions pass;
- durable store: 4 invariants pass, covering ordered append, sequence rejection, torn-tail recovery, and hard failure on complete-record corruption.

No database has been selected. The experiment isolates the durability semantics before storage optimization.
