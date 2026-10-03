# EXP-032: Command Processor Transaction Boundary

The first Command Processor model validates ten invariants covering policy denial, durable intent, optimistic versioning, idempotency-key conflicts, dispatch attempts, unknown completion, probe-gated retry, evidence-required success, and confirmed no-retry behavior.

A command may be retried directly only before the external effect boundary or after evidence proves the previous attempt was not applied. After dispatch, absence of a response is represented as uncertainty rather than failure.
