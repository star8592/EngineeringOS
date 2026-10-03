# EXP-011: Durable Engineering Work Queue

The first Manager Plan produced five live DevControl convergence tasks. They are now materialized into a persistent queue with stable IDs rather than existing only in terminal/chat output.

Initial queue:
- P1 production-verification evidence gap;
- P2 dirty-workspace triage;
- P2 overlapping-development review;
- P3 duplicate-state reconciliation;
- P3 divergent-development review.

The key invariant is conservative closure: disappearance from a scan is not proof of resolution.
