# ADR-021: Persist command intent before external side effects
Status: Accepted

Every side-effecting command must have a durable command identity and idempotency key before execution crosses the external effect boundary. A dispatched command with unknown completion is not retryable until an outcome probe proves whether the effect was applied.

EngineeringOS does not claim atomic transactions across its event log and external systems. It uses durable intent, optimistic concurrency, idempotency keys, evidence-bearing outcome confirmation, and probe-before-retry recovery.
