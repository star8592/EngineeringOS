# EXP-036: First end-to-end G2 Shadow Control Loop

Date: 2026-10-03

EngineeringOS completed its first end-to-end durable G2 control loop against live DevControl observations without authorizing any DevControl mutation.

Pipeline exercised:

`evidence -> reconciliation -> manager -> durable queue -> scheduler -> shadow policy -> durable command intent -> shadow executor -> outcome evidence -> command event commit -> replay/projection -> Control Room`

Observed run:
- target: DevControl
- source head: `bf0ddcf43579f26b5ec395ba6b708199b8850056`
- live production: version `3.1.18`, release `da5e3d2`
- source qualification: PASS
- live production qualification: PASS
- deployment identity: PARTIAL
- artifact identity: UNKNOWN
- queue items projected: 7 (including one already-resolved historical false-positive)
- shadow commands succeeded: 6
- policy-blocked/non-dispatchable: 1
- durable command events: 18 (intent, dispatch, confirmed evidence for each of 6 commands)
- target mutation authorized: false

A second execution against the exact same snapshot produced no additional command events: the event count remained 18. This demonstrates stable snapshot/item idempotency for the shadow loop.

The Control Room now consumes runtime projections generated from the same `.engineeringos` durable state. Dashboard runtime JSON is not a source of truth and is excluded from source control.

This experiment satisfies the mechanical end-to-end loop portion of the G2 exit criteria. G2 is not complete: sustained time-series outcome evaluation, refreshed queue closure, generic adapter expansion, and G3 admission evidence remain required.
