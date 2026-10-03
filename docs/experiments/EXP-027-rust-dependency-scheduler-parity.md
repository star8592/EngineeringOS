# EXP-027: Rust Dependency Graph and Scheduler Parity

Date: 2026-10-03

The second stable EngineeringOS control-plane slice has been implemented in `rust/eos-core`: dependency validation/readiness and scheduler dispatch-lane selection.

## Covered semantics

- missing dependencies are invalid;
- dependency cycles are detected;
- unresolved dependencies block readiness;
- `RESOLVED` and `SUPERSEDED` dependencies satisfy readiness;
- active leases yield `LEASED` rather than dispatchable work;
- deterministic work selects `DETERMINISTIC`;
- review work selects `REASONING_REVIEW`;
- A3/A4/A5 selects `FORMAL_OR_HIGH_ASSURANCE` unless policy gating takes precedence;
- `BLOCK_UNTIL_RESOLVED` selects `POLICY_GATE`.

## Evidence

- Rust unit tests: 10 passed total in `eos-core` (queue/lease plus dependency/scheduler).
- Python dependency invariants: 4 passed.
- Python scheduler invariants: 3 passed.
- Queue Python↔Rust parity assertions: 5 passed.
- Dependency/scheduler Python↔Rust parity assertions: 8 passed.

The parity harness feeds the same JSON work graph to Python and Rust and compares validation plus schedule decisions. Scheduler time is now injectable in Python, making lease behavior deterministic under parity testing.

## Decision

Dependency graph and scheduler semantics are now eligible for the Rust migration track, but Python remains authoritative until the broader control-plane persistence/event-state boundary is proven.
