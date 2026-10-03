# EXP-016 Findings: G1 Genericity

Date: 2026-10-03

CycleAlpha was selected as the second real repository because it is structurally different from DevControl and already contains real in-progress work.

Without changing Fact, Policy, Queue, Dependency, Lease, or Scheduler core semantics, a generic Git adapter observed CycleAlpha and produced a shadow plan.

Observed:
- current branch: `feat/phase2-real-data`
- current HEAD: `aa02a38684c60320e7da2553876b75d30bf142e7`
- `origin/main`: `45d7c6633a140ff53c1dfb1c65ca3556a6269417`
- 4 local branches
- dirty workspace: true
- 3 scoped facts emitted
- 2 durable-work candidates emitted
- 2 scheduler entries dispatchable in reasoning-review lane
- target mutation authorization: false

The generic Git adapter contains no DevControl-specific conditional. Current G1 proves the core can ingest and schedule a second repository at the generic Git/workspace layer. It does not yet prove generic CI/release/runtime adapters; those remain later genericity extensions.

## Result

`G1_GENERICITY = PASS (minimum gate)` with the explicit limitation above.
