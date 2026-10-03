# EXP-041: System-One / Jev advisory contract

Date: 2026-10-04

EngineeringOS now has an executable typed-decision contract for the planned fast System-One layer.

The contract deliberately separates **judgment** from **authorization**:

- Jev/OpenJev-compatible typed questions may recommend one of the EngineeringOS routing lanes.
- Low-confidence results escalate to `REASONING_REVIEW`.
- High-risk work escalates to `FORMAL_OR_HIGH_ASSURANCE` regardless of model confidence.
- Every System-One result carries `authorization=UNAVAILABLE` and `advisory_only=true`.
- A regression invariant rejects any attempt to reinterpret System-One output as an `ALLOW` decision.

This makes the Jev-shaped interface usable for benchmark collection without granting it control-plane authority.

## Activation status

The typed contract is active and tested. A live Jev or OpenJev inference backend is **not yet a production routing authority**. Before activation, EngineeringOS must benchmark candidates on the Engineering Decision Benchmark (EDB), measure false-negative cost for high-risk routing, choose confidence thresholds from observed calibration, and retain a deterministic fallback.

Hosted Jev, OpenJev/Laya-style self-hosted models, or another provider-neutral implementation may satisfy the interface. The chosen backend remains replaceable and cannot bypass policy, command, approval, or formal-assurance gates.
