# Runtime and Language Boundaries

EngineeringOS should separate semantic experimentation from durable execution.

```text
Human / Agents
      |
      v
Web / API boundary
      |
      v
Rust Control Plane (target steady state)
  - event log / world state
  - work queue / leases
  - dependency + contract graph
  - scheduler / dispatcher
  - authorization/policy enforcement
      |
      +----> deterministic adapters / DevControl / Git / CI
      |
      +----> Python Analysis Workers
             - semantic analysis
             - model benchmarks
             - dataset generation
             - experimental verification tooling
```

Python workers may propose classifications, plans, invariants, or evidence interpretations. Durable state transitions and execution authorization should ultimately cross a stable control-plane boundary rather than being implicit Python side effects.

## Rust parity status

As of EXP-027, the following stable semantics have executable Python↔Rust parity gates:

- durable work item lease/closure lifecycle;
- dependency validation and readiness;
- scheduler dispatch-lane selection.

This is migration eligibility, not cutover authorization. Persistence, event replay, recovery, and integration with the existing Python manager remain outside the current Rust authority boundary.
