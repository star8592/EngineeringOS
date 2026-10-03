# Policy Plane

Evidence and reconciliation describe reality; policy decides what that reality requires.

The Policy Plane consumes resolved evidence states and emits explicit decisions such as `OK`, `ACCEPTABLE_DRIFT`, `REVIEW`, or `BLOCK`. It must not rewrite underlying facts.

Initial DevControl rule:

- production endpoints disagree -> `BLOCK`;
- source and production agree -> `OK`;
- source/production differ and production provenance is unresolved -> `REVIEW`;
- source is ahead while runtime identity is internally consistent and provenance resolves -> `ACCEPTABLE_DRIFT` until a separate release-cadence/SLO policy says the drift is overdue.

This separation prevents evidence collection from silently becoming release policy.
