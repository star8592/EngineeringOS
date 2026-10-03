# EXP-013: Work Dependency Graph

Added executable dependency semantics for durable work items.

Initial invariants:
- missing dependency IDs are invalid;
- self/cyclic dependencies are detected;
- unresolved dependencies make a work item `BLOCKED`;
- resolved/superseded dependencies allow a discovered item to become `READY`.

Next, Manager-generated work will attach dependency edges from evidence relationships rather than hand-authored chat ordering.
