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


## Activation status

- A0: routing contract exists; the Jev/OpenJev-class System-One backend is not yet production-active.
- A1: active through deterministic unit/integration/E2E tests.
- A2: active through contract, schema, parity and conformance gates.
- A3: first executable gate added in EXP-040 for command transaction safety using TLA+/TLC.
- A4: first executable Lean proof package added in EXP-040 for stable command retry/evidence semantics, gated by Lean build, bundled `leanchecker`, and `axiom-audit`; nanoda remains an optional independent checker pending upstream compatibility with the current Lean export format.
- A5: partially active through production evidence/replay/provenance work; exact artifact/deployment identity remains an open gap.

An assurance label is earned only by a successful verifier/evidence path. Merely routing an item to `FORMAL_OR_HIGH_ASSURANCE` does not grant A3/A4.
