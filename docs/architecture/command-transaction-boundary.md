# Command Transaction Boundary

EngineeringOS must not pretend that a local event store and an external side effect share one atomic transaction.

The reliable boundary is:

1. validate policy and optimistic version;
2. durably append `COMMAND_INTENT_RECORDED`;
3. dispatch the external action with a stable idempotency key;
4. if completion is uncertain, enter `UNKNOWN_COMPLETION`;
5. probe the target system;
6. append either `COMMAND_EFFECT_CONFIRMED` or `COMMAND_EFFECT_NOT_APPLIED` with evidence;
7. only confirmed outcome events may update durable world-state projections.

Crash windows therefore have explicit semantics:
- before durable intent: nothing happened from EngineeringOS's perspective;
- after intent but before dispatch: dispatch may proceed;
- after dispatch but before outcome evidence: probe is mandatory before retry;
- after confirmed applied: do not retry;
- after proven not applied: retry is allowed.

Exactly-once external effects are only possible when the target system honors the same idempotency key. Otherwise EngineeringOS provides probe-before-retry safety rather than claiming impossible distributed atomicity.
