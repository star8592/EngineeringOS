# Execution Receipts

EngineeringOS distinguishes transport progress from proven side-effect outcome.

A durable execution receipt has an execution ID, idempotency key, action kind, side-effect classification, lifecycle state, and evidence references.

Lifecycle:
`PLANNED -> DISPATCHED -> ACCEPTED -> RUNNING -> SUCCEEDED|FAILED`
with interruption states `LOST_CONTACT` and `UNKNOWN_COMPLETION`.

`ACCEPTED` is not completion. If contact is lost after a side-effecting action may have crossed the execution boundary, default retry policy is `PROBE_REQUIRED`, not retry. A retry becomes safe only when an outcome probe proves the effect was not applied, or the target action has a stronger idempotency contract.

`SUCCEEDED` requires evidence and a failed transition must not mutate the receipt.
