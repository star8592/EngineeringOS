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

## Durable state boundary

The durable core is event-sourced at the semantic boundary. Commands are evaluated against an observed stream version and committed with compare-and-swap semantics. Materialized state and snapshots are projections; they may accelerate reads/recovery but cannot silently override the authoritative event sequence.

## Stable persistence boundary
Python and Rust share the EventEnvelope JSONL and snapshot contract. Runtime migration must not require reinterpretation or rewriting of historical control-plane state. CAS/version semantics are part of the durable contract, not an implementation detail of either language.

## Command boundary
The production control plane must persist command intent before any external side effect. External execution and the local event log are not treated as one transaction. Unknown completion is reconciled through outcome probes before retry.

The Command Processor now has Python↔Rust semantic parity for intent, dispatch, unknown completion, probe-gated retry, and evidence-confirmed outcome. Production authority remains shadow-only until the integrated loop passes dogfood gates.
