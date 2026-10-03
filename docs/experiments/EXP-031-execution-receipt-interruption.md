# EXP-031: Execution Receipt Interruption Semantics

Date: 2026-10-03

The DevControl device interruption during Rust persistence work was used as a dogfood case. A task had been accepted, then the device became unavailable before completion could be verified. EngineeringOS now models that case explicitly rather than interpreting acceptance as success or blindly retrying.

Verified invariants include: accepted side-effect requires outcome probe before retry; lost contact preserves that requirement; proven-not-applied permits retry; proven-applied forbids retry; success requires evidence; failed success validation leaves prior receipt state unchanged; read-only actions remain retryable.
