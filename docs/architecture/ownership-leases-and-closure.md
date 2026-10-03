# Ownership, Leases, and Evidence Closure

Parallel AI development requires coordination without turning task ownership into permanent locks.

## Ownership

A queue item may have a logical owner, but active execution requires a time-bounded lease. Ownership explains responsibility; the lease grants temporary exclusive execution coordination.

## Lease invariants

- one unexpired lease per scoped work item;
- a different agent cannot claim an unexpired lease;
- expired leases may be reclaimed;
- renewal requires current lease ownership;
- leases are coordination evidence, not authorization to merge/deploy/delete.

## Closure protocol

An executing agent may request closure only with evidence. This moves work to `PENDING_RESOLUTION`. A verifier/manager then checks closure evidence and may transition to `RESOLVED`.

The executor saying "done" is therefore not equivalent to EngineeringOS declaring the issue resolved.

## Dependencies

Queue items will carry `depends_on` and `blocks` edges. A task whose unresolved dependencies remain cannot become execution-ready even if it has high priority. Dependency identity must refer to stable work-item IDs, not chat titles.
