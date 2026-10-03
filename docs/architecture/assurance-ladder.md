# Assurance Ladder

EngineeringOS uses the cheapest adequate assurance mechanism and escalates according to risk. Probabilistic judgment and formal proof are complementary, not interchangeable.

## Levels

- **A0 — AI_ASSESSED:** fast probabilistic classification/routing. Useful for triage; never treated as proof.
- **A1 — TESTED:** deterministic unit/integration/E2E evidence for concrete implementations.
- **A2 — CONTRACT_VERIFIED:** explicit interface/invariant/schema/conformance checks.
- **A3 — MODEL_CHECKED:** state-machine/concurrency properties checked with tools such as TLA+/TLC where appropriate.
- **A4 — FORMALLY_PROVED:** critical properties machine-checked by a proof assistant such as Lean when cost is justified.
- **A5 — RUNTIME_CONFORMANT:** production/runtime traces are tied back to the specified/verified behavior and exact deployed identity.

Higher is not automatically better. UI changes may need A1/A2. Approval semantics, gateway failover, execution-at-most-once, authentication, release/convergence state machines, and tool-surface contracts are candidates for A3; only especially critical stable invariants justify A4.

## Principle

AI may propose invariants, specifications, proofs, tests, and counterexample explanations. Deterministic verifiers own PASS/FAIL for formal claims.
