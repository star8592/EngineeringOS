# ADR-020: Unknown completion is a first-class execution state
Status: Accepted

For side-effecting commands, transport interruption after dispatch/acceptance does not authorize automatic replay. EngineeringOS records `LOST_CONTACT` / `UNKNOWN_COMPLETION` and requires an outcome probe or explicit idempotency proof before retry.

This prevents duplicate deploys, commits, deletes, sends, publishes, and other repeated side effects after network/device failure.
