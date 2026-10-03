# EXP-040: Activate formal assurance gates

Date: 2026-10-04

EngineeringOS previously defined A3/A4 assurance levels but did not execute a real model checker or proof assistant in the repository gate.

This experiment activates the first deterministic formal-assurance path:

- **A3 / TLA+ + TLC:** the side-effecting command transaction state machine is modeled with explicit states for intent, dispatch, unknown completion, proven-not-applied and success. TLC checks that outcome states require evidence, dispatched/unknown work cannot be blindly retried, retry after NOT_APPLIED is evidence-backed, and attempt count remains bounded.
- **A4 / Lean:** stable retry/evidence semantics are encoded as pure datatypes/functions and checked by Lean. The initial theorems prove that dispatched and unknown-completion states require probing, succeeded commands are never retried, retry is only allowed before effect or after proven-not-applied, and terminal outcome states require evidence.
- **Proof checking:** the Lean CI builds with Lean 4.34.1, runs the bundled `leanchecker`, and runs `axiom-audit` over the `EngineeringOS` namespace so incomplete `sorry`/admit-style proofs or unexpected axioms fail the gate.
- **Scope:** these proofs cover the stable command-safety kernel only. They do not claim the whole EngineeringOS implementation is formally verified.
- **Authority:** AI may draft the specification/proof, but TLC/Lean/nanoda own PASS/FAIL.

The next A3 candidates are lease exclusivity, dependency/closure transitions, and convergence/release state machines. Lean expansion remains deliberately narrower and follows only after semantics stabilize.

## First TLC feedback

The first TLC execution reached `SUCCEEDED` and reported a deadlock. That was not a safety counterexample: `SUCCEEDED` is intentionally terminal and no command transition is enabled after confirmed application. The model configuration now sets `CHECK_DEADLOCK FALSE` so TLC treats terminal command states as valid while continuing to check the declared safety invariants. The state machine itself was not weakened to manufacture a successor transition.


## nanoda compatibility note

The first independent-checker attempt reached nanoda after a successful Lean build, but nanoda rejected the current Lean export stream with `invalid digit found in string`. This matches the open lean-action nanoda compatibility issue already reported on newer Lean export formats. EngineeringOS therefore does not classify nanoda as a required A4 gate until upstream compatibility is restored. The formal proof remains gated by Lean compilation, bundled `leanchecker`, and `axiom-audit`; the incompatibility is recorded rather than hidden.
