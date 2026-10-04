# Command Receipt Projection

EngineeringOS Control Room must not maintain a second execution state machine.

The authoritative command history remains the durable command event log:

`.engineeringos/runtime/control-loop/events.jsonl`

The Control Room receipt view is a deterministic read-only projection derived by replaying those events with the same `command_processor.replay_command` contract used by the control loop.

## Projection fields

For each command-backed work item, the projection exposes:

- command id and idempotency key;
- action kind and side-effecting classification;
- replayed command state;
- attempts and outcome;
- retry/probe decision from the authoritative retry contract;
- ordered command-event timeline;
- outcome evidence references;
- evidence digest verification result.

Items denied before command creation are explicitly `NO_COMMAND`; the UI does not invent a receipt for them.

## Unknown completion

`UNKNOWN_COMPLETION` is first-class. For side-effecting commands, the replayed retry contract yields `PROBE_REQUIRED` unless external evidence proves applied/not-applied. The Control Room displays this state; it never converts missing evidence into permission to retry.

## Evidence integrity

A local file evidence reference must include a SHA-256 binding:

`file:<path>#sha256:<digest>`

The projection re-hashes the file and reports:

- `VERIFIED`;
- `INVALID`;
- `PENDING`;
- `NOT_APPLICABLE`.

A successful command without valid outcome evidence is shown as invalid projection evidence rather than silently trusted.

## Authority boundary

The receipt projection is `DERIVED_FROM_COMMAND_EVENT_LOG` and always carries `target_mutation_authorized=false`.

It cannot:

- create or mutate command events;
- retry a command;
- probe an external target;
- authorize execution;
- satisfy host approval;
- alter evidence.

Any future Control Room action must call the same command/policy boundary used by agents; no UI-only execution semantics are allowed.
