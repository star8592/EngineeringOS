# EXP-026: Python ↔ Rust Queue/Lease Parity

Date: 2026-10-03

The first `eos-core` Rust prototype now implements the stable Queue/Lease closure semantics currently exercised by the Python research layer.

A first compile exposed a missing `chrono` serde feature; comparison against the Python implementation also exposed two semantic omissions in the initial Rust draft: lease renewal and `resolved_by` attribution. Both were corrected before adoption.

Validation:
- Rust unit tests: 5 passed;
- existing Python queue/lease invariants: 4 passed;
- cross-language deterministic scenario: 5 parity assertions passed.

Parity currently covers state, owner retention, lease removal on resolution, verifier attribution, and ordered resolution evidence. This is a migration gate, not yet authorization to replace the Python implementation.
