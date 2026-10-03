# EXP-025: Rust Migration Readiness

## Goal

Measure when EngineeringOS core concepts are stable enough to migrate from Python prototypes to Rust without freezing immature abstractions.

## Readiness signals

A module is migration-ready when:
- schema/API changed rarely across several G2 shadow iterations;
- invariants cover its key state transitions;
- persisted state compatibility is defined;
- concurrency/failure semantics are explicit;
- performance or operational reliability justifies a systems implementation;
- cross-language parity fixtures can exercise both implementations.

The first migration should be small and evidence-driven, likely Work Queue + Lease semantics, because those already have explicit invariants and represent a durable-concurrency boundary.
