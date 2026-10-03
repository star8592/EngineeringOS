# Reconciliation State Machine

EngineeringOS uses explicit reconciliation states:

- `RESOLVED`: required evidence establishes the relationship.
- `DRIFT`: compatible scopes intentionally or currently differ and the difference is evidenced.
- `CONTRADICTION`: compatible facts for the same scope/time cannot both be true.
- `STALE`: a claim's validity has expired or newer authoritative evidence supersedes it for the same scope/time question.
- `UNKNOWN`: required evidence is absent or cannot be linked.

`DRIFT` is not synonymous with failure. Policy may permit source to be ahead of production. A separate policy layer determines whether an evidenced drift is acceptable, overdue, or blocking.
