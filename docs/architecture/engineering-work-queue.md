# Engineering Work Queue

The Engineering Manager materializes unresolved engineering pressure into a durable queue. Chat threads are inputs; they are not the queue.

## Lifecycle

`DISCOVERED -> IN_PROGRESS -> PENDING_RESOLUTION -> RESOLVED`

Additional states: `BLOCKED`, `REOPENED`, `SUPERSEDED`.

A finding disappearing from a later scan does **not** automatically mean resolved. It becomes `PENDING_RESOLUTION` until evidence proves closure. If a resolved issue reappears, it becomes `REOPENED`.

Each item carries stable identity, project, priority, reason, required assurance, automation level, timestamps, and evidence references. Future versions add scoped subjects/dependencies/owners/leases.

## Safety boundary

Queue membership is not execution authorization. Policy and assurance gates remain separate from action execution.
