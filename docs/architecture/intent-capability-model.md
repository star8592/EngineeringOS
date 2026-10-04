# Intent and Capability Model

EngineeringOS separates what the human wants from what the software can currently prove.

- **Intent** is human-owned desired behavior/outcome.
- **Capability** is evidence-backed observed software behavior/surface.
- **Reconciliation** never upgrades semantic similarity into proof.

States:
- `VERIFIED`: every required capability has explicit verification evidence.
- `DISCOVERED`: relevant surface/code is observed but not behaviorally verified.
- `DECLARED_CHECK`: a verification command exists; this is not proof that it passed.
- `UNKNOWN`: intent is clear, but current evidence cannot prove the software satisfies it.
- `NEEDS_INTENT`: the desired outcome itself is missing/ambiguous.

An `UNKNOWN` is a system investigation task, not a question for the user. Only `NEEDS_INTENT` may become a user interruption.

Initial capability discovery uses static product surfaces and verification commands. Later stages add runtime probes, tests, production evidence, and semantic capability equivalence. Static route presence is evidence of a surface existing, not proof that the feature works in production.
